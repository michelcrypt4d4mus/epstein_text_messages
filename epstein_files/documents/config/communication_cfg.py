from dataclasses import dataclass, field

from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


@dataclass(kw_only=True)
class CommunicationCfg(DocCfg):
    """
    Manual config is always required for MessengerLog author attribution. It's also often needed for Email
    files to handle the terrible OCR text that Congress provided which messes up a lot of the email headers.

    Attributes:
        is_fwded_article (bool, optional): `True` if this is a newspaper article someone fwded. Used to exclude articles from word counting.
        recipients (list[Name]): Who received the communication
        recipient_uncertain (bool | str, optional): Optional explanation of why this recipient was attributed, but uncertainly
    """
    is_fwded_article: bool | None = None
    recipients: list[Name] = field(default_factory=list)
    recipient_uncertain: bool | str = ''

    def __post_init__(self):
        super().__post_init__()

        if not isinstance(self.recipients, list):
            raise ValueError(f"{self.id} recipients is not a list: {self.recipients}")

        if self.is_fwded_article:
            self.is_valid_for_name_scan = False

        self.recipients = sort_names(self.recipients)

    @property
    def is_of_interest(self) -> bool | None:
        """Fwded articles are not interesting."""
        if self.is_fwded_article and not self.is_interesting:
            return False
        else:
            return super().is_of_interest

    @property
    def recipients_str(self) -> str:
        return ', '.join([r or UNKNOWN for r in self.recipients])

    def __repr__(self) -> str:
        return super().__repr__()


@dataclass(kw_only=True)
class TextCfg(CommunicationCfg):
    # This is necessary because for some dumb reason @dataclass(repr=False) doesn't cut it
    def __repr__(self) -> str:
        return super().__repr__()
