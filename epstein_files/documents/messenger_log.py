import re
from dataclasses import dataclass, field
from datetime import datetime

from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.communication_document import CommunicationDocument
from epstein_files.documents.imessage.text_message import MSG_DATE_FORMAT, TextMessage
from epstein_files.util.constants import GUESSED_IMESSAGE_FILE_IDS, KNOWN_IMESSAGE_FILE_IDS
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.rich import logger

CONFIRMED_MSG = 'Found confirmed counterparty'
GUESSED_MSG = 'This is probably a conversation with'
KNOWN_IDS = [id for id in KNOWN_IMESSAGE_FILE_IDS.keys()] + [id for id in GUESSED_IMESSAGE_FILE_IDS.keys()]
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
REDACTED_AUTHOR_REGEX = re.compile(r"^([-+•_1MENO.=F]+|[4Ide])$")


@dataclass
class MessengerLog(CommunicationDocument):
    """Class representing one iMessage log file (one conversation between Epstein and some counterparty)."""
    _messages: list[TextMessage] = field(default_factory=list)

    def description_panel(self) -> Panel:
        """Panelized description() with info_txt(), used in search results."""
        return super().description_panel(include_hints=False)

    def first_message_at(self, name: str | None) -> datetime:
        return self.messages_by(name)[0].timestamp()

    def info_txt(self) -> Text | None:
        if self.file_id not in KNOWN_IDS:
            return None

        hint_msg = CONFIRMED_MSG if self.file_id in KNOWN_IMESSAGE_FILE_IDS else GUESSED_MSG
        return Text(f"({hint_msg} ", style='dim').append(self.author_txt).append(')')

    def last_message_at(self, name: str | None) -> datetime:
        return self.messages_by(name)[-1].timestamp()

    def messages_by(self, name: str | None) -> list[TextMessage]:
        """Return all messages by 'name'."""
        return [m for m in self.messages() if m.author == name]

    def messages(self) -> list[TextMessage]:
        """Lazily evaluated accessor for self._messages."""
        if len(self._messages) == 0:
            self._messages = [
                TextMessage(
                    # If the Sender: is redacted that means it's from self.author
                    author=REDACTED_AUTHOR_REGEX.sub('', match.group(1).strip()) or self.author,
                    id_confirmed=self.file_id in KNOWN_IMESSAGE_FILE_IDS,
                    text=match.group(4).strip(),
                    timestamp_str=match.group(2).strip(),
                )
                for match in MSG_REGEX.finditer(self.text)
            ]

        return self._messages

    def _border_style(self) -> str:
        return self.author_style.removesuffix(' bold')

    def _extract_author(self) -> None:
        self.author = KNOWN_IMESSAGE_FILE_IDS.get(self.file_id, GUESSED_IMESSAGE_FILE_IDS.get(self.file_id))
        self.author_style = get_style_for_name(self.author) + ' bold'

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
        yield(Text(''))

        for message in self.messages():
            yield message
