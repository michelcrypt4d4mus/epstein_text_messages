from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Mapping, Sequence

from rich.table import Table
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import Document, DocType
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.emails.dropsite_email import DropsiteEmail
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.rich import NA_TXT, add_cols_to_table, build_table
from epstein_files.util.helpers.data_helpers import uniquify, warn_on_dupes
from epstein_files.util.helpers.file_helper import file_size_to_str
from epstein_files.util.logging import logger

SUMMARY_TABLE_COLS: list[str | dict] = [
    'Count',
    {'name': 'Has Author', 'style': 'honeydew2'},
    {'name': 'No Author', 'style': 'wheat4'},
    {'name': 'Uncertain Author', 'style': 'royal_blue1 dim'},
    {'name': 'Size', 'justify': 'right', 'style': 'dim'},
]


@dataclass
class DocList:
    """Mixin for classes that maintain a list of `Document` objects and want to sift by type."""

    _documents: list[Document] = field(default_factory=list)
    _docs_by_id: dict[str, Document] = field(default_factory=dict)

    @property
    def all_doj_files(self) -> Sequence[DojFile | Email]:
        """All files with the filename EFTAXXXXXX, including those that were turned into `Email` objs."""
        return [d for d in self.documents if d.file_info.is_doj_file]

    @property
    def communications(self) -> Sequence[Communication]:
        """This person's `MessengerLog` and `Email` object."""
        return self.imessage_logs + self.emails

    @property
    def docs_by_id(self) -> Mapping[str, Document]:
        """`dict` with file IDs as keys and `Document` objs as values."""
        if self.num_docs != (old_len := len(self._docs_by_id)):
            logger.warning(f"Updating {type(self).__name__}._docs_by_id ({self.num_docs} docs vs. {old_len} in dict)")
            warn_on_dupes([d.file_id for d in self._documents])
            self._docs_by_id = {doc.file_id: doc for doc in self._documents}

        return self._docs_by_id

    @property
    def document_ids(self) -> list[str]:
        return [d.file_id for d in self.documents]

    @property
    def documents(self) -> Sequence[Document]:
        """Can be overloaded in subclasses to apply any necessary filters."""
        return self._documents

    @property
    def doj_files(self) -> list[DojFile]:
        """Only returns DojFile type. Emails derived from DOJ files are not included."""
        return DojFile.filter_for_type(self.other_files)

    @property
    def dropsite_emails(self) -> list[DropsiteEmail]:
        """Older emails from the Dropsite News collection exist as .eml files instead of .txt files."""
        return DropsiteEmail.filter_for_type(self.emails)

    @property
    def earliest_email_at(self) -> datetime:
        return self.emails[0].timestamp

    @property
    def earliest_email_date(self) -> date:
        return self.earliest_email_at.date()

    @property
    def emails(self) -> list[Email]:
        return Email.filter_for_type(self.documents)

    @property
    def emails_with_attachments(self) -> list[Email]:
        return [e for e in self.emails if e.attached_docs]

    @property
    def file_ids(self) -> set[str]:
        return set([d.file_id for d in self.documents])

    @property
    def imessage_logs(self) -> list[MessengerLog]:
        return MessengerLog.filter_for_type(self.documents)

    @property
    def interesting_other_files(self) -> Sequence[OtherFile]:
        """`OtherFile` objects that have been deemed of interest."""
        return [f for f in self.other_files if f.is_interesting]

    @property
    def json_files(self) -> list[JsonFile]:
        """JSON files from the November document dump, mostly Apple ads related."""
        return JsonFile.filter_for_type(self.other_files)

    @property
    def last_email_at(self) -> datetime:
        return self.emails[-1].timestamp

    @property
    def last_email_date(self) -> date:
        return self.last_email_at.date()

    @property
    def local_extracts(self) -> Sequence[Document]:
        """Returns documents that are locally derived from source files."""
        return [d for d in self.documents if d.file_info.is_local_extract_file]

    @property
    def non_attachments(self) -> Sequence[OtherFile]:
        """Exclude `OtherFile` objs that are attached to `Email` objects."""
        return [d for d in self.other_files if not d.is_email_attachment]

    @property
    def non_json_other_files(self) -> list[OtherFile]:
        return [doc for doc in self.other_files if not isinstance(doc, JsonFile)]

    @property
    def num_docs(self) -> int:
        return len(self._documents)

    @property
    def num_unique_docs(self) -> int:
        return len(self.unique_documents)

    @property
    def num_unique_emails(self) -> int:
        return len(self.unique_emails)

    @property
    def other_files(self) -> Sequence[OtherFile]:
        return OtherFile.filter_for_type(self.documents)

    @property
    def sorted_by_length(self) -> Sequence[Document]:
        """Sort by number of characters."""
        return sorted(self.documents, key=lambda d: d.file_info.file_size, reverse=True)

    @property
    def unique_documents(self) -> Sequence[Document]:
        """Excludes duplicates and email attachments."""
        return self.without_dupes(self.documents)

    @property
    def unique_doj_files(self) -> Sequence[DojFile]:
        return self.without_dupes(self.doj_files)

    @property
    def unique_emails(self) -> Sequence[Email]:
        """All `Email` objects except for duplicates."""
        return self.without_dupes(self.emails)

    @property
    def unique_other_files(self) -> Sequence[OtherFile]:
        """All `Email` objects except for duplicates."""
        return self.without_dupes(self.other_files)

    def count_by_month(self) -> Counter[str | None]:
        return Counter([d.timestamp.isoformat()[0:7] if d.timestamp else None for d in self.unique_documents])

    def print_ids(self, label: str = '') -> None:
        """Debug method to print raw string of IDs suitable for copy/paste."""
        type(self).print_doc_ids(self.uniquify_by_id(self.documents), label)

    @classmethod
    def files_summary_table(cls, title: str | Text, first_col_name: str) -> Table:
        """Empty table with appropriate cols for summarizing groups of files."""
        table = build_table(title)
        cols = [{'name': first_col_name, 'min_width': 14}] + SUMMARY_TABLE_COLS
        add_cols_to_table(table, cols, 'right')
        return table

    @classmethod
    def files_summary(cls, files: Sequence[Document], is_author_na: bool = False) -> dict[str, str | Text]:
        """Summary info about a group of files."""
        file_count = len(files)
        author_count = cls.known_author_count(files)

        # NOTE: Order matters!
        return {
            'count': str(file_count),
            'author_count': NA_TXT if is_author_na else str(author_count),
            'no_author_count': NA_TXT if is_author_na else str(file_count - author_count),
            'uncertain_author_count': NA_TXT if is_author_na else str(len([f for f in files if f._config.author_uncertain])),
            'bytes': file_size_to_str(sum([f.file_info.file_size for f in files])),
        }

    @classmethod
    def file_summary_row(cls, files: Sequence[Document], author_na: bool = False) -> Sequence[str | Text]:
        """Turn the values in the `cls.files_info()` dict into a list so they can be used as a table row."""
        return [v for v in cls.files_summary(files, author_na).values()]

    @classmethod
    def known_author_count(cls, docs: Sequence[Document]) -> int:
        """Number of elements of `docs` that have an author attribution."""
        return len([doc for doc in docs if doc.author])

    @classmethod
    def sort_by_id(cls, docs: Sequence['DocType']) -> Sequence['DocType']:
        return sorted(docs, key=lambda d: d.file_id)

    @classmethod
    def sort_by_timestamp(cls, docs: Sequence['DocType']) -> list['DocType']:
        return sorted(docs, key=lambda doc: doc.timestamp_sort_key)

    @classmethod
    def without_dupes(cls, docs: Sequence[DocType]) -> Sequence[DocType]:
        return [doc for doc in docs if not doc.is_duplicate]

    @classmethod
    def uniquify_by_id(cls, docs: Sequence['DocType'], allow_dupes: bool = True) -> Sequence['DocType']:
        """Uniquify by file_id."""
        id_map = {doc.file_id: doc for doc in docs}

        if not allow_dupes and (dupe_counts := warn_on_dupes([d.file_id for d in docs])):
            print(f"\n\n Duplicate IDs found:\n\n{' '.join([id for id in dupe_counts.keys()])}\n")

        return [doc for doc in id_map.values()]

    @classmethod
    def print_doc_ids(cls, docs: Sequence[Document], label: str = '') -> None:
        """Debug method to print raw string of IDs suitable for copy/paste."""
        print(f"\n\n IDs for {label}:\n\n{' '.join([doc.file_id for doc in docs])}\n")
