import logging
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from sys import argv

from rich.logging import RichHandler

DEFAULT_WIDTH = 154
HTML_SCRIPTS = ['generate_html.py', 'count_words.py']


parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML page.")
parser.add_argument('--build', '-b', action='store_true', help='write HTML to docs/index.html')
parser.add_argument('--all-emails', '-ae', action='store_true', help='all the emails')
parser.add_argument('--all-email-tables', '-aet', action='store_true', help='all email tables (except Epstein)')
parser.add_argument('--all-other-files', '-ao', action='store_true', help='all the non-email, non-text msg files instead of a limited selection')
parser.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and links and exit')
parser.add_argument('--name', '-n', action='append', dest='names', help='specify the name(s) whose communications should be output')
parser.add_argument('--output-emails', '-oe', action='store_true', help='generate other files section')
parser.add_argument('--output-other-files', '-oo', action='store_true', help='generate other files section')
parser.add_argument('--output-texts', '-ot', action='store_true', help='generate other files section')
parser.add_argument('--pickled', '-p', action='store_true', help='use pickled EpsteinFiles object')
parser.add_argument('--overwrite-pickle', '-op', action='store_true', help='generate new pickled EpsteinFiles object')
parser.add_argument('--sort-alphabetical', '-alpha', action='store_true', help='sort emailers alphabetically in counts table')
parser.add_argument('--suppress-output', '-s', action='store_true', help='no output to terminal (use with --build)')
parser.add_argument('--use-epstein-web-links', '-use', action='store_true', help='use epsteinweb.org links instead of epstein.media')
parser.add_argument('--width', '-w', type=int, default=DEFAULT_WIDTH, help='screen width to use')
parser.add_argument('--whole-file', '-wf', action='store_true', help='print whole file (only used by search script)')
parser.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
parser.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
parser.add_argument('--suppress-logs', '-sl', action='store_true', help='set debug level to FATAL')
parser.add_argument('--json-stats', '-j', action='store_true', help='print JSON formatted stats at the end')
parser.add_argument('positional_args', nargs='*', help='Optional args (only used by helper scripts)')
args = parser.parse_args()

is_env_var_set = lambda s: len(environ.get(s) or '') > 0
current_script = Path(argv[0]).name
is_html_script = current_script in HTML_SCRIPTS

args.deep_debug = args.deep_debug or is_env_var_set('DEEP_DEBUG')
args.debug = args.deep_debug or args.debug or is_env_var_set('DEBUG')
args.output_emails = args.output_emails or args.all_emails
args.output_other_files = args.output_other_files or args.all_other_files
args.pickled = args.pickled or is_env_var_set('PICKLED') or args.colors_only or len(args.names or []) > 0
args.width = args.width if is_html_script else None
specified_names: list[str | None] = [None if n == 'None' else n for n in (args.names or [])]


# Setup logging
logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
# logging.basicConfig(level="DEBUG", handlers=[RichHandler()])
logger = logging.getLogger("rich")

if args.deep_debug:
    logger.setLevel(logging.DEBUG)
elif args.debug:
    logger.setLevel(logging.INFO)
elif args.suppress_logs:
    logger.setLevel(logging.FATAL)
else:
    logger.setLevel(logging.WARNING)

datefinder_logger = logging.getLogger('datefinder')  # Suppress annoying output
datefinder_logger.setLevel(logger.level)


# Massage args that depend on other args to the appropriate state
if not (args.output_texts or args.output_emails or args.output_other_files):
    if is_html_script:
        logger.warning(f"No output section chosen; outputting default of texts, selected emails, and other files...")

    args.output_texts = True
    args.output_emails = True
    args.output_other_files = True

if args.use_epstein_web_links:
    logger.warning(f"Using links to epsteinweb.org links instead of epsteinify.com...")

if args.debug:
    logger.warning(f"is_html_script={is_html_script}, specified_names={specified_names}, args={args}")
