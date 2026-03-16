import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import cast

from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, Document, EntityScanArg, coerce_entity_names
from epstein_files.documents.config.doc_cfg import CommunicationCfg
from epstein_files.output.highlight_config import get_style_for_name, styled_name
from epstein_files.output.rich import styled_key_value
from epstein_files.people.entity import Entity
from epstein_files.people.names import UNKNOWN, Name
from epstein_files.util.helpers.data_helpers import uniq_sorted
from epstein_files.util.helpers.rich_helpers import no_bold
from epstein_files.util.helpers.string_helper import timestamp_without_seconds


@dataclass
class Communication(Document):
    """
    Superclass for `Email` and `MessengerLog`.

    Attributes:
        extracted_recipients (list[Name]): People to whom this email was sent, extracted from `self.text`
    """
    extracted_recipients: list[Name] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.extracted_recipients = [] if self._config.recipients else self.extract_recipients()

    @property
    def author_str(self) -> str:
        return self.author or UNKNOWN

    @property
    def author_style(self) -> str:
        return get_style_for_name(self.author)

    @property
    def author_txt(self) -> Text:
        return styled_name(self.author)

    @property
    def border_style(self) -> str:
        return no_bold(self.author_style)

    @property
    def colored_external_links(self) -> Text:
        """Overrides super() method to apply `self.author_style`."""
        return self.file_info.build_external_links(self.recipient_style, with_alt_links=True)

    @property
    def config(self) -> CommunicationCfg | None:
        """Configured timestamp, if any."""
        cfg = super().config

        if cfg and not isinstance(cfg, CommunicationCfg):
            self._warn(f"Found config that's the wrong type! {repr(cfg)}")
            cfg = cast(CommunicationCfg, cfg)

        return cfg

    @property
    def _config(self) -> CommunicationCfg:
        # TODO: annoying to unnecessarily override superclass just to get python to understanding the types
        return self.config or self.dummy_cfg()

    @property
    def has_unknown_participant(self) -> bool:
        return None in self.participants

    @property
    def has_unknown_recipient(self) -> bool:
        return None in self.recipients

    @property
    def participants(self) -> set[Name]:
        """Author + recipients (including `None` if relevant)."""
        return set([self.author] + self.recipients)

    @property
    def participant_names(self) -> list[str]:
        """`self.participants` without None / unknown."""
        return sorted([p for p in self.participants if p])

    @property
    def recipients(self) -> list[Name]:
        return self._config.recipients or self.extracted_recipients

    @property
    def recipient_style(self) -> str:
        return get_style_for_name((self.recipients or [self.author])[0])

    @property
    def timestamp_without_seconds(self) -> str:
        return timestamp_without_seconds(self.timestamp)

    @property
    def _summary(self) -> Text:
        """One line summary mostly for logging."""
        return self._summary_with_author.append(CLOSE_PROPERTIES_CHAR)

    @property
    def _summary_with_author(self) -> Text:
        """Append author information to `super().summary`, bracket is left open."""
        author_str = styled_key_value('author', Text(f"'{self.author_str}'", style=self.author_style))
        return super()._summary.append(', ').append(author_str)

    def entity_scan(self, exclude: EntityScanArg = None, include: EntityScanArg = None) -> list[Entity]:
        """Overrides superclass to append `self.recipients`."""
        return super().entity_scan(exclude, self.participant_names + coerce_entity_names(include))

    def extract_recipients(self) -> list[Name]:
        """Overload in subclasses"""
        return []

    @classmethod
    def default_category(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def dummy_cfg(cls) -> CommunicationCfg:
        return CommunicationCfg(id='DUMMY')
