import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import CommunicationDocument
from epstein_files.util.constant.strings import PHONE_NUMBER_STYLE
from epstein_files.util.constants import *
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.rich import TEXT_LINK, highlighter, logger

BAD_TEXTER_REGEX = re.compile(r'^([-+_1•F]+|[4Ide])$')
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
MSG_DATE_FORMAT = r"%m/%d/%y %I:%M:%S %p"

UNKNOWN_TEXTERS = [
    '+16463880059',
    '+13108737937',
    '+13108802851',
    'e:',
    '+',
]

TEXTER_MAPPING = {
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
        elif self.author in UNKNOWN_TEXTERS or BAD_TEXTER_REGEX.match(self.author):
            self.author_str = self.author
            self.author = None
        elif self.author in LAST_NAMES_ONLY:
            self.author_str = self.author.split()[-1]
        elif not self.id_confirmed:
            self.author_str = self.author + ' (?)'
        else:
            self.author_str = self.author

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
        timestamp_txt = Text(f"[{self.timestamp_str}] ", style='gray30')
        return Text('').append(timestamp_txt).append(author_txt).append(': ', style='dim').append(self._message())


@dataclass
class MessengerLog(CommunicationDocument):
    hint_txt: Text | None = field(init=False)
    _messages: list[TextMessage] = field(default_factory=list)
    _author_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))

    def __post_init__(self):
        super().__post_init__()

        if self.file_id in KNOWN_IMESSAGE_FILE_IDS:
            self.hint_txt = Text(f" Found confirmed counterparty ", style='dim').append(self.author_txt)
            self.hint_txt.append(f" for file ID {self.file_id}.")
        elif self.file_id in GUESSED_IMESSAGE_FILE_IDS:
            self.hint_txt = Text(" (This is probably a conversation with ", style='dim').append(self.author_txt).append(')')
        else:
            self.hint_txt = None

    def messages(self) -> list[TextMessage]:
        if len(self._messages) == 0:
            self._messages = [
                TextMessage(
                    author=match.group(1).strip() or self.author,  # If the Sender: is redacted that means it's from self.author
                    id_confirmed=self.file_id in KNOWN_IMESSAGE_FILE_IDS,
                    text=match.group(4).strip(),
                    timestamp_str=match.group(2).strip(),
                )
                for match in MSG_REGEX.finditer(self.text)
            ]

        return self._messages

    def _extract_author(self) -> None:
        self.author = KNOWN_IMESSAGE_FILE_IDS.get(self.file_id, GUESSED_IMESSAGE_FILE_IDS.get(self.file_id))
        author_str = self.author or UNKNOWN
        self.author_str = author_str.split(' ')[-1] if author_str in [STEVE_BANNON] else author_str
        self.author_style = get_style_for_name(self.author_or_unknown()) + ' bold'

        if self.file_id in GUESSED_IMESSAGE_FILE_IDS:
            self.author_str += ' (?)'

        self.author_txt = Text(self.author_str, style=self.author_style)

    def _extract_timestamp(self) -> datetime:
        for match in MSG_REGEX.finditer(self.text):
            timestamp_str = match.group(2).strip()

            try:
                return datetime.strptime(timestamp_str, MSG_DATE_FORMAT)
            except ValueError as e:
                logger.info(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")

        raise RuntimeError(f"{self}: No timestamp found!")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Panel(self.raw_document_link_txt(), border_style=self.author_style.removesuffix(' bold'), expand=False)

        if self.hint_txt:
            yield self.hint_txt
            yield Text('')

        for message in self.messages():
            yield message
