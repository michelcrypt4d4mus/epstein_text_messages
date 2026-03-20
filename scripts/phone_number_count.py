#!/usr/bin/env python
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.people.names import *
from epstein_files.people.entity import Entity, Organization, law_enforcement, epstein_co
from epstein_files.documents.config.communication_cfg import CommunicationCfg
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.documents.emails.emailers import ENTITIES_DICT
from epstein_files.documents.messenger_log_pdf import MessengerLogPdf
from epstein_files.output.output import write_html
from epstein_files.output.rich import print_subtitle_panel
from epstein_files.output.site.sites import BASE_DEPLOY_URL, HtmlDir
from epstein_files.people.entity import acronym, Entity
from epstein_files.people.names import extract_first_name, extract_last_name
from epstein_files.util.constant.urls import download_jmail_pdf
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.helpers.debugging_helper import print_all_highlighted_quotes
from epstein_files.util.helpers.file_helper import open_file_or_url
from epstein_files.util.helpers.string_helper import as_pattern
from epstein_files.util.logging import logger
from epstein_files.util.external_link import ExternalLink
from epstein_files.util.helpers.data_helpers import sort_dict


TEL_LINE_PATTERN = r"Telephone ([1#IiN]|It)\s*(?P<phone_number>\d{10})"
BILLING_LINE_PATTERN = r"Billing (#|l?[Ii]t?) (?P<billing_number>\d{10})"
TEL_LINE_REGEX = re.compile(TEL_LINE_PATTERN)
BILLING_LINE_REGEX = re.compile(BILLING_LINE_PATTERN)
ACCOUNT_REGEX = re.compile(fr"^{TEL_LINE_PATTERN}\s*{BILLING_LINE_PATTERN}.*$", re.IGNORECASE)

CALL_REGEX = re.compile(r"^\d{6}\s+[A-Z0-9]{5}\s+(?P<phone_number>\d{3}\s*\d{3}\s*\d{4})\s+.*")
CALL_REGEX2 = re.compile(r"\d+\.?\s+\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}[ap]m\s*(?P<location>[\w ]*?)\s+(?P<phone_number>\d{3} \d{3}-\d{4}|\d{7,})[^\d].*")
CALL_REGEX3 = re.compile(r"^(?P<phone_number>\d{3} \d{3}-\d{4}|\d{11,14})$")
JUNK_LINE = re.compile(r"^(EFTA|PhCnt|ACCOUNT NUM|YRMODY|Case #).*")

FILE_ID = 'EFTA01242527'
RAW_OCR_URL = f"{BASE_DEPLOY_URL}/{FILE_ID}.txt"
RAW_OCR_LINK = ExternalLink(RAW_OCR_URL, f"Raw OCR .txt for {FILE_ID}.pdf")

call_counts = defaultdict(int)
call_counts_by_source_number = defaultdict(lambda: defaultdict(int))
doc = epstein_files.get_id(FILE_ID)
current_billing_number = ''
current_phone_number = ''
epstein_phone_numbers_found = 0
calls_found = 0


def format_phone_number(number: str) -> str:
    if len(number) == 10:
        return f"{number[0:3]}-{number[3:6]}-{number[6:]}"
    elif len(number) > 10:
        return f"+{number}"
    else:
        return number


@dataclass
class CallCounter:
    calls: list[tuple[str, str]] = field(default_factory=list)
    call_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    call_counts_by_source: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))

    def record_call(self, source: str, destination: str) -> None:
        source = source.replace('-', '').replace(' ', '').strip()
        destination = destination.replace('-', '').replace(' ', '').strip()
        self.calls.append((source, destination))
        self.call_counts[destination] += 1
        self.call_counts_by_source[source][destination] += 1
        logger.debug(f"Found call from '{source}' to '{destination}'")

        if len(self.calls) % 1000 == 0:
            logger.warning(f"Found {calls_found} on {epstein_phone_numbers_found} Epstein phone numbers so far...")

    def print(self) -> None:
        console.print(f"Found {len(self.call_counts_by_source)} Epstein phone numbers calling {len(self.call_counts)} other numbers.")
        console.print(Text(f"Source PDF: ").append(doc.file_info.external_link_txt()))
        console.print(RAW_OCR_LINK)
        console.line(2)
        print_subtitle_panel(f"Total Call Counts in {FILE_ID} (imperfect count)")
        console.line()

        for number, count in sort_dict(self.call_counts):
            console.print(f"     {format_phone_number(number)}: {count} calls")

        for epstein_number, call_counts_by_source_number in self.call_counts_by_source.items():
            console.line(2)
            print_subtitle_panel(f"From Epstein phone {format_phone_number(epstein_number)}")

            for number, count in sort_dict(call_counts_by_source_number):
                console.print(f"     {format_phone_number(number)}: {count} calls")

        open_file_or_url(write_html(HtmlDir.build_path(f"{FILE_ID}_phone_calls.html")))


counter = CallCounter()

for line in doc.raw_text().split('\n'):
    line = line.strip()

    if (m := ACCOUNT_REGEX.match(line)):
        epstein_phone = m.group('phone_number')
        billing = m.group('billing_number')

        if epstein_phone != current_phone_number:
            logger.warning(f"New account phone number encountered: {epstein_phone}")
            epstein_phone_numbers_found += 1
            current_phone_number = epstein_phone

        if billing != current_billing_number:
            logger.warning(f"New account billing number encountered: {billing}")
            current_billing_number = billing
    elif (m := BILLING_LINE_REGEX.match(line)):
        billing = m.group('billing_number')

        if billing != current_billing_number:
            logger.warning(f"New account billing number encountered: {billing}")
            current_billing_number = billing
    elif (m := TEL_LINE_REGEX.match(line)):
        epstein_phone = m.group('phone_number')

        if epstein_phone != current_phone_number:
            logger.warning(f"New account phone number encountered: {epstein_phone}")
            epstein_phone_numbers_found += 1
            current_phone_number = epstein_phone
    elif (m := CALL_REGEX.match(line)) or (m := CALL_REGEX2.match(line)) or (m := CALL_REGEX3.match(line)):
        to_number = m.group('phone_number')
        counter.record_call(current_billing_number, to_number)
    else:
        if JUNK_LINE.match(line) or len(line) <= 4:
            logger.info(f"junk line: '{line}'")
        else:
            logger.warning(f"junk line: '{line}'")


counter.print()
