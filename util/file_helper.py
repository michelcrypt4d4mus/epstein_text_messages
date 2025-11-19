import re
from pathlib import Path

FILE_ID_REGEX = re.compile(r'.*HOUSE_OVERSIGHT_(\d+)\.txt')


def extract_file_id(filename) -> str:
    file_match = FILE_ID_REGEX.match(str(filename))

    if file_match:
        return file_match.group(1)
    else:
        raise RuntimeError(f"Failed to extract file ID from {filename}")


def load_file(file_path):
    """Remove BOM and remove HOUSE OVERSIGHT lines."""
    with open(file_path) as f:
        file_text = f.read()
        file_text = file_text[1:] if (len(file_text) > 0 and file_text[0] == '\ufeff') else file_text  # remove BOM
        file_lines = [l.strip() for l in file_text.split('\n') if not l.startswith('HOUSE OVERSIGHT')]
        return '\n'.join(file_lines)


def move_json_file(file_arg: Path):
    json_subdir_path = file_arg.parent.joinpath('json_files').joinpath(file_arg.name + '.json')
    print(f"'{file_arg}' looks like JSON, moving to '{json_subdir_path}'\n")
    file_arg.rename(json_subdir_path)
