import json
import re
from dataclasses import asdict, dataclass, field

from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.env import logger
from epstein_files.util.rich import UNKNOWN

HEADER_REGEX_STR = r'(((?:(?:Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):|on behalf of ?)(?! +(by |from my|via )).*\n){3,})'
EMAIL_SIMPLE_HEADER_REGEX = re.compile(rf'^{HEADER_REGEX_STR}')
EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX = re.compile(HEADER_REGEX_STR)
TIME_REGEX = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday).*')

BAD_NAME_CHARS_REGEX = re.compile(r"[\"'\[\]*><•]")
BAD_EMAILER_REGEX = re.compile(r'^(>|11111111)|agreed|ok|sexy|rt|re:|fwd:|Multiple Senders|((sent|attachments|subject|importance).*|.*(january|201\d|hysterical|i have|image0|so that people|article 1.?|momminnemummin|These conspiracy theories|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)).*)$', re.IGNORECASE)
SKIP_HEADER_ROW_REGEX = re.compile(r"^(agreed|call me|Hysterical|schwartman).*")  # Known bad rows in bad OCR

AUTHOR = 'author'
ON_BEHALF_OF = 'on behalf of'
TO_FIELDS = ['bcc', 'cc', 'to']
EMAILER_FIELDS = [AUTHOR] + TO_FIELDS
NON_HEADER_FIELDS = ['field_names', 'num_header_rows', 'was_initially_empty']


@dataclass(kw_only=True)
class EmailHeader:
    field_names: list[str]  # Order is same as the order header fields appear in the email file text
    num_header_rows: int = field(init=False)
    was_initially_empty: bool = False

    # Fields from the email text
    author: str | None = None
    sent_at: str | None = None
    subject: str | None = None
    bcc: list[str] | None = None
    cc: list[str] | None = None
    importance: str | None = None
    attachments: str | None = None
    to: list[str] | None = None

    def __post_init__(self):
        self.num_header_rows = len(self.field_names)
        self.was_initially_empty = self.is_empty()

    def as_dict(self) -> dict[str, str | None]:
        """Remove housekeeping fields that don't actually come from the email."""
        return {k: v for k, v in asdict(self).items() if k not in NON_HEADER_FIELDS}

    def is_empty(self) -> bool:
        return not any([v for _k, v in self.as_dict().items()])

    def recipients(self) -> list[str]:
        return (self.to or []) + (self.cc or []) + (self.bcc or [])

    def repair_empty_header(self, email_lines: list[str]) -> None:
        num_headers = len(self.field_names)

        # Sometimes the headers and values are on separate lines and we need to do some shenanigans
        for i, field_name in enumerate(self.field_names):
            row_number_to_check = i + num_headers  # Look ahead 3 lines if there's 3 header fields, 4 if 4, etc.

            if row_number_to_check > (len(email_lines) - 1):
                raise RuntimeError(f"Ran out of header rows to check for '{field_name}'")

            value = email_lines[row_number_to_check]
            log_prefix = f"Looks like '{value}' is a mismatch for '{field_name}', "

            if field_name == AUTHOR:
                if SKIP_HEADER_ROW_REGEX.match(value):
                    logger.info(f"{log_prefix}, trying the next line...")
                    num_headers += 1
                    value = email_lines[i + num_headers]
                elif TIME_REGEX.match(value) or value == 'Darren,' or BAD_EMAILER_REGEX.match(value):
                    logger.info(f"{log_prefix}, decrementing num_headers and skipping...")
                    num_headers -= 1
                    continue
            elif field_name in TO_FIELDS:
                if TIME_REGEX.match(value):
                    logger.info(f"{log_prefix}, trying next line...")
                    num_headers += 1
                    value = email_lines[i + num_headers]
                elif BAD_EMAILER_REGEX.match(value):
                    logger.info(f"{log_prefix}, decrementing num_headers and skipping...")
                    num_headers -= 1
                    continue

                value = [v.strip() for v in value.split(';') if len(v.strip()) > 0]

            setattr(self, field_name, value)

        self.num_header_rows = len(self.field_names) + num_headers
        logger.debug(f"Corrected empty header using {self.num_header_rows} lines to:\n%s\n\nTop lines:\n\n%s", self, '\n'.join(email_lines[0:(num_headers + 1) * 2]))

    def __str__(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, indent=4)

    @classmethod
    def from_header_lines(cls, header: str) -> 'EmailHeader':
        kw_args = {}
        field_names = []
        should_log_header = False

        for line in [l.strip() for l in header.strip().split('\n')]:
            if line.lower().startswith(ON_BEHALF_OF):
                author = line.removeprefix(ON_BEHALF_OF).strip()

                if len(author) > 0:
                    kw_args[AUTHOR] = author

                continue

            #logger.debug(f"extracting header line: '{line}'")
            key, value = [element.strip() for element in line.split(':', 1)]
            value = value.rstrip('_')
            key = AUTHOR if key == 'From' else ('sent_at' if key in ['Date', 'Sent'] else key.lower())
            key = 'bcc' if key == 'bee' else key

            if kw_args.get(key):
                logger.debug(f'Already have value "{kw_args[key]}" at key "{key}", not overwriting with "{value}"')
                should_log_header = True
                continue

            field_names.append(key)

            if key in TO_FIELDS:
                recipients = [element.strip() for element in value.split(';')]
                recipients = [r for r in recipients if len(r) > 0]
                kw_args[key] = None if len(value) == 0 else [r if len(r) > 0 else UNKNOWN for r in recipients]
            else:
                kw_args[key.lower()] = None if len(value) == 0 else value

        if should_log_header:
            logger.debug(f"Header being parsed was this:\n\n{header}\n")

        return EmailHeader(field_names=field_names, **kw_args)

    @staticmethod
    def cleanup_str(_str: str) -> str:
        return BAD_NAME_CHARS_REGEX.sub('', _str.replace(REDACTED, '')).strip().strip('_').strip()
