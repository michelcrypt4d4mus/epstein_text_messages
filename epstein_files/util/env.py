import logging
from argparse import ArgumentParser, Namespace
from os import environ
from pathlib import Path
from sys import argv

from rich.logging import RichHandler

DEFAULT_WIDTH = 120
HTML_SCRIPTS = ['generate.py', 'count_words.py']


parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML page.")
parser.add_argument('--build', '-b', action='store_true', help='write HTML to docs/index.html')
parser.add_argument('--all-emails', '-a', action='store_true', help='all the emails (also --no-texts)')
parser.add_argument('--all-email-tables', '-at', action='store_true', help='all email tables (except Epstein)')
parser.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and exit')
parser.add_argument('--email', '-e', action='append', dest='emails', help='specify the emailers to output (implies --no-texts)')
parser.add_argument('--no-texts', '-nt', action='store_true', help='skip text message output')
parser.add_argument('--pickled', '-p', action='store_true', help='use pickled EpsteinFiles object')
parser.add_argument('--pickle-overwrite', '-po', action='store_true', help='generate new pickled EpsteinFiles object')
parser.add_argument('--sort-alphabetical', '-alpha', action='store_true', help='sort emailers alphabetically in counts table')
parser.add_argument('--suppress-output', '-s', action='store_true', help='no output to terminal (use with --build)')
parser.add_argument('--use-epstein-web-links', '-use', action='store_true', help='use epsteinweb.org links instead of epsteinify.com')
parser.add_argument('--search-other', '-so', action='store_true', help='search for string in non email/text files (only used by search script)')
parser.add_argument('--width', '-w', type=int, default=DEFAULT_WIDTH, help='screen width to use')
parser.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
parser.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
parser.add_argument('--json-stats', action='store_true', help='print JSON formatted stats at the end')
parser.add_argument('positional_args', nargs='*', help='Optional args (only used by helper scripts)')
args = parser.parse_args()

is_env_var_set = lambda s: len(environ.get(s) or '') > 0

current_script = Path(argv[0]).name
deep_debug = args.deep_debug or is_env_var_set('DEEP_DEBUG')
is_build = args.build or is_env_var_set('BUILD_HTML')
is_debug = deep_debug or args.debug or is_env_var_set('DEBUG')
is_html_script = current_script in HTML_SCRIPTS
skip_texts = args.no_texts or is_env_var_set('NO_TEXTS')

args.width = args.width if is_html_script else None
specified_emailers = args.emails or []


# Setup logging
logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("rich")

if deep_debug:
    logger.setLevel(logging.DEBUG)
elif is_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)


if len(specified_emailers) > 0:
    logger.warning(f"Found {len(specified_emailers)} --email so setting --no-texts to True")
    args.no_texts = True
    skip_texts = True

if args.use_epstein_web_links:
    logger.warning(f"Using links to epsteinweb.org links instead of epsteinify.com")


logger.debug(f"is_html_script={is_html_script}, args.width={args.width}, current_script='{current_script}'")
