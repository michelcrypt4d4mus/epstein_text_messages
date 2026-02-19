"""
HTML file paths and URLs for files built by `epstein_generate`.
"""
from enum import auto, StrEnum
from pathlib import Path
from typing import Self

from rich.markup import escape
from rich.text import Text

from epstein_files.util.constant.strings import (AUX_SITE_LINK_STYLE, DOJ_2026_TRANCHE,
     EPSTEIN_FILES_NOV_2025, HOUSE_OVERSIGHT_TRANCHE)
from epstein_files.util.helpers.link_helper import link_text_obj, parenthesize
from epstein_files.util.logging import logger

HTML_DIR = Path('docs')
EMAILERS_TABLE_PNG_PATH = HTML_DIR.joinpath('emailers_info_table.png')

# Github URLs
GH_REPO_NAME = 'epstein_text_messages'
GH_PAGES_BASE_URL = 'https://michelcrypt4d4mus.github.io'
GH_PROJECT_URL = f'https://github.com/michelcrypt4d4mus/{GH_REPO_NAME}'
GH_MASTER_URL = f"{GH_PROJECT_URL}/blob/master"
ATTRIBUTIONS_URL = f'{GH_MASTER_URL}/epstein_files/util/constants.py'
EXTRACTS_BASE_URL = f'{GH_MASTER_URL}/emails_extracted_from_legal_filings'
BASE_URL = f"{GH_PAGES_BASE_URL}/{GH_REPO_NAME}"
TO_FROM = 'to/from'


class SiteType(StrEnum):
    CHRONOLOGICAL_EMAILS = auto()
    CURATED = auto()
    CURATED_CHRONOLOGICAL = auto()
    DOJ_FILES = auto()
    GROUPED_EMAILS = auto()
    #JSON_FILES = auto()
    JSON_METADATA = auto()
    MOBILE = auto()
    OTHER_FILES_TABLE = auto()
    TEXT_MESSAGES = auto()
    WORD_COUNT = auto()

    @classmethod
    def all_urls(cls) -> dict[Self, str]:
        return {site_type: cls.get_url(site_type) for site_type in cls}

    @classmethod
    def all_links(cls) -> dict['SiteType', Text]:
        return {site_type: SiteType.link_txt(site_type) for site_type in SITE_DESCRIPTIONS.keys()}

    @classmethod
    def build_path(cls, site_type: Self) -> Path:
        return HTML_DIR.joinpath(HTML_BUILD_FILENAMES[site_type])

    @classmethod
    def get_url(cls, site_type: Self) -> str:
        return f"{BASE_URL}/{cls.build_path(site_type).name}"

    @classmethod
    def link_txt(cls, site_type: Self) -> Text:
        description = SITE_DESCRIPTIONS[site_type]
        extra_info = ''

        if cls._is_lesser_site(site_type):
            style = 'gray30'# 'light_pink4'
        else:
            style = AUX_SITE_LINK_STYLE

        if ':' in description:
            description, extra_info = SITE_DESCRIPTIONS[site_type].split(':')
            extra_info = Text(escape(extra_info), style=f'plum4 italic')
            extra_info = Text(' ').append(parenthesize(extra_info, 'color(147) dim'))

        style_mod = '' if cls._is_lesser_site(site_type) else 'bold'
        link = link_text_obj(SiteType.get_url(site_type), escape(description), f"{style} {style_mod}")
        link.append(extra_info)
        return link

    @classmethod
    def _is_lesser_site(cls, site_type: Self) -> bool:
        return site_type in [cls.DOJ_FILES, cls.JSON_METADATA]  #+ [cls.JSON_FILES]


HTML_BUILD_FILENAMES = {
    SiteType.CHRONOLOGICAL_EMAILS:  f'chronological_emails.html',
    SiteType.CURATED:               f'index.html',
    SiteType.CURATED_CHRONOLOGICAL: f"curated_chronological.html",
    SiteType.DOJ_FILES:             f'doj_2026-01-30_non_email_files.html',
    SiteType.GROUPED_EMAILS:        f'emails_grouped_by_counterparty.html',
    SiteType.JSON_METADATA:         f'metadata.json',
    SiteType.MOBILE:                f'curated_mobile.html',
    SiteType.OTHER_FILES_TABLE:     f'other_files_table.html',
    SiteType.TEXT_MESSAGES:         f'text_messages_{EPSTEIN_FILES_NOV_2025}.html',
    SiteType.WORD_COUNT:            f'communication_word_count.html',
#     SiteType.EPSTEIN_WORD_COUNT: 'epstein_texts_and_emails_word_count.html'),
}

# Order matters, it's the order the links are shown in the header
# Colons are used to break and parenthesize display
SITE_DESCRIPTIONS = {
    SiteType.CURATED:               f"curated:by my interests, files grouped by type",
    SiteType.CURATED_CHRONOLOGICAL: f"curated chronological:all types intermingled",
    SiteType.GROUPED_EMAILS:        f"emailers:emails grouped by counterparty",
    SiteType.CHRONOLOGICAL_EMAILS:  f"emails:pure chronological order",
    SiteType.TEXT_MESSAGES:         f"text messages:{HOUSE_OVERSIGHT_TRANCHE}",
    SiteType.MOBILE:                f"mobile:an attempt at mobile compatibility",
    SiteType.OTHER_FILES_TABLE:     f"other:files that are not emails or texts",
    SiteType.WORD_COUNT:            f"word count:of Epstein's communications",
    SiteType.DOJ_FILES:             f"doj files:raw OCR text {DOJ_2026_TRANCHE}",
    SiteType.JSON_METADATA:         f"metadata:author bios, attribution explanations",
}


###########################################
########  Internal sections links  ########
###########################################
SELECTIONS_FROM = 'Selections from '
HIS_EMAILS = 'His Emails'
HIS_TEXT_MESSAGES = 'His Text Messages'
FILEs_THAT_ARE_NEITHER_EMAILS_NOR = 'Files That Are Neither Emails Nor Text Messages'


class PageSections(StrEnum):
    EMAILS = auto()
    OTHER_FILES = auto()
    TEXT_MESSAGES = auto()

# Search terms that take you to the desired section via magic URL comment arg
SECTION_ANCHORS = {
    PageSections.EMAILS: SELECTIONS_FROM + HIS_EMAILS,
    PageSections.TEXT_MESSAGES: SELECTIONS_FROM + HIS_TEXT_MESSAGES,
    PageSections.OTHER_FILES: FILEs_THAT_ARE_NEITHER_EMAILS_NOR,
}


def make_clean() -> None:
    """Delete all build artifacts."""
    for site_type in SiteType:
        build_file = SiteType.build_path(site_type)

        for file in [build_file, Path(f"{build_file}.txt")]:
            if file.exists():
                logger.warning(f"Removing build file '{file}'...")
                file.unlink()
