from epstein_files.util.constant.names import *
from epstein_files.util.data import dict_sets_to_lists


EMAIL_AUTHOR_COUNTS = {
    None: 54,
    "Abi Schwinck": 1,
    AL_SECKEL: 7,
    "Alain Forget": 3,
    ALAN_DERSHOWITZ: 4,
    "Alan S Halperin": 1,
    "Alex Yablon": 1,
    ALIREZA_ITTIHADIEH: 8,
    AMANDA_ENS: 8,
    ANAS_ALRASHEED: 44,
    ANDRES_SERRANO: 3,
    ANIL_AMBANI: 1,
    "Ann Marie Villafana": 1,
    "Anne Boyles": 1,
    ARIANE_DE_ROTHSCHILD: 4,
    'Audrey/Aubrey Raimbault (???)': 1,
    AZIZA_ALAHMADI: 3,
    BARBRO_C_EHNBOM: 6,
    "Barnaby Marsh": 1,
    BARRY_J_COHEN: 5,
    "Barry Josephson": 2,
    "Bennet Moskowitz": 1,
    "Bill Siegel": 5,
    "Bob Crowe": 1,
    BORIS_NIKOLIC: 22,
    BRAD_EDWARDS: 1,
    BRAD_KARP: 5,
    "Bruce Moskowitz": 6,
    "Caroline Lang": 4,
    "Carolyn Rangel": 1,
    "Cecile de Jongh": 2,
    CECILIA_STEEN: 1,
    CHRISTINA_GALBRAITH: 4,
    DANGENE_AND_JENNIE_ENTERPRISE: 4,
    "Daniel Sabba": 3,
    "Daniel Siad": 2,
    "Danny Frost": 1,
    DARREN_INDYKE: 49,
    "Dave Hope": 1,
    DAVID_FISZEL: 1,
    "David Grosof": 1,
    "David Haig": 1,
    "David Mitchell": 1,
    "David Schoen": 11,
    "David Stern": 7,
    "Deepak Chopra": 18,
    "Diane Ziman": 1,
    "Donald Rubin": 1,
    "Eduardo Robles": 1,
    EDWARD_JAY_EPSTEIN: 2,
    "Edward Rod Larsen": 2,
    EHUD_BARAK: 10,
    "Eric Roth": 3,
    "Erika Kellerhals": 3,
    "Etienne Binant": 1,
    "Eva Dubin": 2,
    "Fabrice Aidan": 1,
    FAITH_KATES: 10,
    "Fred Haddad": 2,
    "Gerald Barton": 2,
    GHISLAINE_MAXWELL: 14,
    "Gianni Serazzi": 2,
    "Gino Yu": 3,
    "Glenn Dubin": 3,
    "Gwendolyn Beck": 5,
    "Harry Fisch": 1,
    HEATHER_MANN: 2,
    HENRY_HOLT: 1,
    "How To Academy": 3,
    IAN_OSBORNE: 2,
    "Intelligence Squared": 4,
    JABOR_Y: 3,
    JACK_GOLDBERGER: 3,
    "Jack Lang": 3,
    'James Hill': 1,
    "Jay Lefkowitz": 6,
    "Jean Huguen": 1,
    JEAN_LUC_BRUNEL: 3,
    JEFF_FULLER: 1,
    JEFFREY_EPSTEIN: 667,
    JENNIFER_JACQUET: 1,
    "Jeremy Rubin": 3,
    JES_STALEY: 2,
    JESSICA_CADWELL: 5,
    JIDE_ZEITLIN: 3,
    JOHN_BROCKMAN: 3,
    JOHN_PAGE: 2,
    JOHNNY_EL_HACHEM: 1,
    JOI_ITO: 25,
    "Jokeland": 1,
    JONATHAN_FARKAS: 19,
    JOSCHA_BACH: 3,
    "Joshua Cooper Ramo": 1,
    "Juleanna Glover": 1,
    "Katherine Keating": 2,
    KATHRYN_RUEMMLER: 81,
    "Kelly Friendly": 4,
    KEN_JENNE: 1,
    "Ken Starr": 5,
    "Kirk Blouin": 1,
    LANDON_THOMAS: 72,
    LARRY_SUMMERS: 48,
    "Laurie Cameron": 1,
    LAWRANCE_VISOSKI: 40,
    LAWRENCE_KRAUSS: 33,
    "Leah Reis-Dennis": 1,
    "Leon Black": 1,
    LESLEY_GROFF: 23,
    "Lilly Sanchez": 4,
    "Linda Pinto": 1,
    "Linda Stone": 13,
    "Lisa New": 22,
    "Lisa Randall": 2,
    "Manuela Martinez": 2,
    "Marc Leon": 2,
    "Mark Epstein": 6,
    "Mark Green": 1,
    MARK_TRAMO: 1,
    "Martin Nowak": 1,
    "Martin Weinberg": 17,
    MASHA_DROKOVA: 11,
    "Matthew Hiltzik": 1,
    "Melanie Spinella": 1,
    "Melanie Walker": 3,
    "Merwin Dela Cruz": 1,
    "Michael Miller": 4,
    "Michael Sanka": 1,
    "Michael Wolff": 84,
    "Miroslav Lajčák": 1,
    "Mitchell Bard": 2,
    "Mohamed Waheed Hassan": 2,
    MOSHE_HOFFMAN: 1,
    "Nadia Marcinko": 7,
    "Neal Kassell": 2,
    NICHOLAS_RIBIS: 42,
    "Noam Chomsky": 4,
    "Norman D. Rau": 1,
    "Olivier Colom": 1,
    "Paul Barrett": 4,
    "Paul Krassner": 27,
    "Paul Morris": 6,
    "Paul Prosperi": 2,
    PAULA: 2,
    PEGGY_SIEGAL: 6,
    PETER_ATTIA: 2,
    "Peter Green": 1,
    "Peter Mandelson": 4,
    PETER_THIEL: 1,
    "Peter Thomas Roth": 2,
    "Philip Kafka": 1,
    "Prince Andrew": 2,
    PUREVSUREN_LUNDEG: 1,
    "R. Couri Hay": 1,
    "Ramsey Elkholy": 1,
    "Reid Hoffman": 1,
    "Reid Weingarten": 72,
    RENATA_BOLOTOVA: 4,
    "Richard Kahn": 116,
    "Richard Merkin": 3,
    ROBERT_LAWRENCE_KUHN: 26,
    "Robert Trivers": 15,
    "Ross Gow": 1,
    "Roy Black": 3,
    "Scott J. Link": 2,
    "Sean Bannon": 3,
    "Sean J. Lancaster": 1,
    SHAHER_ABDULHAK_BESHER: 2,
    "Skip Rimer": 1,
    SOON_YI_PREVIN: 9,
    "Stanley Rosenberg": 3,
    "Stephanie": 2,
    "Stephen Alexander": 1,
    "Stephen Hanson": 5,
    STEVE_BANNON: 44,
    "Steven Elkman": 1,
    STEVEN_HOFFENBERG: 1,
    "Steven Pfeiffer": 2,
    "Steven Sinofsky": 2,
    "Steven Victor MD": 1,
    SULTAN_BIN_SULAYEM: 12,
    TERJE_ROD_LARSEN: 1,
    TERRY_KAFKA: 8,
    "Thorbjørn Jagland": 6,
    "Tim Zagat": 1,
    "Tom Barrack": 1,
    "Tom Pritzker": 6,
    TONJA_HADDAD_COLEMAN: 5,
    "Tyler Shears": 6,
    "Valeria Chomsky": 2,
    VINCENZO_IOZZO: 1,
    "Vinit Sahni": 2,
    "Vladimir Yudashkin": 1,
    ZUBAIR_KHAN: 10,
    "asmallworld@travel.asmallworld.net": 2,
    "digest-noreply@quora.com": 5,
    "drsra": 1,
    "editorialstaff@flipboard.com": 13,
    JP_MORGAN_USGIO: 8,
    "lorraine@mc2mm.com": 1,
    "middle.east.update@hotmail.com": 1,
}

EMAIL_RECIPIENT_COUNTS = {
    None: 31,
    "ACT for America": 1,
    "Alan Dershowitz": 11,
    'Alan Dlugash': 1,
    "Alan Rogers": 1,
    "Alireza Ittihadieh": 2,
    "Allen West": 1,
    "Amanda Ens": 1,
    ANAS_ALRASHEED: 6,
    "Andrew Friendly": 1,
    "Anil Ambani": 1,
    "Ann Marie Villafana": 3,
    "Anthony Barrett": 1,
    "Ariane de Rothschild": 3,
    'Barb Cowles': 1,
    "Barnaby Marsh": 2,
    "Bennet Greenwald": 1,
    "Bennet Moskowitz": 1,
    "Bennett Schmidt": 1,
    "Bill Gates": 2,
    "Bill Siegel": 1,
    'Bob Fass': 1,
    BORIS_NIKOLIC: 10,
    "Brad Karp": 5,
    BRAD_WECHSLER: 2,
    "Caroline Lang": 2,
    'Caryl Ratner': 2,
    "Cecile de Jongh": 2,
    CECILIA_STEEN: 1,
    'Charles Michael': 1,
    "Charlotte Abrams": 1,
    "Cheryl Kleen": 1,
    CHRISTINA_GALBRAITH: 7,
    "Connie Zaguirre": 1,
    "Dan Fleuette": 1,
    'Daniel Dawson': 2,
    "Daniel Siad": 2,
    "Danny Goldberg": 5,
    DARREN_INDYKE: 49,
    DAVID_BLAINE: 1,
    "David Grosof": 6,
    "David Haig": 2,
    "David Schoen": 3,
    "David Stern": 1,
    "Debbie Fein": 5,
    "Deepak Chopra": 1,
    "Diane Ziman": 1,
    "Ed Boyden": 1,
    EDWARD_JAY_EPSTEIN: 1,
    "Ehud Barak": 3,
    "Eric Roth": 1,
    "Erika Kellerhals": 2,
    "Etienne Binant": 1,
    FAITH_KATES: 5,
    "Forrest Miller": 1,
    "Francis Derby": 2,
    "Fred Haddad": 3,
    "Gary Gross": 1,
    "George Krassner": 3,
    "Gerald Barton": 1,
    GERALD_LEFCOURT: 1,
    GHISLAINE_MAXWELL: 8,
    "Gianni Serazzi": 1,
    "Glenn Dubin": 1,
    "Gordon Getty": 2,
    "Grant J. Smith": 1,
    "Grant Seeger": 1,
    "Harry Fisch": 1,
    'Harry Shearer': 1,
    "Henry Hortenstine": 1,
    "Herb Goodman": 1,
    'Holly Krassner Dawson': 1,
    "Jabor Y": 7,
    "Jack Goldberger": 9,
    "Jack Lang": 3,
    JACK_SCAROLA: 1,
    "Jackie Perczek": 3,
    "James Ramsey": 1,
    "Janet Kafka": 1,
    JANUSZ_BANASIAK: 1,
    "Jay Lefkowitz": 3,
    'Jay Levin': 1,
    JEAN_HUGUEN: 1,
    JEAN_LUC_BRUNEL: 9,
    JEFF_FULLER: 2,
    JEFFREY_EPSTEIN: 1478,
    JES_STALEY: 7,
    JESSICA_CADWELL: 3,
    "Joel": 3,
    "Joel Dunn": 1,
    "John Page": 1,
    "John Zouzelka": 1,
    JOI_ITO: 11,
    "Jojo Fontanilla": 1,
    "Jonathan Farkas": 9,
    "Joscha Bach": 4,
    "Joseph Vinciguerra": 1,
    "Joshua Cooper Ramo": 1,
    "Katherine Keating": 3,
    KATHRYN_RUEMMLER: 55,
    KEN_STARR: 9,
    "Kenneth E. Mapp": 1,
    "Kevin Bright": 4,
    "Landon Thomas Jr": 52,
    'Lanny Swerdlow': 1,
    "Larry Cohen": 1,
    'Larry Sloman': 1,
    LARRY_SUMMERS: 38,
    LAWRANCE_VISOSKI: 9,
    "Lawrence Krauss": 11,
    "Leah Reis-Dennis": 1,
    'Lee Quarnstrom': 2,
    "Leon Black": 4,
    "Lesley Groff": 21,
    "Lilly Sanchez": 2,
    "Linda Stone": 2,
    'Linda W. Grossman': 2,
    "Lisa Albert": 1,
    LISA_NEW: 14,
    "Louella Rabuyo": 1,
    "Lyn Fontanilla": 1,
    'Lynnie Tofte Fass': 1,
    "Marc Leon": 1,
    "Marcie Brown": 1,
    MARIANA_IDZKOWSKA: 1,
    'Marie Moneysmith': 1,
    "Mark Albert": 1,
    MARK_EPSTEIN: 3,
    "Marshall Funk": 1,
    "Martin Nowak": 1,
    MARTIN_WEINBERG: 25,
    MASHA_DROKOVA: 4,
    "Matthew Hiltzik": 1,
    "Matthew Schafer": 1,
    MELANIE_SPINELLA: 13,
    "Melanie Walker": 2,
    MICHAEL_BUCHHOLTZ: 2,
    "Michael Horowitz": 1,
    "Michael J. Pike": 1,
    "Michael Simmons": 3,
    "Michael Sitrick": 3,
    "Michael Wolff": 68,
    "Miroslav Lajčák": 1,
    "Mohamed Waheed Hassan": 2,
    "Mortimer Zuckerman": 3,
    MOSHE_HOFFMAN: 1,
    'Mrisman02': 1,
    "Nadia Marcinko": 2,
    "Nancy Cain": 3,
    "Nancy Dahl": 2,
    "Nancy Portland": 2,
    "Nate McClain": 1,
    "Nate White": 1,
    "Neal Kassell": 1,
    "Neil Anderson": 1,
    NICHOLAS_RIBIS: 10,
    'Nick Kazan': 1,
    "Nili Priell Barak": 1,  # Wife of Ehud
    "Noam Chomsky": 2,
    "Norman Finkelstein": 1,
    "Oliver Goodenough": 1,
    "Owen Blicksilver": 1,
    "Paul Barrett": 1,
    "Paul Krassner": 7,
    "Paul Morris": 1,
    PAULA: 5,
    PEGGY_SIEGAL: 11,
    "Peter Aldhous": 2,
    "Peter Mandelson": 4,
    PETER_THIEL: 5,
    "Philip Kafka": 3,
    'Players2': 1,
    "Police Code Enforcement": 1,
    "Prince Andrew": 2,
    "Raafat Alsabbagh": 2,
    "Rafael Bardaji": 1,
    'Rebecca Risman': 1,
    "Reid Hoffman": 2,
    REID_WEINGARTEN: 33,
    RENATA_BOLOTOVA: 2,
    "Richard Barnnet": 1,
    "Richard Joshi": 1,
    RICHARD_KAHN: 30,
    "Richard Merkin": 1,
    "Rita Hortenstine": 1,
    "Robert D. Critton Jr.": 6,
    "Robert Gold": 1,
    "Robert Lawrence Kuhn": 2,
    "Robert Trivers": 3,
    "Roger Schank": 2,
    "Roy Black": 4,
    "Sam Harris": 1,
    SAMUEL_LEFF: 2,
    "Scott J. Link": 1,
    "Sean Bannon": 1,
    "Sean T Lehane": 1,
    SOON_YI_PREVIN: 4,
    "Stanley Rosenberg": 1,
    "Stephen Hanson": 3,
    "Stephen Rubin": 1,
    "Steve Bannon": 31,
    "Steven Gaydos": 2,
    "Steven Pfeiffer": 1,
    "Steven Sinofsky": 1,
    "Sultan Ahmed Bin Sulayem": 11,
    "Susan Edelman": 1,
    "Taal Safdie": 1,
    "Terry Kafka": 1,
    "Thanu Boonyawatana": 1,
    "Thorbjørn Jagland": 6,
    "Tim Kane": 1,
    "Tim Zagat": 1,
    "Tom": 2,
    "Tom Barrack": 2,
    "Tom Pritzker": 8,
    TONJA_HADDAD_COLEMAN: 3,
    "Travis Pangburn": 1,
    "Tyler Shears": 1,
    "Uri Fouzailov": 1,
    "Vahe Stepanian": 1,
    "Val Sherman": 1,
    "Valeria Chomsky": 1,
    VINIT_SAHNI: 1,
    'W&K': 1,
    'Walli Leff': 1,
    "Warren Eisenstein": 2,
    ZUBAIR_KHAN: 1,
    "david.brown@thetimes.co.uk": 1,
    "io-anne.pugh@bbc.co.uk": 1,
    "martin.robinson@mailonline.co.uk": 1,
    "nick.alwav@bbc.co.uk": 1,
    "nick.sommerlad@mirror.co.uk": 1,
    "p.peachev@independent.co.uk": 1,
    "pink@mc2mm.com": 2
}

UNKNOWN_RECIPIENT_FILE_IDS = [
    "016692",
    "016693",
    '018726',
    "022247",
    "022936",
    "022938",
    "023062",
    "024930",
    "026659",
    '026943',
    "028757",
    "028760",
    "029206",
    "029962",
    "029982",
    "030095",
    "030211",
    "030768",
    "030823",
    "030992",
    "030997",
    "031038",
    "031039",
    "031040",
    "031688",
    "031826",
    "031830",
    "032213",
    "032283",
    '032951',
    "033345",
]

DEVICE_SIGNATURE_TO_AUTHORS = {
    'Co-authored with iPhone auto-correct': [
        LINDA_STONE
    ],
    'Envoyé de mon iPhone': [
        'Fabrice Aidan',
    ],
    "Sent from AOL Mobile Mail": [
        DAVID_SCHOEN,
    ],
    "Sent from President's iPad": [
        "Mohamed Waheed Hassan"
    ],
    "Sent from ProtonMail": [
        "Sean Bannon",
    ],
    "Sent from Soon-Yi's iPhone": [
        SOON_YI_PREVIN,
    ],
    "Sent from Steve Hanson's Blackberry": [
        "Stephen Hanson"
    ],
    "Sent from Yahoo Mail for iPhone": [
        MERWIN_DELA_CRUZ,
    ],
    'Sent from iPad': [
        BARBRO_C_EHNBOM,
    ],
    "Sent from my BlackBerry - the most secure mobile device": [
        "Michael Miller"
    ],
    "Sent from my BlackBerry 10 smartphone.": [
        NICHOLAS_RIBIS,
        "Reid Weingarten",
    ],
    "Sent from my BlackBerry® wireless device": [
        "Landon Thomas Jr",
        "Ross Gow"
    ],
    "Sent from my Iphone": [
        VINCENZO_IOZZO
    ],
    "Sent from my Samsung JackTM, a Windows Mobile® smartphone from AT&T": [
        "Boris Nikolic"
    ],
    "Sent from my Verizon 4G LTE Droid": [
        DARREN_INDYKE,
    ],
    "Sent from my Verizon Wireless BlackBerry": [
        ALAN_DERSHOWITZ,
        "Lisa Randall",
    ],
    "Sent from my Windows 10 phone": [
        UNKNOWN,
    ],
    "Sent from my Windows Phone": [
        "Boris Nikolic",
        "Gwendolyn Beck"
    ],
    "Sent from my iPad": [
        '(unknown)',
        'Bruce Moskowitz',
        CECILIA_STEEN,
        'Ehud Barak',
        FRED_HADDAD,
        'Glenn Dubin',
        JOI_ITO,
        KATHRYN_RUEMMLER,
        LARRY_SUMMERS,
        'Lawrance Visoski',
        MARK_EPSTEIN,
        'Neal Kassell',
        'Peggy Siegal',
        PUREVSUREN_LUNDEG,
        'Richard Merkin',
        SHAHER_ABDULHAK_BESHER,
        'Stephen Hanson',
    ],
    "Sent from my iPhone": [
        UNKNOWN,
        ALAN_DERSHOWITZ,
        ANAS_ALRASHEED,
        AZIZA_ALAHMADI,
        'Bruce Moskowitz',
        'Darren Indyke',
        'David Schoen',
        'Ehud Barak',
        'Erika Kellerhals',
        'Eva Dubin',
        'Faith Kates',
        FRED_HADDAD,
        'Gino Yu',
        'Glenn Dubin',
        'Harry Fisch',
        HEATHER_MANN,
        'Jack Goldberger',
        'Jeffrey Epstein',
        'Jes Staley',
        'Johnny el Hachem',
        JOI_ITO,
        'Jonathan Farkas',
        KATHRYN_RUEMMLER,
        'Kelly Friendly',
        'Ken Starr',
        'Landon Thomas Jr',
        'Larry Summers',
        'Lawrance Visoski',
        'Lawrence Krauss',
        'Lesley Groff',
        'Lisa New',
        'Martin Weinberg',
        'Matthew Hiltzik',
        'Mohamed Waheed Hassan',
        'Neal Kassell',
        NICHOLAS_RIBIS,
        'Richard Kahn',
        'Richard Merkin',
        'Robert Lawrence Kuhn',
        'Sean Bannon',
        'Stanley Rosenberg',
        'Stephen Hanson',
        'Sultan Ahmed Bin Sulayem',
        'Terje Rød-Larsen',
        'Terry Kafka',
        'Tom Barrack',
        'Tonja Haddad Coleman',
        'Tyler Shears',
    ],
    "Sent from my iPhone and misspellings courtesy of iPhone.": [
        CECILE_DE_JONGH,
    ],
    "Sent via BlackBerry by AT&T": [
        UNKNOWN,
        PEGGY_SIEGAL,
        STEVE_BANNON,
        TERRY_KAFKA,
    ],
    "Sent via BlackBerry from T-Mobile": [
        PAULA
    ],
    "Sent via tin can and string.": [
        "Mark Epstein"
    ],
    "Sorry for all the typos .Sent from my iPhone": [
        "Jeffrey Epstein"
    ]
}

AUTHORS_TO_DEVICE_SIGNATURES = {
    UNKNOWN: [
        "Sent from my Windows 10 phone",
        "Sent from my iPad",
        "Sent from my iPhone",
        "Sent via BlackBerry by AT&T"
    ],
    ALAN_DERSHOWITZ: [
        "Sent from my Verizon Wireless BlackBerry",
        "Sent from my iPhone"
    ],
    ANAS_ALRASHEED: [
        "Sent from my iPhone"
    ],
    AZIZA_ALAHMADI: [
        "Sent from my iPhone"
    ],
    BARBRO_C_EHNBOM: [
        'Sent from iPad',
    ],
    BORIS_NIKOLIC: [
        "Sent from my Samsung JackTM, a Windows Mobile® smartphone from AT&T",
        "Sent from my Windows Phone"
    ],
    "Bruce Moskowitz": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    CECILE_DE_JONGH: [
        "Sent from my iPhone and misspellings courtesy of iPhone."
    ],
    CECILIA_STEEN: [
        "Sent from my iPad"
    ],
    "Darren Indyke": [
        "Sent from my Verizon 4G LTE Droid",
        "Sent from my iPhone"
    ],
    "David Schoen": [
        "Sent from AOL Mobile Mail",
        "Sent from my iPhone"
    ],
    "Ehud Barak": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Erika Kellerhals": [
        "Sent from my iPhone"
    ],
    "Eva Dubin": [
        "Sent from my iPhone"
    ],
    'Fabrice Aidan': [
        'Envoyé de mon iPhone',
    ],
    "Faith Kates": [
        "Sent from my iPhone"
    ],
    'Fred Haddad': [
        'Sent from my iPad',
        "Sent from my iPhone",
    ],
    "Gino Yu": [
        "Sent from my iPhone"
    ],
    "Glenn Dubin": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Gwendolyn Beck": [
        "Sent from my Windows Phone"
    ],
    "Harry Fisch": [
        "Sent from my iPhone"
    ],
    HEATHER_MANN: [
        "Sent from my iPhone"
    ],
    "Jack Goldberger": [
        "Sent from my iPhone"
    ],
    "Jeffrey Epstein": [
        "Sent from my iPhone",
        "Sorry for all the typos .Sent from my iPhone"
    ],
    JES_STALEY: [
        "Sent from my iPhone"
    ],
    "Johnny el Hachem": [
        "Sent from my iPhone"
    ],
    JOI_ITO: [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Jonathan Farkas": [
        "Sent from my iPhone"
    ],
    KATHRYN_RUEMMLER: [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Kelly Friendly": [
        "Sent from my iPhone"
    ],
    KEN_STARR: [
        "Sent from my iPhone"
    ],
    LANDON_THOMAS: [
        "Sent from my BlackBerry® wireless device",
        "Sent from my iPhone"
    ],
    LARRY_SUMMERS: [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    LAWRANCE_VISOSKI: [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Lawrence Krauss": [
        "Sent from my iPhone"
    ],
    "Lesley Groff": [
        "Sent from my iPhone"
    ],
    LINDA_STONE: [
        'Co-authored with iPhone auto-correct',
    ],
    "Lisa New": [
        "Sent from my iPhone"
    ],
    "Lisa Randall": [
        "Sent from my Verizon Wireless BlackBerry"
    ],
    MARK_EPSTEIN: [
        "Sent from my iPad",
        "Sent via tin can and string.",
    ],
    "Martin Weinberg": [
        "Sent from my iPhone"
    ],
    "Matthew Hiltzik": [
        "Sent from my iPhone"
    ],
    "Merwin Dela Cruz": [
        "Sent from Yahoo Mail for iPhone"
    ],
    "Michael Miller": [
        "Sent from my BlackBerry - the most secure mobile device"
    ],
    "Mohamed Waheed Hassan": [
        "Sent from President's iPad",
        "Sent from my iPhone"
    ],
    "Neal Kassell": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    NICHOLAS_RIBIS: [
        "Sent from my BlackBerry 10 smartphone.",
        "Sent from my iPhone"
    ],
    PAULA: [
        "Sent via BlackBerry from T-Mobile"
    ],
    "Peggy Siegal": [
        "Sent from my iPad",
        "Sent via BlackBerry by AT&T"
    ],
    PUREVSUREN_LUNDEG: [
        'Sent from my iPad',
    ],
    "Reid Weingarten": [
        "Sent from my BlackBerry 10 smartphone.",
    ],
    "Richard Kahn": [
        "Sent from my iPhone"
    ],
    "Richard Merkin": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Robert Lawrence Kuhn": [
        "Sent from my iPhone"
    ],
    "Ross Gow": [
        "Sent from my BlackBerry® wireless device"
    ],
    "Sean Bannon": [
        "Sent from ProtonMail",
        "Sent from my iPhone"
    ],
    SHAHER_ABDULHAK_BESHER: [
        'Sent from my iPad',
    ],
    "Soon-Yi Previn": [
        "Sent from Soon-Yi's iPhone"
    ],
    "Stanley Rosenberg": [
        "Sent from my iPhone"
    ],
    "Stephen Hanson": [
        "Sent from Steve Hanson's Blackberry",
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Steve Bannon": [
        "Sent via BlackBerry by AT&T"
    ],
    "Sultan Ahmed Bin Sulayem": [
        "Sent from my iPhone"
    ],
    TERJE_ROD_LARSEN: [
        "Sent from my iPhone"
    ],
    TERRY_KAFKA: [
        "Sent from my iPhone",
        "Sent via BlackBerry by AT&T"
    ],
    "Tom Barrack": [
        "Sent from my iPhone"
    ],
    TONJA_HADDAD_COLEMAN: [
        'Sent from my iPhone',
    ],
    "Tyler Shears": [
        "Sent from my iPhone"
    ],
    VINCENZO_IOZZO: [
        "Sent from my Iphone"
    ]
}

SIGNATURE_SUBSTITUTION_COUNTS = {
    "(unknown)": 2,
    BARBRO_C_EHNBOM: 5,
    ARIANE_DE_ROTHSCHILD: 4,
    'Daniel Siad': 5,
    "Danny Frost": 8,
    "Darren Indyke": 47,
    "David Ingram": 9,
    "Deepak Chopra": 19,
    EDUARDO_ROBLES: 6,
    "Jeffrey Epstein": 3374,
    JESSICA_CADWELL: 57,
    KEN_JENNE: 1,
    LARRY_SUMMERS: 232,
    "Lawrence Krauss": 78,
    "Martin Weinberg": 17,
    "Paul Barrett": 10,
    "Peter Mandelson": 10,
    "Richard Kahn": 121,
    ROSS_GOW: 7,
    STEVEN_PFEIFFER: 11,
    "Susan Edelman": 9,
    "Terry Kafka": 10,
    TOM_PRITZKER: 17,
    "Tonja Haddad Coleman": 9,
}


def test_email_author_counts(epstein_files):
    assert epstein_files.email_author_counts() == EMAIL_AUTHOR_COUNTS


def test_email_recipient_counts(epstein_files):
    assert epstein_files.email_recipient_counts() == EMAIL_RECIPIENT_COUNTS


def test_info_sentences(epstein_files):
    email = epstein_files.for_ids('026290')[0]
    assert len(email.info()) == 1
    email_with_description = epstein_files.for_ids('031278')[0]
    assert len(email_with_description.info()) == 2


def test_signatures(epstein_files):
    assert dict_sets_to_lists(epstein_files.email_authors_to_device_signatures()) == AUTHORS_TO_DEVICE_SIGNATURES
    assert dict_sets_to_lists(epstein_files.email_device_signatures_to_authors()) == DEVICE_SIGNATURE_TO_AUTHORS


def test_signature_substitutions(epstein_files):
    assert epstein_files.email_signature_substitution_counts() == SIGNATURE_SUBSTITUTION_COUNTS


def test_unknown_recipient_file_ids(epstein_files):
    assert epstein_files.unknown_recipient_ids() == UNKNOWN_RECIPIENT_FILE_IDS
