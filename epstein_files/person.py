from dataclasses import dataclass, field
from datetime import datetime, date

from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document
from epstein_files.documents.email import JUNK_EMAILERS, KRASSNER_RECIPIENTS, Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import *
from epstein_files.util.data import days_between, flatten, without_falsey
from epstein_files.util.env import args
from epstein_files.util.highlighted_group import (QUESTION_MARKS_TXT, HighlightedNames,
     get_highlight_group_for_name, get_style_for_name, styled_category, styled_name)
from epstein_files.util.rich import GREY_NUMBERS, LAST_TIMESTAMP_STYLE, build_table, console, join_texts, print_centered

ALT_INFO_STYLE = 'medium_purple4'
MIN_AUTHOR_PANEL_WIDTH = 80
EMAILER_INFO_TITLE = 'Email Conversations Grouped by Counterparty Will Appear in this Order'

INVALID_FOR_EPSTEIN_WEB = JUNK_EMAILERS + KRASSNER_RECIPIENTS + [
    'ACT for America',
    'BS Stern',
    UNKNOWN,
]


@dataclass(kw_only=True)
class Person:
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
            category = highlight_group.category or highlight_group.label

            if category != self.name and category != 'paula':  # TODO: this sucks
                return category

    def category_txt(self) -> Text | None:
        if self.name is None:
            return None
        elif self.category():
            return styled_category(self.category())
        elif self.is_a_mystery():
            return QUESTION_MARKS_TXT

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
        return PERSON_LINK_BUILDERS[site](self.name_str())

    def external_link_txt(self, site: ExternalSite = EPSTEINIFY, link_str: str | None = None) -> Text:
        if self.name is None:
            return Text('')

        return link_text_obj(self.external_link(site), link_str or site, style=self.style())

    def external_links_line(self) -> Text:
        links = [self.external_link_txt(site) for site in PERSON_LINK_BUILDERS]
        return Text('', justify='center', style='dim').append(join_texts(links, join=' / '))  #, encloser='()'))#, encloser='‹›'))

    def highlight_group(self) -> HighlightedNames | None:
        return get_highlight_group_for_name(self.name)

    def info_panel(self) -> Padding:
        """Print a panel with the name of an emailer and a few tidbits of information about them."""
        style = 'white' if (not self.style() or self.style() == DEFAULT) else self.style()
        panel_style = f"black on {style} bold"

        if self.name == JEFFREY_EPSTEIN:
            email_count = len(self._printable_emails())
            title_suffix = f"sent by {JEFFREY_EPSTEIN} to himself"
        else:
            email_count = len(self.unique_emails())
            num_days = self.email_conversation_length_in_days()
            title_suffix = f"to/from {self.name_str()} starting {self.earliest_email_date()} covering {num_days:,} days"

        title = f"Found {email_count} emails {title_suffix}"
        width = max(MIN_AUTHOR_PANEL_WIDTH, len(title) + 4, len(self.info_with_category()) + 8)
        panel = Panel(Text(title, justify='center'), width=width, style=panel_style)
        elements: list[RenderableType] = [panel]

        if self.info_with_category():
            elements.append(Text(f"({self.info_with_category()})", justify='center', style=f"{style} italic"))

        return Padding(Group(*elements), (2, 0, 1, 0))

    def info_str(self) -> str | None:
        highlight_group = self.highlight_group()

        if highlight_group and isinstance(highlight_group, HighlightedNames) and self.name:
            return highlight_group.info_for(self.name)

    def info_with_category(self) -> str:
        return ', '.join(without_falsey([self.category(), self.info_str()]))

    def info_txt(self) -> Text | None:
        if self.name == JEFFREY_EPSTEIN:
            return Text('(emails sent by Epstein to himself are here)', style=ALT_INFO_STYLE)
        elif self.name is None:
            return Text('(emails whose author or recipient could not be determined)', style=ALT_INFO_STYLE)
        elif self.category() == JUNK:
            return Text(f"({JUNK} mail)", style='tan dim')
        elif self.is_a_mystery():
            return Text(QUESTION_MARKS, style='grey50 dim')
        elif self.info_str() is None:
            return None
        else:
            return Text(self.info_str())

    def is_a_mystery(self) -> bool:
        """Return True if this is someone we theroetically could know more about."""
        return self.is_unstyled() and not self.is_email_address() and not self.info_str()

    def is_email_address(self) -> bool:
        return '@' in (self.name or '')

    def is_linkable(self) -> bool:
        """Return True if it's likely that EpsteinWeb has a page for this name."""
        if self.name is None or ' ' not in self.name:
            return False
        elif self.is_email_address() or '/' in self.name or QUESTION_MARKS in self.name:
            return False
        elif self.name in INVALID_FOR_EPSTEIN_WEB:
            return False

        return True

    def is_unstyled(self) -> bool:
        """True if there's no highlight group for this name."""
        return self.style() == DEFAULT_NAME_STYLE

    def name_str(self) -> str:
        return self.name or UNKNOWN

    def name_link(self) -> Text:
        """Will only link if it's worth linking, otherwise just a Text object."""
        if not self.is_linkable():
            return self.name_txt()
        else:
            return Text.from_markup(link_markup(self.external_link(), self.name_str(), self.style()))

    def name_txt(self) -> Text:
        return styled_name(self.name)

    def print_emails(self) -> list[Email]:
        """Print complete emails to or from a particular 'author'. Returns the Emails that were printed."""
        print_centered(self.info_panel())
        self.print_emails_table()
        last_printed_email_was_duplicate = False

        if self.category() == JUNK:
            logger.warning(f"Not printing junk emailer '{self.name}'")
        else:
            for email in self._printable_emails():
                if email.is_duplicate():
                    console.print(Padding(email.duplicate_file_txt().append('...'), (0, 0, 0, 4)))
                    last_printed_email_was_duplicate = True
                else:
                    if last_printed_email_was_duplicate:
                        console.line()

                    console.print(email)
                    last_printed_email_was_duplicate = False

        return self._printable_emails()

    def print_emails_table(self) -> None:
        emails = [email for email in self._printable_emails() if not email.is_duplicate()]  # Remove dupes
        print_centered(Padding(Email.build_emails_table(emails, self.name), (0, 5, 0, 5)))

        if self.is_linkable():
            print_centered(self.external_links_line())

        console.line()

    def sort_key(self) -> list[int | str]:
        counts = [len(self.unique_emails())]
        counts = [-1 * count for count in counts]

        if args.sort_alphabetical:
            return [self.name_str()] + counts
        else:
            return counts + [self.name_str()]

    def style(self) -> str:
        return get_style_for_name(self.name)

    def unique_emails(self) -> list[Email]:
        return [email for email in self.emails if not email.is_duplicate()]

    def unique_emails_by(self) -> list[Email]:
        return [email for email in self.emails_by() if not email.is_duplicate()]

    def unique_emails_to(self) -> list[Email]:
        return [email for email in self.emails_to() if not email.is_duplicate()]

    def _printable_emails(self):
        """For Epstein we only want to print emails he sent to himself."""
        if self.name == JEFFREY_EPSTEIN:
            return [e for e in self.emails if e.is_note_to_self()]
        else:
            return self.emails

    def __str__(self):
        return f"{self.name_str()}"

    @staticmethod
    def emailer_info_table(people: list['Person']) -> Table:
        is_addendum = len(people) > 100

        """Table of info about emailers."""
        if args.all_emails:
            title = EMAILER_INFO_TITLE
        else:
            if is_addendum:
                title = None
            else:
                title = f"Selected {EMAILER_INFO_TITLE}"

        table = build_table(title)
        table.add_column('Start')
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
            earliest_email_date = person.earliest_email_date()
            year_months = (earliest_email_date.year * 12) + earliest_email_date.month

            # Color year rollovers more brightly
            if current_year != earliest_email_date.year:
                grey_idx = 0
            elif current_year_month != year_months:
                grey_idx = ((current_year_month - 1) % 12) + 1

            current_year_month = year_months
            current_year = earliest_email_date.year

            table.add_row(
                Text(str(earliest_email_date), style=f"grey{GREY_NUMBERS[grey_idx if is_addendum or args.all_emails else 0]}"),
                person.name_txt(),  # TODO: make link?
                person.category_txt(),
                f"{len(person._printable_emails())}",
                f"{len(person.unique_emails_by())}",
                f"{len(person.unique_emails_to())}",
                f"{person.email_conversation_length_in_days()}",
                person.info_txt() or '',
            )

        return table

    @staticmethod
    def emailer_stats_table(people: list['Person']) -> Table:
        email_authors = [p for p in people if p.emails_by() and p.name]
        all_emails = Document.uniquify(flatten([p.unique_emails() for p in people]))
        attributed_emails = [email for email in all_emails if email.author]
        footer = f"(identified {len(email_authors)} authors of {len(attributed_emails):,}"
        footer = f"{footer} out of {len(attributed_emails):,} emails)"

        counts_table = build_table(
            f"All {len(email_authors)} People Who Sent or Received an Email in the Files",
            caption=footer,
            cols=[
                'Name',
                {'name': 'Count', 'justify': 'right', 'style': 'bold bright_white'},
                {'name': 'Sent', 'justify': 'right', 'style': 'gray74'},
                {'name': 'Recv', 'justify': 'right', 'style': 'gray74'},
                {'name': 'First', 'style': TIMESTAMP_STYLE},
                {'name': 'Last', 'style': LAST_TIMESTAMP_STYLE},
                {'name': 'Days', 'justify': 'right', 'style': 'dim'},
                JMAIL,
                EPSTEIN_MEDIA,
                EPSTEIN_WEB,
                'Twitter',
            ]
        )

        for person in sorted(people, key=lambda person: person.sort_key()):
            counts_table.add_row(
                person.name_link(),
                f"{len(person.unique_emails()):,}",
                f"{len(person.unique_emails_by()):,}",
                f"{len(person.unique_emails_to()):,}",
                str(person.earliest_email_date()),
                str(person.last_email_date()),
                f"{person.email_conversation_length_in_days()}",
                person.external_link_txt(JMAIL),
                person.external_link_txt(EPSTEIN_MEDIA) if person.is_linkable() else '',
                person.external_link_txt(EPSTEIN_WEB) if person.is_linkable() else '',
                person.external_link_txt(TWITTER),
            )

        return counts_table
