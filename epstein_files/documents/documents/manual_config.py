import sys
from pathlib import Path
from typing import Mapping, Sequence, Type, cast

from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.documents.documents.doc_cfg import DocCfg, EmailCfg
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.output.rich import console, print_subtitle_panel
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.helpers.string_helper import indented
from epstein_files.util.logging import logger

ALL = 'a'
QUESTION = Text("OK to continue? (", 'honeydew2').append(f"list of IDs to manually config, '{ALL}' for all", 'yellow1').append(')')
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
    console.print(*docs)
    cfgs = []
    what_to_do = Prompt.ask(QUESTION.append(f" [y/n/c/IDs]", style='magenta'))

    if what_to_do == 'n':
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
            doc.warn(f"already has a config...")
            continue

        console.line()
        print_subtitle_panel('whole file', center=False)
        doc.print(whole_file=True)

        if isinstance(doc, Email):
            cfg = EmailCfg(id=doc.file_id)
            doc_props = DOC_PROPS + EMAIL_PROPS

            if (num_chars := doc._truncate_to_length()) < len(doc.text):
                console.line()
                print_subtitle_panel(f'truncated view (num_chars={num_chars}, length={doc.length})', center=False)
                doc.print()
        else:
            cfg = DocCfg(id=doc.file_id)
            doc_props = DOC_PROPS

        console.print(doc._debug_dict(True), '\n')

        if what_to_do == ALL and not Confirm.ask(f"Add config for this file?"):
            continue

        for prop in doc_props:
            doc_val = getattr(doc, prop)

            if not doc_val or isinstance(doc_val, list):
                _ask_for_value(cfg, prop, doc, doc_val)

        for prop in CFG_PROPS:
            if not getattr(cfg, prop):
                _ask_for_value(cfg, prop, doc, doc_val)

        cfgs.append(cfg)

    _insert_configs(cfgs)
    return cfgs


def _ask_for_value(cfg: DocCfg, prop: str, doc: Document, doc_val: list[str] | str) -> None:
    if prop.startswith('is_'):
        value = _ask_for_optional_bool(prop)
    else:
        value = Prompt.ask(f"{prop}?")

        if not value:
            return None
        elif isinstance(doc_val, list):
            value = [value]
        elif prop == 'truncate_to':
            value = int(value)

    setattr(cfg, prop, value)

    if prop == 'truncate_to':
        CONFIGS_BY_ID[doc.file_id] = cfg
        doc.print()

        if not Confirm.ask("looks good?"):
            doc.print(whole_file=True)
            _ask_for_value(cfg, prop, doc, doc_val)


def _ask_for_optional_bool(prop: str) -> bool | None:
    value = Prompt.ask(Text(f"{prop}? ").append('[y/n/None]', style='magenta')).strip()

    if not value:
        return None
    elif value.lower() in ['t', 'y']:
        return True
    elif value.lower() in ['f', 'n']:
        return False
    else:
        logger.warning(f"'{value}' is not a valid response.")
        return _ask_for_optional_bool(prop)


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
            *[repr(cfg) + ',' for cfg in cfgs],
            after
        ])

    for cfg in [c for c in cfgs if not c.is_empty]:
        print(f"    {repr(cfg)},")

    logger.warning(f"Wrote {len(cfgs)} new DocCfg objects to '{CONSTANTS_PY_PATH}'")
