from dataclasses import dataclass

from rich.text import Text

from epstein_files.documents.document import Document


@dataclass
class SearchResult:
    """Simple class used for collecting documents that match a given search term."""
    document: Document
    lines: list[Text]  # The lines that match the search

    def unprefixed_lines(self) -> list[str]:
        return [line.plain.split(':', 1)[1] for line in self.lines]
