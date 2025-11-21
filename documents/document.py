import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from rich.text import Text

from util.file_helper import extract_file_id
from util.rich import logger

MULTINEWLINE_REGEX = re.compile(r"\n{3,}")


@dataclass
class Document:
    file_path: Path
    filename: str = field(init=False)
    text: str = field(init=False)
    file_id: str = field(init=False)
    file_lines: list[str] = field(init=False)
    num_lines: int = field(init=False)
    length: int = field(init=False)

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)
        self.text = self.load_file()
        self.length = len(self.text)
        self.file_lines = self.text.split('\n')
        self.num_lines = len(self.file_lines)


    def load_file(self):
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        with open(self.file_path) as f:
            file_text = f.read()
            file_text = file_text[1:] if (len(file_text) > 0 and file_text[0] == '\ufeff') else file_text  # remove BOM
            file_text = file_text.strip()
            file_lines = [l.strip() for l in file_text.split('\n') if not l.startswith('HOUSE OVERSIGHT')]
            return MULTINEWLINE_REGEX.sub('\n\n\n', '\n'.join(file_lines))

    def top_lines(self, n: int = 10) -> str:
        return '\n'.join(self.file_lines[0:n])

    def log_top_lines(self, n: int = 10, msg: str | None = None) -> None:
        msg = f"{msg + '. ' if msg else ''}Top lines of '{self.filename}' ({self.num_lines} lines):"
        logger.info(f"{msg}:\n\n{self.top_lines(n)}")


@dataclass
class CommunicationDocument(Document):
    author: str | None = field(init=False)
    author_style: str = field(init=False)
    author_txt: Text = field(init=False)
    timestamp: datetime | None = field(init=False)

    def __post_init__(self):
        super().__post_init__()
