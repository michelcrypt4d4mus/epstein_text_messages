from typing import Mapping, Sequence, Type, cast

from rich.prompt import Confirm, Prompt
from rich.table import Table
from yaralyzer.util.helpers.interaction_helper import ask_to_proceed

from epstein_files.documents.document import Document
from epstein_files.documents.documents.doc_cfg import DocCfg, EmailCfg
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.output.rich import console, print_subtitle_panel
from epstein_files.util.constants import CONFIGS_BY_ID

FIELDS = [
    'author',
]

EMAIL_FIELDS = [
    'recipients',
]

CFG_FIELDS = [
    'description',
    'is_interesting',
    'truncate_to',
]


def create_configs(docs: Sequence[Document]) -> Sequence[DocCfg]:
    """Manually review and create DocCfg objects for new files."""
    cfgs = []

    for doc in docs:
        doc.print()

    if not Confirm.ask(f"\nManually configure {len(docs)} documents?"):
        return []

    for doc in docs:
        if doc.config:  #all(getattr(doc, f) for f in fields) and all(getattr(cfg, f) for f in CFG_FIELDS):
            doc.warn(f"already has a config...")
            continue

        console.line()
        print_subtitle_panel('whole file', center=False)
        doc.print(whole_file=True)

        if isinstance(doc, Email):
            cfg = EmailCfg(id=doc.file_id)
            fields = FIELDS + EMAIL_FIELDS

            if (num_chars := doc._truncate_to_length()) < len(doc.text):
                console.line()
                print_subtitle_panel(f'truncated view (num_chars={num_chars}, length={doc.length})', center=False)
                doc.print()
        else:
            cfg = DocCfg(id=doc.file_id)
            fields = FIELDS

        console.print(doc._debug_dict(True), '\n')

        if not Confirm.ask(f"Add config for this file?"):
            continue

        for f in fields:
            if not getattr(doc, f):
                _ask_for_value(cfg, f, doc)

        for f in CFG_FIELDS:
            if not getattr(cfg, f):
                _ask_for_value(cfg, f, doc)

        cfgs.append(cfg)

    print('\n\n\n')

    for cfg in [c for c in cfgs if not c.is_empty]:
        print(f"    {repr(cfg)},")

    return cfgs


def _ask_for_value(cfg: DocCfg, prop: str, doc: Document) -> None:
    if prop.startswith('is_'):
        value = Confirm.ask(f"{prop}?")
    else:
        value = Prompt.ask(f"{prop}?")

    if not value:
        return
    elif prop == 'truncate_to':
        value = int(value)

    setattr(cfg, prop, value)

    if prop == 'truncate_to':
        CONFIGS_BY_ID[doc.file_id] = cfg
        doc.print()

        if not Confirm.ask("looks good?"):
            doc.print(whole_file=True)
            _ask_for_value(cfg, prop, doc)
