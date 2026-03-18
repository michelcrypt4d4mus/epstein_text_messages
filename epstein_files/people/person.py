import logging
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Sequence, Self

from rich.align import Align
from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import Document
from epstein_files.documents.documents.categories import Uninteresting
from epstein_files.documents.documents.doc_types_mixin import DocTypesMixin
from epstein_files.documents.email import BCC_LISTS, TRUNCATE_EMAILS_BY, MAILING_LISTS, Email
from epstein_files.documents.emails.emailers import ENTITIES_DICT, cleanup_str, get_entity
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import (HIGHLIGHTED_NAMES, QUESTION_MARKS_TXT, get_highlight_group_for_name,
     get_style_for_name, styled_category, styled_name)
from epstein_files.output.highlighted_names import HighlightedNames, HighlightPatterns, ManualHighlight
from epstein_files.output.layout_elements.file_display import FileDisplay
from epstein_files.output.rich import GREY_NUMBERS, TABLE_TITLE_STYLE, build_table, console, print_special_note
from epstein_files.output.site.internal_links import TO_FROM
from epstein_files.people.entity import Entity
from epstein_files.people.interesting_people import SPECIAL_NOTES
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import *
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import days_between, flatten, uniquify, without_falsey
from epstein_files.util.external_link import join_texts
from epstein_files.util.logging_entity import LoggingEntity

ALT_INFO_STYLE = 'medium_purple4'
CC = 'cc:'
MAX_NAME_COL_WIDTH = 24
MAX_INFO_COL_WIDTH = len("Epstein's Russian assistant who was recommended for a visa by Sergei Belyakov")
MIN_AUTHOR_PANEL_WIDTH = 80
EMAILER_INFO_TITLE = 'Email Conversations Will Appear'
UNINTERESTING_CC_INFO = "cc: or bcc: recipient only"
UNINTERESTING_CC_INFO_NO_CONTACT = f"{UNINTERESTING_CC_INFO}, no direct contact with Epstein"

# TODO: get rid of this
PEOPLE_BIOS = {
    contact.name: contact.bio_txt
    for highlighted_group in HIGHLIGHTED_NAMES
    for contact in highlighted_group.contacts
    if contact.has_bio
}


@dataclass
class Person(DocTypesMixin, LoggingEntity):
    """
    Collects all known info and files connected to someone who is the author or recipient
    of at least one Epstein File with methods to work with that collection as a whole.
    """
    name: Name = None
    is_interesting: bool | None = None
    entity: Entity = field(init=False)  # TODO: rename 'entity'
    _searched_for_highlight_group: bool = False

    def __post_init__(self):
        self.entity = get_entity(self.name_str)
        self._documents = Document.sort_by_timestamp(self.documents)

    @property
    def biography_txt(self) -> Text | None:
        if self.info_with_category:
            return Text(f"({self.info_with_category})", justify='center', style=f"{self._email_info_style} italic")

    @property
    def category(self) -> str | None:
        """Categories are configured with the `HighlightedGroups`."""
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
        elif self.is_a_mystery or self.is_interesting is False:
            return QUESTION_MARKS_TXT

    @property
    def counterparties(self) -> list[Name]:
        """All text and email counterparties for this person."""
        all_counterparties = flatten([c.participants for c in self.communications])
        return sort_names([c for c in all_counterparties if c != self.name])

    @property
    def full_info_panel(self) -> Padding:
        """Return a `Group` with the name of an emailer and a few tidbits of information about them below."""
        elements: list[RenderableType] = [self.email_info_panel()]

        if self.biography_txt:
            elements.append(self.biography_txt)

        return Padding(Group(*elements), (2, 0, 1, 0))

    @property
    def email_conversation_length_in_days(self) -> int:
        """Number of days between earliest and most recent emails."""
        return days_between(self.emails[0].timestamp, self.emails[-1].timestamp)

    @property
    def emails_by(self) -> list[Email]:
        """Emails written by this person."""
        return [e for e in self.emails if self.name == e.author]

    @property
    def emails_to(self) -> list[Email]:
        """Emails sent to this person."""
        return [
            e for e in self.emails
            if self.name in e.recipients or (self.name is None and len(e.recipients) == 0)
        ]

    @property
    def has_any_epstein_emails(self) -> bool:
        """True if any emails sent to or received from Jeffrey Epstein."""
        contacts = [e.author for e in self.emails] + flatten([e.recipients for e in self.emails])
        return JEFFREY_EPSTEIN in contacts

    @property
    def highlight_group(self) -> HighlightedNames | HighlightPatterns | ManualHighlight | None:
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
    def info_str(self) -> str | None:
        """Description of this person - name, configured biographical text, etc."""
        if self.name and self.highlighted_names_group:
            if (info := self.highlighted_names_group.info_for(self.name)):
                return info

        # A person who wrote no emails stil might be interesting if they received email directly from Epstein
        if self.is_interesting is False and len(self.emails_by) == 0:
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
        elif self.category == Uninteresting.JUNK:
            return Text(f"({Uninteresting.JUNK} mail)", style='bright_black dim')
        elif self.is_interesting is False and (self.info_str or '').startswith(UNINTERESTING_CC_INFO):
            if self.sole_cc_author:
                return Text(f"(cc: from {self.sole_cc_author} only)", style='wheat4 dim')
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
        return self.is_unstyled and not (self.entity.is_email_address or self.info_str or self.is_interesting is False)

    @property
    def is_unstyled(self) -> bool:
        """True if there's no highlight group for this name."""
        return self.style() == DEFAULT_NAME_STYLE

    @property
    def name_str(self) -> str:
        return self.name or UNKNOWN

    @property
    def name_txt(self) -> Text:
        return styled_name(self.name)

    @property
    def other_files_shown_with_emails(self) -> list[OtherFile]:
        """OtherFile objects that should be displayed in the emails section(s)."""
        return [f for f in self.other_files if self.name == f._config.show_with_name]

    @property  # TODO: unused?
    def should_always_truncate(self) -> bool:
        """True if we want to truncate all emails to/from this user."""
        return self.name in TRUNCATE_EMAILS_BY or self.is_interesting is False

    @property
    def sole_cc_author(self) -> str | None:
        """Return a name if this person sent 0 emails (total) and received CCs from only that one name."""
        email_authors = uniquify([e.author for e in self.emails_to])

        if self.num_emails == 1 and len(email_authors) > 0:
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
            self.num_emails,
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
    def unique_emails_by(self) -> list[Email]:
        return Document.without_dupes(self.emails_by)

    @property
    def unique_emails_to(self) -> list[Email]:
        return Document.without_dupes(self.emails_to)

    @property
    def _email_info_style(self) -> str:
        return 'white' if (not self.style() or self.style() == DEFAULT) else self.style()

    @property
    def _identifier(self) -> str:
        """`LoggingEntity` mixin."""
        return self.name_str

    @property
    def _printable_emails(self):
        """For Epstein we only want to print emails he sent to himself."""
        if self.name == JEFFREY_EPSTEIN:
            return [e for e in self.emails if e.is_note_to_self()]
        else:
            return self.emails

    @property
    def _unique_printable_emails(self):
        return Document.without_dupes(self._printable_emails)

    def email_info_panel(self) -> Panel:
        """Just the person's name on the colored background with email counts."""
        if self.name == JEFFREY_EPSTEIN:
            email_count = len(self._printable_emails)
            title_suffix = f"sent by {JEFFREY_EPSTEIN} to himself"
        else:
            email_count = self.num_emails
            num_days = self.email_conversation_length_in_days
            title_suffix = f"{TO_FROM} {self.name_str} starting {self.earliest_email_date} covering {num_days:,} days"

        title = f"Found {email_count} emails {title_suffix}"
        width = max(MIN_AUTHOR_PANEL_WIDTH, len(title) + 4, len(self.info_with_category) + 8)
        panel_style = f"black on {self._email_info_style} bold"
        return Panel(Text(title, justify='center'), width=width, style=panel_style)

    def print_emails(self, printer: 'DocPrinter') -> list[Email]:
        """
        Print complete emails to or from a particular 'author' along with any specially marked docs
        configured with `show_with_name` of this user. Returns the Emails that were printed.
        """
        printer.print_centered(self.email_info_panel())

        if self.biography_txt:
            printer.print_centered(self.biography_txt)

        printer.line()

        if site_config.show_emailer_tables:
            printer.print_centered(self._emails_table())

        if self.category == Uninteresting.JUNK:
            logger.warning(f"Not printing junk emailer '{self.name}'")  # Junk emailers only get a table
            return self._printable_emails
        elif self.name in SPECIAL_NOTES:
            # TODO: DocPrinter doesn't render HTML for the special notes
            print_special_note(SPECIAL_NOTES[self.name])

        docs = Document.sort_by_timestamp(self._printable_emails + self.other_files_shown_with_emails)
        docs = [d.file_display(align='right') if isinstance(d, OtherFile) else d for d in docs]   # TODO this sucks

        # TODO this sucks
        for d in docs:
            if isinstance(d, FileDisplay):
                d.indent = site_config.show_with_indent

        printer.print_documents(docs, log_sfx=f"[{self.name}]")
        printer.line(2)
        return self._printable_emails  # TODO: doesn't return FileDisplay objects that may have also been printed!

    def style(self, allow_bold: bool = True) -> str:
        return get_style_for_name(self.name, allow_bold=allow_bold)

    def _emails_table(self) -> Align | Padding:
        """Build a table of this person's emails summary (timestamps, subject liness, etc)."""
        # TODO: i don't think captions render in custom HTML correctly
        caption = self.entity.epstein_sites_all_links if self.entity.is_linkable else None
        table = Email.build_emails_table(self._unique_printable_emails, self.name, caption=caption)
        padded_table = Padding(table, (0, 5, 0, 5))
        logger.debug(f"built emails table for '{self.name}' with {len(table.columns)} cols and {table.row_count} rows")
        return padded_table

    def __str__(self):
        return f"{self.name_str}"

    @classmethod
    def emailer_info_table(
        cls,
        people: list[Self],
        highlighted: list[Self] | None = None,
        show_epstein_total: bool = False  # TODO: this sucks
    ) -> Table:
        """
        Table of info about people's emails.

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

        if is_selection:
            title = Text(f"{EMAILER_INFO_TITLE} for the Highlighted Names Only (", style=TABLE_TITLE_STYLE)
            title.append(THE_OTHER_PAGE_TXT).append(" has the rest)")
        else:
            title = f"{EMAILER_INFO_TITLE} in Chronological Order Based on Timestamp of First Email"

        footer = f"(identified {len(email_authors)} authors of {len(attributed_emails):,}" \
                 f" out of {len(all_emails):,} emails, {len(all_emails) - len(attributed_emails)} still unknown"

        if args.all_emails:
            footer += ')'
        else:
            num_uninteresting = len([p for p in people if p.is_interesting is False])
            footer += f". {num_uninteresting} uninteresting people not shown, check all emails page for details)"

        table = build_table(title, caption=footer)
        table.add_column('First')
        table.add_column('Name', max_width=MAX_NAME_COL_WIDTH, no_wrap=True)
        table.add_column('Category', justify='left', style='dim italic')
        table.add_column('Num', justify='right', style='white')
        table.add_column('Sent', justify='right', style='wheat4')
        table.add_column('Recv', justify='right', style='wheat4')
        table.add_column('Days', justify='right', style=TIMESTAMP_DIM)
        table.add_column('Info', style='white italic', max_width=MAX_INFO_COL_WIDTH)
        current_year = 1990
        current_year_month = current_year * 12
        grey_idx = 0

        for person in people:
            if person.is_interesting is False and not (args.emailers_info or args.all_emails):
                continue

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
                person.internal_link if is_on_page and person.is_interesting is not False else person.name_txt,
                person.category_txt,
                f"{len(person.unique_emails if show_epstein_total else person._unique_printable_emails)}",
                str(len(person.unique_emails_by)) if len(person.unique_emails_by) > 0 else '',
                str(len(person.unique_emails_to)) if len(person.unique_emails_to) > 0 else '',
                f"{person.email_conversation_length_in_days}",
                person.info_txt or '',
                style='' if show_epstein_total or is_on_page else 'dim',
            )

        if args.mobile:
            new_table = build_table(table.title, copy_props_from=table)
            new_table.add_column(table.columns[1].header)
            new_table.add_column(table.columns[2].header)

            for i, row in enumerate(table.rows):
                new_table.add_row(table.columns[1]._cells[i], table.columns[2]._cells[i])

            return new_table

        return table

    @staticmethod
    def emails_from_people(people: list['Person']) -> Sequence[Email]:
        """Collect all unique emails from a list of `Person` objects."""
        return Document.uniquify(flatten([list(p.unique_emails) for p in people]))
