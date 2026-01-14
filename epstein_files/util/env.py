import logging
from argparse import ArgumentParser
from os import environ
from pathlib import Path

from rich_argparse_plus import RichHelpFormatterPlus

from epstein_files.util.constant.output_files import ALL_EMAILS_PATH, CHRONOLOGICAL_EMAILS_PATH, TEXT_MSGS_HTML_PATH
from epstein_files.util.logging import env_log_level, exit_with_error, logger

DEFAULT_WIDTH = 155
DEFAULT_FILE = 'default_file'
EPSTEIN_GENERATE = 'epstein_generate'
HTML_SCRIPTS = [EPSTEIN_GENERATE, 'epstein_word_count']

# Verify Epstein docs dir exists
EPSTEIN_DOCS_DIR_ENV_VAR_NAME = 'EPSTEIN_DOCS_DIR'
DOCS_DIR_ENV = environ.get(EPSTEIN_DOCS_DIR_ENV_VAR_NAME)
DOCS_DIR = Path(DOCS_DIR_ENV or '').resolve()

if not DOCS_DIR_ENV:
    exit_with_error(f"{EPSTEIN_DOCS_DIR_ENV_VAR_NAME} env var not set!\n")
elif not DOCS_DIR.exists():
    exit_with_error(f"{EPSTEIN_DOCS_DIR_ENV_VAR_NAME}='{DOCS_DIR}' does not exist!\n")

is_env_var_set = lambda s: len(environ.get(s) or '') > 0
is_output_arg = lambda arg: any([arg.startswith(pfx) for pfx in ['colors_only', 'json', 'make_clean', 'output']])


RichHelpFormatterPlus.choose_theme('morning_glory')
parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML pages.", formatter_class=RichHelpFormatterPlus)
parser.add_argument('--make-clean', action='store_true', help='delete all HTML build artifact and write latest URLs to .urls.env')
parser.add_argument('--name', '-n', action='append', dest='names', help='specify the name(s) whose communications should be output')
parser.add_argument('--overwrite-pickle', '-op', action='store_true', help='re-parse the files and ovewrite cached data')

output = parser.add_argument_group('OUTPUT', 'Options used by epstein_generate.')
output.add_argument('--all-emails', '-ae', action='store_true', help='all the emails instead of just the interesting ones')
output.add_argument('--all-other-files', '-ao', action='store_true', help='all the non-email, non-text msg files instead of just the interesting ones')
parser.add_argument('--build', '-b', nargs="?", default=None, const=DEFAULT_FILE, help='write output to HTML file')
output.add_argument('--email-timeline', action='store_true', help='print a table of all emails in chronological order')
output.add_argument('--emailers-info', '-ei', action='store_true', help='write a .png of the eeailers info table')
output.add_argument('--json-files', action='store_true', help='pretty print all the raw JSON data files in the collection and exit')
output.add_argument('--json-metadata', action='store_true', help='dump JSON metadata for all files and exit')
output.add_argument('--output-emails', '-oe', action='store_true', help='generate emails section')
output.add_argument('--output-other', '-oo', action='store_true', help='generate other files section')
output.add_argument('--output-texts', '-ot', action='store_true', help='generate text messages section')
output.add_argument('--sort-alphabetical', action='store_true', help='sort tables alphabetically intead of by count')
output.add_argument('--suppress-output', action='store_true', help='no output to terminal (use with --build)')
output.add_argument('--uninteresting', action='store_true', help='only output uninteresting other files')
output.add_argument('--width', '-w', type=int, default=DEFAULT_WIDTH, help='screen width to use (in characters)')

scripts = parser.add_argument_group('SCRIPTS', 'Options used by epstein_search, epstein_show, and epstein_diff.')
scripts.add_argument('positional_args', nargs='*', help='strings to searchs for, file IDs to show or diff, etc.')
scripts.add_argument('--raw', '-r', action='store_true', help='show raw contents of file (used by epstein_show)')
scripts.add_argument('--whole-file', '-wf', action='store_true', help='print whole files')

debug = parser.add_argument_group('DEBUG')
debug.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and links and exit')
debug.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
debug.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
debug.add_argument('--json-stats', '-j', action='store_true', help='print JSON formatted stats about the files')
debug.add_argument('--skip-other-files', '-sof', action='store_true', help='skip parsing non email/text files')
debug.add_argument('--suppress-logs', '-sl', action='store_true', help='set debug level to FATAL')
debug.add_argument('--truncate', '-t', type=int, help='truncate emails to this many characters')
debug.add_argument('--write-txt', '-wt', action='store_true', help='write a plain text version of output')


# Parse args
args = parser.parse_args()
is_html_script = parser.prog in HTML_SCRIPTS

args.build = args.build
args.debug = args.deep_debug or args.debug or is_env_var_set('DEBUG')
args.names = [None if n == 'None' else n.strip() for n in (args.names or [])]
args.output_emails = args.output_emails or args.all_emails
args.output_other = args.output_other or args.all_other_files or args.uninteresting
args.overwrite_pickle = args.overwrite_pickle or (is_env_var_set('OVERWRITE_PICKLE') and not is_env_var_set('PICKLED'))
args.width = args.width if is_html_script else None

if is_html_script:
    if args.positional_args:
        exit_with_error(f"{parser.prog} does not accept positional arguments (receeived {args.positional_args})")

    if parser.prog == EPSTEIN_GENERATE:
        if any([is_output_arg(arg) and val for arg, val in vars(args).items()]):
            if args.email_timeline:
                exit_with_error(f"--email-timeline option is mutually exlusive with other output options")
        elif not args.email_timeline and not args.emailers_info:
            logger.warning(f"No output section chosen; outputting default selection of texts, selected emails, and other files...")
            args.output_texts = args.output_emails = args.output_other = True

    if args.build == DEFAULT_FILE:
        if args.all_emails:
            args.build = ALL_EMAILS_PATH
        elif args.email_timeline:
            args.build = CHRONOLOGICAL_EMAILS_PATH
        else:
            args.build = TEXT_MSGS_HTML_PATH
elif parser.prog.startswith('epstein_') and not args.positional_args:
    exit_with_error(f"{parser.prog} requires positional arguments but got none!")

if args.names:
    logger.warning(f"Output restricted to {args.names}")
    args.output_other = False


# Log level args
if args.deep_debug:
    logger.setLevel(logging.DEBUG)
elif args.debug:
    logger.setLevel(logging.INFO)
elif args.suppress_logs:
    logger.setLevel(logging.FATAL)
elif not env_log_level:
    logger.setLevel(logging.WARNING)

logger.debug(f'Log level set to {logger.level}...')
args_str = ',\n'.join([f"{k}={v}" for k, v in vars(args).items() if v])
logger.info(f"'{parser.prog}' script invoked\n{args_str}")
logger.debug(f"Reading Epstein documents from '{DOCS_DIR}'...")
