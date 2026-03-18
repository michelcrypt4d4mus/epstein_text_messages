from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from rich import box
from rich.align import Align, AlignMethod
from rich.console import Group, NewLine, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import Document
from epstein_files.documents.documents.categories import sort_categories
from epstein_files.documents.documents.doc_types_mixin import DocTypesMixin
from epstein_files.documents.email import Email
from epstein_files.documents.emails.emailers import ENTITY_CATEGORIES, get_entities
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.layout_elements.file_display import BasePanel, FileDisplay, ListPanel
from epstein_files.output.html.builder import (console_buffer_to_html, render_at_obj_width, panel_to_div,
     render_to_html, text_to_div, write_templated_html)
from epstein_files.output.html.elements import div_class, tag
from epstein_files.output.html.positioned_rich import PositionedRich, to_em, unpack_dimensions, vertical_spacer
from epstein_files.output.rich import console, section_subtitle_panel
from epstein_files.output.site.sites import Site
from epstein_files.people.entity import Entity
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import listify, uniq_sorted, without_falsey
from epstein_files.util.helpers.rich_helpers import vertically_pad
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger
from epstein_files.util.timer import Timer
from epstein_files.output.title_page import color_key, title_page_top_elements, title_page_bottom_elements

OTHER_FILES_TABLE_MSG = Text("(non emails will appear in tables)", 'gray27 italic')
EMPTY_LINE_HEIGHT = to_em(1.5)
EMPTY_LINE_DIV = f'<div style="height: {EMPTY_LINE_HEIGHT}"></div>'
STICKY_BIO_CSS_CLASS = 'sticky_person_bio_panel'

PrintableObj = Document | FileDisplay
PeopleBiosArg = list[str] | list[Entity] | PrintableObj


@dataclass(kw_only=True)
class DocPrinter(DocTypesMixin):
    """
    Handles printing collections of documents with biographical info panels interspersed.

    Args:
        epstein_files (EpsteinFiles): the data
        collect_other_files_to_tables (bool, optional): OtherFiles will be collected into small tables if they are sequential
        html_elements (list[str]): HTML for all objects printed so far
        printed_docs (list[Document]): all Documents that have been printed so far
        printed_name_bios (set[Entity]): all the names for which biographical information has been printed already
    """
    epstein_files: 'EpsteinFiles'
    collect_other_files_to_tables: bool = True
    html_elements: list[str] = field(default_factory=list)
    printed_entity_bios: set[Entity] = field(default_factory=set)
    _last_bio_panel = ''
    _other_files_queue: list[OtherFile] = field(default_factory=list)
    _suppressed_docs_queue: list[Document] = field(default_factory=list)

    def __post_init__(self):
        """Initialize with HTML of what's been printed to the console history buffer up to this point."""
        self.html_elements.append(console_buffer_to_html(console, False))

    @property
    def printed_docs(self) -> list[Document]:
        return Document.filter_for_type(self._documents)  # TODO: necessary because of FileDisplay objs

    @property
    def printed_emails(self) -> list[Email]:
        return self.emails

    @property
    def printed_ids(self) -> list[str]:
        return [f.file_id for f in self.printed_docs]

    def line(self, num: int = 1) -> None:
        """Print blank lines to HTML and terminal, similar to `console.line()`."""
        self.html_elements.append(vertical_spacer(num))
        console.line(num)

    def new_entities(self, names_or_doc: PeopleBiosArg) -> list[Entity]:
        """List of names found in relation to `names_or_doc` that have not been biographically printed before."""
        if isinstance(names_or_doc, FileDisplay) or not names_or_doc:
            return []
        elif isinstance(names_or_doc, Document):
            entities = names_or_doc.entity_scan(exclude=list(self.printed_entity_bios))
        else:
            entities = get_entities(names_or_doc)

        return [e for e in entities if e not in self.printed_entity_bios]

    def new_entities_with_bios(self, names_or_doc: PeopleBiosArg) -> list[Entity]:
        """Return names that a) were not seen before and b) have configured biographical info."""
        return [n for n in self.new_entities(names_or_doc) if n.has_bio]

    def print_biographies(self) -> None:
        """Print all the `Entity` objects that are configured in one big colored list."""
        self.print_section_subtitle('Entities With Configured Biographical Info')

        entity_bios = [
            Padding(c.bio_txt, site_config.contact_list_padding)
            for category in sort_categories([c for c in ENTITY_CATEGORIES.keys()])
            for c in ENTITY_CATEGORIES[category]
        ]

        self.print(entity_bios)

    def print_centered(self, _renderables: RenderableType | list[RenderableType]):
        renderables = listify(_renderables)

        if any(isinstance(r, Align) for r in renderables):
            logger.warning(f"wrapping an Align in another Align...")

        self.print([Align.center(obj) for obj in listify(renderables)])

    def print_color_key(self) -> None:
        self.print_centered(color_key())

    def print_documents(
        self,
        docs: Sequence[PrintableObj],
        suppressed_as_normal: bool = False,
        log_sfx: str = '',
    ) -> None:
        """
        Sequential suppression msgs + OtherFiles collect in queues to be printed when
        an obj of another type shows up or if there's new names for a biography panel.

        Args:
            docs (Sequence[PrintableObj]): objs to print
            suppressed_as_normal (bool, optional): if True docs with suppression msgs will be treated like normal Documents
            log_sfx (str, optional): just for log messages
        """
        suppressed_docs: list[Document] = []
        process_suppressed_docs_queue = lambda: suppressed_docs.extend(self._print_suppression_msgs_queue())
        timer = Timer()

        if (should_log_in_intervals := (len(docs) > 1000)):
            logger.info(f"{type(self).__name__}.print_documents() called with {len(docs):,} objects {log_sfx}")

        for i, doc in enumerate(docs, 1):
            # Handle sequences of uninteresting or otherwise suppressed docs
            if isinstance(doc, Document) and doc.suppressed_txt and not suppressed_as_normal:
                self._log_state(doc, f"suppressing {quote(doc.suppressed_txt.plain)}")
                self._suppressed_docs_queue.append(doc)
                continue

            process_suppressed_docs_queue()

            # Collect sequences of otherFile objects into a table
            if self.collect_other_files_to_tables and isinstance(doc, OtherFile) and doc.is_valid_for_table:
                if (new_entities := self.new_entities_with_bios(doc)):
                    doc._log(f"Caching biographic panel for new entities: {[str(e) for e in new_entities]}")
                    self._cache_biographies_panel(new_entities)

                self._log_state(doc, f"queueing other file for table")
                self._other_files_queue.append(doc)
                continue

            self._log_state(doc, f"triggering print of other files queue")
            self._print_other_files_queue()
            self.print(doc)

            if should_log_in_intervals and (i % 100 == 0):
                timer.print_at_checkpoint(f"Printed {i:,} objs of {len(docs):,} ({len(suppressed_docs):,} suppressed) {log_sfx}")

        process_suppressed_docs_queue()
        self._print_other_files_queue()
        timer.print_at_checkpoint(f"Finished printing {len(docs):,} objs ({len(suppressed_docs):,} suppressed) {log_sfx}")

    def print(self, renderables: RenderableType | Sequence[RenderableType]) -> None:
        """All things being printed should come through here, which collects both terminal and HTML output as its written."""
        for renderable in listify(renderables):
            positioned = PositionedRich.from_unwrapped_obj(renderable)

            # Add html string for this renderable to self.html_elements
            if isinstance(positioned.obj, NewLine):
                self.line()
                continue
            elif isinstance(positioned.obj, PrintableObj):
                doc_bios_html = self._build_biographies_panel_html(self.new_entities_with_bios(positioned.obj))
                self._append_element_with_bio_div(positioned.obj.to_html(), doc_bios_html)
                doc = positioned.obj.document if isinstance(positioned.obj, FileDisplay) else positioned.obj
                self._documents.append(doc)
            elif isinstance(positioned.obj, Table):
                html_table = positioned.to_html()  # TODO: currently the only type that delegates to the PositionedRich obj to get HTML

                # this is a bad way to signify the table being printed is an OtherFiles table
                if self._last_bio_panel:
                    self._append_element_with_bio_div(html_table)
                else:
                    self.html_elements.append(html_table)
            elif isinstance(positioned.obj, Panel):
                self.html_elements.append(panel_to_div(positioned.obj, positioned.css))
            elif isinstance(positioned.obj, BasePanel):
                margin = unpack_dimensions((site_config.info_indent, 0))  # TODO: this margin dimension should only exist on eone side if aligned
                self.html_elements.append(positioned.obj.to_div(margin))
            elif isinstance(positioned.obj, Text):
                self.html_elements.append(text_to_div(positioned.obj, positioned.css))
            elif '__rich__' in dir(positioned.obj) and (rich_obj := positioned.obj.__rich__()):
                if isinstance(rich_obj, Text):
                    element_html = text_to_div(rich_obj, positioned.css)
                else:
                    logger.warning(f"printinng possibly not fully supported object type {type(positioned.obj).__name__}\n{positioned.obj}")
                    element_html = render_to_html(rich_obj)

                self.html_elements.append(element_html)
            elif isinstance(positioned.obj, str):
                self.html_elements.append(tag('p', positioned.obj, positioned.css))
            else:
                raise TypeError(f"renderable of unsupported type: {type(positioned.obj).__name__}: {positioned.obj}")

            # TODO: console.print at end after HTML is generated so the bios panel will be cached first
            # TODO: because build_biographies_panel_html() has the side effect of printing to the console.
            console.print(renderable)

    def print_section_subtitle(self, msg: str) -> None:
        self.print_centered(section_subtitle_panel(msg))

    def print_title_page_top(self) -> None:
        self._print_title_page_elements(title_page_top_elements())

    def print_title_page_bottom(self) -> None:
        self._print_title_page_elements(title_page_bottom_elements(self.epstein_files))

    def write_html(self, write_to: Path | Site) -> Path:
        """Export custom HTML, trigger rich export_html() if `SiteType` given, returns custom HTML path."""
        if isinstance(write_to, Path):
            output_path = write_to
            logger.warning(f"Not exporting rich.console to HTML directly (only custom)...")
        else:
            output_path = Site.custom_html_build_path(write_to)
            from epstein_files.output.output import write_html
            write_html(write_to)

        return write_templated_html(self.html_elements, output_path)

    def _align_biographical_panel(self, panel: Panel) -> Align:
        return Align(Padding(panel, site_config.character_bio_padding), 'right')

    def _append_element_with_bio_div(self, element: str, bio_panel: str = '') -> None:
        """Cache the `last_bio_panel` html so it can be placed inside div with document."""
        if self._last_bio_panel:
            bio_panel = self._last_bio_panel
            self._last_bio_panel = ''

        element = '\n'.join([bio_panel, element])
        self.html_elements.append(div_class(element, 'doc_container'))

    def _biographical_panel(self, _entities: list[Entity]) -> Panel | None:
        """Panel showing biographical info for a list of names."""
        if (entities := self.new_entities_with_bios(_entities)):
            bios = [Text('', justify='right').append(e.bio_txt) for e in entities if e.has_bio]
            logger.debug(f"Creating bios panel for {len(entities)} new names (out of {len(_entities)} _entities)")

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

    def _build_biographies_panel_html(self, entities: list[Entity]) -> str:
        """NOTE: Also prints to console!!"""
        if (bio_panel := self._biographical_panel(entities)):
            self._print_other_files_queue()  # Clear the queue before new biographical panel
            console.print(self._align_biographical_panel(bio_panel))  # TODO: has side effect of printing to console
            panel_html = render_at_obj_width(bio_panel)
            self.printed_entity_bios.update(entities)
            return div_class(panel_html, STICKY_BIO_CSS_CLASS)
        else:
            return ''

    def _cache_biographies_panel(self, entities: list[Entity]) -> None:
        """The html string of the bios panel is cached in `self.last_bio_panel`."""
        if (bios_html := self._build_biographies_panel_html(entities)):
            if self._last_bio_panel:
                raise RuntimeError(f"last_bio_panel should be empty, instead it's:\n{self._last_bio_panel}")
            else:
                self._last_bio_panel = bios_html

    def _log_state(self, doc: PrintableObj, msg: str = '') -> None:
        supressed_ids = [f.file_id for f in self._suppressed_docs_queue]
        other_files_queue_ids = [f.file_id for f in self._other_files_queue]
        queues_str = f"(suppressed queue: {supressed_ids}, other files queue: {other_files_queue_ids})"

        if isinstance(doc, FileDisplay):
            logger.info(f"{doc} {msg} {queues_str}")
        else:
            doc._log(f"{msg} {queues_str}")

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
        self.print(Padding(table, (0, 0, 1, site_config.other_files_table_indent)))
        self._documents.extend(self._other_files_queue)
        self._other_files_queue = []

    def _print_suppression_msgs_queue(self) -> list[Document]:
        """Print any suppression messages. Returns Documents whose suppression msg was printed."""
        if not self._suppressed_docs_queue:
            return []

        suppressed_txts = without_falsey([d.suppressed_txt for d in self._suppressed_docs_queue])
        msgs_panel = ListPanel(border_style='', text=suppressed_txts)
        self.print(msgs_panel)
        console.line()  # TODO this isn't happening in HTML output

        processed_suppressed_docs = self._suppressed_docs_queue
        self._suppressed_docs_queue = []  # Reset queue
        return processed_suppressed_docs

    def _print_title_page_elements(self, renderables: list[RenderableType]) -> None:
        """"Centered and vertically paded Tables and Panels."""
        renderables = [vertically_pad(r) if isinstance(r, (Panel, Table)) else r for r in renderables]
        self.print_centered(renderables)
