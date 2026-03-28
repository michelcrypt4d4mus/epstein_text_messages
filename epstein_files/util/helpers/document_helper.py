from pathlib import Path

from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.output.rich import console
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX
from epstein_files.util.env import DOCS_DIR
from epstein_files.util.helpers.file_helper import coerce_file_name, diff_files, extract_file_id


def diff_documents(files: list[str]) -> None:
    """Diff the contents of two `Document` objects after all cleanup, BOM removal, etc."""
    if len(files) != 2:
        raise RuntimeError('Need 2 files')
    elif files[0] == files[1]:
        raise RuntimeError(f"Filenames are the same!")

    ids = [extract_file_id(arg.upper().strip().strip('_')) for arg in files]
    docs = [Document.from_file_id(id) for id in ids]

    # Write temporary plain text file with all repairs applied.
    with docs[0]._write_tmp_file() as doc0_tmp_path:
        with docs[1]._write_tmp_file() as doc1_tmp_path:
            diff_files(doc0_tmp_path, doc1_tmp_path)
            console.print(f"Possible suppression with: ")
            console.print(Text('   suppress left: ').append(f"   '{extract_file_id(files[0])}': 'the same as {extract_file_id(files[1])}',", style='cyan'))
            console.print(Text('  suppress right: ').append(f"   '{extract_file_id(files[1])}': 'the same as {extract_file_id(files[0])}',", style='cyan'))
