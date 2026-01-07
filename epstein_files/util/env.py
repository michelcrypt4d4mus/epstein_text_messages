import logging
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from sys import argv, exit

from rich_argparse_plus import RichHelpFormatterPlus

from epstein_files.util.logging import env_log_level, logger

DEFAULT_WIDTH = 145
HTML_SCRIPTS = ['epstein_generate', 'epstein_word_count']


RichHelpFormatterPlus.choose_theme('morning_glory')
parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML pages.", formatter_class=RichHelpFormatterPlus)
parser.add_argument('--make-clean', action='store_true', help='delete all HTML build artifact and write latest URLs to .urls.env')
parser.add_argument('--name', '-n', action='append', dest='names', help='specify the name(s) whose communications should be output')
parser.add_argument('--overwrite-pickle', '-op', action='store_true', help='re-parse the files and ovewrite cached data')

output = parser.add_argument_group('OUTPUT', 'Options used by epstein_generate.')
output.add_argument('--all-emails', '-ae', action='store_true', help='all the emails instead of just the interesting ones')
output.add_argument('--all-other-files', '-ao', action='store_true', help='all the non-email, non-text msg files instead of just the interesting ones')
output.add_argument('--build', '-b', action='store_true', help='write HTML output to a file')
output.add_argument('--json-files', action='store_true', help='pretty print all the raw JSON data files in the collection and exit')
output.add_argument('--json-metadata', action='store_true', help='dump JSON metadata for all files and exit')
output.add_argument('--output-emails', '-oe', action='store_true', help='generate emails section')
output.add_argument('--output-other', '-oo', action='store_true', help='generate other files section')
output.add_argument('--output-texts', '-ot', action='store_true', help='generate text messages section')
output.add_argument('--sort-alphabetical', action='store_true', help='sort emailers alphabetically intead of by email count')
output.add_argument('--suppress-output', action='store_true', help='no output to terminal (use with --build)')
output.add_argument('--uninteresting', action='store_true', help='only output uninteresting other files')
output.add_argument('--width', '-w', type=int, default=DEFAULT_WIDTH, help='screen width to use (in characters)')

scripts = parser.add_argument_group('SCRIPTS', 'Options used by epstein_search, epstein_show, and epstein_diff.')
scripts.add_argument('positional_args', nargs='*', help='strings to searchs for, file IDs to show or diff, etc.')
scripts.add_argument('--raw', '-r', action='store_true', help='show raw contents of file (used by epstein_show)')
scripts.add_argument('--whole-file', '-wf', action='store_true', help='print whole file (used by epstein_search)')

debug = parser.add_argument_group('DEBUG')
debug.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and links and exit')
debug.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
debug.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
debug.add_argument('--json-stats', '-j', action='store_true', help='print JSON formatted stats about the files')
debug.add_argument('--skip-other-files', '-sof', action='store_true', help='skip parsing non email/text files')
debug.add_argument('--suppress-logs', '-sl', action='store_true', help='set debug level to FATAL')
args = parser.parse_args()


# Verify Epstein docs can be found
EPSTEIN_DOCS_DIR_ENV_VAR_NAME = 'EPSTEIN_DOCS_DIR'
DOCS_DIR_ENV = environ.get(EPSTEIN_DOCS_DIR_ENV_VAR_NAME)
DOCS_DIR = Path(DOCS_DIR_ENV or '').resolve()

if not DOCS_DIR_ENV:
    print(f"\n   ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME} env var not set!\n")
    exit(1)
elif not DOCS_DIR.exists():
    print(f"\n   ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME}='{DOCS_DIR}' does not exist!\n")
    exit(1)

current_script = Path(argv[0]).name
is_env_var_set = lambda s: len(environ.get(s) or '') > 0
is_html_script = current_script in HTML_SCRIPTS

args.debug = args.deep_debug or args.debug or is_env_var_set('DEBUG')
args.names = [None if n == 'None' else n for n in (args.names or [])]
args.output_emails = args.output_emails or args.all_emails
args.output_other = args.output_other or args.all_other_files or args.uninteresting
args.overwrite_pickle = args.overwrite_pickle or (is_env_var_set('OVERWRITE_PICKLE') and not is_env_var_set('PICKLED'))
args.width = args.width if is_html_script else None
is_any_output_selected = any([arg.startswith('output_') and value for arg, value in vars(args).items()])
is_any_output_selected = is_any_output_selected or args.json_metadata or args.colors_only

# Log level args
if args.deep_debug:
    logger.setLevel(logging.DEBUG)
elif args.debug:
    logger.setLevel(logging.INFO)
elif args.suppress_logs:
    logger.setLevel(logging.FATAL)
elif not env_log_level:
    logger.setLevel(logging.WARNING)

logger.info(f'Log level set to {logger.level}...')

# Massage args that depend on other args to the appropriate state
if current_script == 'epstein_generate' and not (is_any_output_selected or args.make_clean):
    logger.warning(f"No output section chosen; outputting default selection of texts, selected emails, and other files...")
    args.output_texts = args.output_emails = args.output_other = True

if args.debug:
    logger.warning(f"Invocation args:\ncurrent_script={current_script}\nis_html_script={is_html_script},\nis_output_selected={is_any_output_selected},\nargs={args}")

if args.names:
    logger.warning(f"Output restricted to {args.names}")
