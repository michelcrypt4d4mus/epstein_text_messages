"""
HTML file paths and URLs for files built by `epstein_generate`.
"""
import shutil
from enum import auto, StrEnum
from pathlib import Path
from typing import Self

from rich.markup import escape
from rich.text import Text

from epstein_files.util.constant.strings import (AUX_SITE_LINK_STYLE, CHRONOLOGICAL, DOJ_2026_TRANCHE,
     EPSTEIN_FILES_NOV_2025, HOUSE_OVERSIGHT_TRANCHE)
from epstein_files.util.external_link import link_text_obj, parenthesize
from epstein_files.util.logging import logger

HTML_DIR = Path('docs')
EMAILERS_TABLE_PNG_PATH = HTML_DIR.joinpath('emailers_info_table.png')
SAMPLE_HTML_PATH = HTML_DIR.joinpath('sample.html')

# Github URLs
GH_REPO_NAME = 'epstein_text_messages'
GH_PAGES_BASE_URL = 'https://michelcrypt4d4mus.github.io'
GH_PROJECT_URL = f'https://github.com/michelcrypt4d4mus/{GH_REPO_NAME}'
GH_MASTER_URL = f"{GH_PROJECT_URL}/blob/master"
ATTRIBUTIONS_URL = f'{GH_MASTER_URL}/epstein_files/util/constants.py'
EXTRACTS_BASE_URL = f'{GH_MASTER_URL}/emails_extracted_from_legal_filings'
BASE_URL = f"{GH_PAGES_BASE_URL}/{GH_REPO_NAME}"

CUSTOM_HTML_PREFIX = 'real_html_'
TO_FROM = 'to/from'
MOBILE_SUFFIX = '_mobile'


class SiteType(StrEnum):
    BIOGRAPHIES = auto()
    COLORS_ONLY = auto()
    CURATED = auto()
    CURATED_MOBILE = auto()
    CHRONOLOGICAL = CHRONOLOGICAL
    CHRONOLOGICAL_MOBILE = f"{CHRONOLOGICAL}_mobile"
    DEVICE_SIGNATURES = auto()
    DOJ_FILES = auto()
    EMAILS = auto()
    EMAILS_CHRONOLOGICAL = auto()
    JSON_METADATA = auto()
    NAMES = auto()
    OTHER_FILES_TABLE = auto()
    SAMPLE = auto()
    TEXT_MESSAGES = auto()
    WORD_COUNT = auto()
    # Dev sites
    DEV_SAMPLE = auto()

    @classmethod
    def all_urls(cls) -> dict[Self, str]:
        return {site_type: cls.get_url(site_type) for site_type in cls}

    @classmethod
    def all_links(cls) -> dict['SiteType', Text]:
        """Use `SITE_DESCRIPTIONS` dict because it's ordered and also omits unpublished site types."""
        return {site_type: SiteType.link_txt(site_type) for site_type in SITE_DESCRIPTIONS}

    @classmethod
    def custom_html_build_path(cls, site_type: 'SiteType | Path') -> Path:
        """Path for the templated custom HTML version of the page."""
        if isinstance(site_type, Path):
            basename = site_type.name
        else:
            basename = cls.html_output_path(site_type).name

        return HTML_DIR.joinpath(f'{CUSTOM_HTML_PREFIX}{basename}')

    @classmethod
    def directory_links(cls) -> dict['SiteType', Text]:
        """Everything but mobile."""
        return {k: v for k, v in cls.all_links().items() if not cls.is_mobile(k)}

    @classmethod
    def html_output_path(cls, site_type: 'SiteType') -> Path:
        """Defaults to `[site_type].html` if not configured in `HTML_BUILD_FILENAMES`."""

        if site_type == cls.NAMES:
            from epstein_files.util.env import args
            site_type = '__'.join(sorted(args.names)).replace(' ', '_').lower()

        return HTML_DIR.joinpath(HTML_BUILD_FILENAMES.get(site_type, f"{site_type}.html"))

    @classmethod
    def html_output_path_mobile(cls, site_type: 'SiteType') -> Path:
        output_path = cls.html_output_path(site_type)
        return output_path.parent.joinpath(output_path.name.replace('.html', '_mobile.html'))

    @classmethod
    def get_url(cls, site_type: 'SiteType') -> str:
        return f"{BASE_URL}/{cls.html_output_path(site_type).name}"

    @classmethod
    def get_mobile_redirect_url(cls, site_type: Self) -> str:
        """Mobile defaults to chronological."""
        if SiteType.is_mobile(site_type):
            return cls.get_url(site_type)
        elif site_type == cls.CURATED:
            redirect_type = cls.CURATED_MOBILE
        else:
            redirect_type = cls.CHRONOLOGICAL_MOBILE  # TODO: the curated site is breaking iPhone simulator so no redirect for now

        return cls.get_url(redirect_type)

    @classmethod
    def is_chronoligical(cls, site_type: Self) -> bool:
        return site_type.startswith(CHRONOLOGICAL)

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
        return link.append(extra_info)

    @classmethod
    def mobile_compatible_types(cls) -> list['SiteType']:
        """Site types that have a valid mobile equivalent."""
        mobile_site_types = [site for site in cls if cls.is_mobile(site)]
        return [site.removesuffix(MOBILE_SUFFIX) for site in mobile_site_types]

    @classmethod
    def is_mobile(cls, site_type: 'SiteType') -> bool:
        return site_type.endswith(MOBILE_SUFFIX)

    @classmethod
    def _is_lesser_site(cls, site_type: Self) -> bool:
        return site_type in [cls.DOJ_FILES, cls.JSON_METADATA]  #+ [cls.JSON_FILES]


# TODO: purge repo of old files for space:
#  - curated_chronological.html
HTML_BUILD_FILENAMES = {
    SiteType.EMAILS_CHRONOLOGICAL:  f'chronological_emails.html',
    SiteType.CHRONOLOGICAL:         f"index.html",
    SiteType.CHRONOLOGICAL_MOBILE:  f"mobile_chronological.html",
    SiteType.DOJ_FILES:             f'doj_2026-01-30_non_email_files.html',
    SiteType.EMAILS:                f'emails_grouped_by_counterparty.html',
    SiteType.JSON_METADATA:         f'metadata.json',
    SiteType.TEXT_MESSAGES:         f'text_messages_{EPSTEIN_FILES_NOV_2025}.html',
    SiteType.WORD_COUNT:            f'communication_word_count.html',
#     SiteType.EPSTEIN_WORD_COUNT: 'epstein_texts_and_emails_word_count.html'),
}

# NOTE: Order matters, it's the order the links are shown in the header
# Colons are used to break and parenthesize display
SITE_DESCRIPTIONS = {
    SiteType.CHRONOLOGICAL:         f"chronological curated:all types intermingled",
    SiteType.CURATED:               f"emailers curated:emails grouped by person of interest",
    SiteType.EMAILS:                f"emailers:all emails grouped by person",
    SiteType.EMAILS_CHRONOLOGICAL:  f"emails chronological:all emails chronological order",
    SiteType.BIOGRAPHIES:           f"people:one line biographies with some links",
    SiteType.DEVICE_SIGNATURES:     f"signatures:email signatures/emojis and who uses them",
    SiteType.TEXT_MESSAGES:         f"text messages:{HOUSE_OVERSIGHT_TRANCHE}",
    SiteType.CURATED_MOBILE:        f"mobile:an attempt at mobile compatibility",
    SiteType.CHRONOLOGICAL_MOBILE:  f"chrono mobile:another attempt at mobile compatibility",
    SiteType.OTHER_FILES_TABLE:     f"other:files that are not emails or texts",
    SiteType.WORD_COUNT:            f"word count:of Epstein's communications",
    SiteType.DOJ_FILES:             f"doj files:raw OCR text {DOJ_2026_TRANCHE}",
    SiteType.JSON_METADATA:         f"metadata:author bios, attribution explanations",
}

# These are site types where the custom HTML is good enough to deploy
DEPLOY_CUSTOM_HTML_SITES = [
    SiteType.BIOGRAPHIES,
    SiteType.CHRONOLOGICAL,
    SiteType.CHRONOLOGICAL_MOBILE,
    SiteType.EMAILS_CHRONOLOGICAL,
    SiteType.OTHER_FILES_TABLE,
]


###########################################
########  Internal sections links  ########
###########################################
AUTHORS_USING_SIGNATURES = 'Authors Seen Using Email Signatures'
SELECTIONS_FROM = 'Selections from '
HIS_EMAILS = 'His Emails'
HIS_TEXT_MESSAGES = 'His Text Messages'
FILES_THAT_ARE_NEITHER_EMAILS_NOR = 'Files That Are Neither Emails Nor Text Messages'

class PageSections(StrEnum):
    EMAILS = auto()
    EMAIL_SIGNATURES = auto()
    OTHER_FILES = auto()
    TEXT_MESSAGES = auto()

# Search terms that take you to the desired section via magic URL comment arg
SECTION_ANCHORS = {
    PageSections.EMAILS: SELECTIONS_FROM + HIS_EMAILS,
    PageSections.EMAIL_SIGNATURES: AUTHORS_USING_SIGNATURES,
    PageSections.TEXT_MESSAGES: SELECTIONS_FROM + HIS_TEXT_MESSAGES,
    PageSections.OTHER_FILES: FILES_THAT_ARE_NEITHER_EMAILS_NOR,
}


def make_clean() -> None:
    """Delete all build artifacts."""
    for site_type in SiteType:
        for build_file in [SiteType.html_output_path(site_type), SiteType.custom_html_build_path(site_type)]:
            for file in [build_file, Path(f"{build_file}.txt")]:
                if file.exists():
                    logger.warning(f"Removing build file '{file}'...")
                    file.unlink()


def use_custom_html() -> None:
    """Overwrite normal rich html export with custom HTML for all DEPLOY_CUSTOM_HTML_SITES."""
    for site in DEPLOY_CUSTOM_HTML_SITES:
        from_path = SiteType.custom_html_build_path(site)
        to_path = SiteType.html_output_path(site)
        logger.warning(f"Copying '{from_path}' to '{to_path}'...")
