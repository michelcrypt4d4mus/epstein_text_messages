import csv
import re
from copy import deepcopy
from io import StringIO

from dateutil.parser import parse

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX

# Misc
FALLBACK_TIMESTAMP = parse("1/1/2001 12:01:01 AM")
SENT_FROM_REGEX = re.compile(r'^(?:(Please forgive|Sorry for all the) typos.{1,4})?(Sent (from|via).*(and string|AT&T|Droid|iPad|Phone|Mail|BlackBerry(.*(smartphone|device|Handheld|AT&T|T- ?Mobile))?)\.?)', re.M | re.I)

# Email reply regexes (has to be here for circular dependencies reasons)
FORWARDED_LINE_PATTERN = r"-+ ?(Forwarded|Original)\s*Message ?-*|Begin forwarded message:?"
REPLY_LINE_IN_A_MSG_PATTERN = r"In a message dated \d+/\d+/\d+.*writes:"
REPLY_LINE_ENDING_PATTERN = r"[_ \n](AM|PM|[<_]|wrote:?)"
REPLY_LINE_ON_NUMERIC_DATE_PATTERN = fr"On \d+/\d+/\d+[, ].*{REPLY_LINE_ENDING_PATTERN}"
REPLY_LINE_ON_DATE_PATTERN = fr"^On (\d+ )?((Mon|Tues?|Wed(nes)?|Thu(rs)?|Fri|Sat(ur)?|Sun)(day)?|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*)[, ].*{REPLY_LINE_ENDING_PATTERN}"
REPLY_LINE_PATTERN = rf"({REPLY_LINE_IN_A_MSG_PATTERN}|{REPLY_LINE_ON_NUMERIC_DATE_PATTERN}|{REPLY_LINE_ON_DATE_PATTERN}|{FORWARDED_LINE_PATTERN})"
REPLY_REGEX = re.compile(REPLY_LINE_PATTERN, re.IGNORECASE | re.MULTILINE)

HEADER_ABBREVIATIONS = {
    "AD": "Abu Dhabi",
    "Barak": "Ehud Barak (Former Israeli prime minister)",
    "Barrack": "Tom Barrack (Trump ally)",
    'BG, Bill': "Bill Gates",
    "Brock": 'Brock Pierce (crypto bro with a very sordid past)',
    "DB": "Deutsche Bank (maybe??)",
    'HBJ': "Hamad bin Jassim (former Qatari prime minister)",
    'Jabor': '"an influential man in Qatar"',
    'Jared': "Jared Kushner",
    'Jagland': 'Thorbjørn Jagland (former Norwegian prime minister)',
    'Jeffrey Wernick': 'Right wing crypto bro and former COO of Parler',
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

KNOWN_IMESSAGE_FILE_IDS = {
    '031042': ANIL_AMBANI,       # Participants: field
    '027225': ANIL_AMBANI,       # Birthday
    '031173': ARDA_BESKARES,     # Participants: field
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
    '025436': CELINA_DUBIN,
    '027576': MELANIE_WALKER,        # https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.023700
    '027141': MELANIE_WALKER,
    '027232': MELANIE_WALKER,
    '027133': MELANIE_WALKER,
    '027184': MELANIE_WALKER,
    '027214': MELANIE_WALKER,
    '027148': MELANIE_WALKER,
    '027396': SCARAMUCCI,
    '031054': SCARAMUCCI,
}

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
HOUSE_OVERSIGHT_027536.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027655.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027707.txt	Steve Bannon	Italian politics; Trump discussions
HOUSE_OVERSIGHT_027722.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027735.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027794.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_029744.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031045.txt	Steve Bannon (likely)	Trump and New York Times coverage""")

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
    ANN_MARIE_VILLAFANA: re.compile(r'Villafana, Ann Marie|(A(\.|nn) Marie )?Villafa(n|ri)a', re.IGNORECASE),
    ARIANE_DE_ROTHSCHILD: re.compile(r'AdeR|((Ariane|Edmond) de )?Rothschild|Ariane', re.IGNORECASE),
    ANAS_ALRASHEED: re.compile(r'anas\s*al\s*rashee[cd]', re.IGNORECASE),
    BARBRO_EHNBOM: re.compile(r'behnbom@aol.com|(Barbro\s.*)?Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen?', re.IGNORECASE),
    BENNET_MOSKOWITZ: re.compile(r'Moskowitz.*Bennet|Bennet.*Moskowitz', re.IGNORECASE),
    BORIS_NIKOLIC: re.compile(r'(boris )?nikolic?', re.IGNORECASE),
    BRAD_KARP: re.compile(r'Brad (S.? )?Karp|Karp, Brad', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterprise?', re.IGNORECASE),
    DANNY_FROST: re.compile(r'Frost, Danny|frostd@dany.nyc.gov', re.IGNORECASE),
    DARREN_INDYKE: re.compile(r'darren$|darren [il]n[dq]_?yke?|dkiesq', re.IGNORECASE),
    DAVID_STERN: re.compile(r'David Stern?', re.IGNORECASE),
    EDUARDO_ROBLES: re.compile(r'Ed(uardo)?\s*Robles', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|e?h)\s*barak|\behud', re.IGNORECASE),
    FAITH_KATES: re.compile(r'faith kates?', re.IGNORECASE),
    GERALD_BARTON: re.compile(r'Gerald.*Barton', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?|Ghislaine|Maxwell', re.IGNORECASE),
    'Heather Mann': re.compile(r'Heather Mann?', re.IGNORECASE),
    'Intelligence Squared': re.compile(r'intelligence\s*squared', re.IGNORECASE),
    JACKIE_PERCZEK:  re.compile(r'jackie percze[kl]?', re.IGNORECASE),
    JABOR_Y: re.compile(r'[ji]abor\s*y?', re.IGNORECASE),
    JAMES_HILL: re.compile(r"hill, james e.|james.e.hill@abc.com", re.IGNORECASE),
    JEAN_LUC_BRUNEL: re.compile(r'Jean[- ]Luc Brunel?', re.IGNORECASE),
    JEFF_FULLER: re.compile(r"jeff@mc2mm.com|Jeff Fuller", re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'[djl]ee[vy]acation[©@]?g?(mail.com)?|\bJEE?\b|Jeffrey E((sp|ps)tein?)?|jeeproject@yahoo.com|J Jep|Jeffery Edwards|(?<!Mark L. )Epstein', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|(joichi|joi)( Ito)?', re.IGNORECASE),
    JOHNNY_EL_HACHEM: re.compile(r'el hachem johnny|johnny el hachem', re.IGNORECASE),
    JONATHAN_FARKAS: re.compile(r'Jonathan Farka(s|il)', re.IGNORECASE),
    KATHRYN_RUEMMLER: re.compile(r'Kathr?yn? Ruemmler?', re.IGNORECASE),
    KEN_STARR: re.compile(r'starr, ken|Ken(neth W.)?\s+starr?|starr', re.IGNORECASE),
    LANDON_THOMAS: re.compile(r'lando[nr] thomas( jr)?|thomas jr.?, lando[nr]', re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r'(La(wrence|rry).{1,5})?Summers?|^LH$|LHS|Ihsofficel', re.IGNORECASE),
    LAWRANCE_VISOSKI: re.compile(r'La(rry|wrance) Visoski?', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus|lawkrauss', re.IGNORECASE),
    LEON_BLACK: re.compile(r'Leon Black?', re.IGNORECASE),
    MANUELA_MARTINEZ: re.compile(fr'Manuela (- Mega Partners|Martinez)', re.IGNORECASE),
    MARIANA_IDZKOWSKA: re.compile(r'Mariana [Il]d[źi]kowska?', re.IGNORECASE),
    MARK_EPSTEIN: re.compile(r'Mark (L\. )?Epstein', re.IGNORECASE),
    LILLY_SANCHEZ: re.compile(r'Lilly.*Sanchez', re.IGNORECASE),
    LISA_NEW: re.compile(r'E?Lisa New?\b', re.IGNORECASE),
    MARC_LEON: re.compile(r'Marc[.\s]+(Kensington|Leon)|Kensington2', re.IGNORECASE),
    MARTIN_NOWAK: re.compile(r'Martin.*?Nowak|Nowak, Martin', re.IGNORECASE),
    MARTIN_WEINBERG: re.compile(r'martin.*?weinberg', re.IGNORECASE),
    "Matthew Schafer": re.compile(r"matthew\.?schafer?", re.IGNORECASE),
    MELANIE_SPINELLA: re.compile(r'M?elanie Spine[Il]{2}a', re.IGNORECASE),
    MICHAEL_BUCHHOLTZ: re.compile(r'Michael.*Buchholtz', re.IGNORECASE),
    MICHAEL_MILLER: re.compile(r'Micha(el)? Miller|Miller, Micha(el)?', re.IGNORECASE),
    MICHAEL_WOLFF: re.compile(r'Michael\s*Wol(f[ef]|i)|Wolff', re.IGNORECASE),
    MICHAEL_SITRICK: re.compile(r'(Mi(chael|ke).{0,5})?[CS]itrick', re.IGNORECASE),
    MIROSLAV_LAJCAK: re.compile(r"Miro(slav)?(\s+Laj[cč][aá]k)?"),
    MOHAMED_WAHEED_HASSAN: re.compile(r'Mohamed Waheed(\s+Hassan)?', re.IGNORECASE),
    NADIA_MARCINKO: re.compile(r"Na[dď]i?a\s+Marcinko(v[aá])?", re.IGNORECASE),
    NEAL_KASSELL: re.compile(r'Neal Kassel', re.IGNORECASE),
    NICHOLAS_RIBIS: re.compile(r'Nicholas[ ._]Ribi?s?', re.IGNORECASE),
    OLIVIER_COLOM: re.compile(fr'Colom, Olivier|{OLIVIER_COLOM}', re.IGNORECASE),
    PAUL_BARRETT: re.compile(r'Paul Barre(d|tt)', re.IGNORECASE),
    PAUL_KRASSNER: re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    PAULA: re.compile(r'^Paula$', re.IGNORECASE),
    PAUL_MORRIS: re.compile(r'morris, paul|Paul Morris', re.IGNORECASE),
    PEGGY_SIEGAL:  re.compile(r'Peggy Siegal?', re.IGNORECASE),
    PETER_ATTIA: re.compile(r'Peter Attia?', re.IGNORECASE),
    PETER_MANDELSON: re.compile(r"((Lord|Peter) )?Mandelson", re.IGNORECASE),
    'pink@mc2mm.com': re.compile(r"^Pink$|pink@mc2mm\.com", re.IGNORECASE),
    PRINCE_ANDREW: re.compile(r'Prince Andrew|The Duke', re.IGNORECASE),
    REID_WEINGARTEN: re.compile(r'Weingarten, Rei[cdi]|Rei[cdi] Weingarten', re.IGNORECASE),
    RICHARD_KAHN: re.compile(r'rich(ard)? kahn?', re.IGNORECASE),
    ROBERT_D_CRITTON: re.compile(r'Robert D.? Critton Jr.?', re.IGNORECASE),
    ROBERT_LAWRENCE_KUHN: re.compile(r'Robert\s*(Lawrence)?\s*Kuhn', re.IGNORECASE),
    ROBERT_TRIVERS: re.compile(r'tri[vy]ersr@gmail|Robert\s*Trivers?', re.IGNORECASE),
    ROSS_GOW: re.compile(fr"{ROSS_GOW}|ross@acuityreputation.com", re.IGNORECASE),
    SAMUEL_LEFF: re.compile(r"Sam(uel)?(/Walli)? Leff", re.IGNORECASE),
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
    GORDON_GETTY,
    'Jack Lang',
    'Jack Scarola',
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
    MARK_TRAMO,
    MELANIE_WALKER,
    MERWIN_DELA_CRUZ,
    'Michael Simmons',   # Not the only "To:"
    'middle.east.update@hotmail.com',
    'Nancy Cain',
    'Nancy Dahl',
    'Nancy Portland',
    'Oliver Goodenough',
    'Peter Aldhous',
    'Peter Green',
    ROGER_SCHANK,
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
    '033328': AZIZA_ALAHMADI,        # "Regards, #####" at bottom with same pattern
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
    '030634': FAITH_KATES,          # Same as unredacted 031135, same legal signature
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
    '018726': JEFFREY_EPSTEIN,       # Strange fragment only showing what was replied to
    '032283': JEFFREY_EPSTEIN,       # Strange fragment only showing what was replied to
    '026943': JEFFREY_EPSTEIN,       # Strange fragment only showing what was replied to
    '030768': JEFFREY_EPSTEIN,
    '031996': JEFFREY_EPSTEIN,       # bounced
    '022938': JEFFREY_EPSTEIN,
    '028675': JEFFREY_EPSTEIN,       # Just bad OCR
    '025041': JEFFREY_EPSTEIN,       # Just bad OCR
    '032214': JEFFREY_EPSTEIN,       # Just bad OCR
    '029582': JEFFREY_EPSTEIN,
    '031791': JESSICA_CADWELL,
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
    '026652': KATHRYN_RUEMMLER,          # Just bad OCR
    '032224': KATHRYN_RUEMMLER,
    '032386': KATHRYN_RUEMMLER,          # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '032727': KATHRYN_RUEMMLER,          # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '030478': LANDON_THOMAS,
    '029013': LARRY_SUMMERS,
    '032206': LAWRENCE_KRAUSS,         # More of a text convo?
    '032209': LAWRENCE_KRAUSS,         # More of a text convo?
    # '032210': LAWRENCE_KRAUSS,         # More of a text convo?
    '029196': LAWRENCE_KRAUSS,
    '033487': LAWRANCE_VISOSKI,
    '028789': LAWRANCE_VISOSKI,
    '027046': LAWRANCE_VISOSKI,
    '033370': LAWRANCE_VISOSKI,        # Planes discussion signed larry
    '031129': LAWRANCE_VISOSKI,        # Planes discussion, same file as 029977
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
    '029020': RENATA_BOLOTOVA,         # Signature
    '029605': RENATA_BOLOTOVA,         # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '029606': RENATA_BOLOTOVA,         # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '029604': RENATA_BOLOTOVA,         # Continued in 239606 etc
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
    # Unknowns
    '022187': None,                    # Bad OCR causes parsing problems
    # '026571': '(unknown french speaker)',
    # '029504': Probably Audrey Raimbault (based on "GMI" in signature, a company registered by "aubrey raimbault")
}

# Some emails have a lot of uninteresting CCs
IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS = ['Allen West', 'Rafael Bardaji', 'Philip Kafka', 'Herb Goodman', 'Grant Seeger', 'Lisa Albert', 'Janet Kafka', 'James Ramsey', 'ACT for America', 'John Zouzelka', 'Joel Dunn', 'Nate McClain', 'Bennet Greenwald', 'Taal Safdie', 'Uri Fouzailov', 'Neil Anderson', 'Nate White', 'Rita Hortenstine', 'Henry Hortenstine', 'Gary Gross', 'Forrest Miller', 'Bennett Schmidt', 'Val Sherman', 'Marcie Brown', 'Michael Horowitz', 'Marshall Funk']
KRASSNER_MANSON_RECIPIENTS = ['Nancy Cain', 'Tom', 'Marie Moneysmith', 'Steven Gaydos', 'George Krassner', 'Linda W. Grossman', 'Holly Krassner Dawson', 'Daniel Dawson', 'Danny Goldberg', 'Caryl Ratner', 'Kevin Bright', 'Michael Simmons', SAMUEL_LEFF, 'Bob Fass', 'Lynnie Tofte Fass', 'Barb Cowles', 'Lee Quarnstrom']
KRASSNER_024923_RECIPIENTS = ['George Krassner', 'Nick Kazan', 'Mrisman02', 'Rebecca Risman', 'Linda W. Grossman']
KRASSNER_033568_RECIPIENTS = ['George Krassner', 'Daniel Dawson', 'Danny Goldberg', 'Tom', 'Kevin Bright', 'Walli Leff', 'Michael Simmons', 'Lee Quarnstrom', 'Lanny Swerdlow', 'Larry Sloman', 'W&K', 'Harry Shearer', 'Jay Levin']
FLIGHT_IN_2012_PEOPLE = ['Francis Derby', 'Januiz Banasiak', 'Louella Rabuyo', 'Richard Barnnet']

KNOWN_EMAIL_RECIPIENTS = {
    '030626': [ALAN_DERSHOWITZ, DARREN_INDYKE, KATHRYN_RUEMMLER, KEN_STARR, MARTIN_WEINBERG],
    '028968': [ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN],
    '029835': [ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN],
    '027063': ANTHONY_BARRETT,
    '030764': ARIANE_DE_ROTHSCHILD,   # Reply
    '026431': ARIANE_DE_ROTHSCHILD,   # Reply
    '032876': CECILIA_STEEN,
    '031996': CHRISTINA_GALBRAITH,    # bounced
    '033583': [DARREN_INDYKE, JACK_GOLDBERGER],  # Bad OCR
    '033144': [DARREN_INDYKE, RICHARD_KAHN],
    '026245': DIANE_ZIMAN,            # Quoted reply
    '026466': DIANE_ZIMAN,            # Quoted reply
    '031607': EDWARD_EPSTEIN,
    '030525': FAITH_KATES,            # Same as unredacted 030414, same legal signature
    '030999': [JACK_GOLDBERGER, ROBERT_D_CRITTON],
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
    '029196': JEFFREY_EPSTEIN,        # More of a text convo?
    '029324': [JEFFREY_EPSTEIN, 'Jojo Fontanilla', 'Lyn Fontanilla'],
    '033575': [JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN],
    '023067': [JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN, TONJA_HADDAD_COLEMAN],      # Bad OCR
    '033228': [JEFFREY_EPSTEIN, DARREN_INDYKE, FRED_HADDAD],   # Bad OCR
    '025790': [JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER],   # Bad OCR
    '025790': [JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER],   # Bad OCR
    '031384': [JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER, MARTIN_WEINBERG, SCOTT_J_LINK],
    '033512': [JEFFREY_EPSTEIN, DARREN_INDYKE, JACKIE_PERCZEK, MARTIN_WEINBERG],
    '029977': [JEFFREY_EPSTEIN, DARREN_INDYKE, LESLEY_GROFF, RICHARD_KAHN] + FLIGHT_IN_2012_PEOPLE,
    '032063': [JEFFREY_EPSTEIN, DARREN_INDYKE, REID_WEINGARTEN],
    '033486': [JEFFREY_EPSTEIN, DARREN_INDYKE, RICHARD_KAHN],  # OCR
    '033156': [JEFFREY_EPSTEIN, DARREN_INDYKE, RICHARD_KAHN],  # OCR
    '029154': [JEFFREY_EPSTEIN, DAVID_HAIG],         # Bad OCR
    '029498': [JEFFREY_EPSTEIN, DAVID_HAIG, GORDON_GETTY, 'Norman Finkelstein'],      # Bad OCR
    '029889': [JEFFREY_EPSTEIN, JACK_GOLDBERGER, ROBERT_D_CRITTON, 'Connie Zaguirre'],  # Bad OCR
    '028931': [JEFFREY_EPSTEIN, LAWRENCE_KRAUSS],    # Bad OCR
    '026620': [JEFFREY_EPSTEIN, MARK_EPSTEIN, MICHAEL_BUCHHOLTZ] + IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS,
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
    '033073': KATHRYN_RUEMMLER,         # to "Kathy" about dems, sent from iPad (not 100% confirmed)
    '032939': KATHRYN_RUEMMLER,         # to "Kathy" about dems, sent from iPad (not 100% confirmed)
    '031428': [KEN_STARR, LILLY_SANCHEZ, MARTIN_WEINBERG, REID_WEINGARTEN],  # Bad OCR
    '031388': [KEN_STARR, LILLY_SANCHEZ, MARTIN_WEINBERG, REID_WEINGARTEN],  # Bad OCR
    '025329': KRASSNER_MANSON_RECIPIENTS,
    '033568': KRASSNER_033568_RECIPIENTS,
    '024923': KRASSNER_024923_RECIPIENTS,
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
    '032048': MARIANA_IDZKOWSKA,      # Redacted here, visisble in 030242
    '030368': MELANIE_SPINELLA,       # Actually a self fwd from jeffrey to jeffrey
    '030369': MELANIE_SPINELLA,       # Actually a self fwd from jeffrey to jeffrey
    '030371': MELANIE_SPINELLA,       # Actually a self fwd from jeffrey to jeffrey
    '023291': [MELANIE_SPINELLA, BRAD_WECHSLER],  # Can be seen in 023028
    '032214': MIROSLAV_LAJCAK,        # Quoted reply has signature
    '022258': NADIA_MARCINKO,         # Reply header
    '033097': [PAUL_BARRETT, RICHARD_KAHN],  # Bad OCR
    '030506': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030507': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030508': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030509': PAULA,                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030096': PETER_MANDELSON,
    '032951': [RAAFAT_ALSABBAGH, None],  # Redacted
    '029581': RENATA_BOLOTOVA,        # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '029582': RENATA_BOLOTOVA,         # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '030384': [RICHARD_KAHN, 'Alan Dlugash'],
    '019334': STEVE_BANNON,
    '021106': STEVE_BANNON,     # Reply
    # '032213': Probably MIRO or Reid Weingarten based on replies but he sent it to a lot of people
}

# Reason string should end in a file ID
SUPPRESS_OUTPUT_FOR_EMAIL_IDS = {
    '026499': "quoted in full in 026298",
    '028529': "the same as 022344",
    '026563': "a redacted version of 028768",
    '028621': "the same as 019412",
    '028765': "the same as 027053",
    '028773': "the same as 027049",
    '028762': "a redacted version of 027056",
    '028781': "the same as 013460",
    '033207': "the same as 033580",
    '025547': "the same document as 028506",
    '026549': "the same as 028784",
    '033599': "the same as 033386",
    '030622': 'the same as 023024',
    '023026': 'the same as 030618',
    '032246': 'a redacted version of 032248',
    '012898': 'the same as 033575',
    '026834': 'the same as 028780',
    '026835': 'the same as 028775',
    '028968': 'the same as 029835',
    '033489': 'the same as 033251',
    '033517': 'a reminder with same text as 033528',
    '032012': 'a reminder with same text as 032023',
    '028482': 'the same as 026620',
    '019465': 'the same as 031118',
    '032158': 'the same as 031912',
    '030514': 'the same as 030587',
    '012685': 'the same as 029773',
    '033482': 'the same as 029849',
    '023065': 'a redacted version of 030628',
    '033586': 'the same as 033297',
    '018084': 'the same as 031089',
    '030885': 'the same as 031088',
    '030578': 'a redacted version of 030414',
    '032048': 'a redacted version of 030242',
    '031130': 'the same as 030238',
    '031067': 'the same as 030859',
    '028791': 'the same as 031136',
    '031134': 'the same as 030635',
    '026234': 'the same as 028494',
    '021790': 'the same as 030311',
    '029880': 'the same as 033508',
    '030612': 'the same as 030493',
    '031771': 'the same as 032051',
    '021761': 'the same as 031217',
    '031388': 'the same as 031428',
    '033169': 'the same as 033584',
    '031426': 'the same as 031346',
    '028789': 'the same as 027046',
    '031427': 'the same as 031345',
    '031432': 'the same as 031343',
    '021794': 'the same as 030299',
    '031084': 'the same as 031020',
    '033485': 'the same as 033354',
    '021241': 'the same as 031999',
    '033484': 'the same as 033282',
    '028675': 'the same as 025041',
    '030602': 'the same as 030502',
    '033486': 'the same as 033156',
    '030617': 'the same as 030574',
    '025226': 'the same as 031156',
    '031086': 'the same as 031018',
    '031079': 'the same as 031026',
    '032389': 'the same as 033582',
    '031787': 'the same as 032011',
    '022202': 'the same as 029975',
    '030498': 'the same as 030606',
    '021235': 'the same as 032005',
    '026160': 'the same as 028505',
    '029779': 'the same as 029692',
    '030837': 'the same as 031126',
    '031226': 'a redacted version of 017523',
    '029778': 'the same as 029624',
    '031973': 'the same as 024923',
    '031422': 'the same as 031338',
    '031008': 'a redacted version of 031099',
    '030634': 'a redacted version of 031135',
    '033466': 'the same as 033591',
    '023067': 'the same as 030620',
    '033289': 'the same as 033587',
    '026228': 'the same as 028497',
    '012722': 'the same as 032107',
    '031114': 'the same as 030844',
    '031120': 'the same as 029968',
    '031074': 'the same as 031031',
    '028531': 'the same as 027032',
    '018197': 'the same as 028648',
    '026612': 'the same as 028487',
    '028493': 'the same as 026777',
    '029255': 'the same as 029837',
    '033154': 'the same as 033488',
    '033463': 'a redacted version of 033596',
    '023018': 'a redacted version of 030624',
    '025361': 'the same as 031423',
    '033594': 'the same as 029299',
    '031069': 'the same as 030904',
    '031165': 'the same as 030006',
    '031159': 'the same as 025215',
    '031090': 'the same as 031011',
    '018158': 'the same as 032068',
    '031221': 'the same as 031213',
    '016690': 'the same as 016595',
    '028970': 'the same as 029833',
    '028958': 'the same as 029839',
    '031227': 'the same as 031206',
    '032531': 'a redacted version of 033490',
    '033503': 'the same as 029893',
    '028486': 'the same as 025878',
    '033581': 'the same as 033203',
    '033565': 'the same as 032764',
    '028485': 'the same as 026618',
    '028728': 'the same as 027102',
    '030495': 'the same as 030609',
    '033361': 'the same as 033512',
    '028972': 'the same as 029831',
    '030616': 'the same as 021758',
    '029884': 'the same as 033498',
    '027094': 'the same as 028620',
    '033579': 'the same as 032456',
    '030255': 'the same as 030315',
    '030596': 'a redacted version of 030335',
    '032052': 'the same as 031732',
    '026745': 'the same except for \'your Anna!\' as 031215',
    '028787': 'the same as 027097',
    '030876': 'the same as 031112',
    '030491': 'the same as 030614',
    '032279': 'the same as 033585',
    '019409': 'the same as 031980',
    '031994': 'the same as 025790',
    '031189': 'the same as 031220',
    '033563': 'the same as 032779',
    '033577': 'the same as 033230',
    '023971': 'the same as 032125',
    '031442': 'the same as 031996',
    '031203': 'the same as 031230',
    '012711': 'a redacted version of 029841',
    '026569': 'the same as 028752',
    '032050': 'the same as 031773',
    '031983': 'the same as 021400',
    '030581': 'the same as 030525',
    '033491': 'the same as 026548',
    '023550': 'the same as 029752',
    '030592': 'the same as 030339',
    '031129': 'the same as 029977',
    '033561': 'the same as 033157',
    '033589': 'the same as 032250',
    '031708': 'the same as 026624',
}

EMAILED_ARTICLE_IDS = [
    '029692',  # WaPo article
    '029779',  # WaPo article
    '026298',  # Written by someone else?
    '026755',  # HuffPo
    '023627',  # Wolff article about epstein
    '031569',  # Article by Kathryn Alexeeff
    '030528',  # Vicky Ward article
    '030522',  # Vicky Ward article
    '018197', '028648',  # Ray Takeyh article fwd
    '028728', '027102',  # WSJ forward to Larry Summers
    '028508',  # nanosatellites article
    '013460', '028781',  # Atlantic on Jim Yong Kim, Obama's World Bank Pick
    '019845',  # article on Preet Bharara
]
