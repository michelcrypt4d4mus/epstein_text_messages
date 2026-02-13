from dataclasses import asdict, dataclass, field
from pathlib import Path

from rich.text import Text

from epstein_files.util.file_helper import extract_file_id, is_doj_file
from epstein_files.util.constant.strings import indented
from epstein_files.util.constant.urls import link_text_obj
from epstein_files.util.rich import ARCHIVE_LINK_COLOR, prefix_with, style_key_value


@dataclass(kw_only=True)
class DocLocation:
    """
    Attributes:
        `external_url` (str): a web URL where the source document can theoretically be seen
        `local_path` (Path): local path of the document's underlying .txt file
        `local_pdf_path` (Path, optional): local path to the source PDF the .txt was extracted from (if any)
        `source_url` (str, optional): official government source URL
    """
    external_url: str
    file_id: str = field(init=False)
    local_path: Path
    local_pdf_path: Path | None = None
    source_url: str = ''
    # jmail_url: str

    def __post_init__(self):
        self.file_id = extract_file_id(self.local_path)

        if is_doj_file(self.local_path):
            self.source_url = self.external_url

    def __rich__(self) -> Text:
        """Text obj with local paths and URLs."""
        links = [style_key_value(k, link_text_obj(v), '') for k, v in asdict(self).items() if k.endswith('url')]
        paths = [style_key_value(k, v, 'magenta') for k, v in asdict(self).items() if k.endswith('path')]
        return prefix_with(links + paths, self.file_id)

    def __str__(self) -> str:
        lines = [f"{k:>40}: {v}" for k, v in asdict(self).items() if k != 'file_id']
        return '\n'.join(lines)
