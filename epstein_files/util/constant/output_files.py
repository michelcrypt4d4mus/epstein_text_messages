from pathlib import Path

from epstein_files.util.constant.strings import EMAIL, TEXT_MESSAGE, SiteType
from epstein_files.util.logging import logger

# Files output by the code
HTML_DIR = Path('docs')
EPSTEIN_FILES_NOV_2025 = 'epstein_files_nov_2025'
ALL_EMAILS_PATH = HTML_DIR.joinpath(f'all_emails_{EPSTEIN_FILES_NOV_2025}.html')
CHRONOLOGICAL_EMAILS_PATH = HTML_DIR.joinpath(f'chronological_emails_{EPSTEIN_FILES_NOV_2025}.html')
JSON_FILES_JSON_PATH = HTML_DIR.joinpath(f'json_files_from_{EPSTEIN_FILES_NOV_2025}.json')
JSON_METADATA_PATH = HTML_DIR.joinpath(f'file_metadata_{EPSTEIN_FILES_NOV_2025}.json')
TEXT_MSGS_HTML_PATH = HTML_DIR.joinpath('index.html')
WORD_COUNT_HTML_PATH = HTML_DIR.joinpath(f'communication_word_count_{EPSTEIN_FILES_NOV_2025}.html')
# EPSTEIN_WORD_COUNT_HTML_PATH = HTML_DIR.joinpath('epstein_texts_and_emails_word_count.html')
URLS_ENV = '.urls.env'
EMAILERS_TABLE_PNG_PATH = HTML_DIR.joinpath('emailers_info_table.png')

# Deployment URLS
# NOTE: don't rename these variables without changing deploy.sh!
GH_PAGES_BASE_URL = 'https://michelcrypt4d4mus.github.io'
TEXT_MSGS_URL = f"{GH_PAGES_BASE_URL}/epstein_text_messages"
ALL_EMAILS_URL = f"{TEXT_MSGS_URL}/{ALL_EMAILS_PATH.name}"
CHRONOLOGICAL_EMAILS_URL = f"{TEXT_MSGS_URL}/{CHRONOLOGICAL_EMAILS_PATH.name}"
JSON_FILES_URL = f"{TEXT_MSGS_URL}/{JSON_FILES_JSON_PATH.name}"
JSON_METADATA_URL = f"{TEXT_MSGS_URL}/{JSON_METADATA_PATH.name}"
WORD_COUNT_URL = f"{TEXT_MSGS_URL}/{WORD_COUNT_HTML_PATH.name}"

SITE_URLS: dict[SiteType, str] = {
    EMAIL: ALL_EMAILS_URL,
    TEXT_MESSAGE: TEXT_MSGS_URL,
}

BUILD_ARTIFACTS = [
    ALL_EMAILS_PATH,
    CHRONOLOGICAL_EMAILS_PATH,
    # EPSTEIN_WORD_COUNT_HTML_PATH,
    JSON_FILES_JSON_PATH,
    JSON_METADATA_PATH,
    TEXT_MSGS_HTML_PATH,
    WORD_COUNT_HTML_PATH,
]


def make_clean() -> None:
    """Delete all build artifacts."""
    for build_file in BUILD_ARTIFACTS:
        for file in [build_file, f"{build_file}.txt"]:
            if file.exists():
                logger.warning(f"Removing build file '{file}'...")
                file.unlink()
