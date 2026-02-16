import gzip
import json
import pickle
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Sequence, Type, cast

from rich.table import Table

from epstein_files.documents.document import Document
from epstein_files.documents.documents.doc_cfg import Metadata
from epstein_files.documents.documents.search_result import SearchResult
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.emails.constants import UNINTERESTING_EMAILERS
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MSG_REGEX, MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES, HighlightedNames
from epstein_files.people.person import INVALID_FOR_EPSTEIN_WEB, Person
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import *
from epstein_files.util.env import DOCS_DIR, args, logger
from epstein_files.util.helpers.data_helpers import flatten, json_safe, listify, uniquify
from epstein_files.util.helpers.file_helper import doj_txt_paths, file_size_str
from epstein_files.util.timer import Timer

DUPLICATE_PROPS_TO_COPY = ['author', 'recipients', 'timestamp']  # TODO: also copy the config, get rid of synthetic configs
SLOW_FILE_SECONDS = 1.0


@dataclass
class EpsteinFiles:
    all_files: list[Path] = field(init=False)
    emails: list[Email] = field(default_factory=list)
    imessage_logs: list[MessengerLog] = field(default_factory=list)
    other_files: list[OtherFile] = field(default_factory=list)
    timer: Timer = field(default_factory=lambda: Timer())
    uninteresting_ccs: list[Name] = field(default_factory=list)

    @property
    def all_documents(self) -> Sequence[Document]:
        return Document.sort_by_timestamp(self.imessage_logs + self.emails + self.other_files)

    @property
    def all_doj_files(self) -> Sequence[DojFile | Email]:
        """All files with the filename EFTAXXXXXX, including those that were turned into Email objs."""
        return [doc for doc in self.all_documents if doc.is_doj_file]

    @property
    def doj_files(self) -> list[DojFile]:
        return Document.sort_by_timestamp([f for f in self.other_files if isinstance(f, DojFile)])

    @property
    def emailers(self) -> list[Person]:
        """All the people who sent or received an email."""
        authors = [email.author for email in self.emails]
        recipients = flatten([email.recipients for email in self.emails])
        return self.person_objs(uniquify(authors + recipients))

    @property
    def json_files(self) -> list[JsonFile]:
        return Document.sort_by_timestamp([d for d in self.other_files if isinstance(d, JsonFile)])

    @property
    def interesting_other_files(self) -> Sequence[OtherFile]:
        return [f for f in self.other_files if f.is_interesting]

    @property
    def non_duplicate_emails(self) -> list[Email]:
        return Document.without_dupes(self.emails)

    @property
    def non_json_other_files(self) -> list[OtherFile]:
        return [doc for doc in self.other_files if not isinstance(doc, JsonFile)]

    @property
    def uninteresting_emailers(self) -> list[Name]:
        """Emailers whom we don't want to print a separate section for because they're just CCed."""
        if '_uninteresting_emailers' not in vars(self):
            self._uninteresting_emailers = sorted(uniquify(UNINTERESTING_EMAILERS + self.uninteresting_ccs))

        return self._uninteresting_emailers

    def __post_init__(self):
        """Iterate through files and build appropriate objects."""
        file_paths = [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]
        file_paths.extend(doj_txt_paths())
        self.all_files = sorted(file_paths, reverse=True)

        # Split up by type
        docs = self._load_file_paths(self.all_files)
        self.emails = Document.sort_by_timestamp([d for d in docs if isinstance(d, Email)])
        self.imessage_logs = Document.sort_by_timestamp([d for d in docs if isinstance(d, MessengerLog)])
        self.other_files = Document.sort_by_timestamp([d for d in docs if isinstance(d, OtherFile)])

        # Set interdependent fields, dupes, etc.
        self._finalize_data()

    @classmethod
    def get_files(cls, timer: Timer | None = None) -> 'EpsteinFiles':
        """Alternate constructor that reads/writes a pickled version of the data ('timer' arg is for logging)."""
        timer = timer or Timer()

        if args.pickle_path.exists() and not args.overwrite_pickle and not args.skip_other_files:
            with gzip.open(args.pickle_path, 'rb') as file:
                epstein_files = pickle.load(file)
                timer_msg = f"Loaded {len(epstein_files.all_files):,} documents from '{args.pickle_path}'"
                timer.print_at_checkpoint(f"{timer_msg} ({file_size_str(args.pickle_path)})")

            if args.reload_doj:
                epstein_files.reload_doj_files()

            return epstein_files

        logger.warning(f"Building new cache file, this will take a few minutes...")
        epstein_files = EpsteinFiles()

        if args.skip_other_files:
            logger.warning(f"Not writing pickled data because --skip-other-files")
        else:
            epstein_files.save_to_disk()

        timer.print_at_checkpoint(f'Processed {len(epstein_files.all_files):,} files, {OtherFile.num_synthetic_cfgs_created} synthetic configs')
        return epstein_files

    def docs_matching(self, pattern: re.Pattern | str, names: list[Name] | None = None) -> list[SearchResult]:
        """Find documents whose text matches `pattern` optionally limited to only docs involving `name`)."""
        results: list[SearchResult] = []

        for doc in self.all_documents:
            if names and doc.author not in names:
                continue

            lines = doc.matching_lines(pattern)

            if args.min_line_length:
                lines = [line for line in lines if len(line.line) > args.min_line_length]

            if len(lines) > 0:
                results.append(SearchResult(doc, lines))

        return results

    def earliest_email_at(self, name: Name) -> datetime:
        """First email timestamp sent to or received by `name`."""
        return self.emails_for(name)[0].timestamp

    def last_email_at(self, name: Name) -> datetime:
        """Last email timestamp sent to or received by `name`."""
        return self.emails_for(name)[-1].timestamp

    def email_author_counts(self) -> dict[Name, int]:
        """Returns dict counting up how many emails were written by each person."""
        return {
            person.name: len(person.unique_emails_by)
            for person in self.emailers if len(person.unique_emails_by) > 0
        }

    def email_authors_to_device_signatures(self) -> dict[str, set[str]]:
        signatures = defaultdict(set)

        for email in [e for e in self.non_duplicate_emails if e.sent_from_device]:
            signatures[email.author_or_unknown].add(email.sent_from_device)

        return signatures

    def email_device_signatures_to_authors(self) -> dict[str, set[str]]:
        signatures = defaultdict(set)

        for email in [e for e in self.non_duplicate_emails if e.sent_from_device]:
            signatures[email.sent_from_device].add(email.author_or_unknown)

        return signatures

    def email_recipient_counts(self) -> dict[Name, int]:
        """Returns dict counting up how many emails were received by each person."""
        return {p.name: len(p.unique_emails_to) for p in self.emailers if len(p.unique_emails_to) > 0}

    def email_signature_substitution_counts(self) -> dict[str, int]:
        """Return the number of times an email signature was replaced with "<...snipped...>" for each author."""
        substitution_counts = defaultdict(int)

        for email in self.emails:
            for name, num_replaced in email.signature_substitution_counts.items():
                substitution_counts[name] += num_replaced

        return substitution_counts

    def emails_by(self, author: Name) -> list[Email]:
        """All emails sent by `author` (including dupes)."""
        return Document.sort_by_timestamp([e for e in self.emails if e.author == author])

    def emails_for(self, name: Name) -> list[Email]:
        """All emails to or from a given 'name' sorted chronologically (including dupes)."""
        emails = self.emails_by(name) + self.emails_to(name)

        if len(emails) == 0:
            raise RuntimeError(f"No emails found for '{name}'")

        return Document.sort_by_timestamp(Document.uniquify(emails))

    def emails_to(self, name: Name) -> list[Email]:
        """All `Email`s sent to `name` (including dupes)."""
        if name is None:
            emails = [e for e in self.emails if len(e.recipients) == 0 or None in e.recipients]
        else:
            emails = [e for e in self.emails if name in e.recipients]

        return Document.sort_by_timestamp(emails)

    def get_ids(self, file_ids: list[str], rebuild: bool = False) -> Sequence[Document]:
        """Get `Document` objects for `file_ids`. If `rebuild` is True then rebuild `Document` from .txt file."""
        docs = [d for d in self.all_documents if d.file_id in file_ids]

        if len(docs) != len(file_ids):
            logger.warning(f"{len(file_ids)} file IDs provided but only {len(docs)} documents found!")

        return [d.reload() if rebuild else d for d in docs]

    def get_id(self, file_id: str, rebuild: bool = False, required_type: Type[Document] = Document) -> Document:
        """Singular ID version of `get_ids()` but with option to require a type of document subclass."""
        doc = self.get_ids([file_id], rebuild)[0]

        if required_type:
            if not isinstance(doc, required_type):
                raise ValueError(f"No {required_type.__name__} found for {file_id} (found {doc})")

        return doc

    def imessage_logs_for(self, name: Name) -> list[MessengerLog]:
        """Return `MessengerLog` objects where Epstein's counterparty is `name`."""
        return [log for log in self.imessage_logs if name == log.author]

    def json_metadata(self) -> str:
        """Create a JSON string containing metadata for all the files."""
        metadata = {
            'files': {
                Email.__name__: _sorted_metadata(self.emails),
                JsonFile.__name__: _sorted_metadata(self.json_files),
                MessengerLog.__name__: _sorted_metadata(self.imessage_logs),
                OtherFile.__name__: _sorted_metadata(self.non_json_other_files),
            },
            'people': {
                contact.name: highlighted_group.info_for(contact.name, include_category=True)
                for highlighted_group in HIGHLIGHTED_NAMES
                for contact in highlighted_group.contacts
                if contact.info
            }
        }

        return json.dumps(metadata, indent=4, sort_keys=True)

    def person_objs(self, names: list[Name]) -> list[Person]:
        """Construct Person objects for a list of names."""
        return [
            Person(
                name=name,
                emails=self.emails_for(name),
                imessage_logs=self.imessage_logs_for(name),
                is_uninteresting=name in self.uninteresting_emailers,
                other_files=[f for f in self.other_files if name and name == f.author]
            )
            for name in names
        ]

    def reload_doj_files(self) -> None:
        """Reload only the DOJ PDF extracts (keep HOUSE_OVERSIGHT stuff unchanged)."""
        def doj_file_counts_str():
            return f"(have {len(self.all_doj_files)}, {len(self.doj_files)} non-email)"

        timer = Timer()
        logger.warning(f"Only reloading DOJ files {doj_file_counts_str()}...")
        house_oversight_emails = [e for e in self.emails if not e.is_doj_file]
        docs = self._load_file_paths(doj_txt_paths())
        doj_emails = [d for d in docs if isinstance(d, Email)]
        self.doj_files = Document.sort_by_timestamp([d for d in docs if isinstance(d, DojFile)])
        self.emails = Document.sort_by_timestamp(house_oversight_emails + doj_emails)
        timer.print_at_checkpoint(f"Reloaded DOJ files {doj_file_counts_str()}")
        self._finalize_data()
        self.save_to_disk()

    def overview_table(self) -> Table:
        table = Document.file_info_table('Files Overview', 'File Type')
        table.add_row('Emails', *Document.files_info_row(self.emails))
        table.add_row('iMessage Logs', *Document.files_info_row(self.imessage_logs))
        table.add_row('JSON Data', *Document.files_info_row(self.json_files, True))
        table.add_row('Other', *Document.files_info_row(self.non_json_other_files))
        return table

    def save_to_disk(self) -> None:
        """Write a pickled version of this `EpsteinFiles` object with all documents etc."""
        with gzip.open(args.pickle_path, 'wb') as file:
            pickle.dump(self, file)
            logger.warning(f"Pickled data to '{args.pickle_path}' ({file_size_str(args.pickle_path)})...")

    def unknown_recipient_ids(self) -> list[str]:
        """IDs of emails whose recipient is not known."""
        return sorted([e.file_id for e in self.emails if None in e.recipients or not e.recipients])

    def _copy_duplicate_email_properties(self) -> None:
        """Ensure dupe emails have the properties of the emails they duplicate to capture any repairs, config etc."""
        for email in self.emails:
            if not email.duplicate_of_id:
                continue

            original = self.get_id(email.duplicate_of_id, required_type=Email)

            for field_name in DUPLICATE_PROPS_TO_COPY:
                original_prop = getattr(original, field_name)
                duplicate_prop = getattr(email, field_name)

                if original_prop != duplicate_prop:
                    email.warn(f"Replacing {field_name} {duplicate_prop} with {original_prop} from duplicated '{original.file_id}'")
                    setattr(email, field_name, original_prop)

        # Resort in case any timestamp were updated
        self.emails = Document.sort_by_timestamp(self.emails)

    def _finalize_data(self):
        """Handle computation of fields related to uninterestingness, relationships between documents, etc."""
        self._set_uninteresting_ccs()
        self._copy_duplicate_email_properties()
        self._find_email_attachments_and_set_is_first_for_user()

    def _find_email_attachments_and_set_is_first_for_user(self) -> None:
        for other_file in (self.other_files + self.doj_files):
            if other_file.config and other_file.config.attached_to_email_id:
                email: Email = self.get_id(other_file.config.attached_to_email_id, required_type=Email)
                email.attached_docs.append(other_file)

                if other_file.timestamp \
                        and other_file.timestamp != email.timestamp \
                        and not other_file.config_timestamp:
                    other_file.warn(f"Overwriting '{other_file.timestamp}' with {email}'s timestamp {email.timestamp}")

                other_file.timestamp = email.timestamp

        # Set the _is_first_for_user flag on the earliest Email we have for each user.
        for emailer in self.emailers:
            if emailer.name in INVALID_FOR_EPSTEIN_WEB or len(emailer.unique_emails) == 0:
                continue

            emailer.unique_emails[0]._is_first_for_user = True

    def _load_file_paths(self, file_paths: list[Path]) -> Sequence[Document]:
        """Load a list of file paths into a list of `Document` object subclasses."""
        file_type_count = defaultdict(int)  # Hack used by --skip-other-files option to get a few files parsed before skipping the rest
        docs: Sequence[Document] = []

        for file_path in file_paths:
            doc_timer = Timer(decimals=2)
            document = Document(file_path)
            cls = document_cls(document)

            if document.length == 0:
                logger.warning(f"Skipping empty file: {document}]")
                continue
            elif args.skip_other_files and cls == OtherFile and file_type_count[cls.__name__] > 1:
                document.log(f"Skipping OtherFile...")
                continue

            docs.append(cls(file_path, lines=document.lines, text=document.text).printable_document())
            logger.info(str(docs[-1]))
            file_type_count[cls.__name__] += 1

            if doc_timer.seconds_since_start() > SLOW_FILE_SECONDS:
                doc_timer.print_at_checkpoint(f"Slow file: {docs[-1]} processed")

        return docs

    def _set_uninteresting_ccs(self) -> None:
        for email in [e for e in self.emails if e.config and e.config.has_uninteresting_bccs]:
            self.uninteresting_ccs += [bcc.lower() for bcc in cast(list[str], email.header.bcc)]

        for email in [e for e in self.emails if e.config and e.config.has_uninteresting_ccs]:
            self.uninteresting_ccs += email.recipients

        self.uninteresting_ccs = sorted(uniquify(self.uninteresting_ccs))
        logger.info(f"Extracted uninteresting_ccs: {self.uninteresting_ccs}")


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

    if doc.length == 0:
        return Document
    elif doc.is_doj_file:
        return DojFile
    if doc.text[0] == '{':
        return JsonFile
    elif Document.is_email(doc):  # TODO: right now we setup the DojFile which makes an Email obj only later at print time
        return Email
    elif MSG_REGEX.search(search_area):
        return MessengerLog
    else:
        return OtherFile


def _sorted_metadata(docs: Sequence[Document]) -> list[Metadata]:
    return [json_safe(d.metadata) for d in Document.sort_by_id(docs)]
