import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from rich.text import Text

from epstein_files.util.file_helper import extract_file_id, is_doj_file
from epstein_files.util.constant.names import Name
from epstein_files.util.constant.strings import indented
from epstein_files.util.constant.urls import link_text_obj
from epstein_files.util.rich import ARCHIVE_LINK_COLOR, prefix_with, styled_dict


@dataclass(kw_only=True)
class ContactInfo:
    """
    Attributes:
        `name` (Name): Person or organization name
        `email_pattern` (str, optional): regex pattern to match this person in email headers
        `info` (str, optional): biographical info about this person
    """
    name: Name
    emailer_pattern: str = ''
    info: str = ''
    emailer_regex: re.Pattern = field(init=False)

    # jmail_url: str


    def __post_init__(self):
        self.file_id = extract_file_id(self.local_path)

        if is_doj_file(self.local_path):
            self.source_url = self.external_url

    def _props_with_suffix(self, suffix: str) -> dict[str, str]:
        return {k: v for k, v in asdict(self).items() if k.endswith(suffix)}

    def __rich__(self) -> Text:
        """Text obj with local paths and URLs."""
        txt_lines = styled_dict({'file_id': self.file_id, **self.paths, **self.urls}, key_style='khaki3', sep=': ')
        return prefix_with(txt_lines, ' ', pfx_style='grey', indent=2)

    def __str__(self) -> str:
        lines = [f"{k:>40}: {v}" for k, v in asdict(self).items() if k != 'file_id']
        return '\n'.join(lines)
