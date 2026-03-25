from dataclasses import dataclass, field

from epstein_files.documents.document import Document


@dataclass
class Picture(Document):

    def raw_text(self) -> str:
        """Reload the raw data from the underlying file and return it."""
        return str(self.file_id)
