"""
HTML file paths and URLs for files built by `epstein_generate`.
"""
import shutil
from dataclasses import dataclass, field
from enum import auto, StrEnum
from pathlib import Path
from typing import Self

from rich.console import Group, NewLine
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.documents.categories import Interesting
from epstein_files.util.constant.strings import (AUX_SITE_LINK_STYLE, CHRONOLOGICAL,
     DOJ_2026_TRANCHE, EPSTEIN_FILES_NOV_2025, HOUSE_OVERSIGHT_TRANCHE)
from epstein_files.output.html.html_dir import DEFAULT_HTML_DIR, HtmlDir
from epstein_files.output.layout_elements.site_directory import SiteDirectory
from epstein_files.util.external_link import ExternalLink, link_text_obj, parenthesize
from epstein_files.util.helpers.rich_helpers import bold, join_texts
from epstein_files.util.logging import logger

EMAILERS_TABLE_PNG_PATH = DEFAULT_HTML_DIR.joinpath('emailers_info_table.png')

# Github URLs
GH_REPO_NAME = 'epstein_text_messages'
GH_PAGES_BASE_URL = 'https://michelcrypt4d4mus.github.io'
GH_PROJECT_URL = f'https://github.com/michelcrypt4d4mus/{GH_REPO_NAME}'
GH_MASTER_URL = f"{GH_PROJECT_URL}/blob/master"
ATTRIBUTIONS_URL = f'{GH_MASTER_URL}/epstein_files/util/constants.py'
EXTRACTS_BASE_URL = f'{GH_MASTER_URL}/emails_extracted_from_legal_filings'
BASE_DEPLOY_URL = f"{GH_PAGES_BASE_URL}/{GH_REPO_NAME}"
PROJECT_LINK = ExternalLink(BASE_DEPLOY_URL, f"Michel de Cryptadamus Epstein Investigations")

CATEGORY_SITES = [Interesting.CRYPTO, Interesting.GIRLS, Interesting.MONEY]
CATEGORY_PREFIX = 'for_category_'
CUSTOM_HTML_PREFIX = 'real_html_'
NAMES_PREFIX = 'only_names_'
MOBILE_SUFFIX = '_mobile'
PHONE_LOG_FILE_ID = 'EFTA01242527'

# Site directory
SITE_GLOSSARY_MSG = f"The following views of the underlying selection of Epstein Files are available:"
YOU_ARE_HERE = Text('«').append('you are here', style='bold khaki1 blink').append('»')

category_link_text = lambda category: f"category[{category}]"


class Site(StrEnum):
    ANNOTATED = auto()       # only things with `note`s.
    BIOGRAPHIES = auto()
    CATEGORY = auto()
    COLORS_ONLY = auto()
    CURATED = auto()
    CURATED_MOBILE = auto()
    CHRONOLOGICAL = CHRONOLOGICAL
    CHRONOLOGICAL_MOBILE = f"{CHRONOLOGICAL}_mobile"
    DEVICE_SIGNATURES = auto()
    DOCUMENT_NOTES = auto()
    DOJ_FILES = auto()
    EMAILERS = auto()
    EMAILS_CHRONOLOGICAL = auto()
    JSON_METADATA = auto()
    MOST_INTERESTING = auto()
    NAMES = auto()  # Not a single site, depends on the --name argument
    OTHER_FILES_TABLE = auto()
    PHONE_NUMBERS = auto()
    SAMPLE = auto()
    TEXT_MESSAGES = auto()
    WORD_COUNT = auto()
    # Dev sites
    DEV_SAMPLE = auto()

    @classmethod
    def all_urls(cls) -> dict[Self, str]:
        return {site: cls.get_url(site) for site in cls}

    @classmethod
    def all_links(cls) -> 'dict[Site | str, Text]':
        """Use `SITE_DESCRIPTIONS` dict because it's ordered and also omits unpublished site types."""
        links = {site: cls.link_txt(site) for site in SITE_DESCRIPTIONS}
        links.update({category_link_text(c): cls.link_to_category(c).__rich__() for c in CATEGORY_SITES})
        return links

    @classmethod
    def directory(cls) -> 'SiteDirectory':
        return SiteDirectory(
            [cls.get_site_link(site) for site in SITE_DESCRIPTIONS if not cls.is_mobile(site)],
            [],
            [cls.link_to_category(c) for c in CATEGORY_SITES],
        )

    @classmethod
    def custom_html_build_path(cls, site: 'Site | Path') -> Path:
        """Path for the templated custom HTML version of the page."""
        filename = site.name if isinstance(site, Path) else cls.html_output_path(site).name
        return HtmlDir.build_path(f'{CUSTOM_HTML_PREFIX}{filename}')

    @classmethod
    def directory_links(cls) -> dict['Site', Text]:
        """Everything but mobile."""
        return {k: v for k, v in cls.all_links().items() if not cls.is_mobile(k)}

    @classmethod
    def html_output_path(cls, _site: 'Site', category: str = '') -> Path:
        """Defaults to `[site].html` if not configured in `HTML_BUILD_FILENAMES`."""
        if _site in [cls.CATEGORY, cls.NAMES]:
            from epstein_files.util.env import args

            if _site == cls.NAMES:
                prefix = NAMES_PREFIX
                suffixes = ['unknown' if n is None else n for n in args.names]
            else:
                prefix = CATEGORY_PREFIX

                if (category := category or args.category):
                    suffixes = [category]
                else:
                    suffixes = []

            site = prefix + '__'.join(sorted(suffixes)).replace(' ', '_').lower()
        elif _site == cls.CATEGORY:
            site = CATEGORY_PREFIX
        elif _site == INDEX_HTML_SITE:
            site = 'index'
        else:
            site = _site

        return HtmlDir.build_path(HTML_BUILD_FILENAMES.get(site, f"{site}.html"))

    @classmethod
    def html_output_path_mobile(cls, site: 'Site') -> Path:
        output_path = cls.html_output_path(site)
        return output_path.parent.joinpath(output_path.name.replace('.html', '_mobile.html'))

    @classmethod
    def get_site_link(cls, site: Self, category: str = '') -> ExternalLink:
        link_parens_style = ''

        if site == cls.CATEGORY:
            link_text = category_link_text(category)
            link_style = 'red'
            link_comment = 'only files in this category'
            link_comment_style = 'grey50'
        else:
            link_text = SITE_DESCRIPTIONS.get(site, site)
            link_style = AUX_SITE_LINK_STYLE
            link_comment_style = 'plum4 italic'
            link_comment = ''

            if ':' in link_text:
                link_text, link_comment = SITE_DESCRIPTIONS[site].split(':')
                link_parens_style = 'color(147) dim'
                # extra_info = Text(escape(extra_info), style=f'plum4 italic')
                # extra_info = Text(' ').append(parenthesize(extra_info, 'color(147) dim'))

        if cls._is_lesser_site(site):
            link_style = 'gray30'# 'light_pink4'

        return ExternalLink(
            Site.get_url(site, category),
            escape(link_text),
            link_comment,
            comment_style=link_comment_style,
            link_style=bold(link_style),
            parentheses_style=link_parens_style,
        )
        link = link_text_obj(Site.get_url(site), escape(link_text), f"{style} {style_mod}")

    @classmethod
    def get_url(cls, site: 'Site', category: str = '') -> str:
        return f"{BASE_DEPLOY_URL}/{cls.html_output_path(site, category).name}"

    @classmethod
    def get_mobile_redirect_url(cls, site: Self) -> str:
        """Mobile defaults to chronological."""
        if cls.is_mobile(site) or site == cls.NAMES:
            return cls.get_url(site)
        elif site == cls.CURATED:
            redirect_type = cls.CURATED_MOBILE
        else:
            redirect_type = cls.CHRONOLOGICAL_MOBILE  # TODO: the curated site is breaking iPhone simulator so no redirect for now

        return cls.get_url(redirect_type)

    @classmethod
    def is_chronoligical(cls, site: Self) -> bool:
        return CHRONOLOGICAL in site

    @classmethod
    def is_mobile(cls, site: Self) -> bool:
        return site.endswith(MOBILE_SUFFIX)

    @classmethod
    def link_txt(cls, site: Self, category: str = '') -> Text:
        return cls.get_site_link(site, category).__rich__()

    @classmethod
    def link_to_category(cls, category: str) -> ExternalLink:
        from epstein_files.output.highlight_config import get_style_for_category

        return ExternalLink(
            cls.get_url(cls.CATEGORY, category),
            escape(f"category[{category}]"),
            link_style=get_style_for_category(category) or '',
            comment=f'all files related to {category}',
            comment_style='color(147) dim italic'
        )

    @classmethod
    def mobile_compatible_types(cls) -> list['Site']:
        """Site types that have a valid mobile equivalent."""
        mobile_sites = [site for site in cls if cls.is_mobile(site)]
        return [site.removesuffix(MOBILE_SUFFIX) for site in mobile_sites]

    @classmethod
    def _is_lesser_site(cls, site: Self) -> bool:
        return site in [cls.DOJ_FILES, cls.JSON_METADATA]  #+ [cls.JSON_FILES]


INDEX_HTML_SITE = Site.MOST_INTERESTING

# TODO: purge repo of old files for space:
#  - curated_chronological.html
HTML_BUILD_FILENAMES = {
    Site.EMAILS_CHRONOLOGICAL:  f'chronological_emails.html',
    Site.CHRONOLOGICAL_MOBILE:  f"mobile_chronological.html",
    Site.DOJ_FILES:             f'doj_2026-01-30_non_email_files.html',
    Site.EMAILERS:              f'emails_grouped_by_counterparty.html',
    Site.JSON_METADATA:         f'metadata.json',
    Site.PHONE_NUMBERS:         f'{PHONE_LOG_FILE_ID}_phone_calls.html',
    Site.TEXT_MESSAGES:         f'text_messages_{EPSTEIN_FILES_NOV_2025}.html',
    Site.WORD_COUNT:            f'communication_word_count.html',
#     SiteType.EPSTEIN_WORD_COUNT: 'epstein_texts_and_emails_word_count.html'),
}

# NOTE: Order matters, it's the order the links are shown in the header
# Colons are used to break and parenthesize display
SITE_DESCRIPTIONS = {
    # Site.ANNOTATED:             r"annotated:the cream of the crop",
    Site.MOST_INTERESTING:      f"most interesting:the cream of the crop",
    Site.CHRONOLOGICAL:         f"chronological curated:all types intermingled",
    Site.CURATED:               f"emailers curated:emails grouped by person of interest",
    Site.EMAILERS:              f"emailers all:all emails grouped by person",
    Site.EMAILS_CHRONOLOGICAL:  f"emails chronological:all emails chronological order",
    Site.BIOGRAPHIES:           f"people:one line biographies with some links",
    Site.DEVICE_SIGNATURES:     f"signatures:email signatures/emojis and who uses them",
    Site.TEXT_MESSAGES:         f"text messages:{HOUSE_OVERSIGHT_TRANCHE}",
    Site.CURATED_MOBILE:        f"mobile:an attempt at mobile compatibility",
    Site.CHRONOLOGICAL_MOBILE:  f"chrono mobile:another attempt at mobile compatibility",
    Site.OTHER_FILES_TABLE:     f"other:files that are not emails or texts",
    Site.DOCUMENT_NOTES:        f"notes:on the most interesting files",
    Site.PHONE_NUMBERS:         f"phone numbers:called by Epstein's phones",
    Site.WORD_COUNT:            f"word count:of Epstein's communications",
    Site.DOJ_FILES:             f"doj files:raw OCR text {DOJ_2026_TRANCHE}",
    Site.JSON_METADATA:         f"metadata:author bios, attribution explanations",
}

# These are site types where the custom HTML is good enough to deploy
DEPLOY_CUSTOM_HTML_SITES = [
    Site.ANNOTATED,
    Site.BIOGRAPHIES,
    Site.CHRONOLOGICAL,
    Site.CHRONOLOGICAL_MOBILE,
    Site.DOCUMENT_NOTES,
    Site.EMAILS_CHRONOLOGICAL,
    Site.MOST_INTERESTING,
    Site.OTHER_FILES_TABLE,
]



def make_clean() -> None:
    """Delete all build artifacts."""
    for site in Site:
        if site == Site.CATEGORY:
            for category in CATEGORY_SITES:
                logger.error(f'should clean file but not for category: {category}')

            continue

        for build_file in [Site.html_output_path(site)]: #, Site.custom_html_build_path(site)]:
            if site == Site.NAMES:
                paths = [f for f in build_file.parent.glob(f"{build_file.stem}*.html")]
            else:
                paths = [build_file, Path(f"{build_file}.txt")]

            for file in [f for f in paths if f.exists()]:
                logger.warning(f"Removing build file '{file}'...")
                file.unlink()


def use_custom_html() -> None:
    """Overwrite normal rich html export with custom HTML for all `DEPLOY_CUSTOM_HTML_SITES`."""
    for site in DEPLOY_CUSTOM_HTML_SITES:
        from_path = Site.custom_html_build_path(site)
        to_path = Site.html_output_path(site)

        if from_path.exists():
            logger.warning(f"Copying/overwriting '{from_path}' to '{to_path}'...")
            shutil.copy2(from_path, to_path)
        else:
            logger.error(f"No custom HTML file found at '{from_path}'")

    for category in CATEGORY_SITES:
        to_path = Site.html_output_path(Site.CATEGORY, category)
        from_path = Site.custom_html_build_path(to_path)

        if from_path.exists():
            logger.warning(f"Copying/overwriting '{from_path}' to '{to_path}'...")
            shutil.copy2(from_path, to_path)
        else:
            logger.error(f"No custom HTML file found at '{from_path}'")
