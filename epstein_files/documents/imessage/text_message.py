import re
from dataclasses import dataclass, fields
from datetime import datetime

from rich.text import Text

from epstein_files.util.constant.names import JEFFREY_EPSTEIN, STEVE_BANNON, UNKNOWN
from epstein_files.util.constant.strings import TIMESTAMP_DIM
from epstein_files.util.data import extract_last_name, iso_timestamp
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.logging import logger
from epstein_files.util.rich import TEXT_LINK, highlighter

MSG_DATE_FORMAT = r"%m/%d/%y %I:%M:%S %p"
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')

DISPLAY_LAST_NAME_ONLY = [
    JEFFREY_EPSTEIN,
    STEVE_BANNON,
]

TEXTER_MAPPING = {
    'e:': JEFFREY_EPSTEIN,
    'e:jeeitunes@gmail.com': JEFFREY_EPSTEIN,
}


@dataclass(kw_only=True)
class TextMessage:
    """Class representing a single iMessage text message."""
    author: str | None
    author_str: str = ''
    id_confirmed: bool = False
    text: str
    timestamp_str: str

    def __post_init__(self):
        self.author = TEXTER_MAPPING.get(self.author or UNKNOWN, self.author)

        if not self.author:
            self.author_str = UNKNOWN
        elif self.author in DISPLAY_LAST_NAME_ONLY and not self.author_str:
            self.author_str = extract_last_name(self.author)
        else:
            self.author_str = self.author_str or self.author

        if not self.id_confirmed and self.author is not None and self.author != JEFFREY_EPSTEIN:
            self.author_str += ' (?)'

    def parse_timestamp(self) -> datetime:
        return datetime.strptime(self.timestamp_str, MSG_DATE_FORMAT)

    def timestamp_txt(self) -> Text:
        timestamp_str = self.timestamp_str

        try:
            timestamp_str = iso_timestamp(self.parse_timestamp())
        except Exception as e:
            logger.warning(f"Failed to parse timestamp for {self}")

        return Text(f"[{timestamp_str}]", style=TIMESTAMP_DIM)

    def _message(self) -> Text:
        lines = self.text.split('\n')

        # Fix multiline links
        if self.text.startswith('http'):
            text = self.text

            if len(lines) > 1 and not lines[0].endswith('html'):
                if len(lines) > 2 and lines[1].endswith('-'):
                    text = text.replace('\n', '', 2)
                else:
                    text = text.replace('\n', '', 1)

            lines = text.split('\n')
            link_text = lines.pop()
            msg_txt = Text('').append(Text.from_markup(f"[link={link_text}]{link_text}[/link]", style=TEXT_LINK))

            if len(lines) > 0:
                msg_txt.append('\n' + ' '.join(lines))
        else:
            msg_txt = highlighter(' '.join(lines))  # remove newlines

        return msg_txt

    def __rich__(self) -> Text:
        timestamp_txt = self.timestamp_txt().append(' ')
        author_style = get_style_for_name(self.author_str if self.author_str.startswith('+') else self.author)
        author_txt = Text(self.author_str, style=author_style)
        return Text('').append(timestamp_txt).append(author_txt).append(': ', style='dim').append(self._message())

    def __repr__(self) -> str:
        props = []
        add_prop = lambda k, v: props.append(f"{k}={v}")

        for _field in sorted(fields(self), key=lambda f: f.name):
            key = _field.name
            value = getattr(self, key)

            if key == 'author_str' and self.author and self.author_str.startswith(value):
                continue
            elif isinstance(value, str):
                add_prop(key, f'"{value}"')
            else:
                add_prop(key, value)

        return f"{type(self).__name__}(" + ', '.join(props) + f')'
