"""
Functions that build rich Text links.
"""
import re
from typing import Self, Sequence
from urllib.parse import urlsplit

from dataclasses import dataclass
from rich.text import Text

from epstein_files.util.constant.strings import ARCHIVE_LINK_COLOR, ARCHIVE_ALT_LINK_STYLE, ARCHIVE_LINK_COLOR
from epstein_files.util.helpers.rich_helpers import enclose, join_non_empty

HTTPS = 'https://'
LINK_REGEX = re.compile(r"^https?://.*")
LINK_HREF_LINE_REGEX = re.compile(r"^([>• ]*)(http\S+)(.*)")
TLD_REGEX = re.compile(r"\.(com|co.uk|gov|net)$")

EXTERNAL_LINK_STYLE = 'light_slate_grey bold'
LINK_COMMENT_STYLE = 'color(195) dim italic'
OFFICIAL_LINK_STYLE = 'navajo_white3 bold'
LINK_COMMENT_PARENTHESES_STYLE = 'gray27'
SOCIAL_MEDIA_LINK_STYLE = 'pale_turquoise4'
SUBSTACK_POST_LINK_STYLE = 'bright_cyan'

SOCIAL_PLATFORMS = {
    'universeodon': 'mastodon',
    'x.com': 'twitter',
}


@dataclass
class ExternalLink:
    """
    Container for rich `Text` links with optional parenthetical comment.
    """
    url: str
    link_text: str = ''
    comment: str = ''
    comment_url: str = ''
    comment_style: str = LINK_COMMENT_STYLE
    link_style: str = EXTERNAL_LINK_STYLE
    parentheses_style: str = LINK_COMMENT_PARENTHESES_STYLE

    def __post_init__(self):
        self.url = coerce_https(self.url)
        self.comment_url = coerce_https(self.comment_url) if self.comment_url else self.comment_url

    @classmethod
    def official_link(cls, url: str, link_text: str, comment: str, comment_url: str, **kwargs) -> Self:
        """Alternate constructor for differently colored links to official sources like justice.gov."""
        def pop_with_default(arg: str, default_value: str) -> str:
            return kwargs.pop(arg) if arg in kwargs else default_value

        return cls(
            url=url,
            link_text=link_text,
            comment=comment,
            comment_style=pop_with_default('comment_style', ARCHIVE_ALT_LINK_STYLE),
            comment_url=comment_url,
            link_style=pop_with_default('link_style', OFFICIAL_LINK_STYLE),
            parentheses_style='wheat4',
            **kwargs
        )

    @classmethod
    def social_link(cls, url: str, platform_name: str = '') -> Self:
        """Alternate constructor for social media links."""
        if not platform_name:
            for domain_str, platform in SOCIAL_PLATFORMS.items():
                if domain_str in url:
                    platform_name = platform
                    break

        link = cls(url, platform_name, link_style=SOCIAL_MEDIA_LINK_STYLE)
        link.link_text = f"@{link.link_text or link.domain_stem}"
        return link

    @property
    def domain_link(self) -> Text:
        """Returns a link using the TLD free domain as the `link_text`."""
        return enclose(link_text_obj(self.url, self.domain(True), self.link_style), '[]')

    @property
    def domain_stem(self) -> str:
        """e.g. retrun 'github' for a github.com/blah URL."""
        domain_pieces = self.domain().split('.')

        if len(domain_pieces) == 2:
            return domain_pieces[0]
        elif len(domain_pieces) == 3:
            return domain_pieces[1]
        else:
            raise ValueError(f"Can't extract domain_stem for '{self.url}' (domain_pieces={domain_pieces})")

    @property
    def link(self) -> Text:
        """Link without the (comment) part."""
        return link_text_obj(self.url, self.link_text, self.link_style)

    @property
    def short_url(self) -> str:
        return self.url.removeprefix(HTTPS)

    @property
    def url_link(self) -> Text:
        """Link that uses the short_url as link_text (overriding actual link_text property)."""
        return link_text_obj(self.url, self.short_url, self.link_style)

    def domain(self, strip_tld: bool = False) -> str:
        return extract_domain(self.url, strip_tld=strip_tld)

    def to_txt(self) -> Text:
        comment = Text('')

        if self.comment_url:
            comment = link_text_obj(self.comment_url, self.comment, self.comment_style)
            comment = enclose(comment, '()')
        elif self.comment:
            comment = enclose(Text(self.comment, self.comment_style), '()', self.parentheses_style)

        return join_non_empty(self.link, comment)

    @classmethod
    def parenthesized_links(cls, _links: list[Self | Text], base_style: str = 'white') -> Text:
        """Concatenate a collection of links and wrap in parentheses."""
        links = [link if isinstance(link, Text) else link.link for link in _links]
        links = [parenthesize(link) for link in links]
        txt = Text('', style=base_style)
        return txt.append(join_texts(links))

    def __rich__(self) -> Text:
        return self.to_txt()


def coerce_https(url: str) -> str:
    """Prepend https:// if it's not there already."""
    return url if LINK_REGEX.match(url) else f"https://{url}"


def extract_domain(url: str, strip_tld: bool = False) -> str:
    if (domain := urlsplit(url).hostname):
        domain = domain.removeprefix('www.')
        return TLD_REGEX.sub('', domain) if strip_tld else domain
    else:
        raise ValueError(f"no hostname in URL '{url}'")


def hyperlink_line(line: str) -> Text:
    """Handles single line only. Add [link] tags if appropriate."""
    if (match := LINK_HREF_LINE_REGEX.match(line)):
        link = match.group(2)
        txt = Text(match.group(1))
        txt.append(Text.from_markup(f"[link={link}]{link}[/link]"))
        return txt.append(match.group(3))
    else:
        return Text(line)


def hyperlink_text(text: str) -> Text:
    """Add rich Text hyperlinks to a string with newlines in it."""
    return join_texts([hyperlink_line(line) for line in text.split('\n')], '\n')


def join_texts(
    _txts: Sequence[str | ExternalLink | Text],
    join: str = ' ',
    encloser: str = '',
    encloser_style: str = 'wheat4'
) -> Text:
    """Join a collection of `Text` objs into one, similar to standard `str.join()`."""
    txts = [t.to_txt() if isinstance(t, ExternalLink) else t for t in _txts]
    txt = Text('')

    for i, _txt in enumerate(txts):
        txt.append(join if i >= 1 else '').append(enclose(_txt, encloser, encloser_style))

    return txt


def link_markup(
    url: str,
    link_text: str = '',
    style: str | None = ARCHIVE_LINK_COLOR,
    underline: bool = True
) -> str:
    """Create a rich markup string that can be turned to colored/linked `Text` with `Text.from_markup()`."""
    link_text = link_text or url.removeprefix('https://')
    style = ((style or '') + (' underline' if underline else '')).strip()
    return f"[link={url}][{style}]{link_text}[/{style}][/link]"


def link_text_obj(url: str, link_text: str = '', style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(link_markup(url, link_text, style))


def parenthesize(msg: str | Text, parentheses_style: str = '') -> Text:
    txt = Text(msg) if isinstance(msg, str) else msg
    return Text('(', style=parentheses_style).append(txt).append(')')
