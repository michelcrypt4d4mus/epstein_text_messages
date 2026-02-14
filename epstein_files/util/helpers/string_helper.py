"""Help with strings."""


def indented(s: str, spaces: int = 4, prefix: str = '') -> str:
    indent = ' ' * spaces
    indent += prefix
    return indent + f"\n{indent}".join(s.split('\n'))


def quote(s: str) -> str:
    return f"'{s}'" if '"' in s else f'"{s}"'
