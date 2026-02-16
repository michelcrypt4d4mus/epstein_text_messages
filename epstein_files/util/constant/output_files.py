"""
HTML file paths and URLs for files built by epstein_generate.
"""
from enum import auto, StrEnum
from pathlib import Path

from epstein_files.util.logging import logger
from epstein_files.util.constant.strings import DOJ_2026_TRANCHE, EPSTEIN_FILES_NOV_2025, HOUSE_OVERSIGHT_TRANCHE

GH_REPO_NAME = 'epstein_text_messages'
GH_PAGES_BASE_URL = 'https://michelcrypt4d4mus.github.io'
BASE_URL = f"{GH_PAGES_BASE_URL}/{GH_REPO_NAME}"

HTML_DIR = Path('docs')
URLS_ENV = '.urls.env'
EMAILERS_TABLE_PNG_PATH = HTML_DIR.joinpath('emailers_info_table.png')


class SiteType(StrEnum):
    CHRONOLOGICAL_EMAILS = auto()
    CURATED = auto()
    DOJ_FILES = auto()
    GROUPED_EMAILS = auto()
    JSON_FILES = auto()
    JSON_METADATA = auto()
    TEXT_MESSAGES = auto()
    WORD_COUNT = auto()

    @classmethod
    def build_path(cls, site_type: 'SiteType') -> Path:
        return HTML_DIR.joinpath(HTML_BUILD_FILENAMES[site_type])

    @classmethod
    def get_url(cls, site_type: 'SiteType') -> str:
        return f"{BASE_URL}/{cls.build_path(site_type).name}"


HTML_BUILD_FILENAMES = {
    SiteType.CHRONOLOGICAL_EMAILS: f'chronological_emails.html',
    SiteType.CURATED:              f'index.html',
    SiteType.DOJ_FILES:            f'doj_2026-01-30_non_email_files.html',
    SiteType.GROUPED_EMAILS:       f'emails_grouped_by_counterparty.html',
    SiteType.JSON_FILES:           f'json_files_from_{EPSTEIN_FILES_NOV_2025}.json',
    SiteType.JSON_METADATA:        f'file_metadata_{EPSTEIN_FILES_NOV_2025}.json',
    SiteType.TEXT_MESSAGES:        f'text_messages_{EPSTEIN_FILES_NOV_2025}.html',
    SiteType.WORD_COUNT:           f'communication_word_count.html',
#     SiteType.EPSTEIN_WORD_COUNT: 'epstein_texts_and_emails_word_count.html'),
}

# Order matters, it's the order the links are shown in the header
SITE_DESCRIPTIONS = {
    SiteType.CURATED:              f"curated selection of files of particular interest",
    SiteType.GROUPED_EMAILS:       f"emails grouped by counterparty and previews of all non email files",
    SiteType.CHRONOLOGICAL_EMAILS: f"emails in chronological order",
    SiteType.TEXT_MESSAGES:        f"iMessage conversations from the {HOUSE_OVERSIGHT_TRANCHE}",
    SiteType.DOJ_FILES:            f"raw OCR text of non-email PDFs from {DOJ_2026_TRANCHE}",
    SiteType.WORD_COUNT:           f"word count of all communications",
    SiteType.JSON_METADATA:        f"metadata (author, attribution reasons, etc.)",
    SiteType.JSON_FILES:           f"raw JSON files from the {HOUSE_OVERSIGHT_TRANCHE}",
}


def make_clean() -> None:
    """Delete all build artifacts."""
    for site_type in SiteType:
        build_file = SiteType.build_path(site_type)

        for file in [build_file, Path(f"{build_file}.txt")]:
            if file.exists():
                logger.warning(f"Removing build file '{file}'...")
                file.unlink()
