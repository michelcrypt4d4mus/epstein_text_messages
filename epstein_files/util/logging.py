import logging

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


LOG_THEME[f"{ReprHighlighter.base_style}epstein_filename"] = 'wheat4'


class LogHighlighter(ReprHighlighter):
    highlights = ReprHighlighter.highlights + [
        *[fr"(?P<{doc_type}>{doc_type})" for doc_type in DOC_TYPE_STYLES.keys()],
        "(?P<epstein_filename>" + FILE_STEM_REGEX.pattern + ')',
    ]


log_console = Console(color_system='256', theme=Theme(LOG_THEME))
log_handler = RichHandler(console=log_console, highlighter=LogHighlighter())
logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[log_handler])
logger = logging.getLogger("rich")

# Suppress annoying output
datefinder_logger = logging.getLogger('datefinder')
