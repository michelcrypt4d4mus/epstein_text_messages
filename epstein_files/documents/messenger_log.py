import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from rich.console import Console, ConsoleOptions, NewLine, RenderResult
from rich.table import Table
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.documents.doc_cfg import Metadata
from epstein_files.documents.imessage.text_message import TextMessage
from epstein_files.output.highlight_config import styled_name
from epstein_files.output.rich import LAST_TIMESTAMP_STYLE, build_table, highlighter
from epstein_files.people.interesting_people import PERSONS_OF_INTEREST
from epstein_files.util.constant.names import JEFFREY_EPSTEIN, Name
from epstein_files.util.constant.strings import AUTHOR, TIMESTAMP_STYLE
from epstein_files.util.helpers.data_helpers import days_between, days_between_str, sort_dict
from epstein_files.util.helpers.string_helper import iso_timestamp
from epstein_files.util.logging import logger

CONFIRMED_MSG = 'with confirmed counterparty'
GUESSED_MSG = 'and is probably with'
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
REDACTED_AUTHOR_REGEX = re.compile(r"^([-+•_1MENO.=F]+|[4Ide])$")


@dataclass
class MessengerLog(Communication):
    """
    Class representing one iMessage log file (one conversation between Epstein and some counterparty).
    """
    messages: list[TextMessage] = field(default_factory=list)
    phone_number: str | None = None

    def __post_init__(self):
        super().__post_init__()
        self.messages = [self._build_message(match) for match in MSG_REGEX.finditer(self.text)]

    @property
    def is_interesting(self) -> bool | None:
        """Junk emails are not interesting."""
        if (is_interesting := super().is_interesting) is not None:
            return is_interesting
        elif self.author is None or self.author in PERSONS_OF_INTEREST:
            return True

    @property
    def metadata(self) -> Metadata:
        metadata = super().metadata
        metadata.update({'num_messages': len(self.messages)})

        if self.phone_number:
            metadata['phone_number'] = self.phone_number

        return metadata

    @property
    def subheader(self) -> Text | None:
        num_days_str = days_between_str(self.timestamp, self.messages[-1].parse_timestamp())
        txt = Text(f"(Covers {num_days_str} starting ", style='dim')
        txt.append(self.date_str, style=TIMESTAMP_STYLE).append(' ')

        if not self.author:
            txt.append('with unknown counterparty')
        else:
            txt.append(GUESSED_MSG if self.is_attribution_uncertain else CONFIRMED_MSG).append(' ')
            txt.append(Text(self.author, style=self.author_style + ' bold'))

        if self.phone_number:
            txt.append(highlighter(f" using the phone number {self.phone_number}"))

        return txt.append(')')

    def first_message_at(self, name: Name) -> datetime:
        return self.messages_by(name)[0].parse_timestamp()

    def last_message_at(self, name: Name) -> datetime:
        return self.messages_by(name)[-1].parse_timestamp()

    def messages_by(self, name: Name) -> list[TextMessage]:
        """Return all messages by 'name'."""
        return [m for m in self.messages if m.author == name]

    def _build_message(self, match: re.Match) -> TextMessage:
        """Turn a regex match into a `TextMessage`."""
        author_str = REDACTED_AUTHOR_REGEX.sub('', match.group(1).strip())
        is_phone_number = author_str.startswith('+')

        if is_phone_number:
            logger.info(f"{self.summary} Found phone number: {author_str}")
            self.phone_number = author_str

        # If the Sender: is redacted or if it's an unredacted phone number that means it's from self.author
        return TextMessage(
            author=self.author if (is_phone_number or not author_str) else author_str,
            author_str=author_str if is_phone_number else '',  # Preserve phone numbers
            is_id_confirmed=not self.is_attribution_uncertain,
            text=match.group(4).strip(),
            timestamp_str=match.group(2).strip(),
        )

    def _extract_recipients(self) -> list[Name]:
        return [JEFFREY_EPSTEIN]

    def _extract_timestamp(self) -> datetime:
        for match in MSG_REGEX.finditer(self.text):
            message = self._build_message(match)

            try:
                return message.parse_timestamp()
            except ValueError as e:
                logger.info(f"Failed to parse '{message.timestamp_str}' to datetime! Using next match. Error: {e}'")

        raise RuntimeError(f"{self}: No timestamp found!")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield self.file_info_panel()
        yield NewLine()

        for message in self.messages:
            yield message

        yield NewLine()

    @classmethod
    def count_authors(cls, imessage_logs: list['MessengerLog']) -> dict[Name, int]:
        """Count up how many texts were sent by each author."""
        sender_counts: dict[Name, int] = defaultdict(int)

        for message_log in imessage_logs:
            for message in message_log.messages:
                sender_counts[message.author] += 1

        return sender_counts

    @classmethod
    def summary_table(cls, log_files: list['MessengerLog']) -> Table:
        """Build a table summarizing the text messages in 'imessage_logs'."""
        author_counts = cls.count_authors(log_files)
        msg_count = sum([len(log.messages) for log in log_files])

        footer = f"deanonymized {msg_count - author_counts[None]:,} of {msg_count:,} text messages in"
        counts_table = build_table("Text Message Counts By Author", caption=f"({footer} {len(log_files)} files)")
        counts_table.add_column(AUTHOR.title(), justify='left', width=30)
        counts_table.add_column('Files', justify='right', style='white')
        counts_table.add_column("Msgs", justify='right')
        counts_table.add_column('First Sent At', justify='center', highlight=True)
        counts_table.add_column('Last Sent At', justify='center', style=LAST_TIMESTAMP_STYLE)
        counts_table.add_column('Days', justify='right', style='dim')

        for name, count in sort_dict(author_counts):
            logs = log_files if name == JEFFREY_EPSTEIN else [log for log in log_files if log.author == name]
            first_at = logs[0].first_message_at(name)
            last_at = logs[-1].first_message_at(name)

            counts_table.add_row(
                styled_name(name),
                str(len(logs)),
                f"{count:,}",
                iso_timestamp(first_at),
                iso_timestamp(last_at),
                str(days_between(first_at, last_at)),
            )

        return counts_table
