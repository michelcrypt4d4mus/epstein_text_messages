import csv
import json
import logging
import re
import urllib.parse
from io import StringIO

from rich.align import Align
from rich.console import Console
from rich.logging import RichHandler
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .env import deep_debug, is_debug
from .file_helper import extract_file_id

LEADING_WHITESPACE_REGEX = re.compile(r'\A\s*', re.MULTILINE)
MAX_PREVIEW_CHARS = 300
OUTPUT_WIDTH = 120

ARCHIVE_LINK = 'archive_link'
ARCHIVE_LINK_COLOR = 'blue3'
PHONE_NUMBER = 'phone_number'
TEXT_LINK = 'text_link'

# Email Names
# Names
AL_SECKEL = 'Al Seckel'
ARIANE_DE_ROTHSCHILD = 'Ariane de Rothschild'
BARBRO_EHNBOM = 'Barbro Ehnbom'
DARREN_INDKE = 'Darren Indke'
EDWARD_EPSTEIN = 'Edward Epstein'
EHUD_BARAK = 'Ehud Barak'
GHISLAINE_MAXWELL = 'Ghislaine Maxwell'
JEFFREY_EPSTEIN = 'Jeffrey Epstein'
JOHN_PAGE = 'John Page'
JOHNNY_EL_HACHEM = 'Johnny el Hachem'
JONATHAN_FARKAS = 'Jonathan Farkas'
LAWRENCE_KRAUSS = 'Lawrence Krauss'
LAWRANCE_VISOSKI = 'Lawrance Visoski'
LEON_BLACK = 'Leon Black'
NADIA_MARCINKO = 'Nadia Marcinko'
STEVE_BANNON = 'Steve Bannon'
REDACTED = '[REDACTED]'

# Texting Names
ANIL = "Anil Ambani"
BANNON = 'Bannon'
DEFAULT = 'default'
EPSTEIN = 'Epstein'
EVA = 'Eva'
JOI_ITO = 'Joi Ito'
LARRY_SUMMERS = 'Larry Summers'
MELANIE_WALKER = 'Melanie Walker'
MIROSLAV = 'Miroslav Lajčák'
PLASKETT = 'Stacey Plaskett'
SCARAMUCCI = 'The Mooch'
SOON_YI = 'Soon-Yi Previn'
TERJE = 'Terje Rød-Larsen'
UNKNOWN = '(unknown)'

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    ANIL: 'dark_green',
    ARCHIVE_LINK: 'deep_sky_blue4',
    BANNON: 'color(58)',
    'Celina Dubin': 'medium_orchid1',
    DEFAULT: 'wheat4',
    EPSTEIN: 'blue',
    EVA: 'orchid',
    JOI_ITO: 'blue_violet',
    LARRY_SUMMERS: 'bright_red',
    MELANIE_WALKER: 'deep_pink3',
    MIROSLAV: 'slate_blue3',
    "Michael Wolff": 'grey54',
    PHONE_NUMBER: 'bright_green',
    PLASKETT: 'medium_orchid3',
    SCARAMUCCI: 'orange1',
    SOON_YI: 'hot_pink',
    TERJE: 'light_slate_blue',
    TEXT_LINK: 'deep_sky_blue4 underline',
    UNKNOWN: 'cyan',
}

PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED = {
    None: 'grey74',
    STEVE_BANNON: COUNTERPARTY_COLORS[BANNON],
    'Sean Bannon': COUNTERPARTY_COLORS[BANNON],
    GHISLAINE_MAXWELL: 'deep_pink3',
    AL_SECKEL: 'orange_red1',
    EHUD_BARAK: 'chartreuse4',
    LEON_BLACK: 'bright_red',
    'Sultan bin Sulayem': 'green1',
    'Deepak Chopra': 'dark_goldenrod',
    'Darren Indke': 'purple3',
    'Richard Kahn': 'purple4',
}

COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED)

for counterparty in COUNTERPARTY_COLORS:
    COUNTERPARTY_COLORS[counterparty] = f"{COUNTERPARTY_COLORS[counterparty]} bold"


KNOWN_COUNTERPARTY_FILE_IDS = {
    '031042': ANIL,            # Participants: field
    '027225': ANIL,            # Birthday
    '031173': 'Ards',          # Participants: field, possibly incomplete
    '025707': BANNON,
    '025734': BANNON,
    '025452': BANNON,
    '025408': BANNON,
    '027307': BANNON,
    '027401': EVA,             # Participants: field
    '027650': JOI_ITO,         # Participants: field
    '027515': MIROSLAV,        # https://x.com/ImDrinknWyn/status/1990210266114789713
    '027165': MELANIE_WALKER,  # https://www.wired.com/story/jeffrey-epstein-claimed-intimate-knowledge-of-donald-trumps-views-in-texts-with-bill-gates-adviser/
    '025429': PLASKETT,
    '027333': SCARAMUCCI,      # unredacted phone number
    '027128': SOON_YI,         # https://x.com/ImDrinknWyn/status/1990227281101434923
    '027217': SOON_YI,         # refs marriage to woody allen
    '027244': SOON_YI,         # refs Woody
    '027257': SOON_YI,         # 'Woody Allen' in Participants: field
    '027777': LARRY_SUMMERS,
    '027278': TERJE,
    '027255': TERJE,
}

GUESSED_COUNTERPARTY_FILE_IDS = {
    '027221': ANIL,
    '025363': BANNON,          # Trump and New York Times coverage
    '025368': BANNON,          # Trump and New York Times coverage
    '027585': BANNON,          # Tokyo trip
    '027568': BANNON,
    '027695': BANNON,
    '027594': BANNON,
    '027720': BANNON,          # first 3 lines of 027722
    '027549': BANNON,
    '027434': BANNON,          # References Maher appearance
    '027764': BANNON,
    '025436': 'Celina Dubin',
    '027576': MELANIE_WALKER,  # https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.023700
    '027141': MELANIE_WALKER,
    '027232': MELANIE_WALKER,
    '027133': MELANIE_WALKER,
    '027184': MELANIE_WALKER,
    '027214': MELANIE_WALKER,
    '027148': MELANIE_WALKER,
    '027396': SCARAMUCCI,
    '031054': SCARAMUCCI,
}

#  of who is the counterparty in each file
AI_COUNTERPARTY_DETERMINATION_TSV = StringIO("""
filename	counterparty	source
HOUSE_OVERSIGHT_025400.txt	Steve Bannon (likely)	Trump NYT article criticism; Hannity media strategy
HOUSE_OVERSIGHT_025408.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025452.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025479.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_025707.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025734.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027260.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027281.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027346.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027365.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027374.txt	Steve Bannon	China strategy and geopolitics
HOUSE_OVERSIGHT_027406.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027440.txt	Michael Wolff	Trump book/journalism project
HOUSE_OVERSIGHT_027445.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027455.txt	Steve Bannon (likely)	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027460.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027515.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027536.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027655.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027707.txt	Steve Bannon	Italian politics; Trump discussions
HOUSE_OVERSIGHT_027722.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027735.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027794.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_029744.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031045.txt	Steve Bannon (likely)	Trump and New York Times coverage""".strip())

CONSOLE_HTML_FORMAT = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {stylesheet}
        body {{
            color: {foreground};
            background-color: {background};
        }}
    </style>
</head>
<body>
    <pre style="font-family: Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace; white-space: pre-wrap; overflow-wrap: break-word;">
        <code style="font-family: inherit; white-space: pre-wrap; overflow-wrap: break-word;">
            {code}
        </code>
    </pre>
</body>
</html>
"""


COURIER_NEWSROOM_ARCHIVE = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
search_archive_url = lambda txt: f"{COURIER_NEWSROOM_ARCHIVE}&page=1&q={urllib.parse.quote(txt)}&p=1"


for row in csv.DictReader(AI_COUNTERPARTY_DETERMINATION_TSV, delimiter='\t'):
    file_id = extract_file_id(row['filename'].strip())
    counterparty = row['counterparty'].strip()
    counterparty = BANNON if counterparty.startswith('Steve Bannon') else counterparty

    if file_id in GUESSED_COUNTERPARTY_FILE_IDS:
        raise RuntimeError(f"Can't overwrite attribution of {file_id} to {GUESSED_COUNTERPARTY_FILE_IDS[file_id]} with {counterparty}")

    GUESSED_COUNTERPARTY_FILE_IDS[file_id] = counterparty.replace(' (likely)', '').strip()

logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("rich")

if deep_debug:
    logger.setLevel(logging.DEBUG)
elif is_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)

console = Console(color_system='256', theme=Theme(COUNTERPARTY_COLORS), width=OUTPUT_WIDTH)
console.record = True


def archive_link(filename: str, style: str = ARCHIVE_LINK_COLOR) -> str:
    return f"[bold][{style}][link={search_archive_url(filename)}]{filename}[/link][/{style}][/bold]"


def print_header():
    console.line()
    console.print(Panel(Text("Epstein Estate Documents - Seventh Production Collection Reformatted Text Messages", justify='center', style='bold reverse')))
    console.line()
    console.print(Align.center("[bold][link=https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great]I Made Epstein's Text Messages Great Again (And You Should Read Them)[/link][/bold]"))
    console.print(Align.center("https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great"))
    console.print(Align.center("[link=https://cryptadamus.substack.com/]Substack[/link]"))
    console.print(Align.center("[link=https://universeodon.com/@cryptadamist]Mastodon[/link]"))
    console.print(Align.center("[link=https://x.com/Cryptadamist/status/1990866804630036988]Twitter[/link]"))
    # Acronym table
    table = Table(title="Abbreviations Used Frequently In These Chats", show_header=True, header_style="bold")
    table.add_column("Abbreviation", style="steel_blue bold", justify="center", width=19)
    table.add_column("Translation", style="deep_sky_blue4", justify="center")
    table.add_row("AD", "Abu Dhabi")
    table.add_row("Barak", "Ehud Barak (Former Israeli prime minister)")
    table.add_row("Barrack", "Tom Barrack")
    table.add_row('BG', "Bill Gates")
    table.add_row('Bill', "Bill Gates")
    table.add_row("Brock", "Brock Pierce")
    table.add_row("DB", "Deutsche Bank (maybe??)")
    table.add_row('HBJ', "Hamad bin Jassim (Former Qatari Prime Minister)")
    table.add_row('Jagland', 'Thorbjørn Jagland')
    table.add_row("Hoffenberg", "Steven Hoffenberg (Epstein's partner in old ponzi scheme)")
    table.add_row('KSA', "Kingdom of Saudi Arabia")
    table.add_row('MBS', "Mohammed bin Salman Al Saud (Saudi ruler)")
    table.add_row('Jared', "Jared Kushner")
    table.add_row("Miro", MIROSLAV)
    table.add_row("Mooch", "Anthony 'The Mooch' Scaramucci (Skybridge Capital)")
    table.add_row("Terje", TERJE)
    table.add_row("Woody", "Woody Allen")
    table.add_row("Zug", "City in Switzerland (crypto hub)")
    console.print('\n', Align.center(table))
    console.line()
    console.print(Align.center(f"[link=https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/]Oversight Committee Releases Additional Epstein Estate Documents[/link]"))
    console.print(Align.center(f"[link={COURIER_NEWSROOM_ARCHIVE}]Courier Newsroom's Searchable Archive[/link]"))
    console.print(Align.center("[link=https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_]Google Drive Raw Documents[/link]"))
    console.line(2)
    console.print(Align.center("Conversations are sorted chronologically based on timestamp of first message."), style='bold dark_green')
    console.print(Align.center(f"If you think there's an attribution error or can deanonymize an {UNKNOWN} contact @cryptadamist."), style='dim')
    console.line(2)


def print_top_lines(file_text, n = 10, max_chars = MAX_PREVIEW_CHARS, in_panel = False):
    "Print first n lines of a file."
    file_text = LEADING_WHITESPACE_REGEX.sub('', file_text)
    top_text = escape('\n'.join(file_text.split("\n")[0:n])[0:max_chars])
    output = Panel(top_text, expand=False) if in_panel else top_text + '\n'
    console.print(output, style='dim')



if deep_debug:
    console.print('KNOWN_COUNTERPARTY_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_COUNTERPARTY_FILE_IDS))
    console.print('\n\n\nGUESSED_COUNTERPARTY_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_COUNTERPARTY_FILE_IDS))
    console.line(2)
