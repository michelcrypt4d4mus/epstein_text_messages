from dataclasses import dataclass, field
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import get_style_for_name
from epstein_files.output.html.builder import buffer_as_html, rich_to_html, table_to_html, write_templated_html
from epstein_files.output.html.elements import div_class
from epstein_files.output.rich import console
from epstein_files.output.title_page import print_color_key, print_other_page_link, print_section_header
from epstein_files.people.person import PEOPLE_BIOS, Person
from epstein_files.util.constant.names import *
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import dict_sets_to_lists, uniq_sorted
from epstein_files.util.logging import logger, exit_with_error

OTHER_FILES_TABLE_MSG = Text("(non emails will appear in tables)", 'gray27 italic')


@dataclass
class DocPrinter:
    """Handles printing collections of documents with biographical info panels interspersed."""
    html_elements: list[str] = field(default_factory=list)
    other_files_queue: list[OtherFile] = field(default_factory=list)
    people_encountered: set[str] = field(default_factory=set)
    printed_docs: list[Document] = field(default_factory=list)

    def new_names(self, document: Document) -> list[str]:
        return [p for p in document.people if p not in self.people_encountered]

    def print_characters_panel(self, names: list[str], is_sticky: bool) -> str:
        if (bio_panel := self._biographical_panel(uniq_sorted(names))):
            console.print(self._align_biographical_panel(bio_panel))
            self.people_encountered.update(names)
            class_name = ('sticky_' if is_sticky else '') + 'person_bio_panel'
            return div_class(rich_to_html(bio_panel, minimize_width=True), class_name)
        else:
            return ''

    def print_documents(self, docs: Sequence[Document]) -> None:
        if len(self.html_elements) == 0:
            self.html_elements.append(self._html_so_far())

        for doc in docs:
            should_print = doc.is_interesting if not args.invert_chrono else not doc.is_interesting

            if not should_print:
                continue
            elif isinstance(doc, OtherFile) and doc.is_valid_for_table:
                if self.new_names(doc):
                    if self.other_files_queue:
                        self._print_other_files_queue()  # Clear the queue before bios panel

                    if (bio_div := self.print_characters_panel(self.new_names(doc), False)):
                        self.html_elements.append(bio_div)

                self.other_files_queue.append(doc)
                continue
            elif self.other_files_queue:
                self._print_other_files_queue()

            doc.print()
            doc_div = '\n'.join([self.print_characters_panel(self.new_names(doc), True), doc.to_html()])
            self.html_elements.append(div_class(doc_div, 'bio_email_container'))
            self.printed_docs.append(doc)

    def write_html(self, html_path: Path) -> None:
        """Write the collection of html elements to a file."""
        write_templated_html(self.html_elements, html_path)

    def _print_other_files_queue(self) -> None:
        has_printed_any_other_file_objs = any(isinstance(d, OtherFile) for d in self.printed_docs)

        if has_printed_any_other_file_objs:
            table_title = None
        else:
            table_title = OTHER_FILES_TABLE_MSG
            console.line()
            self.html_elements.append('<div style="height: 1em"></div>')

        table = OtherFile.files_preview_table(
            self.other_files_queue,
            title=table_title,
            title_justify='center',
        )

        console.print(Padding(table, (0, 0, 1, site_config.other_files_table_indent)))
        self.html_elements.append(table_to_html(table))  # TODO: missing indent
        self.printed_docs.extend(self.other_files_queue)
        self.other_files_queue = []

    def _align_biographical_panel(self, panel: Panel) -> Align | None:
        return Align(Padding(panel, site_config.character_bio_padding), 'right')

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
        return buffer_as_html(console, False)
