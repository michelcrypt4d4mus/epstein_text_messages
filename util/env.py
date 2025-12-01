import logging
from argparse import ArgumentParser, Namespace
from os import environ

from rich.logging import RichHandler


is_env_var_set = lambda s: len(environ.get(s) or '') > 0

parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML page.")
parser.add_argument('--build', '-b', action='store_true', help='write HTML to docs/index.html')
parser.add_argument('--all-emails', '-a', action='store_true', help='all the emails (also --no-texts)')
parser.add_argument('--all-email-tables', '-at', action='store_true', help='all email tables (except Epstein)')
parser.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and exit')
parser.add_argument('--email', '-e', action='append', dest='emails', help='specify the emailers to output (implies --no-texts)')
parser.add_argument('--fast', '-f', action='store_true', help='skip parsing of email timestamps/authors/etc.')
parser.add_argument('--no-texts', '-nt', action='store_true', help='skip text message output')
parser.add_argument('--sort-alphabetical', '-alpha', action='store_true', help='sort emailers alphabetically in counts table')
parser.add_argument('--suppress-output', '-s', action='store_true', help='no output to terminal (use with --build)')
parser.add_argument('--search-other', '-so', action='store_true', help='search for string in non email/text files (only used by search script)')
parser.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
parser.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
parser.add_argument('positional_args', nargs='*', help='Optional args (only used by helper scripts)')
args = parser.parse_args()

deep_debug = args.deep_debug or is_env_var_set('DEEP_DEBUG')
is_build = args.build or is_env_var_set('BUILD_HTML')
is_debug = deep_debug or args.debug or is_env_var_set('DEBUG')
is_fast_mode = args.fast or is_env_var_set('FAST')
skip_texts = args.no_texts or is_env_var_set('NO_TEXTS')
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
