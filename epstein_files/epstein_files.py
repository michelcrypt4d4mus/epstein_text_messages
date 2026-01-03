import gzip
import pickle
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal, Sequence, Type

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
from epstein_files.util.constant.urls import (EPSTEIN_WEB, JMAIL, epsteinify_name_url, epstein_web_person_url,
     search_jmail_url, search_twitter_url)
from epstein_files.util.constants import *
from epstein_files.util.data import Timer, dict_sets_to_lists, listify, sort_dict
from epstein_files.util.doc_cfg import EmailCfg
from epstein_files.util.env import args, logger
from epstein_files.util.file_helper import DOCS_DIR, PICKLED_PATH, file_size_str
from epstein_files.util.highlighted_group import get_info_for_name, get_style_for_name
from epstein_files.util.rich import (DEFAULT_NAME_STYLE, NA_TXT, add_cols_to_table, console, highlighter,
     link_text_obj, link_markup, print_author_header, print_centered, print_other_site_link, print_panel,
     print_section_header, vertically_pad)
from epstein_files.util.search_result import SearchResult

DEVICE_SIGNATURE = 'Device Signature'
DEVICE_SIGNATURE_PADDING = (1, 0)
NOT_INCLUDED_EMAILERS = [e.lower() for e in (USELESS_EMAILERS + [JEFFREY_EPSTEIN])]

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

    # Analytics / calculations
    email_author_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))
    email_authors_to_device_signatures: dict[str, set] = field(default_factory=lambda: defaultdict(set))
    email_device_signatures_to_authors: dict[str, set] = field(default_factory=lambda: defaultdict(set))
    email_recipient_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))
    _email_unknown_recipient_file_ids: set[str] = field(default_factory=set)

    def __post_init__(self):
        """Iterate through files and build appropriate objects."""
        self.all_files = [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]
        documents = []

        # Read through and classify all the files
        for file_arg in self.all_files:
            logger.info(f"Scanning '{file_arg.name}'...")
            #doc_timer = Timer(decimals=4)
            doc = Document(file_arg)

            if doc.length == 0:
                logger.warning(f"Skipping empty file: {doc}")
                continue

            document = document_cls(doc)(file_arg, text=doc.text)
            documents.append(document)
            logger.info(str(document))
            #doc_timer.print_at_checkpoint(f"Processed {document}")

        self.emails = Document.sort_by_timestamp([d for d in documents if isinstance(d, Email)])
        self.imessage_logs = Document.sort_by_timestamp([d for d in documents if isinstance(d, MessengerLog)])
        self.other_files = Document.sort_by_timestamp([d for d in documents if isinstance(d, (JsonFile, OtherFile))])
        self._tally_email_data()

    @classmethod
    def get_files(cls, timer: Timer | None = None) -> 'EpsteinFiles':
        """Alternate constructor that reads/writes a pickled version of the data ('timer' arg is for logging)."""
        timer = timer or Timer()

        if (args.pickled and PICKLED_PATH.exists()) and not args.overwrite_pickle:
            with gzip.open(PICKLED_PATH, 'rb') as file:
                epstein_files = pickle.load(file)
                timer.print_at_checkpoint(f"Loaded {len(epstein_files.all_files):,} documents from '{PICKLED_PATH}' ({file_size_str(PICKLED_PATH)})")
                return epstein_files

        epstein_files = EpsteinFiles()

        if args.overwrite_pickle or not PICKLED_PATH.exists():
            with gzip.open(PICKLED_PATH, 'wb') as file:
                pickle.dump(epstein_files, file)
                logger.warning(f"Pickled data to '{PICKLED_PATH}' ({file_size_str(PICKLED_PATH)})...")

        timer.print_at_checkpoint(f'Processed {len(epstein_files.all_files):,} documents')
        return epstein_files

    def all_documents(self) -> Sequence[Document]:
        return self.imessage_logs + self.emails + self.other_files

    def all_emailers(self, include_useless: bool = False) -> list[str | None]:
        """Returns all emailers except Epstein and USELESS_EMAILERS, sorted from least frequent to most."""
        names = [a for a in self.email_author_counts.keys()] + [r for r in self.email_recipient_counts.keys()]
        names = names if include_useless else [e for e in names if e is None or e.lower() not in NOT_INCLUDED_EMAILERS]
        return sorted(list(set(names)), key=lambda e: self.email_author_counts[e] + self.email_recipient_counts[e])

    def attributed_email_count(self) -> int:
        return sum([i for author, i in self.email_author_counts.items() if author != UNKNOWN])

    def docs_matching(
            self,
            pattern: re.Pattern | str,
            names: list[str | None] | None = None
        ) -> list[SearchResult]:
        """Find documents whose text matches a pattern (file_type and names args limit the documents searched)."""
        results: list[SearchResult] = []

        for doc in self.all_documents():
            lines = doc.lines_matching_txt(pattern)

            if names and ((not isinstance(doc, (Email, MessengerLog))) or doc.author not in names):
                continue

            if len(lines) > 0:
                results.append(SearchResult(doc, lines))

        return results

    def earliest_email_at(self, author: str | None) -> datetime:
        return self.emails_for(author)[0].timestamp

    def last_email_at(self, author: str | None) -> datetime:
        return self.emails_for(author)[-1].timestamp

    def email_conversation_length_in_days(self, author: str | None) -> int:
        return (self.last_email_at(author) - self.earliest_email_at(author)).days + 1

    def email_signature_substitution_counts(self) -> dict[str, int]:
        """Return the number of times an email signature was replaced with "<...snipped...>" for each author."""
        substitution_counts = defaultdict(int)

        for email in self.emails:
            for name, num_replaced in email.signature_substitution_counts.items():
                substitution_counts[name] += num_replaced

        return substitution_counts

    def email_unknown_recipient_file_ids(self) -> list[str]:
        return sorted(list(self._email_unknown_recipient_file_ids))

    def emails_by(self, author: str | None) -> list[Email]:
        return [e for e in self.emails if e.author == author]

    def emails_for(self, author: str | None) -> list[Email]:
        """Returns emails to or from a given 'author' sorted chronologically."""
        emails = self.emails if author == EVERYONE else (self.emails_by(author) + self.emails_to(author))

        if len(emails) == 0:
            raise RuntimeError(f"No emails found for '{author}'")

        return Document.sort_by_timestamp(Document.uniquify(emails))

    def emails_to(self, author: str | None) -> list[Email]:
        if author is None:
            return [e for e in self.emails if len(e.recipients) == 0 or None in e.recipients]
        else:
            return [e for e in self.emails if author in e.recipients]

    def get_documents_by_id(self, file_ids: list[str]) -> list[Document]:
        docs = [doc for doc in self.all_documents() if doc.file_id in file_ids]

        if len(docs) != len(file_ids):
            logger.warning(f"{len(file_ids)} file IDs provided but only {len(docs)} Epstein files found!")

        return docs

    def imessage_logs_for(self, author: str | None | list[str | None]) -> Sequence[MessengerLog]:
        return MessengerLog.logs_for(author, self.imessage_logs)

    def identified_imessage_log_count(self) -> int:
        return len([log for log in self.imessage_logs if log.author])

    def print_files_summary(self) -> None:
        dupes = defaultdict(int)

        for doc in self.all_documents():
            if doc.is_duplicate:
                dupes[doc.class_name()] += 1

        table = Table()
        add_cols_to_table(table, ['File Type', 'Files', 'Author Known', 'Author Unknown', 'Duplicates'])

        def add_row(label: str, docs: list, known: int | None = None, dupes: int | None = None):
            table.add_row(
                label,
                f"{len(docs):,}",
                f"{known:,}" if known else NA_TXT,
                f"{len(docs) - known:,}" if known else NA_TXT,
                f"{dupes:,}" if dupes else NA_TXT,
            )

        add_row('iMessage Logs', self.imessage_logs, self.identified_imessage_log_count())
        add_row('Emails', self.emails, len([e for e in self.emails if e.author]), dupes[EMAIL_CLASS])
        add_row('JSON Data', self.json_files, dupes=0)
        add_row('Other', self.other_files, dupes=dupes[OTHER_FILE_CLASS])
        console.print(Align.center(table))
        console.line()

    def print_emails_for(self, _author: str | None) -> list[Email]:
        """Print complete emails to or from a particular 'author'. Returns the Emails that were printed."""
        conversation_length = self.email_conversation_length_in_days(_author)
        emails = self.emails_for(_author)
        author = _author or UNKNOWN

        print_author_header(
            f"Found {len(emails)} {author} emails starting {emails[0].timestamp.date()} over {conversation_length:,} days",
            get_style_for_name(author),
            get_info_for_name(author)
        )

        self.print_emails_table_for(_author)
        last_printed_email_was_duplicate = False

        for email in emails:
            if email.is_duplicate:
                console.print(Padding(email.duplicate_file_txt().append('...'), (0, 0, 0, 4)))
                last_printed_email_was_duplicate = True
            else:
                if last_printed_email_was_duplicate:
                    console.line()

                console.print(email)
                last_printed_email_was_duplicate = False

        return emails

    def print_emails_table_for(self, author: str | None) -> None:
        emails = [email for email in self.emails_for(author) if not email.is_duplicate]  # Remove dupes
        console.print(Align.center(Email.build_table(emails, author)), '\n')

    def print_email_device_info(self) -> None:
        print_panel(f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown", padding=(4, 0, 0, 0), centered=True)
        console.print(build_signature_table(self.email_authors_to_device_signatures, (AUTHOR, DEVICE_SIGNATURE)))
        console.print(build_signature_table(self.email_device_signatures_to_authors, (DEVICE_SIGNATURE, AUTHOR), ', '))

    def print_emailer_counts_table(self) -> None:
        footer = f"Identified authors of {self.attributed_email_count()} emails out of {len(self.emails)} potential email files."
        counts_table = Table(title=f"Email Counts", caption=footer, header_style="bold")
        add_cols_to_table(counts_table, ['Name', 'Count', 'Sent', "Recv'd", JMAIL, EPSTEIN_WEB, 'Twitter'])

        emailer_counts = {
            e: self.email_author_counts[e] + self.email_recipient_counts[e]
            for e in self.all_emailers(True)
        }

        for p, count in sort_dict(emailer_counts):
            style = get_style_for_name(p, default_style=DEFAULT_NAME_STYLE)

            counts_table.add_row(
                Text.from_markup(link_markup(epsteinify_name_url(p or UNKNOWN), p or UNKNOWN, style)),
                str(count),
                str(self.email_author_counts[p]),
                str(self.email_recipient_counts[p]),
                '' if p is None else link_text_obj(search_jmail_url(p), JMAIL),
                '' if not is_ok_for_epstein_web(p) else link_text_obj(epstein_web_person_url(p), EPSTEIN_WEB.lower()),
                '' if p is None else link_text_obj(search_twitter_url(p), 'search X'),
            )

        console.print(vertically_pad(counts_table, 2))

    def print_imessage_summary(self) -> None:
        """Print summary table and stats for text messages."""
        console.print(MessengerLog.summary_table(self.imessage_logs))
        text_summary_msg = f"\nDeanonymized {self.identified_imessage_log_count()} of "
        text_summary_msg += f"{len(self.imessage_logs)} {TEXT_MESSAGE} logs found in {len(self.all_files)} files."
        console.print(text_summary_msg)
        imessage_msg_count = sum([len(log.messages()) for log in self.imessage_logs])
        console.print(f"Found {imessage_msg_count} total text messages in {len(self.imessage_logs)} conversations.")
        console.print(f"(Last deploy found 4668 messages in 77 conversations)", style='dim')

    def print_other_files_table(self) -> list[OtherFile]:
        """Returns the OtherFile objects that were interesting enough to print."""
        interesting_files = [doc for doc in self.other_files if args.all_other_files or doc.is_interesting()]
        header_pfx = '' if args.all_other_files else 'Selected '
        print_section_header(f"{FIRST_FEW_LINES} of {len(interesting_files)} {header_pfx}Files That Are Neither Emails Nor Text Msgs")

        if not args.all_other_files:
            print_centered(f"(the other site is uncurated and has all {len(self.other_files)} unclassifiable files and {len(self.emails):,} emails)", style='dim')
            print_other_site_link(False)
            console.line(2)

        console.print(OtherFile.build_table(interesting_files))
        logger.warning(f"Skipped {len(self.other_files) - len(interesting_files)} uninteresting files...")
        return interesting_files

    def _tally_email_data(self) -> None:
        """Tally up summary info about Email objects."""
        for email in self.emails:
            self.email_author_counts[email.author] += 1

            if len(email.recipients) == 0:
                self._email_unknown_recipient_file_ids.add(email.file_id)
                self.email_recipient_counts[None] += 1
            else:
                for recipient in email.recipients:
                    self.email_recipient_counts[recipient] += 1

            if email.sent_from_device:
                self.email_authors_to_device_signatures[email.author_or_unknown()].add(email.sent_from_device)
                self.email_device_signatures_to_authors[email.sent_from_device].add(email.author_or_unknown())


def build_signature_table(keyed_sets: dict[str, set[str]], cols: tuple[str, str], join_char: str = '\n') -> Padding:
    title = 'Signatures Used By Authors' if cols[0] == AUTHOR else 'Authors Seen Using Signatures'
    table = Table(header_style="bold reverse", show_lines=True, title=title)

    for i, col in enumerate(cols):
        table.add_column(col.title() + ('s' if i == 1 else ''))

    new_dict = dict_sets_to_lists(keyed_sets)

    for k in sorted(new_dict.keys()):
        table.add_row(highlighter(k or UNKNOWN), highlighter(join_char.join(sorted(new_dict[k]))))

    return Padding(table, DEVICE_SIGNATURE_PADDING)


def document_cls(document: Document) -> Type[Document]:
    if document.text[0] == '{':
        return JsonFile
    elif MSG_REGEX.search(document.text):
        return MessengerLog
    elif DETECT_EMAIL_REGEX.match(document.text) or isinstance(document.config, EmailCfg):
        return Email
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


def count_by_month(docs: Sequence[Document]) -> dict[str | None, int]:
    counts: dict[str | None, int] = defaultdict(int)

    for doc in docs:
        if doc.timestamp:
            counts[doc.timestamp.date().isoformat()[0:7]] += 1
        else:
            counts[None] += 1

    return counts
