import logging
from os import environ

from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.logging import RichHandler
from rich.theme import Theme

from epstein_files.util.constant.strings import *

DOC_TYPE_STYLES = {
    DOCUMENT_CLASS: 'grey69',
    EMAIL_CLASS: 'dark_orange3',
    JSON_FILE_CLASS: 'sandy_brown',
    MESSENGER_LOG_CLASS: 'deep_pink4',
    OTHER_FILE_CLASS: 'grey69',
}

LOG_THEME = {
    f"{ReprHighlighter.base_style}{doc_type}": f"{doc_style} bold"
    for doc_type, doc_style in DOC_TYPE_STYLES.items()
}

LOG_THEME[f"{ReprHighlighter.base_style}epstein_filename"] = 'gray27'
LOG_LEVEL_ENV_VAR = 'LOG_LEVEL'


class LogHighlighter(ReprHighlighter):
    highlights = ReprHighlighter.highlights + [
        *[fr"(?P<{doc_type}>{doc_type})" for doc_type in DOC_TYPE_STYLES.keys()],
        "(?P<epstein_filename>" + FILE_NAME_REGEX.pattern + ')',
    ]


log_console = Console(color_system='256', theme=Theme(LOG_THEME))
log_handler = RichHandler(console=log_console, highlighter=LogHighlighter())
logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[log_handler])
logger = logging.getLogger("rich")


# Log levels
datefinder_logger = logging.getLogger('datefinder')  # Set log level to suppress annoying output
env_log_level_str = environ.get(LOG_LEVEL_ENV_VAR) or None
env_log_level = None

if env_log_level_str:
    try:
        env_log_level = getattr(logging, env_log_level_str)
    except Exception as e:
        logger.warning(f"{LOG_LEVEL_ENV_VAR}='{env_log_level_str}' does not exist, defaulting to DEBUG")
        env_log_level = logging.DEBUG

    logger.warning(f"Setting log level to {env_log_level} based on {LOG_LEVEL_ENV_VAR} env var...")
    logger.setLevel(env_log_level)
    datefinder_logger.setLevel(env_log_level)
