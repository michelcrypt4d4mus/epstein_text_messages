import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import cast

from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, Document
from epstein_files.documents.config.communication_cfg import CommunicationCfg
from epstein_files.output.highlight_config import get_style_for_name, styled_name
from epstein_files.output.rich import styled_key_value
from epstein_files.people.entity import Entity, EntityScanArg
from epstein_files.people.names import UNKNOWN, Name, extract_last_name
from epstein_files.util.constant.strings import QUESTION_MARKS
from epstein_files.util.helpers.data_helpers import uniq_sorted
from epstein_files.util.helpers.rich_helpers import no_bold, join_texts
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
        txt = super()._summary
        txt = txt[0:len(txt) - 1]

        if self.recipients:
            txt.append(', ').append(styled_key_value('recipients', self.recipients_txt()))

        return txt.append(CLOSE_PROPERTIES_CHAR)

    def entity_scan(self, exclude: EntityScanArg = None, include: EntityScanArg = None) -> list[Entity]:
        """Overrides superclass to append `self.recipients`."""
        include = self.participant_names + Entity.coerce_entity_names(include)
        return super().entity_scan(exclude, include)

    def extract_recipients(self) -> list[Name]:
        """Overload in subclasses"""

        return []
    def recipients_txt(self, max_full_names: int = 2) -> Text:
        """Comma separated colored names (last name only if more than `max_full_names` recipients)."""
        recipients = [r or UNKNOWN for r in self.recipients] if len(self.recipients) > 0 else [UNKNOWN]

        names = [
            Text(r if len(recipients) <= max_full_names else extract_last_name(r), get_style_for_name(r)) + \
                (Text(f" {QUESTION_MARKS}", get_style_for_name(r)) if self._config.recipient_uncertain else Text(''))
            for r in recipients
        ]

        return join_texts(names, join=', ')

    @classmethod
    def default_category(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def dummy_cfg(cls) -> CommunicationCfg:
        return CommunicationCfg(id='DUMMY')
