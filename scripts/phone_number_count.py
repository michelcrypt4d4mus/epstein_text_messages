#!/usr/bin/env python
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.output.epstein_highlighter import highlighter
from epstein_files.output.output import write_html
from epstein_files.output.rich import print_subtitle_panel
from epstein_files.output.site.sites import BASE_DEPLOY_URL, PHONE_LOG_FILE_ID, Site
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
CALL_REGEX2 = re.compile(r"\d+ ?\.?\s+\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}[ap]m\s*(?P<location>[\w ]*?)\s+(?P<phone_number>\d{3} \d{3}-\d{4}|\d{7,})[^\d].*")
CALL_REGEX3 = re.compile(r"^(?P<phone_number>\d{3} \d{3}-\d{4}|\d{11,14})$")
JUNK_LINE = re.compile(r"^(CARRIER|EFTA|PhCnt|ACCOUNT NUM|YRMODY|These charges|Case #).*")

RAW_OCR_URL = f"{BASE_DEPLOY_URL}/{PHONE_LOG_FILE_ID}.txt"
RAW_OCR_LINK = ExternalLink(RAW_OCR_URL, f"Raw OCR .txt for {PHONE_LOG_FILE_ID}.pdf")

call_counts = defaultdict(int)
call_counts_by_source_number = defaultdict(lambda: defaultdict(int))
doc = epstein_files.get_id(PHONE_LOG_FILE_ID)
current_billing_number = ''
current_phone_number = ''
epstein_phone_numbers_found = 0
calls_found = 0


def cleanup_phone_number(number: str) -> str:
    return number.replace('-', '').replace(' ', '').strip()


def format_phone_number(number: str) -> str:
    if len(number) == 10:
        return f"{number[0:3]}-{number[3:6]}-{number[6:]}"
    elif len(number) > 10:
        return f"+{number}"
    else:
        return number


@dataclass
class CallCounter:
    billing_numbers: set[str] = field(default_factory=set)
    calls: list[tuple[str, str]] = field(default_factory=list)
    call_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    call_counts_by_source: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))

    @property
    def epstein_phone_numbers(self) -> list[str]:
        return [n for n in self.call_counts_by_source.keys()]

    def record_call(self, source: str, destination: str, billing: str) -> None:
        # logger.debug(f"Found call from '{source}' to '{destination}' billing '{billing}'")
        source = cleanup_phone_number(source)
        destination = cleanup_phone_number(destination)
        self.calls.append((source, destination))
        self.call_counts[destination] += 1
        self.call_counts_by_source[source][destination] += 1
        self.billing_numbers.add(cleanup_phone_number(billing))

        if len(self.calls) % 1000 == 0:
            logger.warning(f"Found {len(self.calls)} on {len(self.call_counts_by_source)} Epstein phone numbers so far...")

    def print(self) -> None:
        console.print(f"Found {len(self.call_counts_by_source)} Epstein phone numbers calling {len(self.call_counts)} other numbers.")
        console.line()
        self._print_indented(Text(f"Source PDF: ").append(doc.file_info.external_link_txt()))
        self._print_indented(RAW_OCR_LINK.link)
        console.print(f"\nEpstein's phone numbers:")

        for number in self.epstein_phone_numbers:
            count = len([c for c in self.calls if c[0] == number])
            self._print_call_count(number, count)

        console.print(f"\nEpstein's billing numbers:")

        for number in self.billing_numbers:
            count = len([c for c in self.calls if c[2] == number])
            self._print_call_count(number, count)

        self._print_call_counts(f"Total Call Counts in {PHONE_LOG_FILE_ID} (imperfect count)", self.call_counts)

        for epstein_number, call_counts_by_source_number in self.call_counts_by_source.items():
            self._print_call_counts(
                f"Calls from Epstein phone {format_phone_number(epstein_number)}",
                call_counts_by_source_number
            )

        open_file_or_url(write_html(Site.PHONE_NUMBERS))

    def _print_call_counts(self, title: str, counts: dict[str, int]) -> None:
        console.line(2)
        print_subtitle_panel(title)
        console.line()

        for number, count in sort_dict(self.call_counts):
            self._print_call_count(number, count)

    def _print_call_count(self, number: str, count: int) -> None:
        self._print_indented(f"{format_phone_number(number)}: {count:,} calls")

    def _print_indented(self, s: str | Text) -> None:
        console.print(highlighter(Text("    ").append(s)))


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
        counter.record_call(current_phone_number, to_number, current_billing_number)
    else:
        if JUNK_LINE.match(line) or len(line) <= 4:
            logger.info(f"junk line: '{line}'")
        else:
            logger.warning(f"junk line: '{line}'")


counter.print()
