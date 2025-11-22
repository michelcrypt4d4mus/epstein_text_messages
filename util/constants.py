import csv
import re
from io import StringIO

# Email Names
AL_SECKEL = 'Al Seckel'
ARIANE_DE_ROTHSCHILD = 'Ariane de Rothschild'
BARBRO_EHNBOM = 'Barbro Ehnbom'
BENNET_MOSKOWITZ = 'Bennet Moskowitz'
DARREN_INDYKE = 'Darren Indyke'
DAVID_SCHOEN = 'David Schoen'
DONALD_TRUMP = 'Donald Trump'
EDWARD_EPSTEIN = 'Edward Epstein'
EHUD_BARAK = 'Ehud Barak'
GHISLAINE_MAXWELL = 'Ghislaine Maxwell'
GWENDOLYN_BECK = 'Gwendolyn Beck'
JEAN_HUGUEN = 'Jean Huguen'
JOHN_PAGE = 'John Page'
JOHNNY_EL_HACHEM = 'Johnny el Hachem'
JONATHAN_FARKAS = 'Jonathan Farkas'
LANDON_THOMAS = 'Landon Thomas Jr.'
LESLEY_GROFF = 'Lesley Groff'
LAWRENCE_KRAUSS = 'Lawrence Krauss'
LAWRANCE_VISOSKI = 'Lawrance Visoski'
LEON_BLACK = 'Leon Black'
NADIA_MARCINKO = 'Nadia Marcinko'
ROBERT_TRIVERS = 'Robert Trivers'
SULTAN_BIN_SULAYEM = 'Sultan Bin Sulayem'
TERRY_KAFKA = 'Terry Kafka'
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
    'Martin Nowak',
    'middle.east.update@hotmail.com',
    JONATHAN_FARKAS,
    'Mark L. Epstein',
    'Nancy Cain',
    'Nancy Portland',
    'Oliver Goodenough',
    'Peggy Siegal',
    'Peter Aldhous',
    'Peter Green',
    'Steven Victor MD',
    'The Duke',
    'Tom Barrack',
    'Weingarten, Reid',
]

EMAILER_REGEXES = {
    'Alan Dershowitz': re.compile(r'alan.*dershowitz', re.IGNORECASE),
    'Amanda Ens': re.compile(r'ens, amand', re.IGNORECASE),
    'Anas Alrasheed': re.compile(r'anas\s*al\s*rasheed', re.IGNORECASE),
    BARBRO_EHNBOM: re.compile(r'behnbom@aol.com|Barbro\s.*Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen?', re.IGNORECASE),
    'Boris Nikolic': re.compile(r'boris nikoli', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterpris', re.IGNORECASE),
    DARREN_INDYKE: re.compile(r'^darren$|darren [il]ndyke|dkiesq', re.IGNORECASE),
    'David Stern': re.compile(r'David Stern?', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    'Faith Kates': re.compile(r'faith kate', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?', re.IGNORECASE),
    'Google Alerts': re.compile(r'google\s?alerts', re.IGNORECASE),
    'Intelligence Squared': re.compile(r'intelligence\s*squared', re.IGNORECASE),
    'jackie perczel':  re.compile(r'jackie percze', re.IGNORECASE),
    'Jabor Y.': re.compile(r'^[ji]abor\s*y', re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'[djl]ee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein?', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|joichi|^joi$', re.IGNORECASE),
    JOHNNY_EL_HACHEM: re.compile('el hachem johnny|johnny el hachem', re.IGNORECASE),
    'Kathy Ruemmler': re.compile(r'Kathy Ruemmle', re.IGNORECASE),
    'Ken Starr': re.compile('starr, ken', re.IGNORECASE),
    LANDON_THOMAS: re.compile('landon thomas|thomas jr.?, landon', re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r'La(wrence|rry).*Summer|^LH$|^LHS', re.IGNORECASE),
    LEON_BLACK: re.compile(r'Leon Blac', re.IGNORECASE),
    'lilly sanchez': re.compile(r'Lilly.*Sanchez', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus', re.IGNORECASE),
    'Lisa New': re.compile(r'Lisa New?$', re.IGNORECASE),
    'Martin Weinberg': re.compile(r'martin.*?weinberg', re.IGNORECASE),
    'Michael Wolff': re.compile(r'Michael\s*Wol(ff|i)', re.IGNORECASE),
    'Mike Sitrick': re.compile(r'Mi(chael|ke).*Sitrick', re.IGNORECASE),
    'Mohamed Waheed Hassan': re.compile(r'Mohamed Waheed', re.IGNORECASE),
    BENNET_MOSKOWITZ: re.compile(r'Moskowitz.*Bennet|Bennet.*Moskowitz', re.IGNORECASE),
    'Nicholas Ribis': re.compile(r'Nicholas Rib', re.IGNORECASE),
    'Paul Krassner': re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    'Paul Morris': re.compile(r'morris, paul|Paul Morris', re.IGNORECASE),
    'Richard Kahn': re.compile(r'rich(ard)? kahn?', re.IGNORECASE),
    'Robert Lawrence Kuhn': re.compile(r'Robert\s*(Lawrence)?\s*Kuhn', re.IGNORECASE),
    ROBERT_TRIVERS: re.compile(r'tri[vy]ersr@gmail|Robert\s*Trivers?', re.IGNORECASE),
    'Scott J. Link': re.compile(r'scott j. lin', re.IGNORECASE),
    'Sean Bannon': re.compile(r'sean banno', re.IGNORECASE),
    SOON_YI: re.compile(r'Soon[- ]Yi Previn?', re.IGNORECASE),
    'Stephen Hanson': re.compile(r'ste(phen|ve) hanson|Shanson900', re.IGNORECASE),
    STEVE_BANNON: re.compile(r'steve banno[nr]?', re.IGNORECASE),
    'Steven Sinofsky': re.compile(r'Steven Sinofsk', re.IGNORECASE),
    SULTAN_BIN_SULAYEM: re.compile(r'Sultan bin Sulay', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r'Terry Kafk', re.IGNORECASE),
}

for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer, re.IGNORECASE)


KNOWN_EMAIL_AUTHORS = {
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
    '031460': EDWARD_EPSTEIN,
    '026547': 'Gerald G. Barton',
    '029969': GWENDOLYN_BECK,     # Signature
    '031120': GWENDOLYN_BECK,     # Signature
    '029968': GWENDOLYN_BECK,     # Signature
    '029970': GWENDOLYN_BECK,
    '029960': GWENDOLYN_BECK,     # Reply
    '029959': GWENDOLYN_BECK,     # "Longevity & Aging"
    '026024': JEAN_HUGUEN,
    '026024': JEAN_HUGUEN,        # Signature
    '030997': JEFFREY_EPSTEIN,
    '029779': JEFFREY_EPSTEIN,
    '022949': JEFFREY_EPSTEIN,
    '028770': JEFFREY_EPSTEIN,
    '029692': JEFFREY_EPSTEIN,
    '031624': JEFFREY_EPSTEIN,
    '030768': JEFFREY_EPSTEIN,
    '016692': JOHN_PAGE,
    '016693': JOHN_PAGE,
    '028507': JONATHAN_FARKAS,
    '031732': JONATHAN_FARKAS,
    '026764': 'Barry J. Cohen',
    '030478': LANDON_THOMAS,
    '029013': LARRY_SUMMERS,
    '031129': LARRY_SUMMERS,
    '029196': LAWRENCE_KRAUSS,
    '028789': LAWRANCE_VISOSKI,
    '027046': LAWRANCE_VISOSKI,
    '017581': 'Lisa Randall',
    '030472': "Martin Weinberg",   # Maybe. in reply
    '030235': MELANIE_WALKER,      # In fwd
    '022193': NADIA_MARCINKO,
    '021814': NADIA_MARCINKO,
    '021808': NADIA_MARCINKO,
    '022190': NADIA_MARCINKO,
    '021818': NADIA_MARCINKO,
    '021811': NADIA_MARCINKO,      # Signature and email address in the message
    '024923': 'Paul Krassner',
    '029981': 'Paula',             # reply
    '031694': 'Peggy Siegal',
    '029020': 'Renata Bolotova',   # Signature
    '029003': SOON_YI,
    '029005': SOON_YI,
    '029007': SOON_YI,
    '029010': SOON_YI,
    '026620': TERRY_KAFKA,
    '028482': TERRY_KAFKA,         # Signature
    '029992': TERRY_KAFKA,         # Reply
    '020666': TERRY_KAFKA,         # ends with 'Terry'
    # '026571': '(unknown french speaker)',

}

KNOWN_EMAIL_RECIPIENTS = {
    '021106': 'Alexandra Preate',     # Reply
    '030764': ARIANE_DE_ROTHSCHILD,   # Reply
    '026431': ARIANE_DE_ROTHSCHILD,   # Reply
    '026426': JEAN_HUGUEN,            # Reply
    '030522': LANDON_THOMAS,
    '031413': LANDON_THOMAS,          # Reply
    '029692': LARRY_SUMMERS,          # Header
    '029779': LARRY_SUMMERS,          # Header
    '028787': LAWRANCE_VISOSKI,
    '022250': LESLEY_GROFF,           # Reply
    '022258': NADIA_MARCINKO,         # Reply header
    '030096': 'Peter Mandelson',
    '019334': STEVE_BANNON,
}


EPSTEIN_SIGNATURE = re.compile(r"""(> )please note
(> )?(• )?The information contained in this communication is
(> )?confidential, may be attorney-client privileged, may
(> )?constitute inside information, and is intended only.*
(> )?the use of the addressee. It is the property.*(\nJEE|Jeffrey Epstein)?
(> )?Unauthorized use, disclosure or copying of this
(> )?communication or any part thereof is strictly prohibit.*
(> )?and may be unlawful. If you have received this
(> )?communication in error, please notify us immediately by(\n\d\s*)?
(> )?return e-mail or by e-mail to.*
(> )?destroy this communication and all copies thereo.*
(> )?including all attachments. copyright -all rights reserved?""")

EPSTEIN_OLD_SIGNATURE = re.compile(r"""\*+
The information contained in this communication is
confidential, may be attorney-client privileged, may
constitute inside information, and is intend.*
the use of the addressee. It is the property.*(\nJeffrey Epstein)?
Unauthorized use, disclosure or copying of this
communication or any part thereof is strictly prohibited
and may be unlawful. If you have received this
communication in error, please notify us immediately by
return e-mail or by e-mail.*
destroy this communication and all copies thereof.*
including all attachments.( copyright -all rights reserved)?""")
