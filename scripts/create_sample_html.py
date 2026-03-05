#!/usr/bin/env python
# Print email ID + timestamp
from collections import defaultdict

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.doc_printer import DocPrinter
from epstein_files.output.html.builder import table_to_html, write_templated_html
from epstein_files.output.rich import console, highlighter, print_json, print_subtitle_panel
from epstein_files.output.site.sites import SAMPLE_HTML_PATH
from epstein_files.output.title_page import print_title_page_top, print_title_page_bottom
from epstein_files.people.person import Person
from epstein_files.util.helpers.data_helpers import flatten
from epstein_files.util.helpers.file_helper import open_file_or_url
from epstein_files.util.logging import logger

SAMPLE_SIZE = 3


doc_sets_to_sample = [
    [o for o in epstein_files.other_files if o.config and o.config.show_full_panel],
    [o for o in epstein_files.other_files if o.config_description_txt],  # other file with description
    [o for o in epstein_files.other_files if 1000 < o.length < 5000 and not o.config_description_txt], # other files no desc
    [e for e in epstein_files.emails if e.config_description_txt], # emails with description
    [e for e in epstein_files.emails if not e.config_description_txt],  # email no desc
    epstein_files.emails_with_attachments,
    epstein_files.imessage_logs,
]

emails_with_attachments_ids = [e.file_id for e in epstein_files.emails_with_attachments]
print(f"Found {len(emails_with_attachments_ids)} emails with attachments: {emails_with_attachments_ids}")
sample_docs = [epstein_files.get_id('EFTA00034357')] + flatten([docs[:SAMPLE_SIZE] for docs in doc_sets_to_sample])

printer = DocPrinter()
printer.print_documents(sample_docs)

all_emailers = sorted(epstein_files.emailers, key=lambda person: person.sort_key)
people_table = Person.emailer_info_table(all_emailers, all_emailers, show_epstein_total=False)
printer.html_elements.append(table_to_html(people_table))
printer.write_html(SAMPLE_HTML_PATH)
open_file_or_url(SAMPLE_HTML_PATH)

# for doc in sample_docs:
#     doc.print()
