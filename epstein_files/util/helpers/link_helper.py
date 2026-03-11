"""
Functions that build rich Text links.
"""
import re

from dataclasses import dataclass
from rich.text import Text
from typing import Self

from epstein_files.util.constant.strings import (ARCHIVE_LINK_COLOR, ARCHIVE_ALT_LINK_STYLE,
     ARCHIVE_LINK_COLOR, SOCIAL_MEDIA_LINK_STYLE)
from epstein_files.util.helpers.rich_helpers import enclose, join_non_empty

EXTERNAL_LINK_STYLE = 'light_slate_grey bold'
OFFICIAL_LINK_STYLE = 'navajo_white3 bold'
SUBSTACK_POST_LINK_STYLE = 'bright_cyan'

LINK_REGEX = re.compile(r"^https?://.*")

SOCIAL_PLATFORMS = {
    'substack': 'substack',
    'universeodon': 'mastodon',
    'x.com': 'twitter',
}


@dataclass
class ExternalLink:
    """Container for rich `Text` links with optional parenthetical comment."""

    url: str
    link_text: str = ''
    comment: str = ''
    comment_style: str = ''
    comment_url: str = ''
    link_style: str = EXTERNAL_LINK_STYLE
    parentheses_style: str = 'gray27'

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
    def domain_stem(self) -> str:
        """e.g. retrun 'github' for a github.com/blah URL."""
        return self.url.removeprefix('https://').split('.')[0]

    @property
    def link(self) -> Text:
        return link_text_obj(self.url, self.link_text, self.link_style)

    def __rich__(self) -> Text:
        comment = Text('')

        if self.comment_url:
            comment = link_text_obj(self.comment_url, self.comment, self.comment_style)
            comment = enclose(comment, '()')
        elif self.comment:
            comment = enclose(Text(self.comment, 'color(195) dim italic'), '()', self.parentheses_style)

        return join_non_empty(self.link, comment)


def coerce_https(url: str) -> str:
    """Prepend https:// if it's not there already."""
    return url if LINK_REGEX.match(url) else f"https://{url}"


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
