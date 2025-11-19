def load_file(file_path):
    """Remove BOM and remove HOUSE OVERSIGHT lines."""
    with open(file_path) as f:
        file_text = f.read()
        file_text = file_text[1:] if (len(file_text) > 0 and file_text[0] == '\ufeff') else file_text  # remove BOM
        file_lines = [l.strip() for l in file_text.split('\n') if not l.startswith('HOUSE OVERSIGHT')]
        return '\n'.join(file_lines)
