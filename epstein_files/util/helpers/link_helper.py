"""
Functions that build rich Text links.
"""
from dataclasses import dataclass
from rich.text import Text
from typing import Self

from epstein_files.util.constant.strings import ARCHIVE_LINK_COLOR, ARCHIVE_ALT_LINK_STYLE, ARCHIVE_LINK_COLOR
from epstein_files.util.helpers.rich_helpers import enclose, join_non_empty

EXTERNAL_LINK_STYLE = 'light_slate_grey bold'
OFFICIAL_LINK_STYLE = 'navajo_white3 bold'
SUBSTACK_POST_LINK_STYLE = 'bright_cyan'



    # doj_search_link = join_texts([link_text_obj(DOJ_SEARCH_URL, 'search', style=ARCHIVE_ALT_LINK_STYLE)], encloser='()')
    # print_centered(_link_with_comment(DOJ_2026_URL, doj_search_link, 'DOJ Epstein Files Transparency Act Disclosures'))
    # raw_docs_link = link_text_obj(OVERSIGHT_DRIVE_URL, 'raw files', style=ARCHIVE_ALT_LINK_STYLE)
    # raw_docs_link = join_texts([raw_docs_link], encloser='()')
    # print_centered(_link_with_comment(OVERSIGHT_REPUBS_PRESSER_URL, raw_docs_link, '2025 Oversight Committee Press Release'))

@dataclass
class ExternalLink:
    url: str
    comment: str = ''
    comment_style: str = ''
    comment_url: str = ''
    link_style: str = EXTERNAL_LINK_STYLE
    link_text: str = ''
    parentheses_style: str = 'gray27'

    @classmethod
    def official_link(cls, url: str,  **kwargs) -> Self:
        """Alternate constructor."""
        def pop_with_default(arg: str, default_value: str) -> str:
            return kwargs.pop(arg) if arg in kwargs else default_value

        return cls(
            url,
            comment_style=pop_with_default('comment_style', ARCHIVE_ALT_LINK_STYLE),
            link_style=pop_with_default('link_style', OFFICIAL_LINK_STYLE),
            parentheses_style='wheat4',
            **kwargs
        )

    @property
    def link(self) -> Text:
        return link_text_obj(self.url, self.link_text, self.link_style)

    @property
    def link_with_comment(self) -> Text:
        comment = Text('')

        if self.comment_url:
            comment = link_text_obj(self.comment_url, self.comment, self.comment_style)
            comment = enclose(comment, '()')
        elif self.comment:
            comment = enclose(Text(self.comment, 'color(195) dim italic'), '()', self.parentheses_style)

        return join_non_empty(self.link, comment)


def link_markup(
    url: str,
    link_text: str = '',
    style: str | None = ARCHIVE_LINK_COLOR,
    underline: bool = True
) -> str:
    link_text = link_text or url.removeprefix('https://')
    style = ((style or '') + (' underline' if underline else '')).strip()
    return (f"[{style}][link={url}]{link_text}[/link][/{style}]")


def link_text_obj(url: str, link_text: str = '', style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(link_markup(url, link_text, style))


def parenthesize(msg: str | Text, parentheses_style: str = '') -> Text:
    txt = Text(msg) if isinstance(msg, str) else msg
    return Text('(', style=parentheses_style).append(txt).append(')')
