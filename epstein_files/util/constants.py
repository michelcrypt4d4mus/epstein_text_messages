import csv
import re
from copy import deepcopy
from datetime import datetime
from io import StringIO

from dateutil.parser import parse

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX

# Misc
FALLBACK_TIMESTAMP = parse("1/1/2051 12:01:01 AM")
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
    'JEGE': "Epstein's airplane holding company",
    'Jeffrey Wernick': 'Right wing crypto bro and former COO of Parler',
    'Joi': 'Joi Ito (MIT Media Lab)',
    "Hoffenberg": "Steven Hoffenberg (Epstein's ponzi scheme partner)",
    'KSA': "Kingdom of Saudi Arabia",
    'Kurz': 'Sebastian Kurz (former Austrian Chancellor)',
    'Kwok': "Chinese criminal Miles Kwok AKA Miles Guo AKA Guo Wengui",
    'LSJ': "Epstein's private island holding company",
    'Madars': 'Madars Virza, co-founder of the privacy coin ZCash (ZEC)',
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
    '027762': ANDRZEJ_DUDA,
    '027774': ANDRZEJ_DUDA,
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
    ALAN_DERSHOWITZ: re.compile(r'(alan.{1,7})?dershowi(lz?|tz)|AlanDersh', re.IGNORECASE),
    ALIREZA_ITTIHADIEH: re.compile(r'Alireza.[Il]ttihadieh', re.IGNORECASE),
    AMANDA_ENS: re.compile(r'ens, amanda?|Amanda.Ens', re.IGNORECASE),
    ANIL_AMBANI: re.compile(r'Anil.Ambani', re.IGNORECASE),
    ANN_MARIE_VILLAFANA: re.compile(r'Villafana, Ann Marie|(A(\.|nn) Marie )?Villafa(n|ri)a', re.IGNORECASE),
    ARIANE_DE_ROTHSCHILD: re.compile(r'AdeR|((Ariane|Edmond) de )?Rothschild|Ariane', re.IGNORECASE),
    ANAS_ALRASHEED: re.compile(r'anas\s*al\s*rashee[cd]', re.IGNORECASE),
    BARBRO_EHNBOM: re.compile(r'behnbom@aol.com|(Barbro\s.*)?Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry\s*((j.?|james)\s*)?cohen?', re.IGNORECASE),
    BENNET_MOSKOWITZ: re.compile(r'Moskowitz.*Bennet|Bennet.*Moskowitz', re.IGNORECASE),
    BORIS_NIKOLIC: re.compile(r'(boris )?nikolic?', re.IGNORECASE),
    BRAD_EDWARDS:  re.compile(r'Brad(ley)?(\s*J(.?|ames))?\s*Edwards', re.IGNORECASE),
    BRAD_KARP: re.compile(r'Brad (S.? )?Karp|Karp, Brad', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterprise?', re.IGNORECASE),
    DANNY_FROST: re.compile(r'Frost, Danny|frostd@dany.nyc.gov', re.IGNORECASE),
    DARREN_INDYKE: re.compile(r'darren$|darren [il]n[dq]_?yke?|dkiesq', re.IGNORECASE),
    DAVID_FISZEL: re.compile(r'David\s*Fis?zel', re.IGNORECASE),
    DAVID_STERN: re.compile(r'David Stern?', re.IGNORECASE),
    EDUARDO_ROBLES: re.compile(r'Ed(uardo)?\s*Robles', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|e?h)\s*barak|\behud', re.IGNORECASE),
    FAITH_KATES: re.compile(r'faith kates?', re.IGNORECASE),
    GERALD_BARTON: re.compile(r'Gerald.*Barton', re.IGNORECASE),
    GERALD_LEFCOURT: re.compile(r'Gerald\s*(B\.?\s*)?Lefcourt', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?|Ghislaine|Maxwell', re.IGNORECASE),
    'Heather Mann': re.compile(r'Heather Mann?', re.IGNORECASE),
    'Intelligence Squared': re.compile(r'intelligence\s*squared', re.IGNORECASE),
    JACKIE_PERCZEK:  re.compile(r'jackie percze[kl]?', re.IGNORECASE),
    JABOR_Y: re.compile(r'[ji]abor\s*y?', re.IGNORECASE),
    JAMES_HILL: re.compile(r"hill, james e.|james.e.hill@abc.com", re.IGNORECASE),
    JEAN_LUC_BRUNEL: re.compile(r'Jean[- ]Luc Brunel?', re.IGNORECASE),
    JEFF_FULLER: re.compile(r"jeff@mc2mm.com|Jeff Fuller", re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'[djl]ee[vy]acation[©@]?g?(mail.com)?|Epstine|\bJEE?\b|Jeffrey E((sp|ps)tein?)?|jeeproject@yahoo.com|J Jep|Jeffery Edwards|(?<!Mark L. )Epstein', re.IGNORECASE),
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
    JACK_SCAROLA,
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
    '026624': DARREN_INDYKE,        # weird format (signature on top)
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
    '023208': JEFFREY_EPSTEIN,       # Same as 023291
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
    '026652': KATHRYN_RUEMMLER,       # Just bad OCR
    '032224': KATHRYN_RUEMMLER,
    '032386': KATHRYN_RUEMMLER,       # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '032727': KATHRYN_RUEMMLER,       # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '030478': LANDON_THOMAS,
    '029013': LARRY_SUMMERS,
    '032206': LAWRENCE_KRAUSS,         # More of a text convo?
    '032209': LAWRENCE_KRAUSS,         # More of a text convo?
    '032208': LAWRENCE_KRAUSS,         # More of a text convo?
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
    '029985': TERRY_KAFKA,             # Quoted reply in 029992
    '020666': TERRY_KAFKA,             # ends with 'Terry'
    '026014': ZUBAIR_KHAN,             # truncated to only show the quoted reply
    # Unknowns
    '022187': None,                    # Bad OCR causes parsing problems
    # '026571': '(unknown french speaker)',
    '029504': 'Probably Audrey/Aubrey Raimbault',  # (based on "GMI" in signature, a company registered by "aubrey raimbault")
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
    '030575': FAITH_KATES,            # Same Next Management LLC legal signature
    '030475': FAITH_KATES,            # Same Next Management LLC legal signature
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
    '022344': JEFFREY_EPSTEIN,        # Bad OCR
    '029013': JEFFREY_EPSTEIN,        # Bad OCR
    '030347': JEFFREY_EPSTEIN,        # Bad OCR
    '030367': JEFFREY_EPSTEIN,        # Bad OCR
    '026245': JEFFREY_EPSTEIN,        # Bad OCR
    '033274': JEFFREY_EPSTEIN,        # this is a note sent to self
    '032780': JEFFREY_EPSTEIN,        # Bad OCR
    '025233': JEFFREY_EPSTEIN,        # Bad OCR
    '032208': JEFFREY_EPSTEIN,        # More of a text convo with Lawrence Krauss?
    '026014': JEFFREY_EPSTEIN,        # truncated to only show the quoted reply
    '026624': JEFFREY_EPSTEIN,        # weird format (signature on top)
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
    '033456': 'Joel',                   # Reply
    '033460': 'Joel',                   # Reply
    '029282': [JOI_ITO, REID_HOFFMAN],  # Bad OCR
    '021090': JONATHAN_FARKAS,          # Reply to a message signed " jonathan" same as other Farkas emails
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
    '023208': [MELANIE_SPINELLA, BRAD_WECHSLER],  # Can be seen in 023291
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

# Some files are so broken we just have to hardcode it
EMAIL_TIMESTAMPS = {
    '028851': datetime(2014, 4, 27, 6, 00),
    '028849': datetime(2014, 4, 27, 6, 30),
    '032283': datetime(2016, 9, 14, 8, 4),
    '026624': datetime(2016, 10, 1, 16, 40),
    '026014': datetime(2016, 11, 4, 17, 46),
    '032475': datetime(2017, 2, 15, 13, 31, 25),
    '018726': datetime(2018, 6, 8, 8, 36),
    '030373': datetime(2018, 10, 3, 1, 49, 27),
    '026943': datetime(2019, 5, 22, 5, 47),
}

# Reason string should end in a file ID
DUPLICATE_FILE_IDS = {
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
    '026624': 'the same as 031708',
    '030575': 'a redacted version of 030475',
    '023291': 'the same as (?) 023208',
    # non-email documents
    '031415': 'the same as 031396',
    '029357': 'the same as (?) 028887',
    '025210': 'the same as 025205',
    '019864': 'the same as 019849',
    '033481': 'the same as 033480',
    '014697': 'the same as 011284',  # Jeremy Gillula name removed
    '016616': 'the same as 016554',
    '016574': 'the same as 016554',
    '023121': 'earlier draft of 023123'
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
    '029021',  # article about bannon sent by Alain Forget
    '031688',  # Bill Siegel fwd of email about hamas
    '021090',  # Fwd to Jonathan Farkas
    '026551',  # Sultan bin Sulayem Ayatollah between the sheets
    '031768',  # Sultan bin Sulayem 'Horseface'
]

# Descriptions of non-email, non-text message files
CVRA = "Crime Victims' Rights Act [CVRA]"
DEEP_THINKING_HINT = 'book: "Deep Thinking: Twenty-Five Ways of Looking at AI" by John Brockman 2019-02-19'
EDWARDS_V_DERSHOWITZ = f"{BRAD_EDWARDS} and Paul Cassell v. {ALAN_DERSHOWITZ}"
EPSTEIN_V_EDWARDS = f"Epstein v. Scott Rothstein and {BRAD_EDWARDS}"
GIUFFRE_V_MAXWELL = f"Virginia Giuffre v. {GHISLAINE_MAXWELL}"
HARVARD_POETRY = f'Harvard poetry stuff from {LISA_NEW}'
HBS_APPLICATION_NERIO = f"Harvard Business School application letter from Nerio Alessandri (Founder and Chairman Technogym SPA Italy)"
JANE_DOE_V_USA = 'Jane Doe #1 and Jane Doe #2 v. United States'
JP_MORGAN_EYE_ON_THE_MARKET = f"JP Morgan Eye On The Market report"
KEN_STARR_LETTER = f"letter from {KEN_STARR} to judge overseeing Epstein's criminal prosecution, mentions Alex Acosta"
MICHAEL_WOLFF_ARTICLE_HINT = f"draft of an unpublished article about Epstein by {MICHAEL_WOLFF} written ca. 2014/2015"
NIGHT_FLIGHT_HINT = f'draft of book named "Night Flight" by {EHUD_BARAK}?'
OBAMA_JOKE = f'joke about Obama'
PATTERSON_BOOK_SCANS = f'pages of "Filthy Rich: The Shocking True Story of Jeffrey Epstein" by James Patterson 2016-10-10'
SHIMON_POST = 'The Shimon Post selection of articles about the mideast '
VI_DAILY_NEWS_ARTICLE = 'article in Virgin Islands Daily News'
VIRGINIA_FILING = f"court filings from Virginia Giuffre's lawsuit against Epstein (and {ALAN_DERSHOWITZ}?)"
WEINBERG_ABC_LETTER = f"letter from {MARTIN_WEINBERG} to ABC / Good Morning America threatening libel lawsuit"

FILE_DESCRIPTIONS = {
    # books
    '016221': DEEP_THINKING_HINT,
    '016804': DEEP_THINKING_HINT,
    '011472': NIGHT_FLIGHT_HINT,
    '027849': NIGHT_FLIGHT_HINT,
    '010477': PATTERSON_BOOK_SCANS,
    '010486': PATTERSON_BOOK_SCANS,
    '021958': PATTERSON_BOOK_SCANS,
    '022058': PATTERSON_BOOK_SCANS,
    '022118': PATTERSON_BOOK_SCANS,
    '019111': PATTERSON_BOOK_SCANS,
    '015032': f'book: "60 Years of Investigative Satire: The Best of {PAUL_KRASSNER}"',
    '015675': f'book: "Are the Androids Dreaming Yet? Amazing Brain Human Communication, Creativity & Free Will" by James Tagg',
    '012899': f'book: "Engineering General Intelligence: A Path to Advanced AGI Via Embodied Learning and Cognitive Synergy" by Ben Goertzel',
    '012747': f'book: "Evilicious: Explaining Our Taste For Excessive Harm" by Marc D. Hauser',
    '019874': f'book: "Fire And Fury" by {MICHAEL_WOLFF}',
    '010912': f'book: "Free Growth and Other Surprises" by Gordon Getty (draft) 2018-10-18',
    '021247': f'book: "Invisible Forces And Powerful Beliefs: Gravity, Gods, And Minds" by The Chicago Social Brain Network 2010-10-04',
    '019477': f'book: "How America Lost Its Secrets: Edward Snowden, the Man, and the Theft" by {EDWARD_EPSTEIN}',
    '017088': f'book: "Taking the Stand: My Life in the Law" by {ALAN_DERSHOWITZ} (draft)',
    '023731': f'book: "Teaching Minds How Cognitive Science Can Save Our Schools" by {ROGER_SCHANK}',
    '013796': f'book: "The 4-Hour Workweek" by Tim Ferriss',
    '021145': f'book: "The Billionaire\'s Playboy Club" by Virginia Giuffre (draft?)',
    '013501': f'book: "The Nearness Of Grace: A Personal Science Of Spiritual Transformation" by Arnold J. Mandell 2005-01-01 (ish)',
    '018438': f'book: "The S&M Feminist" by Clarisse Thorn',
    '018232': f'book: "The Seventh Sense: Power, Fortune & Survival in the Age of Networks" by Joshua Cooper Ramo',
    '020153': f'book: "The Snowden Affair: A Spy Story In Six Parts" by {EDWARD_EPSTEIN}',
    '021120': f'chapter of "Siege: Trump Under Fire" by {MICHAEL_WOLFF}',
    '031533': f'few pages from book about the Baylor University sexual assault scandal and Sam Ukwuachu',
    # articles
    '022707': MICHAEL_WOLFF_ARTICLE_HINT,
    '022727': MICHAEL_WOLFF_ARTICLE_HINT,
    '022746': MICHAEL_WOLFF_ARTICLE_HINT,
    '022844': MICHAEL_WOLFF_ARTICLE_HINT,
    '022863': MICHAEL_WOLFF_ARTICLE_HINT,
    '022894': MICHAEL_WOLFF_ARTICLE_HINT,
    '022952': MICHAEL_WOLFF_ARTICLE_HINT,
    '023627': MICHAEL_WOLFF_ARTICLE_HINT,
    '024229': MICHAEL_WOLFF_ARTICLE_HINT,
    '012740': f"{PEGGY_SIEGAL} article about Venice Film Festival 2011-09-06",
    '013442': f"{PEGGY_SIEGAL} draft about Oscars around 2011-02-27",
    '012700': f"{PEGGY_SIEGAL} film events diary 2011-02-27",
    '012690': f"{PEGGY_SIEGAL} film events diary 2011-02-27, draft of 012700",
    '013450': f"{PEGGY_SIEGAL} Oscar Diary April 2011-02-27 (Avenue Magazine)",
    '010715': f"{PEGGY_SIEGAL} Oscar Diary April 2012-02-27",
    '019864': f"{PEGGY_SIEGAL} Oscar Diary April 2017-02-27",
    '019849': f"{PEGGY_SIEGAL} Oscar Diary April 2017-02-27",
    '030030': f'{SHIMON_POST} 2011-03-29',
    '025610': f'{SHIMON_POST} 2011-04-03',
    '023458': f'{SHIMON_POST} 2011-04-17',
    '023487': f'{SHIMON_POST} 2011-04-18',
    '030531': f'{SHIMON_POST} 2011-04-20',
    '024958': f'{SHIMON_POST} 2011-05-08',
    '030060': f'{SHIMON_POST} 2011-05-13',
    '030531': f'{SHIMON_POST} 2011-05-16',
    '031834': f'{SHIMON_POST} 2011-05-16',
    '023517': f'{SHIMON_POST} 2011-05-26',
    '030268': f'{SHIMON_POST} 2011-05-29',
    '029628': f'{SHIMON_POST} 2011-06-04',
    '018085': f'{SHIMON_POST} 2011-06-07',
    '030156': f'{SHIMON_POST} 2011-06-22',
    '031876': f'{SHIMON_POST} 2011-06-14',
    '032171': f'{SHIMON_POST} 2011-06-26',
    '029932': f'{SHIMON_POST} 2011-07-03',
    '031913': f'{SHIMON_POST} 2011-08-24',
    '024592': f'{SHIMON_POST} 2011-08-25',
    '024997': f'{SHIMON_POST} 2011-09-08',
    '031941': f'{SHIMON_POST} 2011-11-17',
    '031753': f'{PAUL_KRASSNER} essay',
    '023638': f'{PAUL_KRASSNER} magazine interview',
    '024374': f'{PAUL_KRASSNER} "Remembering Cavalier Magazine"',
    '030187': f'{PAUL_KRASSNER} "Remembering Lenny Bruce While We\'re Thinking About Trump" (draft?)',
    '019088': f'{PAUL_KRASSNER} "Are Rape Jokes Funny? (draft) 2012-07-28',
    '031725': f"article about Gloria Allred and Trump allegations 2016-10-10",
    '012704': f"article about {JANE_DOE_V_USA} and {CVRA} 2011-04-21",
    '026584': f'article from 2009 about tax implications of disregarded entities',
    '032159': f"article about microfinance and cell phones in Zimbabwe, Strive Masiyiwa (Econet Wireless)",
    '031776': f"article about Michael Avenatti by Andrew Strickler",
    '010754': f"article about Yitzhak Rabin in U.S. News 2015-11-04",
    '024256': f'article by {JOI_ITO}: "Internet & Society: The Technologies and Politics of Control',
    '027004': f'article by {JOSCHA_BACH}: "The Computational Structure of Mental Representation" 2013-02-26',
    '019212': f'article in The Times Tribune and WaPo about Bannon, Trump, and healthcare execs',
    '015501': f'article on "Game Theory and Morality" by Moshe Hoffman, Erez Yoeli, Carlos David Navarrete',
    '030013': f'Aviation International News article 2012-07',
    '013275': f"Bloomberg article on notable 2013 obituaries 2013-12-26",
    '023571': f'China Daily front page articles about terrorism, Macau, trade initiatives 2016-09-18',
    '023570': f'China Daily articles about Belt & Road in Central/South America, Xi philosophy 2017-05-14',
    '025115': f'China Daily opinion page 2017-05-14',
    '026868': f'CNN "Quest Means Business New Tariffs — Trade War" by {ROBERT_LAWRENCE_KUHN} 2018-09-18',
    '019468': f"Daily Mail article on Epstein and Clinton",
    '031186': f'Daily News article about rape of 13 year old accusations against Trump 2016-11-02',
    '030199': f'article about Trump rape of 13 year old accusations 2017-11-16',
    '033468': f'draft of article about Rod Rosenstein 2018-09-24 (roughly)',
    '030825': f'draft of article about Syria',
    '030258': f'draft of an article about Mueller probe, almost same as 030248',
    '030248': f'draft of an article about Mueller probe, almost same as 030258',
    '029165': f'draft of an article about Mueller probe, almost same as 030258',
    '026761': f'Forbes article "Swedish American Group Focuses On Cancer" about {BARBRO_EHNBOM}',
    '031716': f'Fortune Magazine article by {TOM_BARRACK} 2016-10-22',
    '019233': f'Freedom House: "Breaking Down Democracy: Goals, Strategies, and Methods of Modern Authoritarians" 2017-06',
    '019444': f'Frontlines magazine article "Biologists Dig Deeper" 2008-01-01',
    '027051': f"German language article about Lifeball / AIDS Gala 2012",
    '021094': f"Globe and Mail article about Gerd Heindrich from 2007",
    '013268': f"JetGala article about airplane interior designer {ERIC_ROTH}",
    '014037': f"Journal of Criminal Law and Criminology article on {CVRA}",
    '029865': f"LA Times front page article about {DEEPAK_CHOPRA} and young Iranians 2016-11-05",
    '013403': f"Lexis Nexis result from The Evening Standard about Bernie Madoff",
    '023102': f"Litigation Daily article about {REID_WEINGARTEN} 2015-09-04",
    '015462': f'magazine (?) issue: Nautilus Education',
    '029416': f'National Enquirer FOIA filing',
    '029925': f"New Yorker article about the placebo effect by Michael Specter 2011-12-04",
    '033181': f'NYT "Donald Trump Used Legally Dubious Method to Avoid Paying Taxes" 2016-10-31',
    '031972': f"NYT article about #MeToo allegations against {LAWRENCE_KRAUSS} 2018-03-07",
    '033479': f"NYT article about Rex Tillerson 2010-03-14",
    '019439': f"NYT column by Maureen Dowd 2013-08-17",
    '033365': f'NYT column by Kevin Rudd "Trump Hands China An Easy Win in the Trade War"',
    '021093': f"page of an article about Epstein and Maxwell",
    '013435': f"Palm Beach Daily News article about Epstein address book 2011-03-11",
    '013440': f"Palm Beach Daily News article about Epstein gag order 2011-07-13",
    '015028': f"Palm Beach Post article about reopening Epstein's criminal case",
    '028481': f'photo of NYT article about Steve Bannon 2018-03-09',
    '033480': f"press clipping about John Bolton 2018-04-06",
    '033481': f"press clipping about John Bolton",
    '031794': f"press clipping in French",
    '033323': f'{ROBERT_TRIVERS} and Nathan H. Lents "Does Trump Fit the Evolutionary Role of Narcissistic Sociopath?" (draft) 2018-12-07',
    '025328': f"scan of NYT page with articles about radio host Bob Fass and Robert Durst",
    '016996': f'SciencExpress article "Quantitative Analysis of Culture Using Millions of Digitized Books" by Jean-Baptiste Michel',
    '025104': f"SCMP article about China and globalisation",
    '030829': f'South Florida Sun Sentinel article about {BRAD_EDWARDS} and {JEFFREY_EPSTEIN}',
    '026520': f'Spanish language article about {SULTAN_BIN_SULAYEM} 2013-09-27',
    '021092': f'Tatler page about {GHISLAINE_MAXWELL} shredding documents 2019-08-15',
    '013437': f"The Telegraph article about Epstein diary 2011-03-05",
    '031736': f'translation of Arabic article by Abdulnaser Salamah "Trump; Prince of Believers (Caliph)!" 2017-05-13',
    '025094': f'translation of Spanish article about Cuba 2015-11-08',
    '017771': f'Vanity Fair article "The Talented Mr. Epstein" by Vicky Ward 2011-06-27',
    '031171': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-06",
    '023048': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-27",
    '023046': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-27",
    '031170': f"{VI_DAILY_NEWS_ARTICLE} 2019-03-06",
    '016506': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-28",
    '033379': f'WaPo "How Washington Pivoted From Finger-Wagging to Appeasement" about Viktor Orban 2018-05-25',
    '031396': f'WaPo "A Justice Dept. discipline office with limited reach to probe handling of controversial sex abuse case" 2019-02-06',
    '019206': f"WSJ article about Edward Snowden by {EDWARD_EPSTEIN} 2016-12-30",
    # court docs
    '010723': KEN_STARR_LETTER,
    '010732': KEN_STARR_LETTER,
    '012135': KEN_STARR_LETTER,
    '025704': KEN_STARR_LETTER,
    '025353': KEN_STARR_LETTER,
    '019224': KEN_STARR_LETTER,
    '019221': KEN_STARR_LETTER,
    '012130': f"{KEN_STARR_LETTER} 2008-06-19",
    '010757': VIRGINIA_FILING,
    '015529': VIRGINIA_FILING,
    '014118': VIRGINIA_FILING,
    '025939': f'affidavit of Jane Doe describing being raped by Epstein',
    '010735': f"court filing by {ALAN_DERSHOWITZ} in {JANE_DOE_V_USA}",
    '010887': f"court filing in {EDWARDS_V_DERSHOWITZ}",
    '015590': f"court filing in {EDWARDS_V_DERSHOWITZ} 2016-02-03",
    '015650': f"court filing in {EDWARDS_V_DERSHOWITZ} 2016-02-08",
    '010566': f"court filing in {EPSTEIN_V_EDWARDS}",
    '017488': f"court filing in {EPSTEIN_V_EDWARDS}",
    '012103': f"court filing in {EPSTEIN_V_EDWARDS} 2011-05-17",
    '032321': f"court filing in Jane Doe v. Donald Trump and {JEFFREY_EPSTEIN}",
    '013489': f'court filing in Jane Doe v. Epstein filed by {BRAD_EDWARDS} 2010-07-20',
    '014084': f"court filing in Jane Doe #1 and Jane Doe #2 v. United States",
    '011908': f"court filing in {JEAN_LUC_BRUNEL} v. {JEFFREY_EPSTEIN} and Tyler McDonald d/b/a YI.org",
    '017935': f"court filing in Virginia Giuffre v. {ALAN_DERSHOWITZ}",
    '014652': f"court filing complaint in {GIUFFRE_V_MAXWELL} 2015-04-22",
    '011304': f"court filing transcript of hearing in {GIUFFRE_V_MAXWELL} 2017-03-17",
    '011463': f"court filing in {GIUFFRE_V_MAXWELL} 2017-03-17",
    '014788': f"court filing in {GIUFFRE_V_MAXWELL} 2017-03-17",
    '014797': f"court filing in {GIUFFRE_V_MAXWELL} 2017-03-17",
    '016420': f"court filing in N.Y. v. {JEFFREY_EPSTEIN} 2019-01-11",
    '017767': f"court exhibit of article about {ALAN_DERSHOWITZ} working with {JEFFREY_EPSTEIN}",
    '017796': f"court exhibit of article about {ALAN_DERSHOWITZ}",
    '017818': f"court exhibit of article about {ALAN_DERSHOWITZ} by Julie K. Brown (Miami Herald) 2018-12-27",
    '017800': f'court exhibit of "Perversion of Justice" by Julie K. Brown (Miami Herald)',
    '013463': f'deposition of Scott Rothstein in Jane Doe v. Epstein filed by {BRAD_EDWARDS} 2010-03-23',
    '018872': f"FBI seized property inventory (redacted)",
    '019352': f"FBI report on Epstein investigation (redacted)",
    '021434': f"FBI report on Epstein investigation (redacted)",
    '017904': f"laws and court filing regarding lawsuit against Saudi Arabia for 9/11?",
    '023361': f"laws and court filing regarding lawsuit against Saudi Arabia for 9/11?",
    '017830': f"laws and court filing regarding lawsuit against Saudi Arabia for 9/11?",
    '012197': f"letter from DOJ to {JAY_LEFKOWITZ} about Epstein's prosecution agreement",
    '010560': f"letter from Gloria Allred to {SCOTT_J_LINK} alleging abuse of a girl from Kansas 2019-06-19",
    '019297': f'letter from {ALAN_DERSHOWITZ} lawyer Andrew G. Celli about {GIUFFRE_V_MAXWELL} 2018-02-07',
    '031447': f"letter from {MARTIN_WEINBERG} to Melanie Ann Pustay and Sean O'Neill re: an Epstein FOIA request",
    '029315': f"letter from {JACK_SCAROLA} about {EPSTEIN_V_EDWARDS}",
    '012707': f"letter from {JACK_SCAROLA} about {EPSTEIN_V_EDWARDS} with Master Contact List",
    '026793': f"letter from {STEVEN_HOFFENBERG}'s lawyer Alan P. Fraade offering to take over Epstein's business and resolve his legal issues",
    '020662': f"letter to Daily Mail threatening libel lawsuit from {ALAN_DERSHOWITZ}'s British lawyers Mishcon de Reya",
    '017603': f"Lexis Nexis search for case law around the {CVRA} by {DAVID_SCHOEN} 2019-02-28",
    '017635': f"Lexis Nexis search for case law around the {CVRA} by {DAVID_SCHOEN} 2019-02-28",
    '016509': f"Lexis Nexis search for case law around the {CVRA} by {DAVID_SCHOEN} 2019-02-28",
    '017714': f"Lexis Nexis search for case law around the {CVRA} by {DAVID_SCHOEN} 2019-02-28",
    '013304': f"motion filed in response to Epstein's lawsuit against {BRAD_EDWARDS}",
    '022237': f"partial court filing involving {ALAN_DERSHOWITZ} and Virginia Giuffre with fact checking questions?",
    '016197': f"response to Florida Bar complaint by {ALAN_DERSHOWITZ} about David Boies from Paul Cassell",
    '028540': f"Supreme Court decision in Budha Ismail Jam et al. v. INTERNATIONAL FINANCE CORP",
    '021824': f"transcript of deposition of Paul Cassell in {EDWARDS_V_DERSHOWITZ}",
    # conferences
    '014951': f"2017 TED Talks program 2017-04-20",
    '017524': f'{BARBRO_EHNBOM} Swedish American Life Science Summit 2012 program',
    '023069': f'BofA / Merrill Lynch 2016 Future of Financials Conference report',
    '014315': f'BofA / Merrill Lynch 2016 Future of Financials Conference report',
    '017526': f'Intellectual Jazz conference brochure',
    '023121': f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' potential invitees f. Johnny Depp, Woody Allen, Obama, and more",
    '031359': f"Nobel Charitable Trust Earth Environment Convention about ESG investing",
    '031354': f'Nobel Charitable Trust "Thinking About the Environment and Technology" report 2011',
    '024185': f'schedule of 67th U.N. General Assembly w/"Presidents Private Dinner - Jeffrey Epstine (sic)" 2012-09-21',
    '024179': f'president and first lady schedule at 67th U.N. General Assembly 2012-09-21',
    '025797': f'someone\'s notes from Aspen Strategy Group 2013-05-29 (?)',
    '017060': f'World Economic Forum (WEF) Annual Meeting 2011 List of Participants 2011-01-18',
    # press releases, reports, etc.
    '024631': f"Ackrell Capital Cannabis Investment Report 2018",
    '014697': f'ASU Origins Project ({LAWRENCE_KRAUSS}) report "Challenges of AI: Envisioning and Addressing Adverse Outcomes"',
    '011284': f'ASU Origins Project ({LAWRENCE_KRAUSS}) report "Challenges of AI: Envisioning and Addressing Adverse Outcomes"',
    '016111': f'BofA / Merrill Lynch 2016-06-30 "GEMs Paper #26 Saudi Arabia: beyond oil but not so fast"',
    '025978': f'BofA / Merrill Lynch 2016-08-09 "Understanding when risk parity risk Increases"',
    '010609': f'BofA / Merrill Lynch 2016-09-22 "Liquid Insight Trump\'s effect on MXN"',
    '014404': f'BofA / Merrill Lynch 2016-11-18 Japan Investment Strategy Report',
    '014410': f'BofA / Merrill Lynch 2016-11-18 Japan Investment Strategy Report',
    '014424': f'BofA / Merrill Lynch 2016-11-14 report "Japan Macro Watch"',
    '014731': f'BofA / Merrill Lynch 2016-11-16 report "Global Rates, FX & EM 2017 Year Ahead',
    '014432': f'BofA / Merrill Lynch 2016-11-30 report "Global Cross Asset Strategy - Year Ahead The Trump inflection"',
    '014460': f'BofA / Merrill Lynch 2016-12-01 report "European Equity Strategy 2017"',
    '014972': f'BofA / Merrill Lynch 2017 report "Global Equity Volatility Insights"',
    '014622': f'BofA / Merrill Lynch 2017-01-03 report "Top 10 US Ideas Quarterly"',
    '014721': f'BofA / Merrill Lynch 2017-02-13 report "Cause and Effect Fade the Trump risk premium',
    '014887': f'BofA / Merrill Lynch 2017-04-06 report "Internet / e-Commerce"',
    '014873': f'BofA / Merrill Lynch 2017-04-11 report "Hess Corp"',
    '023575': f'BofA / Merrill Lynch 2017-06 report "Global Equity Volatility Insights"',
    '029438': f'BofA Wealth Management 2018-01-02 tax report',
    '024271': f"Brock Pierce's Blockchain Capital presentation Oct 2015",
    '024302': f"Carvana form 14A SEC filing proxy statement 2019-04-23",
    '029305': f"CCH Tax Briefing on end of Defense of Marriage Act",
    '024817': f"Cowen's Collective View of CBD / Cannabis report",
    '026794': f'Deutsche Bank Global Public Affairs report: "Global Political and Regulatory Risk in 2015/2016"',
    '022361': f'Deutsche Bank Wealth Management Tax Topics 2013-05',
    '022325': f'Deutsche Bank Wealth Management Tax Topics 2013-12-20',
    '022330': f'Deutsche Bank Wealth Management Tax Topics 2013-12-20 TOC',
    '019440': f'Deutsche Bank Wealth Management Tax Topics 2014-01-29',
    '022494': f'DOJ Resource Guide to the U.S. Foreign Corrupt Practices Act (FCPA)',
    '024202': f'Electron Capital Partners LLC "Global Utility White Paper" 2013-03-08',
    '022372': f'Ernst & Young 2016 election report',
    '025663': f'Goldman Sachs 2017-11 report "An Overview of the Current State of Cryptocurrencies and Blockchain"',
    '014532': f'Goldman Sachs Investment Management Division 2017-01-01 report "Outlook - Half Full"',
    '026909': f'Goldman Sachs Investment Management Division 2018-10-14 report "The Unsteady Undertow Commands the Seas (Temporarily)"',
    '026944': f'Goldman Sachs Investment Management Division 2019-05-23 report "Risk of a US-Iran Military Conflict and Other Geopolitical Risks"',
    '026679': f'Invesco report: "Global Sovereign Asset Management Study 2017"',
    '023096': f'Jeffrey Epstein VI Foundation blog 2012-11-15',
    '029326': f'Jeffrey Epstein VI Foundation press release 2013-02-15',
    '026565': f'Jeffrey Epstein VI Foundation press release 2013-02-15 (draft of 029326?)',
    '026572': f"JP Morgan Global Asset Allocation report dated 2012-11-09",
    '030848': f"JP Morgan Global Asset Allocation report dated 2013-03-28",
    '030840': f"JP Morgan Market Thoughts 2012-11",
    '022350': f"JP Morgan report on tax efficiency of Intentionally Defective Grantor Trusts (IDGT)",
    '025242': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-04-09",
    '030010': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-06-14",
    '030808': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-07-11",
    '025221': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-07-25",
    '025229': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-08-04",
    '030814': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-11-21",
    '024132': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2012-03-15",
    '025242': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2012-04-09",
    '024194': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2012-10-22",
    '025296': f'Laffer Associates report from 2016-07 predicting Trump win',
    '025551': f'Morgan Stanley report about alternative asset managers 2018-01-30',
    '026759': f'press release by Ritz-Carlton club about damage from Hurricane Irma 2017-09-13',
    '033338': f"press release announcing Donald Trump & {NICHOLAS_RIBIS} ended their working relationship at Trump's casino 2000-06-07",
    '012048': f'press release "Rockefeller Partners with Gregory J. Fleming to Create Independent Financial Services Firm" and other articles',
    '020447': f'Promoting Constructive Vigilance: Report of the Working Group on Chinese Influence Activities in the U.S. (Hoover Group/Stanford 2018)',
    '025763': f'S&P Economic Research: "How Increasing Income Inequality Is Dampening U.S. Growth" 2014-08-05',
    '019856': f"Sadis Goldberg LLP report on SCOTUS ruling about insider trading",
    '026827': f'Scowcroft Group report on ISIS 2015-11-14',
    '033220': f"short economic report on defense spending under Trump by Joseph G. Carson",
    '026856': f'speech by former Australian PM Kevin Rudd "Xi Jinping, China And The Global Order" from 2018-06-26',
    '023133': f'"The Search for Peace in the Arab-Israeli Conflict" edited by {TERJE_ROD_LARSEN}, Nur Laiq, Fabrice Aidan 2019-12-09',
    '025247': f'UBS CIO Monthly Extended report 2012-10-25',
    '024135': f'UBS CIO Monthly Extended report 2012-06-29',
    '025849': f'US Office of Government Information Services report: "Building a Bridge Between FOIA Requesters & Agencies"',
    '020824': f"USA Inc: A Basic Summary of America's Financial Statements compiled by Mary Meeker 2011-02-01",
    # letters
    '017789': f'{ALAN_DERSHOWITZ} letter to Harvard Crimson complaining he was defamed',
    '028928': WEINBERG_ABC_LETTER,
    '028965': WEINBERG_ABC_LETTER,
    '022405': f"letter from {NOAM_CHOMSKY} attesting to Epstein's good character",
    '031670': f"letter from General Mike Flynn's lawyers to senators Mark Warner & Richard Burr about subpoena",
    '019086': f"letter from David Blaine recommending visa approval for a Russian model 'Svet' (Svetlana Pozhidaeva?) naming Putin puppets",
    '019474': f"letter from David Blaine recommending visa approval for a model 2015-05-29",
    '019476': f"letter from David Blaine recommending visa approval for a model 2015-06-01",
    '026011': f"letter to Epstein about trading algorithm from Gennady Mashtalyar",
    '026134': f'letter to someone named George about investment opportunities in the Ukraine banking sector',
    # private placement memoranda
    '024432': f"Michael Milken's Knowledge Universe Education (KUE) $1,000,000 corporate share placement notice (SEC filing?)",
    '024003': f"New Leaf Ventures private placement memorandum",
    # property
    '018804': f"appraisal of going concern for IGY American Yacht Harbor Marina in Virgin Islands",
    '016597': f'letter from Trump Properties LLC appealing decision about Mar-a-Lago',
    '016602': f"Palm Beach code enforcement board minutes 2008-04-17",
    '016616': f"Palm Beach code enforcement board minutes 2008-07-17",
    '016554': f"Palm Beach code enforcement board minutes 2008-07-17",
    '016574': f"Palm Beach code enforcement board minutes 2008-07-17",
    '016636': f"Palm Beach Water Committee Meeting on January 29, 2009",
    '016696': f"Palm Beach water quality report",
    '018727': f"property deal in Virgin Islands for a building that will be leased to the U.S. Govt (GSA)",
    '018743': f"property listing in Las Vegas",
    '027068': f"The Real Deal article by Keith Larsen 2018-10-11",
    '029520': f'The Real Deal article by Keith Larsen "Lost Paradise at the Palm House" 2019-06-17',
    '016552': f"TSV of Palm Beach property information",
    '016599': f"TSV of Palm Beach property consumption (water?)",
    '016600': f"TSV of Palm Beach property consumption (water?)",
    '016601': f"TSV of Palm Beach property consumption (water?)",
    '016694': f"TSV of Palm Beach property consumption (water?)",
    '016698': f"TSV of Palm Beach property info (broken?)",
    # misc
    '029102': HBS_APPLICATION_NERIO,
    '029104': HBS_APPLICATION_NERIO,
    '018703': f"Andres Serrano artists statement about Trump objects",
    '028281': f'art show flier for "The House Of The Nobleman" curated by Wolfe Von Lenkiewicz & Victoria Golembiovskaya',
    '025147': f'Brockman book hot list Frankfurt Book Fair 2016 (has article about Silk Road / Ross Ulbricht)',
    '012718': f"congressional record from 2011-06-17 about {CVRA}",
    '018224': f"conversation with {LAWRENCE_KRAUSS}?",
    '029918': f'Diana DeGette (Colorado legislator) campaign profile presser 2012-01-01 (roughly)',
    '010617': f"Donald Trump financial disclosures from U.S. Office of Government Ethics 2017-01-20",
    '016699': f"Donald Trump financial disclosures from U.S. Office of Government Ethics 2017-01-20",
    '025540': f"Epstein's rough draft of 'his side' of the story?",
    '024117': f"FAQ about anti-money laundering and terrorist financing law in the U.S.",
    '031743': f'a few pages describing the internet as a "New Nation State" (Network State?)',
    '022780': f'flight logs',
    '019396': f'Harvard Economics 1545 Professor Kenneth Rogoff syllabus',
    '029517': HARVARD_POETRY,
    '029543': HARVARD_POETRY,
    '029589': HARVARD_POETRY,
    '029589': HARVARD_POETRY,
    '029603': HARVARD_POETRY,
    '033434': f"iMessage screenshot labeled 'Edwards' at the top",
    '029564': OBAMA_JOKE,
    '029353': OBAMA_JOKE,
    '029352': OBAMA_JOKE,
    '029351': OBAMA_JOKE,
    '022445': f"Inference: International Review of Science Feedback & Comments November 2018",
    '028815': f'InsightsPod business plan',
    '033478': f'meme showing Kim Jong Un reading "Fire And Fury" by {MICHAEL_WOLFF}',
    '025205': f'Mercury Films partner profiles of Jennifer Baichwal, Nicholas de Pencier, Kermit Blackwood, Travis Rummel',
    '030426': f'Osborne & Partners reputation management proposal (cites Michael Milken) 2011-06-14',
    '022417': f"Park Partners NYC letter to partners in real estate project with architectural plans",
    '026851': f"Politifact lying politicians chart 2016-07-26",
    '022367': f"professional resumé of Jack J Grynberg 2014-07",
    '029302': f"professional resumé of Michael J. Boccio 2011-08 (roughly)",
    '015671': f"professional resumé of Robin Solomon",
    '015672': f"professional resumé of Robin Solomon",
    '019448': f"proposal for Jacmel, Haiti business investment",
    '030142': f"mostly empty Saudi Arabian proposal for JASTA f. {KATHRYN_RUEMMLER} and {KEN_STARR}",
    '029328': f"Rafanelli Events promotional deck",
    '023666': f"{ROBERT_LAWRENCE_KUHN} sizzle reel / television appearances",
    '022213': f'screenshot of Facebook discussion in Shit Pilots Say disparaging a "global girl"',
    '029356': f'screenshot of quote in book about {LARRY_SUMMERS}',
    '029357': f"some text about Israel's challenges going into 2015",
    '022277': f"text of America's National Labour Relationsh Board (NLRB) law",
    '023644': f"transcription of an interview with MBS from Saudi 2016-04-25",
    '030884': f"tweet by Ed Krassenstein",
    '023050': f"tweet by {ALAN_DERSHOWITZ} about Virginia Giuffre",
    '017787': f"tweet by {ALAN_DERSHOWITZ} about Virginia Giuffre",
    '033433': f"tweet by {ALAN_DERSHOWITZ} about Virginia Giuffre / David Boies 2019-03-02",
    '033432': f"tweet by {ALAN_DERSHOWITZ} about Virginia Giuffre / David Boies 2019-05-02",
    '031546': f"tweets by Donald Trump about Russian collusion 2018-01-06",
    '011170': f'tweets about #Brexit collected by InsightsPod 2016-06-23',
    '033236': f'tweets about Ivanka Trump in Arabic 2017-05-20',
    '029475': f'Virgin Islands Twin City Mobile Integrated Health Services (TCMIH) proposal (donation request?)',
    '029448': f'weird short essay about Obama',
    '032281': f"{ZUBAIR_KHAN} forecasting election for Trump 2016-10-25 (roughly)",
}
