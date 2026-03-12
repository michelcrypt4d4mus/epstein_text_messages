from pathlib import Path

from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.output.rich import console
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX
from epstein_files.util.env import DOCS_DIR
from epstein_files.util.helpers.file_helper import diff_files, extract_file_id


def diff_documents(files: list[str]) -> None:
    """Diff the contents of two `Document` objects after all cleanup, BOM removal, etc."""
    if len(files) != 2:
        raise RuntimeError('Need 2 files')
    elif files[0] == files[1]:
        raise RuntimeError(f"Filenames are the same!")

    files = [f"{HOUSE_OVERSIGHT_PREFIX}{f}" if len(f) == 6 else f for f in files]
    files = [f if f.endswith('.txt') else f"{f}.txt" for f in files]
    tmpfiles = [Path(f"tmp_{f}") for f in files]
    docs = [Document(DOCS_DIR.joinpath(f)) for f in files]

    # Write temporary plain text file with all repairs applied.
    for i, doc in enumerate(docs):
        doc._write_clean_text(tmpfiles[i])

    diff_files(tmpfiles[0], tmpfiles[1])
    console.print(f"Possible suppression with: ")
    console.print(Text('   suppress left: ').append(f"   '{extract_file_id(files[0])}': 'the same as {extract_file_id(files[1])}',", style='cyan'))
    console.print(Text('  suppress right: ').append(f"   '{extract_file_id(files[1])}': 'the same as {extract_file_id(files[0])}',", style='cyan'))

    for f in tmpfiles:
        f.unlink()
