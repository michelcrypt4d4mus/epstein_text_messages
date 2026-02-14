def quote(s: str) -> str:
    return f"'{s}'" if '"' in s else f'"{s}"'
