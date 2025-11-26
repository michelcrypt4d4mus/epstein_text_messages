escape_double_quotes = lambda text: text.replace('"', r'\"')
escape_single_quotes = lambda text: text.replace("'", r"\'")
regex_escape_periods = lambda text: text.replace('.', r'\.?')
