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

KNOWN_TEXTERS = [
    EDUARDO_TEODORANI,
    EVA_DUBIN,
    LAWRENCE_KRAUSS,  # only fully confirmed in EFTA00508054
    MARTIN_NOWAK,     # only fully confirmed in EFTA00785782, could be other Martins
    TERJE_ROD_LARSEN,
]

SENDER_FIRST_NAMES = {
    **{name.split(' ')[0]: name for name in KNOWN_TEXTERS},
    'Self': JEFFREY_EPSTEIN,
    'Tetje': TERJE_ROD_LARSEN,
}


@dataclass
class MessengerLogPdf(MessengerLog):
    """Class for unstructured iMessage logs in some PDFs."""

    def extract_messages(self) -> list[TextMessage]:
        msgs: list[TextMessagePdf] = []

        if args.raw:
            print(f"\n\n------ REPAIRED TEXT -----\n{self.text}\n------ END TEXT -----\n\n")

        for match in MSG_REGEX.finditer(self.text):
            # Determine author
            timestamp_str = match.group('timestamp').strip()
            raw_sender = collapse_whitespace(match.group('sender').replace('(', '').replace(')', ''))
            sender = raw_sender

            if (sender_name := next((v for k, v in SENDER_FIRST_NAMES.items() if raw_sender.startswith(k)), None)):
                sender = sender_name
            elif self.file_id == 'EFTA00781689' and timestamp_str.startswith('2018-10-0') and sender in ['', 't']:
                sender = STEVE_BANNON
            elif VALID_SENDER_REGEX.search(sender) and (extracted_names := extract_emailer_names(sender)):
                if len(extracted_names) > 1:
                    self._error(f"Found multiple names, using first only! {extracted_names}")

                sender = extracted_names[0]
            else:
                sender = None

            # Clean up the actual message
            msg = match.group('msg').strip()

            if JUNK_SUFFIX_REGEX.search(msg):
                self._debug_log(f"removing junk suffixes from msg:\n-----\n{msg}\n-----")
                msg = JUNK_SUFFIX_REGEX.sub('', msg).strip()
                self._debug_log(f"msg stripped of junk suffixes:\n-----\n{msg}\n-----\n")

            text_message = TextMessagePdf(
                author=sender,
                is_id_confirmed=len(sender or '') > 0 and sender != STEVE_BANNON,
                text=msg,
                timestamp_str=timestamp_str,
            )

            if msgs and text_message == msgs[-1]:
                self._log(f"Parsed TextMessage is the same as the last one we found, skipping...")
                continue

            capture_group_msgs = [f"[{g}] '" + quote(match.group(g).replace('\n', ' ').strip()) + "'" for g in MATCH_GROUPS]
            capture_groups_str = f"[raw capture groups]\n\n{indented(capture_group_msgs, 8)}\n"

            if not msg:
                self._warn(f"Skipping empty text msg from {sender} at {timestamp_str}.\n\n{capture_groups_str}..")
                continue

            msgs.append(text_message)
            self._debug_log(f"Found sender='{sender}' from sender_raw='{raw_sender}', timestamp_str='{timestamp_str}', msg={quote(msg)}\nfor TextMsg: {text_message.__rich__().plain}")
            self._debug_log(capture_groups_str)

        return msgs

    def extract_timestamp(self) -> datetime:
        return self.extract_messages()[0].parse_timestamp()


@dataclass(kw_only=True)
class TextMessagePdf(TextMessage):
    def parse_timestamp(self) -> datetime:
        return coerce_utc(parse(self.timestamp_str))
