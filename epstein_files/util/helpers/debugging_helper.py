from rich.text import Text

from epstein_files.documents.other_file import OtherFile
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger
from epstein_files.output.rich import bool_txt, console, styled_key_value, styled_dict


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
        if isinstance(doc, OtherFile) and doc.is_interesting:
            pass
        elif doc.config and doc.config.has_any_info:
            pass
        else:
            continue

        props = {}

        if doc.config:
            props.update(doc.config.important_props)

            if doc.config.is_of_interest != doc.is_interesting:
                logger.warning(f"mismatch of config.is_of_interest and doc.is_interesting")
                props['doc.is_interesting'] = doc.is_interesting
        else:
            props['doc.is_interesting'] = doc.is_interesting

        console.print(doc.summary_panel)
        console.print(styled_dict(props, sep=': '))
        console.line()
