"""Help with strings."""
import re

from epstein_files.util.constant.strings import QUESTION_MARKS_REGEX


def has_line_starting_with(s: str | list[str], pfxes: str | list[str], limit: int | None = None) -> bool:
    lines = s.split('\n') if isinstance(s, str) else s
    lines = lines[0:(limit or len(lines))]

    for line in lines:
        if any(line.startswith(pfx) for pfx in list(pfxes)):
            return True

    return False


def indented(s: str, spaces: int = 4, prefix: str = '') -> str:
    indent = ' ' * spaces
    indent += prefix
    return indent + f"\n{indent}".join(s.split('\n'))


def join_truthy(prefix: str | None, suffix: str | None, sep: str = '') -> str:
    sep = sep or (' ' if prefix and suffix else '')
    parts = [p.strip() for p in [prefix, suffix] if p and p.strip()]
    return sep.join(parts)


def quote(s: str, try_single_quote_first: bool = False) -> str:
    if try_single_quote_first:
        return f"'{s}'" if "'" not in s else f'"{s}"'
    else:
        return f"'{s}'" if '"' in s else f'"{s}"'


def remove_question_marks(name: str):
    return QUESTION_MARKS_REGEX.sub('', name).strip()
