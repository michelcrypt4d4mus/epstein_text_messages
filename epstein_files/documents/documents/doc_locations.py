from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Mapping

from rich.text import Text

from epstein_files.output.rich import prefix_with, styled_dict
from epstein_files.util.helpers.file_helper import extract_file_id, is_doj_file


@dataclass(kw_only=True)
class DocLocation:
    """
    Attributes:
        external_url (str): a web URL where the source document can theoretically be seen
        file_id (str): ID extracted from the filename
        local_path (Path): local path of the document's underlying .txt file
        local_pdf_path (Path, optional): local path to the source PDF the .txt was extracted from (if any)
        source_url (str, optional): official government source URL
    """
    external_url: str
    file_id: str = field(init=False)
    local_path: Path
    local_pdf_path: Path | None = None
    source_url: str = ''
    # jmail_url: str

    @property
    def as_dict(self) -> Mapping[str, str | Path]:
        return {'file_id': self.file_id, **self.paths, **self.urls}

    @property
    def paths(self) -> Mapping[str, Path]:
        return {k: Path(v) for k, v in self._props_with_suffix('path').items() if v}

    @property
    def urls(self) -> Mapping[str, str]:
        urls = {k: str(v) for k, v in self._props_with_suffix('url').items() if v}
        urls = {k: (v if v.startswith('http') else f"https://{v}") for k, v in urls.items()}
        return urls

    def __post_init__(self):
        self.file_id = extract_file_id(self.local_path)

        if is_doj_file(self.local_path):
            self.source_url = self.external_url

    def _props_with_suffix(self, suffix: str) -> Mapping[str, str]:
        return {k: v for k, v in asdict(self).items() if k.endswith(suffix)}

    def __rich__(self) -> Text:
        """Text obj with local paths and URLs."""
        txt_lines = styled_dict(self.as_dict, sep=': ')
        return prefix_with(txt_lines, ' ', pfx_style='grey', indent=2)

    def __str__(self) -> str:
        lines = [f"{k:>40}: {v}" for k, v in asdict(self).items() if k != 'file_id']
        return '\n'.join(lines)
