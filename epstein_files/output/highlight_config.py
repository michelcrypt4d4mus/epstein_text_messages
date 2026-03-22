"""
Configuration of keyword color highlighting which also contains regexes used to identify
email sendersa and recipients in email headers.
"""
import re
from typing import Sequence

from rich.console import Console
from rich.text import Text

from epstein_files.documents.config.categories.government import FBI_REPORT_FIELDS
from epstein_files.documents.documents.categories import (CATEGORY_STYLES, CATEGORY_STYLE_MAPPING,
     DEFAULT_CATEGORY_STYLE)
from epstein_files.documents.emails.constants import (EMAIL_HEADER_FIELD_PATTERNS, QUOTE_INDENT_CHAR_GROUP,
     REPLY_REGEX, SENT_FROM_REGEX, XML_STRIPPED_MSG)
from epstein_files.output.highlighted_names import HighlightGroup, HighlightedNames, HighlightPatterns, ManualHighlight
from epstein_files.people.config import HIGHLIGHTED_NAMES, VICTIM_COLOR
from epstein_files.people.entity import Entity, Organization
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import flatten, sort_dict
from epstein_files.util.helpers.rich_helpers import QUESTION_MARKS_TXT
from epstein_files.util.helpers.string_helper import indented, join_patterns
from epstein_files.util.logging import logger

DATE_PATTERN = r"\d{1,4}[-/]\d{1,2}[-/]\d{2,4}"
TIME_PATTERN = r"\d{1,2}:\d{2}:\d{2}( [AP]M)?"
FINANCIAL_COLOR = 'dark_sea_green2'


HIGHLIGHT_GROUPS: Sequence[HighlightGroup] = [
    # These have to come first to get both stylings applied to the email subjects
    ManualHighlight(
        label='email_subject',
        style='light_yellow3',
        pattern=r"^(> )?(Classification|Flag|Objet\s?|Subject|Sujet\s?): (?P<email_subject>.*)",
    ),
    ManualHighlight(
        label='legal_question',
        style='wheat4',
        pattern=r"^(Q\. )(?P<legal_question>.{,500}?)(?=^A\.)",
        regex_flags=re.DOTALL | re.MULTILINE,
    ),

    *HIGHLIGHTED_NAMES,

    # HighlightedPatterns not HighlightedNames bc of word boundary (\b) issue with '#', '(', etc.
    HighlightPatterns(
        label='dollars',
        style=FINANCIAL_COLOR,
        patterns=[
            r"[€$£][\dO,.]+(\s*(bn|[bm](illl?ion|m)?|k|thousand))?( dollars?)?",
            r"[\dO,.]+\s*(GBP|euros?|[bm]illl?ion( (dollars|euros)?)?( loan)?)",
        ]
    ),
    HighlightPatterns(
        label='metoo',
        style=VICTIM_COLOR,
        patterns=[r"#metoo"]
    ),
    HighlightPatterns(
        label='unknown',
        style='cyan',
        patterns=[r'\(unknown\)']
    ),

    # Highlight regexes for things other than names, only used by RegexHighlighter pattern matching
    HighlightPatterns(
        label='financial',
        style=FINANCIAL_COLOR,
        use_word_boundary=True,
        patterns=[
            r"1040",
            r"accountant",
            r"accounting firm",
            r"American Express",
            r"Amex",
            r"alterna[tv]i[tv]e finance",
            r"((anti )?money )?launder(s?|ers?|ing)?( money)?",
            r"(?<!(alfa|ture|hase|rahi|sche|sica)\s)bank(?!\s+(Leumi|of|secrecy))",
            r"Black Sc?holes",
            r"brokerage",
            r"capital controls",
            r"C[EF]O",
            r"charit(ies|y)",
            r"Chief (Executive|Financ(e|ial)|Investment) Officer",
            r"(co-?)?founder",
            r"convertible note",
            r"donor advised fund",
            r"EBITDA",
            r"equities",
            r"executor",
            r"estate",
            r"fintech",
            r"hedge fund",
            r"(income )?tax(e[ds])?( (abatement|code|return))?",
            r"ISDA",
            r"(?<!Kyara\s)invest(ment|or)s?(\sadvis[eo]r[sy]?)?",
            r"(junk )?bond",
            r"K-[12]",
            r"Managing Director",
            r"Mastercard",
            r"money",
            r"(naked )?shorting",
            r"NASDAQ",
            r"options trad(er|ing)",
            r"philanthrop(i(es|st)|y)",
            r"ponz[il] scheme",
            r"preferreds",
            r"Series (7|30)",
            r"securities(?! ((&|and) Exchange|fraud))",
            r"sovereign (wealth )?fund",
            r"stock market",
            r"Trust(ee| Estate)s?",
            r"Trust Agreement",
            r"(?-i:VAT)",
            r"Wall Street(?! Jour)",
            r"warrants",
            r"wire transfer",
        ]
    ),
    HighlightPatterns(
        label='legal',
        style='pale_turquoise4',
        use_word_boundary=True,
        patterns=[
            r"affidavit",
            r"autopsy",
            fr"^{CASE_ID_REGEX.pattern}.*",
            CASE_ID_REGEX.pattern,
            r"(civil )?litigation",
            r"constitution(al(ly)?)?",
            r"de novo",
            r"deposition",
            r"EDGAR (Filing|Search)",  # SEC database is EDGAR
            r"(federal|state) judge",
            r"General Counsel",
            r"green card",
            r"law partner",
            r"lawyer",
            r"Notary Public",
            r"Page \d+ of \d+",
            r"passport",
            r"testimony",
            r"(eye)?witness(es)?",
        ]
    ),
    HighlightPatterns(
        label='locations',
        style='cornsilk1',
        use_word_boundary=True,
        patterns=STATE_NAME_PATTERNS + [
            r"Arizona(?! State U)",
            r"Aspen",
            r"Berkeley",
            r"Boca Raton",
            r"Boston",
            r"Brooklyn",
            r"Cape Cod",
            r"Charlottesville",
            r"(?<!District\sof\s)Florida",
            r"F(or)?t\.? Lauderdale",
            r"Jersey City",
            r"Los Angeles(?! Times)",
            r"Loudoun County?",
            r"Manhattan(?!\s+DA)",
            r"Martha's Vineyard",
            r"Miami(?!\s?Herald)",
            r"Nantucket",
            r"NY(C| State)",
            r"Orange County",
            r"Palo Alto",
            r"Phoenix",
            r"Portland",
            r"San Francisco",
            r"Santa Monica",
            r"Sant[ae] Fe",
            r"Telluride",
            r"Teterboro",
            r"Texas(?! A&M)",
            r"Toronto",
            r"Tu(sc|cs)on",
            r"Vancouver",
            r"Virginian?(?! (L\.?)? (Giuffre|Roberts))",
            r"Washington( D\.?C)?(?! Post)",
            r"Westchester",
        ],
    ),
    HighlightPatterns(
        label='phone_number',
        style='bright_green',
        patterns=[
            r"\+?(1?\(?\d{3}\)?[-\s]\d{3}[-\s]\d{4}|\d{2}[-\s]\(?0?\)?\d{2}[-\s]\d{4}[-\s]\d{4})",
            r"(\b|\+)[\d+]{10,12}\b",
        ],
    ),
     HighlightPatterns(
        label='header_field',  # email_header (or FBI)
        style='plum4',
        patterns=[
            fr"^([>»•\s]{{,4}}({join_patterns(EMAIL_HEADER_FIELD_PATTERNS)}):|on behalf of)",
            fr"^({join_patterns(FBI_REPORT_FIELDS)}):",
        ],
    ),
    HighlightPatterns(
        label='http_links',
        style=f'{ARCHIVE_LINK_COLOR} underline',
        patterns=[r"https?:[^\s]+"],
    ),
    HighlightPatterns(
        label='quoted_reply_line',
        style='dim',
        patterns=[
            REPLY_REGEX.pattern,
            r"^(Best|Cheers),?\nJeremy",
            r"^@JeremyRubin",
            r"^(> )?wrote:$",
            r"CONFIDENTIAL FOR ATTORNEY'S EYES ONLY(\nDO NOT COPY)?",
            r"PRIVILEGED - ATTORNEY WORK.*(\nCONFIDENTIAL - SUBJECT TO.*)?",
            r"Managing Partner - Crypto Currency Partners",  # brock pierce
            r"Please use this email for.*general Media Lab.*",  # Joi Ito
            r"-Austin\nAustin Hill - B..dder.*(\n.*B92ED3E3)?",  # Austin Hill
            r"^(Please note my new email address?:?.*|Follow me on twitter @[Il]hsummers|www.larrysummers.com)$", # larry summers
            r"^W dniu wt.*",  # Russian cyrillic
        ],
    ),
    HighlightPatterns(
        label='redacted',
        style='grey58',
        patterns=[fr"{REDACTED}|<?Privileged - Redacted>?"],
    ),
    HighlightPatterns(
        label='sent_from_device',
        style='light_cyan3 italic dim',
        patterns=[fr"{QUOTE_INDENT_CHAR_GROUP}*{SENT_FROM_REGEX.pattern}"],
    ),
    HighlightPatterns(
        label='snipped_signature',
        style='gray35 italic dim',
        patterns=[fr'<\.\.\.(snipped|trimmed).*\.\.\.>|{XML_STRIPPED_MSG}'],
    ),
    HighlightPatterns(
        label='timestamp_2',
        style=TIMESTAMP_STYLE,
        patterns=[
            fr"({DATE_PATTERN} )?{TIME_PATTERN}",
            fr"\b{DATE_PATTERN}\b",
        ],
    ),

    # Manual regexes
    ManualHighlight(
        label='email_attachments',
        style='gray30 italic',
        pattern=r"^(> )?(Attach(ed|ments)|[Il]nline-[Il]mages): (?P<email_attachments>.*)",
    ),
    ManualHighlight(
        label='email_timestamp',
        style=TIMESTAMP_STYLE,
        pattern=r"^(> )?(Date|Envoy[eé] ?|Sent): (?P<email_timestamp>.*)",
    ),
]

HIGHLIGHTED_ENTITIES = flatten([hn.entities for hn in HIGHLIGHTED_NAMES])


def get_entity(name: str) -> Entity | None:
    if (group := get_highlight_group_for_name(name)) and isinstance(group, HighlightedNames):
        return group.entities_by_name.get(name)


def get_highlight_group_for_name(name: str | None) -> HighlightGroup | None:
    if not name:
        return None

    for highlight_group in HIGHLIGHT_GROUPS:
        if highlight_group.regex.search(name):
            return highlight_group


def get_style_for_category(category: str) -> str | None:
    """
    First check `CATEGORY_STYLES`, then check if there's a mapping in `CATEGORY_STYLE_MAPPING`,
    and finally just match the category name to the `HighlightedNames.label`.
    """
    if category in CATEGORY_STYLES:
        return CATEGORY_STYLES[category]

    for highlight_group in HIGHLIGHT_GROUPS:
        if highlight_group.label == CATEGORY_STYLE_MAPPING.get(category, category):
            return highlight_group.style


def get_style_for_name(name: str | None, default_style: str = DEFAULT_NAME_STYLE, allow_bold: bool = True) -> str:
    highlight_group = get_highlight_group_for_name(name or UNKNOWN)
    style = highlight_group.style if highlight_group else default_style
    style = style if allow_bold else style.replace('bold', '').strip()
    # logger.debug(f"get_style_for_name('{name}', '{default_style}', '{allow_bold}') yielded '{style}'")
    return style


def styled_category(category: str | None) -> Text:
    if category:
        return Text(category.split('_')[0], get_style_for_category(category) or DEFAULT_CATEGORY_STYLE)
    else:
        return QUESTION_MARKS_TXT


def styled_name(name: str | None, default_style: str = DEFAULT_NAME_STYLE) -> Text:
    return Text(name or UNKNOWN, style=get_style_for_name(name, default_style=default_style))


def _print_highlighted_names_repr() -> None:
    for hn in HIGHLIGHTED_NAMES:
        print(indented(repr(hn)) + ',')
        print(f"pattern: '{hn.regex.pattern}'")

    import sys
    sys.exit()


if args._debug_highlight_patterns:
    for c in HIGHLIGHTED_ENTITIES:
        print(repr(c))
