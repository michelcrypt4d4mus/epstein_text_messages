import re
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Self

from rich.text import Text

from epstein_files.util.constant.names import (NAMES_TO_NOT_HIGHLIGHT, SIMPLE_NAME_REGEX, Name,
     constantize_name, extract_first_name, extract_last_name, reversed_name)
from epstein_files.util.constant.strings import INDENT_NEWLINE, INDENTED_JOIN
from epstein_files.util.helpers.data_helpers import constantize_names
from epstein_files.util.helpers.string_helper import indented, quote, remove_question_marks


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
    is_junk: bool = False  # TODO: this sucks
    # jmail_url: str

    @property
    def highlight_pattern(self) -> str:
        """`self.emailer_pattern` extended with first/last name variations."""
        name_patterns = [self.pattern]

        if self.is_junk or ' ' not in self.name:
            return name_patterns[0]

        if ' ' in self.name:
            for partial_name in [reversed_name(self.name), extract_first_name(self.name), extract_last_name(self.name)]:  # Order matters
                if partial_name.lower() not in NAMES_TO_NOT_HIGHLIGHT and SIMPLE_NAME_REGEX.match(partial_name):
                    name_patterns.append(partial_name.replace(' ', r"\s+"))

        return '|'.join(name_patterns)

    @property
    def pattern(self) -> str:
        return self.emailer_pattern or remove_question_marks(self.name).replace(' ', r"\s+")

    def __post_init__(self):
        if self.name is None:
            raise ValueError(f"ContactInfo.name cannot be None!")

        emailer_pattern = self.emailer_pattern or f"{self.name}?"
        self.emailer_regex = re.compile(emailer_pattern, re.IGNORECASE)

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
        """Dict keyed by contact name."""
        return {c.name: c for c in contacts}

    @classmethod
    def repr_string(cls, contact_infos: list[Self]) -> str:
        return '[\n' + indented(',\n'.join([repr(contact) for contact in contact_infos]), 4) + '\n],'
