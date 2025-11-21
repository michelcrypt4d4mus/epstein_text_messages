import re

from util.constants import DEFAULT, GUESSED_IMESSAGE_FILE_IDS, KNOWN_IMESSAGE_FILE_IDS, UNKNOWN
from util.rich import COUNTERPARTY_COLORS
from documents.document import *

MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
MSG_DATE_FORMAT = "%m/%d/%y %I:%M:%S %p"


@dataclass
class MessengerLog(CommunicationDocument):
    author_str: str = field(init=False)
    hint_txt: Text | None = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.author = KNOWN_IMESSAGE_FILE_IDS.get(self.file_id, GUESSED_IMESSAGE_FILE_IDS.get(self.file_id))
        self.author_str = self.author or UNKNOWN
        self.author_style = COUNTERPARTY_COLORS.get(self.author_str, DEFAULT)
        self.author_txt = Text(self.author_str, style=self.author_style)

        if self.file_id in KNOWN_IMESSAGE_FILE_IDS:
            self.hint_txt = Text(f" Found confirmed counterparty ", style='grey').append(self.author_txt).append(f" for file ID {self.file_id}.")
        elif self.file_id in GUESSED_IMESSAGE_FILE_IDS:
            self.author_str += ' (?)'
            self.author_txt = Text(self.author_str, style=self.author_style)
            self.hint_txt = Text(" (This is probably a conversation with ", style='grey').append(self.author_txt).append(')')
        else:
            self.hint_txt = None

        # Get timestamp
        for match in MSG_REGEX.finditer(self.text):
            timestamp_str = match.group(2).strip()

            try:
                self.timestamp = datetime.strptime(timestamp_str, MSG_DATE_FORMAT)
                break
            except ValueError as e:
                logger.debug(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")
