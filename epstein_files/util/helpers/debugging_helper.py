from rich.text import Text

from epstein_files.documents.other_file import OtherFile
from epstein_files.util.helpers.string_helper import quote
from epstein_files.output.rich import console, styled_key_value


def _show_timestamps(epstein_files):
    for doc in epstein_files.doj_files:
        doc.warn(f"timestamp: {doc.timestamp}")


def _verify_filenames(epstein_files):
    doc_filenames = set([doc.file_path.name for doc in epstein_files.all_documents])

    for file_path in epstein_files.all_files:
        if file_path.name not in doc_filenames:
            print(f"'{file_path}' is not in list of {len(doc_filenames)} Document obj filenames!")



def print_interesting_doc_panels_and_props(epstein_files):
    for doc in epstein_files.all_documents:
        txt = Text(f"interesting? {doc.is_interesting}, ").append(doc.summary)

        if isinstance(doc, OtherFile) and doc.is_interesting:
            console.print(txt)
            console.print(doc.summary_panel)
        elif doc.config and doc.config.has_any_info:
            console.print(txt)
            console.print(doc.summary_panel)
        else:
            continue

        if doc.config:
            console.print(styled_key_value('      complete_description', quote(doc.config.complete_description)))

        console.line()
