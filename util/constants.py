import csv
import re
from io import StringIO

# Email Names
AL_SECKEL = 'Al Seckel'
ALIREZA_ITTIHADIEH = 'Alireza Ittihadieh'
ARIANE_DE_ROTHSCHILD = 'Ariane de Rothschild'
BARBRO_EHNBOM = 'Barbro Ehnbom'
BENNET_MOSKOWITZ = 'Bennet Moskowitz'
DARREN_INDYKE = 'Darren Indyke'
DANIEL_SIAD = 'Daniel Siad'
DAVID_SCHOEN = 'David Schoen'
DAVID_STERN = 'David Stern'
DONALD_TRUMP = 'Donald Trump'
EDWARD_EPSTEIN = 'Edward Epstein'
EHUD_BARAK = 'Ehud Barak'
GERALD_BARTON = 'Gerald Barton'
GHISLAINE_MAXWELL = 'Ghislaine Maxwell'
GWENDOLYN_BECK = 'Gwendolyn Beck'
JEAN_HUGUEN = 'Jean Huguen'
JEAN_LUC_BRUNEL = 'Jean Luc Brunel'
JABOR_Y = 'Jabor Y.'   # Qatari
JEREMY_RUBIN = 'Jeremy Rubin'  # bitcoin dev
JOHN_PAGE = 'John Page'
JOHNNY_EL_HACHEM = 'Johnny el Hachem'
JONATHAN_FARKAS = 'Jonathan Farkas'
KATHY_RUEMMLER = 'Kathy Ruemmler'
LANDON_THOMAS = 'Landon Thomas Jr.'
LAWRANCE_VISOSKI = 'Lawrance Visoski'
LAWRENCE_KRAUSS = 'Lawrence Krauss'
LEON_BLACK = 'Leon Black'
LESLEY_GROFF = 'Lesley Groff'
LISA_NEW = 'Lisa New'          # Harvard poetry prof AKA "Elisa New"
MARTIN_NOWAK = 'Martin Nowak'
MELANIE_SPINELLA = 'Melanie Spinella'
NADIA_MARCINKO = 'Nadia Marcinko'
PEGGY_SIEGAL = 'Peggy Siegal'
PAUL_KRASSNER = 'Paul Krassner'
ROBERT_TRIVERS = 'Robert Trivers'
SULTAN_BIN_SULAYEM = 'Sultan Bin Sulayem'
TERRY_KAFKA = 'Terry Kafka'
THORBJORN_JAGLAND = 'Thorbjørn Jagland'
TONJA_HADDAD_COLEMAN = 'Tonja Haddad Coleman'
REDACTED = '[REDACTED]'

# Texting Names
ANIL = "Anil Ambani"
DEFAULT = 'default'
EVA = 'Eva'
JEFFREY_EPSTEIN = 'Jeffrey Epstein'
JOI_ITO = 'Joi Ito'
LARRY_SUMMERS = 'Larry Summers'
MELANIE_WALKER = 'Melanie Walker'
MIROSLAV = 'Miroslav Lajčák'
PLASKETT = 'Stacey Plaskett'
SCARAMUCCI = 'The Mooch'
SOON_YI = 'Soon-Yi Previn'
STEVE_BANNON = 'Steve Bannon'
TERJE = 'Terje Rød-Larsen'
UNKNOWN = '(unknown)'

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
HOUSE_OVERSIGHT_027460.txt	Steve Bannon	Trump and New York Times coverage
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
    '031042': ANIL,            # Participants: field
    '027225': ANIL,            # Birthday
    '031173': 'Ards',          # Participants: field, possibly incomplete
    '025707': STEVE_BANNON,
    '025734': STEVE_BANNON,
    '025452': STEVE_BANNON,
    '025408': STEVE_BANNON,
    '027307': STEVE_BANNON,
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

GUESSED_IMESSAGE_FILE_IDS = {
    '027221': ANIL,
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
    file_id = row['filename'].strip().replace('HOUSE_OVERSIGHT_', '').replace('.txt', '')
    counterparty = row['counterparty'].strip()

    if file_id in GUESSED_IMESSAGE_FILE_IDS:
        raise RuntimeError(f"Can't overwrite attribution of {file_id} to {GUESSED_IMESSAGE_FILE_IDS[file_id]} with {counterparty}")

    GUESSED_IMESSAGE_FILE_IDS[file_id] = counterparty.replace(' (likely)', '').strip()


# If found as substring consider them the author
EMAILERS = [
    'Anne Boyles',
    AL_SECKEL,
    'Bill Gates',
    'Bill Siegel',
    'Daniel Sabba',
    'Glenn Dubin',
    'Gordon Getty',
    'Jessica Cadwell',
    JOHN_PAGE,
    'Jokeland',
    'Jes Staley',
    'Kathleen Ruderman',
    'Kenneth E. Mapp',
    'Joscha Bach',
    'Lesley Groff',
    'Brad Wechsler',
    'middle.east.update@hotmail.com',
    'Mark L. Epstein',
    MELANIE_WALKER,
    'Michael Simmons',  # Not the only "To:"
    'Multiple Senders',  # Weird files like HOUSE_OVERSIGHT_032210
    'Nancy Cain',
    'Nancy Portland',
    'Oliver Goodenough',
    'Peter Aldhous',
    'Peter Green',
    'Sam/Walli Leff',
    'Steven Victor MD',
    'The Duke',
    'Tom Barrack',
    'Weingarten, Reid',
]

EMAILER_REGEXES = {
    'Alan Dershowitz': re.compile(r'alan.*dershowitz', re.IGNORECASE),
    ALIREZA_ITTIHADIEH: re.compile(r'Alireza.[Il]ttihadieh', re.IGNORECASE),
    'Amanda Ens': re.compile(r'ens, amand', re.IGNORECASE),
    ANIL: re.compile(r'Anil.Ambani', re.IGNORECASE),
    ARIANE_DE_ROTHSCHILD: re.compile(r'^(AdeR|Ariane de Roth)$'),
    'Anas Alrasheed': re.compile(r'anas\s*al\s*rashee[cd]', re.IGNORECASE),
    BARBRO_EHNBOM: re.compile(r'behnbom@aol.com|Barbro\s.*Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen?', re.IGNORECASE),
    BENNET_MOSKOWITZ: re.compile(r'Moskowitz.*Bennet|Bennet.*Moskowitz', re.IGNORECASE),
    'Boris Nikolic': re.compile(r'boris nikoli', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterpris', re.IGNORECASE),
    DARREN_INDYKE: re.compile(r'^darren$|darren [il]ndyke?|dkiesq', re.IGNORECASE),
    DAVID_STERN: re.compile(r'David Stern?', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    'Faith Kates': re.compile(r'faith kate', re.IGNORECASE),
    GERALD_BARTON: re.compile(r'Gerald.*Barton', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?', re.IGNORECASE),
    'Google Alerts': re.compile(r'google\s?alerts', re.IGNORECASE),
    'Heather Mann': re.compile(r'Heather Man', re.IGNORECASE),
    'Intelligence Squared': re.compile(r'intelligence\s*squared', re.IGNORECASE),
    'jackie perczel':  re.compile(r'jackie percze', re.IGNORECASE),
    JABOR_Y: re.compile(r'^[ji]abor\s*y', re.IGNORECASE),
    JEAN_LUC_BRUNEL: re.compile(r'Jean[- ]Luc Brunel?', re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'[djl]ee[vy]acation[©@]?|jeffrey E\.|Jeffrey Epstein?', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|joichi|^joi$', re.IGNORECASE),
    JOHNNY_EL_HACHEM: re.compile('el hachem johnny|johnny el hachem', re.IGNORECASE),
    JONATHAN_FARKAS: re.compile('Jonathan Farka(s|il)', re.IGNORECASE),
    KATHY_RUEMMLER: re.compile(r'Kathy Ruemmle', re.IGNORECASE),
    'Ken Starr': re.compile('starr, ken|Ken star', re.IGNORECASE),
    LANDON_THOMAS: re.compile(r'lando[nr] thomas|thomas jr.?, lando[nr]', re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r'La(wrence|rry).*Summer|^LH$|^LHS|Ihsofficel', re.IGNORECASE),
    LAWRANCE_VISOSKI: re.compile(r'La(rry|wrance) Visosk', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus|lawkrauss', re.IGNORECASE),
    LEON_BLACK: re.compile(r'Leon Blac', re.IGNORECASE),
    'lilly sanchez': re.compile(r'Lilly.*Sanchez', re.IGNORECASE),
    LISA_NEW: re.compile(r'Lisa New?$', re.IGNORECASE),
    'Marc Leon': re.compile(r'Marc[.]+(Kensington|Leon)|Kensington2', re.IGNORECASE),
    'Martin Weinberg': re.compile(r'martin.*?weinberg', re.IGNORECASE),
    MARTIN_NOWAK: re.compile(r'Martin.*?Nowak|Nowak, Martin', re.IGNORECASE),
    MELANIE_SPINELLA: re.compile(r'Melanie Spine[Il]{2}a', re.IGNORECASE),
    'Michael Miller': re.compile(r'Micha(el)? Miller|Miller, Micha(el)?', re.IGNORECASE),
    'Michael Wolff': re.compile(r'Michael\s*Wol(ff|i)', re.IGNORECASE),
    'Mike Sitrick': re.compile(r'Mi(chael|ke).*Sitrick', re.IGNORECASE),
    'Mohamed Waheed Hassan': re.compile(r'Mohamed Waheed', re.IGNORECASE),
    'Neal Kassell': re.compile(r'Neal Kassel', re.IGNORECASE),
    'Nicholas Ribis': re.compile(r'Nicholas[ ._]Rib', re.IGNORECASE),
    'Paul Barrett': re.compile(r'Paul Barre(d|tt)', re.IGNORECASE),
    PAUL_KRASSNER: re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    'Paul Morris': re.compile(r'morris, paul|Paul Morris', re.IGNORECASE),
    PEGGY_SIEGAL:  re.compile(r'Peggy Siega', re.IGNORECASE),
    'Peter Attia': re.compile(r'Peter Atti', re.IGNORECASE),
    'Reid Weingarten': re.compile(r'Weingarten, Rei[cdi]|Rei[cdi] Weingarten', re.IGNORECASE),
    'Richard Kahn': re.compile(r'rich(ard)? kahn?', re.IGNORECASE),
    'Robert Lawrence Kuhn': re.compile(r'Robert\s*(Lawrence)?\s*Kuhn', re.IGNORECASE),
    ROBERT_TRIVERS: re.compile(r'tri[vy]ersr@gmail|Robert\s*Trivers?', re.IGNORECASE),
    'Scott J. Link': re.compile(r'scott j. lin', re.IGNORECASE),
    'Sean Bannon': re.compile(r'sean banno', re.IGNORECASE),
    'Shaher Abdulhak Besher (?)': re.compile(r'^Shaher$', re.IGNORECASE),
    SOON_YI: re.compile(r'Soon[- ]Yi Previn?', re.IGNORECASE),
    'Stephen Hanson': re.compile(r'ste(phen|ve) hanson?|Shanson900', re.IGNORECASE),
    STEVE_BANNON: re.compile(r'steve banno[nr]?', re.IGNORECASE),
    'Steven Sinofsky': re.compile(r'Steven Sinofsk', re.IGNORECASE),
    SULTAN_BIN_SULAYEM: re.compile(r'Sultan bin Sulay', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r'Terry Kafk', re.IGNORECASE),
    THORBJORN_JAGLAND: re.compile(r'Thor.*Jag[il]and?', re.IGNORECASE),
    TONJA_HADDAD_COLEMAN: re.compile(fr"To(nj|rl)a Haddad Coleman|haddadfm@aol.com", re.IGNORECASE)
}

for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer, re.IGNORECASE)


KNOWN_EMAIL_AUTHORS = {
    '032436': 'Alireza Ittihadieh',  # Signature
    '026064': ARIANE_DE_ROTHSCHILD,
    '026069': ARIANE_DE_ROTHSCHILD,
    '030741': ARIANE_DE_ROTHSCHILD,
    '026018': ARIANE_DE_ROTHSCHILD,
    '026659': BARBRO_EHNBOM,      # Reply
    '026745': BARBRO_EHNBOM,      # Signature
    '031227': BENNET_MOSKOWITZ,
    '031442': 'Christina Galbraith',
    '026625': DARREN_INDYKE,
    '026290': DAVID_SCHOEN,       # Signature
    '031339': DAVID_SCHOEN,       # Signature
    '031492': DAVID_SCHOEN,       # Signature
    '031560': DAVID_SCHOEN,       # Signature
    '026287': DAVID_SCHOEN,       # Signature
    '033419': DAVID_SCHOEN,       # Sent by AOL
    '031460': EDWARD_EPSTEIN,
    '026547': GERALD_BARTON,
    '029969': GWENDOLYN_BECK,     # Signature
    '031120': GWENDOLYN_BECK,     # Signature
    '029968': GWENDOLYN_BECK,     # Signature
    '029970': GWENDOLYN_BECK,
    '029960': GWENDOLYN_BECK,     # Reply
    '029959': GWENDOLYN_BECK,     # "Longevity & Aging"
    '033384': 'Jack Goldberger',     # Might be Paul Prosperi?
    '026024': JEAN_HUGUEN,
    '026024': JEAN_HUGUEN,        # Signature
    '021823': JEAN_LUC_BRUNEL,    # Reply
    '031826': JEFFREY_EPSTEIN,
    '030997': JEFFREY_EPSTEIN,
    '029779': JEFFREY_EPSTEIN,
    '022949': JEFFREY_EPSTEIN,
    '028770': JEFFREY_EPSTEIN,
    '029692': JEFFREY_EPSTEIN,
    '031624': JEFFREY_EPSTEIN,
    '030768': JEFFREY_EPSTEIN,
    '031996': JEFFREY_EPSTEIN,
    '022938': JEFFREY_EPSTEIN,
    '016692': JOHN_PAGE,
    '016693': JOHN_PAGE,
    '028507': JONATHAN_FARKAS,
    '031732': JONATHAN_FARKAS,
    '033484': JONATHAN_FARKAS,
    '033282': JONATHAN_FARKAS,
    '033582': JONATHAN_FARKAS,    # Reply
    '032389': JONATHAN_FARKAS,    # Reply
    '033581': JONATHAN_FARKAS,    # Reply
    '033203': JONATHAN_FARKAS,    # Reply
    '032052': JONATHAN_FARKAS,    # Reply
    '033490': JONATHAN_FARKAS,    # Signature
    '032531': JONATHAN_FARKAS,    # Signature
    '026764': 'Barry J. Cohen',
    '032224': KATHY_RUEMMLER,
    '030478': LANDON_THOMAS,
    '029013': LARRY_SUMMERS,
    '031129': LARRY_SUMMERS,
    '029196': LAWRENCE_KRAUSS,
    '033487': LAWRANCE_VISOSKI,
    '028789': LAWRANCE_VISOSKI,
    '027046': LAWRANCE_VISOSKI,
    '033370': LAWRANCE_VISOSKI,       # Planes discussion signed larry
    '029977': LAWRANCE_VISOSKI,       # Planes discussion signed larry
    '033495': LAWRANCE_VISOSKI,       # Planes discussion signed larry
    '033154': LAWRANCE_VISOSKI,
    '033488': LAWRANCE_VISOSKI,
    '033593': LAWRANCE_VISOSKI,    # Signature
    '017581': 'Lisa Randall',
    '030472': "Martin Weinberg",   # Maybe. in reply
    '030235': MELANIE_WALKER,      # In fwd
    '032212': MIROSLAV,
    '022193': NADIA_MARCINKO,
    '021814': NADIA_MARCINKO,
    '021808': NADIA_MARCINKO,
    '022214': NADIA_MARCINKO,         # Reply header
    '022190': NADIA_MARCINKO,
    '021818': NADIA_MARCINKO,
    '022197': NADIA_MARCINKO,
    '021811': NADIA_MARCINKO,      # Signature and email address in the message
    '026612': 'Norman D. Rau',     # Fwded from "to" address
    '028487': 'Norman D. Rau',     # Fwded from "to" address
    '024923': PAUL_KRASSNER,
    '032457': PAUL_KRASSNER,
    '029981': 'Paula',             # reply
    '033157': 'Paul Prosperi',     # Fwded from "to" address
    '033383': 'Paul Prosperi',     # Reply
    '031694': PEGGY_SIEGAL,
    '032219': PEGGY_SIEGAL,        # Signed "Peggy"
    '029020': 'Renata Bolotova',   # Signature
    '033169': ROBERT_TRIVERS,      # Refs paper
    '033584': ROBERT_TRIVERS,      # Refs paper
    '029003': SOON_YI,
    '029005': SOON_YI,
    '029007': SOON_YI,
    '029010': SOON_YI,
    '032296': SOON_YI,             # Sent from soon-yi's phone
    '026620': TERRY_KAFKA,
    '028482': TERRY_KAFKA,         # Signature
    '029992': TERRY_KAFKA,         # Reply
    '020666': TERRY_KAFKA,         # ends with 'Terry'
    # '026571': '(unknown french speaker)',
    # '029504': Probably Audrey Raimbault (based on "GMI" in signature, a company registered by "aubrey raimbault")
}

KNOWN_EMAIL_RECIPIENTS = {
    '021106': 'Alexandra Preate',     # Reply
    '030764': ARIANE_DE_ROTHSCHILD,   # Reply
    '026431': ARIANE_DE_ROTHSCHILD,   # Reply
    '031996': 'Christina Galbraith',  # bounced
    '026245': 'Diane Ziman',          # Quoted reply
    '026466': 'Diane Ziman',          # Quoted reply
    '031607': EDWARD_EPSTEIN,
    '026426': JEAN_HUGUEN,            # Reply
    '029975': JEAN_LUC_BRUNEL,        # Same as another file
    '022202': JEAN_LUC_BRUNEL,        # Follow up
    '032224': JEFFREY_EPSTEIN,        # Reply
    '033169': JEFFREY_EPSTEIN,
    '033584': JEFFREY_EPSTEIN,
    '033487': JEFFREY_EPSTEIN,
    '033456': 'Joel',                 # Reply
    '033460': 'Joel',                 # Reply
    '030522': LANDON_THOMAS,
    '031413': LANDON_THOMAS,          # Reply
    '029692': LARRY_SUMMERS,          # Header
    '029779': LARRY_SUMMERS,          # Header
    '033591': LAWRANCE_VISOSKI,       # Reply signature
    '033466': LAWRANCE_VISOSKI,       # Reply signature
    '028787': LAWRANCE_VISOSKI,
    '027097': LAWRANCE_VISOSKI,       # Signature of reply
    '022250': LESLEY_GROFF,           # Reply
    '023291': MELANIE_SPINELLA,
    '022258': NADIA_MARCINKO,         # Reply header
    '032951': 'Raafat Alsabbagh',
    '030096': 'Peter Mandelson',
    '019334': STEVE_BANNON,
}

EPSTEIN_SIGNATURE = re.compile(
    r"((\*+|please note)\n)?(> )?(• )?(» )?The information contained in this communication is\n(> )*(» )?confidential.*?all attachments.( copyright -all rights reserved?)?",
    re.DOTALL
)
