
def escape_double_quotes(text: str) -> str:
    return text.replace('"', r'\"')


def escape_single_quotes(text: str) -> str:
    return text.replace("'", r"\'")
