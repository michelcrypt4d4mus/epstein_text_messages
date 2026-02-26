import re
from dataclasses import dataclass, field, fields
from typing import Self

from epstein_files.util.constant.names import (NAMES_TO_NOT_PARTIALLY_MATCH, SIMPLE_NAME_REGEX, Name,
     constantize_name, name_variations)
from epstein_files.util.constant.strings import INDENT_NEWLINE, INDENTED_JOIN, LAW_ENFORCEMENT
from epstein_files.util.helpers.data_helpers import constantize_names
from epstein_files.util.helpers.string_helper import as_pattern, indented, quote, remove_question_marks
from epstein_files.util.logging import logger

MIN_LEN_FOR_OPTIONAL_LAST_CHAR = 5
LLC_OR_INC = re.compile(r".*?(,? (Inc\.?|LLC))$")


@dataclass
class Contact:
    """
    Attributes:
        name (str): Person or organization name
        info (str, optional): biographical info about this person
        emailer_pattern (str, optional): manually constructed regex pattern to match this person in email headers
        emailer_regex (re.Pattern): pattern that matches this person's name in various variations
    """
    name: str
    info: str = ''
    emailer_pattern: str = ''
    emailer_regex: re.Pattern = field(init=False)
    highlight_regex: re.Pattern = field(init=False)
    is_junk: bool = False  # TODO: this sucks
    is_organization: bool = False
    link_to_bio: str = ''
    # jmail_url: str

    def __post_init__(self):
        try:
            self.emailer_regex = re.compile(self.pattern, re.IGNORECASE)
            self.highlight_regex = re.compile(fr"\b({self.highlight_pattern})\b", re.IGNORECASE)
        except re.error as e:
            logger.fatal(f"failed to compile emailer_regex for {self.name}: {e}")
            raise e

    @property
    def highlight_pattern(self) -> str:
        """
        `self.emailer_pattern` extended with first/last name variations.
        Used for color highlighting with `HighlightedNames` / `EpsteinHighlighter`.
        """
        if self.is_junk or self.is_organization:
            return self.pattern

        name_patterns = [self.pattern]

        for partial_name in name_variations(self.name):
            if partial_name.lower() not in NAMES_TO_NOT_PARTIALLY_MATCH and SIMPLE_NAME_REGEX.match(partial_name):
                name_patterns.append(as_pattern(partial_name))
                logger.debug(f"Contact('{self.name}'): appending partial name '{partial_name}'")

        return '|'.join(name_patterns)

    @property
    def pattern(self) -> str:
        if self.emailer_pattern:
            pattern = self.emailer_pattern
        else:
            pattern = remove_question_marks(self.name)  # TODO: this sucks

            if len(pattern) >= MIN_LEN_FOR_OPTIONAL_LAST_CHAR:
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


def company(name: str, description: str, emailer_pattern: str = '', **kwargs) -> Contact:
    return Contact(name, description, emailer_pattern, is_organization=True, **kwargs)


def epstein_trust(name: str, emailer_pattern: str = '', beneficiaries: list[str] | None = None) -> Contact:
    beneficiary_str = ''

    if beneficiaries:
        if len(beneficiaries) == 1:
            beneficiary_str = f"with sole beneficiary {beneficiaries[0]}"
        else:
            beneficiary_str = f"with beneficiaries {','.join(beneficiaries)}"

    beneficiary_str = f", {beneficiary_str}" if beneficiary_str else ''
    return Contact(name, f'Epstein financial trust{beneficiary_str}', emailer_pattern, is_organization=True)


def epstein_co(name: str, emailer_pattern: str = '') -> Contact:
    if (llc_or_inc_match := LLC_OR_INC.match(name)) and not emailer_pattern:
        suffix = llc_or_inc_match.group(1)
        emailer_pattern = name.removesuffix(suffix)
        # print(f"suffix='{suffix}', emailer_pattern='{emailer_pattern}'")

        if suffix.startswith(','):
            suffix = suffix.replace(',', ',?')

        if suffix.endswith('.'):
            suffix = suffix.replace('.', r'\.?')

        emailer_pattern += fr"({suffix})?"

    return Contact(name, 'Epstein company', emailer_pattern, is_organization=True)


def law_enforcement(name: str, emailer_pattern: str = '') -> Contact:
    return Contact(name, LAW_ENFORCEMENT, emailer_pattern=emailer_pattern, is_organization=True)
