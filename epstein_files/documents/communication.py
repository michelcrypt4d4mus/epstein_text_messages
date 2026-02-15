import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, cast

from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, Document
from epstein_files.documents.documents.doc_cfg import CommunicationCfg
from epstein_files.documents.emails.constants import FALLBACK_TIMESTAMP
from epstein_files.output.highlight_config import get_style_for_name, styled_name
from epstein_files.output.rich import styled_key_value
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constants import CONFIGS_BY_ID

TIMESTAMP_SECONDS_REGEX = re.compile(r":\d{2}$")


@dataclass
class Communication(Document):
    """Superclass for `Email` and `MessengerLog`."""
    timestamp: datetime = FALLBACK_TIMESTAMP  # TODO this default sucks (though it never happens)

    @property
    def author_or_unknown(self) -> str:
        return self.author or UNKNOWN

    @property
    def author_style(self) -> str:
        return get_style_for_name(self.author)

    @property
    def author_txt(self) -> Text:
        return styled_name(self.author)

    @property
    def config(self) -> CommunicationCfg | None:
        """Configured timestamp, if any."""
        cfg = CONFIGS_BY_ID.get(self.file_id)

        if not isinstance(cfg, CommunicationCfg):
            self.warn(f"Found config that's the wrong type! {repr(cfg)}")
            cfg = cast(CommunicationCfg, cfg)

        return cfg

    @property
    def is_recipient_uncertain(self) -> bool:
        return bool(self.config and self.config.uncertain_recipient)

    @property
    def summary(self) -> Text:
        """One line summary mostly for logging."""
        return self.summary_with_author.append(CLOSE_PROPERTIES_CHAR)

    @property
    def summary_with_author(self) -> Text:
        """Append author information to `super().summary`, bracket is left open."""
        txt = super().summary.append(', ')
        return txt.append(styled_key_value('author', Text(f"'{self.author_or_unknown}'", style=self.author_style)))

    @property
    def timestamp_without_seconds(self) -> str:
        return TIMESTAMP_SECONDS_REGEX.sub('', str(self.timestamp))

    def external_links_txt(self, _style: str = '', include_alt_links: bool = True) -> Text:
        """Overrides super() method to apply self.author_style."""
        return super().external_links_txt(self.author_style, include_alt_links=include_alt_links)

    @classmethod
    def default_category(self) -> str:
        return type(self).__name__.lower()
