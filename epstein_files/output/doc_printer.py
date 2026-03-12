from dataclasses import dataclass, field
from pathlib import Path

from rich import box
from rich.align import Align, AlignMethod
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.layout_elements.file_display import BasePanel, FileDisplay
from epstein_files.output.html.builder import (console_buffer_to_html, panel_to_div, rich_to_html, table_to_html,
     text_to_div, unwrap_rich, write_templated_html)
from epstein_files.output.html.elements import div_class, tag, to_em
from epstein_files.output.rich import console, subtitle_panel
from epstein_files.people.person import PEOPLE_BIOS, Person
from epstein_files.people.names import *
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import uniq_sorted
from epstein_files.util.logging import logger
from epstein_files.util.timer import Timer

OTHER_FILES_TABLE_MSG = Text("(non emails will appear in tables)", 'gray27 italic')
EMPTY_LINE_HEIGHT = to_em(1.5)
EMPTY_LINE_DIV = f'<div style="height: {EMPTY_LINE_HEIGHT}"></div>'


@dataclass
class DocPrinter:
    """Handles printing collections of documents with biographical info panels interspersed."""
    collect_other_files_to_tables: bool = True
    html_elements: list[str] = field(default_factory=list)
    other_files_queue: list[OtherFile] = field(default_factory=list)
    last_bio_panel = ''
    people_encountered: set[str] = field(default_factory=set)
    printed_docs: list[Document] = field(default_factory=list)
    printed_file_displays: list[FileDisplay] = field(default_factory=list)
    suppressed_docs_queue: list[Document] = field(default_factory=list)

    def __post_init__(self):
        self.html_elements.append(self._html_so_far())  # Grab whatever's in the console buffer (usually title page)

    @property
    def printed_emails(self) -> list[Email]:
        emails = [e for e in self.printed_docs if isinstance(e, Email)]

        if len(emails) != len(self.printed_docs):
            logger.warning(f"DocPrinted.printed_emails returning {len(emails)} of {len(self.printed_docs)} printed docs...")

        return emails

    def line(self, num: int = 1) -> None:
        """Print blank lines to HTML and terminal, similar to `console.line()`."""
        for _i in range(0, num):
            console.line()
            self.html_elements.append(EMPTY_LINE_DIV)

    def new_names(self, document: Document) -> list[str]:
        return [p for p in document.people if p in PEOPLE_BIOS and p not in self.people_encountered]

    def print_characters_panel(self, names: list[str], is_sticky: bool = True) -> None:
        if (bio_panel := self._biographical_panel(uniq_sorted(names))):
            if self.last_bio_panel:
                raise RuntimeError(f"last_bio_panel should be empty, instead it's:\n{self.last_bio_panel}")

            console.print(self._align_biographical_panel(bio_panel))
            self.people_encountered.update(names)
            class_name = ('sticky_' if is_sticky else '') + 'person_bio_panel'
            self.last_bio_panel = div_class(rich_to_html(bio_panel, minimize_width=True), class_name)

    def print_documents(self, docs: Sequence[Document | FileDisplay]) -> None:
        if len(docs) > 500:
            logger.warning(f"{type(self).__name__}.print_documents() called with {len(docs):,} Documents...")

        timer = Timer()
        i = 0

        for i, doc in enumerate(docs, 1):
            logger.info(f"Printing {doc}")

            if isinstance(doc, Document) and doc.suppressed_txt:
                self.suppressed_docs_queue.append(doc)
                continue
            elif self.suppressed_docs_queue:
                self._print_suppression_msgs_queue()

            if isinstance(doc, OtherFile) and doc.is_valid_for_table and self.collect_other_files_to_tables:
                if self.new_names(doc):
                    if self.other_files_queue:
                        self._print_other_files_queue()  # Clear the queue before new biographical panel

                    self.print_characters_panel(self.new_names(doc))

                self.other_files_queue.append(doc)
                continue
            elif self.other_files_queue:
                self._print_other_files_queue()

            if isinstance(doc, Document):
                self.print_characters_panel(self.new_names(doc))
                doc.print()
                self._append_html_element(doc.to_html())
                self.printed_docs.append(doc)
            else:
                # TODO: this sucks
                console.print(doc)
                self.html_elements.append(doc.to_html())
                self.printed_file_displays.append(doc)

            if i % 100 == 0:
                timer.print_at_checkpoint(f"Printed {i} documents")

        # Make sure to print any documents left in the queues
        if self.suppressed_docs_queue:
            self._print_suppression_msgs_queue()

        if self.other_files_queue:
            self._print_other_files_queue()

    def print_renderable(
        self,
        _renderable: Align | Padding | Panel | Text | str,
        align: AlignMethod | None = None
    ) -> None:
        _renderable = Align(_renderable, align) if align and not isinstance(_renderable, Align) else _renderable
        console.print(_renderable)
        renderable, css_props = unwrap_rich(_renderable)

        if isinstance(renderable, Panel):
            self.html_elements.append(panel_to_div(renderable, css_props))
        elif isinstance(renderable, Table):
            self.html_elements.append(table_to_html(renderable, css_props))
            console.line(2)  # TODO: table_to_html() adds a bottom marking of 1.9em; should be unified somehow
        elif isinstance(renderable, Text):
            self.html_elements.append(text_to_div(renderable, css_props))
        elif isinstance(renderable, str):
            self.html_elements.append(tag('p', renderable, css_props))
        else:
            raise TypeError(f"renderable of unsupported type: {type(renderable).__name__}: {renderable}")

    def print_subtitle_panel(self, subtitle: str) -> None:
        self.print_renderable(subtitle_panel(subtitle))
        self.line()

    def write_html(self, html_path: Path) -> None:
        """Write the collection of html elements to a file."""
        write_templated_html(self.html_elements, html_path)

    def _align_biographical_panel(self, panel: Panel) -> Align | None:
        return Align(Padding(panel, site_config.character_bio_padding), 'right')

    def _append_html_element(self, element: str) -> None:
        if self.last_bio_panel:
            element = '\n'.join([self.last_bio_panel, element])
            self.last_bio_panel = ''

        self.html_elements.append(div_class(element, 'doc_container'))

    def _biographical_panel(self, names: list[str]) -> Panel | None:
        """Panel showing biographical info for a list of names."""
        bios = [
            Text('', justify='right').append(PEOPLE_BIOS[name])
            for name in names if PEOPLE_BIOS.get(name)
        ]

        if not bios:
            return None

        return Panel(
            Group(*bios),
            border_style='dim',
            box=box.DOUBLE,
            expand=False,
            # padding=(0, 2),
            style='on gray7',
            title=Text(f"new names in next file", 'grey85 italic'),
            title_align='right',
        )

    def _html_so_far(self) -> str:
        return console_buffer_to_html(console, False)

    def _print_other_files_queue(self) -> None:
        has_printed_any_other_file_objs = any(isinstance(d, OtherFile) for d in self.printed_docs)

        if has_printed_any_other_file_objs:
            table_title = None
        else:
            table_title = OTHER_FILES_TABLE_MSG
            self.line()

        table = OtherFile.files_preview_table(
            self.other_files_queue,
            title=table_title,
            title_justify='center',
        )

        console.print(Padding(table, (0, 0, 1, site_config.other_files_table_indent)))
        table_html = table_to_html(table, {'margin-left': to_em(site_config.other_files_table_indent)})
        self._append_html_element(table_html)
        self.printed_docs.extend(self.other_files_queue)
        self.other_files_queue = []

    def _print_suppression_msgs_queue(self) -> None:
        """Print any suppression messages."""
        for doc in self.suppressed_docs_queue:
            doc.print()

        msgs_panel = BasePanel(border_style='', text=[d.suppressed_txt for d in self.suppressed_docs_queue])
        self.html_elements.append(msgs_panel.to_div((site_config.info_indent, 0)))
        self.suppressed_docs_queue = []
        console.line()
