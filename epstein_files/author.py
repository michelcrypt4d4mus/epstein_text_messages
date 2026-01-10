import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Sequence, Type

from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.documents.email import DETECT_EMAIL_REGEX, JUNK_EMAILERS, KRASSNER_RECIPIENTS, USELESS_EMAILERS, Email
from epstein_files.documents.emails.email_header import AUTHOR
from epstein_files.documents.json_file import JsonFile
from epstein_files.documents.messenger_log import MSG_REGEX, MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import *
from epstein_files.util.data import days_between, dict_sets_to_lists, json_safe, listify
from epstein_files.util.doc_cfg import EmailCfg, Metadata
from epstein_files.util.env import DOCS_DIR, args, logger
from epstein_files.util.file_helper import file_size_str
from epstein_files.util.highlighted_group import HIGHLIGHTED_NAMES, QUESTION_MARKS_TXT, HighlightedNames, get_highlight_group_for_name, get_info_for_name, get_style_for_name, styled_category, styled_name
from epstein_files.util.rich import (NA_TXT, add_cols_to_table, build_table, console, highlighter,
     print_author_panel, print_centered, print_subtitle_panel)

ALT_INFO_STYLE = 'medium_purple4'

INVALID_FOR_EPSTEIN_WEB = JUNK_EMAILERS + KRASSNER_RECIPIENTS + [
    'ACT for America',
    'BS Stern',
    INTELLIGENCE_SQUARED,
    UNKNOWN,
]


@dataclass(kw_only=True)
class Author:
    """Collection of data about someone texting or emailing Epstein."""
    name: str | None
    emails: list[Email] = field(default_factory=list)
    imessage_logs: list[MessengerLog] = field(default_factory=list)
    other_files: list[OtherFile] = field(default_factory=list)

    def __post_init__(self):
        self.emails = Document.sort_by_timestamp(self.emails)
        self.imessage_logs = Document.sort_by_timestamp(self.imessage_logs)

    def category(self) -> str | None:
        highlight_group = self.highlight_group()

        if highlight_group and isinstance(highlight_group, HighlightedNames):
            return highlight_group.category or highlight_group.label

    def category_txt(self) -> Text | None:
        if self.category() and self.category() != self.name:
            return styled_category(self.category())

    def email_conversation_length_in_days(self) -> int:
        return days_between(self.emails[0].timestamp, self.emails[-1].timestamp)

    def earliest_email_at(self) -> datetime:
        return self.emails[0].timestamp

    def earliest_email_date(self) -> date:
        return self.earliest_email_at().date()

    def last_email_at(self) -> datetime:
        return self.emails[-1].timestamp

    def last_email_date(self) -> date:
        return self.last_email_at().date()

    def emails_by(self) -> list[Email]:
        return [e for e in self.emails if self.name == e.author]

    def emails_to(self) -> list[Email]:
        return [
            e for e in self.emails
            if self.name in e.recipients or (self.name is None and len(e.recipients) == 0)
        ]

    def external_link(self, site: ExternalSite = EPSTEINIFY) -> str:
        return AUTHOR_LINK_BUILDERS[site](self.name_str())

    def external_link_txt(self, site: ExternalSite = EPSTEINIFY, link_str: str | None = None) -> Text:
        if self.name is None:
            return Text('')

        return link_text_obj(self.external_link(site), link_str or site)

    def highlight_group(self) -> HighlightedNames | None:
        return get_highlight_group_for_name(self.name)

    def info_str(self) -> str | None:
        highlight_group = self.highlight_group()

        if highlight_group and isinstance(highlight_group, HighlightedNames) and self.name:
            return highlight_group.get_info(self.name)

    def info_txt(self) -> Text | None:
        category = self.category()
        info = self.info_str()

        if self.name == JEFFREY_EPSTEIN:
            return Text('(emails sent by Epstein to himself that would not otherwise be printed)', style=ALT_INFO_STYLE)
        if category and category == 'paula':  # TODO: hacky
            category = None
        elif category and info:
            info = info.removeprefix(category).removeprefix(', ')
        elif not self.name:
            info = Text('(emails whose author or recipient could not be determined)', style=ALT_INFO_STYLE)
        elif not self.style() and '@' not in self.name and not (category or info):
            info = QUESTION_MARKS_TXT

    # TODO: rename is_linkable()
    def _is_ok_for_epstein_web(self) -> bool:
        """Return True if it's likely that EpsteinWeb has a page for this name."""
        if self.name is None or ' ' not in self.name:
            return False
        elif '@' in self.name or '/' in self.name or QUESTION_MARKS in self.name:
            return False
        elif self.name in INVALID_FOR_EPSTEIN_WEB:
            return False

        return True

    def name_str(self) -> str:
        return self.name or UNKNOWN

    def name_link(self) -> Text:
        """Will only link if it's worth linking, otherwise just a Text object."""
        if not self._is_ok_for_epstein_web():
            return self.name_txt()
        else:
            return Text.from_markup(link_markup(self.external_link(), self.name_str(), self.style()))

    def name_txt(self) -> Text:
        return styled_name(self.name)

    def print_emails_for(self) -> list[Email]:
        """Print complete emails to or from a particular 'author'. Returns the Emails that were printed."""
        num_days = self.email_conversation_length_in_days()
        unique_emails = [email for email in self.emails if not email.is_duplicate()]
        title = f"Found {len(unique_emails)} emails"

        if self.name == JEFFREY_EPSTEIN:
            title += f" sent by {JEFFREY_EPSTEIN} to himself"
        else:
            title += f" to/from {self.name_str()} starting {self.earliest_email_date()} covering {num_days:,} days"

        print_author_panel(title, self.info_str(), self.style())
        self.print_emails_table_for()
        last_printed_email_was_duplicate = False

        for email in self.emails:
            if email.is_duplicate():
                console.print(Padding(email.duplicate_file_txt().append('...'), (0, 0, 0, 4)))
                last_printed_email_was_duplicate = True
            else:
                if last_printed_email_was_duplicate:
                    console.line()

                console.print(email)
                last_printed_email_was_duplicate = False

        return self.emails

    def print_emails_table_for(self) -> None:
        emails = [email for email in self.emails if not email.is_duplicate()]  # Remove dupes
        print_centered(Padding(Email.build_emails_table(emails, self.name), (0, 5, 1, 5)))

    def sort_key(self) -> list[int | str]:
        counts = [len(self.emails), len(self.emails_by()), len(self.emails_to())]  # TODO: exclude dupes?
        counts = [-1 * count for count in counts]

        if args.sort_alphabetical:
            return [self.name_str()] + counts
        else:
            return counts + [self.name_str()]

    def style(self) -> str:
        return get_style_for_name(self.name, default_style='')
