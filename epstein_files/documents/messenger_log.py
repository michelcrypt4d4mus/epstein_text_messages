import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import CommunicationDocument
from epstein_files.util.constant.strings import PHONE_NUMBER_STYLE, TIMESTAMP_DIM
from epstein_files.util.constants import *
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.rich import SYMBOL_STYLE, TEXT_LINK, highlighter, logger

KNOWN_IDS = [id for id in KNOWN_IMESSAGE_FILE_IDS.keys()] + [id for id in GUESSED_IMESSAGE_FILE_IDS.keys()]
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
REDACTED_AUTHOR_REGEX = re.compile(r"^([-+•_1MENO.=F]+|[4Ide])$")
MSG_DATE_FORMAT = r"%m/%d/%y %I:%M:%S %p"

UNKNOWN_TEXTERS = [
    '+16463880059',
    '+13108737937',
    '+13108802851',
]

TEXTER_MAPPING = {
    'e:': JEFFREY_EPSTEIN,
    'e:jeeitunes@gmail.com': JEFFREY_EPSTEIN,
    '+19174393646': SCARAMUCCI,
    '+13109906526': STEVE_BANNON,
}

LAST_NAMES_ONLY = [
    JEFFREY_EPSTEIN,
    STEVE_BANNON,
]


@dataclass(kw_only=True)
class TextMessage:
    author: str | None
    author_str: str = field(init=False)
    id_confirmed: bool = False
    text: str
    timestamp_str: str

    def __post_init__(self):
        self.author = TEXTER_MAPPING.get(self.author or UNKNOWN, self.author)

        if self.author is None:
            self.author_str = UNKNOWN
        elif self.author in UNKNOWN_TEXTERS:
            logger.warning(f"Bad text from '{self.author}': \"{self.text}\"")
            self.author_str = self.author
            self.author = None
        elif self.author in LAST_NAMES_ONLY:
            self.author_str = self.author.split()[-1]
        elif not self.id_confirmed:
            self.author_str = self.author + ' (?)'
        else:
            self.author_str = self.author

    def timestamp(self) -> datetime:
        return datetime.strptime(self.timestamp_str, MSG_DATE_FORMAT)

    def _message(self) -> Text:
        msg = self.text
        lines = self.text.split('\n')

        # Fix multiline links
        if self.text.startswith('http'):
            if len(lines) > 1 and not lines[0].endswith('html'):
                if len(lines) > 2 and lines[1].endswith('-'):
                    msg = msg.replace('\n', '', 2)
                else:
                    msg = msg.replace('\n', '', 1)

            lines = msg.split('\n')
            link_text = lines.pop()
            msg_txt = Text('').append(Text.from_markup(f"[link={link_text}]{link_text}[/link]", style=TEXT_LINK))

            if len(lines) > 0:
                msg_txt.append('\n' + ' '.join(lines))
        else:
            msg_txt = highlighter(' '.join(lines))  # remove newlines

        return msg_txt

    def __rich__(self) -> Text:
        if PHONE_NUMBER_REGEX.match(self.author_str):
            author_style = PHONE_NUMBER_STYLE
        else:
            author_style = get_style_for_name(self.author)

        author_txt = Text(self.author_str, style=author_style)
        timestamp_txt = Text(f"[{self.timestamp_str}]", style='turquoise4 dim').append(' ')
        return Text('').append(timestamp_txt).append(author_txt).append(': ', style='dim').append(self._message())


@dataclass
class MessengerLog(CommunicationDocument):
    _messages: list[TextMessage] = field(default_factory=list)
    _author_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))

    def description_panel(self) -> Panel:
        """Panelized description() with info_txt(), used in search results."""
        return super().description_panel(include_hints=False)

    def first_message_at(self, name: str | None) -> datetime:
        return self.messages_by(name)[0].timestamp()

    def info_txt(self) -> Text | None:
        if self.file_id not in KNOWN_IDS:
            return None

        if self.file_id in KNOWN_IMESSAGE_FILE_IDS:
            hint_msg = 'Found confirmed counterparty'
        else:
            hint_msg = 'This is probably a conversation with'

        return Text(f"({hint_msg} ", style='dim').append(self.author_txt).append(')')

    def last_message_at(self, name: str | None) -> datetime:
        return self.messages_by(name)[-1].timestamp()

    def messages_by(self, name: str | None) -> list[TextMessage]:
        return [m for m in self.messages() if m.author == name]

    def messages(self) -> list[TextMessage]:
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

    def _extract_author(self) -> None:
        self.author = KNOWN_IMESSAGE_FILE_IDS.get(self.file_id, GUESSED_IMESSAGE_FILE_IDS.get(self.file_id))
        self.author_str = self.author or UNKNOWN
        self.author_style = get_style_for_name(self.author) + ' bold'

        if self.file_id in GUESSED_IMESSAGE_FILE_IDS:
            self.author_str += ' (?)'

    def _extract_timestamp(self) -> datetime:
        for match in MSG_REGEX.finditer(self.text):
            timestamp_str = match.group(2).strip()

            try:
                return datetime.strptime(timestamp_str, MSG_DATE_FORMAT)
            except ValueError as e:
                logger.info(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")

        raise RuntimeError(f"{self}: No timestamp found!")

    def _border_style(self) -> str:
        return self.author_style.removesuffix(' bold')

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield self.file_info_panel()
        yield(Text(''))

        for message in self.messages():
            yield message
