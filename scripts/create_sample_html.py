#!/usr/bin/env python
# Print email ID + timestamp
from collections import defaultdict

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.documents.documents.doc_list import DocList
from epstein_files.documents.email import Email
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.doc_printer import DocPrinter
from epstein_files.output.html.builder import table_to_html, panel_to_div
from epstein_files.output.site.sites import Site
from epstein_files.output.rich import CATEGORY_BG_STYLES
from epstein_files.people.entity import Entity
from epstein_files.people.person import Person
from epstein_files.util.helpers.data_helpers import flatten
from epstein_files.util.helpers.file_helper import open_file_or_url
from epstein_files.util.logging import logger

SAMPLE_SIZE = 2

TEST_PANELS = [
    Panel('bright_red', style='bright_red'),
    Panel('bright_red reverse', style='bright_red reverse'),
    Panel('cyan on red', style='cyan on red'),
    Panel('cyan on red reverse', style='cyan on red reverse'),
    Panel('cyan with padding', padding=(2, 2), style='cyan'),
    Panel('cyan on red with padding', padding=(2, 2), style='cyan on red'),
]


def print_sample_people(num_people_to_print: int = 3):
    """people panels and email history etc."""
    good_sample_people = [p for p in epstein_files.emailers if 5 <= len(p.unique_emails) <= 15]

    for i, person in enumerate(good_sample_people[0:num_people_to_print], 1):
        person.print_docs(printer)


def print_test_panels():
    for panel in TEST_PANELS:
        printer.print(panel)
        printer.line(2)


doc_types_to_sample = [
    [d for d in epstein_files.documents if d._config.show_image],
    [d for d in epstein_files.documents if d._config.background_color], # Configured BG
    [d for d in epstein_files.other_files if d.category in CATEGORY_BG_STYLES],  # BG by category
    [e for e in epstein_files.emails if 'https' in e.text[0:1500]],
    [o for o in epstein_files.other_files if o.config and o.config.show_full_panel],
    [d for d in epstein_files._documents if d.suppressed_txt],
    [o for o in epstein_files.other_files if o._config.note_txt],  # other file with description
    [o for o in epstein_files.other_files if 1000 < o.length < 5000 and not o._config.note_txt], # other files no desc
    [e for e in epstein_files.emails if e._config.note_txt], # emails with description
    [e for e in epstein_files.emails if not e._config.note_txt],  # email no desc
    epstein_files.emails_with_attachments,
    epstein_files.imessage_logs,
]

sample_docs = DocList.uniquify_by_id(flatten([docs[:SAMPLE_SIZE] for docs in doc_types_to_sample]))
printer = DocPrinter(epstein_files=epstein_files)

# print header
printer.print_title_page_top()
printer.print_title_page_bottom()

# Print docs
printer.print_documents(sample_docs)

# print some People and their emails
# print_sample_people()

#Print big emailers summary table
all_emailers = sorted(epstein_files.emailers, key=lambda person: person.sort_key)
people_table = Person.emailer_info_table(all_emailers, all_emailers, show_epstein_total=False)
printer.html_elements.append(table_to_html(people_table))

# print contacts
# Entity.print_all_biographies(printer)

html_path = printer.write_html(Site.DEV_SAMPLE)
open_file_or_url(html_path)
