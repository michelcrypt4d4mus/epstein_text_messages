import gzip
import json
import pickle
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Sequence, Type, cast

from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.documents.email import DETECT_EMAIL_REGEX, Email
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MSG_REGEX, MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.person import Person
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import *
from epstein_files.util.data import flatten, json_safe, listify, uniquify
from epstein_files.util.doc_cfg import EmailCfg, Metadata
from epstein_files.util.env import DOCS_DIR, args, logger
from epstein_files.util.file_helper import file_size_str
from epstein_files.util.highlighted_group import HIGHLIGHTED_NAMES, HighlightedNames
from epstein_files.util.rich import NA_TXT, add_cols_to_table, build_table, console, print_centered
from epstein_files.util.search_result import SearchResult
from epstein_files.util.timer import Timer

DUPLICATE_PROPS_TO_COPY = ['author', 'recipients', 'timestamp']
PICKLED_PATH = Path("the_epstein_files.pkl.gz")
SLOW_FILE_SECONDS = 1.0


@dataclass
class EpsteinFiles:
    all_files: list[Path] = field(init=False)
    emails: list[Email] = field(default_factory=list)
    imessage_logs: list[MessengerLog] = field(default_factory=list)
    json_files: list[JsonFile] = field(default_factory=list)
    other_files: list[OtherFile] = field(default_factory=list)
    timer: Timer = field(default_factory=lambda: Timer())

    def __post_init__(self):
        """Iterate through files and build appropriate objects."""
        self.all_files = sorted([f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')])
        documents = []
        file_type_count = defaultdict(int)  # Hack used by --skip-other-files option

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
        self._copy_duplicate_email_properties()

    @classmethod
    def get_files(cls, timer: Timer | None = None) -> 'EpsteinFiles':
        """Alternate constructor that reads/writes a pickled version of the data ('timer' arg is for logging)."""
        timer = timer or Timer()

        if PICKLED_PATH.exists() and not args.overwrite_pickle and not args.skip_other_files:
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

    def author_objs(self, names: list[str | None]) -> list[Person]:
        """Construct Author objects for a list of names."""
        return [
            Person(
                name=name,
                emails=self.emails_for(name),
                imessage_logs=[l for l in self.imessage_logs if name == l.author]
            )
            for name in names
        ]

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

    def email_author_counts(self) -> dict[str | None, int]:
        return {
            person.name: len(person.unique_emails_by())
            for person in self.emailers() if len(person.unique_emails_by()) > 0
        }

    def email_authors_to_device_signatures(self) -> dict[str, set[str]]:
        signatures = defaultdict(set)

        for email in [e for e in self.non_duplicate_emails() if e.sent_from_device]:
            signatures[email.author_or_unknown()].add(email.sent_from_device)

        return signatures

    def email_device_signatures_to_authors(self) -> dict[str, set[str]]:
        signatures = defaultdict(set)

        for email in [e for e in self.non_duplicate_emails() if e.sent_from_device]:
            signatures[email.sent_from_device].add(email.author_or_unknown())

        return signatures

    def email_recipient_counts(self) -> dict[str | None, int]:
        return {
            person.name: len(person.unique_emails_to())
            for person in self.emailers() if len(person.unique_emails_to()) > 0
        }

    def email_signature_substitution_counts(self) -> dict[str, int]:
        """Return the number of times an email signature was replaced with "<...snipped...>" for each author."""
        substitution_counts = defaultdict(int)

        for email in self.emails:
            for name, num_replaced in email.signature_substitution_counts.items():
                substitution_counts[name] += num_replaced

        return substitution_counts

    def emailers(self) -> list[Person]:
        """All the people who sent or received an email."""
        authors = [email.author for email in self.emails]
        recipients = flatten([email.recipients for email in self.emails])
        return self.author_objs(uniquify(authors + recipients))

    def emails_by(self, author: str | None) -> list[Email]:
        return Document.sort_by_timestamp([e for e in self.emails if e.author == author])

    def emails_for(self, author: str | None) -> list[Email]:
        """Returns emails to or from a given 'author' sorted chronologically."""
        emails = self.emails_by(author) + self.emails_to(author)

        if len(emails) == 0:
            raise RuntimeError(f"No emails found for '{author}'")

        return Document.sort_by_timestamp(Document.uniquify(emails))

    def emails_to(self, author: str | None) -> list[Email]:
        if author is None:
            emails = [e for e in self.emails if len(e.recipients) == 0 or None in e.recipients]
        else:
            emails = [e for e in self.emails if author in e.recipients]

        return Document.sort_by_timestamp(emails)

    def for_ids(self, file_ids: str | list[str]) -> list[Document]:
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
        table = build_table('File Overview')
        add_cols_to_table(table, ['File Type', 'Count', 'Author Known', 'Author Unknown', 'Duplicates'])
        table.columns[1].justify = 'right'

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
        print_centered(table)
        console.line()

    def unknown_recipient_ids(self) -> list[str]:
        """IDs of emails whose recipient is not known."""
        return sorted([e.file_id for e in self.emails if None in e.recipients or not e.recipients])

    def _copy_duplicate_email_properties(self) -> None:
        """Ensure dupe emails have the properties of the emails they duplicate to capture any repairs, config etc."""
        for email in self.emails:
            if not email.is_duplicate():
                continue

            original = cast(Email, self.for_ids(email.duplicate_of_id())[0])

            for field_name in DUPLICATE_PROPS_TO_COPY:
                original_prop = getattr(original, field_name)
                duplicate_prop = getattr(email, field_name)

                if original_prop != duplicate_prop:
                    logger.warning(f"Replacing '{email.file_id}' {field_name} {duplicate_prop} with {original_prop} from duplicated '{original.file_id}'")
                    setattr(email, field_name, original_prop)

        # Resort in case any timestamp were updated
        self.emails = Document.sort_by_timestamp(self.emails)


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


def _sorted_metadata(docs: Sequence[Document]) -> list[Metadata]:
    docs_sorted_by_id = sorted(docs, key=lambda d: d.file_id)
    return [json_safe(d.metadata()) for d in docs_sorted_by_id]
