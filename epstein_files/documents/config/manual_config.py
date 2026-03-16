"""
Methods to help with manually adjusting `DocCfg` objects at new file import time.
"""
import sys
from pathlib import Path
from typing import Mapping, Sequence, Type, cast

from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.email import Email
from epstein_files.output.rich import console, print_subtitle_panel
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.helpers.string_helper import indented, is_bool_prop
from epstein_files.util.logging import logger

ALL = 'a'
QUESTION = Text("OK to save these new docs? (", 'honeydew2').append(f"list of IDs to manually config, '{ALL}' for all", 'yellow1').append(')')
MAGIC_COMMENT = '#### MAGIC COMMENT FOR MANUAL CONFIG ####'
CONSTANTS_PY_PATH = Path(__file__).parent.parent.parent.joinpath('util', 'constants.py')

DOC_PROPS = [
    'author',
]

EMAIL_PROPS = [
    'recipients',
]

CFG_PROPS = [
    'description',
    'is_interesting',
    'truncate_to',
]


def create_configs(docs: Sequence[Document]) -> Sequence[DocCfg]:
    """Manually review and create `DocCfg` objects for new files."""
    console.print(*Document.sort_by_timestamp(docs))
    cfgs = []
    what_to_do = Prompt.ask(QUESTION.append(f" [y/n/{ALL}/IDs]", style='magenta'))

    if (what_to_do or 'n') == 'n':
        logger.warning(f"Exiting...")
        sys.exit()
    elif what_to_do == 'y':
        return []
    elif what_to_do == ALL:
        pass
    else:
        docs = [d for d in docs if d.file_id in what_to_do.split()]
        console.print(f"Manually configuring {len(docs)} documents...", style='dim')

    for doc in docs:
        if doc.config:  #all(getattr(doc, f) for f in fields) and all(getattr(cfg, f) for f in CFG_FIELDS):
            doc._warn(f"already has a config, skipping!")
            continue

        console.line()
        print_subtitle_panel('whole file', center=False)
        doc.print_untruncated()

        if isinstance(doc, Email):
            cfg = EmailCfg(id=doc.file_id)
            doc_props = DOC_PROPS + EMAIL_PROPS

            if (char_range := doc.char_range_to_display):
                console.line()
                print_subtitle_panel(f'truncated view (char_range={char_range}, length={doc.length})', center=False)
                console.print(doc)
        else:
            cfg = DocCfg(id=doc.file_id)
            doc_props = DOC_PROPS

        console.print(doc._debug_dict(True), '\n')
        logger.warning(f"Updating doc_props: {doc_props}")

        if what_to_do == ALL and len(docs) > 1 and not Confirm.ask(f"Add config for this file?"):
            continue

        for prop in doc_props:
            if not (doc_val := getattr(doc, prop)):
                _ask_for_value(cfg, prop, doc, doc_val)

                if prop == 'author':
                    _ask_for_value(cfg, 'author_reason', doc, doc_val)

                    if not cfg.author_reason:
                        _ask_for_value(cfg, 'author_uncertain', doc, doc_val)
                elif prop == 'recipients':
                    _ask_for_value(cfg, 'recipient_uncertain', doc, doc_val)

        for prop in CFG_PROPS:
            if not (doc_val := getattr(cfg, prop)):
                _ask_for_value(cfg, prop, doc, doc_val)

        cfgs.append(cfg)

    _insert_configs(cfgs)
    return cfgs


def _ask_for_value(cfg: DocCfg, prop: str, doc: Document, doc_val: list[str] | str) -> None:
    """Ask for a value for `prop`. If provided use `setattr` to set it on to the `cfg`."""
    question = Text('').append(prop, style='cyan').append('?')
    is_list_prop = isinstance(doc_val, list)
    is_truncate_prop = prop == 'truncate_to'

    if is_list_prop:
        question.append(' (semicolon separated)', style='dim')
    elif is_bool_prop(prop):
        question.append(' [y/n/None]', style='magenta')

    if is_bool_prop(prop):
        value = _ask_for_optional_bool(question)
    else:
        value = Prompt.ask(question).strip()

        if not value:
            return
        elif isinstance(doc_val, list):
            value = [name.strip() for name in value.split(';')]
        elif is_truncate_prop:
            value = int(value)
        elif value == 'True':
            value = True

    setattr(cfg, prop, value)

    # Keep asking until a good value is found
    if is_truncate_prop:
        CONFIGS_BY_ID[doc.file_id] = cfg
        console.print(doc)

        if not Confirm.ask("looks good?"):
            doc.print_untruncated()
            return _ask_for_value(cfg, prop, doc, doc_val)


def _ask_for_optional_bool(question: Text) -> bool | None:
    value = Prompt.ask(question).strip()

    if not value:
        return None
    elif value.lower() in ['t', 'y']:
        return True
    elif value.lower() in ['f', 'n']:
        return False
    else:
        logger.warning(f"'{value}' is not a valid boolean value.")
        return _ask_for_optional_bool(question)


def _insert_configs(cfgs: list[DocCfg]) -> None:
    """Write the configs into the constants.py file."""
    if not cfgs:
        logger.warning(f"No new configs to write...")
        return

    before, after = CONSTANTS_PY_PATH.read_text().split(MAGIC_COMMENT)
    print('\n\n\n')

    with open(CONSTANTS_PY_PATH, 'wt') as f:
        f.writelines([
            before,
            MAGIC_COMMENT + '\n',
            *[repr(cfg) + ',\n' for cfg in cfgs],
            after
        ])

    for cfg in [c for c in cfgs if not c.is_empty]:
        print(f"    {repr(cfg)},")

    logger.warning(f"Wrote {len(cfgs)} new DocCfg objects to '{CONSTANTS_PY_PATH}'")
