"""
String manipulation.
"""
import re
from datetime import datetime
from typing import Any

from inflection import underscore

from epstein_files.util.constant.strings import AMPERSAND_CHAR_GROUP, QUESTION_MARKS_REGEX
from epstein_files.util.logging import logger, text_block

DATE_LENGTH = len('2025-05-05')
WHITESPACE_CHAR = r"[-_.\s]*"

EMOJI_REGEX = re.compile(r"(?:^|\s)([:;=][-^]?[oODP()]|[oO()][-^]?[:=])(?=$|\s)")
INTEGER_REGEX = re.compile(r'^\d+$')
MULTINEWLINE_REGEX = re.compile(r"\n{2,}")
MULTISPACE_REGEX = re.compile(" +")
PDFALYZER_IMAGE_PANEL_REGEX = re.compile(r"\n╭─* Page \d+, Image \d+.*?╯\n?", re.DOTALL)
TIMESTAMP_SECONDS_REGEX = re.compile(r":\d{2}(\.\d+)?([-+]\d{2}:\d{2})?$")
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)

# Auto doublespacing
DOUBLESPACE_IF_LINE_LEN_OVER = 130
DOUBLESPACE_IF_LONG_LINE_PCT = 0.5
DOUBLESPACE_LIST_MIN_LEN = 100
DOUBLESPACE_LIST_MAX_LEN = 1_900
DOUBLESPACE_PARAGRAPH_MIN_AVG_LEN = 80

LIST_REGEX_FLAGS = re.DOTALL | re.IGNORECASE | re.MULTILINE
LIST_ELEMENT_TEXT_PATTERN = fr".{{{DOUBLESPACE_LIST_MIN_LEN},{DOUBLESPACE_LIST_MAX_LEN}}}?"

def list_item_regex(pattern: str, flags: re.RegexFlag = LIST_REGEX_FLAGS) -> re.Pattern:
    return re.compile(fr"^({pattern} +{LIST_ELEMENT_TEXT_PATTERN})(?=\n{pattern}\s|\Z)", flags)

BULLETED_ITEM_REGEX = list_item_regex('•')
LIST_ITEM_REGEX = list_item_regex(r"\(?([a-z]{1,2}|\d+)[.)]")
ORDINAL_PATTERN = '|'.join([o.upper() for o in 'first second third fourth fifth sixth seventh eighth ninth tenth'.split()])
ORDINAL_LIST_REGEX = list_item_regex(ORDINAL_PATTERN, re.DOTALL | re.MULTILINE)
SECTION_LIST_REGEX = re.compile(r"(\nSection \d+)")  # doesn't match already doublespaced

capitalize_first = lambda s: s[0].upper() + s[1:]
capture_group_marker = lambda label: fr"?P<{label}>"
collapse_newlines = lambda text: MULTINEWLINE_REGEX.sub('\n\n', text)
collapse_spaces = lambda s: MULTISPACE_REGEX.sub(' ', s)
collapse_whitespace = lambda s: WHITESPACE_REGEX.sub(' ', s).strip()
constantize = lambda s: underscore(s.upper())
contains_list = lambda s: bool(LIST_ITEM_REGEX.search(s) or BULLETED_ITEM_REGEX.search(s))
is_bool_prop = lambda prop: prop.startswith('is_')
is_integer = lambda s: isinstance(s, int) or bool(INTEGER_REGEX.match(s))
join_patterns = lambda patterns: '|'.join(patterns)
iso_date = lambda dt: dt.isoformat()[0:10]
iso_timestamp = lambda dt: dt.isoformat().replace('T', ' ')
or_equal_sign_char_group = lambda s: f"[{s}=]"  # DataSet 11 has a lot of random '=' replacing characters
strip_pdfalyzer_panels = lambda s: PDFALYZER_IMAGE_PANEL_REGEX.sub('', s)
timestamp_str = lambda dt: dt.isoformat()[0:19]
timestamp_human = lambda dt: timestamp_str(dt).replace('T', ' ')


def as_pattern(s: str) -> str:
    """Replace spaces with regex pattern for whitespace and ampersands with common OCR fails."""
    s = collapse_spaces(s).replace('@', AMPERSAND_CHAR_GROUP)
    return s if '?<!' in s else s.replace(' ', WHITESPACE_CHAR)


def doublespace_lines(s: str) -> str:
    """Doublespace \n chars if s has a high pct of long lines, doublespace numbered lists."""
    return collapse_newlines(doublespace_lists(doublespace_paragraphs(s)))


def doublespace_lists(s: str) -> str:
    """Doublespace things that look like bulleted/numbered/lettered lists in the text."""
    for regex in [BULLETED_ITEM_REGEX, LIST_ITEM_REGEX, ORDINAL_LIST_REGEX]:
        s = regex.sub(r"\n\1", s)

    return SECTION_LIST_REGEX.sub(r"\n\n\1", s)  # Triple space 'Section 1.'


def doublespace_paragraphs(s: str):
    """Heuristic to find paragraph endpoints and create extra line breaks after them."""
    lines = s.split('\n')
    line_lengths = [len(line) for line in lines]
    avg_line_length = int(sum(line_lengths) / len(lines))

    if avg_line_length < DOUBLESPACE_PARAGRAPH_MIN_AVG_LEN:
        return s

    logger.info(f"{len(lines)} lines with average length {avg_line_length}\nlengths: {sorted(line_lengths)}")
    new_lines = []

    for i, line in enumerate(lines):
        new_lines.append(line)

        if i < (len(lines) - 1) and len(line) < avg_line_length and line.endswith('.'):
            msg = f"short line with period ({len(line)} chars) vs. average in doc of {avg_line_length}"

            if len(lines[i + 1]) > avg_line_length:
                logger.debug(f"{msg}, inserting line break!")
                new_lines.append('')
            else:
                logger.debug(f"skipping {msg}...")

    if (new_text := '\n'.join(new_lines)) != s:
        logger.info(text_block(new_text[:10_000], 'doublespaced paragraphs'))

    return new_text


def extract_emojis(s: str) -> list[str]:
    return [m.group(1) for m in EMOJI_REGEX.finditer(s)]


def has_line_starting_with(s: str | list[str], pfxes: str | list[str], limit: int | None = None) -> bool:
    lines = s.split('\n') if isinstance(s, str) else s
    lines = lines[0:(limit or len(lines))]

    for line in lines:
        if any(line.startswith(pfx) for pfx in list(pfxes)):
            return True

    return False


def indented(text: str | list[str], spaces: int = 4, prefix: str = '') -> str:
    line_prefix = (' ' * spaces) + prefix
    lines = text.split('\n') if isinstance(text, str) else text
    return line_prefix + f"\n{line_prefix}".join(lines)


def join_truthy(prefix: str | None, suffix: str | None, sep: str = '') -> str:
    """Join two strings but only if they are not empty."""
    sep = sep or (' ' if prefix and suffix else '')
    parts = [p.strip() for p in [prefix, suffix] if p and p.strip()]
    return sep.join(parts)


def prop_str(prop: Any) -> Any:
    return quote(str(prop)) if isinstance(prop, (datetime, str)) else str(prop)


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


def snip_msg(msg: str) -> str:
    return f'<...{msg}...>'


def starred_header(msg: str, num_stars: int = 7, num_spaces: int = 2) -> str:
    """String like '  *** Title Msg ***  '."""
    stars = '*' * num_stars
    spaces = ' ' * num_spaces
    return f"{spaces}{stars} {msg} {stars}{spaces}"


def timestamp_without_seconds(dt: datetime) -> str:
    return TIMESTAMP_SECONDS_REGEX.sub('', str(dt))


def timestamp_without_zero_hour(dt: datetime) -> str:
    """Remove the time part of a datetime string if it's 00:00:00, otherwise keep it."""
    return dt.strftime(r'%Y-%m-%d %H:%M:%S').removesuffix(' 00:00:00')
