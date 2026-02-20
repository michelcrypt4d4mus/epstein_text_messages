"""
Classes holding information that creates color highlighting via `rich.Highlighter`
regex mechanism as well as identify individuals in email headers etc.
"""
import json
import re
from dataclasses import dataclass, field

from epstein_files.people.contact import Contact
from epstein_files.util.constant.names import Name, constantize_name
from epstein_files.util.constant.strings import REGEX_STYLE_PREFIX
from epstein_files.util.helpers.data_helpers import without_falsey
from epstein_files.util.logging import logger


@dataclass(kw_only=True)
class HighlightGroup:
    """
    Regex and style information for things we want to highlight.

    Attributes:
        label (str): RegexHighlighter match group name
        regex (re.Pattern): regex pattern identifying strings matching this group
        style (str): Rich style to apply to text matching this group
        theme_style_name (str): The style name that must be a part of the rich.Console's theme
    """
    label: str = ''
    regex: re.Pattern = field(init=False)
    style: str
    theme_style_name: str = field(init=False)
    _capture_group_label: str = field(init=False)
    _match_group_var: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            raise ValueError(f'Missing label for {self}')

        self._capture_group_label = self.label.lower().replace(' ', '_').replace('-', '_')
        self._match_group_var = fr"?P<{self._capture_group_label}>"
        self.theme_style_name = f"{REGEX_STYLE_PREFIX}.{self._capture_group_label}"


@dataclass(kw_only=True)
class HighlightedText(HighlightGroup):
    """
    Color highlighting for things other than people's names (e.g. phone numbers, email headers).

    Attributes:
        patterns (list[str]): regex patterns identifying strings matching this group
    """
    patterns: list[str] = field(default_factory=list)
    _pattern: str = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        if not self.label:
            raise ValueError(f"No label provided for {repr(self)}")

        self._pattern = '|'.join(self.patterns)

        try:
            self.regex = re.compile(fr"({self._match_group_var}{self._pattern})", re.IGNORECASE | re.MULTILINE)
            logger.debug(self._pattern)
        except Exception as e:
            logger.error(f"Failed to compile regex for {self.label}, trying each:")

            for p in self.patterns:
                logger.warning(f"Attempting to compile '{p}'...")
                re.compile(p)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(label='{self.label}', pattern='{self._pattern}', style='{self.style}')"


@dataclass(kw_only=True)
class HighlightedNames(HighlightedText):
    """
    Encapsulates info about people, places, and other strings we want to highlight with RegexHighlighter.
    Constructor must be called with either an 'emailers' arg or a 'pattern' arg (or both).

    Attributes:
        category (str): optional string to use as an override for self.label in some contexts
        contacts (list[ContactInfo]): optional `ContactInfo` objects with names and regexes
        contacts_lookup (dict[Name, ContactInfo]): lookup dictionary for `ContactInfo` objects
        should_match_first_last_name (bool): if False don't match first/last/reversed versions of emailers
    """
    category: str = ''
    contacts: list[Contact] = field(default_factory=list)
    contacts_lookup: dict[Name, Contact] = field(default_factory=dict)
    should_match_first_last_name: bool = True  # TODO: this no longer does anything?

    def __post_init__(self):
        if not (self.patterns or self.contacts):
            raise ValueError(f"Must provide either 'emailers' or 'pattern' arg.")
        elif not self.label:
            if len(self.contacts) == 1 and self.contacts[0].name:
                self.label = self.contacts[0].name
            else:
                raise ValueError(f"No label provided for {repr(self)}")

        self.patterns = [p.replace(' ', r"[\s_]+") if '?<!' not in p else p for p in self.patterns]
        super().__post_init__()
        self._pattern = '|'.join([contact.highlight_pattern for contact in self.contacts] + self.patterns)
        self.regex = re.compile(fr"\b({self._match_group_var}({self._pattern})s?)\b", re.IGNORECASE)
        self.contacts_lookup = Contact.build_name_lookup(self.contacts)

    def category_str(self) -> str:
        if self.category:
            return self.category
        elif len(self.contacts) == 1 and self.label == self.contacts[0].name:
            return ''
        else:
            return self.label.replace('_', ' ')

    def info_for(self, name: str, include_category: bool = False) -> str | None:
        """Label and additional info for 'name' if 'name' is in `self.contacts`."""
        info_pieces = [self.category_str()] if include_category else []

        if (contact := self.contacts_lookup.get(name)):
            info_pieces.append(contact.info)

        info_pieces = without_falsey(info_pieces)
        return ', '.join(info_pieces) if info_pieces else None

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        s = f"{type(self).__name__}("

        for property in ['label', 'style', 'category', 'patterns', 'contacts']:
            value = getattr(self, property)

            if not value or (property == 'label' and len(self.contacts) == 1 and not self.patterns):
                continue

            s += f"\n    {property}="

            if isinstance(value, dict):
                s += '{'

                for k, v in value.items():
                    s += f"\n        {constantize_name(k)}: {json.dumps(v).replace('null', 'None')},"

                s += '\n    },'
            elif property == 'patterns':
                s += '[\n        '
                s += repr(value).removeprefix('[').removesuffix(']').replace(', ', ',\n        ')
                s += ',\n    ],'
            else:
                s += f"{json.dumps(value)},"

        return s + '\n)'


@dataclass(kw_only=True)
class ManualHighlight(HighlightGroup):
    """For when you can't construct the regex."""
    pattern: str

    def __post_init__(self):
        super().__post_init__()

        if self._match_group_var not in self.pattern:
            raise ValueError(f"Label '{self.label}' must appear in regex pattern '{self.pattern}'")

        self.regex = re.compile(self.pattern, re.MULTILINE)
