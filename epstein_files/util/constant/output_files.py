from pathlib import Path

URLS_ENV = '.urls.env'

# Files output by the code
HTML_DIR = Path('docs')
EPSTEIN_FILES_NOV_2025 = 'epstein_files_nov_2025'
ALL_EMAILS_PATH = HTML_DIR.joinpath(f'all_emails_{EPSTEIN_FILES_NOV_2025}.html')
JSON_FILES_JSON_PATH = HTML_DIR.joinpath(f'json_files_from_{EPSTEIN_FILES_NOV_2025}.json')
JSON_METADATA_PATH = HTML_DIR.joinpath(f'file_metadata_{EPSTEIN_FILES_NOV_2025}.json')
TEXT_MSGS_HTML_PATH = HTML_DIR.joinpath('index.html')
WORD_COUNT_HTML_PATH = HTML_DIR.joinpath(f'communication_word_count_{EPSTEIN_FILES_NOV_2025}.html')
# EPSTEIN_WORD_COUNT_HTML_PATH = HTML_DIR.joinpath('epstein_texts_and_emails_word_count.html')

BUILD_ARTIFACTS = [
    ALL_EMAILS_PATH,
    # EPSTEIN_WORD_COUNT_HTML_PATH,
    JSON_FILES_JSON_PATH,
    JSON_METADATA_PATH,
    TEXT_MSGS_HTML_PATH,
    WORD_COUNT_HTML_PATH,
]


def make_clean() -> None:
    """Delete all build artifacts."""
    for build_file in BUILD_ARTIFACTS:
        if build_file.exists():
            print(f"Removing build file '{build_file}'...")
            build_file.unlink()
