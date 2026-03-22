import logging
import sys
from os import environ

from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.logging import RichHandler
from rich.theme import Theme
from yaralyzer.util.helpers.env_helper import console_width_possibilities

from epstein_files.util.constant.strings import *

FILENAME_STYLE = 'gray27'
RICH_COLOR_SYSTEM = '256'  # Setting to 'truecolor' makes terminal unable to print hex/rgb() colors

DOC_TYPE_STYLES = {
    DOCUMENT_CLASS: 'grey69',
    DOJ_FILE_CLASS: 'magenta',
    EMAIL_CLASS: 'dark_orange3',
    'DropsiteEmail': 'orange1',
    JSON_FILE_CLASS: 'sandy_brown',
    MESSENGER_LOG_CLASS: 'deep_pink4',
    f"{MESSENGER_LOG_CLASS}Pdf": 'deep_pink4',
    OTHER_FILE_CLASS: 'dark_sea_green',
}

LOG_THEME = {
    f"{ReprHighlighter.base_style}{doc_type}": f"{doc_style} bold"
    for doc_type, doc_style in DOC_TYPE_STYLES.items()
}

LOG_THEME[f"{ReprHighlighter.base_style}epstein_filename"] = FILENAME_STYLE
LOG_LEVEL_ENV_VAR = 'EPSTEIN_LOG_LEVEL'


# Augment the standard log highlighter with 'epstein_filename' matcher
class LogHighlighter(ReprHighlighter):
    highlights = ReprHighlighter.highlights + [
        *[fr"(?P<{doc_type}>{doc_type}(Cfg|s)?)" for doc_type in DOC_TYPE_STYLES.keys()],
        "(?P<epstein_filename>" + '|'.join([HOUSE_OVERSIGHT_NOV_2025_FILE_NAME_REGEX.pattern, DOJ_FILE_NAME_REGEX.pattern]) + ')',
    ]


log_console = Console(
    color_system=RICH_COLOR_SYSTEM,
    stderr=True,
    theme=Theme(LOG_THEME),
    width=max(console_width_possibilities())
)

datefmt = r'%H:%M:%S' if SUPPRESS_OUTPUT in sys.argv else ' '
log_handler = RichHandler(console=log_console, highlighter=LogHighlighter(), show_path=False)
logging.basicConfig(level="NOTSET", format="%(message)s", datefmt=datefmt, handlers=[log_handler])
logger = logging.getLogger("epstein_text_files")


# Set log levels to suppress annoying output from other packages
logging.getLogger('datefinder').setLevel(logging.FATAL)
logging.getLogger('rich_argparse').setLevel(logging.FATAL)
env_log_level_str = environ.get(LOG_LEVEL_ENV_VAR) or None
env_log_level = None


def exit_with_error(msg: str) -> None:
    print('')
    logger.error(msg + '\n')
    sys.exit(1)


def print_text_block(s: str, label: str) -> None:
    print(f"\n-------- {label} ----------\n{s}\n-------- end {label} --------\n\n")


def set_log_level(log_level: int | str) -> None:
    for lg in [logger] + logger.handlers:
        lg.setLevel(log_level)


if env_log_level_str:
    try:
        env_log_level = getattr(logging, env_log_level_str)
    except Exception as e:
        logger.warning(f"{LOG_LEVEL_ENV_VAR}='{env_log_level_str}' does not exist, defaulting to DEBUG")
        env_log_level = logging.DEBUG

    logger.warning(f"Setting log level to {env_log_level} based on {LOG_LEVEL_ENV_VAR} env var...")
    set_log_level(env_log_level)


# logger.setLevel(logging.DEBUG)
# print(f"logger name = '{logger.name}', handlers = {logger.handlers}")

# for app_name in ['pdfalyzer', 'yaralyzer']:
#     app_log = logging.getLogger(app_name)

#     for log in [app_log] + app_log.handlers:
#         log.setLevel(logging.DEBUG)

#         if isinstance(log, Handler):
#             log.formatter = Formatter("[%(name)s] %(message)s")
#         else:
#             print(f"logger name = '{log.name}', handlers = {log.handlers}")
