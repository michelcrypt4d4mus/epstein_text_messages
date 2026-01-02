import re
from dataclasses import dataclass, field
from datetime import datetime

from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.imessage.text_message import MSG_DATE_FORMAT, TextMessage
from epstein_files.util.file_cfg import MessageCfg
from epstein_files.util.rich import logger

CONFIRMED_MSG = 'Found confirmed counterparty'
GUESSED_MSG = 'This is probably a conversation with'
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
REDACTED_AUTHOR_REGEX = re.compile(r"^([-+•_1MENO.=F]+|[4Ide])$")


@dataclass
class MessengerLog(Communication):
    """Class representing one iMessage log file (one conversation between Epstein and some counterparty)."""
    config: MessageCfg | None = None
    _messages: list[TextMessage] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()

    def first_message_at(self, name: str | None) -> datetime:
        return self.messages_by(name)[0].timestamp()

    def info_txt(self) -> Text | None:
        hint_msg = GUESSED_MSG if self.is_author_uncertain() else CONFIRMED_MSG
        author_txt = Text(self.author_or_unknown(), style=self.author_style + ' bold')
        return Text(f"({hint_msg} ", style='dim').append(author_txt).append(')')

    def is_author_uncertain(self) -> bool | None:
        if self.config:
            return self.config.is_author_uncertain

    def last_message_at(self, name: str | None) -> datetime:
        return self.messages_by(name)[-1].timestamp()

    def messages(self) -> list[TextMessage]:
        """Lazily evaluated accessor for self._messages."""
        if len(self._messages) == 0:
            self._messages = [
                TextMessage(
                    # If the Sender: is redacted that means it's from self.author
                    author=REDACTED_AUTHOR_REGEX.sub('', match.group(1).strip()) or self.author,
                    id_confirmed=not self.is_author_uncertain(),
                    text=match.group(4).strip(),
                    timestamp_str=match.group(2).strip(),
                )
                for match in MSG_REGEX.finditer(self.text)
            ]

        return self._messages

    def messages_by(self, name: str | None) -> list[TextMessage]:
        """Return all messages by 'name'."""
        return [m for m in self.messages() if m.author == name]

    def _border_style(self) -> str:
        return self.author_style

    def _extract_timestamp(self) -> datetime:
        for match in MSG_REGEX.finditer(self.text):
            timestamp_str = match.group(2).strip()

            try:
                return datetime.strptime(timestamp_str, MSG_DATE_FORMAT)
            except ValueError as e:
                logger.info(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")

        raise RuntimeError(f"{self}: No timestamp found!")

    def __rich_console__(self, _console: Console, _options: ConsoleOptions) -> RenderResult:
        yield self.file_info_panel()
        yield Text('')

        for message in self.messages():
            yield message
