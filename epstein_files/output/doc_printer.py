from dataclasses import dataclass, field
from pathlib import Path

from rich import box
from rich.align import Align, AlignMethod
from rich.console import Group, NewLine, RenderableType
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
from epstein_files.output.html.elements import div_class, tag, to_em, vertical_spacer
from epstein_files.output.rich import console, mobile_console, section_subtitle_panel
from epstein_files.output.site.sites import SiteType
from epstein_files.people.person import PEOPLE_BIOS, Person
from epstein_files.people.names import *
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import listify, uniq_sorted
from epstein_files.util.helpers.rich_helpers import vertically_pad
from epstein_files.util.logging import logger
from epstein_files.util.timer import Timer
from epstein_files.output.title_page import color_key, title_page_top_elements, title_page_bottom_elements
# page_title_elements

OTHER_FILES_TABLE_MSG = Text("(non emails will appear in tables)", 'gray27 italic')
EMPTY_LINE_HEIGHT = to_em(1.5)
EMPTY_LINE_DIV = f'<div style="height: {EMPTY_LINE_HEIGHT}"></div>'
STICKY_BIO_CSS_CLASS = 'sticky_person_bio_panel'

PrintableObj = Document | FileDisplay
PeopleBiosArg = list[str] | PrintableObj


@dataclass(kw_only=True)
class DocPrinter:
    """
    Handles printing collections of documents with biographical info panels interspersed.

    Args:
        epstein_files (EpsteinFiles): the data
        collect_other_files_to_tables (bool, optional): OtherFiles will be collected into small tables if they are sequential
        html_elements (list[str]): HTML for all objects printed so far
        printed_docs (list[Document]): all Documents that have been printed so far
        printed_name_bios (set[str]): all the names for which biographical information has been printed already

    """
    epstein_files: 'EpsteinFiles'
    collect_other_files_to_tables: bool = True
    html_elements: list[str] = field(default_factory=list)
    printed_name_bios: set[str] = field(default_factory=set)
    printed_objs: list[PrintableObj] = field(default_factory=list)
    _last_bio_panel = ''
    _other_files_queue: list[OtherFile] = field(default_factory=list)
    _suppressed_docs_queue: list[Document] = field(default_factory=list)

    def __post_init__(self):
        self.html_elements.append(self._html_so_far())  # Grab whatever's in the console buffer (usually title page)

    @property
    def printed_emails(self) -> list[Email]:
        return [e for e in self.printed_objs if isinstance(e, Email)]

    @property
    def printed_file_displays(self) -> list[FileDisplay]:
        return [e for e in self.printed_objs if isinstance(e, FileDisplay)]

    @property
    def printed_docs(self) -> list[Document]:
        return [e for e in self.printed_objs if isinstance(e, Document)]

    def line(self, num: int = 1) -> None:
        """Print blank lines to HTML and terminal, similar to `console.line()`."""
        self.html_elements.append(vertical_spacer(num))
        console.line(num)

    def new_names(self, names_or_doc: PeopleBiosArg) -> list[str]:
        """List of names found in relation to the documents that have not been encountered before."""
        if isinstance(names_or_doc, FileDisplay):
            return []
        elif isinstance(names_or_doc, Document):
            names = names_or_doc.people
        else:
            names = names_or_doc

        return [n for n in names if n not in self.printed_name_bios]

    def new_names_with_bios(self, names_or_doc: PeopleBiosArg) -> list[str]:
        """Return names that a) were not seen before and b) have configured biographical info."""
        return [n for n in self.new_names(names_or_doc) if PEOPLE_BIOS.get(n)]

    def print_centered(self, _renderables: RenderableType | list[RenderableType]):
        renderables = listify(_renderables)

        if any(isinstance(r, Align) for r in renderables):
            logger.warning(f"wrapping an Align in another Align...")

        self.print_renderable([Align.center(obj) for obj in listify(renderables)])

    def print_color_key(self) -> None:
        self.print_centered(color_key())

    def print_documents(self, docs: Sequence[Document | FileDisplay]) -> None:
        """
        # sequential suppression msgs + OtherFiles collect in queues to be printed
        # when obj of another type shows up OR (for OtherFiles) if there's new names for a biography panel
        """
        suppressed_docs: list[Document] = []
        processed_suppressed_docs_queue = lambda: suppressed_docs.extend(self._print_suppression_msgs_queue())
        timer = Timer()

        if (should_log_in_intervals := (len(docs) > 1000)):
            logger.info(f"{type(self).__name__}.print_documents() called with {len(docs):,} objects...")

        for i, doc in enumerate(docs, 1):
            logger.debug(f"Printing {doc}")

            # Handle sequences of uninteresting or otherwise suppressed docs
            if isinstance(doc, Document) and doc.suppressed_txt:
                self._suppressed_docs_queue.append(doc)
                continue

            processed_suppressed_docs_queue()

            # Collect sequences of otherFile objects into a table
            if isinstance(doc, OtherFile) and doc.is_valid_for_table and self.collect_other_files_to_tables:
                if (new_names := self.new_names_with_bios(doc)):
                    self._cache_biographies_panel(new_names)

                self._other_files_queue.append(doc)
                continue

            self._print_other_files_queue()
            self.print_renderable(doc)

            if should_log_in_intervals and (i % 100 == 0):
                timer.print_at_checkpoint(f"Printed {i:,} objs of {len(docs):,} ({len(suppressed_docs):,} suppressed)")

        processed_suppressed_docs_queue()
        self._print_other_files_queue()
        timer.print_at_checkpoint(f"Finished printing {len(docs):,} objs ({len(suppressed_docs):,} suppressed)")

    def print_renderable(self, renderables: RenderableType | list[RenderableType]) -> None:
        """All things being printed should come through here, which collects both terminal and HTML output as its written."""
        # _renderable = Align(_renderable, align) if align and not isinstance(_renderable, Align) else _renderable
        for renderable in listify(renderables):
            rich_obj, css_props = unwrap_rich(renderable)

            # Add html string for this renderable to self.html_elements
            if isinstance(rich_obj, NewLine):
                self.line()
                continue
            elif isinstance(rich_obj, (Document, FileDisplay)):
                doc_bios_html = self._build_biographies_panel_html(rich_obj.people) if isinstance(rich_obj, Document) else ''
                self._append_element_with_bio_div(rich_obj.to_html(), doc_bios_html)
                self.printed_objs.append(rich_obj)
            elif isinstance(rich_obj, Table):
                html_table = table_to_html(rich_obj, css_props)

                # this is a bad way to signify the table being printed is an OtherFiles table
                if self._last_bio_panel:
                    self._append_element_with_bio_div(html_table)
                else:
                    self.html_elements.append(html_table)
            elif isinstance(rich_obj, Panel):
                self.html_elements.append(panel_to_div(rich_obj, css_props))
            elif isinstance(rich_obj, Text):
                self.html_elements.append(text_to_div(rich_obj, css_props))
            elif isinstance(rich_obj, BasePanel):
                self.html_elements.append(rich_obj.to_div((site_config.info_indent, 0)))
            elif '__rich__' in dir(rich_obj):
                if (rendered_obj := rich_obj.__rich__()):
                    if isinstance(rendered_obj, Text):
                        element = text_to_div(rendered_obj, css_props)
                    else:
                        logger.warning(f"printinng possibly not fully supported object type {type(rich_obj).__name__}\n{rich_obj}")
                        element = rich_to_html(rendered_obj)

                    self.html_elements.append(element)
                else:
                    logger.warning(f"__rich__() returned None for {rich_obj} ({type(rich_obj).__name__})")
            elif isinstance(rich_obj, str):
                self.html_elements.append(tag('p', rich_obj, css_props))
            else:
                raise TypeError(f"renderable of unsupported type: {type(rich_obj).__name__}: {rich_obj}")

            # TODO: we print at end after HTML is generated so the bios panel will be cached first but that sucks
            # TODO: because build_biographies_panel_html() has the side effect of printing to the console.
            console.print(renderable)

    def print_section_subtitle(self, msg: str) -> None:
        self.print_centered(section_subtitle_panel(msg))

    def print_title_page_top(self) -> None:
        self._print_title_page_elements(title_page_top_elements())

    def print_title_page_bottom(self) -> None:
        self._print_title_page_elements(title_page_bottom_elements(self.epstein_files))

    def write_html(self, html_path: Path | SiteType) -> Path:
        """Export custom HTML, trigger rich export_html() if `SiteType` given, returns custom HTML path."""
        if isinstance(html_path, SiteType):
            from epstein_files.output.output import write_html
            write_html(SiteType.html_output_path(html_path))
            output_path = SiteType.real_html_build_path(html_path)
        else:
            output_path = html_path

        return write_templated_html(self.html_elements, output_path)

    # def write_mobile_html(self, html_path: Path) -> None:
    #     write_templated_html(self.mobile_html_elements, html_path)

    def _align_biographical_panel(self, panel: Panel) -> Align:
        return Align(Padding(panel, site_config.character_bio_padding), 'right')

    def _append_element_with_bio_div(self, element: str, bio_panel: str = '') -> None:
        """Cache the `last_bio_panel` html so it can be placed inside div with document."""
        if self._last_bio_panel:
            bio_panel = self._last_bio_panel
            self._last_bio_panel = ''

        element = '\n'.join([bio_panel, element])
        self.html_elements.append(div_class(element, 'doc_container'))

    def _biographical_panel(self, _names: list[str]) -> Panel | None:
        """Panel showing biographical info for a list of names."""
        names = uniq_sorted(self.new_names_with_bios(_names))

        if (bios := [Text('', justify='right').append(PEOPLE_BIOS[n]) for n in names if PEOPLE_BIOS.get(n)]):
            logger.debug(f"Creating bios panel for {len(names)} new names (of {len(_names)} _names), names={names}")

            return Panel(
                Group(*bios),
                border_style='dim',
                box=box.DOUBLE,
                expand=False,
                style='on gray7',
                title=Text(f"new names in next file", 'grey85 italic'),
                title_align='right',
            )
        else:
            return None

    def _build_biographies_panel_html(self, names: list[str]) -> str:
        """NOTE: Also prints to console!!"""
        if (bio_panel := self._biographical_panel(names)):
            self._print_other_files_queue()  # Clear the queue before new biographical panel
            console.print(self._align_biographical_panel(bio_panel))
            self.printed_name_bios.update(names)
            return div_class(rich_to_html(bio_panel, minimize_width=True), STICKY_BIO_CSS_CLASS)
        else:
            return ''

    def _cache_biographies_panel(self, names: list[str]) -> None:
        """The html string of the bios panel is cached in `self.last_bio_panel`."""
        if (bios_html := self._build_biographies_panel_html(names)):
            if self._last_bio_panel:
                raise RuntimeError(f"last_bio_panel should be empty, instead it's:\n{self._last_bio_panel}")
            else:
                self._last_bio_panel = bios_html

    def _html_so_far(self, mobile: bool = False) -> str:
        """Return everything currently in the console buffer as an HTML string."""
        if mobile:
            return console_buffer_to_html(mobile_console, False)
        else:
            return console_buffer_to_html(console, False)

    def _print_other_files_queue(self) -> None:
        """Print any queued OtherFile objects collected in a table."""
        if not self._other_files_queue:
            return

        # Title is only on the first OtherFiles table printed
        if any(isinstance(d, OtherFile) for d in self.printed_docs):
            table_title = None
        else:
            table_title = OTHER_FILES_TABLE_MSG
            self.line()

        table = OtherFile.files_preview_table(self._other_files_queue, title=table_title, title_justify='center')
        self.print_renderable(Padding(table, (0, 0, 1, site_config.other_files_table_indent)))
        self.printed_objs.extend(self._other_files_queue)
        self._other_files_queue = []

    def _print_suppression_msgs_queue(self) -> list[Document]:
        """Print any suppression messages. Returns Documents whose suppression msg was printed."""
        if not self._suppressed_docs_queue:
            return []

        msgs_panel = BasePanel(border_style='', text=[d.suppressed_txt for d in self._suppressed_docs_queue])
        self.print_renderable(msgs_panel)
        console.line()  # TODO this isn't happening in HTML output

        processed_suppressed_docs = self._suppressed_docs_queue
        self._suppressed_docs_queue = []  # Reset queue
        return processed_suppressed_docs

    def _print_title_page_elements(self, renderables: list[RenderableType]) -> None:
        """"Centered and vertically paded Tables and Panels."""
        renderables = [vertically_pad(r) if isinstance(r, (Panel, Table)) else r for r in renderables]

        for r in renderables:
            obj, css_props = unwrap_rich(r)
            logger.debug(f"Printing title page {type(obj).__name__} with css_props: {css_props}")

        self.print_centered(renderables)
