import json
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
from epstein_files.output.site.site_config import MobileConfig
from epstein_files.people.interesting_people import PERSONS_OF_INTEREST
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import coerce_utc_strict, without_falsey
from epstein_files.util.helpers.file_helper import is_doj_file
from epstein_files.util.external_link import ExternalLink
from epstein_files.util.helpers.rich_helpers import CharRange
from epstein_files.util.helpers.string_helper import collapse_whitespace, is_bool_prop, join_truthy, quote
from epstein_files.util.logging import logger
from epstein_files.util.logging_entity import LoggingEntity

DebugDict = dict[str, bool | datetime | set | str | Path | None]
DuplicateType = Literal['bounced', 'earlier', 'quoted', 'redacted', 'same']
Metadata = dict[str, bool | datetime | int | str | None | list[str | None] | dict[str, bool | str]]

DOC_CHAR_RANGE = (0, 12_000)
EMAIL_TRUNCATE_TO = int(DOC_CHAR_RANGE[1] / 3)
SHORT_TRUNCATE_TO = int(EMAIL_TRUNCATE_TO / 3)
WHOLE_FILE_CHAR_RANGE = (0, 10_000_000_000)
NO_TRUNCATE = -1
MAX_REPR_LINE_LENGTH = 135

CHECK_LINK_FOR_DETAILS = 'not shown here, check original PDF for details'
QUOTE_PREFIX = 'see quote'
SAME = 'same'

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
    Interesting.REPUTATION: REPUTATION_MGMT,
    Neutral.DEPOSITION: 'deposition of',
    Neutral.FLIGHT_LOG: Neutral.FLIGHT_LOG.replace('_', ' '),
    Neutral.PRESSER: Neutral.PRESSER.replace('_', ' '),
    Neutral.RESUMÉ: 'professional resumé',
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
        comment (str, optional): Info about this file not worth being in the `note`
        date (str, optional): Parsed to a datetime by timestamp() if it exists
        display_text (str, optional): Replace the contents of this file with this string when it's displayed
        dupe_type (DuplicateType | None): The type of duplicate this file is or its 'duplicate_ids' are
        duplicate_ids (list[str]): IDs of *other* documents that are dupes of this document
        duplicate_of_id (str | None): If this is a dupe the ID of the duplicated file. This file will be suppressed
        highlight_quote (str, optional): text to highlight, also triggers `is_of_interest` and `show_full_panel` to True
        is_interesting (bool | int | None): Force this file to be interesting (or not) if set, int value ranks most intersting
        is_in_chrono (bool | None): Like is_interesting, but only applies with --output-chrono
        is_synthetic (bool): True if this config was generated by the `duplicate_cfgs()` method
        is_valid_for_name_scan (bool): should text of this doc be scanned for names to create biographical panels
        non_participants (list[str]): hacky way to avoid false detection of these names
        note (str, optional): description of what's in this file
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
    display_text: str = ''
    dupe_type: DuplicateType | None = None
    duplicate_ids: list[str] = field(default_factory=list)
    duplicate_of_id: str | None = None
    entity_names: list[str] = field(default_factory=list)
    highlight_quote: str = ''
    is_interesting: bool | int | None = None  # NOTE: if truthy emails will not be truncated!
    is_in_chrono: bool | None = None
    is_synthetic: bool | None = None
    is_valid_for_name_scan: bool = True
    non_participants: list[str] = field(default_factory=list)  # TODO: this sucks
    note: str = ''
    num_preview_chars: int | None = None
    show_full_panel: bool = False
    show_with_name: str = ''
    truncate_to: int | tuple[int, int] | None = None
    url: str = ''
    url_link_text: str = ''

    def __post_init__(self):
        if self.id in self.duplicate_ids:
            raise ValueError(f"{self.id} is a duplicate of itself!")
        elif self.truncate_to is not None and not isinstance(self.truncate_to, (int, tuple)):
            raise ValueError(f"{self.id} truncate_to ({type(self.truncate_to).__name__}, value={self.truncate_to})")
        elif 'efta' in self.id:
            self._warn(f"id should not be lowercase: '{self.id}'")
            self.id = self.id.upper()

        self.set_category(self.category)

        # background_color, highlight_quote, or a tuple truncate_to set show_full_panel to true
        if self.background_color or self.highlight_quote or isinstance(self.truncate_to, tuple):
            self.show_full_panel = True

            if self.highlight_quote:
                description_quote = collapse_whitespace(self.highlight_quote.replace('>', ''))
                self.note = join_truthy(self.note, f'{QUOTE_PREFIX}: {quote(description_quote)}', ', ')

        # show_full_panel sets is_interesting=10
        if self.show_full_panel and self.is_interesting is not False:
            self.is_interesting = 10

        if self.duplicate_of_id or self.duplicate_ids:
            self.dupe_type = self.dupe_type or SAME

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
        if args.truncate:
            return (0, args.truncate)
        elif args.whole_file or self.truncate_to == NO_TRUNCATE:
            return WHOLE_FILE_CHAR_RANGE
        elif self.truncate_to is None:
            if self.is_interesting:
                return WHOLE_FILE_CHAR_RANGE
            elif self.category in SHORT_TRUNCATE_CATEGORIES:
                return (0, SHORT_TRUNCATE_TO)
            else:
                return None
        elif isinstance(self.truncate_to, tuple):
            return self.truncate_to
        else:
            return (0, self.truncate_to)

    @property
    def complete_description(self) -> str:
        """String that summarizes what is known about this document."""
        author = f"{self.author} {QUESTION_MARKS}" if self.author and self.author_uncertain else self.author
        preamble = CATEGORY_PREAMBLES.get(self.category, '')
        preamble_separator = ''
        author_separator = ''
        description = ''

        # If description is set at all in one of these if/else checks must be fully constructed
        if self.display_text and not self.has_full_ocr_text_replacement:
            return join_truthy(self.display_text, self.note, ', ')
        if self.category == Uninteresting.BOOK or \
                (self.category == Uninteresting.ACADEMIA and self.author and self.note):
            description = join_truthy(self.note, author, ' by ')  # note reversed args
            description = join_truthy(preamble, description)
        elif self.category == Neutral.FINANCE and self._is_description_a_title:
            author_separator = ' report: '
        elif self.category == Neutral.PRESSER:
            description = join_truthy(preamble, self.note, ' announcing ')  # note reversed args
            description = join_truthy(author, description)
        elif self.category == Interesting.REPUTATION or (self.category == Neutral.LEGAL and 'v.' in self.author_str):
            author_separator = ': '
        elif self.category in [Category.RESUMÉ, Category.TWEET]:
            preamble_separator = 'of' if self.category == Category.RESUMÉ else 'by'
            preamble_separator = preamble_separator.center(3, ' ')

        # Construct standard description from pieces if a custom one has not been created yet
        if not description:
            preamble_author = join_truthy(preamble, author, preamble_separator)
            author_description = join_truthy(author, self.note, author_separator)

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
    def display_preview_txt(self) -> Text | None:
        """Override for the `OtherFile`s table preview column."""
        if self.replacement_preview_text:
            text = join_truthy(self.author, self.replacement_preview_text)
            return Text(f"(Text of {text} {CHECK_LINK_FOR_DETAILS})", 'dim italic')

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
        return bool(self.note or self.author)

    @property
    def has_full_ocr_text_replacement(self) -> bool:
        """`display_text` longer than other_files_preview_chars is considered a drop in replacement, not a short description."""
        return bool(self.display_text and len(self.display_text) > MobileConfig.other_files_preview_chars)

    @property
    def note_txt(self) -> Text | None:
        """Add formatting to `self.complete_description`."""
        if self.complete_description:
            txt = Text(self.complete_description, NOTE_STYLE)

            if self.external_link_txt:
                txt.append(' ').append(self.external_link_txt)

            from epstein_files.output.epstein_highlighter import non_epstein_highlighter
            return non_epstein_highlighter(txt)

    @property
    def replacement_preview_text(self) -> str:
        """Returns a string if `self.display_text` exists and is not too long."""
        return self.display_text if self.display_text and not self.has_full_ocr_text_replacement else ''

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
    def is_doj_file(self) -> bool:
        return is_doj_file(self.id)

    @property
    def is_empty(self) -> bool:
        has_truthy_field = any([v for k, v in asdict(self).items() if k not in ['id', 'is_valid_for_name_scan']])
        return self.is_valid_for_name_scan is True and not has_truthy_field

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
            return bool(self.is_interesting)
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
        elif any (self.note.startswith(pfx) for pfx in UNINTERESTING_PREFIXES):
            return False

        return None

    @property
    def is_very_interesting(self) -> bool:
        return isinstance(self.is_interesting, int)

    @property
    def metadata(self) -> Metadata:
        metadata = {k: v for k, v in asdict(self).items() if v and k not in NON_METADATA_FIELDS}

        if self.is_interesting is False:
            metadata['is_interesting'] = False  # Configured False is valid signal

        return metadata

    @property
    def names(self) -> list[str]:
        """Names configured for this document. Overloaded in subclass to add recipients."""
        return [self.author] if self.author else []

    @property
    def char_range_as_table_row(self) -> tuple[int, int] | None:
        """The char range that should be shown in `OtherFile` rollup tables."""
        if self.num_preview_chars:
            return (0, self.num_preview_chars)
        elif self.category == Uninteresting.BOOK:
            return (0, int(site_config.other_files_preview_chars / 2))
        else:
            return (0, site_config.other_files_preview_chars)

    @property
    def timestamp(self) -> datetime | None:
        if self.date and (parsed_dt := coerce_utc_strict(parse(self.date))):
            self._debug_log(f"parsed {parsed_dt.isoformat()} from date='{self.date}'")
            return parsed_dt

    @property
    def truthy_props(self) -> dict[str, bool | str | None]:
        props = {k: v for k, v in asdict(self).items() if v or (is_bool_prop(k) and v is False)}

        if self.is_of_interest is not None:
            if self.is_of_interest == props.get('is_interesting'):
                props['is_of_interest'] = props.pop('is_interesting')  # Remove is_interesting, just keep is_of_interest
            else:
                props['is_of_interest'] = self.is_of_interest

        if self.complete_description:
            description_pieces = without_falsey([self.author, self.note])

            # Avoid showing complete_description if it's just the author or description and other prop doesn't exist
            if len(description_pieces) != 1 or description_pieces[0] != self.complete_description:
                props['complete_description'] = self.complete_description

        if (category_txt := self.category_txt):
            if category_txt.plain == props.get('category'):
                props.pop('category')  # Leave only the colored version of category_txt

            # Only add ??? for non-email, non immesage. # TODO: this sucks
            if category_txt.plain == QUESTION_MARKS:
                if 'recipients' not in dir(self):
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

    @property
    def _is_description_a_title(self) -> bool:
        """True if first char is uppercase or a quote."""
        if not (self.author and self.note):
            return False
        elif self.category not in [Category.ACADEMIA, Category.BOOK, Category.FINANCE]:
            return False
        elif self.category == Category.FINANCE and self.author not in FINANCIAL_REPORTS_AUTHORS:
            return False

        first_char = self.note[0]
        return first_char.isupper() or first_char in ["'", '"']

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

        if self.category == Uninteresting.BOOK:
            self.is_valid_for_name_scan = False

        self.note = quote(self.note) if self._is_description_a_title else self.note

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
    def update_or_create_cfgs(cls, ids: list[str], manual_cfgs: Sequence['DocCfg'], prop: str, new_val: Any) -> None:
        """If a record exists in `existing_cfgs` update it, otherwise create new and append."""
        cfg_dict = {cfg.id: cfg for cfg in manual_cfgs}
        created = updated = 0

        for id in ids:
            if (manual_cfg := cfg_dict.get(id)):
                if (manual_val := getattr(manual_cfg, prop)) and manual_val != new_val:
                    manual_cfg._warn(f"overwriting manual '{prop}' value '{manual_val}' with '{new_val}' from configured list")

                setattr(manual_cfg, prop, new_val)
                updated += 1
            else:
                manual_cfgs.append(cls(id=id, **{prop: new_val}))
                created += 1

        logger.info(f"Created {created} {cls.__name__} with {prop}={new_val}, updated {updated} existing.")

    @classmethod
    def set_categories(cls, cfgs: Sequence['DocCfg'], category: str | Path) -> None:
        """Set the `category` property for all `cfgs`."""
        category = category.stem if isinstance(category, Path) else category
        logger.debug(f"Setting category for {len(cfgs)} configs to '{category}'")

        for cfg in cfgs:
            cfg.set_category(cfg.category or category)
