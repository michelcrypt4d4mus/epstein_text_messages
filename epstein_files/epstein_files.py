import gzip
import json
import pickle
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Sequence, Type

from rich.align import Align
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.documents.email import DETECT_EMAIL_REGEX, JUNK_EMAILERS, KRASSNER_RECIPIENTS, USELESS_EMAILERS, Email
from epstein_files.documents.emails.email_header import AUTHOR
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MSG_REGEX, MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import (EPSTEIN_MEDIA, EPSTEIN_WEB, JMAIL, epstein_media_person_url,
     epsteinify_name_url, epstein_web_person_url, search_jmail_url, search_twitter_url)
from epstein_files.util.constants import *
from epstein_files.util.data import days_between, dict_sets_to_lists, json_safe, listify, sort_dict
from epstein_files.util.doc_cfg import EmailCfg, Metadata
from epstein_files.util.env import DOCS_DIR, args, logger
from epstein_files.util.file_helper import file_size_str
from epstein_files.util.highlighted_group import HIGHLIGHTED_NAMES, HighlightedNames, get_info_for_name, get_style_for_name
from epstein_files.util.rich import (DEFAULT_NAME_STYLE, LAST_TIMESTAMP_STYLE, NA_TXT, add_cols_to_table,
     print_other_page_link, build_table, console, highlighter, link_text_obj, link_markup, print_author_panel, print_centered,
     print_panel, print_section_header, vertically_pad)
from epstein_files.util.search_result import SearchResult
from epstein_files.util.timer import Timer

EXCLUDED_EMAILERS = [e.lower() for e in (USELESS_EMAILERS + [JEFFREY_EPSTEIN])]
PICKLED_PATH = Path("the_epstein_files.pkl.gz")
DEVICE_SIGNATURE = 'Device Signature'
DEVICE_SIGNATURE_PADDING = (1, 0)
SLOW_FILE_SECONDS = 1.0

INVALID_FOR_EPSTEIN_WEB = JUNK_EMAILERS + KRASSNER_RECIPIENTS + [
    'ACT for America',
    'BS Stern',
    INTELLIGENCE_SQUARED,
    UNKNOWN,
]


@dataclass
class EpsteinFiles:
    all_files: list[Path] = field(init=False)
    emails: list[Email] = field(default_factory=list)
    imessage_logs: list[MessengerLog] = field(default_factory=list)
    json_files: list[JsonFile] = field(default_factory=list)
    other_files: list[OtherFile] = field(default_factory=list)
    timer: Timer = field(default_factory=lambda: Timer())

    # Analytics / calculations
    email_author_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))
    email_authors_to_device_signatures: dict[str, set] = field(default_factory=lambda: defaultdict(set))
    email_device_signatures_to_authors: dict[str, set] = field(default_factory=lambda: defaultdict(set))
    email_recipient_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))
    unknown_recipient_email_ids: set[str] = field(default_factory=set)

    def __post_init__(self):
        """Iterate through files and build appropriate objects."""
        self.all_files = sorted([f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')])
        documents = []
        file_type_count = defaultdict(int)

        # Read through and classify all the files
        for file_arg in self.all_files:
            doc_timer = Timer(decimals=2)
            document = Document(file_arg)
            cls = document_cls(document)

            if document.length() == 0:
                logger.warning(f"Skipping empty file: {document}]")
                continue
            elif args.skip_other_files and cls == OtherFile and file_type_count[cls.__name__] > 1:
                document.log(f"Skipping OtherFile...")
                continue

            documents.append(cls(file_arg, lines=document.lines, text=document.text))
            logger.info(str(documents[-1]))
            file_type_count[cls.__name__] += 1

            if doc_timer.seconds_since_start() > SLOW_FILE_SECONDS:
                doc_timer.print_at_checkpoint(f"Slow file: {documents[-1]} processed")

        self.emails = Document.sort_by_timestamp([d for d in documents if isinstance(d, Email)])
        self.imessage_logs = Document.sort_by_timestamp([d for d in documents if isinstance(d, MessengerLog)])
        self.other_files = Document.sort_by_timestamp([d for d in documents if isinstance(d, (JsonFile, OtherFile))])
        self.json_files = [doc for doc in self.other_files if isinstance(doc, JsonFile)]
        self._tally_email_data()

    @classmethod
    def get_files(cls, timer: Timer | None = None) -> 'EpsteinFiles':
        """Alternate constructor that reads/writes a pickled version of the data ('timer' arg is for logging)."""
        timer = timer or Timer()

        if PICKLED_PATH.exists() and not args.overwrite_pickle:
            with gzip.open(PICKLED_PATH, 'rb') as file:
                epstein_files = pickle.load(file)
                epstein_files.timer = timer
                timer_msg = f"Loaded {len(epstein_files.all_files):,} documents from '{PICKLED_PATH}'"
                epstein_files.timer.print_at_checkpoint(f"{timer_msg} ({file_size_str(PICKLED_PATH)})")
                return epstein_files

        logger.warning(f"Building new cache file, this will take a few minutes...")
        epstein_files = EpsteinFiles(timer=timer)

        if args.skip_other_files:
            logger.warning(f"Not writing pickled data because --skip-other-files")
        else:
            with gzip.open(PICKLED_PATH, 'wb') as file:
                pickle.dump(epstein_files, file)
                logger.warning(f"Pickled data to '{PICKLED_PATH}' ({file_size_str(PICKLED_PATH)})...")

        timer.print_at_checkpoint(f'Processed {len(epstein_files.all_files):,} documents')
        return epstein_files

    def all_documents(self) -> Sequence[Document]:
        return self.imessage_logs + self.emails + self.other_files

    def all_emailers(self, include_useless: bool = False) -> list[str | None]:
        """Returns all emailers except Epstein and EXCLUDED_EMAILERS, sorted from least frequent to most."""
        names = [a for a in self.email_author_counts.keys()] + [r for r in self.email_recipient_counts.keys()]
        names = names if include_useless else [e for e in names if e is None or e.lower() not in EXCLUDED_EMAILERS]
        return sorted(list(set(names)), key=lambda e: self.email_author_counts[e] + self.email_recipient_counts[e])

    def docs_matching(
            self,
            pattern: re.Pattern | str,
            names: list[str | None] | None = None
        ) -> list[SearchResult]:
        """Find documents whose text matches a pattern (file_type and names args limit the documents searched)."""
        results: list[SearchResult] = []

        for doc in self.all_documents():
            if names and doc.author not in names:
                continue

            lines = doc.matching_lines(pattern)

            if len(lines) > 0:
                results.append(SearchResult(doc, lines))

        return results

    def earliest_email_at(self, author: str | None) -> datetime:
        return self.emails_for(author)[0].timestamp

    def last_email_at(self, author: str | None) -> datetime:
        return self.emails_for(author)[-1].timestamp

    def email_conversation_length_in_days(self, author: str | None) -> int:
        return days_between(self.earliest_email_at(author), self.last_email_at(author))

    def email_signature_substitution_counts(self) -> dict[str, int]:
        """Return the number of times an email signature was replaced with "<...snipped...>" for each author."""
        substitution_counts = defaultdict(int)

        for email in self.emails:
            for name, num_replaced in email.signature_substitution_counts.items():
                substitution_counts[name] += num_replaced

        return substitution_counts

    def email_unknown_recipient_file_ids(self) -> list[str]:
        return sorted(list(self.unknown_recipient_email_ids))

    def emails_by(self, author: str | None) -> list[Email]:
        return Document.sort_by_timestamp([e for e in self.emails if e.author == author])

    def emails_for(self, author: str | None) -> list[Email]:
        """Returns emails to or from a given 'author' sorted chronologically."""
        emails = self.emails if author == EVERYONE else (self.emails_by(author) + self.emails_to(author))

        if len(emails) == 0:
            raise RuntimeError(f"No emails found for '{author}'")

        return Document.sort_by_timestamp(Document.uniquify(emails))

    def emails_to(self, author: str | None) -> list[Email]:
        if author is None:
            emails = [e for e in self.emails if len(e.recipients) == 0 or None in e.recipients]
        else:
            emails = [e for e in self.emails if author in e.recipients]

        return Document.sort_by_timestamp(emails)

    def get_documents_by_id(self, file_ids: str | list[str]) -> list[Document]:
        file_ids = listify(file_ids)
        docs = [doc for doc in self.all_documents() if doc.file_id in file_ids]

        if len(docs) != len(file_ids):
            logger.warning(f"{len(file_ids)} file IDs provided but only {len(docs)} Epstein files found!")

        return docs

    def json_metadata(self) -> str:
        """Create a JSON string containing metadata for all the files."""
        metadata = {
            'files': {
                Email.__name__: _sorted_metadata(self.emails),
                JsonFile.__name__: _sorted_metadata(self.json_files),
                MessengerLog.__name__: _sorted_metadata(self.imessage_logs),
                OtherFile.__name__: _sorted_metadata(self.non_json_other_files()),
            },
            'people': {
                name: highlighted_group.get_info(name)
                for highlighted_group in HIGHLIGHTED_NAMES
                if isinstance(highlighted_group, HighlightedNames)
                for name, description in highlighted_group.emailers.items()
                if description
            }
        }

        return json.dumps(metadata, indent=4, sort_keys=True)

    def non_duplicate_emails(self) -> list[Email]:
        return [email for email in self.emails if not email.is_duplicate()]

    def non_json_other_files(self) -> list[OtherFile]:
        return [doc for doc in self.other_files if not isinstance(doc, JsonFile)]

    def print_files_summary(self) -> None:
        table = build_table('Summary of Document Types')
        add_cols_to_table(table, ['File Type', 'Files', 'Author Known', 'Author Unknown', 'Duplicates'])

        def add_row(label: str, docs: list):
            known = None if isinstance(docs[0], JsonFile) else Document.known_author_count(docs)

            table.add_row(
                label,
                f"{len(docs):,}",
                f"{known:,}" if known is not None else NA_TXT,
                f"{len(docs) - known:,}" if known is not None else NA_TXT,
                f"{len([d for d in docs if d.is_duplicate()])}",
            )

        add_row('Emails', self.emails)
        add_row('iMessage Logs', self.imessage_logs)
        add_row('JSON Data', self.json_files)
        add_row('Other', self.non_json_other_files())
        console.print(Align.center(table))
        console.line()

    def print_emails_for(self, _author: str | None) -> list[Email]:
        """Print complete emails to or from a particular 'author'. Returns the Emails that were printed."""
        conversation_length = self.email_conversation_length_in_days(_author)
        emails = self.emails_for(_author)
        unique_emails = [email for email in emails if not email.is_duplicate()]
        author = _author or UNKNOWN

        print_author_panel(
            f"Found {len(unique_emails)} {author} emails starting {emails[0].timestamp.date()} over {conversation_length:,} days",
            get_style_for_name(author),
            get_info_for_name(author)
        )

        self.print_emails_table_for(_author)
        last_printed_email_was_duplicate = False

        for email in emails:
            if email.is_duplicate():
                console.print(Padding(email.duplicate_file_txt().append('...'), (0, 0, 0, 4)))
                last_printed_email_was_duplicate = True
            else:
                if last_printed_email_was_duplicate:
                    console.line()

                console.print(email)
                last_printed_email_was_duplicate = False

        return emails

    def print_emails_table_for(self, author: str | None) -> None:
        emails = [email for email in self.emails_for(author) if not email.is_duplicate()]  # Remove dupes
        console.print(Align.center(Email.build_table(emails, author)), '\n')

    def print_email_device_info(self) -> None:
        print_panel(f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown", padding=(2, 0, 0, 0), centered=True)
        console.print(_build_signature_table(self.email_authors_to_device_signatures, (AUTHOR, DEVICE_SIGNATURE)))
        console.print(_build_signature_table(self.email_device_signatures_to_authors, (DEVICE_SIGNATURE, AUTHOR), ', '))

    def table_of_emailers(self) -> Table:
        attributed_emails = [e for e in self.non_duplicate_emails() if e.author]
        footer = f"Identified authors of {len(attributed_emails):,} out of {len(self.non_duplicate_emails()):,} emails."
        counts_table = build_table("Email Counts", caption=footer)

        add_cols_to_table(counts_table, [
            'Name',
            'Num',
            'Sent',
            "Recv",
            {'name': 'First', 'highlight': True},
            {'name': 'Last', 'style': LAST_TIMESTAMP_STYLE},
            JMAIL,
            'eMedia',
            'eWeb',
            'Twitter',
        ])

        emailer_counts = {
            emailer: self.email_author_counts[emailer] + self.email_recipient_counts[emailer]
            for emailer in self.all_emailers(True)
        }

        for name, count in sort_dict(emailer_counts):
            style = get_style_for_name(name, default_style=DEFAULT_NAME_STYLE)
            emails = self.emails_for(name)

            counts_table.add_row(
                Text.from_markup(link_markup(epsteinify_name_url(name or UNKNOWN), name or UNKNOWN, style)),
                str(count),
                str(self.email_author_counts[name]),
                str(self.email_recipient_counts[name]),
                emails[0].timestamp_without_seconds(),
                emails[-1].timestamp_without_seconds(),
                link_text_obj(search_jmail_url(name), JMAIL) if name else '',
                link_text_obj(epstein_media_person_url(name), 'eMedia') if is_ok_for_epstein_web(name) else '',
                link_text_obj(epstein_web_person_url(name), 'eWeb') if is_ok_for_epstein_web(name) else '',
                link_text_obj(search_twitter_url(name), 'search X') if name else '',
            )

        return counts_table

    def _tally_email_data(self) -> None:
        """Tally up summary info about Email objects."""
        for email in self.non_duplicate_emails():
            self.email_author_counts[email.author] += 1

            if len(email.recipients) == 0:
                self.unknown_recipient_email_ids.add(email.file_id)
                self.email_recipient_counts[None] += 1
            else:
                for recipient in email.recipients:
                    self.email_recipient_counts[recipient] += 1

            if email.sent_from_device:
                self.email_authors_to_device_signatures[email.author_or_unknown()].add(email.sent_from_device)
                self.email_device_signatures_to_authors[email.sent_from_device].add(email.author_or_unknown())


def count_by_month(docs: Sequence[Document]) -> dict[str | None, int]:
    counts: dict[str | None, int] = defaultdict(int)

    for doc in docs:
        if doc.timestamp:
            counts[doc.timestamp.date().isoformat()[0:7]] += 1
        else:
            counts[None] += 1

    return counts


def document_cls(doc: Document) -> Type[Document]:
    search_area = doc.text[0:5000]  # Limit search area to avoid pointless scans of huge files

    if doc.length() == 0:
        return Document
    if doc.text[0] == '{':
        return JsonFile
    elif isinstance(doc.config, EmailCfg) or (DETECT_EMAIL_REGEX.match(search_area) and doc.config is None):
        return Email
    elif MSG_REGEX.search(search_area):
        return MessengerLog
    else:
        return OtherFile


def is_ok_for_epstein_web(name: str | None) -> bool:
    """Return True if it's likely that EpsteinWeb has a page for this name."""
    if name is None or ' ' not in name:
        return False
    elif '@' in name or '/' in name or '??' in name:
        return False
    elif name in INVALID_FOR_EPSTEIN_WEB:
        return False

    return True


def _build_signature_table(keyed_sets: dict[str, set[str]], cols: tuple[str, str], join_char: str = '\n') -> Padding:
    title = 'Signatures Used By Authors' if cols[0] == AUTHOR else 'Authors Seen Using Signatures'
    table = build_table(title, header_style="bold reverse", show_lines=True)

    for i, col in enumerate(cols):
        table.add_column(col.title() + ('s' if i == 1 else ''))

    new_dict = dict_sets_to_lists(keyed_sets)

    for k in sorted(new_dict.keys()):
        table.add_row(highlighter(k or UNKNOWN), highlighter(join_char.join(sorted(new_dict[k]))))

    return Padding(table, DEVICE_SIGNATURE_PADDING)


def _sorted_metadata(docs: Sequence[Document]) -> list[Metadata]:
    docs_sorted_by_id = sorted(docs, key=lambda d: d.file_id)
    return [json_safe(d.metadata()) for d in docs_sorted_by_id]
