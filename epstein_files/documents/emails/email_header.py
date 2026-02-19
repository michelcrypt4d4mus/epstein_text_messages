import json
import re
from dataclasses import asdict, dataclass, field

from epstein_files.documents.documents.doc_cfg import EmailCfg
from epstein_files.documents.emails.constants import FIELDS_PATTERN
from epstein_files.documents.emails.emailers import BAD_EMAILER_REGEX, TIME_REGEX
from epstein_files.util.constant.strings import AUTHOR
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.helpers.string_helper import indented
from epstein_files.util.logging import logger

FIELD_NAMES = ['Date', 'From', 'Sent', 'Subject']
ON_BEHALF_OF = 'on behalf of'
TO_FIELDS = ['bcc', 'cc', 'to']
EMAILER_FIELDS = [AUTHOR] + TO_FIELDS

DETECT_EMAIL_REGEX = re.compile(r'^(.*\n){0,2}(From|Subject):')  # IDed 140 emails out of 3777 DOJ files with just 'From:' match
HEADER_REGEX_STR = fr"(((?:(?:{FIELDS_PATTERN}|Bee):|on behalf of ?)(?! +(by |from my|via )).*\n){{3,}})"
EMAIL_SIMPLE_HEADER_REGEX = re.compile(rf'^{HEADER_REGEX_STR}')
EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX = re.compile(HEADER_REGEX_STR)
EMAIL_PRE_FORWARD_REGEX = re.compile(r"(.{3,2000}?)" + HEADER_REGEX_STR, re.DOTALL)  # Match up to the next email header section

CONFIGURED_ACTUAL_TEXTS = [
    cfg.actual_text for cfg in CONFIGS_BY_ID.values()
    if isinstance(cfg, EmailCfg) and cfg.actual_text is not None
]

NON_HEADER_FIELDS = [
    'field_names',
    'header_chars',
    'num_header_rows',
    'was_initially_empty',
]


@dataclass(kw_only=True)
class EmailHeader:
    field_names: list[str]  # Order is same as the order header fields appear in the email file text
    header_chars: str = ''
    num_header_rows: int = field(init=False)
    was_initially_empty: bool = False

    # Fields from the email text
    author: str | None = None
    sent_at: str | None = None
    subject: str | None = None
    bcc: list[str] | None = None
    cc: list[str] | None = None
    classification: str | None = None
    flag: str | None = None
    importance: str | None = None
    inline_images: str | None = None
    attachments: str | None = None
    attached: str | None = None
    to: list[str] | None = None
    reply_to: str | None = None

    @property
    def is_empty(self) -> bool:
        return not any(v for v in self.as_dict().values())

    @property
    def recipients(self) -> list[str]:
        return (self.to or []) + (self.cc or []) + (self.bcc or [])

    def __post_init__(self):
        self.num_header_rows = len(self.field_names)
        self.was_initially_empty = self.is_empty

    def as_dict(self, truthy_only: bool = True) -> dict[str, str | None]:
        """Remove housekeeping fields that don't actually come from the email."""
        props = {k: v for k, v in asdict(self).items() if k not in NON_HEADER_FIELDS}
        return {k: v for k, v in props.items() if v} if truthy_only else props

    def repair_empty_header(self, email_lines: list[str]) -> None:
        num_headers = len(self.field_names)

        # Sometimes the headers and values are on separate lines and we need to do some shenanigans
        for i, field_name in enumerate(self.field_names):
            row_number_to_check = i + num_headers  # Look ahead 3 lines if there's 3 header fields, 4 if 4, etc.

            if row_number_to_check > (len(email_lines) - 1):
                raise RuntimeError(f"Ran out of header rows to check for '{field_name}'")

            value = email_lines[row_number_to_check]
            log_prefix = f"Looks like '{value}' is a mismatch for '{field_name}'"

            if field_name == AUTHOR:
                if value in CONFIGURED_ACTUAL_TEXTS:
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
                elif BAD_EMAILER_REGEX.match(value) or value.startswith('http'):
                    logger.info(f"{log_prefix}, decrementing num_headers and skipping...")
                    num_headers -= 1
                    continue

                value = [v.strip() for v in value.split(';') if len(v.strip()) > 0]

            setattr(self, field_name, value)

        self.num_header_rows = len(self.field_names) + num_headers
        self.header_chars = '\n'.join(email_lines[0:self.num_header_rows])
        log_msg = f"Corrected empty header using {self.num_header_rows} lines to:\n"

        logger.info(
            f"{log_msg}{self}\n\n[top lines]:\n\n%s\n\n[body_lines]:\n\n%s\n\n",
            indented('\n'.join(email_lines[0:(num_headers + 1) * 2]), prefix='> '),
            indented('\n'.join(email_lines[self.num_header_rows:self.num_header_rows + 5]), prefix='> '),
        )

    def rewrite_header(self) -> str:
        header_fields = {}

        for field_name in self.field_names:
            if field_name == AUTHOR:
                header_fields['From'] = self.author or ''
            elif field_name == 'sent_at':
                if self.sent_at in CONFIGURED_ACTUAL_TEXTS:
                    header_fields['Date'] = ''
                else:
                    header_fields['Date'] = self.sent_at or ''
            elif field_name in TO_FIELDS:
                header_fields[field_name.title()] = '; '.join(getattr(self, field_name) or [])
            else:
                header_fields[field_name.title()] = getattr(self, field_name) or ''

        return '\n'.join([f"{k}: {v}" for k, v in header_fields.items()])

    def __str__(self) -> str:
        return json.dumps(self.as_dict(truthy_only=False), sort_keys=True, indent=4)

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
            key = AUTHOR if key == 'From' else ('sent_at' if key in ['Date', 'Sent'] else key.lower().replace('-', '_'))
            key = 'bcc' if key == 'bee' else key

            if kw_args.get(key):
                logger.debug(f'Already have value "{kw_args[key]}" at key "{key}", not overwriting with "{value}"')
                should_log_header = True
                continue

            field_names.append(key)

            if key == 'reply_to':
                logger.warning(f"Found value for Reply-To field: '{value}'")

            if key in TO_FIELDS:
                recipients = [element.strip() for element in value.split(';')]
                recipients = [r for r in recipients if len(r) > 0]
                kw_args[key] = None if len(value) == 0 else [r if len(r) > 0 else UNKNOWN for r in recipients]
            else:
                kw_args[key.lower()] = None if len(value) == 0 else value

        if should_log_header:
            logger.debug(f"Header being parsed was this:\n\n{header}\n")

        return cls(field_names=field_names, header_chars=header, **kw_args)
