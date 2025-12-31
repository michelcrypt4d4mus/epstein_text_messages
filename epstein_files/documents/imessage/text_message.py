import re
from dataclasses import dataclass, field
from datetime import datetime

from rich.text import Text

from epstein_files.util.constant.names import JEFFREY_EPSTEIN, SCARAMUCCI, STEVE_BANNON, UNKNOWN
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.rich import TEXT_LINK, highlighter, logger

MSG_DATE_FORMAT = r"%m/%d/%y %I:%M:%S %p"
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
TIMESTAMP_STYLE = 'turquoise4 dim'

DISPLAY_LAST_NAME_ONLY = [
    JEFFREY_EPSTEIN,
    STEVE_BANNON,
]

UNKNOWN_TEXTERS = [
    '+16463880059',
    '+13108737937',
    '+13108802851',
]

TEXTER_MAPPING = {
    'e:': JEFFREY_EPSTEIN,
    'e:jeeitunes@gmail.com': JEFFREY_EPSTEIN,
    '+19174393646': SCARAMUCCI,
    '+13109906526': STEVE_BANNON,
}


@dataclass(kw_only=True)
class TextMessage:
    """Class representing a single iMessage text message."""
    author: str | None
    author_str: str = field(init=False)
    id_confirmed: bool = False
    text: str
    timestamp_str: str

    def __post_init__(self):
        self.author = TEXTER_MAPPING.get(self.author or UNKNOWN, self.author)

        if self.author is None:
            self.author_str = UNKNOWN
        elif self.author in UNKNOWN_TEXTERS:
            logger.warning(f"Bad text from '{self.author}': \"{self.text}\"")
            self.author_str = self.author
            self.author = None  # TODO: this shouldn't be happening; we still know the author...
        elif self.author in DISPLAY_LAST_NAME_ONLY:
            self.author_str = self.author.split()[-1]
        else:
            self.author_str = self.author

        if not self.id_confirmed and self.author is not None:
            self.author_str = self.author + ' (?)'

    def timestamp(self) -> datetime:
        return datetime.strptime(self.timestamp_str, MSG_DATE_FORMAT)

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
        # TODO: Workaround for phone numbers that sucks
        author_style = get_style_for_name(self.author_str if self.author_str.startswith('+') else self.author)
        author_txt = Text(self.author_str, style=author_style)
        timestamp_txt = Text(f"[{self.timestamp_str}]", style=TIMESTAMP_STYLE).append(' ')
        return Text('').append(timestamp_txt).append(author_txt).append(': ', style='dim').append(self._message())
