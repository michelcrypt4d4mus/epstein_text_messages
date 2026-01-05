import logging
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from sys import argv

from epstein_files.util.logging import datefinder_logger, env_log_level, logger

COUNT_WORDS_SCRIPT = 'count_words.py'
DEFAULT_WIDTH = 145
HTML_SCRIPTS = ['epstein_generate', 'generate_html.py', COUNT_WORDS_SCRIPT]


parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML page.")
parser.add_argument('--name', '-n', action='append', dest='names', help='specify the name(s) whose communications should be output')
parser.add_argument('--overwrite-pickle', '-op', action='store_true', help='generate new pickled EpsteinFiles object')

output = parser.add_argument_group('OUTPUT')
output.add_argument('--all-emails', '-ae', action='store_true', help='all the emails instead of just the interesting ones')
output.add_argument('--all-other-files', '-ao', action='store_true', help='all the non-email, non-text msg files instead of just the interesting ones')
output.add_argument('--build', '-b', action='store_true', help='write output to HTML file')
output.add_argument('--make-clean', '-mc', action='store_true', help='delete all build artifact HTML and JSON files')
output.add_argument('--output-emails', '-oe', action='store_true', help='generate other files section')
output.add_argument('--output-other-files', '-oo', action='store_true', help='generate other files section')
output.add_argument('--output-texts', '-ot', action='store_true', help='generate other files section')
output.add_argument('--suppress-output', action='store_true', help='no output to terminal (use with --build)')
output.add_argument('--width', '-w', type=int, default=DEFAULT_WIDTH, help='screen width to use (in characters)')
output.add_argument('--use-epstein-web-links', action='store_true', help='use epsteinweb.org links instead of epstein.media')

scripts = parser.add_argument_group('SCRIPTS', 'Arguments used only by epstein_search, epstein_show, epstein_diff')
scripts.add_argument('positional_args', nargs='*', help='strings to searchs for, file IDs to show or diff, etc.')
scripts.add_argument('--raw', '-r', action='store_true', help='show raw contents of file (only used by scripts)')
scripts.add_argument('--whole-file', '-wf', action='store_true', help='print whole file (only used by epstein_search)')

debug = parser.add_argument_group('DEBUG')
debug.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and links and exit')
debug.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
debug.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
debug.add_argument('--json-metadata', '-jm', action='store_true', help='dump JSON metadata for all files')
debug.add_argument('--json-stats', '-j', action='store_true', help='print JSON formatted stats at the end')
debug.add_argument('--sort-alphabetical', action='store_true', help='sort emailers alphabetically in counts table')
debug.add_argument('--suppress-logs', '-sl', action='store_true', help='set debug level to FATAL')
args = parser.parse_args()

current_script = Path(argv[0]).name
is_env_var_set = lambda s: len(environ.get(s) or '') > 0
is_html_script = current_script in HTML_SCRIPTS

args.debug = args.deep_debug or args.debug or is_env_var_set('DEBUG')
args.output_emails = args.output_emails or args.all_emails
args.output_other_files = args.output_other_files or args.all_other_files
args.overwrite_pickle = args.overwrite_pickle or (is_env_var_set('OVERWRITE_PICKLE') and not is_env_var_set('USE_PICKLED'))
args.width = args.width if is_html_script else None
specified_names: list[str | None] = [None if n == 'None' else n for n in (args.names or [])]


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
datefinder_logger.setLevel(logger.level)


# Massage args that depend on other args to the appropriate state
if not (args.json_metadata or args.output_texts or args.output_emails or args.output_other_files):
    if is_html_script and current_script != COUNT_WORDS_SCRIPT and not args.make_clean and not args.colors_only:
        logger.warning(f"No output section chosen; outputting default selection of texts, selected emails, and other files...")

    args.output_texts = True
    args.output_emails = True
    args.output_other_files = True

if args.use_epstein_web_links:
    logger.warning(f"Using links to epsteinweb.org links instead of epsteinify.com...")

if args.debug:
    logger.warning(f"Invocation args:\ncurrent_script={current_script}\nis_html_script={is_html_script},\nspecified_names={specified_names},\nargs={args}")
