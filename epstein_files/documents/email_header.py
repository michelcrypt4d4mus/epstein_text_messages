import json
import re
from dataclasses import asdict, dataclass, field

from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.env import logger
from epstein_files.util.rich import UNKNOWN

HEADER_REGEX_STR = r'(((?:(?:Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):|on behalf of ?)(?! +(by |from my|via )).*\n){3,})'
EMAIL_SIMPLE_HEADER_REGEX = re.compile(rf'^{HEADER_REGEX_STR}')
EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX = re.compile(HEADER_REGEX_STR)
AUTHOR = 'author'
TO_FIELDS = ['bcc', 'cc', 'to']
EMAILER_FIELDS = [AUTHOR] + TO_FIELDS
ON_BEHALF_OF = 'on behalf of'


@dataclass(kw_only=True)
class EmailHeader:
    field_names: list[str]  # Ordered
    author: str | None = None
    sent_at: str | None = None
    subject: str | None = None
    bcc: list[str] | None = None
    cc: list[str] | None = None
    importance: str | None = None
    attachments: str | None = None
    to: list[str] | None = None

    def as_dict(self) -> dict[str, str | None]:
        """Remove 'field_names' field."""
        _dict = {}

        for k, v in asdict(self).items():
            if k != 'field_names':
                _dict[k] = v

        return _dict

    def is_empty(self) -> bool:
        return not any([v for _k, v in self.as_dict().items()])

    def __str__(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, indent=4)

    @classmethod
    def from_str(cls, header: str) -> 'EmailHeader':
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
        _str = _str.strip().removesuffix(REDACTED)
        _str = _str.strip().lstrip('"').lstrip("'").rstrip('"').rstrip("'").strip().strip('_')
        _str = _str.strip('[').strip(']').strip('*').strip('<').strip('•').rstrip(',').strip('>').strip()
        return _str
