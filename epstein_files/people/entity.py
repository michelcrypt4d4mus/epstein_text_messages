import re
from dataclasses import dataclass, field, fields
from typing import ClassVar, Literal, Self, Sequence, TypeVar

from rich.style import Style
from rich.text import Text

from epstein_files.output.html.rich_style import RichStyle
from epstein_files.people.names import DEUTSCHE_BANK, LEON_BLACK, constantize_name, extract_first_name, extract_last_name
from epstein_files.util.constant.strings import (INDENT_NEWLINE, INDENTED_JOIN, JOURNALISM_STYLE, LAW_ENFORCEMENT,
     QUESTION_MARKS, WIKIPEDIA, PartialName)
from epstein_files.util.constant.urls import EPSTEINIFY, PERSON_LINK_BUILDERS, EpsteinSite, wikipedia_url, internal_person_link_url
from epstein_files.util.env import args
from epstein_files.util.external_link import ExternalLink, link_text_obj
from epstein_files.util.helpers.data_helpers import constantize_names, listify, without_falsey
from epstein_files.util.helpers.rich_helpers import QUESTION_MARKS_TXT, Textish, enclose, join_texts
from epstein_files.util.helpers.string_helper import (as_pattern, clean_phone_number, indented, is_integer,
     join_patterns, join_truthy, join_truthy_args, quote, remove_question_marks)
from epstein_files.util.logging_entity import LoggingEntity
from epstein_files.util.logging import logger

AKA_STYLE = 'grey39 italic'
BIO_COLOR = 'grey70'
BIO_STYLE = f'italic {BIO_COLOR}'
LINK_JOIN_STYLE = 'grey23 bold'

MIN_LEN_FOR_OPTIONAL_LAST_CHAR = 5

ALL_CAPS_REGEX = re.compile(r"^[A-Z]{1,2}$")
MGMT_PATTERN = r"M(ana)?ge?m(en)?t"
MGMT_REGEX = re.compile(MGMT_PATTERN)
COMPANY_SUFFIX_REGEX = re.compile(fr".*?(,? (Inc\.?|LLC|{MGMT_PATTERN}))$")
MIDDLE_INITIAL_REGEX = re.compile(r"^[A-Z]\.?$")
SIMPLE_NAME_REGEX = re.compile(r"^[-\w, ]+$", re.IGNORECASE)

BLACK_BOOK_PHONE_NUMBER_COLS = [
    "Phone (h) – home",
    "Phone (no specifics)",
    "Phone (p) – portable/mobile",
    "Phone (w) – work",
]

EntityKwarg = TypeVar('EntityKwarg', bound=str | bool | None)


@dataclass
class Entity(LoggingEntity):
    """
    Attributes:
        name (str): Person or organization name
        info (str, optional): biographical info about this person
        emailer_pattern (str, optional): manually constructed regex pattern to match this person in email headers
        aliases (list[str]): known aliases
        category (str, optional): category of this entity
        email_addresses (list[str]): known email addresses
        emailer_regex (re.Pattern): pattern that matches this person's name in email headers
        highlight_regex (re.Pattern): pattern that matches this person's name in various variations for highlightihng
        is_emailer (bool): should email headers be scanned for this entity
        is_interesting (bool): should a biographical entry be generated for this panel in the chronological view
        is_scannable (bool): set to False for a few people whose names are easy to match (e.g. Larry Summers)
        is_junk (bool): for junk email
        match_partial (PartialName | None): whether to also match this entity's first and/or last names
        style (str, optional): style to use when printing this entity's name
        unique_phraseologies (list[str], optional): turns of phrase known to be unique to this person
        url (str | list[str] | Literal['WIKIPEDIA'], optional): link(s) to info about this entity
    """
    name: str
    info: str = ''  # TODO: rename "note" for consistency w/DocCfg
    emailer_pattern: str = ''

    # Props after here not set by positional args
    aliases: list[str] = field(default_factory=list)
    email_addresses: list[str] = field(default_factory=list)
    emailer_regex: re.Pattern = field(init=False)
    highlight_regex: re.Pattern = field(init=False)
    is_emailer: bool | None = True
    is_interesting: bool = True  # Eligible for bio panel
    is_junk: bool = False  # TODO: this sucks
    is_scannable: bool = True
    match_partial: PartialName | None = 'last'
    phone_numbers: list[str] = field(default_factory=list)
    unique_phraseologies: list[str] = field(default_factory=list)
    url: str | list[str] | Literal['WIKIPEDIA'] = ''

    # NOTE: category is usually set by a `HighlightedNames` that holds this `Entity`
    category: str = ''
    _style: RichStyle = field(default_factory=lambda: RichStyle(None))
    _urls: list[str] = field(init=False)
    # jmail_url: str

    # Class variables
    DEFAULT_PATTERN_SFX: ClassVar[str] = '?'
    MATCH_REVERSED_NAME: ClassVar[bool] = True

    def __post_init__(self):
        self._urls = [wikipedia_url(self.name) if url == WIKIPEDIA else url for url in listify(self.url)]

        if not all(url.startswith('http') for url in self._urls):
            self._error(f"Bad URL configured: {self._urls}")

        try:
            self.emailer_regex = re.compile(self.pattern, re.IGNORECASE)
            self.highlight_regex = re.compile(fr"\b({self.highlight_pattern})\b", re.IGNORECASE)
        except re.error as e:
            self._error(f"failed to compile emailer or highlight regex: {e}")
            raise e

        if self.category:
            self._warn(f"has category '{self.category}' at instantiation time (style='{self.style}')")

        self.phone_numbers = sorted([clean_phone_number(number) for number in self.phone_numbers])

    @classmethod
    def anon(cls, name: str) -> Self:
        """Alternate convenience constructor for names like 'Jane Doe'."""
        return cls(name, is_interesting=False, is_emailer=False, match_partial=None)

    @classmethod
    def assistant(cls, name: str, to: str, note: str = '', **kwargs) -> Self:
        """Alternative constructor for people's assistants."""
        note = join_truthy(f"assistant to {to}", note, ' ' if note == QUESTION_MARKS else  ', ')
        return cls(name, note, match_partial=None, **kwargs)

    @classmethod
    def from_black_book(cls, black_book_row: dict[str, str]) -> Self:
        """
        {
            "Address": "",
            "Address-Type": "",
            "City": "",
            "Company/Add. Text": "",
            "Country": "",
            "Email": "",
            "First Name": "Abby",
            "Name": "Abby",
            "Phone (h) – home": "",
            "Phone (no specifics)": "7944574202",
            "Phone (p) – portable/mobile": "",
            "Phone (w) – work": "",
            "Surname": "",
            "Zip": ""
        }
        """
        name = black_book_row['Name']
        first_name = black_book_row['First Name']
        last_name = black_book_row['Surname']
        location = join_truthy_args(black_book_row['City'], black_book_row['Country'])
        phone_numbers = []

        if (name and first_name and first_name not in name) or (name and last_name and last_name not in name):
            logger.warning(f"Too many names (name='{name}', first_name='{first_name}', last_name='{last_name}')")

        for number in without_falsey([v for k, v in black_book_row.items() if k in BLACK_BOOK_PHONE_NUMBER_COLS]):
            numbers = without_falsey(number.split('|') if '|' in number else [number])
            phone_numbers.extend([n.split('(')[0] for n in numbers])

        return cls(
            name=name or join_truthy(first_name, last_name),
            info=join_truthy_args(black_book_row["Company/Add. Text"], location),
            email_addresses=without_falsey([black_book_row['Email']]),
            phone_numbers=phone_numbers,
        )

    @property
    def alt_links(self) -> list[ExternalLink]:
        """Links beyond the first one (which is usually attached to the name)."""
        return self.links()[1:]

    @property
    def alt_links_txt(self) -> Text:
        """Alternate links parenthesized and concatenated into one Text object."""
        return self._joined_links(self.alt_links)

    # TODO: add known email addresses?
    @property
    def bio_txt(self) -> Text:
        """Biographical info about this entity with links etc."""
        from epstein_files.output.epstein_highlighter import non_epstein_highlighter
        bio_pieces: list[Textish] = [Text('').append(self.name_with_link)]
        bio_pieces.extend([Text('aka ', AKA_STYLE).append(Text(alias, self.style)) for alias in self.aliases])

        if self.category:
            category_style = self._style.style if 'red' in str(self._style) else self._style.dim
            category_txt = Text(self.category.lower(), style=category_style)
            bio_pieces.append(enclose(category_txt, encloser='[]', encloser_style='dim'))

        bio_pieces.append(non_epstein_highlighter(Text(self.info, BIO_STYLE)) if self.info else QUESTION_MARKS_TXT)
        bio_pieces.append(self.links_txt(include_wikipedia=False))
        return join_texts(bio_pieces)

    # TODO: rename this somehting that means "non_custom_external_links"
    @property
    def epstein_sites_all_links(self) -> Text:
        """Collection of links to sites that have biographies of the Epstein network like epsteinify, Jmail search, etc."""
        links = [self.epstein_site_link(site) for site in PERSON_LINK_BUILDERS]
        return Text('', justify='center', style='dim').append(join_texts(links, join=' / '))

    @property
    def has_bio(self) -> bool:
        return bool(self.is_interesting and self.info)

    @property
    def highlight_pattern(self) -> str:
        """`self.emailer_pattern` extended with first/last name variations for Rich highlighting."""
        if self.is_junk:
            return self.pattern  # TODO: this sucks

        return join_patterns(self._name_patterns)

    @property
    def identifying_strings(self) -> list[str]:
        """Strings that indicate a document is likely tied to this entity."""
        return self.unique_phraseologies + (self.email_addresses if self.is_emailer else [])

    @property
    def info_with_category(self) -> str:
        """String lik 'category, info'."""
        return ', '.join(without_falsey([self.category, self.info]))

    @property
    def internal_link(self) -> Text:
        """Kind of like an anchor link to the section of the page containing these emails."""
        return link_text_obj(internal_person_link_url(self.name), self.name, self.style)

    @property
    def is_email_address(self) -> bool:
        return '@' in self.name

    @property
    def is_linkable(self) -> bool:
        """Return True if it's likely that EpsteinWeb has a page for this name."""
        return not (self.is_email_address or '/' in self.name)

    @property
    def name_with_link(self) -> Text:
        """Colored name with hyperlink if applicable (otherwise just colored name)."""
        if self._urls:
            return ExternalLink(self._urls[0], self.name, link_style=self._style.bold).link
        else:
            return Text(self.name, self._style.not_bold)

    @property
    def pattern(self) -> str:
        """Pattern used for matching emails, base pattern for highlights."""
        if self.emailer_pattern:
            pattern = self.emailer_pattern
        else:
            if self._middle_initial:
                pattern = fr"{self._names[0]} ({self._middle_initial}\.? )?{self._names[-1]}"
            else:
                pattern = self.name

            if len(self.name) >= MIN_LEN_FOR_OPTIONAL_LAST_CHAR:
                pattern += self.DEFAULT_PATTERN_SFX

            if self.MATCH_REVERSED_NAME and (len(self._names) == 2 or (len(self._names) == 3 and self._middle_initial)):
                pattern = join_patterns([pattern, fr"{self._names[-1]},? {self._names[0]}{self.DEFAULT_PATTERN_SFX}"])

        return as_pattern(join_patterns([pattern, *self.email_addresses]))

    @property
    def style(self) -> str:
        style_str = str(self._style.style)
        return '' if style_str == 'none' else style_str

    @style.setter
    def style(self, val: str | Style | None):
        self._style = RichStyle(val)

    @property
    def wikipedia_url(self) -> str:
        return wikipedia_url(self.name)

    @property
    def _identifier(self) -> str:
        """`LoggingEntity` abstract method implementation."""
        return quote(self.name)

    @property
    def _middle_initial(self) -> str:
        """Returns 'J' for 'Albert J. Gomez'."""
        if len(self._names) != 3:
            return ''
        elif MIDDLE_INITIAL_REGEX.match(self._names[1]):
            return self._names[1][0]
        else:
            return ''

    @property
    def _name_patterns(self) -> list[str]:
        """['Firstname', 'Lastname', 'Lastname, Firstname'."""
        name_patterns = [self.pattern]
        name = remove_question_marks(self.name)  # TODO: this sucks

        if self.match_partial is None or ' ' not in self.name:
            return name_patterns

        first_name = extract_first_name(name)
        last_name = extract_last_name(name)
        name_patterns.append(as_pattern(f"{last_name},? {first_name}"))  # TODO: maybe reversed name should be included by default?

        if self.match_partial in ['both', 'first'] and SIMPLE_NAME_REGEX.match(first_name):
            name_patterns.append(as_pattern(first_name))

        if self.match_partial in ['both', 'last'] and SIMPLE_NAME_REGEX.match(last_name):
            name_patterns.append(as_pattern(last_name))

        if args._debug_highlight_patterns:
            self._debug_log(f"name_patterns: '{name_patterns}'")

        return name_patterns

    @property
    def _names(self) -> list[str]:
        return self.name.split()

    @property
    def _props_strs(self) -> list[str]:
        props = []
        # if there's no self.emailer_pattern this obj was probably instantiated with positional args only
        add_prop = lambda f, value: props.append(f"{f}={value}" if self.emailer_pattern else value)

        for _field in fields(self):
            if _field.name == 'name':
                add_prop(_field.name, constantize_name(getattr(self, _field.name)))
            elif _field.name == '_style':
                add_prop('style', quote(self.style))
            elif (value := getattr(self, _field.name)) and not _field.name.endswith('regex'):
                if _field.name.endswith('pattern'):
                    value = f'r"{value}"'
                else:
                    value = quote(constantize_names(str(value)))
                    value = ('f' + value) if '{' in value else value

                add_prop(_field.name, value)

        props.append(f'highlight_pattern=r"{self.highlight_pattern}"')
        return props

    @property
    def _style_bold(self) -> Style:
        return self._style.not_bold

    @property
    def _style_no_bold(self) -> Style:
        return self._style.bold

    @property
    def _style_dim(self) -> str:
        return self.style if 'dim' in self.style else f'{self.style} dim'

    def epstein_site_link(self, site: EpsteinSite = EPSTEINIFY, link_text: str | None = None) -> ExternalLink:
        """Link to epsteinify.com, EpsteinWeb, or similar for this name."""
        return ExternalLink(self.epstein_site_url(site), link_text or site, link_style=self.style)

    def epstein_site_url(self, site: EpsteinSite = EPSTEINIFY) -> str:
        """URL pointing to info about this entity on one of the Epstein sites like epsteinify.com."""
        return PERSON_LINK_BUILDERS[site](self.name)

    def links(self) -> list[ExternalLink]:
        """All configured links from the `url` property."""
        return [
            ExternalLink(url, 'link' + (str(i) if i > 1 else ''), link_style=JOURNALISM_STYLE)
            for i, url in enumerate(self._urls, 1)
        ]

    def links_txt(self, include_wikipedia: bool = True) -> Text:
        """All links concatenated into one Text object."""
        links = self.links()

        if links and links[0].url == self.wikipedia_url and not include_wikipedia:
            links = links[1:]

        return self._joined_links([link.domain_link() for link in links])

    def _joined_links(self, links: Sequence[ExternalLink | Text]) -> Text:
        """Join links to '[link/link/link]' Text."""
        return enclose(join_texts(links, Text('/', LINK_JOIN_STYLE)), '[]', LINK_JOIN_STYLE) if links else Text('')

    def __eq__(self, other: Self):
        if not isinstance(other, Self):
            return NotImplemented

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self) -> str:
        props = self._props_strs
        type_str = f"{type(self).__name__}("

        if self.emailer_pattern:
            repr_str = f"{type_str}{INDENT_NEWLINE}" + INDENTED_JOIN.join(props)
            repr_str += ',' if props else ''
            repr_str += '\n)'
        else:
            repr_str = type_str + ', '.join(props) + ')'

        return repr_str

    def __str__(self) -> str:
        return self.name

    @classmethod
    def coerce_entity_names(cls, _arg: 'EntityScanArg') -> list[str]:
        if not _arg:
            return []

        return [e.name if isinstance(e, cls) else e for e in listify(_arg)]

    @classmethod
    def _repr_string(cls, contact_infos: list[Self]) -> str:
        """Print a list of `Entity` objects to a python string that can recreate them when executed."""
        return '[\n' + indented([repr(contact) for contact in contact_infos], 4) + '\n],'


@dataclass(eq=False)
class Organization(Entity):
    # Different defaults
    is_emailer: bool | None = None
    match_partial: PartialName | None = 'suffix'
    # Additional properties
    belongs_to: str = ''

    # Class vars
    DEFAULT_PATTERN_SFX: ClassVar[str] = ''
    MATCH_REVERSED_NAME: ClassVar[bool] = True

    def __post_init__(self):
        if self.emailer_pattern and self.is_emailer is not False:
            self.is_emailer = True

        if not self.emailer_pattern:
            if self.match_partial == 'suffix' and (suffix_match := COMPANY_SUFFIX_REGEX.match(self.name)):
                suffix = suffix_match.group(1)
                emailer_pattern = self.name.removesuffix(suffix)

                if not MGMT_REGEX.search(suffix):
                    if suffix.startswith(','):
                        suffix = suffix.replace(',', ',?')
                    else:
                        suffix = f",?{suffix}"

                if suffix.endswith('.'):
                    suffix = suffix.replace('.', r'\.?')

                self.emailer_pattern += fr"{emailer_pattern}({suffix})?"
            elif self.name.startswith('UAB '):
                self.emailer_pattern = self.name.removeprefix('UAB ')

        if self.belongs_to:
            if self.info:
                self.info = join_truthy(f"{self.belongs_to}", self.info)
            else:
                self.info = f"{self.belongs_to} organization"

        return super().__post_init__()

    @classmethod
    def well_known(cls, name: str, **kwargs) -> Self:
        """Alternate constructor that sets is_interesting to False."""
        return cls(name, is_interesting=False, is_scannable=False, **kwargs)


EntityScanArg = Sequence[Entity | str] | Entity | str | None


def acronym(name: str, info: str = '', **kwargs) -> Organization:
    """Auto-generates a regex matching the org's initials."""
    initials = [
        word if ALL_CAPS_REGEX.match(word) else word[0]
        for word in name.split() if word[0].isupper()
    ]

    initials_pattern = ''.join([fr"{letter}\.?" for letter in initials])
    emailer_pattern = join_patterns([initials_pattern, name])

    # Force word boundary in front to prevent spurious matches (can't force at end bc of period)
    if (is_emailer := _pop_kwarg(kwargs, 'is_emailer', False)):
        emailer_pattern = fr"\b({emailer_pattern})"

    return Organization(
        ''.join(initials),
        join_truthy(name, info, ', '),
        emailer_pattern,
        is_emailer=is_emailer,
        **kwargs
    )


def deutsche_bank_employee(name: str, role: str = '', **kwargs) -> Entity:
    match_partial = _pop_kwarg(kwargs, 'match_partial', None)
    note = f"{role} at {DEUTSCHE_BANK}" if role else f"{DEUTSCHE_BANK} employee"
    return Entity(name, note, match_partial=match_partial, **kwargs)


def epstein_co(name: str, emailer_pattern: str = '', info: str = '', **kwargs) -> Organization:
    return Organization(name, join_truthy('Epstein company', info), emailer_pattern, **kwargs)


def epstein_trust(
    name: str,
    emailer_pattern: str = '',
    beneficiaries: list[str] | None = None,
    trustees: list[str] | None = None,
) -> Organization:
    """One of Epstein's financial trust entities."""
    beneficiary_str = ''

    if beneficiaries:
        if len(beneficiaries) == 1:
            beneficiary_str = f"sole beneficiary {beneficiaries[0]}"
        else:
            beneficiary_str = f"beneficiaries {', '.join(beneficiaries)}"

    if trustees:
        beneficiary_str = join_truthy(beneficiary_str, f"trustees: " + ', '.join(trustees), ', ')

    beneficiary_str = f", {beneficiary_str}" if beneficiary_str else ''
    return Organization(epstein_trust_name(name), f'Epstein financial trust{beneficiary_str}', emailer_pattern)


def epstein_trust_name(name: str) -> str:
    return f"Jeffrey E. Epstein {name} Trust" if is_integer(name) else name


def island_employee(name: str, job_title: str, **kwargs) -> Entity:
    return Entity(name, f"{job_title} at the island", match_partial=None, **kwargs)


def law_enforcement(name: str, emailer_pattern: str = '', info: str = '', **kwargs) -> Organization:
    is_interesting = _pop_kwarg(kwargs, 'is_interesting', False)
    is_emailer = _pop_kwarg(kwargs, 'is_emailer', False) or bool(emailer_pattern)

    if name.startswith('US ') and not emailer_pattern:
        emailer_pattern = r"U(\.|nited)? S(\.|tates)? " + name.removeprefix('US ')
        match_partial = None
    else:
        match_partial = 'suffix'

    return Organization(
        name,
        info or LAW_ENFORCEMENT,
        emailer_pattern,
        is_emailer=is_emailer,
        is_interesting=is_interesting,
        match_partial=match_partial,
        **kwargs
    )


def leon_black_co(name: str, info: str = '', **kwargs) -> Organization:
    return Organization(name, info, belongs_to=LEON_BLACK, **kwargs)



def publication(name: str, emailer_pattern: str = '', is_scannable: bool = False, **kwargs) -> Organization:
    """Convenience method for WSJ, New York Times, etc."""
    # Make sure not to match 'Daily News' to 'Virgin Islands Daily News' / 'Palm Beach Daily News'
    if name.startswith('Daily'):
        emailer_pattern = fr"(?<!(Beach|lands)\s){as_pattern(emailer_pattern or name)}"

    return Organization(
        name,
        emailer_pattern=emailer_pattern,
        is_interesting=False,
        is_scannable=is_scannable,
        **kwargs
    )


def the_publication(name: str, emailer_pattern: str = '', is_scannable: bool = False, **kwargs) -> Organization:
    """Publication that starts with 'The'."""
    emailer_pattern = emailer_pattern or name
    pattern = fr"({emailer_pattern})" if '|' in emailer_pattern else emailer_pattern
    return publication(name, fr"(The )?{pattern}", is_scannable=is_scannable, **kwargs)


def _pop_kwarg(kwargs: dict, key: str, default: EntityKwarg = False) -> EntityKwarg:
    """Pop a kwarg and return if it exists, elese return `default`."""
    return kwargs.pop(key) if key in kwargs else default
