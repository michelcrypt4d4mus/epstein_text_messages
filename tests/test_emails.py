from epstein_files.util.constant.names import *
from epstein_files.util.data import dict_sets_to_lists

EMAIL_AUTHOR_COUNTS = {
    None: 105,
    "Abi Schwinck": 1,
    AL_SECKEL: 7,
    "Alain Forget": 3,
    ALAN_DERSHOWITZ: 5,
    "Alan S Halperin": 1,
    "Alex Yablon": 1,
    ALIREZA_ITTIHADIEH: 8,
    AMANDA_ENS: 8,
    ANAS_ALRASHEED: 7,
    ANDRES_SERRANO: 3,
    ANIL_AMBANI: 2,
    "Ann Marie Villafana": 1,
    "Anne Boyles": 1,
    ARIANE_DE_ROTHSCHILD: 4,
    'Audrey/Aubrey Raimbault (???)': 1,
    AZIZA_ALAHMADI: 3,
    BARBRO_C_EHNBOM: 11,
    "Barnaby Marsh": 1,
    BARRY_J_COHEN: 5,
    "Barry Josephson": 2,
    "Bennet Moskowitz": 2,
    "Bill Siegel": 5,
    "Bob Crowe": 2,
    BORIS_NIKOLIC: 29,
    BRAD_EDWARDS: 1,
    BRAD_KARP: 5,
    "Bruce Moskowitz": 6,
    "Caroline Lang": 4,
    "Carolyn Rangel": 1,
    "Cecile de Jongh": 2,
    CECILIA_STEEN: 1,
    "Christina Galbraith": 5,
    "Dangene and Jennie Enterprise": 5,
    "Daniel Sabba": 3,
    "Daniel Siad": 2,
    "Danny Frost": 1,
    DARREN_INDYKE: 52,
    "Dave Hope": 1,
    DAVID_FISZEL: 2,
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
    EHUD_BARAK: 13,
    "Eric Roth": 5,
    "Erika Kellerhals": 3,
    "Etienne Binant": 1,
    "Eva Dubin": 2,
    "Fabrice Aidan": 1,
    "Faith Kates": 17,
    "Fred Haddad": 3,
    "Gerald Barton": 2,
    "Ghislaine Maxwell": 15,
    "Gianni Serazzi": 2,
    "Gino Yu": 3,
    "Glenn Dubin": 3,
    "Gwendolyn Beck": 6,
    "Harry Fisch": 1,
    HEATHER_MANN: 2,
    HENRY_HOLT: 1,
    "How To Academy": 3,
    IAN_OSBORNE: 2,
    "Intelligence Squared": 4,
    JABOR_Y: 3,
    "Jack Goldberger": 4,
    "Jack Lang": 3,
    'James Hill': 1,
    "Jay Lefkowitz": 7,
    "Jean Huguen": 1,
    JEAN_LUC_BRUNEL: 3,
    JEFF_FULLER: 1,
    JEFFREY_EPSTEIN: 709,
    JENNIFER_JACQUET: 1,
    "Jeremy Rubin": 3,
    JES_STALEY: 2,
    JESSICA_CADWELL: 7,
    JIDE_ZEITLIN: 3,
    JOHN_BROCKMAN: 3,
    JOHN_PAGE: 2,
    JOHNNY_EL_HACHEM: 1,
    JOI_ITO: 25,
    "Jokeland": 2,
    JONATHAN_FARKAS: 24,
    JOSCHA_BACH: 3,
    "Joshua Cooper Ramo": 1,
    "Juleanna Glover": 1,
    "Katherine Keating": 2,
    KATHRYN_RUEMMLER: 82,
    "Kelly Friendly": 4,
    KEN_JENNE: 1,
    "Ken Starr": 5,
    "Kirk Blouin": 2,
    "Landon Thomas Jr": 72,
    "Larry Summers": 48,
    "Laurie Cameron": 1,
    LAWRANCE_VISOSKI: 46,
    LAWRENCE_KRAUSS: 37,
    "Leah Reis-Dennis": 1,
    "Leon Black": 1,
    "Lesley Groff": 24,
    "Lilly Sanchez": 4,
    "Linda Pinto": 1,
    "Linda Stone": 13,
    "Lisa New": 22,
    "Lisa Randall": 2,
    "Manuela Martinez": 2,
    "Marc Leon": 2,
    "Mark Epstein": 5,
    "Mark Green": 1,
    "Mark Lloyd": 1,
    MARK_TRAMO: 1,
    "Martin Nowak": 1,
    "Martin Weinberg": 21,
    "Masha Drokova": 2,
    "Matthew Hiltzik": 2,
    "Melanie Spinella": 1,
    "Melanie Walker": 3,
    "Merwin Dela Cruz": 1,
    "Michael Miller": 4,
    "Michael Sanka": 1,
    "Michael Wolff": 84,
    "Miroslav Lajčák": 1,
    "Mitchell Bard": 4,
    "Mohamed Waheed Hassan": 2,
    MOSHE_HOFFMAN: 1,
    "Nadia Marcinko": 8,
    "Neal Kassell": 2,
    NICHOLAS_RIBIS: 53,
    "Noam Chomsky": 4,
    "Norman D. Rau": 2,
    "Olivier Colom": 1,
    "Paul Barrett": 4,
    "Paul Krassner": 29,
    "Paul Morris": 6,
    "Paul Prosperi": 3,
    PAULA: 2,
    "Peggy Siegal": 8,
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
    "Richard Kahn": 117,
    "Richard Merkin": 3,
    "Robert Lawrence Kuhn": 26,
    "Robert Trivers": 16,
    "Ross Gow": 1,
    "Roy Black": 5,
    "Saved by Internet Explorer 11": 1,
    "Scott J. Link": 2,
    "Sean Bannon": 3,
    "Sean J. Lancaster": 1,
    "Shaher Abdulhak Besher (???)": 2,
    "Skip Rimer": 1,
    "Soon-Yi Previn": 10,
    "Stanley Rosenberg": 3,
    "Stephanie": 4,
    "Stephen Alexander": 1,
    "Stephen Hanson": 5,
    STEVE_BANNON: 44,
    "Steven Elkman": 1,
    STEVEN_HOFFENBERG: 1,
    "Steven Pfeiffer": 2,
    "Steven Sinofsky": 2,
    "Steven Victor MD": 1,
    SULTAN_BIN_SULAYEM: 15,
    "Terje Rød-Larsen": 2,
    TERRY_KAFKA: 9,
    "Thorbjørn Jagland": 6,
    "Tim Zagat": 1,
    "Tom Barrack": 1,
    "Tom Pritzker": 6,
    "Tonja Haddad Coleman": 8,
    "Tyler Shears": 6,
    "Valeria Chomsky": 2,
    "Vincenzo Lozzo": 1,
    "Vinit Sahni": 2,
    "Vladimir Yudashkin": 1,
    ZUBAIR_KHAN: 10,
    "asmallworld@travel.asmallworld.net": 4,
    "digest-noreply@quora.com": 5,
    "drsra": 1,
    "editorialstaff@flipboard.com": 13,
    JP_MORGAN_USGIO: 13,
    "lorraine@mc2mm.com": 1,
    "middle.east.update@hotmail.com": 1,
}

EMAIL_RECIPIENT_COUNTS = {
    None: 71,
    "ACT for America": 2,
    "Alan Dershowitz": 15,
    'Alan Dlugash': 1,
    "Alan Rogers": 1,
    "Alireza Ittihadieh": 2,
    "Allen West": 2,
    "Amanda Ens": 1,
    "Anas Alrasheed": 5,
    "Andrew Friendly": 1,
    "Anil Ambani": 1,
    "Ann Marie Villafana": 3,
    "Anthony Barrett": 1,
    "Ariane de Rothschild": 3,
    "BS Stern": 1,
    'Barb Cowles': 1,
    "Barnaby Marsh": 2,
    "Bennet Greenwald": 2,
    "Bennet Moskowitz": 2,
    "Bennett Schmidt": 2,
    "Bill Gates": 2,
    "Bill Siegel": 1,
    'Bob Fass': 1,
    BORIS_NIKOLIC: 17,
    "Brad Karp": 5,
    BRAD_WECHSLER: 2,
    "Caroline Lang": 2,
    'Caryl Ratner': 1,
    "Cecile de Jongh": 2,
    CECILIA_STEEN: 1,
    "Charlotte Abrams": 1,
    "Cheryl Kleen": 1,
    CHRISTINA_GALBRAITH: 7,
    "Connie Zaguirre": 1,
    "Dan Fleuette": 1,
    'Daniel Dawson': 2,
    "Daniel Siad": 2,
    "Danny Goldberg": 4,
    "Darren Indyke": 61,
    DAVID_BLAINE: 1,
    "David Grosof": 6,
    "David Haig": 2,
    "David Schoen": 3,
    "David Stern": 1,
    "Debbie Fein": 9,
    "Deepak Chopra": 1,
    "Diane Ziman": 1,
    "Ed Boyden": 1,
    EDWARD_JAY_EPSTEIN: 1,
    "Ehud Barak": 3,
    "Eric Roth": 2,
    "Erika Kellerhals": 2,
    "Etienne Binant": 1,
    FAITH_KATES: 9,
    "Forrest Miller": 2,
    "Francis Derby": 3,
    "Fred Haddad": 4,
    "Gary Gross": 2,
    "George Krassner": 4,
    "Gerald Barton": 1,
    GERALD_LEFCOURT: 1,
    "Ghislaine Maxwell": 8,
    "Gianni Serazzi": 1,
    "Glenn Dubin": 1,
    "Gordon Getty": 2,
    "Grant J. Smith": 1,
    "Grant Seeger": 2,
    "Harry Fisch": 1,
    'Harry Shearer': 1,
    "Henry Hortenstine": 2,
    "Herb Goodman": 2,
    'Holly Krassner Dawson': 1,
    "Jabor Y": 7,
    "Jack Goldberger": 12,
    "Jack Lang": 3,
    JACK_SCAROLA: 1,
    "Jackie Perczek": 4,
    "James Ramsey": 2,
    "Janet Kafka": 2,
    "Januiz Banasiak": 2,
    "Jay Lefkowitz": 4,
    'Jay Levin': 1,
    JEAN_HUGUEN: 1,
    JEAN_LUC_BRUNEL: 10,
    JEFF_FULLER: 2,
    JEFFREY_EPSTEIN: 1547,
    JES_STALEY: 7,
    JESSICA_CADWELL: 6,
    "Joel": 2,
    "Joel Dunn": 2,
    "John Page": 2,
    "John Zouzelka": 2,
    JOI_ITO: 11,
    "Jojo Fontanilla": 1,
    'Jokeland': 1,
    "Jonathan Farkas": 9,
    "Joscha Bach": 4,
    "Joseph Vinciguerra": 1,
    "Joshua Cooper Ramo": 1,
    "Katherine Keating": 3,
    KATHRYN_RUEMMLER: 57,
    "Ken Starr": 10,
    "Kenneth E. Mapp": 1,
    "Kevin Bright": 3,
    "Landon Thomas Jr": 52,
    'Lanny Swerdlow': 1,
    "Larry Cohen": 1,
    'Larry Sloman': 1,
    LARRY_SUMMERS: 42,
    LAWRANCE_VISOSKI: 11,
    "Lawrence Krauss": 13,
    "Leah Reis-Dennis": 1,
    'Lee Quarnstrom': 2,
    "Leon Black": 4,
    "Lesley Groff": 22,
    "Lilly Sanchez": 3,
    "Linda Stone": 2,
    'Linda W. Grossman': 3,
    "Lisa Albert": 2,
    LISA_NEW: 14,
    "Louella Rabuyo": 2,
    "Lyn Fontanilla": 1,
    'Lynnie Tofte Fass': 1,
    "Marc Leon": 1,
    "Marcie Brown": 2,
    MARIANA_IDZKOWSKA: 2,
    'Marie Moneysmith': 1,
    "Mark Albert": 1,
    MARK_EPSTEIN: 4,
    "Marshall Funk": 2,
    "Martin Nowak": 1,
    "Martin Weinberg": 28,
    "Masha Drokova": 2,
    "Matthew Hiltzik": 1,
    "Matthew Schafer": 1,
    MELANIE_SPINELLA: 15,
    "Melanie Walker": 2,
    MICHAEL_BUCHHOLTZ: 3,
    "Michael Horowitz": 2,
    "Michael J. Pike": 2,
    "Michael Simmons": 3,
    "Michael Sitrick": 4,
    "Michael Wolff": 69,
    "Miroslav Lajčák": 1,
    "Mohamed Waheed Hassan": 2,
    "Mortimer Zuckerman": 3,
    MOSHE_HOFFMAN: 1,
    'Mrisman02': 2,
    "Nadia Marcinko": 1,
    "Nancy Cain": 3,
    "Nancy Dahl": 2,
    "Nancy Portland": 2,
    "Nate McClain": 2,
    "Nate White": 2,
    "Neal Kassell": 1,
    "Neil Anderson": 2,
    NICHOLAS_RIBIS: 10,
    'Nick Kazan': 2,
    "Nili Priell Barak": 1,
    "Noam Chomsky": 2,
    "Norman Finkelstein": 1,
    "Oliver Goodenough": 1,
    "Owen Blicksilver": 1,
    "Paul Barrett": 1,
    "Paul Krassner": 7,
    "Paul Morris": 1,
    PAULA: 4,
    "Peggy Siegal": 18,
    "Peter Aldhous": 2,
    "Peter Mandelson": 4,
    PETER_THIEL: 5,
    "Philip Kafka": 4,
    'Players2': 1,
    "Police Code Enforcement": 2,
    "Prince Andrew": 2,
    "Raafat Alsabbagh": 2,
    "Rafael Bardaji": 2,
    'Rebecca Risman': 2,
    "Reid Hoffman": 2,
    "Reid Weingarten": 34,
    RENATA_BOLOTOVA: 2,
    "Richard Barnnet": 2,
    "Richard Joshi": 1,
    "Richard Kahn": 31,
    "Richard Merkin": 1,
    "Rita Hortenstine": 2,
    "Robert D. Critton Jr.": 9,
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
    "Steven Gaydos": 3,
    "Steven Pfeiffer": 2,
    "Steven Sinofsky": 1,
    "Sultan Ahmed Bin Sulayem": 14,
    "Susan Edelman": 1,
    "Taal Safdie": 2,
    "Terry Kafka": 1,
    "Thanu Boonyawatana": 1,
    "Thorbjørn Jagland": 6,
    "Tim Kane": 1,
    "Tim Zagat": 1,
    "Tom": 2,
    "Tom Barrack": 2,
    "Tom Pritzker": 9,
    "Tonja Haddad Coleman": 6,
    "Travis Pangburn": 1,
    "Tyler Shears": 1,
    "Uri Fouzailov": 2,
    "Vahe Stepanian": 1,
    "Val Sherman": 2,
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
    "013482",
    "016692",
    "016693",
    '018726',
    "019871",
    "022193",
    "022247",
    "022811",
    "022936",
    "022938",
    "023054",
    "023062",
    "023550",
    "023627",
    "024930",
    "025215",
    "025226",
    "025235",
    "026631",
    "026632",
    "026659",
    "026755",
    "026788",
    '026943',
    "028757",
    "028760",
    "029206",
    "029558",
    "029622",
    "029962",
    "029982",
    "030006",
    "030095",
    "030211",
    "030245",
    "030572",
    "030768",
    "030823",
    "030837",
    "030844",
    "030992",
    "030997",
    "031038",
    "031039",
    "031040",
    "031114",
    "031121",
    "031126",
    "031130",
    "031146",
    "031156",
    "031159",
    "031165",
    '031278',
    "031329",
    "031688",
    "031747",
    "031826",
    "031830",
    "032213",
    "032283",
    "033021",
    "033025",
    "033027",
    "033205",
    "033242",
    '033274',
    "033345",
    "033428",
    "033458",
]

DEVICE_SIGNATURE_TO_AUTHORS = {
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
        "Vincenzo Lozzo"
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
        'Mark Lloyd',
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
    "Lisa New": [
        "Sent from my iPhone"
    ],
    "Lisa Randall": [
        "Sent from my Verizon Wireless BlackBerry"
    ],
    "Mark Epstein": [
        "Sent via tin can and string."
    ],
    "Mark Lloyd": [
        "Sent from my iPad"
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
    "Vincenzo Lozzo": [
        "Sent from my Iphone"
    ]
}

SIGNATURE_SUBSTITUTION_COUNTS = {
    "(unknown)": 2,
    BARBRO_C_EHNBOM: 5,
    ARIANE_DE_ROTHSCHILD: 4,
    "Danny Frost": 8,
    "Darren Indyke": 47,
    "David Ingram": 9,
    "Deepak Chopra": 19,
    "Jeffrey Epstein": 3374,
    JESSICA_CADWELL: 57,
    KEN_JENNE: 1,
    LARRY_SUMMERS: 232,
    "Lawrence Krauss": 78,
    "Martin Weinberg": 17,
    "Paul Barrett": 10,
    "Peter Mandelson": 10,
    "Richard Kahn": 121,
    STEVEN_PFEIFFER: 11,
    "Susan Edelman": 9,
    "Terry Kafka": 10,
    "Tonja Haddad Coleman": 9,
}


def test_email_author_counts(epstein_files):
    assert epstein_files.email_author_counts == EMAIL_AUTHOR_COUNTS


def test_email_recipient_counts(epstein_files):
    assert epstein_files.email_recipient_counts == EMAIL_RECIPIENT_COUNTS


def test_unknown_recipient_file_ids(epstein_files):
    assert epstein_files.email_unknown_recipient_file_ids() == UNKNOWN_RECIPIENT_FILE_IDS


def test_signatures(epstein_files):
    assert dict_sets_to_lists(epstein_files.email_authors_to_device_signatures) == AUTHORS_TO_DEVICE_SIGNATURES
    assert dict_sets_to_lists(epstein_files.email_device_signatures_to_authors) == DEVICE_SIGNATURE_TO_AUTHORS


def test_signature_substitutions(epstein_files):
    assert epstein_files.email_signature_substitution_counts() == SIGNATURE_SUBSTITUTION_COUNTS
