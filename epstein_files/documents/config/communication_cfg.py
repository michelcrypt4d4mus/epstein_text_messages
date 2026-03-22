from dataclasses import dataclass, field
from enum import StrEnum, auto

from rich.text import Text

from epstein_files.documents.documents.categories import Interesting, Neutral, Uninteresting
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.data_helpers import without_falsey
from epstein_files.util.helpers.string_helper import join_truthy

class Platform(StrEnum):
    EMAIL = auto()
    IMESSAGE = 'iMessage'
    LETTER = auto()
    SKYPE = 'Skype'
    TEXT_MSG = 'text message'
    WHATSAPP = 'WhatsApp'

PLATFORM_STYLES = {
    Platform.LETTER: 'plum4',
    Platform.SKYPE: 'bright_cyan',
    Platform.WHATSAPP: 'cyan',
}


@dataclass(kw_only=True)
class CommunicationCfg(DocCfg):
    """
    Manual config is always required for MessengerLog author attribution. It's also often needed for Email
    files to handle the terrible OCR text that Congress provided which messes up a lot of the email headers.

    Attributes:
        is_fwded_article (bool, optional): `True` if this is a newspaper article someone fwded. Used to exclude articles from word counting.
        platform (Platform, optional): platform this happened on (e.g. Skype, WhatsApp, etc.)
        recipients (list[Name]): Who received the communication
        recipient_uncertain (bool | str, optional): Optional explanation of why this recipient was attributed, but uncertainly
    """
    is_fwded_article: bool | None = None
    platform: Platform | Literal[''] = ''
    recipients: list[Name] = field(default_factory=list)
    recipient_uncertain: bool | str = ''

    def __post_init__(self):
        # TODO: sucks, Sets show_full_panel to false temporarily to avoid is_interesting=10 logic
        show_full_panel = self.show_full_panel
        self.show_full_panel = False
        super().__post_init__()
        self.show_full_panel = show_full_panel

        if not isinstance(self.recipients, list):
            raise ValueError(f"{self.id} recipients is not a list: {self.recipients}")

        if self.is_fwded_article:
            self.is_valid_for_name_scan = False

        self.recipients = sort_names(self.recipients)

    @property
    def category_txt(self) -> Text:
        """Overloads superclass to return `self.platform`."""
        if self.category:
            return super().category_txt
        elif self.platform and self.platform in PLATFORM_STYLES:
            return Text(self.platform.lower(), PLATFORM_STYLES[self.platform])
        else:
            return super().category_txt

    @property
    def complete_description(self) -> str:
        """Add platform to superclass return value."""
        if self.platform == Platform.EMAIL:
            return self.note
        elif self.platform:
            author = f"{self.author} {QUESTION_MARKS}" if self.author and self.author_uncertain else self.author
            recipients = self.recipients_str

            if self.platform in [Platform.SKYPE, Platform.WHATSAPP]:
                description = f"{self.platform} log"
                recipients = join_truthy(author, recipients, ', ')
                recipients_sep = ' of conversation with '
            else:
                description = join_truthy(self.platform, author, ' from ')
                recipients_sep = ' to '

            description = join_truthy(description, recipients, recipients_sep)
            return join_truthy(description, self.note)
        else:
            return super().complete_description

    @property
    def is_of_interest(self) -> bool | None:
        """Fwded articles are not interesting."""
        if self.is_fwded_article and not self.is_interesting:
            return False
        else:
            return super().is_of_interest

    @property
    def names(self) -> list[str]:
        """Names configured for this document. Overloaded in subclass to add recipients."""
        return super().names + without_falsey(self.recipients)

    @property
    def recipients_str(self) -> str:
        return ', '.join([r or UNKNOWN for r in self.recipients])

    def __repr__(self) -> str:
        return super().__repr__()


# TODO: rename MessengerLogCfg
@dataclass(kw_only=True)
class TextCfg(CommunicationCfg):
    """Config for the `MessengerLog` class."""
    platform: Platform = Platform.IMESSAGE

    @property
    def complete_description(self) -> str:
        """Just return the `note` field for iMessage log files."""
        return self.note

    # This is necessary because for some dumb reason @dataclass(repr=False) doesn't cut it
    def __repr__(self) -> str:
        return super().__repr__()


def imessage_log(id: str, **kwargs) -> CommunicationCfg:
    return CommunicationCfg(id=id, platform=Platform.IMESSAGE, **kwargs)


def imessage_screenshot(id: str, **kwargs) -> CommunicationCfg:
    return imessage_log(id=id, note='screenshot(s)', **kwargs)


def skype_log(id: str, **kwargs) -> CommunicationCfg:
    return _communication_app_log(id, Platform.SKYPE, **kwargs)


def whatsapp_log(id: str, **kwargs) -> CommunicationCfg:
    return _communication_app_log(id, Platform.WHATSAPP, **kwargs)


def _communication_app_log(id: str, platform: Platform, **kwargs) -> CommunicationCfg:
    return CommunicationCfg(id=id, platform=platform, show_full_panel=True, **kwargs)
