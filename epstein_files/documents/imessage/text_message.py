import re
from dataclasses import dataclass, field, fields
from datetime import datetime

from rich.text import Text

from epstein_files.util.constant.names import ANTHONY_SCARAMUCCI, JEFFREY_EPSTEIN, STEVE_BANNON, UNKNOWN, Name, extract_last_name
from epstein_files.util.constant.strings import TIMESTAMP_DIM
from epstein_files.util.data import iso_timestamp
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.logging import logger
from epstein_files.util.rich import TEXT_LINK, highlighter

EPSTEIN_TEXTERS = ['e:', 'e:jeeitunes@gmail.com']
MSG_DATE_FORMAT = r"%m/%d/%y %I:%M:%S %p"
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
UNCERTAIN_SUFFIX = ' (?)'

DISPLAY_LAST_NAME_ONLY = [
    ANTHONY_SCARAMUCCI,
    JEFFREY_EPSTEIN,
    STEVE_BANNON,
]


@dataclass(kw_only=True)
class TextMessage:
    """Class representing a single iMessage text message."""
    author: Name
    author_str: str = ''
    is_id_confirmed: bool = False
    text: str
    timestamp_str: str

    def __post_init__(self):
        self.author = JEFFREY_EPSTEIN if self.author in EPSTEIN_TEXTERS else self.author

        if not self.author:
            self.author_str = UNKNOWN
        elif self.author in DISPLAY_LAST_NAME_ONLY and not self.author_str:
            self.author_str = extract_last_name(self.author)
        else:
            self.author_str = self.author_str or self.author

        if not self.is_id_confirmed and self.author is not None and self.author != JEFFREY_EPSTEIN:
            self.author_str += UNCERTAIN_SUFFIX

        if self.is_link():
            self.text = self.text.replace('\n', '').replace(' ', '_')
        else:
            self.text = self.text.replace('\n', ' ')

    def is_link(self) -> bool:
        return self.text.startswith('http')

    def parse_timestamp(self) -> datetime:
        return datetime.strptime(self.timestamp_str, MSG_DATE_FORMAT)

    def timestamp_txt(self) -> Text:
        try:
            timestamp_str = iso_timestamp(self.parse_timestamp())
        except Exception as e:
            logger.info(f"Failed to parse timestamp for {self}")
            timestamp_str = self.timestamp_str

        return Text(f"[{timestamp_str}]", style=TIMESTAMP_DIM)

    def _message(self) -> Text:
        if self.is_link():
            return Text.from_markup(f"[link={self.text}]{self.text}[/link]", style=TEXT_LINK)
        else:
            return highlighter(self.text)

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
