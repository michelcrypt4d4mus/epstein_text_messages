from collections import defaultdict

from rich.padding import Padding
from rich.text import Text

from epstein_files.documents.emails.constants import FALLBACK_TIMESTAMP
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger


def highlight_config_dict() -> dict:
    from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES

    return {
        hn.label: {
            'patterns': hn.patterns,
            'regex.pattern': hn.regex.pattern,
        }
        for hn in HIGHLIGHTED_NAMES
    }


def print_all_timestamps(epstein_files):
    from epstein_files.output.rich import console
    fallbacks = valid = 0

    for i, doc in enumerate(epstein_files.unique_documents):
        console.print(doc.summary)

        if doc.timestamp == FALLBACK_TIMESTAMP:
            fallbacks += 1
        elif doc.timestamp:
            valid += 1

    no_timestamp = len(epstein_files.unique_documents) - valid - fallbacks
    console.print(f"\nFound {i + 1} documents (no_timestamp={no_timestamp}, valid={valid}, fallback={fallbacks})\n")


def print_highlight_patterns() -> None:
    from epstein_files.output.rich import print_json
    print_json('patterns', highlight_config_dict())
    import sys
    sys.exit()


def print_file_counts(epstein_files) -> None:
    from epstein_files.output.rich import console, styled_dict
    counts = defaultdict(int)

    for i, doc in enumerate(epstein_files.unique_documents):
        counts[doc._class_name] += 1

    counts['total'] = i + 1
    console.print(styled_dict(counts))


def _verify_filenames(epstein_files):
    doc_filenames = set([doc.file_path.name for doc in epstein_files.documents])

    for file_path in epstein_files.file_paths:
        if file_path.name not in doc_filenames:
            print(f"'{file_path}' is not in list of {len(doc_filenames)} Document obj filenames!")


def print_interesting_doc_panels_and_props(epstein_files, sort_by_category: bool = True):
    """Only prints OtherFile objects."""
    from epstein_files.documents.other_file import OtherFile
    from epstein_files.output.rich import console, indent_txt, styled_dict
    num_printed = 0
    num_interesting = 0

    if sort_by_category:
        docs = sorted(epstein_files.documents, key=lambda d: [d.category, d.timestamp or FALLBACK_TIMESTAMP])
    else:
        docs = epstein_files.documents

    for doc in docs:
        if not isinstance(doc, OtherFile):
            continue
        elif doc.is_interesting is None and doc.config is None:
            continue

        if doc.config:
            props = doc.config.truthy_props
            props.pop('id')

            if doc.is_interesting != doc.config.is_of_interest:
                logger.warning(f"mismatch of config.is_of_interest and doc.is_interesting")
                props['doc.is_interesting'] = doc.is_interesting
        else:
            props = {'doc.is_interesting': doc.is_interesting}

        # console.print(doc.summary_panel)
        console.print(doc.file_info_panel())
        from epstein_files.util.env import args

        if args.debug:
            props_table = styled_dict(props, sep=': ')
            props_table = Padding(indent_txt(props_table, 12), (0, 0, 1, 0))
            console.print(props_table)

        num_printed += 1
        num_interesting += int(doc.is_interesting or False)
        # console.line()

    print('')
    logger.warning(f"Printed {num_printed} object configs, {num_interesting} interesting ones.\n\n")
