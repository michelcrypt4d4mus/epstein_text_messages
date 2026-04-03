import re
from dateutil.parser import parse
from dataclasses import dataclass, field
from datetime import datetime

from epstein_files.documents.emails.emailers import extract_emailer_names
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.imessage.text_message import TextMessage
from epstein_files.people.names import *
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import coerce_utc
from epstein_files.util.logging import logger
from epstein_files.util.helpers.string_helper import collapse_whitespace, indented, quote

MSG_START_PATTERN = '(iMessage|Skype)'
BRACKET_NUM_PATTERN = r"\s*\[?[\dIl]*\]?\s*"
DATE_PATTERN = r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\(?UTC\)?" + fr"(?:{BRACKET_NUM_PATTERN})?"
SENDER_PATTERN = r"\s*Sender:(?P<sender>.*?)Participants:?(?P<participants>(\s*?|.*?\))$)"
MSG_REGEX = re.compile(fr'{MSG_START_PATTERN}\s+(?:{BRACKET_NUM_PATTERN})?{DATE_PATTERN}{SENDER_PATTERN}(?P<msg>.*?)(?={MSG_START_PATTERN}|Notes|NYCO24362|SMS)', re.DOTALL | re.M)
REDACTED_AUTHOR_REGEX = re.compile(r"^([-+•_1MENO.=F]+|[4Ide])$")

# Sometimes participants field ends up in the message
INVALID_SENDER_REGEX = re.compile(r'^(M[EI]|M[an] .*|\d)')
JUNK_PREFIX_REGEX = re.compile(r"Sender: Self .{1,3}eeitunes.{,10}Participants: ? \(?")
JUNK_SUFFIX_REGEX = re.compile(r"\)?,? ?(Sender:\s)?Self \( ?(e:?)?jeeitunes[®@]gmail.com ?\)|Participants: Lawrence Krauss(\s*\()?")
VALID_SENDER_REGEX = re.compile(r"\w{4,}")
# print(MSG_REGEX.pattern)

MATCH_GROUPS = [
    'timestamp',
    'sender',
    'participants',
    'msg',
]

IMESSAGE_PDF_IDS = [
    'EFTA00781689',
    'EFTA00508054',  # TODO: needs review, might be missing messages
    'EFTA01218267',
    'EFTA00509258',
    'EFTA00507900',    # TODO: verify
    'EFTA01209003',    # TODO: verify
    'EFTA00508702',    # TODO: verify
    'EFTA00786793',    # TODO: verify
    'EFTA00508996',    # TODO: verify
    'EFTA00785279',    # TODO: verify
    'EFTA00784260',    # TODO: verify
    'EFTA00786091',    # TODO: verify
    'EFTA00508003',    # TODO: verify
    'EFTA00783435',    # TODO: verify
    'EFTA00781780',    # TODO: verify
    'EFTA00508858',    # TODO: verify
    'EFTA00508962',    # TODO: verify
    # 'EFTA01618718',    # TODO: verify
    'EFTA00785782',    # TODO: verify
    'EFTA01212310',    # TODO: verify
    'EFTA00784321',    # TODO: verify
    'EFTA00786073',    # TODO: verify
    'EFTA00507505',    # TODO: verify
    'EFTA00786405',    # TODO: verify
    'EFTA01214317',    # TODO: verify, also includes Skype logs
    'EFTA01209254',    # TODO: verify, also includes Skype logs
    'EFTA01212440',    # TODO: verify, also includes Skype logs
    'EFTA01209934',    # TODO: verify, also includes Skype logs
    # 'EFTA01616222',  # TODO: Doesn't parse well
    # 'EFTA01613143',  # TODO: Doesn't parse well
]


@dataclass
class MessengerLogPdf(MessengerLog):
    """Class for unstructured iMessage logs in some PDFs."""

    def extract_messages(self) -> list[TextMessage]:
        msgs: list[TextMessagePdf] = []

        if args.raw:
            print(f"\n\n------ REPAIRED TEXT -----\n{self.text}\n------ END TEXT -----\n\n")

        for match in MSG_REGEX.finditer(self.text):
            msg = match.group('msg').strip()
            timestamp_str = match.group('timestamp').strip()
            sender = collapse_whitespace(match.group('sender').replace('(', '').replace(')', ''))

            if sender.startswith('Self'):
                sender = JEFFREY_EPSTEIN
            elif self.file_id == 'EFTA00781689' and timestamp_str.startswith('2018-10-0') and sender in ['', 't']:
                sender = STEVE_BANNON
            elif self.file_id == 'EFTA00785782' and sender.startswith('Martin'):
                sender = MARTIN_NOWAK
            elif self.file_id == 'EFTA00508054' and sender == 'Lawrence':
                sender = LAWRENCE_KRAUSS
            elif sender in ['Terje', 'Tetje']:
                sender = TERJE_ROD_LARSEN
            elif sender.startswith('Eva'):
                sender = EVA_DUBIN
            elif sender == 'Eduardo':
                sender = EDUARDO_TEODORANI
            elif sender.startswith('ME') or sender.startswith('MI') or sender == 'Ma m':
                sender = None
            elif (extracted_names := extract_emailer_names(sender)):
                if len(extracted_names) > 1:
                    self._error(f"Found multiple names, using first only! {extracted_names}")

                sender = extracted_names[0]
            elif re.compile(r"^[\d.+MEM]+$").match(sender):
                self._warn(f"no emailer from string '{sender}'")
                sender = None
            elif not VALID_SENDER_REGEX.search(sender):
                self._log(f"text message sender '{sender}' is not a valid name")
                sender = None

            if JUNK_SUFFIX_REGEX.search(msg):
                self._debug_log(f"Found junk suffixes in message, removing. msg:\n-----\n{msg}\n-----")
                msg = JUNK_SUFFIX_REGEX.sub('', msg).strip()

                if msg:
                    self._debug_log(f"Text message stripped of junk suffixes:\n-----\n{msg}\n-----\n")
                else:
                    self._debug_log(f"Text stripped of junk suffixes is empty!")

            text_message = TextMessagePdf(
                author=sender,
                is_id_confirmed=len(sender or '') > 0 and sender != STEVE_BANNON,
                text=msg,
                timestamp_str=timestamp_str,
            )

            if msgs and text_message == msgs[-1]:
                self._log(f"Parsed TextMessage is the same as the last one, skipping...\n")
                continue
            else:
                if msg:
                    self._log(f'adding TextMsg: {text_message.__rich__().plain}')
                    # self._log(f"Found sender='{sender}', timestamp_str='{timestamp_str}', msg={quote(msg)}")
                else:
                    self._warn(f"Skipping empty text message match from {sender} at {timestamp_str}...")

                capture_group_msgs = [f"[{g}] '" + quote(match.group(g).replace('\n', ' ').strip()) + "'" for g in MATCH_GROUPS]
                self._debug_log(f"[raw capture groups]\n\n{indented(capture_group_msgs, 8)}\n")

                if not msg:
                    continue

            msgs.append(text_message)

        return msgs

    def extract_timestamp(self) -> datetime:
        return self.extract_messages()[0].parse_timestamp()


@dataclass(kw_only=True)
class TextMessagePdf(TextMessage):
    def parse_timestamp(self) -> datetime:
        return coerce_utc(parse(self.timestamp_str))
