import re
from collections import defaultdict

from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.text import Text

from util.constants import *
from util.rich import PHONE_NUMBER, TEXT_LINK, TIMESTAMP, get_style_for_name, highlight_interesting_text
from documents.document import *

MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
BAD_TEXTER_REGEX = re.compile(r'^([-+_1•F]+|[4Ide])$')
MSG_DATE_FORMAT = "%m/%d/%y %I:%M:%S %p"
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')

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

sender_counts = defaultdict(int)


@dataclass
class MessengerLog(CommunicationDocument):
    author_str: str = field(init=False)
    hint_txt: Text | None = field(init=False)
    msg_count: int = 0

    def __post_init__(self):
        super().__post_init__()
        self.author = KNOWN_IMESSAGE_FILE_IDS.get(self.file_id, GUESSED_IMESSAGE_FILE_IDS.get(self.file_id))
        author_str = self.author or UNKNOWN
        self.author_str = author_str.split(' ')[-1] if author_str in [STEVE_BANNON] else author_str
        self.author_style = get_style_for_name(author_str) + ' bold'
        self.author_txt = Text(self.author_str, style=self.author_style)
        self.archive_link = self.epsteinify_link(self.author_style)

        if self.file_id in KNOWN_IMESSAGE_FILE_IDS:
            self.hint_txt = Text(f" Found confirmed counterparty ", style='dim').append(self.author_txt)
            self.hint_txt.append(f" for file ID {self.file_id}.")
        elif self.file_id in GUESSED_IMESSAGE_FILE_IDS:
            self.author_str += ' (?)'
            self.author_txt = Text(self.author_str, style=self.author_style)
            self.hint_txt = Text(" (This is probably a conversation with ", style='dim').append(self.author_txt).append(')')
        else:
            self.hint_txt = None

        # Get timestamp
        for match in MSG_REGEX.finditer(self.text):
            timestamp_str = match.group(2).strip()

            try:
                self.timestamp = datetime.strptime(timestamp_str, MSG_DATE_FORMAT)
                break
            except ValueError as e:
                logger.info(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Panel(self.archive_link, border_style=self.author_style.removesuffix(' bold'), expand=False)

        if self.hint_txt:
            yield self.hint_txt
            yield Text('')

        for match in MSG_REGEX.finditer(self.text):
            sender = sender_str = match.group(1).strip()
            timestamp = Text(f"[{match.group(2).strip()}] ", style=TIMESTAMP)
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
                    sender_style = PHONE_NUMBER
                elif re.match('[ME]+', sender):
                    sender = MELANIE_WALKER

                sender_txt = Text(sender_str, style=sender_style or f"{get_style_for_name(sender)} bold")

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
                msg = Text.from_markup(highlight_interesting_text(msg.replace('\n', ' ')))  # remove newlines

            sender_counts[UNKNOWN if (sender in UNKNOWN_TEXTERS or BAD_TEXTER_REGEX.match(sender)) else sender] += 1
            yield Text('').append(timestamp).append(sender_txt).append(': ', style='dim').append(msg)
            self.msg_count += 1
