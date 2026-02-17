from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Sequence

from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.documents.email import TRUNCATE_EMAILS_BY, MAILING_LISTS, JUNK_EMAILERS, Email
from epstein_files.documents.emails.emailers import CONTACTS_DICT, cleanup_str
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import (QUESTION_MARKS_TXT, get_highlight_group_for_name,
     get_style_for_name, styled_category, styled_name)
from epstein_files.output.highlighted_names import HighlightedNames, HighlightedText, ManualHighlight
from epstein_files.output.rich import (GREY_NUMBERS, TABLE_TITLE_STYLE, build_table,
     console, join_texts, print_centered)
from epstein_files.people.contact import Contact
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import *
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import days_between, flatten, uniquify, without_falsey

ALT_INFO_STYLE = 'medium_purple4'
CC = 'cc:'
MIN_AUTHOR_PANEL_WIDTH = 80
EMAILER_INFO_TITLE = 'Email Conversations Will Appear'
UNINTERESTING_CC_INFO = "cc: or bcc: recipient only"
UNINTERESTING_CC_INFO_NO_CONTACT = f"{UNINTERESTING_CC_INFO}, no direct contact with Epstein"

INVALID_FOR_EPSTEIN_WEB = JUNK_EMAILERS + MAILING_LISTS + [
    'ACT for America',
    'BS Stern',
    UNKNOWN,
]


@dataclass(kw_only=True)
class Person:
    """Collection of data about someone texting or emailing Epstein."""
    contact_info: Contact = field(init=False)
    name: Name
    emails: list[Email] = field(default_factory=list)
    imessage_logs: list[MessengerLog] = field(default_factory=list)
    other_files: list[OtherFile] = field(default_factory=list)
    is_uninteresting: bool = False
    _searched_for_highlight_group: bool = False

    def __post_init__(self):
        self.contact_info = CONTACTS_DICT.get(str(self.name)) or Contact(name=cleanup_str(str(self.name)))
        self.emails = Document.sort_by_timestamp(self.emails)
        self.imessage_logs = Document.sort_by_timestamp(self.imessage_logs)

    @property
    def category(self) -> str | None:
        if self.highlighted_names_group:
            category = self.highlighted_names_group.category or self.highlighted_names_group.label

            if category != self.name and category != 'paula':  # TODO: this sucks
                return category

    @property
    def category_txt(self) -> Text | None:
        if self.name is None:
            return None
        elif self.category:
            return styled_category(self.category)
        elif self.is_a_mystery or self.is_uninteresting:
            return QUESTION_MARKS_TXT

    @property
    def email_conversation_length_in_days(self) -> int:
        return days_between(self.emails[0].timestamp, self.emails[-1].timestamp)

    @property
    def earliest_email_at(self) -> datetime:
        return self.emails[0].timestamp

    @property
    def earliest_email_date(self) -> date:
        return self.earliest_email_at.date()

    @property
    def last_email_at(self) -> datetime:
        return self.emails[-1].timestamp

    @property
    def last_email_date(self) -> date:
        return self.last_email_at.date()

    @property
    def emails_by(self) -> list[Email]:
        return [e for e in self.emails if self.name == e.author]

    @property
    def emails_to(self) -> list[Email]:
        return [
            e for e in self.emails
            if self.name in e.recipients or (self.name is None and len(e.recipients) == 0)
        ]

    @property
    def external_links_line(self) -> Text:
        links = [self.external_link_txt(site) for site in PERSON_LINK_BUILDERS]
        return Text('', justify='center', style='dim').append(join_texts(links, join=' / '))

    @property
    def has_any_epstein_emails(self) -> bool:
        """True if any emails sent to or received from Jeffrey Epstein."""
        contacts = [e.author for e in self.emails] + flatten([e.recipients for e in self.emails])
        return JEFFREY_EPSTEIN in contacts

    @property
    def highlight_group(self) -> HighlightedNames | HighlightedText | ManualHighlight | None:
        """Highlight group of any kind that matches this name."""
        if '_highlight_group' not in dir(self):
            self._highlight_group = get_highlight_group_for_name(self.name)

        return self._highlight_group

    @property
    def highlighted_names_group(self) -> HighlightedNames | None:
        """`HighlightedNames` (class with biographical info field) only."""
        if isinstance(self.highlight_group, HighlightedNames):
            return self.highlight_group

    @property
    def info_panel(self) -> Padding:
        """Return a `Panel` with the name of an emailer and a few tidbits of information about them."""
        style = 'white' if (not self.style() or self.style() == DEFAULT) else self.style()
        panel_style = f"black on {style} bold"

        if self.name == JEFFREY_EPSTEIN:
            email_count = len(self._printable_emails)
            title_suffix = f"sent by {JEFFREY_EPSTEIN} to himself"
        else:
            email_count = len(self.unique_emails)
            num_days = self.email_conversation_length_in_days
            title_suffix = f"{TO_FROM} {self.name_str} starting {self.earliest_email_date} covering {num_days:,} days"

        title = f"Found {email_count} emails {title_suffix}"
        width = max(MIN_AUTHOR_PANEL_WIDTH, len(title) + 4, len(self.info_with_category) + 8)
        panel = Panel(Text(title, justify='center'), width=width, style=panel_style)
        elements: list[RenderableType] = [panel]

        if self.info_with_category:
            elements.append(Text(f"({self.info_with_category})", justify='center', style=f"{style} italic"))

        return Padding(Group(*elements), (2, 0, 1, 0))

    @property
    def info_str(self) -> str | None:
        """Description of this person - name, configured biographical text, etc."""
        if self.name and self.highlighted_names_group:
            if (info := self.highlighted_names_group.info_for(self.name)):
                return info

        if self.is_uninteresting and len(self.emails_by) == 0:
            if self.has_any_epstein_emails:
                return UNINTERESTING_CC_INFO
            else:
                return UNINTERESTING_CC_INFO_NO_CONTACT

    @property
    def info_txt(self) -> Text | None:
        if self.name is None:
            return Text('(emails whose author or recipient could not be determined)', style=ALT_INFO_STYLE)
        elif self.name == JEFFREY_EPSTEIN:
            return Text('(emails sent by Epstein to himself are here)', style=ALT_INFO_STYLE)
        elif self.category == JUNK:
            return Text(f"({JUNK} mail)", style='bright_black dim')
        elif self.is_uninteresting and (self.info_str or '').startswith(UNINTERESTING_CC_INFO):
            if self.sole_cc:
                return Text(f"(cc: from {self.sole_cc} only)", style='wheat4 dim')
            elif self.info_str == UNINTERESTING_CC_INFO:
                return Text(f"({self.info_str})", style='wheat4 dim')
            else:
                return Text(f"({self.info_str})", style='plum4 dim')
        elif self.is_a_mystery:
            return Text(QUESTION_MARKS, style='honeydew2 bold')
        elif self.info_str is None:
            if self.name in MAILING_LISTS:
                return Text('(mailing list)', style=f"pale_turquoise4 dim")
            elif self.category:
                return Text(QUESTION_MARKS, style=self.style())
            else:
                return None
        else:
            return Text(self.info_str, style=self.style(allow_bold=False))

    @property
    def info_with_category(self) -> str:
        """Configured biographical info (if any) preceded by configured category (if any)."""
        return ', '.join(without_falsey([self.category, self.info_str]))

    @property
    def internal_link(self) -> Text:
        """Kind of like an anchor link to the section of the page containing these emails."""
        return link_text_obj(internal_person_link_url(self.name_str), self.name_str, style=self.style())

    @property
    def is_a_mystery(self) -> bool:
        """Return True if this is someone we theroetically could know more about."""
        return self.is_unstyled and not (self.is_email_address or self.info_str or self.is_uninteresting)

    @property
    def is_email_address(self) -> bool:
        return '@' in (self.name or '')

    @property
    def is_linkable(self) -> bool:
        """Return True if it's likely that EpsteinWeb has a page for this name."""
        if self.name is None or ' ' not in self.name:
            return False
        elif self.is_email_address or '/' in self.name or QUESTION_MARKS in self.name:
            return False
        elif self.name in INVALID_FOR_EPSTEIN_WEB:
            return False

        return True

    @property
    def is_unstyled(self) -> bool:
        """True if there's no highlight group for this name."""
        return self.style() == DEFAULT_NAME_STYLE

    @property
    def name_link(self) -> Text:
        """Will only link if it's worth linking, otherwise just a Text object."""
        if not self.is_linkable:
            return self.name_txt
        else:
            return Text.from_markup(link_markup(self.external_link(), self.name_str, self.style()))

    @property
    def name_str(self) -> str:
        return self.name or UNKNOWN

    @property
    def name_txt(self) -> Text:
        return styled_name(self.name)

    @property  # TODO: unused?
    def should_always_truncate(self) -> bool:
        """True if we want to truncate all emails to/from this user."""
        return self.name in TRUNCATE_EMAILS_BY or self.is_uninteresting

    @property
    def sole_cc(self) -> str | None:
        """Return name if this person sent 0 emails and received CC from only one that name."""
        email_authors = uniquify([e.author for e in self.emails_to])

        if len(self.unique_emails) == 1 and len(email_authors) > 0:
            logger.info(f"sole author of email to '{self.name}' is '{email_authors[0]}'")
        else:
            logger.info(f"'{self.name}' email_authors '{email_authors[0]}'")

        if len(self.unique_emails_by) > 0:
            return None

        if len(email_authors) == 1:
            return email_authors[0]

    @property
    def sort_key(self) -> list[int | str]:
        """Key used to sort `Person` objects by the number of emails sent/received."""
        counts = [
            len(self.unique_emails),
            -1 * int((self.info_str or '') == UNINTERESTING_CC_INFO_NO_CONTACT),
            -1 * int((self.info_str or '') == UNINTERESTING_CC_INFO),
            int(self.has_any_epstein_emails),
        ]

        counts = [-1 * count for count in counts]

        if args.sort_alphabetical:
            return [self.name_str] + counts
        else:
            return counts + [self.name_str]

    @property
    def unique_emails(self) -> Sequence[Email]:
        return Document.without_dupes(self.emails)

    @property
    def unique_emails_by(self) -> list[Email]:
        return Document.without_dupes(self.emails_by)

    @property
    def unique_emails_to(self) -> list[Email]:
        return Document.without_dupes(self.emails_to)

    @property
    def _printable_emails(self):
        """For Epstein we only want to print emails he sent to himself."""
        if self.name == JEFFREY_EPSTEIN:
            return [e for e in self.emails if e.is_note_to_self]
        else:
            return self.emails

    @property
    def _unique_printable_emails(self):
        return Document.without_dupes(self._printable_emails)

    def external_link(self, site: ExternalSite = EPSTEINIFY) -> str:
        return PERSON_LINK_BUILDERS[site](self.name_str)

    def external_link_txt(self, site: ExternalSite = EPSTEINIFY, link_str: str | None = None) -> Text:
        if self.name is None:
            return Text('')

        return link_text_obj(self.external_link(site), link_str or site, style=self.style())

    def print_emails(self) -> list[Email]:
        """Print complete emails to or from a particular 'author'. Returns the Emails that were printed."""
        print_centered(self.info_panel)
        self.print_emails_table()
        last_printed_email_was_duplicate = False

        if self.category == JUNK:
            logger.warning(f"Not printing junk emailer '{self.name}'")
        else:
            for email in self._printable_emails:
                if email.is_duplicate:
                    console.print(email.duplicate_file_txt_padded)
                    last_printed_email_was_duplicate = True
                else:
                    if last_printed_email_was_duplicate:
                        console.line()

                    console.print(email)
                    last_printed_email_was_duplicate = False

        return self._printable_emails

    def print_emails_table(self) -> None:
        """Print a table of this person's emails summary (timestamps, subject liness, etc)."""
        table = Email.build_emails_table(self._unique_printable_emails, self.name)
        print_centered(Padding(table, (0, 5, 0, 5)))

        if self.is_linkable:
            print_centered(self.external_links_line)

        console.line()

    def style(self, allow_bold: bool = True) -> str:
        return get_style_for_name(self.name, allow_bold=allow_bold)

    def __str__(self):
        return f"{self.name_str}"

    @staticmethod
    def emailer_info_table(
        people: list['Person'],
        highlighted: list['Person'] | None = None,
        show_epstein_total: bool = False
    ) -> Table:
        """
        Table of info about emailers.

        Args:
            people (list[Person]): Everyone who sent or received an email in the files.
            highlighted (list[Person], optional): Which emailers should be highlighted (rest will be dim).
            show_epstein_total (bool, optional): Whether to show total number of emails or just notes to self for Epstein himself.
        """
        highlighted = highlighted or people
        highlighted_names = [p.name for p in highlighted]
        is_selection = len(people) != len(highlighted) or args.emailers_info
        all_emails = Person.emails_from_people(people)
        email_authors = [p for p in people if p.emails_by and p.name]
        attributed_emails = [email for email in all_emails if email.author]
        footer = f"(identified {len(email_authors)} authors of {len(attributed_emails):,}" \
                 f" out of {len(all_emails):,} emails, {len(all_emails) - len(attributed_emails)} still unknown)"

        if is_selection:
            title = Text(f"{EMAILER_INFO_TITLE} for the Highlighted Names Only (", style=TABLE_TITLE_STYLE)
            title.append(THE_OTHER_PAGE_TXT).append(" has the rest)")
        else:
            title = f"{EMAILER_INFO_TITLE} in Chronological Order Based on Timestamp of First Email"

        table = build_table(title, caption=footer)
        table.add_column('First')
        table.add_column('Name', max_width=24, no_wrap=True)
        table.add_column('Category', justify='left', style='dim italic')
        table.add_column('Num', justify='right', style='white')
        table.add_column('Sent', justify='right', style='wheat4')
        table.add_column('Recv', justify='right', style='wheat4')
        table.add_column('Days', justify='right', style=TIMESTAMP_DIM)
        table.add_column('Info', style='white italic')
        current_year = 1990
        current_year_month = current_year * 12
        grey_idx = 0

        for person in people:
            earliest_email_date = person.earliest_email_date
            is_on_page = False if show_epstein_total else person.name in highlighted_names
            year_months = (earliest_email_date.year * 12) + earliest_email_date.month

            # Color year rollovers more brightly
            if current_year != earliest_email_date.year:
                grey_idx = 0
            elif current_year_month != year_months:
                grey_idx = ((current_year_month - 1) % 12) + 1

            current_year_month = year_months
            current_year = earliest_email_date.year

            table.add_row(
                Text(str(earliest_email_date), style=f"grey{GREY_NUMBERS[0 if is_selection else grey_idx]}"),
                person.internal_link if is_on_page and not person.is_uninteresting else person.name_txt,
                person.category_txt,
                f"{len(person.unique_emails if show_epstein_total else person._unique_printable_emails)}",
                str(len(person.unique_emails_by)) if len(person.unique_emails_by) > 0 else '',
                str(len(person.unique_emails_to)) if len(person.unique_emails_to) > 0 else '',
                f"{person.email_conversation_length_in_days}",
                person.info_txt or '',
                style='' if show_epstein_total or is_on_page else 'dim',
            )

        return table

    @staticmethod
    def emails_from_people(people: list['Person']) -> Sequence[Email]:
        """Collect all unique emails from a list of `Person` objects."""
        return Document.uniquify(flatten([list(p.unique_emails) for p in people]))
