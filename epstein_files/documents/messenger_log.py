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
MSG_DATE_FORMAT = "%m/%d/%y %I:%M:%S %p"

UNKNOWN_TEXTERS = [
    '+16463880059',
    '+13108737937',
    '+13108802851',
    'e:',
    '+',
    None,
]

TEXTER_MAPPING = {
    'e:jeeitunes@gmail.com': JEFFREY_EPSTEIN,
    '+19174393646': SCARAMUCCI,
    '+13109906526': STEVE_BANNON,
}


@dataclass
class TextMessage:
    timestamp: datetime
    author: str
    author_txt: Text
    text: Text

    def __rich__(self) -> Text:
        return Text('').append(self.timestamp).append(self.author_txt).append(': ', style='dim').append(self.text)


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
        if len(self._messages) > 0:
            return self._messages

        for match in MSG_REGEX.finditer(self.text):
            sender = sender_str = match.group(1).strip()
            timestamp = Text(f"[{match.group(2).strip()}] ", style='gray30')
            msg = match.group(4).strip()
            msg_lines = msg.split('\n')
            sender_style = None
            sender_txt = None

            # If the Sender: is redacted we need to fill it in from our configuration
            if len(sender) == 0:
                sender = self.author
                sender_str = self.author_str
                sender_txt = self.author_txt
            else:
                if sender in TEXTER_MAPPING:
                    sender = sender_str = TEXTER_MAPPING[sender]
                    sender_str = JEFFREY_EPSTEIN.split(' ')[-1] if sender_str == JEFFREY_EPSTEIN else sender_str
                elif PHONE_NUMBER_REGEX.match(sender):
                    sender_style = PHONE_NUMBER_STYLE
                elif re.match('[ME]+', sender):
                    sender = MELANIE_WALKER

                author_style = f"{get_style_for_name(sender)} bold"
                sender_txt = Text(sender_str, style=sender_style or author_style)

            # Fix multiline links
            if msg.startswith('http'):
                if len(msg_lines) > 1 and not msg_lines[0].endswith('html'):
                    if len(msg_lines) > 2 and msg_lines[1].endswith('-'):
                        msg = msg.replace('\n', '', 2)
                    else:
                        msg = msg.replace('\n', '', 1)

                msg_lines = msg.split('\n')
                link_text = msg_lines.pop()
                msg = Text('').append(Text.from_markup(f"[link={link_text}]{link_text}[/link]", style=TEXT_LINK))

                if len(msg_lines) > 0:
                    msg = msg.append('\n' + ' '.join(msg_lines))
            else:
                msg = highlighter(msg.replace('\n', ' '))  # remove newlines

            text_message = TextMessage(
                timestamp=timestamp,
                author=UNKNOWN if (sender in UNKNOWN_TEXTERS or BAD_TEXTER_REGEX.match(sender)) else sender,
                author_txt=sender_txt,
                text=msg
            )

            self._messages.append(text_message)

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
