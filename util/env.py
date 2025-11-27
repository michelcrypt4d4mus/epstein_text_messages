from argparse import ArgumentParser
from os import environ


parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML page.")
parser.add_argument('--build', '-b', action='store_true', help='write HTML to docs/index.html')
parser.add_argument('--fast', '-f', action='store_true', help='skip parsing of email timestamps/authors/etc.')
parser.add_argument('--skip-texts', '-s', action='store_true', help='skip text message output')
parser.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
parser.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
args = parser.parse_args()

deep_debug = args.deep_debug or (len(environ.get('DEEP_DEBUG') or '') > 0)
is_debug = deep_debug or args.debug or (len(environ.get('DEBUG') or '') > 0)
is_build = args.build or (len(environ.get('BUILD_HTML') or '') > 0)
is_fast_mode = args.fast or (len(environ.get('FAST') or '') > 0)
skip_texts = args.skip_texts or (len(environ.get('SKIP_TEXTS') or '') > 0)
