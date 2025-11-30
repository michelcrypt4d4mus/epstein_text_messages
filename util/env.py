import logging
from argparse import ArgumentParser
from os import environ

from rich.logging import RichHandler


parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML page.")
parser.add_argument('--build', '-b', action='store_true', help='write HTML to docs/index.html')
parser.add_argument('--email', '-e', action='append', dest='emails', help='specify additional emailers to output')
parser.add_argument('--all', '-a', action='store_true', help='all email authors and recipients (except Epstein)')
parser.add_argument('--all-tables', '-at', action='store_true', help='all email tables (except Epstein)')
parser.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and exit')
parser.add_argument('--fast', '-f', action='store_true', help='skip parsing of email timestamps/authors/etc.')
parser.add_argument('--no-highlights', '-nh', action='store_true', help="don't color highligh text (faster)")
parser.add_argument('--no-texts', '-nt', action='store_true', help='skip text message output')
parser.add_argument('--sort-alphabetical', '-alpha', action='store_true', help='sort emailers alphabetically in counts table')
parser.add_argument('--suppress-output', '-sup', action='store_true', help='no output to terminal (use with --build)')
parser.add_argument('--search', '-s', action='append', help='search for string in repaired OCR text')
parser.add_argument('--search-other', '-so', action='append', help='search for string in non email/text files')
parser.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
parser.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
args = parser.parse_args()

deep_debug = args.deep_debug or (len(environ.get('DEEP_DEBUG') or '') > 0)
is_build = args.build or (len(environ.get('BUILD_HTML') or '') > 0)
is_debug = deep_debug or args.debug or (len(environ.get('DEBUG') or '') > 0)
is_fast_mode = args.fast or (len(environ.get('FAST') or '') > 0)
skip_texts = args.no_texts or (len(environ.get('SKIP_TEXTS') or '') > 0)

additional_emailers = args.emails or []
args.search = args.search or []
args.search_other = args.search_other or []

# Setup logging
logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("rich")

if deep_debug:
    logger.setLevel(logging.DEBUG)
elif is_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)
