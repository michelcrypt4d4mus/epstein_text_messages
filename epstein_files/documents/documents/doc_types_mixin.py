from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Mapping, Sequence

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.emails.dropsite_email import DropsiteEmail
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile


@dataclass
class DocTypesMixin(ABC):
    """Mixin for classes that maintain a list of `Document`s and want to sift by type."""
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
        """dict with file IDs as keys and Document objs as values."""
        self._docs_by_id = self._docs_by_id or {doc.file_id: doc for doc in self._documents}
        return self._docs_by_id

    @property
    def documents(self) -> Sequence[Document]:
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
        return len(self.unique_documents)

    @property
    def num_emails(self) -> int:
        return len(self.unique_emails)

    @property
    def other_files(self) -> Sequence[OtherFile]:
        return OtherFile.filter_for_type(self.documents)

    @property
    def unique_documents(self) -> Sequence[Document]:
        """Excludes duplicates and email attachments."""
        return Document.without_dupes(self.documents)

    @property
    def unique_doj_files(self) -> Sequence[DojFile]:
        return Document.without_dupes(self.doj_files)

    @property
    def unique_emails(self) -> list[Email]:
        """All `Email` objects except for duplicates."""
        return Document.without_dupes(self.emails)
