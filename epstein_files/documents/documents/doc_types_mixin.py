from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.emails.dropsite_email import DropsiteEmail
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile


@dataclass
class DocTypesMixin(ABC):
    _documents: list[Document] = field(default_factory=list)
    _docs_by_id: dict[str, Document] = field(default_factory=dict)

    @property
    def all_doj_files(self) -> Sequence[DojFile | Email]:
        """All files with the filename EFTAXXXXXX, including those that were turned into `Email` objs."""
        return [d for d in self.documents if d.file_info.is_doj_file]

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
        return [f for f in self.other_files if isinstance(f, DojFile)]

    @property
    def dropsite_emails(self) -> list[DropsiteEmail]:
        """Older emails from the Dropsite News collection exist as .eml files instead of .txt files."""
        return [f for f in self.documents if isinstance(f, DropsiteEmail)]

    @property
    def emails(self) -> list[Email]:
        return [d for d in self.documents if isinstance(d, Email)]

    @property
    def imessage_logs(self) -> list[MessengerLog]:
        return [d for d in self.documents if isinstance(d, MessengerLog)]

    @property
    def interesting_other_files(self) -> Sequence[OtherFile]:
        """`OtherFile` objects that have been deemed of interest."""
        return [f for f in self.other_files if f.is_interesting]

    @property
    def json_files(self) -> list[JsonFile]:
        """JSON files from the November document dump, mostly Apple ads related."""
        return [d for d in self.other_files if isinstance(d, JsonFile)]

    @property
    def local_extracts(self) -> Sequence[Document]:
        """Returns documents that are locally derived from source files."""
        return [d for d in self.documents if d.file_info.is_local_extract_file]

    @property
    def non_attachments(self) -> Sequence[OtherFile]:
        """Exclude `OtherFile` objs that are attached to `Email` objects."""
        return [d for d in self.other_files if not d._config.attached_to_email_id]

    @property
    def non_json_other_files(self) -> list[OtherFile]:
        return [doc for doc in self.other_files if not isinstance(doc, JsonFile)]

    @property
    def other_files(self) -> Sequence[OtherFile]:
        return [d for d in self.documents if isinstance(d, OtherFile)]

    @property
    def unique_documents(self) -> Sequence[Document]:
        """Excludes duplicates and email attachments."""
        return Document.without_dupes(self.documents)

    @property
    def unique_emails(self) -> list[Email]:
        """All `Email` objects except for duplicates."""
        return Document.without_dupes(self.emails)
