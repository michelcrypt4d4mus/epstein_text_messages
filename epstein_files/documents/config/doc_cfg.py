import json
from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Literal, Self, Sequence

from dateutil import tz
from dateutil.parser import parse
from rich.text import Text

from epstein_files.documents.documents.categories import (Category, Interesting, Neutral, Uninteresting,
     is_category, is_interesting, is_uninteresting)
from epstein_files.people.interesting_people import PERSONS_OF_INTEREST
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import CharRange, coerce_utc_strict, without_falsey
from epstein_files.util.helpers.file_helper import is_doj_file
from epstein_files.util.helpers.link_helper import ExternalLink
from epstein_files.util.helpers.string_helper import collapse_whitespace, is_bool_prop, join_truthy, quote
from epstein_files.util.logging import logger
from epstein_files.util.logging_entity import LoggingEntity

DebugDict = dict[str, bool | datetime | set | str | Path | None]
DuplicateType = Literal['bounced', 'earlier', 'quoted', 'redacted', 'same']
Metadata = dict[str, bool | datetime | int | str | None | list[str | None] | dict[str, bool | str]]

DEFAULT_TRUNCATE_TO = 4000
SHORT_TRUNCATE_TO = int(DEFAULT_TRUNCATE_TO / 3)
NO_TRUNCATE = -1
SAME = 'same'

MAX_REPR_LINE_LENGTH = 135
GOLDMAN_INVESTMENT_MGMT = f'{GOLDMAN_SACHS} Investment Management Division'
ZUBAIR_AND_ANYA = f"{ZUBAIR_KHAN} and Anya Rasulova"

# Authors of financial report pablum
FINANCIAL_REPORTS_AUTHORS = [
    BOFA_MERRILL,
    DEUTSCHE_BANK,
    ELECTRON_CAPITAL_PARTNERS,
    GOLDMAN_INVESTMENT_MGMT,
    'Invesco',
    JP_MORGAN,
    'Morgan Stanley',
    'S&P',
]

# Description prefixes we are uninterested in
UNINTERESTING_PREFIXES = [
    'article about',
    CVRA,
    f"{HARVARD} Econ",
    HARVARD_POETRY,
    JASTA,
    LEXIS_NEXIS,
    PALM_BEACH_TSV,
    'US Office',
]

DUPE_TYPE_STRS: dict[DuplicateType, str] = {
    'bounced': 'a bounced copy of',
    'earlier': 'an earlier draft of',
    'quoted': 'quoted in full in',
    'redacted': 'a redacted version of',
    SAME: 'the same as',
}

# only used to order fields in metadtaa and repr()
FIELD_SORT_KEY = {
    'id': 'a',
    AUTHOR: 'aa',
    'comment': 'zz',
    'duplicate_ids': 'dup',
    'duplicate_of_id': 'dupe',
    'recipients': 'aaa',
}

# Fields like timestamp and author are better added from the Document object
NON_METADATA_FIELDS = [
    'actual_text',
    'id',
    'is_synthetic',
    'display_text',
]

# Categories where we want to include the category name at start of the description string
CATEGORY_PREAMBLES = {
    Interesting.DIARY: VICTIM_DIARY,
    Interesting.LETTER: 'letter',
    Interesting.REPUTATION: REPUTATION_MGMT,
    Interesting.TEXT_MSG: 'text message',
    Neutral.DEPOSITION: 'deposition of',
    Neutral.FLIGHT_LOG: Neutral.FLIGHT_LOG.replace('_', ' '),
    Neutral.PRESSER: Neutral.PRESSER.replace('_', ' '),
    Neutral.RESUMÉ: 'professional resumé',
    Neutral.SKYPE_LOG: Neutral.SKYPE_LOG.replace('_', ' '),
    Uninteresting.BOOK: 'book titled',
    Uninteresting.TWEET: Uninteresting.TWEET.title(),
}

SHORT_TRUNCATE_CATEGORIES = [
    Uninteresting.ARTICLE,
]


@dataclass(kw_only=True)
class DocCfg(LoggingEntity):
    """
    Encapsulates info about files that needs to be manually configured because it cannot be programmatically inferred.
    Setting the `is_interesting` flag overrides all other considerations when determining a document's
    interestingness (or lack thereof) and also has the additional side effect of causing the entire file to be
    printed (it's the equivalent of setting truncate_to=NO_TRUNCATE).

    Attributes:
        id (str): ID of file
        attached_to_email_id (str, optional): ID of `Email` object this document was an attachment of
        author (Name): Author of the document (if any)
        author_reason (str, optional): Optional explanation of why we are sure this email can be attributed to this author
        author_uncertain (str | bool, optional): Like `author_reason` but for author attributions that aren't 100% confirmed
        background_color (str, optional): set `is_interesting=True` and show in full panel with background color
        category (str, optional): Type of file
        comment (str, optional): Info about this file not worth being in the description
        date (str, optional): Parsed to a datetime by timestamp() if it exists
        display_text (str, optional): Replace the contents of this file with this string when it's displayed
        dupe_type (DuplicateType | None): The type of duplicate this file is or its 'duplicate_ids' are
        duplicate_ids (list[str]): IDs of *other* documents that are dupes of this document
        duplicate_of_id (str | None): If this is a dupe the ID of the duplicated file. This file will be suppressed
        highlight_quote (str, optional): text to highlight, also triggers `is_of_interest` and `show_full_panel` to True
        is_interesting (bool | None): Override other considerations and always consider this file interesting (or not)
        is_in_chrono (bool | None): Like is_interesting, but only applies with --output-chrono
        is_synthetic (bool): True if this config was generated by the `duplicate_cfgs()` method
        is_valid_for_name_scan (bool): should text of this doc be scanned for names to create biographical panels
        non_participants (list[str]): hacky way to avoid false detection of these names
        num_preview_chars (int, optional): customize number of preview_chars shown in `OtherFile` tables
        people (list[str]): override `Document.people()` with a fixed set of names (meaning no scan of the text)
        show_full_panel (bool, optional): set `is_interesting=True` and show in a full panel view, not in a table
        show_with_name (str, optional): if set this document will be displayed all with the person specified
        truncate_to (int | tuple[int, int], optional): Number of characters to truncate this email to when displayed
        url (str, optional): URL with more info about this document
        url_link_text (str, optiona): text to show when displaying the `url` link for this document
    """
    id: str
    attached_to_email_id: str | None = None
    author: Name = None
    author_reason: str = ''
    author_uncertain: bool | str = ''
    background_color: str = ''
    category: str = ''
    comment: str = ''
    date: str = ''
    date_uncertain: str | bool = False
    description: str = ''
    display_text: str = ''
    dupe_type: DuplicateType | None = None
    duplicate_ids: list[str] = field(default_factory=list)
    duplicate_of_id: str | None = None
    highlight_quote: str = ''
    is_interesting: bool | None = None  # NOTE: if True emails will not be truncated!
    is_in_chrono: bool | None = None
    is_synthetic: bool | None = None
    is_valid_for_name_scan: bool = True
    non_participants: list[str] = field(default_factory=list)  # TODO: this sucks
    num_preview_chars: int | None = None
    people: list[str] = field(default_factory=list)
    show_full_panel: bool = False
    show_with_name: str = ''
    truncate_to: int | tuple[int, int] | None = None
    url: str = ''
    url_link_text: str = ''

    def __post_init__(self):
        if self.id in self.duplicate_ids:
            raise ValueError(f"{self.id} is a duplicate of itself!")
        elif 'efta' in self.id:
            self._warn(f"id should not be lowercase: '{self.id}'")
            self.id = self.id.upper()

        self.set_category(self.category)

        if self.highlight_quote:
            description_quote = collapse_whitespace(self.highlight_quote.replace('>', ''))
            self.description = join_truthy(self.description, f'quote of interest: {quote(description_quote)}', ', ')
            self.show_full_panel = True

        if self.background_color:
            self.show_full_panel = True

        if self.show_full_panel:
            self.is_interesting = True

        if self.duplicate_of_id or self.duplicate_ids:
            self.dupe_type = self.dupe_type or SAME

    @classmethod
    def describe(cls, id: str, description: str, **kwargs) -> Self:
        """Alternate constructor for a config with a description."""
        # TODO: VScode find / replace expression attempts to update DocCfg objs to use this method
        # TODO: find expression: (Doc|Email)Cfg\(id=('\w+'), description=(f?'.*?')\),
        # TODO:         replace: $1Cfg.describe($2, $3),
        return cls(id=id, description=description, **kwargs)

    @property
    def author_str(self) -> str:
        return self.author or ''

    @property
    def category_txt(self) -> Text:
        """Returns '???' for missing category."""
        from epstein_files.output.highlight_config import styled_category
        return styled_category(self.category)

    @property
    def char_range(self) -> CharRange | None:
        """`truncate_to` as `(0, truncate_to)` tuple if truncate_to is an `int`."""
        if args.whole_file or self.truncate_at in [None, NO_TRUNCATE]:
            return None
        elif isinstance(self.truncate_at, tuple):
            return self.truncate_at
        elif isinstance(self.truncate_at, int):
            return (0, self.truncate_at)
        else:
            raise ValueError(f"{self.id} unknown truncate_at type ({type(self.truncate_at).__name__}, value={self.truncate_at})")

    @property
    def complete_description(self) -> str:
        """String that summarizes what is known about this document."""
        author = f"{self.author} {QUESTION_MARKS}" if self.author and self.author_uncertain else self.author
        preamble = CATEGORY_PREAMBLES.get(self.category, '')
        preamble_separator = ''
        author_separator = ''
        description = ''

        # If description is set at all in one of these if/else checks must be fully constructed
        if self.display_text and not self.description:
            return ''
        if self.category == Uninteresting.BOOK or \
                (self.category == Uninteresting.ACADEMIA and self.author and self.description):
            description = join_truthy(self.description, author, ' by ')  # note reversed args
            description = join_truthy(preamble, description)
        elif self.category == Neutral.FINANCE and self.is_description_a_title:
            author_separator = ' report: '
        elif self.category in [Interesting.LETTER, Interesting.TEXT_MSG, Neutral.SKYPE_LOG]:
            recipients = self.recipients_str

            if self.category == Neutral.SKYPE_LOG:
                description = preamble
                recipients = join_truthy(author, recipients, ', ')
                recipients_sep = ' of conversation with '
            else:
                description = join_truthy(preamble, author, ' from ')
                recipients_sep = ' to '

            description = join_truthy(description, recipients, recipients_sep)
            description = join_truthy(description, self.description)
        elif self.category == Neutral.SKYPE_LOG:
            author = JEFFREY_EPSTEIN if self.recipients_str and not author else author
            preamble_separator = ' of conversation with '
        elif self.category == Neutral.PRESSER:
            description = join_truthy(preamble, self.description, ' announcing ')  # note reversed args
            description = join_truthy(author, description)
        elif self.category == Interesting.REPUTATION or (self.category == Neutral.LEGAL and 'v.' in self.author_str):
            author_separator = ': '
        elif self.category in [Category.RESUMÉ, Category.TWEET]:
            preamble_separator = 'of' if self.category == Category.RESUMÉ else 'by'
            preamble_separator = preamble_separator.center(3, ' ')

        # Construct standard description from pieces if a custom one has not been created yet
        if not description:
            preamble_author = join_truthy(preamble, author, preamble_separator)
            author_description = join_truthy(author, self.description, author_separator)

            if author and preamble_author.endswith(author) and author_description.startswith(author):
                preamble_author = preamble_author.removesuffix(author).strip()

            description = join_truthy(preamble_author, author_description)

        # TODO: this sucks
        if self.author == INSIGHTS_POD:
            description = join_truthy(description, f"from {ZUBAIR_AND_ANYA}")

        if self.attached_to_email_id:
            description = join_truthy(description, f"attached to email {self.attached_to_email_id}", sep=', ')

        return description

    @property
    def description_txt(self) -> Text | None:
        """Add parentheses to `self.config.description`."""
        if self.complete_description:
            from epstein_files.output.epstein_highlighter import non_epstein_highlighter
            style = 'bright_white italic' if site_config.email_info_in_subtitle else INFO_STYLE
            return non_epstein_highlighter(Text(self.complete_description, style))

    @property
    def external_link(self) -> ExternalLink | None:
        """Link to more info about this document (almost unused)."""
        return ExternalLink(self.url, self.url_link_text) if self.url else None

    @property
    def external_link_txt(self) -> Text | None:
        """Link to more info about this document (almost unused)."""
        return self.external_link.domain_link if self.external_link else None

    @property
    def has_any_info(self) -> bool:
        """True if either `author` or `description` is truthy."""
        return bool(self.description or self.author)

    @property
    def text_highlighter(self) -> 'EpsteinHighlighter':
        """Use a custom highlighter that also colors `self.highlight_quote` string if set."""
        from epstein_files.output.epstein_highlighter import highlighter, temp_highlighter

        if self.highlighted_pattern:
            return temp_highlighter(self.highlighted_pattern)
        else:
            return highlighter

    @property
    def highlighted_pattern(self) -> str | None:
        """Regex pattern that matches `self.highlight_quote` string, allowing for line breaks etc."""
        return re.escape(self.highlight_quote).replace(r'\ ', r"\s+") if self.highlight_quote else None

    @property
    def is_empty(self) -> bool:
        has_truthy_field = any([v for k, v in asdict(self).items() if k not in ['id', 'is_valid_for_name_scan']])
        return self.is_valid_for_name_scan is True and not has_truthy_field

    @property
    def is_description_a_title(self) -> bool:
        """True if first char is uppercase or a quote."""
        if not (self.author and self.description):
            return False
        elif self.category not in [Category.ACADEMIA, Category.BOOK, Category.FINANCE]:
            return False
        elif self.category == Category.FINANCE and self.author not in FINANCIAL_REPORTS_AUTHORS:
            return False

        first_char = self.description[0]
        return first_char.isupper() or first_char in ["'", '"']

    @property
    def is_doj_file(self) -> bool:
        return is_doj_file(self.id)

    @property
    def is_excerpt(self) -> bool:
        return isinstance(self.truncate_to, tuple)

    @property
    def is_house_file(self) -> bool:
        return not self.is_doj_file

    @property
    def is_of_interest(self) -> bool | None:
        """
        `self.is_interesting` value takes precedence. If it's not set apply the rules below.
        Defaults to True for HOUSE_OVERSIGHT files w/out info, None for DOJ files.
        Returns None (not False) if there's no firm decision, leaving `Document` classes
        to do any other checks they might want to.

                [+] = interesting  /  - = uninteresting

            [+] is_interesting (+ is_in_chrono if --output-chrono in effect)
            [+] highlight_quote is set
            [+] author in PERSONS_OF_INTEREST
            [+] category is in Interesting enum
            [+] having no author/description *if* HOUSE_OVERSIGHT
             -  duplicates
             -  known email attachments
             -  is_interesting == False (not None)
             -  finance category with any author (more broadly "Neutral categories can check bespoke additional conditions")
             -  category in Uninteresting enum
             -  description text starts with one of UNINTERESTING_PREFIXES

        """
        if self.duplicate_of_id:
            return False
        elif self.attached_to_email_id and (args.output_chrono or args.output_emails):  # TODO: not sure whether it's good always exclude attachments
            return False
        elif args.output_chrono and self.is_in_chrono is not None:
            return self.is_in_chrono
        elif self.is_interesting is not None:
            return self.is_interesting
        elif self.highlight_quote:
            return True
        # author related checks  # NOTE: this only applies to configured authors or derived_cfg! so other files but not most emails
        elif self.author and self.author in PERSONS_OF_INTEREST:
            return True
        # category field checks
        elif is_interesting(self.category):
            return True
        elif self.category == Category.FINANCE and self.author is not None:  # TODO: boothbay and other pitch decks should be of interest
            return False
        elif is_uninteresting(self.category):
            return False
        # description field checks
        elif any (self.description.startswith(pfx) for pfx in UNINTERESTING_PREFIXES):
            return False

        return None

    @property
    def metadata(self) -> Metadata:
        metadata = {k: v for k, v in asdict(self).items() if v and k not in NON_METADATA_FIELDS}

        if self.is_interesting is False:
            metadata['is_interesting'] = False  # Configured False is valid signal

        return metadata

    @property
    def recipients_str(self) -> str:
        """Overloaded in subclasses that support recipients."""   # TODO: this shouldn't have to be here
        return ''

    # @property
    # def table_preview_len(self) -> int | None:
    #     """Number of chars to show in an `OtherFile` table view."""

    @property
    def timestamp(self) -> datetime | None:
        if self.date and (parsed_dt := coerce_utc_strict(parse(self.date))):
            self._debug_log(f"parsed {parsed_dt.isoformat()} from date='{self.date}'")
            return parsed_dt

    @property
    def truncate_at(self) -> int | CharRange | None:
        """The number of chars to show when printing this document."""
        if self.truncate_to:
            return self.truncate_to
        elif self.is_interesting:
            return NO_TRUNCATE
        elif self.category in SHORT_TRUNCATE_CATEGORIES:
            return SHORT_TRUNCATE_TO

    @property
    def truthy_props(self) -> dict[str, bool | str | None]:
        props = {k: v for k, v in asdict(self).items() if v or (is_bool_prop(k) and v is False)}

        if self.is_of_interest is not None:
            if self.is_of_interest == props.get('is_interesting'):
                props['is_of_interest'] = props.pop('is_interesting')  # Remove is_interesting, just keep is_of_interest
            else:
                props['is_of_interest'] = self.is_of_interest

        if self.complete_description:
            description_pieces = without_falsey([self.author, self.description])

            # Avoid showing complete_description if it's just the author or description and other prop doesn't exist
            if len(description_pieces) != 1 or description_pieces[0] != self.complete_description:
                props['complete_description'] = self.complete_description

        if (category_txt := self.category_txt):
            if category_txt.plain == props.get('category'):
                props.pop('category')  # Leave only the colored version of category_txt

            # Only add ??? for non-email, non immesage
            if category_txt.plain == QUESTION_MARKS:
                if not isinstance(self, CommunicationCfg):
                    props['category_txt'] = category_txt
            else:
                props['category_txt'] = category_txt

        if self.timestamp:
            props['timestamp'] = self.timestamp

            if 'date' in props:
                props.pop('date')

        if props.get('dupe_type') == SAME:
            props.pop('dupe_type')

        return props

    @property
    def _class_name(self) -> str:
        return type(self).__name__

    @property
    def _identifier(self) -> str:
        """Required `LoggingEntity` abstract method."""
        return self.id

    def duplicate_cfgs(self) -> Generator[Self, None, None]:
        """Create synthetic `DocCfg` objects that set the 'duplicate_of_id' field to point back to this object."""
        for id in self.duplicate_ids:
            dupe_cfg = deepcopy(self)
            dupe_cfg.id = id
            dupe_cfg.duplicate_ids = []
            dupe_cfg.duplicate_of_id = self.id
            dupe_cfg.dupe_type = self.dupe_type
            dupe_cfg.is_synthetic = True
            yield dupe_cfg

    def set_category(self, category: str) -> None:
        """Update the title if we changed to a category that allows titling (books, academia, finance)."""
        self.category = category.lower().strip()

        if not self.category:
            return
        elif not is_category(self.category):
            self._warn(f"'{self.category}' does not appear to be a valid category")

        if self.category == Category.FLIGHT_LOG and not self.display_text:
            self.display_text ='flight log'

        self.description = quote(self.description) if self.is_description_a_title else self.description

    def _props_strs(self) -> list[str]:
        props = []
        add_prop = lambda f, value: props.append(f"{f.name}={value}")

        for _field in sorted(fields(self), key=lambda f: FIELD_SORT_KEY.get(f.name, f.name)):
            value = getattr(self, _field.name)

            if _field.name in ['actual_text'] or is_bool_prop(_field.name):  # fields can be False or None or ''
                if value is not None:
                    add_prop(_field, str(value))
            elif not value or (_field.name == 'dupe_type' and value == 'same'):
                continue
            elif _field.name == AUTHOR:
                add_prop(_field, constantize_name(str(value)) if args.constantize else f"'{value}'")
            elif _field.name == 'recipients':
                recipients_str = str([constantize_name(r) if (args.constantize and r) else r for r in value])
                add_prop(_field, recipients_str.replace("'", '') if args.constantize else recipients_str)
            elif _field.name == 'truncate_to' and value == NO_TRUNCATE:
                add_prop(_field, 'NO_TRUNCATE')
            elif isinstance(value, str):
                if "'" in value:
                    value = '"' + value.replace('"', r'\"') + '"'
                else:
                    value = "'" + value.replace("'", r'\'') + "'"

                add_prop(_field, value)
            else:
                add_prop(_field, str(value))

        return props

    def __rich__(self) -> Text:
        return Text(', ').join([Text(p) for p in self._props_strs()])

    def __repr__(self) -> str:
        props = self._props_strs()
        type_str = f"{self._class_name}("
        single_line_repr = type_str + ', '.join(props) + f')'

        if len(single_line_repr) < MAX_REPR_LINE_LENGTH or \
                (self.comment and 'is_fwded_article' in dir(self) and getattr(self, 'is_fwded_article')):
            repr_str = single_line_repr
        else:
            repr_str = f"{type_str}{INDENT_NEWLINE}" + INDENTED_JOIN.join(props)
            repr_str += ',' if props else ''
            repr_str += '\n)'

        if args.constantize:
            repr_str = INDENT + INDENT_NEWLINE.join(repr_str.split('\n'))
            return repr_str.replace(',,', ',').replace(',),', '),').replace(',),', '),')
        else:
            return repr_str

    @classmethod
    def create_or_set_prop(cls, ids: list[str], existing_cfgs: Sequence['DocCfg'], prop: str, val: Any) -> None:
        """If a record exists in `existing_cfgs` update it, otherwise create new and append."""
        cfg_dict = {cfg.id: cfg for cfg in existing_cfgs}
        created = updated = 0

        for id in ids:
            if (cfg := cfg_dict.get(id)):
                assert getattr(cfg, prop) is None, f"Can't overwrite existing '{prop}' value for {cfg}"
                setattr(cfg, prop, val)
                updated += 1
            else:
                existing_cfgs.append(cls(id=id, **{prop: val}))
                created += 1

        logger.info(f"Created {created} {cls.__name__} with {prop}={val}, updated {updated} existing.")

    @classmethod
    def set_categories(cls, cfgs: Sequence['DocCfg'], category: str | Path) -> None:
        """Set the `category` property for all `cfgs`."""
        category = category.stem if isinstance(category, Path) else category
        logger.debug(f"Setting category for {len(cfgs)} configs to '{category}'")

        for cfg in cfgs:
            cfg.set_category(cfg.category or category)


@dataclass(kw_only=True)
class CommunicationCfg(DocCfg):
    """
    Manual config is always required for MessengerLog author attribution. It's also often needed for Email
    files to handle the terrible OCR text that Congress provided which messes up a lot of the email headers.

    Attributes:
        is_fwded_article (bool, optional): `True` if this is a newspaper article someone fwded. Used to exclude articles from word counting.
        recipients (list[Name]): Who received the communication
        recipient_uncertain (bool | str, optional): Optional explanation of why this recipient was attributed, but uncertainly
    """
    is_fwded_article: bool | None = None
    recipients: list[Name] = field(default_factory=list)
    recipient_uncertain: bool | str = ''

    def __post_init__(self):
        super().__post_init__()

        if not isinstance(self.recipients, list):
            raise ValueError(f"{self.id} recipients is not a list: {self.recipients}")

        if self.is_fwded_article:
            self.is_valid_for_name_scan = False

        self.recipients = sort_names(self.recipients)

    @property
    def is_of_interest(self) -> bool | None:
        """Fwded articles are not interesting."""
        if self.is_fwded_article and not self.is_interesting:
            return False
        else:
            return super().is_of_interest

    @property
    def recipients_str(self) -> str:
        return ', '.join([r or UNKNOWN for r in self.recipients])

    def __repr__(self) -> str:
        return super().__repr__()


@dataclass(kw_only=True)
class EmailCfg(CommunicationCfg):
    """
    Attributes:
        actual_text (str, optional): In dire cases of broken OCR we just configure the body of the email as a string.
        fwded_text_after (str, optional): If set, any text after this is a fwd of an article or similar.
        has_uninteresting_ccs (bool): If `True` this email's CC: recipients will be marked as 'uninteresting'.
        has_uninteresting_bccs (bool): If `True` this email's BCC: recipients will be marked as 'uninteresting'.
        subject (str, optional): Subject line.
    """
    actual_text: str | None = None
    fwded_text_after: str | None = None
    has_uninteresting_ccs: bool = False
    has_uninteresting_bccs: bool = False
    subject: str | None = None

    def __post_init__(self):
        super().__post_init__()

        if self.fwded_text_after:
            self.is_valid_for_name_scan = False

    @property
    def truncate_at(self) -> int | CharRange | None:
        if super().truncate_at:
            return super().truncate_at
        elif self.is_fwded_article or self.fwded_text_after:
            return SHORT_TRUNCATE_TO

    # This is necessary because for some dumb reason @dataclass(repr=False) doesn't cut it
    def __repr__(self) -> str:
        return super().__repr__()


@dataclass(kw_only=True)
class TextCfg(CommunicationCfg):
    # This is necessary because for some dumb reason @dataclass(repr=False) doesn't cut it
    def __repr__(self) -> str:
        return super().__repr__()
