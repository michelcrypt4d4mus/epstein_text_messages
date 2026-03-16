import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field, fields
from typing import Literal, Self

from rich.padding import Padding
from rich.style import Style
from rich.text import Text

# from epstein_files.output.html.html_style import HtmlStyle
from epstein_files.people.names import Name, constantize_name, extract_first_name, extract_last_name
from epstein_files.util.constant.strings import INDENT_NEWLINE, INDENTED_JOIN, LAW_ENFORCEMENT, WIKIPEDIA, PartialName
from epstein_files.util.constant.urls import wikipedi_url
from epstein_files.util.env import args, site_config
from epstein_files.util.external_link import ExternalLink
from epstein_files.util.helpers.data_helpers import constantize_names, listify
from epstein_files.util.helpers.rich_helpers import QUESTION_MARKS_TXT, Textish, enclose, join_texts, parenthesize
from epstein_files.util.helpers.string_helper import (as_pattern, indented, is_integer, join_patterns,
     join_truthy, quote, remove_question_marks)
from epstein_files.util.logging import logger
from epstein_files.util.logging_entity import LoggingEntity

AKA_STYLE = 'grey39 italic'
BIO_COLOR = 'grey70'
BIO_STYLE = f'italic {BIO_COLOR}'
MIN_LEN_FOR_OPTIONAL_LAST_CHAR = 5

LINK_JOIN_STYLE = 'grey23 bold'
MGMT_PATTERN = r"M(ana)?ge?m(en)?t"
MGMT_REGEX = re.compile(MGMT_PATTERN)
COMPANY_SUFFIX_REGEX = re.compile(fr".*?(,? (Inc\.?|LLC|{MGMT_PATTERN}))$")
MIDDLE_INITIAL_REGEX = re.compile(r"^[A-Z]\.?$")
SIMPLE_NAME_REGEX = re.compile(r"^[-\w, ]+$", re.IGNORECASE)


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
        is_junk (bool): for junk email
        is_organization (bool): if this is a company or group, don't try to match first and last versions of its name
        match_partial (PartialName | None): whether to also match this entity's first and last names
        style (str, optional): style to use when printing this entity's name
        unique_phraseologies (list[str], optional): turns of phrase known to be unique to this person
        url (str | list[str] | Literal['WIKIPEDIA'], optional): link(s) to info about this entity
    """
    name: str
    info: str = ''
    emailer_pattern: str = ''
    # Props after here not usually set by positional args
    aliases: list[str] = field(default_factory=list)
    category: str = ''  # NOTE: not usually set at instantiation time!
    email_addresses: list[str] = field(default_factory=list)
    emailer_regex: re.Pattern = field(init=False)
    highlight_regex: re.Pattern = field(init=False)
    is_emailer: bool = True
    is_interesting: bool = True  # Eligible for bio panel
    is_junk: bool = False  # TODO: this sucks
    is_organization: bool = False
    match_partial: PartialName | None = 'last'
    style: str = ''  # NOTE: not usually set at instantiation time!
    unique_phraseologies: list[str] = field(default_factory=list)
    url: str | list[str] | Literal['WIKIPEDIA'] = ''
    _urls: list[str] = field(init=False)
    # jmail_url: str

    def __post_init__(self):
        if self.is_organization:
            self.match_partial = None

        self._urls = [wikipedi_url(self.name) if url == WIKIPEDIA else url for url in listify(self.url)]

        try:
            self.emailer_regex = re.compile(self.pattern, re.IGNORECASE)
            self.highlight_regex = re.compile(fr"\b({self.highlight_pattern})\b", re.IGNORECASE)
        except re.error as e:
            self._log(f"failed to compile emailer or highlight regex: {e}", logging.ERROR)
            raise e

        if self.category:
            self._warn(f"has category '{self.category}' at instantiation time (style='{self.style}')")
        if self.style:
            self._warn(f"has style '{self.category}' at instantiation time (style='{self.style}')")

    @property
    def alt_links(self) -> list[ExternalLink]:
        return [ExternalLink(url, f'more', link_style=self.style) for i, url in enumerate(self._urls[1:], 2)]

    @property
    def alt_links_txt(self) -> Text:
        """Alternate links parenthesized and concatenated into one Text object."""
        if self.alt_links:
            return enclose(join_texts(self.alt_links, Text('/', LINK_JOIN_STYLE)), '()', LINK_JOIN_STYLE)
        else:
            return Text('')

    # TODO: add known email addresses
    @property
    def bio_txt(self) -> Text:
        """Biographical info about this entity with links etc."""
        from epstein_files.output.epstein_highlighter import non_epstein_highlighter
        bio_pieces: list[Textish] = [Text('').append(self.name_with_link)]
        bio_pieces.extend([Text('').append('aka ', AKA_STYLE).append(Text(alias, self.style)) for alias in self.aliases])

        if self.category:
            category_txt = Text(self.category.lower(), style=self._style_dim)
            bio_pieces.append(enclose(category_txt, encloser='[]', encloser_style='dim'))

        bio_pieces.append(non_epstein_highlighter(Text(self.info, BIO_STYLE)) if self.info else QUESTION_MARKS_TXT)
        bio_pieces.append(self.alt_links_txt)
        return join_texts(bio_pieces)

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
        return self.email_addresses + self.unique_phraseologies

    @property
    def name_with_link(self) -> Text:
        """Colored name with hyperlink if applicable (otherwise just colored name)."""
        if self._urls:
            return ExternalLink(self._urls[0], self.name, link_style=self._style_bold).link
        else:
            return Text(self.name, self._style_bold)

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

            if len(self.name) >= MIN_LEN_FOR_OPTIONAL_LAST_CHAR and not self.is_organization:
                pattern += '?'

        return as_pattern(pattern)

    @property
    def _identifier(self) -> str:
        """`LoggingEntity` abstract method implementation."""
        return self.name

    @property
    def _middle_initial(self) -> str:
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

        if ' ' in self.name and self.match_partial is not None:
            name = remove_question_marks(self.name)  # TODO: this sucks
            first_name = extract_first_name(name)
            last_name = extract_last_name(name)
            name_patterns.append(as_pattern(f"{last_name},? {first_name}"))  # Reversed name

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

        def add_prop(f, value):
            if self.emailer_pattern:
                props.append(f"{f.name}={value}")
            else:
                props.append(value)

        for _field in fields(self):
            if _field.name == 'name':
                add_prop(_field, constantize_name(getattr(self, _field.name)))
            elif (value := getattr(self, _field.name)) and not _field.name.endswith('regex'):
                if _field.name.endswith('pattern'):
                    value = f'r"{value}"'
                else:
                    value = quote(constantize_names(str(value)))
                    value = ('f' + value) if '{' in value else value

                add_prop(_field, value)

        props.append(f'highlight_pattern=r"{self.highlight_pattern}"')
        return props

    @property
    def _style_bold(self) -> str:
        return self.style if 'bold' in self.style else f"{self.style} bold".strip()

    @property
    def _style_no_bold(self) -> str:
        return self.style.replace('bold' )

    @property
    def _style_dim(self) -> str:
        return self.style if 'dim' in self.style else f'{self.style} dim'

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
    def build_name_lookup(cls, contacts: list[Self]) -> dict[Name, Self]:
        """Dict of `Contact` objects keyed by contact name."""
        return {c.name: c for c in contacts}

    @classmethod
    def _repr_string(cls, contact_infos: list[Self]) -> str:
        """Print a list of `Contact` objects to a python string that can recreate them when executed."""
        return '[\n' + indented([repr(contact) for contact in contact_infos], 4) + '\n],'


def acronym(name: str, description: str = '', **kwargs) -> Entity:
    """Like organization() but auto-generates a regex matching the org's initials."""
    initials = [word[0] for word in name.split() if word[0].isupper()]
    initials_pattern = ''.join([fr"{letter}\.?" for letter in initials])

    return organization(
        ''.join(initials),
        join_truthy(name, description, ', '),
        join_patterns([initials_pattern, name]),
        **kwargs
    )


# TODO: make class method (?)
def organization(name: str, description: str = '', emailer_pattern: str = '', **kwargs) -> Entity:
    if (suffix_match := COMPANY_SUFFIX_REGEX.match(name)) and not emailer_pattern:
        suffix = suffix_match.group(1)
        emailer_pattern = name.removesuffix(suffix)

        if not MGMT_REGEX.search(suffix):
            if suffix.startswith(','):
                suffix = suffix.replace(',', ',?')
            else:
                suffix = f",?{suffix}"

        if suffix.endswith('.'):
            suffix = suffix.replace('.', r'\.?')

        emailer_pattern += fr"({suffix})?"

    kwargs['is_emailer'] = kwargs.get('is_emailer', False)
    return Entity(name, description, emailer_pattern, is_organization=True, **kwargs)


def epstein_co(name: str, emailer_pattern: str = '', description: str = '', **kwargs) -> Entity:
    return organization(name, join_truthy('Epstein company', description), emailer_pattern, **kwargs)


def epstein_trust(
    name: str,
    emailer_pattern: str = '',
    beneficiaries: list[str] | None = None,
    trustees: list[str] | None = None,
) -> Entity:
    """One of Epstein's financial trust entities."""
    name = f"Jeffrey E. Epstein {name} Trust" if is_integer(name) else name
    beneficiary_str = ''

    if beneficiaries:
        if len(beneficiaries) == 1:
            beneficiary_str = f"sole beneficiary {beneficiaries[0]}"
        else:
            beneficiary_str = f"beneficiaries {', '.join(beneficiaries)}"

    if trustees:
        beneficiary_str = join_truthy(beneficiary_str, f"trustees: " + ', '.join(trustees), ', ')

    beneficiary_str = f", {beneficiary_str}" if beneficiary_str else ''
    return organization(name, f'Epstein financial trust{beneficiary_str}', emailer_pattern)


def law_enforcement(name: str, emailer_pattern: str = '', description: str = '', **kwargs) -> Entity:
    return organization(name, description or LAW_ENFORCEMENT, emailer_pattern, is_interesting=False, **kwargs)


_DEBUG_EXCLUDED_PARTIAL_NAMES = defaultdict(int)
