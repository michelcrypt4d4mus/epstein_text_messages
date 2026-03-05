import re
from dateutil.parser import parse
from dataclasses import dataclass, field
from datetime import datetime

from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.imessage.text_message import TextMessage
from epstein_files.output.rich import console
from epstein_files.people.names import JEFFREY_EPSTEIN, LAWRENCE_KRAUSS, STEVE_BANNON
from epstein_files.util.env import args
from epstein_files.util.logging import logger

BRACKET_NUM_PATTERN = r"\s*\[?\d\]?\s*"
DATE_PATTERN = r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\(?UTC\)?" + fr"(?:{BRACKET_NUM_PATTERN})?"
SENDER_PATTERN = r"\s*Sender:(?P<sender>.*?)Participants:?(?P<participants>.*?\)$)"
MSG_REGEX = re.compile(fr'iMessage\s+(?:{BRACKET_NUM_PATTERN})?{DATE_PATTERN}{SENDER_PATTERN}(?P<msg>.*?)(?=iMessage|NYCO24362|SMS)', re.DOTALL | re.M)
REDACTED_AUTHOR_REGEX = re.compile(r"^([-+•_1MENO.=F]+|[4Ide])$")
# print(MSG_REGEX.pattern)

MATCH_GROUPS = [
    'sender',
    'participants',
    'timestamp',
    'msg',
]

IMESSAGE_PDF_IDS = [
    'EFTA00781689',
    'EFTA00508054',  # TODO: needs review, might be missing messages
]


@dataclass
class MessengerLogPdf(MessengerLog):
    """Class for unstructured iMessage logs in some PDFs."""

    def _extract_messages(self) -> list[TextMessage]:
        msgs: list[TextMessagePdf] = []

        if args.raw:
            print(f"\n\n------ REPAIRED TEXT -----\n{self.text}\n------ END TEXT -----\n\n")

        for match in MSG_REGEX.finditer(self.text):
            msg = match.group('msg').strip()
            timestamp_str = match.group('timestamp').strip()
            sender = match.group('sender').replace('(', '').replace(')', '').strip()

            if sender.startswith('Self'):
                sender = JEFFREY_EPSTEIN
            elif self.file_id == 'EFTA00781689' and timestamp_str.startswith('2018-10-0') and sender in ['', 't']:
                sender = STEVE_BANNON
            elif self.file_id == 'EFTA00508054' and sender == 'Lawrence':
                sender = LAWRENCE_KRAUSS
            elif not sender:
                sender = None

            text_message = TextMessagePdf(
                author=sender,
                is_id_confirmed=len(sender or '') > 0 and sender != STEVE_BANNON,
                text=msg,
                timestamp_str=match.group('timestamp').strip(),
            )

            if msgs and text_message == msgs[-1]:
                self.log(f"Parsed TextMessage is the same as the last one, skipping...\n")
                continue

            for g in MATCH_GROUPS:
                self.log(f"  match [{g}] '{match.group(g).strip()}'")

            self.log(f'\nmessage: {text_message.__rich__().plain}\n')
            msgs.append(text_message)

        return msgs

    def _extract_timestamp(self) -> datetime:
        return self._extract_messages()[0].parse_timestamp()



@dataclass(kw_only=True)
class TextMessagePdf(TextMessage):
    def parse_timestamp(self) -> datetime:
        return parse(self.timestamp_str)
