"""
String manipulation.
"""
import re
from datetime import datetime
from typing import Any

from inflection import underscore

from epstein_files.util.constant.strings import QUESTION_MARKS_REGEX

PDFALYZER_IMAGE_PANEL_REGEX = re.compile(r"\n╭─* Page \d+, Image \d+.*?╯\n?", re.DOTALL)
MULTINEWLINE_REGEX = re.compile(r"\n{2,}")
MULTISPACE_REGEX = re.compile(" +")
WHITESPACE_CHAR = r"[-_\s]*"
DATE_LENGTH = len('2025-05-05')

capitalize_first = lambda s: s[0].upper() + s[1:]
capture_group_marker = lambda label: fr"?P<{label}>"
collapse_newlines = lambda text: MULTINEWLINE_REGEX.sub('\n\n', text)
collapse_spaces = lambda s: MULTISPACE_REGEX.sub(' ', s)
is_bool_prop = lambda prop: prop.startswith('is_')
iso_timestamp = lambda dt: dt.isoformat().replace('T', ' ')
strip_pdfalyzer_panels = lambda s: PDFALYZER_IMAGE_PANEL_REGEX.sub('', s)


def as_pattern(s: str) -> str:
    """Replace spaces with regex pattern for whitespace."""
    s = collapse_spaces(s)
    return s if '?<!' in s else s.replace(' ', WHITESPACE_CHAR)


def constantize(s: str) -> str:
    return underscore(s.upper())


def has_line_starting_with(s: str | list[str], pfxes: str | list[str], limit: int | None = None) -> bool:
    lines = s.split('\n') if isinstance(s, str) else s
    lines = lines[0:(limit or len(lines))]

    for line in lines:
        if any(line.startswith(pfx) for pfx in list(pfxes)):
            return True

    return False


def indented(s: str, spaces: int = 4, prefix: str = '') -> str:
    indent = (' ' * spaces) + prefix
    return indent + f"\n{indent}".join(s.split('\n'))


def join_truthy(prefix: str | None, suffix: str | None, sep: str = '') -> str:
    """Join two strings but only if they are not empty."""
    sep = sep or (' ' if prefix and suffix else '')
    parts = [p.strip() for p in [prefix, suffix] if p and p.strip()]
    return sep.join(parts)


def prop_str(prop: Any) -> Any:
    if isinstance(prop, (datetime, str)):
        return quote(str(prop))
    else:
        return str(prop)


def quote(s: str, try_single_quote_first: bool = False) -> str:
    if '"' in s and "'" in s:
        return s
    elif s and s[0] in ['"', "'"]:
        return s
    elif try_single_quote_first:
        return f"'{s}'" if "'" not in s else f'"{s}"'
    else:
        return f"'{s}'" if '"' in s else f'"{s}"'


def remove_question_marks(name: str):
    return QUESTION_MARKS_REGEX.sub('', name).strip()


def starred_header(msg: str, num_stars: int = 7, num_spaces: int = 2) -> str:
    """String like '  *** Title Msg ***  '."""
    stars = '*' * num_stars
    spaces = ' ' * num_spaces
    return f"{spaces}{stars} {msg} {stars}{spaces}"
