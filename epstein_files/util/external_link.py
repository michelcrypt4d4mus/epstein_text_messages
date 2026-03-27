"""
Functions that build rich Text links.
"""
import re
from dataclasses import dataclass
from typing import Self, Sequence
from urllib.parse import urlsplit

from rich.style import Style
from rich.text import Text

from epstein_files.util.constant.strings import ARCHIVE_LINK_COLOR, ARCHIVE_ALT_LINK_STYLE, ARCHIVE_LINK_COLOR
from epstein_files.util.helpers.rich_helpers import TextCast, enclose, join_non_empty, join_texts, parenthesize
from epstein_files.util.logging import logger

HTTPS = 'https://'
BARE_URL_REGEX = re.compile(r"^[-\w.]+(/|\Z)")  # bare = 'missing https'
LINK_REGEX = re.compile(r"^https?://.*")
LINK_HREF_LINE_REGEX = re.compile(r"^([>• ]*)(http\S+)(.*)")
SUBSTACK_REGEX = re.compile(r'//(\w+)\.substack\.com')
TLD_REGEX = re.compile(r"\.(com|co.(nz|uk)|edu|fr|gov|io|net|org|ph)$")

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

SHORT_LINKS = {
    'aljazeera.com': 'alj',
    'bloomberg.com': 'bbg',
    'businessinsider.com': 'bi',
    # 'cryptadamus.substack': 'chronicles',
    'dossier.center': 'dossier',
    'dropsitenews': 'dropsite',
    'graziadaily': 'grazia',
    'hollywoodreporter': 'hollywood',
    'jmail.world/calendar': 'Jcal',
    'jmail.world': 'jmail',
    'justice.gov': 'doj',
    'instagram.com': 'insta',
    'lunch.publishersmarketplace': 'publ',
    'newyorker.com': 'NYer',
    'nypost.com': 'nyp',
    'nytimes.com': 'nyt',
    'reddit.com': 'rddt',
    'stanford.edu': 'stanford',
    # 'substack.com': 'sbstk',
    'tabletmag': 'tablet',
    'tommycarstensen.com': 'carstensen',
    'usatoday.com': 'usa',
    'vanityfair.com': 'vf',
    'wikipedia': 'wiki',
    'yahoo.com': 'yahoo',
}


@dataclass
class ExternalLink(TextCast):
    """
    Container for rich `Text` links with optional parenthetical comment.
    """
    url: str
    link_text: str = ''
    comment: str = ''
    comment_url: str = ''
    comment_style: str | Style = LINK_COMMENT_STYLE
    link_style: str | Style = EXTERNAL_LINK_STYLE
    parentheses_style: str = LINK_COMMENT_PARENTHESES_STYLE

    def __post_init__(self):
        if self.comment_url and not self.comment:
            raise ValueError(f"comment_url='{self.comment_url}' but no actual comment to attach it to.")

        self.url = coerce_https(self.url)
        self.comment_url = coerce_https(self.comment_url) if self.comment_url else self.comment_url
        # TODO: shouldn't need to convert, better to work with Style objs sometimes
        self.link_style = str(self.link_style)
        self.comment_style = str(self.comment_style)

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

    def domain_link(self, bracketed: bool = False) -> Text:
        """Returns a link using the TLD free domain as the `link_text`, e.g. '[wsj]' for a link to wsj.com."""
        link_text = ''

        for domain, shorthand in SHORT_LINKS.items():
            if domain in self.url:
                link_text = shorthand
                break

        if not link_text and (match := SUBSTACK_REGEX.search(self.url)):
            link_text = match.group(1)

        link_text = link_text or self.domain(True).removeprefix('the')
        link = link_text_obj(self.url, link_text, self.link_style)
        return enclose(link, '[]') if bracketed else link

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

    def link_with_text(self, link_text: str) -> Text:
        """Build a link with alternate text."""
        return link_text_obj(self.url, link_text, self.link_style)

    @classmethod
    def parenthesized_links(cls, _links: Sequence[Self | Text], base_style: str = 'white') -> Text:
        """Concatenate a collection of links and wrap in parentheses."""
        links = [link if isinstance(link, Text) else link.link for link in _links]
        links = [parenthesize(link) for link in links]
        return Text('', style=base_style).append(join_texts(links))

    def __rich__(self) -> Text:
        comment = Text('')

        if self.comment_url:
            comment = link_text_obj(self.comment_url, self.comment, self.comment_style)
            comment = enclose(comment, '()')
        elif self.comment:
            comment = enclose(Text(self.comment, self.comment_style), '()', self.parentheses_style)

        return join_non_empty(self.link, comment)


def coerce_https(url: str) -> str:
    """Prepend https:// if it's not there already."""
    if LINK_REGEX.match(url):
        return url
    elif not BARE_URL_REGEX.match(url):
        logger.warning(f'prepending https to "{url}" but looks invalid...')

    return f"https://{url}"


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
    return join_texts([hyperlink_line(line) for line in text.split('\n')], '\n', allow_falsey=True)


def link_markup(
    url: str,
    link_text: str = '',
    style: str | Style | None = ARCHIVE_LINK_COLOR,
    underline: bool = True
) -> str:
    """Create a rich markup string that can be turned to colored/linked `Text` with `Text.from_markup()`."""
    link_text = link_text or url.removeprefix('https://')
    style = ((str(style or '')) + (' underline' if underline else '')).strip()
    return f"[link={url}][{style}]{link_text}[/{style}][/link]"


def link_text_obj(url: str, link_text: str = '', style: str | Style = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(link_markup(url, link_text, style))
