"""Help with strings."""
from epstein_files.util.constant.strings import QUESTION_MARKS_REGEX


def indented(s: str, spaces: int = 4, prefix: str = '') -> str:
    indent = ' ' * spaces
    indent += prefix
    return indent + f"\n{indent}".join(s.split('\n'))


def quote(s: str) -> str:
    return f"'{s}'" if '"' in s else f'"{s}"'


def remove_question_marks(name: str):
    return QUESTION_MARKS_REGEX.sub('', name).strip()
