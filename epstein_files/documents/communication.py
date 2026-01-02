import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar

from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, Document
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constants import FALLBACK_TIMESTAMP
from epstein_files.util.file_cfg import MessageCfg
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.rich import key_value_txt

TIMESTAMP_SECONDS_REGEX = re.compile(r":\d{2}$")


@dataclass
class Communication(Document):
    """Superclass for Email and MessengerLog."""
    author_style: str = 'white'
    author_txt: Text = field(init=False)
    config: MessageCfg | None = None
    timestamp: datetime = FALLBACK_TIMESTAMP  # TODO this default sucks (though it never happens)

    def __post_init__(self):
        super().__post_init__()
        self.author_style = get_style_for_name(self.author_or_unknown())
        self.author_txt = Text(self.author_or_unknown(), style=self.author_style)

    def author_or_unknown(self) -> str:
        return self.author or UNKNOWN

    def description(self) -> Text:
        return self._description().append(CLOSE_PROPERTIES_CHAR)

    def raw_document_link_txt(self, _style: str = '', include_alt_link: bool = True) -> Text:
        """Overrides super() method to apply self.author_style."""
        return super().raw_document_link_txt(self.author_style, include_alt_link=include_alt_link)

    def timestamp_without_seconds(self) -> str:
        return TIMESTAMP_SECONDS_REGEX.sub('', str(self.timestamp))

    def _description(self) -> Text:
        """One line summary mostly for logging."""
        txt = super().description().append(', ')
        return txt.append(key_value_txt('author', Text(f"'{self.author_or_unknown()}'", style=self.author_style)))


CommunicationType = TypeVar('CommunicationType', bound=Document)
