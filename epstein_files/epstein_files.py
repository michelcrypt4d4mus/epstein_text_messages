import gzip
import json
import pickle
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence, Type, cast

from rich.table import Table
from yaralyzer.util.helpers.interaction_helper import ask_to_proceed

from epstein_files.documents.document import Document
from epstein_files.documents.documents.doc_cfg import EMAIL_PROPS_TO_COPY, PROPS_TO_COPY, Metadata
from epstein_files.documents.documents.search_result import SearchResult
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.emails.constants import UNINTERESTING_EMAILERS
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MSG_REGEX, MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES
from epstein_files.output.rich import console
from epstein_files.people.person import INVALID_FOR_EPSTEIN_WEB, Person
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import *
from epstein_files.util.env import args, logger
from epstein_files.util.helpers.data_helpers import flatten, json_safe, uniquify
from epstein_files.util.helpers.file_helper import all_txt_paths, doj_txt_paths, extract_file_id, file_size_str
from epstein_files.util.timer import Timer

SLOW_FILE_SECONDS = 1.0


@dataclass
class EpsteinFiles:
    """
    Attributes:
        file_paths (list[Path]): paths to Epstein related text documents
        emails (list[Email]): all `Email` objects
        imessage_logs (list[MessengerLog]): all `MessengerLog` objects
        other_files (list[OtherFile]): all `OtherFile` objects
        timer (Timer): for logging only
        uninteresting_ccs (list[Name]): names of tangential people who were just CCed once or similar
    """
    file_paths: list[Path] = field(init=False)

    # Derived fields
    documents: list[Document] = field(default_factory=list)
    timer: Timer = field(default_factory=lambda: Timer())
    uninteresting_ccs: list[Name] = field(default_factory=list)
    _empty_file_ids: set[str] = field(default_factory=set)

    @property
    def all_doj_files(self) -> Sequence[DojFile | Email]:
        """All files with the filename EFTAXXXXXX, including those that were turned into `Email` objs."""
        return [doc for doc in self.documents if doc.file_info.is_doj_file]

    @property
    def doj_files(self) -> list[DojFile]:
        """Only returns DojFile type. Emails derived from DOJ files are not included."""
        return [f for f in self.other_files if isinstance(f, DojFile)]

    @property
    def emails(self) -> list[Email]:
        return [d for d in self.documents if isinstance(d, Email)]

    @property
    def emailers(self) -> list[Person]:
        """All the people who sent or received an email."""
        authors = [email.author for email in self.emails]
        recipients = flatten([email.recipients for email in self.emails])
        return self.person_objs(uniquify(authors + recipients))

    @property
    def imessage_logs(self) -> list[MessengerLog]:
        return [d for d in self.documents if isinstance(d, MessengerLog)]

    @property
    def json_files(self) -> list[JsonFile]:
        """JSON files from the November document dump, mostly Apple ads related."""
        return [d for d in self.other_files if isinstance(d, JsonFile)]

    @property
    def interesting_other_files(self) -> Sequence[OtherFile]:
        """`OtherFile` objects that have been deemed of interest."""
        return [f for f in self.other_files if f.is_interesting]

    @property
    def non_json_other_files(self) -> list[OtherFile]:
        return [doc for doc in self.other_files if not isinstance(doc, JsonFile)]

    @property
    def other_files(self) -> Sequence[OtherFile]:
        return [d for d in self.documents if isinstance(d, OtherFile)]

    @property
    def uninteresting_emailers(self) -> list[Name]:
        """Emailers whom we don't want to print a separate section for because they're just CCed."""
        if '_uninteresting_emailers' not in vars(self):
            self._uninteresting_emailers = sorted(uniquify(UNINTERESTING_EMAILERS + self.uninteresting_ccs))

        return self._uninteresting_emailers

    @property
    def unique_documents(self) -> Sequence[Document]:
        return Document.without_dupes(self.documents)

    @property
    def unique_emails(self) -> list[Email]:
        """All `Email` objects except for duplicates."""
        return Document.without_dupes(self.emails)

    def __post_init__(self):
        """Iterate through files and build appropriate objects."""
        self.file_paths = sorted(all_txt_paths(), reverse=True)
        self.documents = self._load_file_paths(self.file_paths)
        self._finalize_data_and_write_to_disk()

    @classmethod
    def get_files(cls, timer: Timer | None = None) -> 'EpsteinFiles':
        """Alternate constructor that reads/writes a pickled version of the data ('timer' arg is for logging)."""
        timer = timer or Timer()

        if args.pickle_path.exists() and not args.overwrite_pickle:
            with gzip.open(args.pickle_path, 'rb') as file:
                epstein_files = pickle.load(file)
                timer_msg = f"Loaded {len(epstein_files.file_paths):,} documents from '{args.pickle_path}'"
                timer.print_at_checkpoint(f"{timer_msg} ({file_size_str(args.pickle_path)})")

            if args.reload_doj:
                epstein_files.reload_doj_files()
            elif args.load_new:
                epstein_files.load_new_files()

            return epstein_files

        logger.warning(f"Building new cache file, this will take a few minutes...")
        epstein_files = EpsteinFiles()
        timer.print_at_checkpoint(f'Processed {len(epstein_files.file_paths):,} files, {OtherFile.num_synthetic_cfgs_created} synthetic configs')
        return epstein_files

    def docs_matching(self, pattern: re.Pattern | str, names: list[Name] | None = None) -> list[SearchResult]:
        """Find documents whose text matches `pattern` optionally limited to only docs involving `name`)."""
        results: list[SearchResult] = []

        for doc in self.documents:
            if names and doc.author not in names:
                continue

            lines = doc.lines_matching(pattern)

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
        """Mapping of authors to all the device signatures identified in their history."""
        signatures = defaultdict(set)

        for email in [e for e in self.unique_emails if e.sent_from_device]:
            signatures[email.author_or_unknown].add(email.sent_from_device)

        return signatures

    def email_device_signatures_to_authors(self) -> dict[str, set[str]]:
        """Mapping of device signatures to all the users who ever signed an email with them."""
        signatures = defaultdict(set)

        for email in [e for e in self.unique_emails if e.sent_from_device]:
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
            logger.warning(f"No emails found for '{name}'")

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
        docs = [d for d in self.documents if d.file_id in file_ids]

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

    def load_new_files(self) -> None:
        current_docs = self._docs_by_id()
        self.file_paths = all_txt_paths()
        new_paths = [p for p in self.file_paths if extract_file_id(p) not in current_docs]

        if not new_paths:
            logger.warning(f"No new files found, doing nothing.")
            return

        self._finalize_new_docs_if_approved(self._load_file_paths(new_paths))

    def reload_doj_files(self) -> None:
        """Reload only the DOJ PDF extracts (keep HOUSE_OVERSIGHT stuff unchanged)."""
        def doj_file_counts_str():
            return f"(have {len(self.all_doj_files)}, {len(self.doj_files)} non-email)"

        timer = Timer()
        logger.warning(f"Reloading all DOJ files {doj_file_counts_str()}...")
        self._finalize_data_and_write_to_disk(self._load_file_paths(doj_txt_paths()))
        timer.print_at_checkpoint(f"Reloaded {len(self.doj_files)} DOJ files {doj_file_counts_str()}")

    def overview_table(self) -> Table:
        """Table showing file counts by type."""
        table = Document.file_info_table('Files Overview', 'File Type')
        table.add_row('Emails', *Document.files_info_row(self.emails))
        table.add_row('iMessage Logs', *Document.files_info_row(self.imessage_logs))
        table.add_row('JSON Data', *Document.files_info_row(self.json_files, True))
        table.add_row('Other', *Document.files_info_row(self.non_json_other_files))
        return table

    def repair_ids(self, ids: list[str]) -> None:
        """Repair/reload the ids specified and save to disk."""
        doc_paths = [d.file_path for d in self.documents if d.file_id in ids]

        if len(doc_paths) != len(ids):
            raise RuntimeError(f"{len(ids)} specified but only {len(doc_paths)} Document objects found!")

        self._finalize_new_docs_if_approved(self._load_file_paths(doc_paths))

    def save_to_disk(self) -> None:
        """Write a pickled version of this `EpsteinFiles` object with all documents etc."""
        with gzip.open(args.pickle_path, 'wb') as file:
            pickle.dump(self, file)
            logger.warning(f"Pickled data to '{args.pickle_path}' ({file_size_str(args.pickle_path)})...")

    def unknown_recipient_ids(self) -> list[str]:
        """IDs of emails whose recipient is not known."""
        return sorted([e.file_id for e in self.emails if None in e.recipients or not e.recipients])

    def _copy_duplicate_doc_properties(self) -> None:
        """Ensure dupe emails have the properties of the emails they duplicate to capture any repairs, config etc."""
        for doc in self.documents:
            if not doc.duplicate_of_id:
                continue

            original = self.get_id(doc.duplicate_of_id)
            props_to_copy = (EMAIL_PROPS_TO_COPY + PROPS_TO_COPY) if isinstance(doc, Email) else PROPS_TO_COPY

            for field_name in props_to_copy:
                original_prop = getattr(original, field_name)
                duplicate_prop = getattr(doc, field_name)

                if original_prop != duplicate_prop:
                    doc.warn(f"Replacing {field_name} {duplicate_prop} with {original_prop} from duplicated '{original.file_id}'")
                    setattr(doc, field_name, original_prop)

    def _docs_by_id(self) -> Mapping[str, Document]:
        return {doc.file_id: doc for doc in self.documents}

    def _finalize_data_and_write_to_disk(self, new_docs: list[Document] | None = None) -> None:
        """Handle computation of fields related to uninterestingness, relationships between documents, etc."""
        new_docs = new_docs or []

        if new_docs:
            old_num_docs = len(self.documents)
            new_doc_ids = [d.file_info.file_id for d in new_docs]
            self.documents = [d for d in self.documents if d.file_info.file_id not in new_doc_ids]  # Remove existing
            logger.warning(f"Adding {len(new_docs)} Documents (replacing {old_num_docs - len(self.documents)} existing)")
            self.documents += new_docs

        self._set_uninteresting_ccs()
        self._copy_duplicate_doc_properties()
        self._find_email_attachments_and_set_is_first_for_user()
        self.documents = Document.sort_by_timestamp(self.documents)
        self.save_to_disk()

    def _find_email_attachments_and_set_is_first_for_user(self) -> None:
        for email in self.emails:
            email.attached_docs = []  # Remove all attachments before re-finding them if it's a repair

        for file in [f for f in self.other_files if f.config and f.config.attached_to_email_id]:
            email: Email = self.get_id(file.config.attached_to_email_id, required_type=Email)
            email.attached_docs.append(file)

            if file.config.timestamp:  # Don't overwrite configured timestamps (think of a book or article attachment)
                continue
            elif file.timestamp and file.timestamp != email.timestamp:
                file.warn(f"Overwriting '{file.timestamp}' with {email}'s timestamp {email.timestamp}")

            file.timestamp = email.timestamp

        # Set the _is_first_for_user flag on the earliest Email we have for each user.
        for emailer in self.emailers:
            if emailer.name in INVALID_FOR_EPSTEIN_WEB or len(emailer.unique_emails) == 0:
                continue

            emailer.unique_emails[0]._is_first_for_user = True

    def _finalize_new_docs_if_approved(self, new_docs: list[Document]) -> None:
        """Same as _finalize_data_and_write_to_disk() but prints new docs and asks for permission."""
        console.print(*new_docs)
        logger.warning(f"Finalizing {len(new_docs)} files: {[d.file_id for d in new_docs]}")
        ask_to_proceed("Looks good?")
        self._finalize_data_and_write_to_disk(new_docs)

    def _load_file_paths(self, file_paths: list[Path]) -> list[Document]:
        """Load a list of file paths into a list of `Document` object subclasses."""
        file_type_count = defaultdict(int)  # Hack used by --skip-other-files option to get a few files parsed before skipping the rest
        docs: list[Document] = []

        for file_path in file_paths:
            doc_timer = Timer(decimals=2)
            document = Document(file_path)
            cls = document_cls(document)

            if document.length == 0:
                if document.file_id not in self._empty_file_ids:
                    document.warn(f"Skipping empty file...")
                    self._empty_file_ids.add(document.file_id)

                continue

            docs.append(cls(file_path, lines=document.lines, text=document.text).printable_document())
            logger.info(str(docs[-1]))
            file_type_count[cls.__name__] += 1

            if doc_timer.seconds_since_start() > SLOW_FILE_SECONDS:
                doc_timer.print_at_checkpoint(f"Slow file: {docs[-1]} processed")

        return docs

    def _set_uninteresting_ccs(self) -> None:
        """Extract the recipients of emails configured has having uninteresting CCs or BCCs."""
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
    elif doc.file_info.is_doj_file:
        return DojFile
    if doc.text[0] == '{':
        return JsonFile
    elif doc.is_email:  # TODO: right now we setup the DojFile which makes an Email obj only later at print time
        return Email
    elif MSG_REGEX.search(search_area):
        return MessengerLog
    else:
        return OtherFile


def _sorted_metadata(docs: Sequence[Document]) -> list[Metadata]:
    return [json_safe(d.metadata) for d in Document.sort_by_id(docs)]
