import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar

from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, Document
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constants import FALLBACK_TIMESTAMP
from epstein_files.util.doc_cfg import CommunicationCfg
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.rich import key_value_txt

TIMESTAMP_SECONDS_REGEX = re.compile(r":\d{2}$")


@dataclass
class Communication(Document):
    """Superclass for Email and MessengerLog."""
    config: CommunicationCfg | None = None
    timestamp: datetime = FALLBACK_TIMESTAMP  # TODO this default sucks (though it never happens)

    def author_or_unknown(self) -> str:
        return self.author or UNKNOWN

    def author_style(self) -> str:
        return get_style_for_name(self.author_or_unknown())

    def author_txt(self) -> Text:
        return Text(self.author_or_unknown(), style=self.author_style())

    def is_attribution_uncertain(self) -> bool:
        return bool(self.config and self.config.is_attribution_uncertain)

    def external_links_txt(self, _style: str = '', include_alt_links: bool = True) -> Text:
        """Overrides super() method to apply self.author_style."""
        return super().external_links_txt(self.author_style(), include_alt_links=include_alt_links)

    def summary(self) -> Text:
        return self._summary().append(CLOSE_PROPERTIES_CHAR)

    def timestamp_without_seconds(self) -> str:
        return TIMESTAMP_SECONDS_REGEX.sub('', str(self.timestamp))

    def _summary(self) -> Text:
        """One line summary mostly for logging."""
        txt = super().summary().append(', ')
        return txt.append(key_value_txt('author', Text(f"'{self.author_or_unknown()}'", style=self.author_style())))


CommunicationType = TypeVar('CommunicationType', bound=Document)
