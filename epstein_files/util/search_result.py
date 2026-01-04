from dataclasses import dataclass

from rich.text import Text
# from epstein_files.documents.document import type Document


@dataclass
class MatchedLine:
    line: str
    line_number: int

    def __rich__(self) -> Text:
        return Text('').append(str(self.line_number), style='cyan').append(f":{self.line}")

    def __str__(self) -> str:
        return f"{self.line_number}:{self.line}"


@dataclass
class SearchResult:
    """Simple class used for collecting documents that match a given search term."""
    document: 'Document'
    lines: list[MatchedLine]
