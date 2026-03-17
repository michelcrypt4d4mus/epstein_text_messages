import logging
from argparse import ArgumentParser
from os import environ
from pathlib import Path

from rich_argparse_plus import RichHelpFormatterPlus

from epstein_files.output.site.site_config import ALL_OTHER_FILES_MULTIPLIER, DEFAULT_WIDTH, MobileConfig, SiteConfig
from epstein_files.output.site.sites import *
from epstein_files.util.constant.strings import SUPPRESS_OUTPUT
from epstein_files.util.helpers.env_helpers import get_env_dir
from epstein_files.util.logging import env_log_level, exit_with_error, logger, set_log_level

BUILD_TRUE_BUT_UNSPECIFIED = 'default_file'  # default value if --build is specified without an arg
EPSTEIN_GENERATE = 'epstein_generate'
HTML_SCRIPTS = [EPSTEIN_GENERATE]
PICKLED_PATH = Path("the_epstein_files.local.pkl.gz")

# Get source file dirs from these vars
DOCS_DIR_ENV_VAR = 'EPSTEIN_DOCS_DIR'
DOJ_PDFS_20260130_DIR_ENV_VAR = 'EPSTEIN_DOJ_PDFS_20260130_DIR'
DOJ_TXTS_20260130_DIR_ENV_VAR = 'EPSTEIN_DOJ_TXTS_20260130_DIR'
DROPSITE_EMLS_DIR_ENV_VAR = 'DROPSITE_EMLS_DIR'

DOCS_DIR: Path = get_env_dir(DOCS_DIR_ENV_VAR, must_exist=True)
DOJ_PDFS_20260130_DIR: Path = get_env_dir(DOJ_PDFS_20260130_DIR_ENV_VAR, must_exist=False)
DOJ_TXTS_20260130_DIR: Path = get_env_dir(DOJ_TXTS_20260130_DIR_ENV_VAR, must_exist=False)
DROPSITE_EMLS_DIR: Path = get_env_dir(DROPSITE_EMLS_DIR_ENV_VAR, must_exist=False)

is_env_var_set = lambda s: len(environ.get(s) or '') > 0
is_output_arg = lambda arg: any([arg.startswith(pfx) for pfx in ['all', 'colors_only', 'json', 'make_clean', 'output', 'show']])


RichHelpFormatterPlus.choose_theme('morning_glory')
parser = ArgumentParser(description="Parse epstein OCR docs and generate HTML pages.", formatter_class=RichHelpFormatterPlus)
parser.add_argument('--make-clean', action='store_true', help='delete all HTML build artifact and write latest URLs to .urls.env')
parser.add_argument('--name', '-n', action='append', dest='names', help='specify the name(s) whose communications should be output')
parser.add_argument('--overwrite-pickle', '-op', action='store_true', help='re-parse the files and ovewrite cached data')
parser.add_argument('--pickle-path', '-fp', help='path to load saved data from', default=PICKLED_PATH)
parser.add_argument('--use-custom-html', action='store_true', help='overwrite rich html exports with custom HTML exports')

# Any output arg that doesn't start with --all is curated, meaning uninteresting documents will be suppressed
output = parser.add_argument_group('OUTPUT', 'Options used by epstein_generate.')
output.add_argument('--all-doj-files', '-ad', action='store_true', help='all the DOJ files from 2026-01-30')
output.add_argument('--all-emails', '-ae', action='store_true', help='all the emails instead of just the interesting ones')
output.add_argument('--all-emails-chrono', '-aec', action='store_true', help='all emails in chronological order')
output.add_argument('--all-other-files', '-ao', action='store_true', help='all the non-email, non-text msg files instead of just the interesting ones')
output.add_argument('--all-texts', '-at', action='store_true', help='all the text messages instead of just the interesting ones')
parser.add_argument('--build', '-b', nargs="?", default=None, const=BUILD_TRUE_BUT_UNSPECIFIED, help='write output to HTML file')
output.add_argument('--emailers-info', '-ei', action='store_true', help='write a .png of the eeailers info table')
output.add_argument('--json-files', action='store_true', help='pretty print all the raw JSON data files in the collection and exit')
output.add_argument('--json-metadata', '-jm', action='store_true', help='dump JSON metadata for all files and exit')
output.add_argument('--mobile', '-mob', action='store_true', help='build a mobile version of the site')
output.add_argument('--output-bios', '-bios', action='store_true', help='output one line biographies + links for all Contacts')
output.add_argument('--output-chrono', '-oc', action='store_true', help='output curated files of all types in chronological order')
output.add_argument('--output-devices', '-od', action='store_true', help='output "Sent from my iPhone" style device signature')
output.add_argument('--output-emails', '-oe', action='store_true', help='generate emails section')
output.add_argument('--output-other', '-oo', action='store_true', help='generate other files section')
output.add_argument('--output-texts', '-ot', action='store_true', help='generate text messages section')
output.add_argument('--output-word-count', '-ow', action='store_true', help='generate table of most frequently used words')
output.add_argument('--sort-alphabetical', action='store_true', help='sort tables alphabetically intead of by count')
output.add_argument(SUPPRESS_OUTPUT, action='store_true', help='no output to terminal (use with --build)')
output.add_argument('--uninteresting', action='store_true', help='only output uninteresting other files')
output.add_argument('--width', '-w', type=int, default=DEFAULT_WIDTH, help='screen width to use (in characters)')

scripts = parser.add_argument_group('SCRIPTS', 'Options used by epstein_grep, epstein_show, and epstein_diff.')
scripts.add_argument('positional_args', nargs='*', help='strings to searchs for, file IDs to show or diff, etc.')
scripts.add_argument('--email-body', action='store_true', help='epstein_grep but only for the body of the email')
scripts.add_argument('--min-line-length', type=int, help='epstein_grep minimum length of a matched line')
scripts.add_argument('--open-both', '-ob', action='store_true', help='open the source PDF and txt after showing')
scripts.add_argument('--open-pdf', '-pdf', action='store_true', help='open the source PDF file after showing (if it exists)')
scripts.add_argument('--open-txt', '-o', action='store_true', help='open the file in a text editor after showing')
scripts.add_argument('--open-url', '-web', action='store_true', help='open the source URL in a web browser')
scripts.add_argument('--raw', action='store_true', help='show raw contents of file (used by epstein_show)')
scripts.add_argument('--whole-file', '-wf', action='store_true', help='print whole files')

debug = parser.add_argument_group('DEBUG')
debug.add_argument('--char-nums', '-cn', nargs="?", default=None, const=100, type=int, help='inject char nums every N chars')
debug.add_argument('--colors-only', '-c', action='store_true', help='print header with color key table and links and exit')
debug.add_argument('--constantize', action='store_true', help='constantize names when printing repr() of objects')
debug.add_argument('--debug', '-d', action='store_true', help='set debug level to INFO')
debug.add_argument('--deep-debug', '-dd', action='store_true', help='set debug level to DEBUG')
debug.add_argument('--invert-chrono', action='store_true', help='uninteresting emails in chrono view instead of interesting ones')
debug.add_argument('--load-new', '-ln', action='store_true', help='load any new files and write pickle file')
debug.add_argument('--max-records', '-mr', type=int, help='maximum number of records to print')
debug.add_argument('--panelize-emails', '-pe', action='store_true', help='show email descriptions in Panels instead of Tables')
debug.add_argument('--reload-doj', '-rd', action='store_true', help='reload only the DOJ files, not HOUSE_OVERSIGHT')
debug.add_argument('--repair', '-r', action='store_true', help='reload file IDs specified in the positional args')
debug.add_argument('--show-urls', '-urls', action='store_true', help='show the site URLs generated by this code')
debug.add_argument('--stats', '-j', action='store_true', help='print JSON formatted stats about the files')
debug.add_argument('--suppress-logs', '-sl', action='store_true', help='set debug level to FATAL')
debug.add_argument('--truncate', '-t', type=int, help='truncate emails to this many characters')
debug.add_argument('--write-txt', '-wt', action='store_true', help='write a plain text version of output')


# Parse args
if environ.get('INVOKED_BY_PYTEST'):
    args = parser.parse_args([EPSTEIN_GENERATE])
else:
    args = parser.parse_args()

is_html_script = parser.prog in HTML_SCRIPTS or 'html' in parser.prog
site_config = MobileConfig if args.mobile else SiteConfig
logger.info(f"site_config set to {site_config.__name__}...")

args.debug = args.deep_debug or args.debug or is_env_var_set('DEBUG')
args._debug_highlight_patterns = (args.colors_only and args.debug)
args._site_type = SiteType.CURATED  # TODO: not ideal

# args.names = [name.title() for name in args.names] if args.names and args.names[0][0].islower() else args.names
args.names = [None if n == 'None' else n.strip() for n in (args.names or [])]
args.output_emails = args.output_emails or args.all_emails
args.output_other = args.output_other or args.all_other_files or args.uninteresting
args.output_texts = args.output_texts or args.all_texts
args.overwrite_pickle = args.overwrite_pickle or (is_env_var_set('OVERWRITE_PICKLE') and not is_env_var_set('PICKLED'))
args.width = site_config.width if is_html_script else None

truthy_args = {k: v for k, v in vars(args).items() if v}
any_output_selected = any(is_output_arg(k) for k in truthy_args.keys())
args._suppress_uninteresting = not (args.names or any(k.startswith('all_') for k in truthy_args.keys()))

if not (any_output_selected or args.all_emails_chrono or args.emailers_info or args.stats):
    if is_html_script:
        logger.warning(f"No output section chosen; outputting default selection of texts, selected emails, and other files...")

    args.output_emails = args.output_other = args.output_texts = True

if (args.output_chrono or args.all_emails_chrono or args.output_emails) and not args.build:
    logger.warning(f"--output-chrono requires --build to export new HTML, setting...")
    args.build = BUILD_TRUE_BUT_UNSPECIFIED

if is_html_script:
    if args.repair:
        if not args.positional_args:
            exit_with_error(f"--repair requires positional args")
    elif args.positional_args:
        exit_with_error(f"{parser.prog} does not accept positional arguments (receeived {args.positional_args})")

    if 'sample_html' in parser.prog:
        args._site_type = SiteType.SAMPLE
    elif args.mobile:
        if args.output_chrono:
            args._site_type = SiteType.CHRONOLOGICAL_MOBILE
        else:
            logger.warning(f"Mobile site type couldn't be conclusively determined, settings to {SiteType.CURATED_MOBILE}...")
            args._site_type = SiteType.CURATED_MOBILE  # This isn't great; requires args be correct to build
    else:
        if args.names:
            args._site_type = SiteType.NAMES  # --name args overrides other considerations
        elif args.colors_only:
            args._site_type = SiteType.COLORS_ONLY
            args.build = args.build or BUILD_TRUE_BUT_UNSPECIFIED
        elif args.output_bios:
            args._site_type = SiteType.BIOGRAPHIES
        elif args.all_doj_files:
            args._site_type = SiteType.DOJ_FILES
        elif args.all_emails:
            args._site_type = SiteType.EMAILS
        elif args.all_emails_chrono:
            args._site_type = SiteType.EMAILS_CHRONOLOGICAL
        elif args.all_texts:
            args._site_type = SiteType.TEXT_MESSAGES
        elif args.all_other_files:
            args._site_type = SiteType.OTHER_FILES_TABLE
        elif args.json_metadata:
            args._site_type = SiteType.JSON_METADATA
        elif args.output_chrono:
            args._site_type = SiteType.CHRONOLOGICAL
        elif args.output_devices:
            args._site_type = SiteType.DEVICE_SIGNATURES
        elif args.output_word_count:
            args._site_type = SiteType.WORD_COUNT
        else:
            logger.warning(f"Site type couldn't be conclusively determined, settings to {SiteType.CURATED}...")
            args._site_type = SiteType.CURATED
elif parser.prog.startswith('epstein_') and not args.positional_args and not args.names:
    exit_with_error(f"{parser.prog} requires positional arguments but got none!")

# More preview chars in OtherFile table if it's --all-other-files
if args.all_other_files:
    site_config.other_files_preview_chars = int(site_config.other_files_preview_chars * ALL_OTHER_FILES_MULTIPLIER)

if args.names:
    logger.warning(f"Output restricted to {args.names}")
    args.output_other = False

if args.truncate and args.whole_file:
    exit_with_error(f"--whole-file and --truncate are incompatible")
elif args.char_nums and not args.truncate:
    args.whole_file = True

if args.open_both:
    args.open_pdf = True
    args.open_txt = True

if args.repair or args.load_new:
    args.constantize = True

# Log level args
if args.deep_debug:
    set_log_level(logging.DEBUG)
elif args.debug:
    set_log_level(logging.INFO)
elif args.suppress_logs:
    set_log_level(logging.FATAL)
elif not env_log_level:
    set_log_level(logging.WARNING)

logger.debug(f'Log level set to {logger.level}...')
args_str = ',\n'.join([f"{k}={v}" for k, v in vars(args).items() if v])
logger.debug(f"'{parser.prog}' script invoked\n{args_str}")
logger.debug(f"Reading Epstein documents from '{DOCS_DIR}'...")
