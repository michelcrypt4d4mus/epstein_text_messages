from pathlib import Path
from subprocess import run

from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.output.rich import console
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX
from epstein_files.util.env import DOCS_DIR
from epstein_files.util.helpers.file_helper import extract_file_id


def diff_files(files: list[str]) -> None:
    """Diff the contents of two `Document` objects after all cleanup, BOM removal, etc."""
    if len(files) != 2:
        raise RuntimeError('Need 2 files')
    elif files[0] == files[1]:
        raise RuntimeError(f"Filenames are the same!")

    files = [f"{HOUSE_OVERSIGHT_PREFIX}{f}" if len(f) == 6 else f for f in files]
    files = [f if f.endswith('.txt') else f"{f}.txt" for f in files]
    tmpfiles = [Path(f"tmp_{f}") for f in files]
    docs = [Document(DOCS_DIR.joinpath(f)) for f in files]

    for i, doc in enumerate(docs):
        doc._write_clean_text(tmpfiles[i])

    cmd = f"diff {tmpfiles[0]} {tmpfiles[1]}"
    console.print(f"Running '{cmd}'...")
    results = run(cmd, shell=True, capture_output=True, text=True).stdout

    for line in _color_diff_output(results):
        console.print(line, highlight=True)

    console.print(f"Possible suppression with: ")
    console.print(Text('   suppress left: ').append(f"   '{extract_file_id(files[0])}': 'the same as {extract_file_id(files[1])}',", style='cyan'))
    console.print(Text('  suppress right: ').append(f"   '{extract_file_id(files[1])}': 'the same as {extract_file_id(files[0])}',", style='cyan'))

    for f in tmpfiles:
        f.unlink()


def _color_diff_output(diff_result: str) -> list[Text]:
    txts = [Text('diff output:')]
    style = 'dim'

    for line in diff_result.split('\n'):
        if line.startswith('>'):
            style='spring_green4'
        elif line.startswith('<'):
            style='sea_green1'

        txts.append(Text(line, style=style))

    return txts
