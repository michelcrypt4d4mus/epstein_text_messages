"""
Classes holding information that creates color highlighting via `rich.Highlighter`
regex mechanism as well as identify individuals in email headers etc.
"""
import json
import re
from abc import ABC
from dataclasses import dataclass, field

from epstein_files.people.entity import Entity
from epstein_files.people.names import Name, constantize_name
from epstein_files.util.constant.strings import REGEX_STYLE_PREFIX
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import build_name_lookup, without_falsey
from epstein_files.util.helpers.string_helper import as_pattern, capture_group_marker, join_patterns
from epstein_files.util.logging import logger


@dataclass(kw_only=True)
class HighlightGroup(ABC):
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
    _capture_group_marker: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            raise ValueError(f'Missing label for {self}')

        self._capture_group_label = self.label.lower().replace(' ', '_').replace('-', '_')
        self._capture_group_marker = capture_group_marker(self._capture_group_label)
        self.theme_style_name = f"{REGEX_STYLE_PREFIX}.{self._capture_group_label}"


@dataclass(kw_only=True)
class HighlightPatterns(HighlightGroup):
    """
    Color highlighting for things other than people's names (e.g. phone numbers, email headers).

    Attributes:
        patterns (list[str]): regex patterns identifying strings matching this group
        regex_flags (re.RegexFlag): flags to use when compiling the patterns to an `re.Pattern`
        use_word_boundary (bool, optional): if True, patterns can only match before/after word boundary `\b`
    """
    patterns: list[str] = field(default_factory=list)
    regex_flags: re.RegexFlag = re.IGNORECASE | re.MULTILINE
    use_word_boundary: bool = False
    _pattern: str = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        if not self.label:
            raise ValueError(f"No label provided for {repr(self)}")

        self.patterns = [as_pattern(p) for p in self.patterns]
        self._pattern = join_patterns(self.patterns)

        if self.use_word_boundary:
            self._pattern = fr"\b(({self._pattern})s?)\b"

        self.regex = self.compile_patterns(self._pattern)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(label='{self.label}', pattern='{self._pattern}', style='{self.style}')"

    def compile_patterns(self, pattern: str) -> re.Pattern:
        try:
            return re.compile(fr"({self._capture_group_marker}{pattern})", self.regex_flags)
        except Exception as e:
            logger.error(f"Failed to compile regex '{pattern}'\n\nTrying each piece individually...")

            for p in self.patterns:
                logger.warning(f"Attempting to compile '{p}'...")
                re.compile(p)

            raise e


@dataclass(kw_only=True)
class HighlightedNames(HighlightPatterns):
    """
    Encapsulates info about people, places, and other strings we want to highlight with RegexHighlighter.
    Constructor must be called with either an 'emailers' arg or a 'pattern' arg (or both).

    Attributes:
        category (str): optional string to use as an override for `self.label` in some contexts
        entities (list[Entity]): optional `Entity` objects that will provide highlight regexes
        entities_by_name (dict[Name, Entity]): lookup dictionary for `Entity` objects
    """
    category: str = ''
    entities: list[Entity] = field(default_factory=list)
    entities_by_name: dict[Name, Entity] = field(init=False)
    flags: re.RegexFlag = re.IGNORECASE

    def __post_init__(self):
        if not (self.patterns or self.entities):
            raise ValueError(f"Must provide either 'contacts' or 'patterns' arg.")
        elif not self.label:
            if len(self.entities) == 1 and self.entities[0].name:
                self.label = self.entities[0].name
            else:
                raise ValueError(f"No label provided for {repr(self)}")

        super().__post_init__()
        with_contacts_pattern = join_patterns([c.highlight_pattern for c in self.entities] + self.patterns)
        self._pattern = fr"\b(({with_contacts_pattern})s?)\b"
        self.regex = self.compile_patterns(self._pattern)
        self.entities_by_name = build_name_lookup(self.entities)

        for entity in self.entities:
            entity.category = self.category_str
            entity.style = self.style

        if args._debug_highlight_patterns:
            logger.debug(repr(self))

    @property
    def category_str(self) -> str:
        if self.category:
            return self.category
        elif len(self.entities) == 1 and self.label == self.entities[0].name:
            return ''
        else:
            return self.label.replace('_', ' ')

    def info_for(self, name: str, include_category: bool = False) -> str | None:
        """Label and additional info for 'name' if 'name' is in `self.contacts`."""
        info_pieces = [self.category_str] if include_category else []

        if (entity := self.entities_by_name.get(name)):
            # Don't prefix with category if category is in the info string
            if info_pieces and info_pieces[0] in entity.info:
                info_pieces = [entity.info]
            else:
                info_pieces.append(entity.info)

        info_pieces = without_falsey(info_pieces)
        return ', '.join(info_pieces) if info_pieces else None

    def __repr__(self) -> str:
        s = f"{type(self).__name__}("

        for property in ['label', 'style', 'category', 'patterns', 'entities', '_pattern']:
            value = getattr(self, property)

            if not value or (property == 'label' and len(self.entities) == 1 and not self.patterns):
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
            elif isinstance(value, list) and value and isinstance(value[0], Entity):
                s += '[\n        '
                s += f"    {', '.join([c.name for c in value])}"
                s += ',\n    ],'
            else:
                s += f"{json.dumps(value)},"

        return s + '\n)'

    def __str__(self) -> str:
        return super().__str__()


@dataclass(kw_only=True)
class ManualHighlight(HighlightGroup):
    """For when you can't construct the regex."""
    pattern: str
    regex_flags: re.RegexFlag = re.MULTILINE

    def __post_init__(self):
        super().__post_init__()

        if self._capture_group_marker not in self.pattern:
            raise ValueError(f"Label '{self.label}' must appear in regex pattern '{self.pattern}'")

        self.regex = re.compile(self.pattern, self.regex_flags)
