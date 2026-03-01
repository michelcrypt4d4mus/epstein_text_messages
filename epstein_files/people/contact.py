import re
from dataclasses import dataclass, field, fields
from typing import Literal, Self

from rich.text import Text

from epstein_files.util.constant.names import Name, constantize_name, extract_first_name, extract_last_name
from epstein_files.util.constant.strings import INDENT_NEWLINE, INDENTED_JOIN, LAW_ENFORCEMENT, PartialName
from epstein_files.util.helpers.data_helpers import constantize_names
from epstein_files.util.helpers.link_helper import link_text_obj
from epstein_files.util.helpers.string_helper import as_pattern, indented, is_integer, quote, remove_question_marks, join_truthy
from epstein_files.util.logging import logger

MIN_LEN_FOR_OPTIONAL_LAST_CHAR = 5
COMPANY_SUFFIX_REGEX = re.compile(r".*?(,? (Inc\.?|LLC|Mgmt|Management))$")
SIMPLE_NAME_REGEX = re.compile(r"^[-\w, ]+$", re.IGNORECASE)


@dataclass
class Contact:
    """
    Attributes:
        name (str): Person or organization name
        info (str, optional): biographical info about this person
        emailer_pattern (str, optional): manually constructed regex pattern to match this person in email headers
        category (str, optional): category of this entity
        style (str, optional): style to use when printing this entity's name
        emailer_regex (re.Pattern): pattern that matches this person's name in email headers
        highlight_regex (re.Pattern): pattern that matches this person's name in various variations for highlightihng
        is_emailer (bool): should email headers be scanned for this entity
        is_interesting (bool): should a biographical entry be generated for this panel in the chronological view
        is_junk (bool): for junk email
        is_organization (bool): if this is a company or group, don't try to match first and last versions of its name
        link_to_bio (str, optional): a link to some info about this entity
        match_partial (PartialName | None): whether to also match this entity's first and last names
    """
    name: str
    info: str = ''
    emailer_pattern: str = ''
    category: str = ''
    style: str = ''
    emailer_regex: re.Pattern = field(init=False)
    highlight_regex: re.Pattern = field(init=False)
    is_emailer: bool = True
    is_interesting: bool = True  # Eligible for bio panel
    is_junk: bool = False  # TODO: this sucks
    is_organization: bool = False
    link_to_bio: str = ''
    match_partial: PartialName | None = 'last'
    # jmail_url: str

    def __post_init__(self):
        if self.is_organization:
            self.match_partial = None

        try:
            self.emailer_regex = re.compile(self.pattern, re.IGNORECASE)
        except re.error as e:
            logger.fatal(f"failed to compile emailer_regex for {self.name}: {e}")
            raise e

        try:
            self.highlight_regex = re.compile(fr"\b({self.highlight_pattern})\b", re.IGNORECASE)
        except re.error as e:
            logger.fatal(f"failed to compile highlight_regex for {self.name}: {e}")
            raise e

    @property
    def bio(self) -> Text:
        """Biographical info about this entity."""
        from epstein_files.output.epstein_highlighter import non_epstein_highlighter
        txt = Text('')

        if self.link_to_bio:
            txt.append(link_text_obj(self.link_to_bio, self.name, self.bold_style))
        else:
            txt.append(self.name, style=self.bold_style)

        if self.category:
            txt.append(' [', style='dim').append(self.category.lower(), style=f'{self.style} dim').append(']', style='dim')

        return txt.append(' ').append(non_epstein_highlighter(Text(self.info, style='italic grey70')))

    @property
    def bold_style(self) -> str:
        return f"{self.style} bold".strip()

    @property
    def has_bio(self) -> bool:
        return bool(self.is_interesting and self.info)

    @property
    def highlight_pattern(self) -> str:
        """
        `self.emailer_pattern` extended with first/last name variations.
        Used for color highlighting with `HighlightedNames` / `EpsteinHighlighter`.
        """
        # TODO: this sucks
        if self.is_junk:
            return self.pattern

        return '|'.join(self.name_patterns)

    @property
    def name_patterns(self) -> list[str]:
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

        logger.debug(f"Contact('{self.name}') name_patterns: '{name_patterns}'")
        return name_patterns

    @property
    def pattern(self) -> str:
        """Pattern used for matching emails, base pattern for highlights."""
        if self.emailer_pattern:
            pattern = self.emailer_pattern
        else:
            pattern = remove_question_marks(self.name)  # TODO: this sucks

            if len(pattern) >= MIN_LEN_FOR_OPTIONAL_LAST_CHAR and not self.is_organization:
                pattern = self.name + '?'

        return as_pattern(pattern)

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

    @classmethod
    def build_name_lookup(cls, contacts: list[Self]) -> dict[Name, Self]:
        """Dict of `Contact` objects keyed by contact name."""
        return {c.name: c for c in contacts}

    @classmethod
    def repr_string(cls, contact_infos: list[Self]) -> str:
        return '[\n' + indented(',\n'.join([repr(contact) for contact in contact_infos]), 4) + '\n],'


# TODO: rename organization(), make class method (?)
def company(name: str, description: str = '', emailer_pattern: str = '', **kwargs) -> Contact:
    if (suffix_match := COMPANY_SUFFIX_REGEX.match(name)) and not emailer_pattern:
        suffix = suffix_match.group(1)
        emailer_pattern = name.removesuffix(suffix)

        if suffix.startswith(','):
            suffix = suffix.replace(',', ',?')

        if suffix.endswith('.'):
            suffix = suffix.replace('.', r'\.?')

        emailer_pattern += fr"({suffix})?"

    kwargs['is_emailer'] = kwargs.get('is_emailer', False)
    return Contact(name, description, emailer_pattern, is_organization=True, **kwargs)


def epstein_co(name: str, emailer_pattern: str = '', **kwargs) -> Contact:
    return company(name, 'Epstein company', emailer_pattern, **kwargs)


def epstein_trust(
    name: str,
    emailer_pattern: str = '',
    beneficiaries: list[str] | None = None,
    trustees: list[str] | None = None,
) -> Contact:
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
    return company(name, f'Epstein financial trust{beneficiary_str}', emailer_pattern)


def law_enforcement(name: str, emailer_pattern: str = '', description: str = '') -> Contact:
    return company(name, description or LAW_ENFORCEMENT, emailer_pattern, is_interesting=False)
