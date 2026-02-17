"""
Functions that build rich Text links.
"""

from rich.text import Text

from epstein_files.util.constant.strings import ARCHIVE_LINK_COLOR


def link_markup(
    url: str,
    link_text: str | None = None,
    style: str | None = ARCHIVE_LINK_COLOR,
    underline: bool = True
) -> str:
    link_text = link_text or url.removeprefix('https://')
    style = ((style or '') + (' underline' if underline else '')).strip()
    return (f"[{style}][link={url}]{link_text}[/link][/{style}]")


def link_text_obj(url: str, link_text: str | None = None, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(link_markup(url, link_text, style))
