import csv
import re
import urllib.parse
from copy import deepcopy
from io import StringIO

from dateutil.parser import parse

# Misc
HOUSE_OVERSIGHT_PREFIX = 'HOUSE_OVERSIGHT_'
FALLBACK_TIMESTAMP = parse("1/1/2001 12:01:01 AM")
SENT_FROM_REGEX = re.compile(r'^(?:(Please forgive|Sorry for all the) typos.{1,4})?(Sent (from|via).*(and string|AT&T|Droid|iPad|Phone|Mail|BlackBerry(.*(smartphone|device|Handheld|AT&T|T- ?Mobile))?)\.?)', re.M | re.I)
# Email replies
REPLY_LINE_IN_A_MSG_PATTERN = r"In a message dated \d+/\d+/\d+.*writes:"
REPLY_LINE_ENDING_PATTERN = r"[_ \n](AM|PM|[<_]|wrote:?)"
REPLY_LINE_ON_NUMERIC_DATE_PATTERN = fr"On \d+/\d+/\d+[, ].*{REPLY_LINE_ENDING_PATTERN}"
REPLY_LINE_ON_DATE_PATTERN = fr"On (\d+ )?((Mon|Tues?|Wed(nes)?|Thu(rs)?|Fri|Sat(ur)?|Sun)(day)?|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*).*{REPLY_LINE_ENDING_PATTERN}"
FORWARDED_LINE_PATTERN = r"-+ ?(Forwarded|Original)\s*Message ?-*|Begin forwarded message:?"
REPLY_LINE_PATTERN = rf"({REPLY_LINE_IN_A_MSG_PATTERN}|{REPLY_LINE_ON_NUMERIC_DATE_PATTERN}|{REPLY_LINE_ON_DATE_PATTERN}|{FORWARDED_LINE_PATTERN})"
REPLY_REGEX = re.compile(REPLY_LINE_PATTERN, re.IGNORECASE)

# Texting Names
ANIL_AMBANI = "Anil Ambani"
DEFAULT = 'default'
EVA = 'Eva'
JEFFREY_EPSTEIN = 'Jeffrey Epstein'
JOI_ITO = 'Joi Ito'
LARRY_SUMMERS = 'Larry Summers'
MELANIE_WALKER = 'Melanie Walker'
MIROSLAV_LAJCAK = 'Miroslav Lajčák'
STACEY_PLASKETT = 'Stacey Plaskett'
SCARAMUCCI = "Anthony Scaramucci"
SOON_YI = 'Soon-Yi Previn'
STEVE_BANNON = 'Steve Bannon'
STEVEN_SINOFSKY = 'Steven Sinofsky'
TERJE_ROD_LARSEN = 'Terje Rød-Larsen'
UNKNOWN = '(unknown)'

# Email Names
# TODO: no trailing periods!
AL_SECKEL = 'Al Seckel'
ALAN_DERSHOWITZ = 'Alan Dershowitz'
ALIREZA_ITTIHADIEH = 'Alireza Ittihadieh'
AMANDA_ENS = 'Amanda Ens'
ANN_MARIE_VILLAFANA = 'Ann Marie Villafana'
ANTHONY_BARRETT = 'Anthony Barrett'
ARIANE_DE_ROTHSCHILD = 'Ariane de Rothschild'
ANAS_ALRASHEED = 'Anas Alrasheed'
BRAD_KARP = 'Brad Karp'
AZIZA_ALAHMADI = 'Aziza Alahmadi'
BARBRO_EHNBOM = 'Barbro Ehnbom'
BENNET_MOSKOWITZ = 'Bennet Moskowitz'
BILL_GATES = 'Bill Gates'
BILL_SIEGEL = 'Bill Siegel'
BRAD_WECHSLER = 'Brad Wechsler'
BORIS_NIKOLIC = 'Boris Nikolic'
CELINA_DUBIN = 'Celina Dubin'
CHRISTINA_GALBRAITH = 'Christina Galbraith'  # Works with Tyler Shears on reputation stuff
DANIEL_SABBA = 'Daniel Sabba'
DANIEL_SIAD = 'Daniel Siad'
DARREN_INDYKE = 'Darren Indyke'
DAVID_SCHOEN = 'David Schoen'
DAVID_HAIG = 'David Haig'
DAVID_INGRAM = 'David Ingram'
DAVID_STERN = 'David Stern'
DEBBIE_FEIN = 'Debbie Fein'
DEEPAK_CHOPRA = 'Deepak Chopra'
DIANE_ZIMAN = 'Diane Ziman'
DONALD_TRUMP = 'Donald Trump'
EDUARDO_ROBLES = 'Eduardo Robles'
EDWARD_EPSTEIN = 'Edward Epstein'
EHUD_BARAK = 'Ehud Barak'
ELON_MUSK = 'Elon Musk'
FAITH_KATES = 'Faith Kates'
FRED_HADDAD = 'Fred Haddad'
GERALD_BARTON = 'Gerald Barton'
GHISLAINE_MAXWELL = 'Ghislaine Maxwell'
GLENN_DUBIN = 'Glenn Dubin'
GWENDOLYN_BECK = 'Gwendolyn Beck'         # https://www.lbc.co.uk/article/who-gwendolyn-beck-epstein-andrew-5HjdN66_2/
IVANKA = 'Ivanka'
JABOR_Y = 'Jabor Y'                       # Qatari
JACK_GOLDBERGER = 'Jack Goldberger'
JACKIE_PERCZEK = 'Jackie Perczek'
JARED_KUSHNER = 'Jared Kushner'
JAY_LEFKOWITZ = 'Jay Lefkowitz'
JEAN_HUGUEN = 'Jean Huguen'
JEAN_LUC_BRUNEL = 'Jean Luc Brunel'
JEREMY_RUBIN = 'Jeremy Rubin'             # Bitcoin dev
JES_STALEY = 'Jes Staley'
JESSICA_CADWELL = 'Jessica Cadwell'       # Paralegal?
JIDE_ZEITLIN = 'Jide Zeitlin'
JOHN_PAGE = 'John Page'
JOHNNY_EL_HACHEM = 'Johnny el Hachem'
JONATHAN_FARKAS = 'Jonathan Farkas'
JOSCHA_BACH = 'Joscha Bach'
KATHY_RUEMMLER = 'Kathy Ruemmler'
KATHERINE_KEATING = 'Katherine Keating'
KEN_STARR = 'Ken Starr'
KENNETH_E_MAPP = 'Kenneth E. Mapp'
LANDON_THOMAS = 'Landon Thomas Jr'
LAWRANCE_VISOSKI = 'Lawrance Visoski'
LAWRENCE_KRAUSS = 'Lawrence Krauss'
LEON_BLACK = 'Leon Black'
LESLEY_GROFF = 'Lesley Groff'
LILLY_SANCHEZ = 'Lilly Sanchez'
LINDA_STONE = 'Linda Stone'
LISA_NEW = 'Lisa New'                      # Harvard poetry prof AKA "Elisa New"
MARC_LEON = 'Marc Leon'
MARIANA_IDZKOWSKA = 'Mariana Idźkowska'
MARK_EPSTEIN = 'Mark L. Epstein'
MARTIN_NOWAK = 'Martin Nowak'
MARTIN_WEINBERG = "Martin Weinberg"
MASHA_DROKOVA = 'Masha Drokova'
MELANIE_SPINELLA = 'Melanie Spinella'
MICHAEL_BUCHHOLTZ = 'Michael Buchholtz'
MICHAEL_SITRICK = 'Michael Sitrick'
MICHAEL_WOLFF = "Michael Wolff"
MOHAMED_WAHEED_HASSAN = 'Mohamed Waheed Hassan'
NADIA_MARCINKO = 'Nadia Marcinko'
NICHOLAS_RIBIS = 'Nicholas Ribis'
NORMAN_D_RAU = 'Norman D. Rau'
OLIVIER_COLOM = 'Olivier Colom'
PAULA = 'Paula'
PAUL_BARRETT = 'Paul Barrett'
PAUL_KRASSNER = 'Paul Krassner'
PAUL_MORRIS = 'Paul Morris'
PAUL_PROSPERI = 'Paul Prosperi'
PEGGY_SIEGAL = 'Peggy Siegal'
PETER_MANDELSON = 'Peter Mandelson'
PRINCE_ANDREW = 'Prince Andrew'
PUREVSUREN_LUNDEG = 'Purevsuren Lundeg'
RAAFAT_ALSABBAGH = 'Raafat Alsabbagh'
REID_HOFFMAN = 'Reid Hoffman'
REID_WEINGARTEN = 'Reid Weingarten'
RICHARD_KAHN = 'Richard Kahn'
ROBERT_D_CRITTON = 'Robert D. Critton Jr.'
ROBERT_LAWRENCE_KUHN = 'Robert Lawrence Kuhn'
ROBERT_TRIVERS = 'Robert Trivers'
ROGER_SCHANK = 'Roger Schank'
RUDY_GIULIANI = 'Rudy Giuliani'
SCOTT_J_LINK = 'Scott J. Link'
SEAN_BANNON = 'Sean Bannon'
SHAHER_ABDULHAK_BESHER = 'Shaher Abdulhak Besher (?)'
STEPHEN_HANSON = 'Stephen Hanson'
STEVEN_PFEIFFER = 'Steven Pfeiffer'
STEVEN_HOFFENBERG = 'Steven Hoffenberg'
SULTAN_BIN_SULAYEM = 'Sultan Ahmed Bin Sulayem'
TERRY_KAFKA = 'Terry Kafka'
THANU_BOONYAWATANA = 'Thanu Boonyawatana'
THORBJORN_JAGLAND = 'Thorbjørn Jagland'
TOM_BARRACK = 'Tom Barrack'
TOM_PRITZKER = 'Tom Pritzker'
TONJA_HADDAD_COLEMAN = 'Tonja Haddad Coleman'
TULSI_GABBARD = 'Tulsi Gabbard'
TYLER_SHEARS = 'Tyler Shears'  # Reputation manager, like Al Seckel
VINIT_SAHNI = 'Vinit Sahni'

# Other strings
EMAIL_HEADER_FIELD = 'header_field'
EMAIL = 'email'
TEXT_MESSAGE = 'text message'
REDACTED = '<REDACTED>'

#  of who is the counterparty in each text message file
AI_COUNTERPARTY_DETERMINATION_TSV = StringIO("""filename	counterparty	source
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
HOUSE_OVERSIGHT_027515.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027536.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027655.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027707.txt	Steve Bannon	Italian politics; Trump discussions
HOUSE_OVERSIGHT_027722.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027735.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027794.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_029744.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031045.txt	Steve Bannon (likely)	Trump and New York Times coverage""")

KNOWN_IMESSAGE_FILE_IDS = {
    '031042': ANIL_AMBANI,       # Participants: field
    '027225': ANIL_AMBANI,       # Birthday
    '031173': 'Ards',            # Participants: field, possibly incomplete
    '027401': EVA,               # Participants: field
    '027650': JOI_ITO,           # Participants: field
    '027777': LARRY_SUMMERS,     # Participants: field
    '027515': MIROSLAV_LAJCAK,   # https://x.com/ImDrinknWyn/status/1990210266114789713
    '027165': MELANIE_WALKER,    # https://www.wired.com/story/jeffrey-epstein-claimed-intimate-knowledge-of-donald-trumps-views-in-texts-with-bill-gates-adviser/
    '027248': MELANIE_WALKER,    # Says "we met through trump" which is confirmed by Melanie in 032803
    '025429': STACEY_PLASKETT,
    '027333': SCARAMUCCI,        # unredacted phone number in one of the messages
    '027128': SOON_YI,           # https://x.com/ImDrinknWyn/status/1990227281101434923
    '027217': SOON_YI,           # refs marriage to woody allen
    '027244': SOON_YI,           # refs Woody
    '027257': SOON_YI,           # 'Woody Allen' in Participants: field
    '027460': STEVE_BANNON,      # Discusses leaving scotland when Bannon was confirmed in Scotland, also NYT
    '025707': STEVE_BANNON,
    '025734': STEVE_BANNON,
    '025452': STEVE_BANNON,
    '025408': STEVE_BANNON,
    '027307': STEVE_BANNON,
    '027278': TERJE_ROD_LARSEN,
    '027255': TERJE_ROD_LARSEN,
}

GUESSED_IMESSAGE_FILE_IDS = {
    '027221': ANIL_AMBANI,
    '025363': STEVE_BANNON,          # Trump and New York Times coverage
    '025368': STEVE_BANNON,          # Trump and New York Times coverage
    '027585': STEVE_BANNON,          # Tokyo trip
    '027568': STEVE_BANNON,
    '027695': STEVE_BANNON,
    '027594': STEVE_BANNON,
    '027720': STEVE_BANNON,          # first 3 lines of 027722
    '027549': STEVE_BANNON,
    '027434': STEVE_BANNON,          # References Maher appearance
    '027764': STEVE_BANNON,
    '027428': STEVE_BANNON,          # References HBJ meeting on 9/28 from other Bannon/Epstein convo
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

for row in csv.DictReader(AI_COUNTERPARTY_DETERMINATION_TSV, delimiter='\t'):
    file_id = row['filename'].strip().replace(HOUSE_OVERSIGHT_PREFIX, '').replace('.txt', '')
    counterparty = row['counterparty'].strip()

    if file_id in GUESSED_IMESSAGE_FILE_IDS:
        raise RuntimeError(f"Can't overwrite attribution of {file_id} to {GUESSED_IMESSAGE_FILE_IDS[file_id]} with {counterparty}")

    GUESSED_IMESSAGE_FILE_IDS[file_id] = counterparty.replace(' (likely)', '').strip()


# Emailers
EMAILER_ID_REGEXES: dict[str, re.Pattern] = {
    ALAN_DERSHOWITZ: re.compile(r'(alan.{1,7})?dershowi(lz?|tz)', re.IGNORECASE),
    ALIREZA_ITTIHADIEH: re.compile(r'Alireza.[Il]ttihadieh', re.IGNORECASE),
    AMANDA_ENS: re.compile(r'ens, amanda?|Amanda Ens', re.IGNORECASE),
    ANIL_AMBANI: re.compile(r'Anil.Ambani', re.IGNORECASE),
    ANN_MARIE_VILLAFANA: re.compile(r'Villafana, Ann Marie|(A(\.|nn) Marie )?Villafana', re.IGNORECASE),
    ARIANE_DE_ROTHSCHILD: re.compile(r'AdeR|((Ariane|Edmond) de )?Rothschild|Ariane', re.IGNORECASE),
    ANAS_ALRASHEED: re.compile(r'anas\s*al\s*rashee[cd]', re.IGNORECASE),
    BARBRO_EHNBOM: re.compile(r'behnbom@aol.com|(Barbro\s.*)?Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen?', re.IGNORECASE),
    BENNET_MOSKOWITZ: re.compile(r'Moskowitz.*Bennet|Bennet.*Moskowitz', re.IGNORECASE),
    BORIS_NIKOLIC: re.compile(r'(boris )?nikolic?', re.IGNORECASE),
    BRAD_KARP: re.compile(r'Brad (S.? )?Karp|Karp, Brad', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterpris', re.IGNORECASE),
    'Danny Frost': re.compile(r'Frost, Danny|frostd@dany.nyc.gov', re.IGNORECASE),
    DARREN_INDYKE: re.compile(r'darren$|darren [il]n[dq]_?yke?|dkiesq', re.IGNORECASE),
    DAVID_STERN: re.compile(r'David Stern?', re.IGNORECASE),
    EDUARDO_ROBLES: re.compile(r'Ed(uardo)?\s*Robles', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    FAITH_KATES: re.compile(r'faith kates?', re.IGNORECASE),
    GERALD_BARTON: re.compile(r'Gerald.*Barton', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?|Ghislaine|Maxwell', re.IGNORECASE),
    'Google Alerts': re.compile(r'google\s?alerts', re.IGNORECASE),
    'Heather Mann': re.compile(r'Heather Man', re.IGNORECASE),
    'Intelligence Squared': re.compile(r'intelligence\s*squared', re.IGNORECASE),
    JACKIE_PERCZEK:  re.compile(r'jackie percze[kl]?', re.IGNORECASE),
    JABOR_Y: re.compile(r'[ji]abor\s*y?', re.IGNORECASE),
    JEAN_LUC_BRUNEL: re.compile(r'Jean[- ]Luc Brunel?', re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'[djl]ee[vy]acation[©@]?g?(mail.com)?|JEE?\b|Jeffrey E((sp|ps)tein?)?|jeeproject@yahoo.com|J Jep|Jeffery Edwards|(?<!Mark L. )Epstein', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|(joichi|joi)( Ito)?', re.IGNORECASE),
    JOHNNY_EL_HACHEM: re.compile(r'el hachem johnny|johnny el hachem', re.IGNORECASE),
    JONATHAN_FARKAS: re.compile(r'Jonathan Farka(s|il)', re.IGNORECASE),
    KATHY_RUEMMLER: re.compile(r'Kathy Ruemmler?', re.IGNORECASE),
    KEN_STARR: re.compile(r'starr, ken|Ken(neth W.)?\s+starr?|starr', re.IGNORECASE),
    LANDON_THOMAS: re.compile(r'lando[nr] thomas( jr)?|thomas jr.?, lando[nr]', re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r'(La(wrence|rry).{1,5})?Summers?|^LH$|LHS|Ihsofficel', re.IGNORECASE),
    LAWRANCE_VISOSKI: re.compile(r'La(rry|wrance) Visoski?', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus|lawkrauss', re.IGNORECASE),
    LEON_BLACK: re.compile(r'Leon Black?', re.IGNORECASE),
    MARIANA_IDZKOWSKA: re.compile(r'Mariana ldikowsk', re.IGNORECASE),  # Raw image
    MARK_EPSTEIN: re.compile(r'Mark (L\. )?Epstein', re.IGNORECASE),
    LILLY_SANCHEZ: re.compile(r'Lilly.*Sanchez', re.IGNORECASE),
    LISA_NEW: re.compile(r'E?Lisa New?\b', re.IGNORECASE),
    MARC_LEON: re.compile(r'Marc[.\s]+(Kensington|Leon)|Kensington2', re.IGNORECASE),
    MARTIN_NOWAK: re.compile(r'Martin.*?Nowak|Nowak, Martin', re.IGNORECASE),
    MARTIN_WEINBERG: re.compile(r'martin.*?weinberg', re.IGNORECASE),
    "Matthew Schafer": re.compile(r"matthew\.?schafer?", re.IGNORECASE),
    MELANIE_SPINELLA: re.compile(r'M?elanie Spine[Il]{2}a', re.IGNORECASE),
    'Michael Miller': re.compile(r'Micha(el)? Miller|Miller, Micha(el)?', re.IGNORECASE),
    MICHAEL_BUCHHOLTZ: re.compile(r'Michael.*Buchholtz', re.IGNORECASE),
    MICHAEL_WOLFF: re.compile(r'Michael\s*Wol(ff|i)|Wolff', re.IGNORECASE),
    MICHAEL_SITRICK: re.compile(r'(Mi(chael|ke).{0,5})?[CS]itrick', re.IGNORECASE),
    MIROSLAV_LAJCAK: re.compile(r"Miro(slav)?(\s+Laj[cč][aá]k)?"),
    MOHAMED_WAHEED_HASSAN: re.compile(r'Mohamed Waheed(\s+Hassan)?', re.IGNORECASE),
    NADIA_MARCINKO: re.compile(r"Na[dď]i?a\s+Marcinko(v[aá])?", re.IGNORECASE),
    'Neal Kassell': re.compile(r'Neal Kassel', re.IGNORECASE),
    NICHOLAS_RIBIS: re.compile(r'Nicholas[ ._]Ribi?s?', re.IGNORECASE),
    OLIVIER_COLOM: re.compile(fr'Colom, Olivier|{OLIVIER_COLOM}', re.IGNORECASE),
    PAUL_BARRETT: re.compile(r'Paul Barre(d|tt)', re.IGNORECASE),
    PAUL_KRASSNER: re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    PAULA: re.compile(r'^Paula$', re.IGNORECASE),
    PAUL_MORRIS: re.compile(r'morris, paul|Paul Morris', re.IGNORECASE),
    PEGGY_SIEGAL:  re.compile(r'Peggy Siegal?', re.IGNORECASE),
    'Peter Attia': re.compile(r'Peter Attia?', re.IGNORECASE),
    PETER_MANDELSON: re.compile(r"((Lord|Peter) )?Mandelson", re.IGNORECASE),
    'pink@mc2mm.com': re.compile(r"^Pink$|pink@mc2mm\.com", re.IGNORECASE),
    PRINCE_ANDREW: re.compile(r'Prince Andrew|The Duke', re.IGNORECASE),
    REID_WEINGARTEN: re.compile(r'Weingarten, Rei[cdi]|Rei[cdi] Weingarten', re.IGNORECASE),
    RICHARD_KAHN: re.compile(r'rich(ard)? kahn?', re.IGNORECASE),
    ROBERT_D_CRITTON: re.compile(r'Robert D.? Critton Jr.?', re.IGNORECASE),
    ROBERT_LAWRENCE_KUHN: re.compile(r'Robert\s*(Lawrence)?\s*Kuhn', re.IGNORECASE),
    ROBERT_TRIVERS: re.compile(r'tri[vy]ersr@gmail|Robert\s*Trivers?', re.IGNORECASE),
    SCARAMUCCI: re.compile(r"mooch|(Anthony ('The Mooch' )?)?Scaramucci", re.IGNORECASE),
    SCOTT_J_LINK: re.compile(r'scott j. link?', re.IGNORECASE),
    SEAN_BANNON: re.compile(r'sean bannon?', re.IGNORECASE),
    SHAHER_ABDULHAK_BESHER: re.compile(r'\bShaher( Abdulhak Besher)?\b', re.IGNORECASE),
    SOON_YI: re.compile(r'Soon[- ]Yi Previn?', re.IGNORECASE),
    STEPHEN_HANSON: re.compile(r'ste(phen|ve) hanson?|Shanson900', re.IGNORECASE),
    STEVE_BANNON: re.compile(r'steve banno[nr]?', re.IGNORECASE),
    STEVEN_SINOFSKY: re.compile(r'Steven Sinofsky?', re.IGNORECASE),
    SULTAN_BIN_SULAYEM: re.compile(r'Sultan (Ahmed )?bin Sulaye?m?', re.IGNORECASE),
    TERJE_ROD_LARSEN: re.compile(r"Terje(( (R[øo]e?d[- ])?)?Lars[eo]n)?", re.IGNORECASE),
    TERRY_KAFKA: re.compile(r'Terry Kafka?', re.IGNORECASE),
    THANU_BOONYAWATANA: re.compile(r"Thanu (BOONYAWATANA|Cnx)", re.IGNORECASE),
    THORBJORN_JAGLAND: re.compile(r'(Thor.{3,8})?Jag[il]and?', re.IGNORECASE),
    TONJA_HADDAD_COLEMAN: re.compile(fr"To(nj|rl)a Haddad Coleman|haddadfm@aol.com", re.IGNORECASE)
}

# If found as substring consider them the author
EMAILERS = [
    'Anne Boyles',
    AL_SECKEL,
    AZIZA_ALAHMADI,
    BILL_GATES,
    BILL_SIEGEL,
    BRAD_WECHSLER,
    DANIEL_SABBA,
    'Danny Goldberg',
    DAVID_SCHOEN,
    DEEPAK_CHOPRA,
    GLENN_DUBIN,
    'Gordon Getty',
    'Jack Lang',
    JAY_LEFKOWITZ,
    JES_STALEY,
    JESSICA_CADWELL,
    JOHN_PAGE,
    'Jokeland',
    JOSCHA_BACH,
    'Kathleen Ruderman',
    KENNETH_E_MAPP,
    'Larry Cohen',
    LESLEY_GROFF,
    'lorraine@mc2mm.com',
    LINDA_STONE,
    'Lyn Fontanilla',
    'Mark Tramo',
    MELANIE_WALKER,
    'Merwin Dela Cruz',
    'Michael Simmons',   # Not the only "To:"
    'middle.east.update@hotmail.com',
    'Multiple Senders',  # Weird files like HOUSE_OVERSIGHT_032210
    'Nancy Cain',
    'Nancy Dahl',
    'Nancy Portland',
    'Oliver Goodenough',
    'Peter Aldhous',
    'Peter Green',
    ROGER_SCHANK,
    'ross@acuityreputation.com',
    r'Sam/Walli Leff',
    STEVEN_PFEIFFER,
    'Steven Victor MD',
    'Susan Edelman',
    TOM_BARRACK,
    'Vincenzo Lozzo',
    'Vladimir Yudashkin',
]

EMAILER_REGEXES = deepcopy(EMAILER_ID_REGEXES)

for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer, re.IGNORECASE)


KNOWN_EMAIL_AUTHORS = {
    '032436': ALIREZA_ITTIHADIEH,    # Signature
    '032543': ANAS_ALRASHEED,        # Later reply 033000 has quote
    '026064': ARIANE_DE_ROTHSCHILD,
    '026069': ARIANE_DE_ROTHSCHILD,
    '030741': ARIANE_DE_ROTHSCHILD,
    '026018': ARIANE_DE_ROTHSCHILD,
    '033316': AZIZA_ALAHMADI,        # "Regards, Aziza" at bottom
    '026659': BARBRO_EHNBOM,         # Reply
    '026745': BARBRO_EHNBOM,         # Signature
    '031227': BENNET_MOSKOWITZ,
    '031442': CHRISTINA_GALBRAITH,
    '019446': CHRISTINA_GALBRAITH,  # Not 100% but from "Christina media/PR" which fits
    '026625': DARREN_INDYKE,
    '026290': DAVID_SCHOEN,         # Signature
    '031339': DAVID_SCHOEN,         # Signature
    '031492': DAVID_SCHOEN,         # Signature
    '031560': DAVID_SCHOEN,         # Signature
    '026287': DAVID_SCHOEN,         # Signature
    '033419': DAVID_SCHOEN,         # Sent by AOL
    '031460': EDWARD_EPSTEIN,
    '030578': FAITH_KATES,          # Same as unredacted 030414, same legal signature
    '026547': GERALD_BARTON,
    '029969': GWENDOLYN_BECK,       # Signature
    '031120': GWENDOLYN_BECK,       # Signature
    '029968': GWENDOLYN_BECK,       # Signature
    '029970': GWENDOLYN_BECK,
    '029960': GWENDOLYN_BECK,       # Reply
    '029959': GWENDOLYN_BECK,       # "Longevity & Aging"
    '033360': 'Henry Holt',         # in signature
    '033384': JACK_GOLDBERGER,    # Might be Paul Prosperi?
    '026024': JEAN_HUGUEN,
    '026024': JEAN_HUGUEN,          # Signature
    '021823': JEAN_LUC_BRUNEL,      # Reply
    '031826': JEFFREY_EPSTEIN,
    '030997': JEFFREY_EPSTEIN,
    '029779': JEFFREY_EPSTEIN,
    '022949': JEFFREY_EPSTEIN,
    '028770': JEFFREY_EPSTEIN,
    '029692': JEFFREY_EPSTEIN,
    '031624': JEFFREY_EPSTEIN,
    '030768': JEFFREY_EPSTEIN,
    '031996': JEFFREY_EPSTEIN,       # bounced
    '022938': JEFFREY_EPSTEIN,
    '028675': JEFFREY_EPSTEIN,       # Just bad OCR
    '025041': JEFFREY_EPSTEIN,       # Just bad OCR
    '032214': JEFFREY_EPSTEIN,       # Just bad OCR
    '031791': JESSICA_CADWELL,       # paralegal, see https://x.com/ImDrinknWyn/status/1993765348898927022
    '028849': JOI_ITO,               # Conversation with Joi Ito
    '028851': JOI_ITO,
    '016692': JOHN_PAGE,
    '016693': JOHN_PAGE,
    '028507': JONATHAN_FARKAS,
    '031732': JONATHAN_FARKAS,
    '033484': JONATHAN_FARKAS,
    '033282': JONATHAN_FARKAS,
    '033582': JONATHAN_FARKAS,        # Reply
    '032389': JONATHAN_FARKAS,        # Reply
    '033581': JONATHAN_FARKAS,        # Reply
    '033203': JONATHAN_FARKAS,        # Reply
    '032052': JONATHAN_FARKAS,        # Reply
    '033490': JONATHAN_FARKAS,        # Signature
    '032531': JONATHAN_FARKAS,        # Signature
    '026764': 'Barry J. Cohen',
    '026652': KATHY_RUEMMLER,          # Just bad OCR
    '032224': KATHY_RUEMMLER,
    '032386': KATHY_RUEMMLER,          # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '032727': KATHY_RUEMMLER,          # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '030478': LANDON_THOMAS,
    '029013': LARRY_SUMMERS,
    '031129': LARRY_SUMMERS,
    '032206': LAWRENCE_KRAUSS,         # More of a text convo?
    '032209': LAWRENCE_KRAUSS,         # More of a text convo?
    # '032210': LAWRENCE_KRAUSS,         # More of a text convo?
    '029196': LAWRENCE_KRAUSS,
    '033487': LAWRANCE_VISOSKI,
    '028789': LAWRANCE_VISOSKI,
    '027046': LAWRANCE_VISOSKI,
    '033370': LAWRANCE_VISOSKI,        # Planes discussion signed larry
    '029977': LAWRANCE_VISOSKI,        # Planes discussion signed larry
    '033495': LAWRANCE_VISOSKI,        # Planes discussion signed larry
    '033154': LAWRANCE_VISOSKI,
    '033488': LAWRANCE_VISOSKI,
    '033593': LAWRANCE_VISOSKI,        # Signature
    '033309': LINDA_STONE,             # "Co-authored with iPhone autocorrect"
    '017581': 'Lisa Randall',
    '026609': 'Mark Green',            # Actually a fwd
    '030472': MARTIN_WEINBERG,         # Maybe. in reply
    '030235': MELANIE_WALKER,          # In fwd
    '032343': MELANIE_WALKER,          # In later reply 032346
    '032212': MIROSLAV_LAJCAK,
    '022193': NADIA_MARCINKO,
    '021814': NADIA_MARCINKO,
    '021808': NADIA_MARCINKO,
    '022214': NADIA_MARCINKO,          # Reply header
    '022190': NADIA_MARCINKO,
    '021818': NADIA_MARCINKO,
    '022197': NADIA_MARCINKO,
    '021811': NADIA_MARCINKO,          # Signature and email address in the message
    '026612': NORMAN_D_RAU,            # Fwded from "to" address
    '028487': NORMAN_D_RAU,            # Fwded from "to" address
    '024923': PAUL_KRASSNER,
    '032457': PAUL_KRASSNER,
    '029981': PAULA,                   # reply
    '030482': PAULA,                   # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '033157': PAUL_PROSPERI,           # Fwded from "to" address
    '033383': PAUL_PROSPERI,           # Reply
    '033561': PAUL_PROSPERI,           # Fwded mail sent to Prosperi. Might be Subotnick Stuart ?
    '031694': PEGGY_SIEGAL,
    '032219': PEGGY_SIEGAL,            # Signed "Peggy"
    '029020': 'Renata Bolotova',       # Signature
    '033169': ROBERT_TRIVERS,          # Refs paper
    '033584': ROBERT_TRIVERS,          # Refs paper
    '026320': SEAN_BANNON,             # From protonmail, Bannon wrote 'just sent from my protonmail' in 027067
    '029003': SOON_YI,
    '029005': SOON_YI,
    '029007': SOON_YI,
    '029010': SOON_YI,
    '032296': SOON_YI,                 # "Sent from soon-yi's phone"
    '026620': TERRY_KAFKA,             # "Respectfully, terry"
    '028482': TERRY_KAFKA,             # Signature
    '029992': TERRY_KAFKA,             # Quoted reply
    '020666': TERRY_KAFKA,             # ends with 'Terry'
    '022346': VINIT_SAHNI,             # Signature  #TODO: check this, also maybe 022346 and 022322
    # '026571': '(unknown french speaker)',
    # '029504': Probably Audrey Raimbault (based on "GMI" in signature, a company registered by "aubrey raimbault")
}

IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS = ['Allen West', 'Rafael Bardaji', 'Philip Kafka', 'Herb Goodman', 'Grant Seeger', 'Lisa Albert', 'Janet Kafka', 'James Ramsey', 'ACT for America', 'John Zouzelka', 'Joel Dunn', 'Nate McClain', 'Bennet Greenwald', 'Taal Safdie', 'Uri Fouzailov', 'Neil Anderson', 'Nate White', 'Rita Hortenstine', 'Henry Hortenstine', 'Gary Gross', 'Forrest Miller', 'Bennett Schmidt', 'Val Sherman', 'Marcie Brown', 'Michael Horowitz', 'Marshall Funk']
PAUL_KRASSNER_MANSON_RECIPIENTS = ['Nancy Cain', 'Holly Krassner Dawson', 'Marie Moneysmith', 'Linda W. Grossman', 'Daniel Dawson', 'Danny Goldberg', 'Caryl Ratner', 'Michael Simmons', 'Barb Cowles', 'Lee Quarnstorm', 'Lynnie Tofte Fass', 'Kevin Bright', 'Samuel Leff', 'Bob Fass']

KNOWN_EMAIL_RECIPIENTS = {
    '021106': 'Alexandra Preate',     # Reply
    '028968': [ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN],
    '029835': [ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN],
    '026620': [MARK_EPSTEIN, JEFFREY_EPSTEIN, MICHAEL_BUCHHOLTZ] + IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS,
    '027063': ANTHONY_BARRETT,
    '030764': ARIANE_DE_ROTHSCHILD,   # Reply
    '026431': ARIANE_DE_ROTHSCHILD,   # Reply
    '031996': CHRISTINA_GALBRAITH,    # bounced
    '026245': DIANE_ZIMAN,            # Quoted reply
    '026466': DIANE_ZIMAN,            # Quoted reply
    '031607': EDWARD_EPSTEIN,
    '030525': FAITH_KATES,            # Same as unredacted 030414, same legal signature
    '026426': JEAN_HUGUEN,            # Reply
    '029975': JEAN_LUC_BRUNEL,        # Same as another file
    '022202': JEAN_LUC_BRUNEL,        # Follow up
    '032224': JEFFREY_EPSTEIN,        # Reply
    '033169': JEFFREY_EPSTEIN,
    '033584': JEFFREY_EPSTEIN,
    '033487': JEFFREY_EPSTEIN,
    '028851': JEFFREY_EPSTEIN,
    '022187': JEFFREY_EPSTEIN,        # Bad OCR
    '028849': JEFFREY_EPSTEIN,        # Conversation
    '026547': JEFFREY_EPSTEIN,        # Bad OCR
    '031489': JEFFREY_EPSTEIN,        # Bad OCR
    '032209': JEFFREY_EPSTEIN,        # More of a text convo?
    '032210': JEFFREY_EPSTEIN,        # More of a text convo?
    '033575': [JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN],
    '033228': [JEFFREY_EPSTEIN, DARREN_INDYKE, FRED_HADDAD],  # Bad OCR
    '023067': [JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN, TONJA_HADDAD_COLEMAN],      # Bad OCR
    '029498': [JEFFREY_EPSTEIN, DAVID_HAIG, 'Gordon Getty', 'Norman Finkelstein'],      # Bad OCR
    '029154': [JEFFREY_EPSTEIN, DAVID_HAIG],         # Bad OCR
    '029889': [JEFFREY_EPSTEIN, JACK_GOLDBERGER, ROBERT_D_CRITTON, 'Connie Zaguirre'],  # Bad OCR
    '028931': [JEFFREY_EPSTEIN, LAWRENCE_KRAUSS],    # Bad OCR
    '019407': [JEFFREY_EPSTEIN, MICHAEL_SITRICK],    # Bad OCR
    '019409': [JEFFREY_EPSTEIN, MICHAEL_SITRICK],    # Bad OCR
    '031980': [JEFFREY_EPSTEIN, MICHAEL_SITRICK],    # Bad OCR
    '029163': [JEFFREY_EPSTEIN, ROBERT_TRIVERS],     # Bad OCR
    '026228': [JEFFREY_EPSTEIN, STEVEN_PFEIFFER],    # Bad OCR
    '021794': [JESSICA_CADWELL, ROBERT_D_CRITTON],   # Bad OCR
    '033456': 'Joel',                 # Reply
    '033460': 'Joel',                 # Reply
    '029282': [JOI_ITO, REID_HOFFMAN],# Bad OCR
    '021090': JONATHAN_FARKAS,        # Reply to a message signed " jonathan" same as other Farkas emails
    '033073': KATHY_RUEMMLER,         # to "Kathy" about dems, sent from iPad (not 100% confirmed)
    '032939': KATHY_RUEMMLER,         # to "Kathy" about dems, sent from iPad (not 100% confirmed)
    '031388': [KEN_STARR, LILLY_SANCHEZ, MARTIN_WEINBERG, REID_WEINGARTEN],  # Bad OCR
    '030522': LANDON_THOMAS,
    '031413': LANDON_THOMAS,          # Reply
    '029692': LARRY_SUMMERS,          # Header
    '029779': LARRY_SUMMERS,          # Header
    '028675': LARRY_SUMMERS,          # Just bad OCR
    '025041': LARRY_SUMMERS,          # Just bad OCR
    '033591': LAWRANCE_VISOSKI,       # Reply signature
    '033466': LAWRANCE_VISOSKI,       # Reply signature
    '028787': LAWRANCE_VISOSKI,
    '027097': LAWRANCE_VISOSKI,       # Signature of reply
    '022250': LESLEY_GROFF,           # Reply
    '030368': MELANIE_SPINELLA,       # Actually a self fwd from jeffrey to jeffrey
    '030369': MELANIE_SPINELLA,       # Actually a self fwd from jeffrey to jeffrey
    '030371': MELANIE_SPINELLA,       # Actually a self fwd from jeffrey to jeffrey
    '023291': [MELANIE_SPINELLA, BRAD_WECHSLER],  # Can be seen in 023028
    '032214': MIROSLAV_LAJCAK,               # Quoted reply has signature
    '022258': NADIA_MARCINKO,         # Reply header
    '033097': [PAUL_BARRETT, RICHARD_KAHN],  # Bad OCR #TODO: check
    '030506': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030507': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030508': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030509': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030096': PETER_MANDELSON,
    '032951': RAAFAT_ALSABBAGH,
    '019334': STEVE_BANNON,
    # '032213': Probably MIRO or Reid Weingarten based on replies but he sent it to a lot of people
}

# frJaca &dazeEE e9), Yccia'
# Certified Paralegal
# Florida Registered Paralegal
# BURMAN CRITTON LUTTIER & COLEMAN, LLP
# 515 N. Flagler Drive
# Suite #400
# West Palm Beach, FL 33401

EMAIL_SIGNATURES = {
    #DARREN_INDYKE: re.compile(r"(DARREN K. INDYKE\n)?DARREN.*\n575 Lexington.*\nNew York.*(\nTelephone.*)?(\nTelecop.*)?(\nMobil.*)?(\nemail.*)?\**\nThe info.*\nprivileged.*\nDarren.*\nor any part.*\n(communication.*\n){2}Copyright.*(\nIndyke.*)?\n\**", re.IGNORECASE),
    DARREN_INDYKE: re.compile(r"DARREN K. INDYKE.*?\**\nThe information contained in this communication.*?Darren K.[\n\s]+?[Il]ndyke(, PLLC)? — All rights reserved\.? ?\n\*{50,120}(\n\**)?", re.DOTALL),
    DAVID_INGRAM: re.compile(r"Thank you in advance.*\nDavid Ingram.*\nCorrespondent\nReuters.*\nThomson.*(\n(Office|Mobile|Reuters.com).*)*"),
    DEEPAK_CHOPRA: re.compile(fr"({DEEPAK_CHOPRA}( MD)?\n)?2013 Costa Del Mar Road\nCarlsbad, CA 92009(\n(Chopra Foundation|Super Genes: Unlock.*))?(\nJiyo)?(\nChopra Center for Wellbeing)?(\nHome: Where Everyone is Welcome)?"),
    JEFFREY_EPSTEIN: re.compile(r"((\*+|please note)\n+)?(> )?(• )?(» )?The information contained in this communication is\n(> )*(» )?confidential.*?all attachments.( copyright -all rights reserved?)?", re.DOTALL),
    JESSICA_CADWELL: re.compile(r"(f.*\n)?Certified Para.*\nFlorida.*\nBURMAN.*\n515.*\nSuite.*\nWest Palm.*", re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r"Lawrence (M. )?Krauss\n(Director.*\n)?(Co-director.*\n)?Foundation.*\nSchool.*\n(Co-director.*\n)?(and Director.*\n)?Arizona.*(\nResearch.*\nOri.*\n(krauss.*\n)?origins.*)?", re.IGNORECASE),
    MARTIN_WEINBERG: re.compile(r"This Electronic Message contains.*?contents of this message is.*?prohibited.", re.DOTALL),
    (MARTIN_WEINBERG + ' address'):  re.compile(r"Martin G. Weinberg, Esq.\n20 Park Plaza, Suite 1000\nBoston, MA 02116(\n61.*)?(\n.*([cC]ell|Office))*"),
    PETER_MANDELSON: re.compile(r'Disclaimer This email and any attachments to it may be.*?with[ \n]+number(.*?EC4V[ \n]+6BJ)?', re.DOTALL | re.IGNORECASE),
    PAUL_BARRETT: re.compile(r"Paul Barrett[\n\s]+Alpha Group Capital LLC[\n\s]+(142 W 57th Street, 11th Floor, New York, NY 10019?[\n\s]+)?(al?[\n\s]*)?ALPHA GROUP[\n\s]+CAPITAL"),
    RICHARD_KAHN: re.compile(r'Richard Kahn[\n\s]+HBRK Associates Inc.?[\n\s]+((301 East 66th Street, Suite 1OF|575 Lexington Avenue,? 4th Floor,?)[\n\s]+)?New York, (NY|New York) 100(22|65)([\n\s]+(Tel|Phone)( I)?[\n\s]+Fa[x"]?[\n\s]+[Ce]el?l?)?', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r"((>|I) )?Terry B.? Kafka.*\n(> )?Impact Outdoor.*\n(> )?5454.*\n(> )?Dallas.*\n((> )?c?ell.*\n)?(> )?Impactoutdoor.*(\n(> )?cell.*)?", re.IGNORECASE),
    TONJA_HADDAD_COLEMAN: re.compile(fr"Tonja Haddad Coleman.*\nTonja Haddad.*\nAdvocate Building\n315 SE 7th.*(\nSuite.*)?\nFort Lauderdale.*(\n({REDACTED} )?facsimile)?(\nwww.tonjahaddad.com?)?(\nPlease add this efiling.*\nThe information.*\nyou are not.*\nyou are not.*)?", re.IGNORECASE),
    UNKNOWN: re.compile(r"(This message is directed to and is for the use of the above-noted addressee only.*\nhereon\.)", re.DOTALL),
}

HEADER_ABBREVIATIONS = {
    "AD": "Abu Dhabi",
    "Barak": "Ehud Barak (Former Israeli prime minister)",
    "Barrack": "Tom Barrack (Trump ally)",
    'BG': "Bill Gates",
    'Bill': "Bill Gates",
    "Brock": 'Brock Pierce (crypto bro with a very sordid past)',
    "DB": "Deutsche Bank (maybe??)",
    'HBJ': "Hamad bin Jassim (former Qatari prime minister)",
    'Jabor': '"an influential man in Qatar"',
    'Jared': "Jared Kushner",
    'Jagland': 'Thorbjørn Jagland (former Norwegian prime minister)',
    'Jeffrey Wernick': 'Right wing crypto bro',
    'Joi': 'Joi Ito (MIT Media Lab)',
    "Hoffenberg": "Steven Hoffenberg (Epstein's ponzi scheme partner)",
    'KSA': "Kingdom of Saudi Arabia",
    'Kurz': 'Sebastian Kurz (former Austrian Chancellor)',
    'Kwok': "Chinese criminal Miles Kwok AKA Miles Guo AKA Guo Wengui",
    'Mapp': f'{KENNETH_E_MAPP} (Governor Virgin Islands)',
    'Masa': 'Masayoshi Son (Softbank)',
    'MBS': "Mohammed bin Salman Al Saud (Saudi ruler)",
    'MBZ': "Mohamed bin Zayed Al Nahyan (Emirates sheikh)",
    "Miro": MIROSLAV_LAJCAK,
    "Mooch": "Anthony 'The Mooch' Scaramucci (Skybridge crypto bro)",
    "Terje": TERJE_ROD_LARSEN,
    "Woody": "Woody Allen",
    "Zug": "City in Switzerland (crypto hub)",
}

NAMES_TO_NOT_HIGHLIGHT: list[str] = [name.lower() for name in [
    'Al',
    'Allen',
    'Amanda',
    'Andres',
    'Andrew',
    'Black',
    'Brad',
    'Daniel',
    'Darren',
    'David',
    'Etienne',
    'Fred',
    'Jack',
    'Jay',
    'Jeff',
    'jeffrey',
    'Jeremy',
    'jessica',
    'John',
    'Jonathan',
    'Joseph',
    'Kahn',
    'Katherine',
    'Jr',
    'Leon',
    'Lesley',
    'Marc',
    'Martin',
    'Melanie',
    'Michael',
    'Mike',
    'Paul',
    'Pen',
    'Peter',
    'Reid',
    'Richard',
    'Robert',
    'Roger',
    'Rubin',
    'Scott',
    'Sean',
    'Stephen',
    'Steve',
    'Steven',
    'Stone',
    'Susan',
    'The',
    'Thomas',
    'Tom',
    'Victor',
    "Y",
    "Y.",
]]

# URLs
ATTRIBUTIONS_URL = 'https://github.com/michelcrypt4d4mus/epstein_text_messages/blob/master/util/constants.py'
COFFEEZILLA_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'
COURIER_NEWSROOM_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
EPSTEINIFY_URL = 'https://epsteinify.com'
EPSTEIN_WEB_DOC_URL = 'https://epsteinweb.org/wp-content/uploads/epstein_evidence/images'
JMAIL_URL = 'https://jmail.world'
OVERSIGHT_REPUBLICANS_PRESSER_URL = 'https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/'
RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL = 'https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_'
SUBSTACK_URL = 'https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great'

SITE_URLS = {
    EMAIL: 'https://michelcrypt4d4mus.github.io/epstein_emails_house_oversight/',
    TEXT_MESSAGE: 'https://michelcrypt4d4mus.github.io/epstein_text_messages/',
}


epsteinify_api_url = lambda file_id: f"{EPSTEINIFY_URL}/api/documents/HOUSE_OVERSIGHT_{file_id}"
epsteinify_doc_url = lambda file_stem: f"{EPSTEINIFY_URL}/document/{file_stem}"
epsteinify_name_url = lambda name: f"{EPSTEINIFY_URL}/?name={urllib.parse.quote(name)}"

esptein_web_doc_url = lambda file_stem: f"{EPSTEIN_WEB_DOC_URL}/{file_stem}.jpg"

search_archive_url = lambda txt: f"{COURIER_NEWSROOM_ARCHIVE_URL}&q={urllib.parse.quote(txt)}&p=1"
search_coffeezilla_url = lambda txt: f"{COFFEEZILLA_ARCHIVE_URL}&q={urllib.parse.quote(txt)}&p=1"
search_jmail_url = lambda txt: f"{JMAIL_URL}/search?q={urllib.parse.quote(txt)}"
search_twitter_url = lambda txt: f"https://x.com/search?q={urllib.parse.quote(txt)}&src=typed_query&f=live"
