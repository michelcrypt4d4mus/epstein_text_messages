from epstein_files.util.constant.names import *
from epstein_files.util.data import dict_sets_to_lists


EMAIL_AUTHOR_COUNTS = {
    None: 86,
    "Abi Schwinck": 1,
    AL_SECKEL: 8,
    "Alain Forget": 3,
    ALAN_DERSHOWITZ: 4,
    "Alan S Halperin": 1,
    'Alex Conlon': 1,
    "Alex Yablon": 1,
    ALIREZA_ITTIHADIEH: 10,
    ALISON_J_NATHAN: 2,
    AMANDA_ENS: 8,
    AMIR_TAAKI: 10,
    ANAS_ALRASHEED: 50,
    'Anastasiya': 1,
    ANDRES_SERRANO: 3,
    ANDREW_MCCORMACK: 20,
    ANIL_AMBANI: 1,
    "Ann Marie Villafana": 1,
    "Anne Boyles": 1,
    ARIANE_DE_ROTHSCHILD: 4,
    ATT_COURT_APPEARANCE_TEAM: 1,
    'Audrey/Aubrey Raimbault (???)': 1,
    'Audrey Strauss': 1,
    AUSTIN_HILL: 29,
    AZIZA_ALAHMADI: 4,
    BARBRO_C_EHNBOM: 6,
    "Barnaby Marsh": 1,
    BARRY_J_COHEN: 5,
    "Barry Josephson": 2,
    'Bella Klein': 1,
    "Bennet Moskowitz": 1,
    "Bill Siegel": 5,
    "Bob Crowe": 1,
    BORIS_NIKOLIC: 24,
    BRAD_EDWARDS: 1,
    BRAD_KARP: 5,
    BROCK_PIERCE: 39,
    "Bruce Moskowitz": 6,
    BRYAN_BISHOP: 3,
    BUREAU_OF_PRISONS: 1,
    "Caroline Lang": 4,
    CAROLYN_RANGEL: 1,
    CECILE_DE_JONGH: 2,
    CECILIA_STEEN: 1,
    CHRISTIAN_EVERDELL: 1,
    CHRISTINA_GALBRAITH: 6,
    CHRISTOPHER_DILORIO: 4,
    'Coursera': 1,
    DANGENE_AND_JENNIE_ENTERPRISE: 4,
    DANIEL_SABBA: 3,
    DANIEL_SIAD: 2,
    "Danny Frost": 1,
    DARREN_INDYKE: 50,
    "Dave Hope": 1,
    DAVID_FISZEL: 1,
    "David Grosof": 1,
    "David Haig": 1,
    "David Mitchell": 1,
    "David Schoen": 11,
    DAVID_STERN: 9,
    DEEPAK_CHOPRA: 18,
    "Diane Ziman": 1,
    'DOJ London': 1,
    DONALD_NORMAN: 2,
    "Donald Rubin": 1,
    DOUGLAS_WIGDOR: 1,
    "Eduardo Robles": 1,
    EDWARD_JAY_EPSTEIN: 2,
    EDWARD_ROD_LARSEN: 2,
    EHUD_BARAK: 10,
    'Eric Doherty': 1,
    "Eric Roth": 3,
    "Erika Kellerhals": 3,
    "Etienne Binant": 1,
    "Eva Dubin": 2,
    "Fabrice Aidan": 1,
    FAITH_KATES: 10,
    FBI: 4,
    'Florence Hutner': 1,
    'Francesca Hall': 1,
    "Fred Haddad": 2,
    GANBAT_CHULUUNKHUU: 7,
    "Gerald Barton": 2,
    GHISLAINE_MAXWELL: 14,
    "Gianni Serazzi": 2,
    "Gino Yu": 3,
    GLENN_DUBIN: 3,
    GOOGLE_PLUS: 1,
    'Gregory Brown': 1,
    "Gwendolyn Beck": 5,
    "Harry Fisch": 1,
    HEATHER_MANN: 2,
    HENRY_HOLT: 1,
    "How To Academy": 3,
    'Ian ODonnell': 2,
    IAN_OSBORNE: 2,
    'Ike Groff': 1,
    "Intelligence Squared": 4,
    JABOR_Y: 4,
    JACK_GOLDBERGER: 3,
    "Jack Lang": 3,
    JACK_SCAROLA: 1,
    'James Fitzgerald': 2,
    'James Hill': 1,
    "Jay Lefkowitz": 6,
    JEAN_HUGUEN: 1,
    JEAN_LUC_BRUNEL: 3,
    JEANNE_M_CHRISTENSEN: 14,
    JEFF_FULLER: 1,
    JEFFREY_EPSTEIN: 783,
    JENNIFER_JACQUET: 1,
    JEREMY_RUBIN: 6,
    JES_STALEY: 2,
    JESSICA_CADWELL: 5,
    JIDE_ZEITLIN: 3,
    JOHN_BROCKMAN: 3,
    JOHN_PAGE: 2,
    JOHNNY_EL_HACHEM: 1,
    JOI_ITO: 32,
    "Jokeland": 1,
    JONATHAN_FARKAS: 19,
    JOSCHA_BACH: 3,
    "Joshua Cooper Ramo": 1,
    "Juleanna Glover": 1,
    JULIA_SANTOS: 1,
    'Justin Alfano': 1,
    KARYNA_SHULIAK: 6,
    KATHERINE_KEATING: 2,
    KATHRYN_RUEMMLER: 82,
    "Kelly Friendly": 4,
    KEN_JENNE: 1,
    KEN_STARR: 5,
    "Kirk Blouin": 1,
    LANDON_THOMAS: 72,
    LARRY_SUMMERS: 49,
    'Laura Menninger': 1,
    "Laurie Cameron": 1,
    LAWRANCE_VISOSKI: 39,
    LAWRENCE_KRAUSS: 33,
    "Leah Reis-Dennis": 1,
    "Leon Black": 1,
    LESLEY_GROFF: 106,
    "Lilly Sanchez": 4,
    "Linda Pinto": 1,
    LINDA_STONE: 19,
    'LinkedIn': 4,
    "Lisa New": 22,
    "Lisa Randall": 2,
    'LSJ': 1,  # TODO: this is epstein?
    "Manuela Martinez": 1,
    "Marc Leon": 2,
    MARIYA_PRUSAKOVA: 6,
    MARK_EPSTEIN: 6,
    "Mark Green": 1,
    MARK_TRAMO: 1,
    MARTIN_NOWAK: 1,
    "Martin Weinberg": 17,
    MASHA_DROKOVA: 12,
    MATTHEW_HILTZIK: 1,
    MELANIE_SPINELLA: 1,
    MELANIE_WALKER: 3,
    MERWIN_DELA_CRUZ: 1,
    "Michael Miller": 4,
    "Michael Sanka": 1,
    MICHAEL_WOLFF: 85,
    MIROSLAV_LAJCAK: 1,
    "Mitchell Bard": 2,
    MOHAMED_WAHEED_HASSAN: 2,
    MOSHE_HOFFMAN: 1,
    NADIA_MARCINKO: 5,
    NEAL_KASSELL: 2,
    'Newsmax': 1,
    NICHOLAS_RIBIS: 42,
    NICOLE_JUNKERMANN: 4,
    NOAM_CHOMSKY: 4,
    "Norman D. Rau": 1,
    OFFICE_OF_THE_DEPUTY_ATTORNEY_GENERAL: 1,
    "Olivier Colom": 1,
    "Paul Barrett": 4,
    PAUL_KRASSNER: 27,
    PAUL_MORRIS: 6,
    PAUL_PROSPERI: 3,
    PAULA: 2,
    'Paula Speer': 1,
    PEGGY_SIEGAL: 6,
    PETER_ATTIA: 2,
    "Peter Green": 1,
    "Peter Mandelson": 4,
    PETER_THIEL: 2,
    "Peter Thomas Roth": 2,
    "Philip Kafka": 1,
    PRINCE_ANDREW: 2,
    PUREVSUREN_LUNDEG: 1,
    "R. Couri Hay": 1,
    "Ramsey Elkholy": 1,
    'Records Management (Sun Sentinel?)': 1,
    REID_HOFFMAN: 1,
    REID_WEINGARTEN: 72,
    RENATA_BOLOTOVA: 55,
    RICHARD_KAHN: 155,
    "Richard Merkin": 3,
    ROBERT_LAWRENCE_KUHN: 26,
    ROBERT_TRIVERS: 15,
    "Ross Gow": 1,
    "Roy Black": 3,
    "Scott J. Link": 2,
    'SDNY': 1,
    SEAN_BANNON: 3,
    "Sean J. Lancaster": 1,
    SERGEY_BELYAKOV: 7,
    'Seth Lloyd': 1,
    SHAHER_ABDULHAK_BESHER: 3,
    "Skip Rimer": 1,
    SOON_YI_PREVIN: 9,
    STACEY_RICHMAN: 1,
    "Stanley Rosenberg": 3,
    "Stephanie": 2,
    "Stephen Alexander": 1,
    STEPHEN_HANSON: 5,
    STEVE_BANNON: 44,
    "Steven Elkman": 1,
    STEVEN_HOFFENBERG: 1,
    "Steven Pfeiffer": 2,
    STEVEN_SINOFSKY: 5,
    "Steven Victor MD": 1,
    SULTAN_BIN_SULAYEM: 12,
    TERJE_ROD_LARSEN: 3,
    TERRY_KAFKA: 8,
    THORBJORN_JAGLAND: 7,
    "Tim Zagat": 1,
    TOM_BARRACK: 1,
    TOM_PRITZKER: 6,
    TONJA_HADDAD_COLEMAN: 5,
    TYLER_SHEARS: 19,
    USANYS: 72,
    'USMS': 1,
    VALAR_VENTURES: 1,
    "Valeria Chomsky": 2,
    VINCENZO_IOZZO: 8,
    VINIT_SAHNI: 2,
    "Vladimir Yudashkin": 1,
    ZUBAIR_KHAN: 9,
    "asmallworld@travel.asmallworld.net": 2,
    "digest-noreply@quora.com": 5,
    "drsra": 1,
    "editorialstaff@flipboard.com": 13,
    JP_MORGAN_USGIO: 8,
    "lorraine@mc2mm.com": 1,
    "middle.east.update@hotmail.com": 1,
}

EMAIL_RECIPIENT_COUNTS = {
    None: 95,
    "ACT for America": 1,
    ADAM_BACK: 3,
    AL_SECKEL: 1,
    ALAN_DERSHOWITZ: 11,
    'Alan Dlugash': 1,
    "Alan Rogers": 1,
    'Alex Fowler': 1,
    'Alexandra Elenowitz-Hess': 1,
    ALIREZA_ITTIHADIEH: 2,
    ALISON_J_NATHAN: 3,
    "Allen West": 1,
    AMANDA_ENS: 1,
    'Amanda Kirby': 1,
    AMIR_TAAKI: 5,
    ANAS_ALRASHEED: 6,
    ANDREW_FARKAS: 6,
    "Andrew Friendly": 1,
    ANDREW_MCCORMACK: 16,
    'Andrew Stemmer': 2,
    "Anil Ambani": 1,
    "Ann Marie Villafana": 3,
    "Anthony Barrett": 1,
    ARIANE_DE_ROTHSCHILD: 3,
    'Ariane Dwyer': 1,
    ATT_COURT_APPEARANCE_TEAM: 1,
    AUSTIN_HILL: 22,
    'Barb Cowles': 1,
    "Barnaby Marsh": 2,
    'Bella Klein': 1,
    "Bennet Greenwald": 1,
    "Bennet Moskowitz": 1,
    "Bennett Schmidt": 1,
    BILL_GATES: 2,
    'Bill Gross': 1,
    "Bill Siegel": 1,
    'Bob Fass': 1,
    BOBBI_C_STERNHEIM: 2,
    BORIS_NIKOLIC: 10,
    BRAD_EDWARDS: 1,
    BRAD_KARP: 6,
    BRAD_WECHSLER: 2,
    'Brittany Henderson': 1,
    BROCK_PIERCE: 26,
    BRYAN_BISHOP: 1,
    BUREAU_OF_PRISONS: 1,
    "Caroline Lang": 2,
    'Caryl Ratner': 2,
    CECILE_DE_JONGH: 2,
    CECILIA_STEEN: 1,
    'Charles Michael': 1,
    "Charlotte Abrams": 1,
    "Cheryl Kleen": 1,
    CHRISTIAN_EVERDELL: 2,
    CHRISTINA_GALBRAITH: 7,
    "Connie Zaguirre": 1,
    "Dan Fleuette": 1,
    'Daniel Dawson': 2,
    DANIEL_SIAD: 2,
    "Danny Goldberg": 5,
    'Daphne Wallace': 1,
    DARREN_INDYKE: 51,
    DAVID_BLAINE: 1,
    "David Grosof": 6,
    "David Haig": 2,
    "David Schoen": 3,
    "David Stern": 1,
    "Debbie Fein": 5,
    "Deepak Chopra": 1,
    "Diane Ziman": 1,
    'DOJ Inspector General': 1,
    DONALD_NORMAN: 2,
    DOUGLAS_WIGDOR: 6,
    "Ed Boyden": 1,
    ED_BOYLE: 1,
    EDWARD_JAY_EPSTEIN: 1,
    EHUD_BARAK: 3,
    ERIC_ROTH: 1,
    'Erika Engelson': 2,
    "Erika Kellerhals": 2,
    "Etienne Binant": 1,
    FAITH_KATES: 5,
    FBI: 4,
    "Forrest Miller": 1,
    "Francis Derby": 2,
    FRED_HADDAD: 3,
    GANBAT_CHULUUNKHUU: 8,
    "Gary Gross": 1,
    "George Krassner": 3,
    "Gerald Barton": 1,
    GERALD_LEFCOURT: 1,
    GHISLAINE_MAXWELL: 8,
    "Gianni Serazzi": 1,
    GLENN_DUBIN: 1,
    GORDON_GETTY: 2,
    "Grant J. Smith": 1,
    "Grant Seeger": 1,
    'Hammie Hill': 1,
    "Harry Fisch": 1,
    'Harry Shearer': 1,
    "Henry Hortenstine": 1,
    "Herb Goodman": 1,
    'Holly Krassner Dawson': 1,
    'Hongbo Bao': 1,
    'Ike Groff': 1,
    JABOR_Y: 8,
    "Jack Goldberger": 9,
    "Jack Lang": 3,
    JACK_SCAROLA: 2,
    "Jackie Perczek": 3,
    JAMES_FITZGERALD: 16,
    "James Ramsey": 1,
    "Janet Kafka": 1,
    JANUSZ_BANASIAK: 1,
    JAY_LEFKOWITZ: 3,
    'Jay Levin': 1,
    JEAN_HUGUEN: 2,
    JEAN_LUC_BRUNEL: 8,
    JEANNE_M_CHRISTENSEN: 8,
    JEFF_FULLER: 2,
    'Jeff Pagliuca': 4,
    JEFFREY_EPSTEIN: 1780,
    JEREMY_RUBIN: 7,
    JES_STALEY: 7,
    JESSICA_CADWELL: 3,
    "Joel": 3,
    "Joel Dunn": 1,
    "John Page": 1,
    "John Zouzelka": 1,
    JOI_ITO: 17,
    JOJO_FONTANILLA: 8,
    JONATHAN_FARKAS: 9,
    JOSCHA_BACH: 4,
    "Joseph Vinciguerra": 1,
    "Joshua Cooper Ramo": 1,
    JULIA_SANTOS: 1,
    'Justin Alfano': 1,
    KARYNA_SHULIAK: 3,
    KATHERINE_KEATING: 3,
    KATHRYN_RUEMMLER: 57,
    KEN_STARR: 9,
    "Kenneth E. Mapp": 1,
    "Kevin Bright": 4,
    LANDON_THOMAS: 52,
    'Lanny Swerdlow': 1,
    "Larry Cohen": 1,
    'Larry Sloman': 1,
    LARRY_SUMMERS: 39,
    'Laura Menninger': 3,
    LAWRANCE_VISOSKI: 9,
    LAWRENCE_KRAUSS: 11,
    "Leah Reis-Dennis": 1,
    'Lee Quarnstrom': 2,
    'Leo': 1,  # TODO: who is this?
    LEON_BLACK: 4,
    LESLEY_GROFF: 44,
    "Lilly Sanchez": 2,
    'LIMITED PARTNERS': 1,
    LINDA_STONE: 4,
    'Linda W. Grossman': 2,
    "Lisa Albert": 1,
    LISA_NEW: 14,
    'Lorenzo de Medici': 1,
    "Louella Rabuyo": 1,
    LYN_FONTANILLA: 12,
    'Lynnie Tofte Fass': 1,
    'Manhattan DA': 2,
    MARC_LEON: 1,
    "Marcie Brown": 1,
    MARIANA_IDZKOWSKA: 1,
    'Marie Moneysmith': 1,
    'Marites Tess McCorquodale': 1,
    MARIYA_PRUSAKOVA: 1,
    "Mark Albert": 1,
    MARK_EPSTEIN: 3,
    "Marshall Funk": 1,
    MARTIN_NOWAK: 1,
    MARTIN_WEINBERG: 25,
    MASHA_DROKOVA: 5,
    MATTHEW_HILTZIK: 1,
    "Matthew Schafer": 1,
    MELANIE_SPINELLA: 13,
    MELANIE_WALKER: 2,
    'Meredith Firetog': 4,
    MERWIN_DELA_CRUZ: 7,
    MICHAEL_BUCHHOLTZ: 2,
    'Michael Danchuk': 1,
    "Michael Horowitz": 1,
    "Michael J. Pike": 1,
    "Michael Simmons": 3,
    MICHAEL_SITRICK: 3,
    MICHAEL_WOLFF: 69,
    MIROSLAV_LAJCAK: 1,
    MOHAMED_WAHEED_HASSAN: 2,
    MORTIMER_ZUCKERMAN: 3,
    MOSHE_HOFFMAN: 1,
    'Mrisman02': 1,
    "Nadia Marcinko": 4,
    "Nancy Cain": 3,
    "Nancy Dahl": 2,
    "Nancy Portland": 2,
    "Nate McClain": 1,
    "Nate White": 1,
    "Neal Kassell": 1,
    "Neil Anderson": 1,
    NICHOLAS_RIBIS: 10,
    NICOLE_JUNKERMANN: 7,
    'Nick Kazan': 1,
    "Nili Priell Barak": 1,  # Wife of Ehud
    "Noam Chomsky": 2,
    "Norman Finkelstein": 1,
    'NY FBI': 3,
    OFFICE_OF_THE_DEPUTY_ATTORNEY_GENERAL: 2,
    "Oliver Goodenough": 1,
    "Owen Blicksilver": 1,
    PAUL_BARRETT: 2,
    PAUL_KRASSNER: 7,
    PAUL_MORRIS: 1,
    PAULA: 5,
    PEGGY_SIEGAL: 11,
    "Peter Aldhous": 2,
    "Peter Mandelson": 4,
    PETER_THIEL: 7,
    "Philip Kafka": 3,
    'Players2': 1,
    "Police Code Enforcement": 1,
    PRINCE_ANDREW: 2,
    'PROSPECTIVE INVESTORS': 2,  # TODO: what is this
    RAAFAT_ALSABBAGH: 2,
    "Rafael Bardaji": 1,
    'Rebecca Risman': 1,
    'Records Management Division': 1,
    REID_HOFFMAN: 3,
    REID_WEINGARTEN: 33,
    RENATA_BOLOTOVA: 15,
    'Reuben Kobulnik': 2,
    "Richard Barnnet": 1,
    "Richard Joshi": 1,
    RICHARD_KAHN: 61,
    "Richard Merkin": 1,
    "Rita Hortenstine": 1,
    ROBERT_D_CRITTON_JR: 6,
    "Robert Gold": 1,
    ROBERT_LAWRENCE_KUHN: 2,
    ROBERT_TRIVERS: 3,
    ROGER_SCHANK: 2,
    "Roy Black": 4,
    "Sam Harris": 1,
    SAMUEL_LEFF: 2,
    "Scott J. Link": 1,
    'SDNY': 1,
    SEAN_BANNON: 1,
    "Sean T Lehane": 1,
    SERGEY_BELYAKOV: 3,
    'Seth Lloyd': 1,
    SOON_YI_PREVIN: 4,
    STACEY_RICHMAN: 1,
    "Stanley Rosenberg": 1,
    "Stephen Hanson": 3,
    "Stephen Rubin": 1,
    STEVE_BANNON: 32,
    "Steven Gaydos": 2,
    "Steven Pfeiffer": 1,
    STEVEN_SINOFSKY: 1,
    'Steven Victor MD': 1,
    'Story Cowles': 1,
    SULTAN_BIN_SULAYEM: 12,
    "Susan Edelman": 1,
    "Taal Safdie": 1,
    "Terry Kafka": 1,
    "Thanu Boonyawatana": 1,
    THORBJORN_JAGLAND: 8,
    "Tim Kane": 1,
    "Tim Zagat": 1,
    "Tom": 2,
    TOM_BARRACK: 2,
    TOM_PRITZKER: 9,
    TONJA_HADDAD_COLEMAN: 3,
    "Travis Pangburn": 1,
    TYLER_SHEARS: 7,
    'USAHUB-USAJournal111': 1,
    "Uri Fouzailov": 1,
    USANYS: 62,
    'USMS': 1,
    "Vahe Stepanian": 1,
    "Val Sherman": 1,
    "Valeria Chomsky": 1,
    'Vijay Dewan': 2,
    VINCENZO_IOZZO: 3,
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
    "pink@mc2mm.com": 2,
    "Alan Rogers": 1,
    'Alisa Bekins': 1,
    "Anna Dreber": 1,
    "Anula Jayasuriya": 1,
    "Bill Prezant": 1,
    "Bobby McCormick": 1,
    "Clive Crook": 1,
    "Dane Stangler": 1,
    "Ron Bailey": 1,
    "Ditsa Pines": 1,
    "David Darst": 1,
    "Gerry Ohrstrom": 1,
    "Paul Romer": 1,
    "John Mallen": 1,
    "Jim Halligan": 1,
    "Lee Silver": 1,
    'Lorenz Ehrsam': 2,
    "Monika Gruter Cheney": 1,
    "Marguerite Atkins": 1,
    "Matt Ridley": 1,
    "Mike Cagney": 1,
    "Evan Smith": 1,
    "Roger Edelen": 1,
    "Oliver Goodenough": 1,
    "Paul Zak": 1,
    "Peter J Richerson": 1,
    "Clair Brown": 1,
    "Terry Anderson": 1,
    "Tim Kane": 1,
    "Rob Hanson": 1,
    "president@usfca.edu": 1,
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
    '029976',
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
    '032951',
    "033345",
    '033386',
    '033599',
    'EFTA00039665',
    'EFTA00039689',
    'EFTA00039799',
    'EFTA00039802',
    'EFTA00039806',
    'EFTA00039809',
    'EFTA00039828',
    'EFTA00039867',
    'EFTA00039879',
    'EFTA00039893',
    'EFTA00039894',
    'EFTA00039965',
    'EFTA00039995',
    'EFTA00040105',
    'EFTA00040118',
    'EFTA00040141',
    'EFTA00040144',
    'EFTA00080250',
    'EFTA00093702',
    'EFTA00381451',
    'EFTA00419486',
    'EFTA00428084',
    'EFTA00888467',
    'EFTA01013922',
    'EFTA01823635',
    'EFTA01932234',
    'EFTA01950559',
    'EFTA02160715',
    'EFTA02227488',
    'EFTA02229858',
    'EFTA02285514',
    'EFTA02304891',
    'EFTA02318365',
    'EFTA02328335',
    'EFTA02565917',
    'EFTA02730468',
    'EFTA02730469',
    'EFTA02730471',
    'EFTA02730481',
    'EFTA02730483',
    'EFTA02730485',
    'EFTA02731473',
    'EFTA02731479',
    'EFTA02731482',
    'EFTA02731488',
    'EFTA02731526',
    'EFTA02731578',
    'EFTA02731628',
    'EFTA02731648',
    'EFTA02731655',
    'EFTA02731662',
    'EFTA02731687',
    'EFTA02731713',
    'EFTA02731718',
    'EFTA02731724',
    'EFTA02731727',
    'EFTA02731732',
    'EFTA02731733',
    'EFTA02731734',
    'EFTA02731735',
    'EFTA02731754',
    'EFTA02731765',
    'EFTA02731774',
    'EFTA02731781',
    'EFTA02731783',
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
        "Sent from my iPhone",
    ],
    'Audrey Strauss': [
        "Sent from my iPhone",
    ],
    AUSTIN_HILL: [
        'Sent from Mailbox for iPad',
        'Sent from Mailbox for iPhone',
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
    BROCK_PIERCE: [
        'Sent from my iPad',
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
    KARYNA_SHULIAK: [
        'Sent from my iPhone',
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
        'Typos, misspellings courtesy of iPhone',
        'Typos, misspellings courtesy of iPhone word & thought substitution.',
        'Typos, misspellings courtesy of iPhone.',
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
    PEGGY_SIEGAL: [
        "Sent from my iPad",
    ],
    PUREVSUREN_LUNDEG: [
        'Sent from my iPad',
    ],
    "Reid Weingarten": [
        "Sent from my BlackBerry 10 smartphone.",
    ],
    RENATA_BOLOTOVA: [
        "Sent from my iPad",
        "Sent from my iPhone"
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
    STACEY_RICHMAN: [
        "Sent from my iPhone"
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
    STEVEN_SINOFSKY: [
        'Sent from Windows Mail',
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
    TYLER_SHEARS: [
        "Sent from my iPhone"
    ],
    USANYS: [
        "Sent from my iPhone"
    ],
    VINCENZO_IOZZO: [
        "Sent from my Iphone"
    ]
}

SIGNATURE_SUBSTITUTION_COUNTS = {
    "(unknown)": 2,
    BARBRO_C_EHNBOM: 5,
    BRAD_KARP: 5,
    ARIANE_DE_ROTHSCHILD: 4,
    BROCK_PIERCE: 99,
    DANIEL_SIAD: 5,
    "Danny Frost": 8,
    DARREN_INDYKE: 47,
    DAVID_FISZEL: 2,
    "David Ingram": 9,
    DEEPAK_CHOPRA: 19,
    EDUARDO_ROBLES: 6,
    ERIC_ROTH: 5,
    GHISLAINE_MAXWELL: 13,
    JEANNE_M_CHRISTENSEN: 37,
    JEFFREY_EPSTEIN: 3778,
    JESSICA_CADWELL: 57,
    KEN_JENNE: 1,
    LARRY_SUMMERS: 233,
    "Lawrence Krauss": 78,
    LEON_BLACK: 4,
    LISA_NEW: 68,
    "Martin Weinberg": 17,
    'Michael Miller': 6,
    NICHOLAS_RIBIS: 2,
    "Paul Barrett": 10,
    PETER_ATTIA: 3,
    "Peter Mandelson": 10,
    RICHARD_KAHN: 184,
    ROSS_GOW: 7,
    'Stephen Hanson': 2,
    STEVEN_PFEIFFER: 11,
    "Susan Edelman": 9,
    "Terry Kafka": 10,
    TOM_PRITZKER: 17,
    "Tonja Haddad Coleman": 9,
    'W Bradford Stephens': 2,
}


def test_email_author_counts(epstein_files):
    assert epstein_files.email_author_counts() == EMAIL_AUTHOR_COUNTS


def test_email_recipient_counts(epstein_files):
    assert epstein_files.email_recipient_counts() == EMAIL_RECIPIENT_COUNTS


def test_info_sentences(epstein_files):
    email = epstein_files.for_ids('026290')[0]
    assert len(email.info) == 1
    email_with_description = epstein_files.for_ids('031278')[0]
    assert len(email_with_description.info) == 2


def test_signatures(epstein_files):
    assert dict_sets_to_lists(epstein_files.email_authors_to_device_signatures()) == AUTHORS_TO_DEVICE_SIGNATURES
    assert dict_sets_to_lists(epstein_files.email_device_signatures_to_authors()) == DEVICE_SIGNATURE_TO_AUTHORS


def test_signature_substitutions(epstein_files):
    assert epstein_files.email_signature_substitution_counts() == SIGNATURE_SUBSTITUTION_COUNTS


def test_unknown_recipient_file_ids(epstein_files):
    assert epstein_files.unknown_recipient_ids() == UNKNOWN_RECIPIENT_FILE_IDS


def test_border_style(epstein_files):
    email = epstein_files.email_for_id('033071')
    assert email.border_style == 'purple'
    assert email.author_style == 'blue1'


def test_is_fwded_article(epstein_files):
    fwded_article = epstein_files.email_for_id('033311')
    assert fwded_article.is_word_count_worthy is False
    non_article_with_fwd_text = epstein_files.email_for_id('012197_4')
    assert non_article_with_fwd_text.is_fwded_article is False
    assert non_article_with_fwd_text.is_word_count_worthy is True
    article_with_fwd_text = epstein_files.email_for_id('016413')
    assert article_with_fwd_text.is_fwded_article is True
    assert article_with_fwd_text.is_word_count_worthy is True


def test_broken_header_repair(epstein_files):
    broken_email = epstein_files.email_for_id('032213')
    assert broken_email.actual_text == 'https://www.thedailybeast.com/how-close-is-donald-trump-to-a-psychiatric-breakdown?ref=home\n<...snipped jeffrey epstein legal signature...>'
    assert broken_email.header.num_header_rows == 5
