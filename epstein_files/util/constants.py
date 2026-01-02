import re
from copy import deepcopy

from dateutil.parser import parse

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.file_cfg import MessageCfg, FileCfg

# Misc
FALLBACK_TIMESTAMP = parse("1/1/2051 12:01:01 AM")
RESUME_OF = 'professional resumé of'
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
    'bgC3': 'Bill Gates Ventures (renamed in 2018)',
    "Brock": 'Brock Pierce (crypto bro with a very sordid past)',
    "DB": "Deutsche Bank (maybe??)",
    'HBJ': "Sheikh Hamad bin Jassim (former Qatari prime minister)",
    'Jabor': '"an influential man in Qatar"',
    'Jared': "Jared Kushner",
    'Jagland': 'Thorbjørn Jagland (former Norwegian prime minister)',
    'JEGE': "Epstein's airplane holding company",
    'Jeffrey Wernick': 'right wing crypto bro, former COO of Parler',
    'Joi': 'Joi Ito (MIT Media Lab, MIT Digital Currency Initiative)',
    "Hoffenberg": "Steven Hoffenberg (Epstein's ponzi scheme partner)",
    'KSA': "Kingdom of Saudi Arabia",
    'Kurz': 'Sebastian Kurz (former Austrian Chancellor)',
    'Kwok': "Chinese criminal Miles Kwok AKA Miles Guo AKA Guo Wengui",
    'LSJ': "Epstein's private island holding company",
    'Madars': 'Madars Virza (co-founder of privacy crypto ZCash)',
    'Mapp': f'{KENNETH_E_MAPP} (Governor of {VIRGIN_ISLANDS})',
    'Masa': 'Masayoshi Son (Softbank)',
    'MBS': "Mohammed bin Salman Al Saud (Saudi ruler)",
    'MBZ': "Mohamed bin Zayed Al Nahyan (Emirates sheikh)",
    "Miro": MIROSLAV_LAJCAK,
    "Mooch": "Anthony 'The Mooch' Scaramucci (Skybridge crypto bro)",
    "Terje": TERJE_ROD_LARSEN,
    "VI": f"U.S. {VIRGIN_ISLANDS}",
    "Woody": "Woody Allen",
    "Zug": "City in Switzerland (crypto hub)",
}


#######################
# Emails Config Stuff #
#######################

# Emailers
EMAILER_ID_REGEXES: dict[str, re.Pattern] = {
    ALAN_DERSHOWITZ: re.compile(r'(alan.{1,7})?dershowi(lz?|tz)|AlanDersh', re.IGNORECASE),
    ALIREZA_ITTIHADIEH: re.compile(r'Alireza.[Il]ttihadieh', re.IGNORECASE),
    AMANDA_ENS: re.compile(r'ens, amanda?|Amanda.Ens', re.IGNORECASE),
    ANIL_AMBANI: re.compile(r'Anil.Ambani', re.IGNORECASE),
    ANN_MARIE_VILLAFANA: re.compile(r'Villafana, Ann Marie|(A(\.|nn) Marie )?Villafa(n|ri)a', re.IGNORECASE),
    ARIANE_DE_ROTHSCHILD: re.compile(r'AdeR|((Ariane|Edmond) de )?Rothschild|Ariane', re.IGNORECASE),
    ANAS_ALRASHEED: re.compile(r'anas\s*al\s*rashee[cd]', re.IGNORECASE),
    BARBRO_C_EHNBOM: re.compile(r'behnbom@aol.com|(Barbro\s.*)?Ehnbom', re.IGNORECASE),
    BARRY_J_COHEN: re.compile(r'barry\s*((j.?|james)\s*)?cohen?', re.IGNORECASE),
    BENNET_MOSKOWITZ: re.compile(r'Moskowitz.*Bennet|Bennet.*Moskowitz', re.IGNORECASE),
    BORIS_NIKOLIC: re.compile(r'(boris )?nikolic?', re.IGNORECASE),
    BRAD_EDWARDS:  re.compile(r'Brad(ley)?(\s*J(.?|ames))?\s*Edwards', re.IGNORECASE),
    BRAD_KARP: re.compile(r'Brad (S.? )?Karp|Karp, Brad', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterprise?', re.IGNORECASE),
    DANNY_FROST: re.compile(r'Frost, Danny|frostd@dany.nyc.gov', re.IGNORECASE),
    DARREN_INDYKE: re.compile(r'darren$|Darren\s*(K\.?\s*)?[il]n[dq]_?yke?|dkiesq', re.IGNORECASE),
    DAVID_FISZEL: re.compile(r'David\s*Fis?zel', re.IGNORECASE),
    DAVID_STERN: re.compile(r'David Stern?', re.IGNORECASE),
    EDUARDO_ROBLES: re.compile(r'Ed(uardo)?\s*Robles', re.IGNORECASE),
    EDWARD_JAY_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|e?h)\s*barak|\behud', re.IGNORECASE),
    FAITH_KATES: re.compile(r'faith kates?', re.IGNORECASE),
    GERALD_BARTON: re.compile(r'Gerald.*Barton', re.IGNORECASE),
    GERALD_LEFCOURT: re.compile(r'Gerald\s*(B\.?\s*)?Lefcourt', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?|Ghislaine|Maxwell', re.IGNORECASE),
    HEATHER_MANN: re.compile(r'Heather Mann?', re.IGNORECASE),
    INTELLIGENCE_SQUARED: re.compile(r'intelligence\s*squared', re.IGNORECASE),
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
    LAWRANCE_VISOSKI: re.compile(r'La(rry|wrance) Visoski?|Lvjet', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus|lawkrauss', re.IGNORECASE),
    LEON_BLACK: re.compile(r'Leon Black?', re.IGNORECASE),
    MANUELA_MARTINEZ: re.compile(fr'Manuela (- Mega Partners|Martinez)', re.IGNORECASE),
    MARIANA_IDZKOWSKA: re.compile(r'Mariana [Il]d[źi]kowska?', re.IGNORECASE),
    MARK_EPSTEIN: re.compile(r'Mark (L\. )?Epstein', re.IGNORECASE),
    LILLY_SANCHEZ: re.compile(r'Lilly.*Sanchez', re.IGNORECASE),
    LISA_NEW: re.compile(r'E?Lisa New?\b', re.IGNORECASE),
    MARC_LEON: re.compile(r'Marc[.\s]+(Kensington|Leon)|Kensington2', re.IGNORECASE),
    MARTIN_NOWAK: re.compile(r'(Martin.*?)?No[vw]ak|Nowak, Martin', re.IGNORECASE),
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
    NICHOLAS_RIBIS: re.compile(r'Nic(holas|k)[\s._]Ribi?s?|Ribbis', re.IGNORECASE),
    OLIVIER_COLOM: re.compile(fr'Colom, Olivier|{OLIVIER_COLOM}', re.IGNORECASE),
    PAUL_BARRETT: re.compile(r'Paul Barre(d|tt)', re.IGNORECASE),
    PAUL_KRASSNER: re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    PAUL_MORRIS: re.compile(r'morris, paul|Paul Morris', re.IGNORECASE),
    PAULA: re.compile(r'^Paula( Heil Fisher)?$', re.IGNORECASE),
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
    SOON_YI_PREVIN: re.compile(r'Soon[- ]Yi Previn?', re.IGNORECASE),
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

# Add simple matching regexes for EMAILERS entries to EMAILER_REGEXES
for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer, re.IGNORECASE)

# Some emails have a lot of uninteresting CCs
IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS: list[str | None] = ['Allen West', 'Rafael Bardaji', 'Philip Kafka', 'Herb Goodman', 'Grant Seeger', 'Lisa Albert', 'Janet Kafka', 'James Ramsey', 'ACT for America', 'John Zouzelka', 'Joel Dunn', 'Nate McClain', 'Bennet Greenwald', 'Taal Safdie', 'Uri Fouzailov', 'Neil Anderson', 'Nate White', 'Rita Hortenstine', 'Henry Hortenstine', 'Gary Gross', 'Forrest Miller', 'Bennett Schmidt', 'Val Sherman', 'Marcie Brown', 'Michael Horowitz', 'Marshall Funk']
KRASSNER_MANSON_RECIPIENTS: list[str | None] = ['Nancy Cain', 'Tom', 'Marie Moneysmith', 'Steven Gaydos', 'George Krassner', 'Linda W. Grossman', 'Holly Krassner Dawson', 'Daniel Dawson', 'Danny Goldberg', 'Caryl Ratner', 'Kevin Bright', 'Michael Simmons', SAMUEL_LEFF, 'Bob Fass', 'Lynnie Tofte Fass', 'Barb Cowles', 'Lee Quarnstrom']
KRASSNER_024923_RECIPIENTS: list[str | None] = ['George Krassner', 'Nick Kazan', 'Mrisman02', 'Rebecca Risman', 'Linda W. Grossman']
KRASSNER_033568_RECIPIENTS: list[str | None] = ['George Krassner', 'Daniel Dawson', 'Danny Goldberg', 'Tom', 'Kevin Bright', 'Walli Leff', 'Michael Simmons', 'Lee Quarnstrom', 'Lanny Swerdlow', 'Larry Sloman', 'W&K', 'Harry Shearer', 'Jay Levin']
FLIGHT_IN_2012_PEOPLE: list[str | None] = ['Francis Derby', 'Januiz Banasiak', 'Louella Rabuyo', 'Richard Barnnet']


##########################
# OtherFile Config Stuff #
##########################
BOOK = 'book:'
FBI = 'FBI'
FLIGHT_LOGS = 'flight logs'
MEME = 'meme of'
PRESS_RELEASE = 'press release'
REPUTATION_MGMT = 'reputation management:'
SCREENSHOT = 'screenshot of'
TRANSLATION = 'translation of'
TWEET = 'tweet'
TEXT_OF_US_LAW = 'text of U.S. law:'

# Court cases
EDWARDS_V_DERSHOWITZ = f"{BRAD_EDWARDS} and {PAUL_G_CASSELL} v. {ALAN_DERSHOWITZ}"
EPSTEIN_V_ROTHSTEIN_AND_EDWARDS = f"Epstein v. Scott Rothstein, {BRAD_EDWARDS}, and L.M."
GIUFFRE_V_DERSHOWITZ = f"{VIRGINIA_GIUFFRE} v. {ALAN_DERSHOWITZ}"
GIUFFRE_V_EPSTEIN = f"{VIRGINIA_GIUFFRE} v. {JEFFREY_EPSTEIN}"
GIUFFRE_V_MAXWELL = f"{VIRGINIA_GIUFFRE} v. {GHISLAINE_MAXWELL}"
JANE_DOE_V_EPSTEIN_TRUMP = f"Jane Doe v. Donald Trump and {JEFFREY_EPSTEIN}"
JANE_DOE_V_USA = 'Jane Doe #1 and Jane Doe #2 v. United States'
NEW_YORK_V_EPSTEIN = f"New York v. {JEFFREY_EPSTEIN}"

# Descriptions of non-email, non-text message files
ARTICLE_DRAFT = 'draft of an article about'
BOFA = 'BofA'
BOFA_MERRILL = f'{BOFA} / Merrill Lynch Report'
BOFA_WEALTH_MGMT = f'{BOFA} Wealth Management'
CHALLENGES_OF_AI = f'ASU Origins Project ({LAWRENCE_KRAUSS}) report "Challenges of AI: Envisioning and Addressing Adverse Outcomes"'
CHINA_DAILY_ARTICLE = "China Daily article about"
CVRA = "Crime Victims' Rights Act [CVRA]"
DAILY_MAIL_ARTICLE = "Daily Mail article about"
DAILY_TELEGRAPH_ARTICLE = "Daily Telegraph article about"
DAVID_BLAINE_VISA_LETTER = f"{DAVID_BLAINE} letter of recommendation for visa for a model"
DAVID_SCHOEN_CVRA_LEXIS_SEARCH = f"Lexis Nexis search for case law around the {CVRA} by {DAVID_SCHOEN} 2019-02-28"
DEEP_THINKING_HINT = f'{BOOK} "Deep Thinking: Twenty-Five Ways of Looking at AI" by John Brockman 2019-02-19'
DERSH_GIUFFRE_TWEET = f"{TWEET} by {ALAN_DERSHOWITZ} about {VIRGINIA_GIUFFRE}"
DEUTSCHE_BANK_TAX_TOPICS = f'{DEUTSCHE_BANK} Wealth Management Tax Topics'
DIANA_DEGETTES_CAMPAIGN = "Colorado legislator Diana DeGette's campaign"
EPSTEIN_FOUNDATION = 'Jeffrey Epstein VI Foundation'
FBI_REPORT = f"{FBI} report on Epstein investigation (redacted)"
FBI_SEIZED_PROPERTY = f"{FBI} seized property inventory (redacted)"
FEMALE_HEALTH_COMPANY = 'Female Health Company (FHX)'
FIRE_AND_FURY = f'"Fire And Fury" by {MICHAEL_WOLFF} 2018-01-05'
GOLDMAN_REPORT = f'{GOLDMAN_SACHS} Investment Management Division report'
HARVARD_POETRY = f'{HARVARD} poetry stuff from {LISA_NEW}'
HBS_APPLICATION_NERIO = f"{HARVARD} Business School application letter from Nerio Alessandri (Founder and Chairman Technogym SPA Italy)"
INSIGHTS_POD = f"{ZUBAIR_KHAN} and Anya Rasulova's InsightsPod"
JASTA = 'JASTA'
JASTA_SAUDI_LAWSUIT = f"{JASTA} lawsuit against Saudi Arabia by 9/11 victims"
JOHN_BOLTON_PRESS_CLIPPING = 'John Bolton press clipping'
JP_MORGAN_EYE_ON_THE_MARKET = f"{JP_MORGAN} Eye On The Market report"
KEN_STARR_LETTER = f"letter from {KEN_STARR} to judge overseeing Epstein's criminal prosecution, mentions Alex Acosta"
MERCURY_FILMS_PROFILES = f'Mercury Films partner profiles of Jennifer Baichwal, Nicholas de Pencier, Kermit Blackwood, Travis Rummel'
MICHAEL_WOLFF_ARTICLE_HINT = f"draft of an unpublished article about Epstein by {MICHAEL_WOLFF} written ca. 2014/2015"
NATIONAL_ENQUIRER_FILING = f"National Enquirer / Radar Online v. FBI FOIA lawsuit court filing"
NIGHT_FLIGHT_HINT = f'draft of book named "Night Flight" by {EHUD_BARAK}?'
NOBEL_CHARITABLE_TRUST = 'Nobel Charitable Trust'
OBAMA_JOKE = 'joke about Obama'
OSBORNE_LLP = f"{IAN_OSBORNE} & Partners LLP"
PALM_BEACH = 'Palm Beach'
PALM_BEACH_CODE_ENFORCEMENT = f'{PALM_BEACH} code enforcement board minutes'
PALM_BEACH_DAILY_ARTICLE = f'{PALM_BEACH} Daily News article about'
PALM_BEACH_POST_ARTICLE = f'{PALM_BEACH} Post article about'
PALM_BEACH_TSV = f"TSV of {PALM_BEACH} property"
PALM_BEACH_WATER_COMMITTEE = f'{PALM_BEACH} Water Committee'
PATTERSON_BOOK_SCANS = f'{BOOK} pages of "Filthy Rich: The Shocking True Story of {JEFFREY_EPSTEIN}" by James Patterson 2016-10-10'
SHIMON_POST = 'The Shimon Post'
SHIMON_POST_ARTICLE = f'{SHIMON_POST} selection of articles about the mideast'
SINGLE_PAGE = 'single page of'
SWEDISH_LIFE_SCIENCES_SUMMIT = f"{BARBRO_C_EHNBOM}'s Swedish American Life Science Summit"
THE_REAL_DEAL_ARTICLE = 'The Real Deal article by Keith Larsen'
TRUMP_DISCLOSURES = f"Donald Trump financial disclosures from U.S. Office of Government Ethics 2017-01-20"
UBS_CIO_REPORT = 'UBS CIO Monthly Extended report'
VI_DAILY_NEWS_ARTICLE = f'{VIRGIN_ISLANDS} Daily News article'
WAPO = 'WaPo'
WEINBERG_ABC_LETTER = f"letter from {MARTIN_WEINBERG} to ABC / Good Morning America threatening libel lawsuit"
WOMEN_EMPOWERMENT = f"Women Empowerment (WE) conference run by {SVETLANA_POZHIDAEVA}"

# Atribution reasons
BOLOTOVA_REASON = 'Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")'
PAULA_REASON = 'Signature of "Sent via BlackBerry from T-Mobile"'

UNINTERESTING_PREFIXES = [
    'article about',
    ARTICLE_DRAFT,
    'Aviation International',
    BBC,
    BLOOMBERG,
    BOFA,
    BOFA_MERRILL,
    BOOK,
    'Boston Globe',
    'Brockman',
    CHALLENGES_OF_AI,
    CHINA_DAILY_ARTICLE,
    CNN,
    'completely redacted',
    CVRA,
    DAILY_MAIL_ARTICLE,
    DAILY_TELEGRAPH_ARTICLE,
    DAVID_SCHOEN_CVRA_LEXIS_SEARCH[0:-12],  # Because date at end :(
    DEEP_THINKING_HINT,
    DERSH_GIUFFRE_TWEET,
    DEUTSCHE_BANK,
    'Forbes',
    'fragment',
    'Frontlines',
    'Future Science',
    'Globe and Mail',
    GOLDMAN_REPORT,
    GORDON_GETTY,
    f"{HARVARD} Econ",
    HARVARD_POETRY,
    'Inference',
    'Invesco',
    JASTA,
    'JetGala',
    JOHN_BOLTON_PRESS_CLIPPING,
    'Journal of Criminal',
    JP_MORGAN,
    LA_TIMES,
    'Litigation Daily',
    'MarketWatch',
    MEME,
    'Morgan Stanley',
    NOBEL_CHARITABLE_TRUST,
    'Nautilus',
    'New Yorker',
    NIGHT_FLIGHT_HINT,
    NYT_ARTICLE,
    NYT_COLUMN,
    OBAMA_JOKE,
    PALM_BEACH_CODE_ENFORCEMENT,
    PALM_BEACH_DAILY_ARTICLE,
    PALM_BEACH_POST_ARTICLE,
    PALM_BEACH_TSV,
    PALM_BEACH_WATER_COMMITTEE,
    PAUL_KRASSNER,
    PEGGY_SIEGAL,
    'Politifact',
    'Rafanelli',
    REDACTED,
    ROBERT_LAWRENCE_KUHN,
    ROBERT_TRIVERS,
    'S&P',
    'SciencExpress',
    'Scowcroft',
    SHIMON_POST_ARTICLE,
    SINGLE_PAGE,
    STACEY_PLASKETT,
    TEXT_OF_US_LAW,
    TRANSLATION,
    TWEET,
    THE_REAL_DEAL_ARTICLE,
    TRUMP_DISCLOSURES,
    UBS_CIO_REPORT,
    'U.S. News',
    'US Office',
    'USA Inc',
    'Vanity Fair',
    VI_DAILY_NEWS_ARTICLE,
    WAPO,
]


# List containing anything manually configured about any of the files.
ALL_CONFIGS = [

        ####################################
        ############ TEXTS CONFIG ##########
        ####################################

    MessageCfg(id='031042', author=ANIL_AMBANI, attribution_reason='Participants: field'),
    MessageCfg(id='027225', author=ANIL_AMBANI, attribution_reason='Birthday mentioned and confirmed as Ambani\'s'),
    MessageCfg(id='031173', author=ARDA_BESKARDES, attribution_reason='Participants: field'),
    MessageCfg(id='027401', author='Eva (Dubin?)', attribution_reason='Participants: field'),
    MessageCfg(id='027650', author=JOI_ITO, attribution_reason='Participants: field'),
    MessageCfg(id='027777', author=LARRY_SUMMERS, attribution_reason='Participants: field'),
    MessageCfg(id='027515', author=MIROSLAV_LAJCAK, attribution_reason='https://x.com/ImDrinknWyn/status/1990210266114789713'),
    MessageCfg(id='027165', author=MELANIE_WALKER, attribution_reason='https://www.wired.com/story/jeffrey-epstein-claimed-intimate-knowledge-of-donald-trumps-views-in-texts-with-bill-gates-adviser/'),
    MessageCfg(id='027248', author=MELANIE_WALKER, attribution_reason='Says "we met through trump" which is confirmed by Melanie in 032803'),
    MessageCfg(id='025429', author=STACEY_PLASKETT),
    MessageCfg(id='027333', author=SCARAMUCCI, attribution_reason='unredacted phone number in one of the messages belongs to Scaramucci'),
    MessageCfg(id='027128', author=SOON_YI_PREVIN, attribution_reason='https://x.com/ImDrinknWyn/status/1990227281101434923'),
    MessageCfg(id='027217', author=SOON_YI_PREVIN, attribution_reason='refs marriage to woody allen'),
    MessageCfg(id='027244', author=SOON_YI_PREVIN, attribution_reason='refs Woody'),
    MessageCfg(id='027257', author=SOON_YI_PREVIN, attribution_reason="'Woody Allen' in Participants: field"),
    MessageCfg(id='027460', author=STEVE_BANNON, attribution_reason='Discusses leaving scotland when Bannon was confirmed in Scotland, also NYT'),
    MessageCfg(id='027307', author=STEVE_BANNON),
    MessageCfg(id='027278', author=TERJE_ROD_LARSEN),
    MessageCfg(id='027255', author=TERJE_ROD_LARSEN),
    MessageCfg(id='027762', author=ANDRZEJ_DUDA, is_author_uncertain=True),
    MessageCfg(id='027774', author=ANDRZEJ_DUDA, is_author_uncertain=True),
    MessageCfg(id='027221', author=ANIL_AMBANI, is_author_uncertain=True),
    MessageCfg(id='025436', author=CELINA_DUBIN, is_author_uncertain=True),
    MessageCfg(id='027576', author=MELANIE_WALKER, is_author_uncertain=True, attribution_reason='https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.023700'),
    MessageCfg(id='027141', author=MELANIE_WALKER, is_author_uncertain=True),
    MessageCfg(id='027232', author=MELANIE_WALKER, is_author_uncertain=True),
    MessageCfg(id='027133', author=MELANIE_WALKER, is_author_uncertain=True),
    MessageCfg(id='027184', author=MELANIE_WALKER, is_author_uncertain=True),
    MessageCfg(id='027214', author=MELANIE_WALKER, is_author_uncertain=True),
    MessageCfg(id='027148', author=MELANIE_WALKER, is_author_uncertain=True),
    MessageCfg(id='027396', author=SCARAMUCCI, is_author_uncertain=True),
    MessageCfg(id='031054', author=SCARAMUCCI, is_author_uncertain=True),
    MessageCfg(id='025363', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='Trump and New York Times coverage'),
    MessageCfg(id='025368', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='Trump and New York Times coverage'),
    MessageCfg(id='027585', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='Tokyo trip'),
    MessageCfg(id='027568', author=STEVE_BANNON, is_author_uncertain=True),
    MessageCfg(id='027695', author=STEVE_BANNON, is_author_uncertain=True),
    MessageCfg(id='027594', author=STEVE_BANNON, is_author_uncertain=True),
    MessageCfg(id='027720', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='first 3 lines of 027722'),
    MessageCfg(id='027549', author=STEVE_BANNON, is_author_uncertain=True),
    MessageCfg(id='027434', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='References Maher appearance'),
    MessageCfg(id='027764', author=STEVE_BANNON, is_author_uncertain=True),
    MessageCfg(id='027428', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='References HBJ meeting on 9/28 from other Bannon/Epstein convo'),
    MessageCfg(id='025400', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump NYT article criticism; Hannity media strategy'),
    MessageCfg(id='025408', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='025452', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='025479', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    MessageCfg(id='025707', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='025734', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    MessageCfg(id='027260', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027281', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027346', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027365', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027374', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says China strategy and geopolitics'),
    MessageCfg(id='027406', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027440', author=MICHAEL_WOLFF, is_author_uncertain=True, attribution_reason='AI says Trump book/journalism project'),
    MessageCfg(id='027445', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    MessageCfg(id='027455', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    MessageCfg(id='027536', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    MessageCfg(id='027655', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027707', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Italian politics; Trump discussions'),
    MessageCfg(id='027722', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027735', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='027794', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='029744', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),
    MessageCfg(id='031045', author=STEVE_BANNON, is_author_uncertain=True, attribution_reason='AI says Trump and New York Times coverage'),


        ####################################
        ############ EMAIL_INFO ############
        ####################################

    MessageCfg(id='022187', recipients=[JEFFREY_EPSTEIN]),
    MessageCfg(id='032436', author=ALIREZA_ITTIHADIEH, attribution_reason='Signature'),
    MessageCfg(id='032543', author=ANAS_ALRASHEED, attribution_reason='Later reply 033000 has quote'),
    MessageCfg(id='026064', author=ARIANE_DE_ROTHSCHILD),
    MessageCfg(id='026069', author=ARIANE_DE_ROTHSCHILD),
    MessageCfg(id='030741', author=ARIANE_DE_ROTHSCHILD),
    MessageCfg(id='026018', author=ARIANE_DE_ROTHSCHILD),
    MessageCfg(
        id='029504',
        author='Audrey/Aubrey Raimbault (???)',
        attribution_reason='(based on "GMI" in signature, a company registered by "aubrey raimbault")',
    ),
    MessageCfg(id='033316', author=AZIZA_ALAHMADI, attribution_reason='"Regards, Aziza" at bottom'),
    MessageCfg(id='033328', author=AZIZA_ALAHMADI, attribution_reason='"Regards, Aziza" at bottom'),
    MessageCfg(id='026659', author=BARBRO_C_EHNBOM, attribution_reason='Reply'),
    MessageCfg(id='026764', author=BARRY_J_COHEN),
    MessageCfg(id='031227', author=BENNET_MOSKOWITZ, dupe_of_id='031206'),
    MessageCfg(id='031442', author=CHRISTINA_GALBRAITH, duplicate_ids=['031996']),
    MessageCfg(
        id='019446',
        author=CHRISTINA_GALBRAITH,
        attribution_reason='Not 100% but from "Christina media/PR" which fits',
        is_author_uncertain=True,
    ),
    MessageCfg(id='026625', author=DARREN_INDYKE, actual_text='Hysterical.'),
    MessageCfg(
        id='026624',
        author=DARREN_INDYKE,
        recipients=[JEFFREY_EPSTEIN],
        timestamp=parse('2016-10-01 16:40:00'),
        duplicate_ids=['031708'],
    ),
    MessageCfg(
        id='031278',
        author=DARREN_INDYKE,
        description=f"heavily redacted email, quoted replies are from {STEVEN_HOFFENBERG} about James Patterson's book",  # Quoted replies are in 019109,
        timestamp=parse('2016-08-17 11:26:00'),
        attribution_reason='Quoted replies are in 019109',
    ),
    MessageCfg(id='026290', author=DAVID_SCHOEN, attribution_reason='Signature'),
    MessageCfg(id='031339', author=DAVID_SCHOEN, attribution_reason='Signature'),
    MessageCfg(id='031492', author=DAVID_SCHOEN, attribution_reason='Signature'),
    MessageCfg(id='031560', author=DAVID_SCHOEN, attribution_reason='Signature'),
    MessageCfg(id='026287', author=DAVID_SCHOEN, attribution_reason='Signature'),
    MessageCfg(id='033419', author=DAVID_SCHOEN, attribution_reason='Signature'),
    #MessageCfg(id='026245', author=DIANE_ZIMAN, recipients=[JEFFREY_EPSTEIN]),  # TODO: Shouldn't need to be configured
    MessageCfg(id='031460', author=EDWARD_JAY_EPSTEIN),
    MessageCfg(id='030578', author=FAITH_KATES, dupe_of_id='030414', dupe_type='redacted'),
    MessageCfg(
        id='030634',
        author=FAITH_KATES,
        dupe_of_id='031135',
        dupe_type='redacted',
        attribution_reason='Same as unredacted 031135, same legal signature',
    ),
    MessageCfg(id='026547', author=GERALD_BARTON, recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    MessageCfg(id='029969', author=GWENDOLYN_BECK, attribution_reason='Signature'),
    MessageCfg(id='029968', author=GWENDOLYN_BECK, attribution_reason='Signature', duplicate_ids=['031120']),
    MessageCfg(id='029970', author=GWENDOLYN_BECK),
    MessageCfg(id='029960', author=GWENDOLYN_BECK, attribution_reason='Reply'),
    MessageCfg(id='029959', author=GWENDOLYN_BECK, attribution_reason='"Longevity & Aging"'),
    MessageCfg(id='033360', author=HENRY_HOLT, attribution_reason='in signature'),  # Henry Holt is a company not a person
    MessageCfg(id='033384', author=JACK_GOLDBERGER, attribution_reason='Might be Paul Prosperi?'),
    MessageCfg(id='026024', author=JEAN_HUGUEN, attribution_reason='Signature'),
    MessageCfg(id='021823', author=JEAN_LUC_BRUNEL, attribution_reason='Reply'),
    MessageCfg(id='022949', author=JEFFREY_EPSTEIN),
    MessageCfg(id='031624', author=JEFFREY_EPSTEIN),
    MessageCfg(id='031996', author=JEFFREY_EPSTEIN, recipients=[CHRISTINA_GALBRAITH], attribution_reason='bounced', duplicate_ids=['031442']),
    MessageCfg(id='025041', author=JEFFREY_EPSTEIN, recipients=[LARRY_SUMMERS], duplicate_ids=['028675']),  # Bad OCR
    MessageCfg(
        id='029692',
        author=JEFFREY_EPSTEIN,
        is_fwded_article=True,  # Bad OCR, WaPo article
        recipients=[LARRY_SUMMERS],
        duplicate_ids=['029779'],
    ),
    MessageCfg(id='018726', author=JEFFREY_EPSTEIN, timestamp=parse('2018-06-08 08:36:00')),
    MessageCfg(id='032283', author=JEFFREY_EPSTEIN, timestamp=parse('2016-09-14 08:04:00')),
    MessageCfg(id='026943', author=JEFFREY_EPSTEIN, timestamp=parse('2019-05-22 05:47:00')),
    MessageCfg(id='023208', author=JEFFREY_EPSTEIN, recipients=[BRAD_WECHSLER, MELANIE_SPINELLA], duplicate_ids=['023291']),
    MessageCfg(
        id='032214',
        author=JEFFREY_EPSTEIN,
        actual_text='Agreed',
        recipients=[MIROSLAV_LAJCAK],
        attribution_reason='Quoted reply has signature',
    ),
    MessageCfg(id='029582', author=JEFFREY_EPSTEIN, recipients=[RENATA_BOLOTOVA], attribution_reason=BOLOTOVA_REASON),
    MessageCfg(id='030997', author=JEFFREY_EPSTEIN, actual_text='call back'),
    MessageCfg(id='028770', author=JEFFREY_EPSTEIN, actual_text='call me now'),
    MessageCfg(id='031826', author=JEFFREY_EPSTEIN, actual_text='I have'),
    MessageCfg(id='030768', author=JEFFREY_EPSTEIN, actual_text='ok'),
    MessageCfg(id='022938', author=JEFFREY_EPSTEIN, actual_text='what do you suggest?'),  # TODO: this email's header rewrite sucks
    MessageCfg(id='031791', author=JESSICA_CADWELL),
    MessageCfg(id='028851', author=JOI_ITO, recipients=[JEFFREY_EPSTEIN], timestamp=parse('2014-04-27 06:00:00')),
    MessageCfg(
        id='028849',
        author=JOI_ITO,
        recipients=[JEFFREY_EPSTEIN],
        timestamp=parse('2014-04-27 06:30:00'),
        attribution_reason='Conversation with Joi Ito',
    ),
    MessageCfg(id='016692', author=JOHN_PAGE),
    MessageCfg(id='016693', author=JOHN_PAGE),
    MessageCfg(id='028507', author=JONATHAN_FARKAS),
    MessageCfg(id='033282', author=JONATHAN_FARKAS, duplicate_ids=['033484']),
    MessageCfg(id='033582', author=JONATHAN_FARKAS, attribution_reason='Reply', duplicate_ids=['032389']),
    MessageCfg(id='033203', author=JONATHAN_FARKAS, attribution_reason='Reply', duplicate_ids=['033581']),
    MessageCfg(id='032052', author=JONATHAN_FARKAS, attribution_reason='Reply', duplicate_ids=['031732']),
    MessageCfg(id='033490', author=JONATHAN_FARKAS, attribution_reason='Signature', duplicate_ids=['032531']),
    MessageCfg(id='026652', author=KATHRYN_RUEMMLER),  # Bad OCR
    MessageCfg(id='032224', author=KATHRYN_RUEMMLER, recipients=[JEFFREY_EPSTEIN], attribution_reason='Reply'),
    MessageCfg(
        id='032386',
        author=KATHRYN_RUEMMLER,
        attribution_reason='from "Kathy" about dems, sent from iPad',
        is_author_uncertain=True
    ),
    MessageCfg(
        id='032727',
        author=KATHRYN_RUEMMLER,
        attribution_reason='from "Kathy" about dems, sent from iPad',
        is_author_uncertain=True
    ),
    MessageCfg(id='030478', author=LANDON_THOMAS),
    MessageCfg(id='029013', author=LARRY_SUMMERS, recipients=[JEFFREY_EPSTEIN]),
    MessageCfg(id='032206', author=LAWRENCE_KRAUSS, ),  # More of a text convo?
    MessageCfg(id='032208', author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN], ),  # More of a text convo?
    MessageCfg(id='032209', author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN], ),  # More of a text convo?
    MessageCfg(id='029196', author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN], actual_text='Talk in 40?'),  # TODO: this email's header rewrite sucks
    MessageCfg(id='027046', author=LAWRANCE_VISOSKI, duplicate_ids=['028789']),
    MessageCfg(id='033370', author=LAWRANCE_VISOSKI, attribution_reason='Planes discussion signed larry'),
    MessageCfg(id='033495', author=LAWRANCE_VISOSKI, attribution_reason='Planes discussion signed larry'),
    MessageCfg(id='033488', author=LAWRANCE_VISOSKI, duplicate_ids=['033154']),
    MessageCfg(id='033593', author=LAWRANCE_VISOSKI, attribution_reason='Signature'),
    MessageCfg(id='033487', author=LAWRANCE_VISOSKI, recipients=[JEFFREY_EPSTEIN]),
    MessageCfg(
        id='029977',
        author=LAWRANCE_VISOSKI,
        recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, LESLEY_GROFF, RICHARD_KAHN] + FLIGHT_IN_2012_PEOPLE,
        attribution_reason='Planes discussion signed larry',
        duplicate_ids=['031129'],
    ),
    MessageCfg(id='033309', author=LINDA_STONE, attribution_reason='"Co-authored with iPhone autocorrect"'),
    MessageCfg(id='017581', author='Lisa Randall'),
    MessageCfg(id='026609', author='Mark Green', attribution_reason='Actually a fwd'),
    MessageCfg(id='030472', author=MARTIN_WEINBERG, attribution_reason='Maybe. in reply', is_author_uncertain=True),
    MessageCfg(id='030235', author=MELANIE_WALKER, attribution_reason='In fwd'),
    MessageCfg(id='032343', author=MELANIE_WALKER, attribution_reason='Name seen in later reply 032346'),
    MessageCfg(id='032212', author=MIROSLAV_LAJCAK),
    MessageCfg(id='022193', author=NADIA_MARCINKO),
    MessageCfg(id='021814', author=NADIA_MARCINKO),
    MessageCfg(id='021808', author=NADIA_MARCINKO),
    MessageCfg(id='022214', author=NADIA_MARCINKO, attribution_reason='Reply header'),
    MessageCfg(id='022190', author=NADIA_MARCINKO),
    MessageCfg(id='021818', author=NADIA_MARCINKO),
    MessageCfg(id='022197', author=NADIA_MARCINKO),
    MessageCfg(id='021811', author=NADIA_MARCINKO, attribution_reason='Signature and email address in the message'),
    MessageCfg(id='028487', author=NORMAN_D_RAU, attribution_reason='Fwded from "to" address', duplicate_ids=['026612']),
    MessageCfg(id='024923', author=PAUL_KRASSNER, recipients=KRASSNER_024923_RECIPIENTS, duplicate_ids=['031973']),
    MessageCfg(id='032457', author=PAUL_KRASSNER),
    MessageCfg(id='029981', author=PAULA, attribution_reason='Name in reply + opera reference (Fisher now works in opera)'),
    MessageCfg(id='030482', author=PAULA, attribution_reason=PAULA_REASON),
    MessageCfg(id='033383', author=PAUL_PROSPERI, attribution_reason='Reply'),
    MessageCfg(
        id='033561',
        author=PAUL_PROSPERI,
        attribution_reason='Fwded mail sent to Prosperi. Might be Subotnick Stuart?',
        duplicate_ids=['033157'],
    ),
    MessageCfg(id='031694', author=PEGGY_SIEGAL),
    MessageCfg(id='032219', author=PEGGY_SIEGAL, attribution_reason='Signed "Peggy"'),
    MessageCfg(id='029020', author=RENATA_BOLOTOVA, attribution_reason='Signature'),
    MessageCfg(id='029605', author=RENATA_BOLOTOVA, attribution_reason=BOLOTOVA_REASON),
    MessageCfg(id='029606', author=RENATA_BOLOTOVA, attribution_reason=BOLOTOVA_REASON),
    MessageCfg(id='029604', author=RENATA_BOLOTOVA, attribution_reason='Continued in 239606 etc'),
    MessageCfg(
        id='033584',
        author=ROBERT_TRIVERS,
        recipients=[JEFFREY_EPSTEIN],
        attribution_reason='Refs paper by Trivers', duplicate_ids=['033169']
    ),
    MessageCfg(
        id='026320',
        author=SEAN_BANNON,
        attribution_reason="From protonmail, Bannon wrote 'just sent from my protonmail' in 027067",
    ),
    MessageCfg(id='029003', author='Soon-Yi Previn', attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    MessageCfg(id='029005', author='Soon-Yi Previn', attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    MessageCfg(id='029007', author='Soon-Yi Previn', attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    MessageCfg(id='029010', author='Soon-Yi Previn', attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    MessageCfg(id='032296', author='Soon-Yi Previn', attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    MessageCfg(
        id='019109',
        author=STEVEN_HOFFENBERG,
        recipients=["Players2"],
        timestamp=parse('2016-08-11 09:36:01'),
        attribution_reason='Actually a fwd by Charles Michael but Hofenberg email more interesting',
    ),
    MessageCfg(
        id='026620',
        author=TERRY_KAFKA,
        recipients=[JEFFREY_EPSTEIN, MARK_EPSTEIN, MICHAEL_BUCHHOLTZ] + IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS,
        attribution_reason='"Respectfully, terry"',
        duplicate_ids=['028482'],
    ),
    MessageCfg(id='029992', author=TERRY_KAFKA, attribution_reason='Quoted reply'),
    MessageCfg(id='029985', author=TERRY_KAFKA, attribution_reason='Quoted reply in 029992'),
    MessageCfg(id='020666', author=TERRY_KAFKA, attribution_reason="Ends with 'Terry'"),
    MessageCfg(id='026014', author=ZUBAIR_KHAN, recipients=[JEFFREY_EPSTEIN], timestamp=parse('2016-11-04 17:46:00')),
    MessageCfg(id='030626', recipients=[ALAN_DERSHOWITZ, DARREN_INDYKE, KATHRYN_RUEMMLER, KEN_STARR, MARTIN_WEINBERG]),
    MessageCfg(id='029835', recipients=[ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN], duplicate_ids=['028968']),
    MessageCfg(id='027063', recipients=[ANTHONY_BARRETT]),
    MessageCfg(id='030764', recipients=[ARIANE_DE_ROTHSCHILD], attribution_reason='Reply'),
    MessageCfg(id='026431', recipients=[ARIANE_DE_ROTHSCHILD], attribution_reason='Reply'),
    MessageCfg(id='032876', recipients=[CECILIA_STEEN]),
    MessageCfg(id='033583', recipients=[DARREN_INDYKE, JACK_GOLDBERGER]),  # Bad OCR
    MessageCfg(id='033144', recipients=[DARREN_INDYKE, RICHARD_KAHN]),
    MessageCfg(id='026466', recipients=[DIANE_ZIMAN], attribution_reason='Quoted reply'),
    MessageCfg(id='031607', recipients=[EDWARD_JAY_EPSTEIN]),
    MessageCfg(
        id='030525',
        recipients=[FAITH_KATES],
        attribution_reason='Same as unredacted 030414, same legal signature',
        duplicate_ids=['030581'],
    ),
    MessageCfg(
        id='030475',
        recipients=[FAITH_KATES],
        attribution_reason='Same Next Management LLC legal signature',
        duplicate_ids=['030575'],
        dupe_type='redacted'
    ),
    MessageCfg(id='030999', recipients=[JACK_GOLDBERGER, ROBERT_D_CRITTON]),
    MessageCfg(id='026426', recipients=[JEAN_HUGUEN], attribution_reason='Reply'),
    MessageCfg(id='022202', recipients=[JEAN_LUC_BRUNEL], attribution_reason='Follow up / reply', duplicate_ids=['029975']),
    MessageCfg(id='031489', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    MessageCfg(id='032210', recipients=[JEFFREY_EPSTEIN], ),  # More of a text convo?
    MessageCfg(id='022344', recipients=[JEFFREY_EPSTEIN], duplicate_ids=['028529']),  # Bad OCR
    MessageCfg(id='030347', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    MessageCfg(id='030367', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    MessageCfg(id='033274', recipients=[JEFFREY_EPSTEIN]),  # this is a note sent to self'
    MessageCfg(id='032780', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    MessageCfg(id='025233', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    MessageCfg(id='029324', recipients=[JEFFREY_EPSTEIN, "Jojo Fontanilla", "Lyn Fontanilla"]),
    MessageCfg(id='033575', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN], duplicate_ids=['012898']),
    MessageCfg(id='023067', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN, TONJA_HADDAD_COLEMAN]),  # Bad OCR
    MessageCfg(id='033228', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, FRED_HADDAD]),  # Bad OCR
    MessageCfg(id='025790', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER], duplicate_ids=['031994']),  # Bad OCR
    MessageCfg(
        id='031384',
        actual_text='',
        recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER, MARTIN_WEINBERG, SCOTT_J_LINK],
    ),
    MessageCfg(id='033512', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACKIE_PERCZEK, MARTIN_WEINBERG], duplicate_ids=['033361']),
    MessageCfg(id='032063', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, REID_WEINGARTEN]),
    MessageCfg(id='033486', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, RICHARD_KAHN], duplicate_ids=['033156']),  # Bad OCR
    MessageCfg(id='029154', recipients=[JEFFREY_EPSTEIN, DAVID_HAIG]),  # Bad OCR
    MessageCfg(id='029498', recipients=[JEFFREY_EPSTEIN, DAVID_HAIG, GORDON_GETTY, "Norman Finkelstein"]),  # Bad OCR
    MessageCfg(id='029889', recipients=[JEFFREY_EPSTEIN, "Connie Zaguirre", JACK_GOLDBERGER, ROBERT_D_CRITTON]),  # Bad OCR
    MessageCfg(id='028931', recipients=[JEFFREY_EPSTEIN, LAWRENCE_KRAUSS]),  # Bad OCR
    MessageCfg(id='019407', recipients=[JEFFREY_EPSTEIN, MICHAEL_SITRICK]),  # Bad OCR
    MessageCfg(id='031980', recipients=[JEFFREY_EPSTEIN, MICHAEL_SITRICK], duplicate_ids=['019409']),  # Bad OCR
    MessageCfg(id='029163', recipients=[JEFFREY_EPSTEIN, ROBERT_TRIVERS]),   # Bad OCR
    MessageCfg(id='026228', recipients=[JEFFREY_EPSTEIN, STEVEN_PFEIFFER]),  # Bad OCR
    MessageCfg(id='030299', recipients=[JESSICA_CADWELL, ROBERT_D_CRITTON], duplicate_ids=['021794']),  # Bad OCR
    MessageCfg(id='033456', recipients=["Joel"], attribution_reason='Reply'),
    MessageCfg(id='033460', recipients=["Joel"], attribution_reason='Reply'),
    MessageCfg(
        id='021090',
        is_fwded_article=True,
        recipients=[JONATHAN_FARKAS],
        attribution_reason='Reply to a message signed "jonathan" same as other Farkas emails',
    ),
    MessageCfg(
        id='033073',
        is_author_uncertain=True,
        recipients=[KATHRYN_RUEMMLER],
        attribution_reason='to "Kathy" about dems, sent from iPad',
    ),
    MessageCfg(
        id='032939',
        recipients=[KATHRYN_RUEMMLER],
        is_author_uncertain=True,
        attribution_reason='to "Kathy" about dems, sent from iPad',
    ),
    MessageCfg(id='031428', recipients=[KEN_STARR, LILLY_SANCHEZ, MARTIN_WEINBERG, REID_WEINGARTEN], duplicate_ids=['031388']), # Bad OCR
    MessageCfg(id='025329', recipients=KRASSNER_MANSON_RECIPIENTS),
    MessageCfg(id='033568', recipients=KRASSNER_033568_RECIPIENTS),
    MessageCfg(id='030522', is_fwded_article=True, recipients=[LANDON_THOMAS]),  # Vicky Ward article
    MessageCfg(id='031413', recipients=[LANDON_THOMAS]),
    MessageCfg(id='033591', recipients=[LAWRANCE_VISOSKI], attribution_reason='Reply signature', duplicate_ids=['033591']),
    MessageCfg(id='027097', recipients=[LAWRANCE_VISOSKI], attribution_reason='Reply signature', duplicate_ids=['028787']),
    MessageCfg(id='022250', recipients=[LESLEY_GROFF], attribution_reason='Reply'),
    MessageCfg(
        id='032048',
        dupe_of_id='030242',
        dupe_type='redacted',
        recipients=[MARIANA_IDZKOWSKA],
        attribution_reason='Redacted here, visisble in 030242',
    ),
    MessageCfg(id='030368', recipients=[MELANIE_SPINELLA], attribution_reason='Actually a self fwd from jeffrey to jeffrey'),
    MessageCfg(id='030369', recipients=[MELANIE_SPINELLA], attribution_reason='Actually a self fwd from jeffrey to jeffrey'),
    MessageCfg(id='030371', recipients=[MELANIE_SPINELLA], attribution_reason='Actually a self fwd from jeffrey to jeffrey'),
    MessageCfg(id='022258', recipients=[NADIA_MARCINKO], attribution_reason='Reply header'),
    MessageCfg(id='033097', recipients=[PAUL_BARRETT, RICHARD_KAHN]),  # Bad OCR
    MessageCfg(id='030506', recipients=[PAULA], attribution_reason=PAULA_REASON, is_author_uncertain=True),
    MessageCfg(id='030507', recipients=[PAULA], attribution_reason=PAULA_REASON, is_author_uncertain=True),
    MessageCfg(id='030508', recipients=[PAULA], attribution_reason=PAULA_REASON, is_author_uncertain=True),
    MessageCfg(id='030509', recipients=[PAULA], attribution_reason=PAULA_REASON, is_author_uncertain=True),
    MessageCfg(id='030096', recipients=[PETER_MANDELSON]),
    MessageCfg(id='032951', recipients=[RAAFAT_ALSABBAGH, None], attribution_reason='Redacted'),
    MessageCfg(id='029581', recipients=[RENATA_BOLOTOVA], attribution_reason=BOLOTOVA_REASON),
    MessageCfg(id='030384', recipients=[RICHARD_KAHN, "Alan Dlugash"]),
    MessageCfg(id='019334', recipients=[STEVE_BANNON]),
    MessageCfg(id='021106', recipients=[STEVE_BANNON], attribution_reason='Reply'),
    MessageCfg(id='032475', timestamp=parse('2017-02-15 13:31:25')),
    MessageCfg(id='030373', timestamp=parse('2018-10-03 01:49:27')),
    MessageCfg(id='033050', actual_text='schwartman'),
    MessageCfg(id='026298', is_fwded_article=True, duplicate_ids=['026499']),  # Written by someone else?
    MessageCfg(id='026755', is_fwded_article=True),  # HuffPo
    MessageCfg(
        id='023627',
        description=MICHAEL_WOLFF_ARTICLE_HINT,
        is_fwded_article=True,
        attribution_reason='Wolff article about epstein',
    ),
    MessageCfg(id='030528', is_fwded_article=True),  # Vicky Ward article
    MessageCfg(id='018197', is_fwded_article=True, duplicate_ids=['028648']),   # Ray Takeyh article fwd
    MessageCfg(
        id='028728',
        is_fwded_article=True,
        attribution_reason='WSJ forward to Larry Summers',
        duplicate_ids=['027102'],
    ),
    MessageCfg(id='028508', is_fwded_article=True),  # nanosatellites article
    MessageCfg(
        id='028781',
        is_fwded_article=True,
        attribution_reason="Atlantic on Jim Yong Kim, Obama's World Bank Pick",
        duplicate_ids=['013460']
    ),
    MessageCfg(id='019845', is_fwded_article=True),  # Pro Publica article on Preet Bharara
    MessageCfg(id='029021', is_fwded_article=True),  # article about bannon sent by Alain Forget
    MessageCfg(id='031688', is_fwded_article=True),  # Bill Siegel fwd of email about hamas
    MessageCfg(id='026551', is_fwded_article=True),  # Sultan bin Sulayem "Ayatollah between the sheets"
    MessageCfg(id='031768', is_fwded_article=True),  # Sultan bin Sulayem 'Horseface'
    MessageCfg(id='031569', is_fwded_article=True),  # Article by Kathryn Alexeeff fwded to Peter Thiel


        ####################################
        ######### DUPE_FILE_CFGS ###########
        ####################################

    MessageCfg(id='031215', duplicate_ids=['026745'], dupe_type='redacted'),
    MessageCfg(id='026563', dupe_of_id='028768', dupe_type='redacted'),
    MessageCfg(id='028762', dupe_of_id='027056', dupe_type='redacted'),
    MessageCfg(id='032246', dupe_of_id='032248', dupe_type='redacted'),
    MessageCfg(id='023065', dupe_of_id='030628', dupe_type='redacted'),
    MessageCfg(id='031226', dupe_of_id='017523', dupe_type='redacted'),
    MessageCfg(id='031008', dupe_of_id='031099', dupe_type='redacted'),
    MessageCfg(id='033463', dupe_of_id='033596', dupe_type='redacted'),
    MessageCfg(id='023018', dupe_of_id='030624', dupe_type='redacted'),
    MessageCfg(id='030596', dupe_of_id='030335', dupe_type='redacted'),
    MessageCfg(id='012711', dupe_of_id='029841', dupe_type='redacted'),
    MessageCfg(id='033517', dupe_of_id='033528'),
    MessageCfg(id='032012', dupe_of_id='032023'),
    MessageCfg(id='028621', dupe_of_id='019412'),
    MessageCfg(id='028765', dupe_of_id='027053'),
    MessageCfg(id='028773', dupe_of_id='027049'),
    MessageCfg(id='033207', dupe_of_id='033580'),
    MessageCfg(id='025547', dupe_of_id='028506'),
    MessageCfg(id='026549', dupe_of_id='028784'),
    MessageCfg(id='033599', dupe_of_id='033386'),
    MessageCfg(id='030622', dupe_of_id='023024'),
    MessageCfg(id='023026', dupe_of_id='030618'),
    MessageCfg(id='026834', dupe_of_id='028780'),
    MessageCfg(id='026835', dupe_of_id='028775'),
    MessageCfg(id='033489', dupe_of_id='033251'),
    MessageCfg(id='019465', dupe_of_id='031118'),
    MessageCfg(id='032158', dupe_of_id='031912'),
    MessageCfg(id='030514', dupe_of_id='030587'),
    MessageCfg(id='012685', dupe_of_id='029773'),
    MessageCfg(id='033482', dupe_of_id='029849'),
    MessageCfg(id='033586', dupe_of_id='033297'),
    MessageCfg(id='018084', dupe_of_id='031089'),
    MessageCfg(id='030885', dupe_of_id='031088'),
    MessageCfg(id='031130', dupe_of_id='030238'),
    MessageCfg(id='031067', dupe_of_id='030859'),
    MessageCfg(id='028791', dupe_of_id='031136'),
    MessageCfg(id='031134', dupe_of_id='030635'),
    MessageCfg(id='026234', dupe_of_id='028494'),
    MessageCfg(id='021790', dupe_of_id='030311'),
    MessageCfg(id='029880', dupe_of_id='033508'),
    MessageCfg(id='030612', dupe_of_id='030493'),
    MessageCfg(id='031771', dupe_of_id='032051'),
    MessageCfg(id='021761', dupe_of_id='031217'),
    MessageCfg(id='031426', dupe_of_id='031346'),
    MessageCfg(id='031427', dupe_of_id='031345'),
    MessageCfg(id='031432', dupe_of_id='031343'),
    MessageCfg(id='031084', dupe_of_id='031020'),
    MessageCfg(id='033485', dupe_of_id='033354'),
    MessageCfg(id='021241', dupe_of_id='031999'),
    MessageCfg(id='030602', dupe_of_id='030502'),
    MessageCfg(id='030617', dupe_of_id='030574'),
    MessageCfg(id='025226', dupe_of_id='031156'),
    MessageCfg(id='031086', dupe_of_id='031018'),
    MessageCfg(id='031079', dupe_of_id='031026'),
    MessageCfg(id='031787', dupe_of_id='032011'),
    MessageCfg(id='030498', dupe_of_id='030606'),
    MessageCfg(id='021235', dupe_of_id='032005'),
    MessageCfg(id='026160', dupe_of_id='028505'),
    MessageCfg(id='030837', dupe_of_id='031126'),
    MessageCfg(id='029778', dupe_of_id='029624'),
    MessageCfg(id='031422', dupe_of_id='031338'),
    MessageCfg(id='033289', dupe_of_id='033587'),
    MessageCfg(id='012722', dupe_of_id='032107'),
    MessageCfg(id='031114', dupe_of_id='030844'),
    MessageCfg(id='031074', dupe_of_id='031031'),
    MessageCfg(id='028531', dupe_of_id='027032'),
    MessageCfg(id='028493', dupe_of_id='026777'),
    MessageCfg(id='029255', dupe_of_id='029837'),
    MessageCfg(id='025361', dupe_of_id='031423'),
    MessageCfg(id='033594', dupe_of_id='029299'),
    MessageCfg(id='031069', dupe_of_id='030904'),
    MessageCfg(id='031165', dupe_of_id='030006'),
    MessageCfg(id='031159', dupe_of_id='025215'),
    MessageCfg(id='031090', dupe_of_id='031011'),
    MessageCfg(id='018158', dupe_of_id='032068'),
    MessageCfg(id='031221', dupe_of_id='031213'),
    MessageCfg(id='016690', dupe_of_id='016595'),
    MessageCfg(id='028970', dupe_of_id='029833'),
    MessageCfg(id='028958', dupe_of_id='029839'),
    MessageCfg(id='033503', dupe_of_id='029893'),
    MessageCfg(id='028486', dupe_of_id='025878'),
    MessageCfg(id='033565', dupe_of_id='032764'),
    MessageCfg(id='028485', dupe_of_id='026618'),
    MessageCfg(id='030495', dupe_of_id='030609'),
    MessageCfg(id='028972', dupe_of_id='029831'),
    MessageCfg(id='030616', dupe_of_id='021758'),
    MessageCfg(id='029884', dupe_of_id='033498'),
    MessageCfg(id='027094', dupe_of_id='028620'),
    MessageCfg(id='033579', dupe_of_id='032456'),
    MessageCfg(id='030255', dupe_of_id='030315'),
    MessageCfg(id='030876', dupe_of_id='031112'),
    MessageCfg(id='030491', dupe_of_id='030614'),
    MessageCfg(id='032279', dupe_of_id='033585'),
    MessageCfg(id='031189', dupe_of_id='031220'),
    MessageCfg(id='033563', dupe_of_id='032779'),
    MessageCfg(id='033577', dupe_of_id='033230'),
    MessageCfg(id='023971', dupe_of_id='032125'),
    MessageCfg(id='031203', dupe_of_id='031230'),
    MessageCfg(id='026569', dupe_of_id='028752'),
    MessageCfg(id='032050', dupe_of_id='031773'),
    MessageCfg(id='031983', dupe_of_id='021400'),
    MessageCfg(id='033491', dupe_of_id='026548'),
    MessageCfg(id='023550', dupe_of_id='029752'),
    MessageCfg(id='030592', dupe_of_id='030339'),
    MessageCfg(id='033589', dupe_of_id='032250'),
    FileCfg(
        id='019224',
        description=f"{KEN_STARR_LETTER} 2008-05-19",
        dupe_of_id='025353',
        dupe_type='redacted',
    ),
    FileCfg(id='014697', description=CHALLENGES_OF_AI, duplicate_ids=['011284']),
    FileCfg(id='028965', description=WEINBERG_ABC_LETTER, duplicate_ids=['028928']),
    FileCfg(id='033478', description=f'{MEME} Kim Jong Un reading {FIRE_AND_FURY}', timestamp=parse('2018-01-05'), duplicate_ids=['032713']),
    FileCfg(
        id='029357',
        description=f"some text about Israel's challenges going into 2015, feels like it was extracted from a book 2015-01",
        dupe_of_id='028887',
    ),
    FileCfg(
        id='029356',
        description=f'{SCREENSHOT} quote in book about {LARRY_SUMMERS} (zoomed in corner of 029355)',
        duplicate_ids=['029355'],
    ),


        ####################################
        ######### FILE_DESCRIPTIONS ########
        ####################################

    # books
    FileCfg(id='015032', description=f'{BOOK} "60 Years of Investigative Satire: The Best of {PAUL_KRASSNER}"'),
    FileCfg(id='015675', description=f'{BOOK} "Are the Androids Dreaming Yet? Amazing Brain Human Communication, Creativity & Free Will" by James Tagg'),
    FileCfg(id='012899', description=f'{BOOK} "Engineering General Intelligence: A Path to Advanced AGI Via Embodied Learning and Cognitive Synergy" by Ben Goertzel'),
    FileCfg(id='012747', description=f'{BOOK} "Evilicious: Explaining Our Taste For Excessive Harm" by Marc D. Hauser'),
    FileCfg(id='019874', description=f'{BOOK} {FIRE_AND_FURY}', timestamp=parse('2018-01-05')),
    FileCfg(id='032724', description=f'{BOOK} cover of {FIRE_AND_FURY}', timestamp=parse('2018-01-05')),
    FileCfg(
        id='010912',
        description=f'{BOOK} "Free Growth and Other Surprises" by Gordon Getty (draft)',
        timestamp=parse('2018-10-18'),
    ),
    FileCfg(
        id='021247',
        description=f'{BOOK} "Invisible Forces And Powerful Beliefs: Gravity, Gods, And Minds" by The Chicago Social Brain Network',
        timestamp=parse('2010-10-04'),
    ),
    FileCfg(id='019477', description=f'{BOOK} "How America Lost Its Secrets: Edward Snowden, the Man, and the Theft" by {EDWARD_JAY_EPSTEIN}'),
    FileCfg(id='017088', description=f'{BOOK} "Taking the Stand: My Life in the Law" by {ALAN_DERSHOWITZ} (draft)'),
    FileCfg(id='023731', description=f'{BOOK} "Teaching Minds How Cognitive Science Can Save Our Schools" by {ROGER_SCHANK}'),
    FileCfg(id='013796', description=f'{BOOK} "The 4-Hour Workweek" by Tim Ferriss'),
    FileCfg(id='021145', description=f'{BOOK} "The Billionaire\'s Playboy Club" by {VIRGINIA_GIUFFRE} (draft?)'),
    FileCfg(
        id='013501',
        description=f'{BOOK} "The Nearness Of Grace: A Personal Science Of Spiritual Transformation" by Arnold J. Mandell',
        timestamp=parse('2005-01-01'),
    ),
    FileCfg(id='018438', description=f'{BOOK} "The S&M Feminist" by Clarisse Thorn'),
    FileCfg(id='018232', description=f'{BOOK} "The Seventh Sense: Power, Fortune & Survival in the Age of Networks" by Joshua Cooper Ramo'),
    FileCfg(id='020153', description=f'{BOOK} "The Snowden Affair: A Spy Story In Six Parts" by {EDWARD_JAY_EPSTEIN}'),
    FileCfg(id='021120', description=f'{BOOK} chapter of "Siege: Trump Under Fire" by {MICHAEL_WOLFF}'),
    FileCfg(id='016221', description=DEEP_THINKING_HINT, timestamp=parse('2019-02-19')),
    FileCfg(id='016804', description=DEEP_THINKING_HINT, timestamp=parse('2019-02-19')),
    FileCfg(id='031533', description=f'few pages from a book about the Baylor University sexual assault scandal and Sam Ukwuachu'),
    FileCfg(id='011472', description=NIGHT_FLIGHT_HINT,),
    FileCfg(id='027849', description=NIGHT_FLIGHT_HINT,),
    FileCfg(id='010477', description=PATTERSON_BOOK_SCANS, timestamp=parse('2016-10-10')),
    FileCfg(id='010486', description=PATTERSON_BOOK_SCANS, timestamp=parse('2016-10-10')),
    FileCfg(id='021958', description=PATTERSON_BOOK_SCANS, timestamp=parse('2016-10-10')),
    FileCfg(id='022058', description=PATTERSON_BOOK_SCANS, timestamp=parse('2016-10-10')),
    FileCfg(id='022118', description=PATTERSON_BOOK_SCANS, timestamp=parse('2016-10-10')),
    FileCfg(id='019111', description=PATTERSON_BOOK_SCANS, timestamp=parse('2016-10-10')),
    FileCfg(
        id='030199',
        description=f'article about allegations Trump raped a 13 year old girl {JANE_DOE_V_EPSTEIN_TRUMP}',
        timestamp=parse('2017-11-16'),
    ),
    # articles
    FileCfg(id='031725', description=f"article about Gloria Allred and Trump allegations", timestamp=parse('2016-10-10')),
    FileCfg(id='031198', description=f"article about identify of Jane Doe in {JANE_DOE_V_EPSTEIN_TRUMP}"),
    FileCfg(id='012704', description=f"article about {JANE_DOE_V_USA} and {CVRA}", timestamp=parse('2011-04-21')),
    FileCfg(
        id='026648',
        description=f'article about {JASTA} lawsuit against Saudi Arabia by 9/11 victims (Russian propaganda?)',
        timestamp=parse('2017-05-13'),
    ),
    FileCfg(id='031776', description=f"article about Michael Avenatti by Andrew Strickler"),
    FileCfg(id='032159', description=f"article about microfinance and cell phones in Zimbabwe, Strive Masiyiwa (Econet Wireless)"),
    FileCfg(
        id='026584',
        description=f'article about tax implications of "disregarded entities"',
        timestamp=parse('2009-07-01'),
    ),
    FileCfg(id='024256', description=f'article by {JOI_ITO}: "Internet & Society: The Technologies and Politics of Control"'),
    FileCfg(
        id='027004',
        description=f'article by {JOSCHA_BACH}: "The Computational Structure of Mental Representation"',
        timestamp=parse('2013-02-26'),
    ),
    FileCfg(id='015501', description=f'article by {MOSHE_HOFFMAN}, Erez Yoeli, and Carlos David Navarrete: "Game Theory and Morality"'),
    FileCfg(id='030258', description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030248'),
    FileCfg(id='030248', description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    FileCfg(id='029165', description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    FileCfg(id='033468', description=f'{ARTICLE_DRAFT} Rod Rosenstein', timestamp=parse('2018-09-24')),
    FileCfg(id='030825', description=f'{ARTICLE_DRAFT} Syria'),
    FileCfg(id='030013', description=f'Aviation International News article', timestamp=parse('2012-07-01')),
    FileCfg(id='033253', description=f'{BBC} article about Rohingya in Myanmar by {ROBERT_LAWRENCE_KUHN}'),
    FileCfg(id='026887', description=f'{BBC} "New Tariffs - Trade War" by {ROBERT_LAWRENCE_KUHN}'),
    FileCfg(id='013275', description=f"{BLOOMBERG} article on notable 2013 obituaries", timestamp=parse('2013-12-26')),
    FileCfg(id='026543', description=f"{BLOOMBERG} BNA article about taxes"),
    FileCfg(id='014865', description=f"Boston Globe article about {ALAN_DERSHOWITZ}"),
    FileCfg(id='033231', description=f"Business Standard article about Trump's visit with India's Modi"),
    FileCfg(id='023572', description=f"{CHINA_DAILY_ARTICLE} China's Belt & Road Initiative by {ROBERT_LAWRENCE_KUHN}"),
    FileCfg(
        id='023571',
        description=f'{CHINA_DAILY_ARTICLE} terrorism, Macau, trade initiatives',
        timestamp=parse('2016-09-18'),
    ),
    FileCfg(
        id='023570',
        description=f'{CHINA_DAILY_ARTICLE} Belt & Road in Central/South America, Xi philosophy',
        timestamp=parse('2017-05-14'),
    ),
    FileCfg(
        id='025115',
        description=f'{CHINA_DAILY_ARTICLE} China and the US working together',
        timestamp=parse('2017-05-14'),
    ),
    FileCfg(id='026877', description=f'{CNN} "New Tariffs - Trade War" by {ROBERT_LAWRENCE_KUHN}'),
    FileCfg(
        id='026868',
        description=f'{CNN} "Quest Means Business New China Tariffs — Trade War" by {ROBERT_LAWRENCE_KUHN}',
        timestamp=parse('2018-09-18'),
    ),
    FileCfg(
        id='023707',
        description=f'{CNN} "Quest Means Business U.S. and China Agree to Pause Trade War" by {ROBERT_LAWRENCE_KUHN}',
        timestamp=parse('2018-12-03'),
    ),
    FileCfg(id='029176', description=f'{CNN} "U.S. China Tariffs - Trade War" by {ROBERT_LAWRENCE_KUHN}'),
    FileCfg(id='032638', description=f'{CNN} "Xi Jinping and the New Politburo Committee" by {ROBERT_LAWRENCE_KUHN}'),
    FileCfg(id='025292', description=f"{DAILY_MAIL_ARTICLE} Bill Clinton being named in a lawsuit"),
    FileCfg(id='019468', description=f"{DAILY_MAIL_ARTICLE} Epstein and Clinton"),
    FileCfg(id='022970', description=f"{DAILY_MAIL_ARTICLE} Epstein and Prince Andrew"),
    FileCfg(
        id='031186',
        description=f'{DAILY_MAIL_ARTICLE} rape of 13 year old accusations against Trump',
        timestamp=parse('2016-11-02'),
    ),
    FileCfg(id='013437', description=f"{DAILY_TELEGRAPH_ARTICLE} Epstein diary", timestamp=parse('2011-03-05')),
    FileCfg(
        id='023287',
        description=f"{DAILY_TELEGRAPH_ARTICLE} play based on the Oslo Accords",
        timestamp=parse('2017-09-15'),
    ),
    FileCfg(id='023567', description=f"Financial Times article about quantitative easing"),
    FileCfg(id='026761', description=f'Forbes article about {BARBRO_C_EHNBOM} "Swedish American Group Focuses On Cancer"'),
    FileCfg(id='031716', description=f'Fortune Magazine article by {TOM_BARRACK}', timestamp=parse('2016-10-22')),
    FileCfg(
        id='019233',
        description=f'Freedom House: "Breaking Down Democracy: Goals, Strategies, and Methods of Modern Authoritarians"',
        timestamp=parse('2017-06-02'),
    ),
    FileCfg(
        id='019444',
        description=f'Frontlines magazine article "Biologists Dig Deeper"',
        timestamp=parse('2008-01-01'),
    ),
    FileCfg(id='023720', description=f'Future Science article: "Is Shame Necessary?" by {JENNIFER_JACQUET}'),
    FileCfg(
        id='027051',
        description=f"German language article about the 2013 Lifeball / AIDS Gala",
        timestamp=parse('2013-01-01'),
    ),
    FileCfg(id='021094', description=f"Globe and Mail article about Gerd Heinrich", timestamp=parse('2007-06-12')),
    FileCfg(id='013268', description=f"JetGala article about airplane interior designer {ERIC_ROTH}"),
    FileCfg(id='033480', description=f"{JOHN_BOLTON_PRESS_CLIPPING}", timestamp=parse('2018-04-06'), duplicate_ids=['033481']),
    FileCfg(id='029539', description=f"{LA_TIMES} Alan Trounson interview on California stem cell research and CIRM"),
    FileCfg(
        id='029865',
        description=f"{LA_TIMES} front page article about {DEEPAK_CHOPRA} and young Iranians",
        timestamp=parse('2016-11-05'),
    ),
    FileCfg(id='026598', description=f"{LA_TIMES} op-ed about why America needs a Ministry of Culture"),
    FileCfg(
        id='027024',
        description=f'{LA_TIMES} "Scientists Create Human Embryos to Make Stem Cells"',
        timestamp=parse('2013-05-15'),
    ),
    FileCfg(
        id='013403',
        description=f"Lexis Nexis result from The Evening Standard about Bernie Madoff",
        timestamp=parse('2009-12-24'),
    ),
    FileCfg(id='023102', description=f"Litigation Daily article about {REID_WEINGARTEN}", timestamp=parse('2015-09-04')),
    FileCfg(id='029340', description=f'MarketWatch article about estate taxes, particularly Epstein\'s favoured GRATs'),
    FileCfg(id='022707', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='022727', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='022746', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='022844', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='022863', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='022894', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='022952', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='024229', description=MICHAEL_WOLFF_ARTICLE_HINT,),
    FileCfg(id='029416', description=NATIONAL_ENQUIRER_FILING, timestamp=parse('2017-05-25'), duplicate_ids=['029405']),
    FileCfg(id='015462', description=f'Nautilus Education magazine (?) issue'),
    FileCfg(id='029925', description=f"New Yorker article about the placebo effect by Michael Specter", timestamp=parse('2011-12-04')),
    FileCfg(id='031972', description=f"{NYT_ARTICLE} #MeToo allegations against {LAWRENCE_KRAUSS}", timestamp=parse('2018-03-07')),
    FileCfg(id='032435', description=f'{NYT_ARTICLE} Chinese butlers'),
    FileCfg(id='029452', description=f"{NYT_ARTICLE} {PETER_THIEL}"),
    FileCfg(id='025328', description=f"{NYT_ARTICLE} radio host Bob Fass and Robert Durst"),
    FileCfg(id='033479', description=f"{NYT_ARTICLE} Rex Tillerson", timestamp=parse('2010-03-14')),
    FileCfg(id='028481', description=f'{NYT_ARTICLE} {STEVE_BANNON}', timestamp=parse('2018-03-09')),
    FileCfg(id='033181', description=f'{NYT_ARTICLE} Trump\'s tax avoidance', timestamp=parse('2016-10-31')),
    FileCfg(id='023097', description=f'{NYT_COLUMN} The Aristocrats by Frank Rich "The Greatest Dirty Joke Ever Told"'),
    FileCfg(id='033365', description=f'{NYT_COLUMN} trade war with China by Kevin Rudd'),
    FileCfg(id='019439', description=f"{NYT_COLUMN} the Clintons and money by Maureen Dowd", timestamp=parse('2013-08-17')),
    FileCfg(id='021093', description=f"page of unknown article about Epstein and Maxwell"),
    FileCfg(id='013435', description=f"{PALM_BEACH_DAILY_ARTICLE} Epstein's address book", timestamp=parse('2011-03-11')),
    FileCfg(id='013440', description=f"{PALM_BEACH_DAILY_ARTICLE} Epstein's gag order", timestamp=parse('2011-07-13')),
    FileCfg(id='029238', description=f"{PALM_BEACH_DAILY_ARTICLE} Epstein's plea deal"),
    FileCfg(id='021775', description=f'{PALM_BEACH_POST_ARTICLE} "He Was 50. And They Were Girls"'),
    FileCfg(id='022989', description=f"{PALM_BEACH_POST_ARTICLE} alleged rape of 13 year old by Trump"),
    FileCfg(id='022987', description=f"{PALM_BEACH_POST_ARTICLE} just a headline on Trump and Epstein"),
    FileCfg(id='015028', description=f"{PALM_BEACH_POST_ARTICLE} reopening Epstein's criminal case"),
    FileCfg(id='022990', description=f"{PALM_BEACH_POST_ARTICLE} Trump and Epstein"),
    FileCfg(id='031753', description=f'{PAUL_KRASSNER} essay for Playboy in the 1980s', timestamp=parse('1985-01-01')),
    FileCfg(id='023638', description=f'{PAUL_KRASSNER} magazine interview'),
    FileCfg(id='024374', description=f'{PAUL_KRASSNER} "Remembering Cavalier Magazine"'),
    FileCfg(id='030187', description=f'{PAUL_KRASSNER} "Remembering Lenny Bruce While We\'re Thinking About Trump" (draft?)'),
    FileCfg(id='019088', description=f'{PAUL_KRASSNER} "Are Rape Jokes Funny? (draft)', timestamp=parse('2012-07-28')),
    FileCfg(id='012740', description=f"{PEGGY_SIEGAL} article about Venice Film Festival", timestamp=parse('2011-09-06')),
    FileCfg(id='013442', description=f"{PEGGY_SIEGAL} draft about Oscars", timestamp=parse('2011-02-27')),
    FileCfg(id='012700', description=f"{PEGGY_SIEGAL} film events diary", timestamp=parse('2011-02-27')),
    FileCfg(id='012690', description=f"{PEGGY_SIEGAL} film events diary early draft of 012700", timestamp=parse('2011-02-27')),
    FileCfg(id='013450', description=f"{PEGGY_SIEGAL} Oscar Diary in Avenue Magazine", timestamp=parse('2011-02-27')),
    FileCfg(id='010715', description=f"{PEGGY_SIEGAL} Oscar Diary April", timestamp=parse('2012-02-27')),
    FileCfg(id='019849', description=f"{PEGGY_SIEGAL} Oscar Diary April", timestamp=parse('2017-02-27'), duplicate_ids=['019864']),
    FileCfg(
        id='033323',
        description=f'{ROBERT_TRIVERS} and Nathan H. Lents "Does Trump Fit the Evolutionary Role of Narcissistic Sociopath?" (draft)',
        timestamp=parse('2018-12-07'),
    ),
    FileCfg(
        id='025143',
        description=f'{ROBERT_TRIVERS} essay "Africa, Parasites, Intelligence"',
        timestamp=parse('2018-06-25'),
    ),
    FileCfg(id='016996', description=f'SciencExpress article "Quantitative Analysis of Culture Using Millions of Digitized Books" by Jean-Baptiste Michel'),
    FileCfg(id='025104', description=f"SCMP article about China and globalisation"),
    FileCfg(id='030030', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-03-29')),
    FileCfg(id='025610', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-04-03')),
    FileCfg(id='023458', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-04-17')),
    FileCfg(id='023487', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-04-18')),
    FileCfg(id='030531', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-05-16')),
    FileCfg(id='024958', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-05-08')),
    FileCfg(id='030060', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-05-13')),
    FileCfg(id='031834', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-05-16')),
    FileCfg(id='023517', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-05-26')),
    FileCfg(id='030268', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-05-29')),
    FileCfg(id='029628', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-06-04')),
    FileCfg(id='018085', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-06-07')),
    FileCfg(id='030156', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-06-22')),
    FileCfg(id='031876', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-06-14')),
    FileCfg(id='032171', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-06-26')),
    FileCfg(id='029932', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-07-03')),
    FileCfg(id='031913', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-08-24')),
    FileCfg(id='024592', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-08-25')),
    FileCfg(id='024997', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-09-08')),
    FileCfg(id='031941', description=f'{SHIMON_POST_ARTICLE}', timestamp=parse('2011-11-17')),
    FileCfg(id='021092', description=f'{SINGLE_PAGE} Tatler article about {GHISLAINE_MAXWELL} shredding documents', timestamp=parse('2019-08-15')),
    FileCfg(id='031191', description=f"{SINGLE_PAGE} unknown article about Epstein and Trump's relationship in 1997"),
    FileCfg(id='030829', description=f'South Florida Sun Sentinel article about {BRAD_EDWARDS} and {JEFFREY_EPSTEIN}'),
    FileCfg(id='026520', description=f'Spanish language article about {SULTAN_BIN_SULAYEM}', timestamp=parse('2013-09-27')),
    FileCfg(id='030333', description=f'The Independent article about Prince Andrew, Epstein, and Epstein\'s butler who stole his address book'),
    FileCfg(
        id='031736',
        description=f'{TRANSLATION} Arabic article by Abdulnaser Salamah "Trump; Prince of Believers (Caliph)!"',
        timestamp=parse('2017-05-13'),
    ),
    FileCfg(id='025094', description=f'{TRANSLATION} Spanish article about Cuba', timestamp=parse('2015-11-08')),
    FileCfg(id='010754', description=f"U.S. News article about Yitzhak Rabin", timestamp=parse('2015-11-04')),
    FileCfg(id='031794', description=f"very short French magazine clipping"),
    FileCfg(id='014498', description=f"{VI_DAILY_NEWS_ARTICLE}", timestamp=parse('2016-12-13')),
    FileCfg(id='031171', description=f"{VI_DAILY_NEWS_ARTICLE}", timestamp=parse('2019-02-06')),
    FileCfg(id='023048', description=f"{VI_DAILY_NEWS_ARTICLE}", timestamp=parse('2019-02-27')),
    FileCfg(id='023046', description=f"{VI_DAILY_NEWS_ARTICLE}", timestamp=parse('2019-02-27')),
    FileCfg(id='031170', description=f"{VI_DAILY_NEWS_ARTICLE}", timestamp=parse('2019-03-06')),
    FileCfg(id='016506', description=f"{VI_DAILY_NEWS_ARTICLE}", timestamp=parse('2019-02-28')),
    FileCfg(id='016507', description=f'{VI_DAILY_NEWS_ARTICLE} "Perversion of Justice" by {JULIE_K_BROWN}', timestamp=parse('2018-12-19')),
    FileCfg(id='019212', description=f'{WAPO} and Times Tribune articles about Bannon, Trump, and healthcare execs'),
    FileCfg(
        id='033379',
        description=f'{WAPO} "How Washington Pivoted From Finger-Wagging to Appeasement" about Viktor Orban',
        timestamp=parse('2018-05-25'),
    ),
    FileCfg(
        id='031396',
        description=f'{WAPO} "DOJ discipline office with limited reach to probe handling of controversial sex abuse case"',
        timestamp=parse('2019-02-06'),
        duplicate_ids=['031415'],
    ),
    FileCfg(
        id='019206',
        description=f"WSJ article about Edward Snowden by {EDWARD_JAY_EPSTEIN}",
        timestamp=parse('2016-12-30'),
    ),
    FileCfg(id='017603', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, timestamp=parse('2019-02-28')),
    # court docs
    FileCfg(id='017635', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, timestamp=parse('2019-02-28')),
    FileCfg(id='016509', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, timestamp=parse('2019-02-28')),
    FileCfg(id='017714', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, timestamp=parse('2019-02-28')),
    FileCfg(id='021824', description=f"{EDWARDS_V_DERSHOWITZ} deposition of {PAUL_G_CASSELL}"),
    FileCfg(
        id='010757',
        description=f"{EDWARDS_V_DERSHOWITZ} plaintiff response to Dershowitz Motion to Determine Confidentiality of Court Records",
        timestamp=parse('2015-11-23'),
    ),
    FileCfg(
        id='010887',
        description=f"{EDWARDS_V_DERSHOWITZ} Dershowitz Motion for Clarification of Confidentiality Order",
        timestamp=parse('2016-01-29'),
    ),
    FileCfg(
        id='015590',
        description=f"{EDWARDS_V_DERSHOWITZ} Dershowitz Redacted Motion to Modify Confidentiality Order",
        timestamp=parse('2016-02-03'),
    ),
    FileCfg(
        id='015650',
        description=f"{EDWARDS_V_DERSHOWITZ} Giuffre Response to Dershowitz Motion for Clarification of Confidentiality Order",
        timestamp=parse('2016-02-08'),
    ),
    FileCfg(
        id='010566',
        description=f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Statement of Undisputed Facts",
        timestamp=parse('2010-11-04'),
    ),
    FileCfg(
        id='012707',
        description=f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Master Contact List - Privilege Log",
        timestamp=parse('2011-03-22'),
    ),
    FileCfg(
        id='012103',
        description=f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Telephone Interview with {VIRGINIA_GIUFFRE}",
        timestamp=parse('2011-05-17'),
    ),
    FileCfg(
        id='017488',
        description=f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Deposition of Scott Rothstein",
        timestamp=parse('2012-06-22'),
    ),
    FileCfg(
        id='029315',
        description=f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Plaintiff Motion for Summary Judgment by {JACK_SCAROLA}",
        timestamp=parse('2013-09-13'),
    ),
    FileCfg(
        id='013304',
        description=f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Plaintiff Response to Epstein's Motion for Summary Judgment",
        timestamp=parse('2014-04-17'),
    ),
    FileCfg(id='019352', description=FBI_REPORT,),
    FileCfg(id='021434', description=FBI_REPORT,),
    FileCfg(id='018872', description=FBI_SEIZED_PROPERTY,),
    FileCfg(id='021569', description=FBI_SEIZED_PROPERTY,),
    FileCfg(id='022494', description=f'Foreign Corrupt Practices Act (FCPA) DOJ Resource Guide', timestamp=parse('2013-01-01')),
    FileCfg(id='017792', description=f"{GIUFFRE_V_DERSHOWITZ} article about Dershowitz's appearance on Wolf Blitzer"),
    FileCfg(id='017767', description=f"{GIUFFRE_V_DERSHOWITZ} article about {ALAN_DERSHOWITZ} working with {JEFFREY_EPSTEIN}"),
    FileCfg(id='017796', description=f"{GIUFFRE_V_DERSHOWITZ} article about {ALAN_DERSHOWITZ}"),
    FileCfg(id='017935', description=f"{GIUFFRE_V_DERSHOWITZ} defamation complaint", timestamp=parse('2019-04-16')),
    FileCfg(id='017824', description=f"{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} article by {JULIE_K_BROWN}"),
    FileCfg(
        id='017818',
        description=f"{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} article about accusations against {ALAN_DERSHOWITZ} by {JULIE_K_BROWN}",
        timestamp=parse('2018-12-27'),
    ),
    FileCfg(id='017800', description=f'{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} "Perversion of Justice" by {JULIE_K_BROWN}'),
    FileCfg(id='022237', description=f"{GIUFFRE_V_DERSHOWITZ} partial court filing with fact checking questions?"),
    FileCfg(id='016197', description=f"{GIUFFRE_V_DERSHOWITZ} response to Florida Bar complaint by {ALAN_DERSHOWITZ} about David Boies from {PAUL_G_CASSELL}"),
    FileCfg(
        id='017771',
        description=f'{GIUFFRE_V_DERSHOWITZ} Vanity Fair article "The Talented Mr. Epstein" by Vicky Ward',
        timestamp=parse('2011-06-27'),
    ),
    FileCfg(id='014652', description=f"{GIUFFRE_V_MAXWELL} Complaint", timestamp=parse('2015-04-22')),
    FileCfg(
        id='014797',
        description=f"{GIUFFRE_V_MAXWELL} Declaration of Laura A. Menninger in Opposition to Plaintiff's Motion",
        timestamp=parse('2017-03-17'),
    ),
    FileCfg(
        id='014118',
        description=f"{GIUFFRE_V_EPSTEIN} Declaration in Support of Motion to Compel Production of Documents",
        timestamp=parse('2016-10-21'),
    ),
    FileCfg(id='015529', description=f"{GIUFFRE_V_MAXWELL} defamation complaint", timestamp=parse('2015-09-21')),
    FileCfg(
        id='019297',
        description=f'{GIUFFRE_V_MAXWELL} letter from {ALAN_DERSHOWITZ} lawyer Andrew G. Celli',
        timestamp=parse('2018-02-07'),
    ),
    FileCfg(
        id='014788',
        description=f"{GIUFFRE_V_MAXWELL} Maxwell Response to Plaintiff's Omnibus Motion in Limine",
        timestamp=parse('2017-03-17'),
        duplicate_ids=['011463'],
    ),
    FileCfg(id='011304', description=f"{GIUFFRE_V_MAXWELL} Oral Argument Transcript", timestamp=parse('2017-03-17')),
    FileCfg(
        id='013489',
        description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of {BRAD_EDWARDS}',
        timestamp=parse('2010-07-20'),
    ),
    FileCfg(
        id='025939',
        description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of Jane Doe describing being raped by Epstein',
        timestamp=parse('2016-06-20'),
    ),
    FileCfg(
        id='025937',
        description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of Tiffany Doe describing Jane Doe being raped by Epstein and Trump',
        timestamp=parse('2016-06-20'),
    ),
    FileCfg(id='029398', description=f'{JANE_DOE_V_EPSTEIN_TRUMP} article in Law.com'),
    FileCfg(id='026854', description=f"{JANE_DOE_V_EPSTEIN_TRUMP} Civil Docket"),
    FileCfg(
        id='026384',
        description=f"{JANE_DOE_V_EPSTEIN_TRUMP} Complaint for rape and sexual abuse",
        timestamp=parse('2016-06-20'),
    ),
    FileCfg(
        id='013463',
        description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Deposition of Scott Rothstein filed by {BRAD_EDWARDS}',
        timestamp=parse('2010-03-23'),
    ),
    FileCfg(
        id='029257',
        description=f'{JANE_DOE_V_EPSTEIN_TRUMP} factual allegations and identity of plaintiff Katie Johnson',
        timestamp=parse('2016-04-26'),
    ),
    FileCfg(
        id='032321',
        description=f"{JANE_DOE_V_EPSTEIN_TRUMP} Notice of Initial Conference",
        timestamp=parse('2016-10-04'),
    ),
    FileCfg(
        id='010735',
        description=f"{JANE_DOE_V_USA} Dershowitz Reply in Support of Motion for Limited Intervention",
        timestamp=parse('2015-02-02'),
    ),
    FileCfg(
        id='014084',
        description=f"{JANE_DOE_V_USA} Jane Doe Response to Dershowitz's Motion for Limited Intervention",
        timestamp=parse('2015-03-24'),
    ),
    FileCfg(
        id='023361',
        description=f"{JASTA_SAUDI_LAWSUIT} legal text and court documents",
        timestamp=parse('2012-01-20'),
    ),
    FileCfg(id='017830', description=f"{JASTA_SAUDI_LAWSUIT} legal text and court documents"),
    FileCfg(id='017904', description=f"{JASTA_SAUDI_LAWSUIT} Westlaw search results", timestamp=parse('2019-01-01')),
    FileCfg(id='011908', description=f"{JEAN_LUC_BRUNEL} v. {JEFFREY_EPSTEIN} and Tyler McDonald d/b/a YI.org court filing"),
    FileCfg(id='014037', description=f"Journal of Criminal Law and Criminology article on {CVRA}"),
    FileCfg(id='025353', description=f"{KEN_STARR_LETTER}", timestamp=parse('2008-05-19'), duplicate_ids=['010723', '019224'], dupe_type='redacted'),
    FileCfg(id='025704', description=f"{KEN_STARR_LETTER}", timestamp=parse('2008-05-27'), duplicate_ids=['010732', '019221'], dupe_type='redacted'),
    FileCfg(id='012130', description=f"{KEN_STARR_LETTER}", timestamp=parse('2008-06-19'), duplicate_ids=['012135']),
    FileCfg(id='020662', description=f"letter from {ALAN_DERSHOWITZ}'s British lawyers Mishcon de Reya to Daily Mail threatening libel suit"),
    FileCfg(
        id='010560',
        description=f"letter from Gloria Allred to {SCOTT_J_LINK} alleging abuse of a girl from Kansas",
        timestamp=parse('2019-06-19'),
    ),
    FileCfg(id='031447', description=f"letter from {MARTIN_WEINBERG} to Melanie Ann Pustay and Sean O'Neill re: an Epstein FOIA request"),
    FileCfg(
        id='026793',
        description=f"letter from {STEVEN_HOFFENBERG}'s lawyers at Mintz Fraade offering to take over Epstein's business and resolve his legal issues",
        timestamp=parse('2018-03-23'),
    ),
    FileCfg(
        id='016420',
        description=f"{NEW_YORK_V_EPSTEIN} New York Post Motion to Unseal Appellate Briefs",
        timestamp=parse('2019-01-11'),
    ),
    FileCfg(id='028540', description=f"SCOTUS decision in Budha Ismail Jam et al. v. INTERNATIONAL FINANCE CORP"),
    FileCfg(id='012197', description=f"SDFL Response to {JAY_LEFKOWITZ} on Epstein Plea Agreement Compliance"),
    FileCfg(id='022277', description=f"{TEXT_OF_US_LAW} National Labour Relations Board (NLRB)"),
    FileCfg(id='030769', description=f"2017 Independent Filmmaker Project (IFP) Gotham Awards invitation"),
    # conferences
    FileCfg(id='014951', description=f"2017 TED Talks program", timestamp=parse('2017-04-20')),
    FileCfg(id='023069', description=f'{BOFA_MERRILL} 2016 Future of Financials Conference'),
    FileCfg(id='014315', description=f'{BOFA_MERRILL} 2016 Future of Financials Conference'),
    FileCfg(id='026825', description=f"Deutsche Asset & Wealth Management featured speaker bios"),
    FileCfg(id='017526', description=f'Intellectual Jazz conference brochure f. {DAVID_BLAINE}'),
    FileCfg(id='023120', description=f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more (old draft)"),
    FileCfg(id='023123', description=f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more", duplicate_ids=['023121'], dupe_type='earlier'),
    FileCfg(id='031359', description=f"{NOBEL_CHARITABLE_TRUST} Earth Environment Convention about ESG investing"),
    FileCfg(id='031354', description=f'{NOBEL_CHARITABLE_TRUST} "Thinking About the Environment and Technology" report 2011'),
    FileCfg(id='024179', description=f'president and first lady schedule at 67th U.N. General Assembly', timestamp=parse('2012-09-21')),
    FileCfg(id='029427', description=f"seems related to an IRL meeting about concerns China will attempt to absorb Mongolia"),
    FileCfg(
        id='024185',
        description=f'schedule of 67th U.N. General Assembly w/"Presidents Private Dinner - Jeffrey Epstine (sic)"',
        timestamp=parse('2012-09-21'),
    ),
    FileCfg(id='025797', description=f'someone\'s notes from Aspen Strategy Group', timestamp=parse('2013-05-29')),
    FileCfg(id='017524', description=f"{SWEDISH_LIFE_SCIENCES_SUMMIT} 2012 program", timestamp=parse('2012-08-22')),
    FileCfg(id='026747', description=f"{SWEDISH_LIFE_SCIENCES_SUMMIT} 2017 program", timestamp=parse('2017-08-23')),
    FileCfg(id='026731', description=f"text of speech by Lord Martin Rees at first inaugural Carl Sagan Lecture at Cornell"),
    FileCfg(id='019300', description=f'{WOMEN_EMPOWERMENT} f. {KATHRYN_RUEMMLER}', timestamp=parse('2019-04-05')),
    FileCfg(id='022267', description=f'{WOMEN_EMPOWERMENT} founder essay about growing the seminar business'),
    FileCfg(id='022407', description=f'{WOMEN_EMPOWERMENT} seminar pitch deck'),
    FileCfg(
        id='017060',
        description=f'World Economic Forum (WEF) Annual Meeting 2011 List of Participants',
        timestamp=parse('2011-01-18'),
    ),

    # press releases, reports, etc.
    FileCfg(id='024631', description=f"Ackrell Capital Cannabis Investment Report 2018"),
    FileCfg(id='016111', description=f'{BOFA_MERRILL} "GEMs Paper #26 Saudi Arabia: beyond oil but not so fast"', timestamp=parse('2016-06-30')),
    FileCfg(id='010609', description=f'{BOFA_MERRILL} "Liquid Insight Trump\'s effect on MXN"', timestamp=parse('2016-09-22')),
    FileCfg(id='025978', description=f'{BOFA_MERRILL} "Understanding when risk parity risk Increases"', timestamp=parse('2016-08-09')),
    FileCfg(id='014404', description=f'{BOFA_MERRILL} Japan Investment Strategy Report', timestamp=parse('2016-11-18')),
    FileCfg(id='014410', description=f'{BOFA_MERRILL} Japan Investment Strategy Report', timestamp=parse('2016-11-18')),
    FileCfg(id='014424', description=f'{BOFA_MERRILL} "Japan Macro Watch"', timestamp=parse('2016-11-14')),
    FileCfg(id='014731', description=f'{BOFA_MERRILL} "Global Rates, FX & EM 2017 Year Ahead"', timestamp=parse('2016-11-16')),
    FileCfg(id='014432', description=f'{BOFA_MERRILL} "Global Cross Asset Strategy - Year Ahead The Trump inflection"', timestamp=parse('2016-11-30')),
    FileCfg(id='014460', description=f'{BOFA_MERRILL} "European Equity Strategy 2017"', timestamp=parse('2016-12-01')),
    FileCfg(id='014972', description=f'{BOFA_MERRILL} "Global Equity Volatility Insights"', timestamp=parse('2017-06-20')),
    FileCfg(id='014622', description=f'{BOFA_MERRILL} "Top 10 US Ideas Quarterly"', timestamp=parse('2017-01-03')),
    FileCfg(id='014721', description=f'{BOFA_MERRILL} "Cause and Effect Fade the Trump Risk Premium"', timestamp=parse('2017-02-13')),
    FileCfg(id='014887', description=f'{BOFA_MERRILL} "Internet / e-Commerce"', timestamp=parse('2017-04-06')),
    FileCfg(id='014873', description=f'{BOFA_MERRILL} "Hess Corp"', timestamp=parse('2017-04-11')),
    FileCfg(id='023575', description=f'{BOFA_MERRILL} "Global Equity Volatility Insights"', timestamp=parse('2017-06-01')),
    FileCfg(id='014518', description=f'{BOFA_WEALTH_MGMT} tax alert', timestamp=parse('2016-05-02')),
    FileCfg(id='029438', description=f'{BOFA_WEALTH_MGMT} tax report', timestamp=parse('2018-01-02')),
    FileCfg(id='024271', description=f"Blockchain Capital and Brock Pierce pitch deck", timestamp=parse('2015-10-01')),
    FileCfg(id='024302', description=f"Carvana form 14A SEC filing proxy statement", timestamp=parse('2019-04-23')),
    FileCfg(id='029305', description=f"CCH Tax Briefing on end of Defense of Marriage Act", timestamp=parse('2013-06-27')),
    FileCfg(id='024817', description=f"Cowen's Collective View of CBD / Cannabis report"),
    FileCfg(id='026794', description=f'{DEUTSCHE_BANK} Global Public Affairs report: "Global Political and Regulatory Risk in 2015/2016"'),
    FileCfg(id='022361', description=f'{DEUTSCHE_BANK_TAX_TOPICS}', timestamp=parse('2013-05-01')),
    FileCfg(id='022325', description=f'{DEUTSCHE_BANK_TAX_TOPICS}', timestamp=parse('2013-12-20')),
    FileCfg(id='022330', description=f'{DEUTSCHE_BANK_TAX_TOPICS} table of contents', timestamp=parse('2013-12-20')),
    FileCfg(id='019440', description=f'{DEUTSCHE_BANK_TAX_TOPICS}', timestamp=parse('2014-01-29')),
    FileCfg(
        id='024202',
        description=f'Electron Capital Partners LLC "Global Utility White Paper"',
        timestamp=parse('2013-03-08'),
    ),
    FileCfg(id='022372', description=f'Ernst & Young 2016 election report'),
    FileCfg(
        id='025663',
        description=f'{GOLDMAN_SACHS} report "An Overview of the Current State of Cryptocurrencies and Blockchain"',
        timestamp=parse('2017-11-01'),
    ),
    FileCfg(id='014532', description=f'{GOLDMAN_REPORT} "Outlook - Half Full"', timestamp=parse('2017-01-01')),
    FileCfg(
        id='026909',
        description=f'{GOLDMAN_REPORT} "The Unsteady Undertow Commands the Seas (Temporarily)"',
        timestamp=parse('2018-10-14'),
    ),
    FileCfg(
        id='026944',
        description=f'{GOLDMAN_REPORT} "Risk of a US-Iran Military Conflict"',
        timestamp=parse('2019-05-23'),
    ),
    FileCfg(id='026679', description=f'Invesco report: "Global Sovereign Asset Management Study 2017"'),
    FileCfg(id='023096', description=f'{EPSTEIN_FOUNDATION} blog', timestamp=parse('2012-11-15')),
    FileCfg(id='029326', description=f'{EPSTEIN_FOUNDATION} {PRESS_RELEASE}', timestamp=parse('2013-02-15')),
    FileCfg(
        id='026565',
        description=f'{EPSTEIN_FOUNDATION} {PRESS_RELEASE}, maybe a draft of 029326',
        timestamp=parse('2013-02-15'),
    ),
    FileCfg(id='026572', description=f"{JP_MORGAN} Global Asset Allocation report", timestamp=parse('2012-11-09')),
    FileCfg(id='030848', description=f"{JP_MORGAN} Global Asset Allocation report", timestamp=parse('2013-03-28')),
    FileCfg(id='030840', description=f"{JP_MORGAN} Market Thoughts", timestamp=parse('2012-11-01')),
    FileCfg(id='022350', description=f"{JP_MORGAN} report on tax efficiency of Intentionally Defective Grantor Trusts (IDGT)"),
    FileCfg(id='025242', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2012-04-09')),
    FileCfg(id='030010', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2011-06-14')),
    FileCfg(id='030808', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2011-07-11')),
    FileCfg(id='025221', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2011-07-25')),
    FileCfg(id='025229', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2011-08-04')),
    FileCfg(id='030814', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2011-11-21')),
    FileCfg(id='024132', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2012-03-15')),
    FileCfg(id='024194', description=f"{JP_MORGAN_EYE_ON_THE_MARKET}", timestamp=parse('2012-10-22')),
    FileCfg(id='025296', description=f'Laffer Associates report predicting Trump win', timestamp=parse('2016-07-01')),
    FileCfg(
        id='025551',
        description=f'Morgan Stanley report about alternative asset managers',
        timestamp=parse('2018-01-30'),
    ),
    FileCfg(
        id='026759',
        description=f'{PRESS_RELEASE} by Ritz-Carlton club about damage from Hurricane Irma',
        timestamp=parse('2017-09-13'),
    ),
    FileCfg(
        id='033338',
        description=f"{PRESS_RELEASE} announcing Donald Trump & {NICHOLAS_RIBIS} ended their working relationship at Trump's casino",
        timestamp=parse('2000-06-07'),
    ),
    FileCfg(id='012048', description=f'{PRESS_RELEASE} "Rockefeller Partners with Gregory J. Fleming to Create Independent Financial Services Firm" and other articles'),
    FileCfg(id='020447', description=f'Promoting Constructive Vigilance: Report of the Working Group on Chinese Influence Activities in the U.S. (Hoover Group/Stanford 2018)'),
    FileCfg(
        id='025763',
        description=f'S&P Economic Research: "How Increasing Income Inequality Is Dampening U.S. Growth"',
        timestamp=parse('2014-08-05'),
    ),
    FileCfg(id='019856', description=f"Sadis Goldberg LLP report on SCOTUS ruling about insider trading"),
    FileCfg(id='026827', description=f'Scowcroft Group report on ISIS', timestamp=parse('2015-11-14')),
    FileCfg(id='033220', description=f"short economic report on defense spending under Trump by Joseph G. Carson"),
    FileCfg(
        id='026856',
        description=f'speech by former Australian PM Kevin Rudd "Xi Jinping, China And The Global Order"',
        timestamp=parse('2018-06-26'),
    ),
    FileCfg(
        id='023133',
        description=f'"The Search for Peace in the Arab-Israeli Conflict" edited by {TERJE_ROD_LARSEN}, Nur Laiq, Fabrice Aidan',
        timestamp=parse('2019-12-09'),
    ),
    FileCfg(id='024135', description=f'{UBS_CIO_REPORT}', timestamp=parse('2012-06-29')),
    FileCfg(id='025247', description=f'{UBS_CIO_REPORT}', timestamp=parse('2012-10-25')),
    FileCfg(id='025849', description=f'US Office of Government Information Services report: "Building a Bridge Between FOIA Requesters & Agencies"'),
    FileCfg(
        id='020824',
        description=f"USA Inc: A Basic Summary of America's Financial Statements compiled by Mary Meeker",
        timestamp=parse('2011-02-01'),
    ),
    FileCfg(id='017789', description=f'{ALAN_DERSHOWITZ} letter to {HARVARD} Crimson complaining he was defamed'),
    # letters
    FileCfg(
        id='019086',
        description=f"{DAVID_BLAINE_VISA_LETTER} from Russia 'Svet' ({SVETLANA_POZHIDAEVA}?), names Putin puppet regimes",  # Date is a guess based on other drafts,
        timestamp=parse('2015-05-27'),
    ),
    FileCfg(
        id='019474',
        description=f"{DAVID_BLAINE_VISA_LETTER} from Russia 'Svetlana' ({SVETLANA_POZHIDAEVA}?)",
        timestamp=parse('2015-05-29'),
    ),
    FileCfg(
        id='019476',
        description=f"{DAVID_BLAINE_VISA_LETTER} (probably {SVETLANA_POZHIDAEVA}?)",
        timestamp=parse('2015-06-01'),
    ),
    FileCfg(id='031670', description=f"letter from General Mike Flynn's lawyers to senators Mark Warner & Richard Burr about subpoena"),
    FileCfg(
        id='026011',
        description=f"letter from Gennady Mashtalyar to Epstein about algorithmic trading",  # date is based on Brexit reference but he could be backtesting,
        timestamp=parse('2016-06-24'),
    ),
    FileCfg(
        id='029301',
        description=f"letter from {MICHAEL_J_BOCCIO}, former lawyer at the Trump Organization",
        timestamp=parse('2011-08-07'),
    ),
    FileCfg(id='022405', description=f"letter from {NOAM_CHOMSKY} attesting to Epstein's good character"),
    FileCfg(id='026248', description=f'letter from Trump lawyer Don McGahn to Devin Nunes (R-CA) about FISA courts and Trump'),
    FileCfg(id='026134', description=f'letter to someone named George about investment opportunities in the Ukraine banking sector'),
    FileCfg(id='029304', description=f"Trump recommendation letter for recently departed Trump Organization lawyer {MICHAEL_J_BOCCIO}"),
    FileCfg(id='026668', description=f"Boothbay Fund Management 2016-Q4 earnings report signed by Ari Glass"),
    # private placement memoranda
    FileCfg(id='024432', description=f"Michael Milken's Knowledge Universe Education (KUE) $1,000,000 corporate share placement notice (SEC filing?)"),
    FileCfg(id='024003', description=f"New Leaf Ventures private placement memorandum"),
    FileCfg(id='018804', description=f"appraisal of going concern for IGY American Yacht Harbor Marina in {VIRGIN_ISLANDS}"),
    # property
    FileCfg(id='018743', description=f"Las Vegas property listing"),
    FileCfg(id='016597', description=f'letter from Trump Properties LLC appealing some decision about Mar-a-Lago by {PALM_BEACH} authorities'),
    FileCfg(id='016602', description=PALM_BEACH_CODE_ENFORCEMENT, timestamp=parse('2008-04-17')),
    FileCfg(id='016554', description=PALM_BEACH_CODE_ENFORCEMENT, timestamp=parse('2008-07-17'), duplicate_ids=['016616', '016574']),
    FileCfg(id='016695', description=f"{PALM_BEACH} property info (?)"),
    FileCfg(id='016697', description=f"{PALM_BEACH} property tax info (?) that mentions Trump"),
    FileCfg(id='016636', description=f"{PALM_BEACH_WATER_COMMITTEE} Meeting on January 29, 2009"),
    FileCfg(id='022417', description=f"Park Partners NYC letter to partners in real estate project with architectural plans"),
    FileCfg(id='027068', description=f"{THE_REAL_DEAL_ARTICLE}", timestamp=parse('2018-10-11')),
    FileCfg(
        id='029520',
        description=f'{THE_REAL_DEAL_ARTICLE} "Lost Paradise at the Palm House"',
        timestamp=parse('2019-06-17'),
    ),
    FileCfg(
        id='018727',
        description=f"{VIRGIN_ISLANDS} property deal pitch deck, building will be leased to the U.S. govt GSA",
        timestamp=parse('2014-06-01'),
    ),
    FileCfg(id='016599', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    # TSV files
    FileCfg(id='016600', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    FileCfg(id='016601', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    FileCfg(id='016694', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    FileCfg(id='016552', description=f"{PALM_BEACH_TSV} info"),
    FileCfg(id='016698', description=f"{PALM_BEACH_TSV} info (broken?)"),
    FileCfg(id='016696', description=f"{PALM_BEACH_TSV} info (water quality?"),
    FileCfg(id='026582', description=f"{REPUTATION_MGMT} Epstein's internet search results at start of reputation repair campaign, maybe from {OSBORNE_LLP}"),
    # reputation management
    FileCfg(id='030573', description=f"{REPUTATION_MGMT} Epstein's unflattering Google search results, maybe screenshot by {AL_SECKEL} or {OSBORNE_LLP}"),
    FileCfg(id='026583', description=f"{REPUTATION_MGMT} Google search results for '{JEFFREY_EPSTEIN}' with analysis ({OSBORNE_LLP}?)"),
    FileCfg(id='029350', description=f"{REPUTATION_MGMT} Microsoft Bing search results for Epstein with sex offender at top, maybe from {TYLER_SHEARS}?"),
    FileCfg(
        id='030426',
        description=f'{REPUTATION_MGMT} {OSBORNE_LLP} reputation repair proposal (cites Michael Milken)',
        timestamp=parse('2011-06-14'),
    ),
    FileCfg(id='030875', description=f"{REPUTATION_MGMT} {SCREENSHOT} Epstein's Wikipedia page"),
    FileCfg(id='031743', description=f'a few pages describing the internet as a "New Nation State" (Network State?)'),
    # misc
    FileCfg(id='018703', description=f"{ANDRES_SERRANO} artist statement about Trump objects"),
    FileCfg(id='028281', description=f'art show flier for "The House Of The Nobleman" curated by Wolfe Von Lenkiewicz & Victoria Golembiovskaya'),
    FileCfg(id='023438', description=f"Brockman announcemeent of auction of 'Noise' by Daniel Kahneman, Olivier Sibony, and Cass Sunstein"),
    FileCfg(
        id='025147',
        description=f'Brockman hot list Frankfurt Book Fair (includes article about Silk Road/Ross Ulbricht)',
        timestamp=parse('2016-10-23'),
    ),
    FileCfg(id='031425', description=f'completely redacted email from {SCOTT_J_LINK}'),
    FileCfg(id='012718', description=f"{CVRA} congressional record", timestamp=parse('2011-06-17')),
    FileCfg(id='018224', description=f"conversation with {LAWRENCE_KRAUSS}?"),
    FileCfg(id='023050', description=f"{DERSH_GIUFFRE_TWEET}"),
    FileCfg(id='017787', description=f"{DERSH_GIUFFRE_TWEET}"),
    FileCfg(id='033433', description=f"{DERSH_GIUFFRE_TWEET} / David Boies", timestamp=parse('2019-03-02')),
    FileCfg(id='033432', description=f"{DERSH_GIUFFRE_TWEET} / David Boies", timestamp=parse('2019-05-02')),
    FileCfg(id='029918', description=f"{DIANA_DEGETTES_CAMPAIGN} campaign bio", timestamp=parse('2012-01-01')),
    FileCfg(id='031184', description=f"{DIANA_DEGETTES_CAMPAIGN} fundraiser invitation"),
    FileCfg(id='027009', description=f"{EHUD_BARAK} speech to AIPAC", timestamp=parse('2013-03-03')),
    FileCfg(id='025540', description=f"Epstein's rough draft of his side of the story?"),
    FileCfg(id='024117', description=f"FAQ about anti-money laundering (AML) and terrorist financing (CFT) laws in the U.S."),
    FileCfg(id='027071', description=f"{FEMALE_HEALTH_COMPANY} brochure request donations for female condoms in Uganda"),
    FileCfg(id='027074', description=f"{FEMALE_HEALTH_COMPANY} pitch deck (USAID was a customer)"),
    FileCfg(id='022780', description=FLIGHT_LOGS,),
    FileCfg(id='022816', description=FLIGHT_LOGS,),
    FileCfg(id='026678', description=f"fragment of image metadata {QUESTION_MARKS}", timestamp=parse('2017-06-29')),
    FileCfg(id='022986', description=f"fragment of a screenshot {QUESTION_MARKS}"),
    FileCfg(id='026521', description=f"game theory paper by {MARTIN_NOWAK}, Erez Yoeli, and Moshe Hoffman"),
    FileCfg(
        id='032735',
        description=f"{GORDON_GETTY} on Trump",  # Dated based on concurrent emails from Getty,
        timestamp=parse('2018-03-20'),
    ),
    FileCfg(id='019396', description=f'{HARVARD} Economics 1545 Professor Kenneth Rogoff syllabus'),
    FileCfg(id='023416', description=HARVARD_POETRY,),
    FileCfg(id='023435', description=HARVARD_POETRY,),
    FileCfg(id='023450', description=HARVARD_POETRY,),
    FileCfg(id='023452', description=HARVARD_POETRY,),
    FileCfg(id='029517', description=HARVARD_POETRY,),
    FileCfg(id='029543', description=HARVARD_POETRY,),
    FileCfg(id='029589', description=HARVARD_POETRY,),
    FileCfg(id='029603', description=HARVARD_POETRY,),
    FileCfg(id='029298', description=HARVARD_POETRY,),
    FileCfg(id='029592', description=HARVARD_POETRY,),
    FileCfg(id='029102', description=HBS_APPLICATION_NERIO,),
    FileCfg(id='029104', description=HBS_APPLICATION_NERIO,),
    FileCfg(
        id='022445',
        description=f"Inference: International Review of Science Feedback & Comments",
        timestamp=parse('2018-11-01'),
    ),
    FileCfg(id='028815', description=f"{INSIGHTS_POD} business plan", timestamp=parse('2016-08-20')),
    FileCfg(
        id='011170',
        description=f'{INSIGHTS_POD} collected tweets about #Brexit',
        timestamp=parse('2016-06-23'),
    ),
    FileCfg(
        id='032324',
        description=f"{INSIGHTS_POD} election social media trend analysis",
        timestamp=parse('2016-11-05'),
    ),
    FileCfg(id='032281', description=f"{INSIGHTS_POD} forecasting election for Trump", timestamp=parse('2016-10-25')),
    FileCfg(id='028988', description=f"{INSIGHTS_POD} pitch deck", timestamp=parse('2016-08-20')),
    FileCfg(id='026627', description=f"{INSIGHTS_POD} report on the presidential debate"),
    FileCfg(
        id='030142',
        description=f"{JASTA} (Justice Against Sponsors of Terrorism Act) doc that's mostly empty, references suit against Saudi f. {KATHRYN_RUEMMLER} & {KEN_STARR}",
        timestamp=parse('2016-09-01'),
    ),
    FileCfg(id='033177', description=f'{MEME} Trump with text "WOULD YOU TRUST THIS MAN WITH YOUR DAUGHTER?"'),
    FileCfg(id='025205', description=MERCURY_FILMS_PROFILES, timestamp=parse('2010-02-01'), duplicate_ids=['025210']),
    FileCfg(id='029564', description=OBAMA_JOKE, timestamp=parse('2013-07-26')),
    FileCfg(id='029353', description=OBAMA_JOKE, timestamp=parse('2013-07-26')),
    FileCfg(id='029352', description=OBAMA_JOKE, timestamp=parse('2013-07-26')),
    FileCfg(id='029351', description=OBAMA_JOKE, timestamp=parse('2013-07-26')),
    FileCfg(id='029354', description=OBAMA_JOKE, timestamp=parse('2013-07-26')),
    FileCfg(id='026851', description=f"Politifact lying politicians chart", timestamp=parse('2016-07-26')),
    FileCfg(id='022367', description=f"{RESUME_OF} Jack J Grynberg", timestamp=parse('2014-07-01')),
    FileCfg(
        id='029302',
        description=f"{RESUME_OF} {MICHAEL_J_BOCCIO}, former lawyer at the Trump Organization",
        timestamp=parse('2011-08-07'),
    ),
    FileCfg(
        id='015671',
        description=f"{RESUME_OF} Robin Solomon",  # She left Mount Sinai at some point in 2015,
        timestamp=parse('2015-06-02'),
    ),
    FileCfg(
        id='015672',
        description=f"{RESUME_OF} Robin Solomon",  # She left Mount Sinai at some point in 2015,
        timestamp=parse('2015-06-02'),
    ),
    FileCfg(id='019448', description=f"Haitian business investment proposal called Jacmel"),
    FileCfg(id='029328', description=f"Rafanelli Events promotional deck"),
    FileCfg(id='029155', description=f'response sent to the Gruterites ({GORDON_GETTY} fans) by {ROBERT_TRIVERS}', timestamp=parse('2018-03-19')),
    FileCfg(id='023666', description=f"{ROBERT_LAWRENCE_KUHN} sizzle reel / television appearances"),
    FileCfg(id='022213', description=f"{SCREENSHOT} Facebook group called 'Shit Pilots Say' disparaging a 'global girl'"),
    FileCfg(id='033434', description=f"{SCREENSHOT} iPhone chat labeled 'Edwards' at the top"),
    FileCfg(id='029623', description=f'short bio of Kathleen Harrington, Founding Partner, C/H Global Strategies'),
    FileCfg(id='026634', description=f"some short comments about an Apollo linked hedge fund 'DE Fund VIII'"),
    FileCfg(id='024294', description=f"{STACEY_PLASKETT} campaign flier", timestamp=parse('2016-10-01')),
    FileCfg(id='023644', description=f"transcription of an interview with MBS from Saudi", timestamp=parse('2016-04-25')),
    FileCfg(id='010617', description=TRUMP_DISCLOSURES, timestamp=parse('2017-01-20')),
    FileCfg(id='016699', description=TRUMP_DISCLOSURES, timestamp=parse('2017-01-20')),
    FileCfg(id='030884', description=f"{TWEET} by Ed Krassenstein"),
    FileCfg(id='031546', description=f"{TWEET}s by Donald Trump about Russian collusion", timestamp=parse('2018-01-06')),
    FileCfg(id='033236', description=f'{TWEET}s about Ivanka Trump in Arabic', timestamp=parse('2017-05-20')),
    FileCfg(id='029475', description=f'{VIRGIN_ISLANDS} Twin City Mobile Integrated Health Services (TCMIH) proposal/request for donation'),
    FileCfg(id='029448', description=f'weird short essay titled "President Obama and Self-Deception"'),
]

# Create a dict keyed by file_id
ALL_FILE_CONFIGS: dict[str, FileCfg] = {}

# Add extra config objects for duplicate files that match the config of file they are duplicating
for cfg in ALL_CONFIGS:
    ALL_FILE_CONFIGS[cfg.id] = cfg

    for dupe_cfg in cfg.duplicate_cfgs():
        ALL_FILE_CONFIGS[dupe_cfg.id] = dupe_cfg

EMAIL_CONFIGS = {id: cfg for id, cfg in ALL_FILE_CONFIGS.items() if isinstance(cfg, MessageCfg)}


# TODO: Dupe scanning should be removed evenutally
for cfg in ALL_FILE_CONFIGS.values():
    if not cfg.dupe_of_id:
        continue

    if cfg.dupe_of_id in ALL_FILE_CONFIGS:
        dupe_of_cfg = ALL_FILE_CONFIGS[cfg.dupe_of_id]
        pfx = f"{dupe_of_cfg.id} is duplicated by {cfg.id}"

        if cfg.was_generated:
            # print(f"{pfx}, duplicate config was generated...")
            continue
        elif dupe_of_cfg == cfg:
            print(f"\n{pfx}, configurations are the same\n")
        else:
            print(f"\n{pfx} but configs differ...")
            print(f"    {dupe_of_cfg.id}: {dupe_of_cfg}")
            print(f"    {cfg.id}: {cfg}")
            print(f"\n        Fix in {dupe_of_cfg.id}:   \", duplicate_ids=['{cfg.id}']\"")

        fix = f"\", duplicate_ids=['{dupe_of_cfg.id}']"

        if cfg.dupe_type != 'same':
            fix += f", dupe_type='{cfg.dupe_type}'"

        print(f"        Fix in {cfg.id}:   {fix}\"\n")


# Error checking.
encountered_file_ids = set()

for cfg in ALL_CONFIGS:
    if cfg.dupe_of_id and cfg.dupe_of_id == cfg.id:
        raise ValueError(f"Invalid config!\n\n{cfg}\n")
    elif cfg.id in encountered_file_ids:
        raise ValueError(f"{cfg.id} configured twice!\n\n{cfg}\n")

    encountered_file_ids.add(cfg.id)
