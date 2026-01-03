import re
from copy import deepcopy

from dateutil.parser import parse

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.doc_cfg import EmailCfg, DocCfg, TextCfg

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
    ANAS_ALRASHEED: re.compile(r'anas\s*al\s*rashee[cd]', re.IGNORECASE),
    ANIL_AMBANI: re.compile(r'Anil.Ambani', re.IGNORECASE),
    ANN_MARIE_VILLAFANA: re.compile(r'Villafana, Ann Marie|(A(\.|nn) Marie )?Villafa(n|ri)a', re.IGNORECASE),
    ANTHONY_SCARAMUCCI: re.compile(r"mooch|(Anthony ('The Mooch' )?)?Scaramucci", re.IGNORECASE),
    ARIANE_DE_ROTHSCHILD: re.compile(r'AdeR|((Ariane|Edmond) de )?Rothschild|Ariane', re.IGNORECASE),
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
    JOHNNY_EL_HACHEM: re.compile(r'el hachem johnny|johnny el hachem', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|(joichi|joi)( Ito)?', re.IGNORECASE),
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
    MICHAEL_SITRICK: re.compile(r'(Mi(chael|ke).{0,5})?[CS]itrick', re.IGNORECASE),
    MICHAEL_WOLFF: re.compile(r'Michael\s*Wol(f[ef]|i)|Wolff', re.IGNORECASE),
    MIROSLAV_LAJCAK: re.compile(r"Miro(slav)?(\s+Laj[cč][aá]k)?"),
    MOHAMED_WAHEED_HASSAN: re.compile(r'Mohamed Waheed(\s+Hassan)?', re.IGNORECASE),
    NADIA_MARCINKO: re.compile(r"Na[dď]i?a\s+Marcinko(v[aá])?", re.IGNORECASE),
    NEAL_KASSELL: re.compile(r'Neal\s*Kassell?', re.IGNORECASE),
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
FLIGHT_IN_2012_PEOPLE: list[str | None] = ['Francis Derby', 'Januiz Banasiak', 'Louella Rabuyo', 'Richard Barnnet']


##########################
# OtherFile config stuff #
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
BRUNEL_V_EPSTEIN = f"{JEAN_LUC_BRUNEL} v. {JEFFREY_EPSTEIN}"
EDWARDS_V_DERSHOWITZ = f"{BRAD_EDWARDS} & {PAUL_G_CASSELL} v. {ALAN_DERSHOWITZ}:"
EPSTEIN_V_ROTHSTEIN_EDWARDS = f"Epstein v. Scott Rothstein, {BRAD_EDWARDS}, and L.M.:"
GIUFFRE_V_DERSHOWITZ = f"{VIRGINIA_GIUFFRE} v. {ALAN_DERSHOWITZ}:"
GIUFFRE_V_EPSTEIN = f"{VIRGINIA_GIUFFRE} v. {JEFFREY_EPSTEIN}:"
GIUFFRE_V_MAXWELL = f"{VIRGINIA_GIUFFRE} v. {GHISLAINE_MAXWELL}:"
JANE_DOE_V_EPSTEIN_TRUMP = f"Jane Doe v. Donald Trump and {JEFFREY_EPSTEIN}:"
JANE_DOE_V_USA = 'Jane Doe #1 and Jane Doe #2 v. United States:'
NEW_YORK_V_EPSTEIN = f"New York v. {JEFFREY_EPSTEIN}:"

# Descriptions of non-email, non-text message files
ARTICLE_DRAFT = 'draft of an article about'
BOFA = 'BofA'
BOFA_MERRILL = f'{BOFA} / Merrill Lynch Report'
BOFA_WEALTH_MGMT = f'{BOFA} Wealth Management'
CHALLENGES_OF_AI = f'ASU Origins Project ({LAWRENCE_KRAUSS}) report "Challenges of AI: Envisioning and Addressing Adverse Outcomes"'
CVRA = "Crime Victims' Rights Act [CVRA]"
DAVID_BLAINE_VISA_LETTER = f"letter of recommendation for visa for a model"
DAVID_SCHOEN_CVRA_LEXIS_SEARCH = f"Lexis Nexis search for case law around the {CVRA} by {DAVID_SCHOEN}"
DEEP_THINKING_HINT = f'{BOOK} "Deep Thinking: Twenty-Five Ways of Looking at AI" by John Brockman'
DERSH_GIUFFRE_TWEET = f"{TWEET} by {ALAN_DERSHOWITZ} about {VIRGINIA_GIUFFRE}"
DEUTSCHE_BANK_TAX_TOPICS = f'{DEUTSCHE_BANK} Wealth Management Tax Topics'
DIANA_DEGETTES_CAMPAIGN = "Colorado legislator Diana DeGette's campaign"
EPSTEIN_FOUNDATION = 'Jeffrey Epstein VI Foundation'
FBI_REPORT = f"{FBI} report on Epstein investigation (redacted)"
FBI_SEIZED_PROPERTY = f"{FBI} seized property inventory (redacted)"
FEMALE_HEALTH_COMPANY = 'Female Health Company (FHX)'
FIRE_AND_FURY = f"'Fire And Fury' by {MICHAEL_WOLFF}"
GOLDMAN_REPORT = f'{GOLDMAN_SACHS} Investment Management Division report'
HARVARD_POETRY = f'{HARVARD} poetry stuff from {LISA_NEW}'
HBS_APPLICATION_NERIO = f"{HARVARD} Business School application letter from Nerio Alessandri (Founder and Chairman Technogym SPA Italy)"
JASTA = 'JASTA'
JASTA_SAUDI_LAWSUIT = f"{JASTA} lawsuit against Saudi Arabia by 9/11 victims"
JOHN_BOLTON_PRESS_CLIPPING = 'John Bolton press clipping'
JP_MORGAN_EYE_ON_THE_MARKET = f"{JP_MORGAN} Eye On The Market report"
KEN_STARR_LETTER = f"letter to judge overseeing Epstein's criminal prosecution, mentions Alex Acosta"
MICHAEL_WOLFF_ARTICLE_HINT = f"draft of an unpublished article about Epstein by {MICHAEL_WOLFF} written ca. 2014/2015"
NIGHT_FLIGHT_HINT = f'draft of book named "Night Flight"'
NOBEL_CHARITABLE_TRUST = 'Nobel Charitable Trust'
OBAMA_JOKE = 'joke about Obama'
PALM_BEACH = 'Palm Beach'
PALM_BEACH_CODE_ENFORCEMENT = f'{PALM_BEACH} code enforcement board minutes'
PALM_BEACH_DAILY_ARTICLE = f'{PALM_BEACH} Daily News article about'
PALM_BEACH_POST_ARTICLE = f'{PALM_BEACH} Post article about'
PALM_BEACH_TSV = f"TSV of {PALM_BEACH} property"
PALM_BEACH_WATER_COMMITTEE = f'{PALM_BEACH} Water Committee'
PATTERSON_BOOK_SCANS = f"pages of 'Filthy Rich: The Shocking True Story of {JEFFREY_EPSTEIN}'"
SHIMON_POST = 'The Shimon Post'
SHIMON_POST_ARTICLE = f'{SHIMON_POST} selection of articles about the mideast'
SINGLE_PAGE = 'single page of'
SWEDISH_LIFE_SCIENCES_SUMMIT = f"{BARBRO_C_EHNBOM}'s Swedish American Life Science Summit"
THE_REAL_DEAL_ARTICLE = 'article by Keith Larsen'
TRUMP_DISCLOSURES = f"Donald Trump financial disclosures from U.S. Office of Government Ethics"
UBS = 'UBS'
UBS_CIO_REPORT = 'CIO Monthly Extended report'
VI_DAILY_NEWS_ARTICLE = f'{VIRGIN_ISLANDS} Daily News article'
WOMEN_EMPOWERMENT = f"Women Empowerment (WE) conference run by {SVETLANA_POZHIDAEVA}"
ZUBAIR_AND_ANYA = f"{ZUBAIR_KHAN} and Anya Rasulova"

# Atribution reasons
BOLOTOVA_REASON = 'Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")'
KATHY_REASON = 'from "Kathy" about dems, sent from iPad'
LARRY_REASON = 'Planes discussion signed "Larry"'
PAULA_REASON = 'Signature of "Sent via BlackBerry from T-Mobile"'


################################################################################################
############################################ TEXTS #############################################
################################################################################################

CONFIRMED_TEXTS_CONFIG = [
    TextCfg(id='031042', author=ANIL_AMBANI, attribution_reason='Participants: field'),
    TextCfg(id='027225', author=ANIL_AMBANI, attribution_reason='Birthday mentioned and confirmed as Ambani\'s'),
    TextCfg(id='031173', author=ARDA_BESKARDES, attribution_reason='Participants: field'),
    TextCfg(id='027401', author='Eva (Dubin?)', attribution_reason='Participants: field'),
    TextCfg(id='027650', author=JOI_ITO, attribution_reason='Participants: field'),
    TextCfg(id='027777', author=LARRY_SUMMERS, attribution_reason='Participants: field'),
    TextCfg(id='027515', author=MIROSLAV_LAJCAK, attribution_reason='https://x.com/ImDrinknWyn/status/1990210266114789713'),
    TextCfg(id='027165', author=MELANIE_WALKER, attribution_reason='https://www.wired.com/story/jeffrey-epstein-claimed-intimate-knowledge-of-donald-trumps-views-in-texts-with-bill-gates-adviser/'),
    TextCfg(id='027248', author=MELANIE_WALKER, attribution_reason='Says "we met through trump" which is confirmed by Melanie in 032803'),
    TextCfg(id='025429', author=STACEY_PLASKETT, attribution_reason='widely reported'),
    TextCfg(id='027333', author=ANTHONY_SCARAMUCCI, attribution_reason='unredacted phone number in one of the messages belongs to Scaramucci'),
    TextCfg(id='027128', author=SOON_YI_PREVIN, attribution_reason='https://x.com/ImDrinknWyn/status/1990227281101434923'),
    TextCfg(id='027217', author=SOON_YI_PREVIN, attribution_reason='refs marriage to Woody Allen'),
    TextCfg(id='027244', author=SOON_YI_PREVIN, attribution_reason='refs Woody'),
    TextCfg(id='027257', author=SOON_YI_PREVIN, attribution_reason="'Woody Allen' in Participants: field"),
    TextCfg(id='027460', author=STEVE_BANNON, attribution_reason='Discusses leaving scotland when Bannon was confirmed in Scotland, also NYT'),
    TextCfg(id='027307', author=STEVE_BANNON),
    TextCfg(id='027278', author=TERJE_ROD_LARSEN),
    TextCfg(id='027255', author=TERJE_ROD_LARSEN),
]

UNCONFIRMED_TEXTS_CONFIG = [
    TextCfg(id='027762', author=ANDRZEJ_DUDA),
    TextCfg(id='027774', author=ANDRZEJ_DUDA),
    TextCfg(id='027221', author=ANIL_AMBANI),
    TextCfg(id='025436', author=CELINA_DUBIN),
    TextCfg(id='027576', author=MELANIE_WALKER, attribution_reason='https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.023700'),
    TextCfg(id='027141', author=MELANIE_WALKER),
    TextCfg(id='027232', author=MELANIE_WALKER),
    TextCfg(id='027133', author=MELANIE_WALKER),
    TextCfg(id='027184', author=MELANIE_WALKER),
    TextCfg(id='027214', author=MELANIE_WALKER),
    TextCfg(id='027148', author=MELANIE_WALKER),
    TextCfg(id='027440', author=MICHAEL_WOLFF, attribution_reason='AI says Trump book/journalism project'),
    TextCfg(id='027396', author=ANTHONY_SCARAMUCCI),
    TextCfg(id='031054', author=ANTHONY_SCARAMUCCI),
    TextCfg(id='025363', author=STEVE_BANNON, attribution_reason='Trump and New York Times coverage'),
    TextCfg(id='025368', author=STEVE_BANNON, attribution_reason='Trump and New York Times coverage'),
    TextCfg(id='027585', author=STEVE_BANNON, attribution_reason='references Tokyo trip'),
    TextCfg(id='027568', author=STEVE_BANNON),
    TextCfg(id='027695', author=STEVE_BANNON),
    TextCfg(id='027594', author=STEVE_BANNON),
    TextCfg(id='027720', author=STEVE_BANNON, attribution_reason='first 3 lines of 027722'),
    TextCfg(id='027549', author=STEVE_BANNON),
    TextCfg(id='027434', author=STEVE_BANNON, attribution_reason='references Maher appearance'),
    TextCfg(id='027764', author=STEVE_BANNON),
    TextCfg(id='027428', author=STEVE_BANNON, attribution_reason='references HBJ meeting on 9/28 from other Bannon/Epstein convo'),
    TextCfg(id='025400', author=STEVE_BANNON, attribution_reason='AI says Trump NYT article criticism; Hannity media strategy'),
    TextCfg(id='025408', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='025452', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='025479', author=STEVE_BANNON, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='025707', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='025734', author=STEVE_BANNON, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='027260', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027281', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027346', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027365', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027374', author=STEVE_BANNON, attribution_reason='AI says China strategy and geopolitics'),
    TextCfg(id='027406', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027445', author=STEVE_BANNON, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='027455', author=STEVE_BANNON, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='027536', author=STEVE_BANNON, attribution_reason='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='027655', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027707', author=STEVE_BANNON, attribution_reason='AI says Italian politics; Trump discussions'),
    TextCfg(id='027722', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027735', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='027794', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='029744', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
    TextCfg(id='031045', author=STEVE_BANNON, attribution_reason='AI says Trump and New York Times coverage'),
]

for cfg in UNCONFIRMED_TEXTS_CONFIG:
    cfg.is_attribution_uncertain = True

TEXTS_CONFIG = CONFIRMED_TEXTS_CONFIG + UNCONFIRMED_TEXTS_CONFIG


########################################################################################################
################################################ EMAILS ################################################
########################################################################################################

EMAILS_CONFIG = [
    EmailCfg(id='032436', author=ALIREZA_ITTIHADIEH, attribution_reason='Signature'),
    EmailCfg(id='032543', author=ANAS_ALRASHEED, attribution_reason='Later reply 033000 has quote'),
    EmailCfg(id='026064', author=ARIANE_DE_ROTHSCHILD),
    EmailCfg(id='026069', author=ARIANE_DE_ROTHSCHILD),
    EmailCfg(id='030741', author=ARIANE_DE_ROTHSCHILD),
    EmailCfg(id='026018', author=ARIANE_DE_ROTHSCHILD),
    EmailCfg(
        id='029504',
        author='Audrey/Aubrey Raimbault (???)',
        attribution_reason='based on "GMI" in signature, a company registered by "aubrey raimbault"',
    ),
    EmailCfg(id='033316', author=AZIZA_ALAHMADI, attribution_reason='"Regards, Aziza" at bottom'),
    EmailCfg(id='033328', author=AZIZA_ALAHMADI, attribution_reason='"Regards, Aziza" at bottom'),
    EmailCfg(id='026659', author=BARBRO_C_EHNBOM, attribution_reason='Reply'),
    EmailCfg(id='031215', author=BARBRO_C_EHNBOM, duplicate_ids=['026745'], dupe_type='redacted'),  # the same except for 'your Anna!'. author must be specified because email address is redacted in 026745 so it needs the config
    EmailCfg(id='026764', author=BARRY_J_COHEN),
    EmailCfg(id='031206', author=BENNET_MOSKOWITZ, duplicate_ids=['031227']),
    EmailCfg(id='031442', author=CHRISTINA_GALBRAITH, duplicate_ids=['031996']),
    EmailCfg(
        id='019446',
        author=CHRISTINA_GALBRAITH,
        attribution_reason='shows from "Christina media/PR" which fits',
        is_attribution_uncertain=True,
    ),
    EmailCfg(id='026625', author=DARREN_INDYKE, actual_text='Hysterical.'),
    EmailCfg(
        id='026624',
        author=DARREN_INDYKE,
        recipients=[JEFFREY_EPSTEIN],
        timestamp=parse('2016-10-01 16:40:00'),
        duplicate_ids=['031708'],
    ),
    EmailCfg(
        id='031278',
        author=DARREN_INDYKE,
        description=f"heavily redacted email, quoted replies are from {STEVEN_HOFFENBERG} about James Patterson's book",
        timestamp=parse('2016-08-17 11:26:00'),
        attribution_reason='Quoted replies are in 019109',
    ),
    EmailCfg(id='026290', author=DAVID_SCHOEN, attribution_reason='Signature'),
    EmailCfg(id='031339', author=DAVID_SCHOEN, attribution_reason='Signature'),
    EmailCfg(id='031492', author=DAVID_SCHOEN, attribution_reason='Signature'),
    EmailCfg(id='031560', author=DAVID_SCHOEN, attribution_reason='Signature'),
    EmailCfg(id='026287', author=DAVID_SCHOEN, attribution_reason='Signature'),
    EmailCfg(id='033419', author=DAVID_SCHOEN, attribution_reason='Signature'),
    EmailCfg(id='031460', author=EDWARD_JAY_EPSTEIN),
    EmailCfg(id='030414', author=FAITH_KATES, duplicate_ids=['030578'], dupe_type='redacted'),
    EmailCfg(id='031135', author=FAITH_KATES, duplicate_ids=['030634'], dupe_type='redacted'),
    EmailCfg(id='026547', author=GERALD_BARTON, recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    EmailCfg(id='029969', author=GWENDOLYN_BECK, attribution_reason='Signature'),
    EmailCfg(id='029968', author=GWENDOLYN_BECK, attribution_reason='Signature', duplicate_ids=['031120']),
    EmailCfg(id='029970', author=GWENDOLYN_BECK),
    EmailCfg(id='029960', author=GWENDOLYN_BECK, attribution_reason='Reply'),
    EmailCfg(id='029959', author=GWENDOLYN_BECK, attribution_reason='"Longevity & Aging"'),
    EmailCfg(id='033360', author=HENRY_HOLT, attribution_reason='in signature'),  # Henry Holt is a company not a person
    EmailCfg(id='033384', author=JACK_GOLDBERGER, attribution_reason='Might be Paul Prosperi?', is_attribution_uncertain=True),
    EmailCfg(id='026024', author=JEAN_HUGUEN, attribution_reason='Signature'),
    EmailCfg(id='021823', author=JEAN_LUC_BRUNEL, attribution_reason='Reply'),
    EmailCfg(id='022949', author=JEFFREY_EPSTEIN),
    EmailCfg(id='031624', author=JEFFREY_EPSTEIN),
    EmailCfg(id='031996', author=JEFFREY_EPSTEIN, recipients=[CHRISTINA_GALBRAITH], attribution_reason='bounced', duplicate_ids=['031442']),
    EmailCfg(id='025041', author=JEFFREY_EPSTEIN, recipients=[LARRY_SUMMERS], duplicate_ids=['028675']),  # Bad OCR
    EmailCfg(
        id='029692',  # TODO: this file's header is jankily prettified
        author=JEFFREY_EPSTEIN,
        is_fwded_article=True,  # Bad OCR, WaPo article
        recipients=[LARRY_SUMMERS],
        duplicate_ids=['029779'],
    ),
    EmailCfg(id='018726', author=JEFFREY_EPSTEIN, timestamp=parse('2018-06-08 08:36:00')),
    EmailCfg(id='032283', author=JEFFREY_EPSTEIN, timestamp=parse('2016-09-14 08:04:00')),
    EmailCfg(id='026943', author=JEFFREY_EPSTEIN, timestamp=parse('2019-05-22 05:47:00')),
    EmailCfg(id='023208', author=JEFFREY_EPSTEIN, recipients=[BRAD_WECHSLER, MELANIE_SPINELLA], duplicate_ids=['023291']),
    EmailCfg(
        id='032214',
        author=JEFFREY_EPSTEIN,
        actual_text='Agreed',
        recipients=[MIROSLAV_LAJCAK],
        attribution_reason='Quoted reply has signature',
    ),
    EmailCfg(id='029582', author=JEFFREY_EPSTEIN, recipients=[RENATA_BOLOTOVA], attribution_reason=BOLOTOVA_REASON),
    EmailCfg(id='030997', author=JEFFREY_EPSTEIN, actual_text='call back'),
    EmailCfg(id='028770', author=JEFFREY_EPSTEIN, actual_text='call me now'),
    EmailCfg(id='031826', author=JEFFREY_EPSTEIN, actual_text='I have'),
    EmailCfg(id='030768', author=JEFFREY_EPSTEIN, actual_text='ok'),
    EmailCfg(id='022938', author=JEFFREY_EPSTEIN, actual_text='what do you suggest?'),  # TODO: this email's header rewrite sucks
    EmailCfg(id='031791', author=JESSICA_CADWELL),
    EmailCfg(id='028851', author=JOI_ITO, recipients=[JEFFREY_EPSTEIN], timestamp=parse('2014-04-27 06:00:00')),
    EmailCfg(
        id='028849',
        author=JOI_ITO,
        recipients=[JEFFREY_EPSTEIN],
        timestamp=parse('2014-04-27 06:30:00'),
        attribution_reason='Conversation with Joi Ito',
    ),
    EmailCfg(id='016692', author=JOHN_PAGE),
    EmailCfg(id='016693', author=JOHN_PAGE),
    EmailCfg(id='028507', author=JONATHAN_FARKAS),
    EmailCfg(id='033282', author=JONATHAN_FARKAS, duplicate_ids=['033484']),
    EmailCfg(id='033582', author=JONATHAN_FARKAS, attribution_reason='Reply', duplicate_ids=['032389']),
    EmailCfg(id='033203', author=JONATHAN_FARKAS, attribution_reason='Reply', duplicate_ids=['033581']),
    EmailCfg(id='032052', author=JONATHAN_FARKAS, attribution_reason='Reply', duplicate_ids=['031732']),
    EmailCfg(id='033490', author=JONATHAN_FARKAS, attribution_reason='Signature', duplicate_ids=['032531']),
    EmailCfg(id='032224', author=KATHRYN_RUEMMLER, recipients=[JEFFREY_EPSTEIN], attribution_reason='Reply'),
    EmailCfg(id='032386', author=KATHRYN_RUEMMLER, attribution_reason=KATHY_REASON, is_attribution_uncertain=True),
    EmailCfg(id='032727', author=KATHRYN_RUEMMLER, attribution_reason=KATHY_REASON, is_attribution_uncertain=True),
    EmailCfg(id='030478', author=LANDON_THOMAS),
    EmailCfg(id='029013', author=LARRY_SUMMERS, recipients=[JEFFREY_EPSTEIN]),
    EmailCfg(id='032206', author=LAWRENCE_KRAUSS),                                # More of a text convo?
    EmailCfg(id='032208', author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN]),  # More of a text convo?
    EmailCfg(id='032209', author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN]),  # More of a text convo?
    EmailCfg(id='029196', author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN], actual_text='Talk in 40?'),  # TODO: this email's header rewrite sucks
    EmailCfg(id='033593', author=LAWRANCE_VISOSKI, attribution_reason='Signature'),
    EmailCfg(id='033370', author=LAWRANCE_VISOSKI, attribution_reason=LARRY_REASON),
    EmailCfg(id='033495', author=LAWRANCE_VISOSKI, attribution_reason=LARRY_REASON),
    EmailCfg(id='033487', author=LAWRANCE_VISOSKI, recipients=[JEFFREY_EPSTEIN]),
    EmailCfg(
        id='029977',
        author=LAWRANCE_VISOSKI,
        recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, LESLEY_GROFF, RICHARD_KAHN] + FLIGHT_IN_2012_PEOPLE,
        attribution_reason=LARRY_REASON,
        duplicate_ids=['031129'],
    ),
    EmailCfg(id='027046', author=LAWRANCE_VISOSKI, duplicate_ids=['028789']),
    EmailCfg(id='033488', author=LAWRANCE_VISOSKI, duplicate_ids=['033154']),
    EmailCfg(id='033309', author=LINDA_STONE, attribution_reason='"Co-authored with iPhone autocorrect"'),
    EmailCfg(id='017581', author='Lisa Randall'),
    EmailCfg(id='026609', author='Mark Green', attribution_reason='Actually a fwd'),
    EmailCfg(id='030472', author=MARTIN_WEINBERG, attribution_reason='Maybe. in reply', is_attribution_uncertain=True),
    EmailCfg(id='030235', author=MELANIE_WALKER, attribution_reason='In fwd'),
    EmailCfg(id='032343', author=MELANIE_WALKER, attribution_reason='Name seen in later reply 032346'),
    EmailCfg(id='032212', author=MIROSLAV_LAJCAK),
    EmailCfg(id='022193', author=NADIA_MARCINKO),
    EmailCfg(id='021814', author=NADIA_MARCINKO),
    EmailCfg(id='021808', author=NADIA_MARCINKO),
    EmailCfg(id='022190', author=NADIA_MARCINKO),
    EmailCfg(id='021818', author=NADIA_MARCINKO),
    EmailCfg(id='022197', author=NADIA_MARCINKO),
    EmailCfg(id='022214', author=NADIA_MARCINKO, attribution_reason='Reply header'),
    EmailCfg(id='021811', author=NADIA_MARCINKO, attribution_reason='Signature and email address in the message'),
    EmailCfg(id='028487', author=NORMAN_D_RAU, attribution_reason='Fwded from "to" address', duplicate_ids=['026612']),
    EmailCfg(
        id='024923',
        author=PAUL_KRASSNER,
        recipients=['George Krassner', 'Nick Kazan', 'Mrisman02', 'Rebecca Risman', 'Linda W. Grossman'],
        duplicate_ids=['031973']
    ),
    EmailCfg(id='032457', author=PAUL_KRASSNER),
    EmailCfg(id='029981', author=PAULA, attribution_reason='Name in reply + opera reference (Fisher now works in opera)'),
    EmailCfg(id='030482', author=PAULA, attribution_reason=PAULA_REASON),
    EmailCfg(id='033383', author=PAUL_PROSPERI, attribution_reason='Reply'),
    EmailCfg(
        id='033561',
        author=PAUL_PROSPERI,
        attribution_reason='Fwded mail sent to Prosperi. Might be Subotnick Stuart?',
        duplicate_ids=['033157'],
    ),
    EmailCfg(id='031694', author=PEGGY_SIEGAL),
    EmailCfg(id='032219', author=PEGGY_SIEGAL, attribution_reason='Signed "Peggy"'),
    EmailCfg(id='029020', author=RENATA_BOLOTOVA, attribution_reason='Signature'),
    EmailCfg(id='029605', author=RENATA_BOLOTOVA, attribution_reason=BOLOTOVA_REASON),
    EmailCfg(id='029606', author=RENATA_BOLOTOVA, attribution_reason=BOLOTOVA_REASON),
    EmailCfg(id='029604', author=RENATA_BOLOTOVA, attribution_reason='Continued in 239606 etc'),
    EmailCfg(
        id='033584',
        author=ROBERT_TRIVERS,
        recipients=[JEFFREY_EPSTEIN],
        attribution_reason='Refs paper by Trivers',
        duplicate_ids=['033169'],
    ),
    EmailCfg(
        id='026320',
        author=SEAN_BANNON,
        attribution_reason="From protonmail, Bannon wrote 'just sent from my protonmail' in 027067",
    ),
    EmailCfg(id='029003', author=SOON_YI_PREVIN, attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    EmailCfg(id='029005', author=SOON_YI_PREVIN, attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    EmailCfg(id='029007', author=SOON_YI_PREVIN, attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    EmailCfg(id='029010', author=SOON_YI_PREVIN, attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    EmailCfg(id='032296', author=SOON_YI_PREVIN, attribution_reason="\"Sent from Soon-Yi's iPhone\""),
    EmailCfg(
        id='019109',
        author=STEVEN_HOFFENBERG,
        recipients=["Players2"],
        timestamp=parse('2016-08-11 09:36:01'),
        attribution_reason='Actually a fwd by Charles Michael but Hoffenberg email more interesting',
    ),
    EmailCfg(
        id='026620',
        author=TERRY_KAFKA,
        recipients=[JEFFREY_EPSTEIN, MARK_EPSTEIN, MICHAEL_BUCHHOLTZ] + IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS,
        attribution_reason='"Respectfully, terry"',
        duplicate_ids=['028482'],
    ),
    EmailCfg(id='029992', author=TERRY_KAFKA, attribution_reason='Quoted reply'),
    EmailCfg(id='029985', author=TERRY_KAFKA, attribution_reason='Quoted reply in 029992'),
    EmailCfg(id='020666', author=TERRY_KAFKA, attribution_reason="Ends with 'Terry'"),
    EmailCfg(id='026014', author=ZUBAIR_KHAN, recipients=[JEFFREY_EPSTEIN], timestamp=parse('2016-11-04 17:46:00')),
    EmailCfg(id='030626', recipients=[ALAN_DERSHOWITZ, DARREN_INDYKE, KATHRYN_RUEMMLER, KEN_STARR, MARTIN_WEINBERG]),
    EmailCfg(id='029835', recipients=[ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN], duplicate_ids=['028968']),
    EmailCfg(id='027063', recipients=[ANTHONY_BARRETT]),
    EmailCfg(id='030764', recipients=[ARIANE_DE_ROTHSCHILD], attribution_reason='Reply'),
    EmailCfg(id='026431', recipients=[ARIANE_DE_ROTHSCHILD], attribution_reason='Reply'),
    EmailCfg(id='032876', recipients=[CECILIA_STEEN]),
    EmailCfg(id='033583', recipients=[DARREN_INDYKE, JACK_GOLDBERGER]),  # Bad OCR
    EmailCfg(id='033144', recipients=[DARREN_INDYKE, RICHARD_KAHN]),
    EmailCfg(id='026466', recipients=[DIANE_ZIMAN], attribution_reason='Quoted reply'),
    EmailCfg(id='031607', recipients=[EDWARD_JAY_EPSTEIN]),
    EmailCfg(
        id='030525',
        recipients=[FAITH_KATES],
        attribution_reason='Same as unredacted 030414, same legal signature',
        duplicate_ids=['030581'],
    ),
    EmailCfg(
        id='030475',
        recipients=[FAITH_KATES],
        attribution_reason='Next Management LLC legal signature',
        duplicate_ids=['030575'],
        dupe_type='redacted'
    ),
    EmailCfg(id='030999', recipients=[JACK_GOLDBERGER, ROBERT_D_CRITTON]),
    EmailCfg(id='026426', recipients=[JEAN_HUGUEN], attribution_reason='Reply'),
    EmailCfg(id='022202', recipients=[JEAN_LUC_BRUNEL], attribution_reason='Follow up / reply', duplicate_ids=['029975']),
    EmailCfg(id='022187', recipients=[JEFFREY_EPSTEIN]),
    EmailCfg(id='031489', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    EmailCfg(id='032210', recipients=[JEFFREY_EPSTEIN]),  # More of a text convo?
    EmailCfg(id='030347', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    EmailCfg(id='030367', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    EmailCfg(id='033274', recipients=[JEFFREY_EPSTEIN]),  # this is a note sent to self
    EmailCfg(id='032780', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    EmailCfg(id='025233', recipients=[JEFFREY_EPSTEIN]),  # Bad OCR
    EmailCfg(id='022344', recipients=[JEFFREY_EPSTEIN], duplicate_ids=['028529']),  # Bad OCR
    EmailCfg(id='029324', recipients=[JEFFREY_EPSTEIN, "Jojo Fontanilla", "Lyn Fontanilla"]),
    EmailCfg(id='033575', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN], duplicate_ids=['012898']),
    EmailCfg(id='023067', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN, TONJA_HADDAD_COLEMAN]),  # Bad OCR
    EmailCfg(id='033228', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, FRED_HADDAD]),  # Bad OCR
    EmailCfg(id='025790', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER], duplicate_ids=['031994']),  # Bad OCR
    EmailCfg(
        id='031384',
        actual_text='',
        recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER, MARTIN_WEINBERG, SCOTT_J_LINK],
    ),
    EmailCfg(id='033512', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACKIE_PERCZEK, MARTIN_WEINBERG], duplicate_ids=['033361']),
    EmailCfg(id='032063', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, REID_WEINGARTEN]),
    EmailCfg(id='033486', recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, RICHARD_KAHN], duplicate_ids=['033156']),  # Bad OCR
    EmailCfg(id='029154', recipients=[JEFFREY_EPSTEIN, DAVID_HAIG]),  # Bad OCR
    EmailCfg(id='029498', recipients=[JEFFREY_EPSTEIN, DAVID_HAIG, GORDON_GETTY, "Norman Finkelstein"]),  # Bad OCR
    EmailCfg(id='029889', recipients=[JEFFREY_EPSTEIN, "Connie Zaguirre", JACK_GOLDBERGER, ROBERT_D_CRITTON]),  # Bad OCR
    EmailCfg(id='028931', recipients=[JEFFREY_EPSTEIN, LAWRENCE_KRAUSS]),  # Bad OCR
    EmailCfg(id='019407', recipients=[JEFFREY_EPSTEIN, MICHAEL_SITRICK]),  # Bad OCR
    EmailCfg(id='031980', recipients=[JEFFREY_EPSTEIN, MICHAEL_SITRICK], duplicate_ids=['019409']),  # Bad OCR
    EmailCfg(id='029163', recipients=[JEFFREY_EPSTEIN, ROBERT_TRIVERS]),   # Bad OCR
    EmailCfg(id='030299', recipients=[JESSICA_CADWELL, ROBERT_D_CRITTON], duplicate_ids=['021794']),  # Bad OCR
    EmailCfg(id='033456', recipients=["Joel"], attribution_reason='Reply'),
    EmailCfg(id='033460', recipients=["Joel"], attribution_reason='Reply'),
    EmailCfg(
        id='021090',
        is_fwded_article=True,
        recipients=[JONATHAN_FARKAS],
        attribution_reason='Reply to a message signed "jonathan" same as other Farkas emails',
    ),
    EmailCfg(
        id='033073',
        recipients=[KATHRYN_RUEMMLER],
        attribution_reason='to "Kathy" about dems, sent from iPad',
        is_attribution_uncertain=True,  # It's actually Kathy R. as t eh recipient that's the uncertain part
    ),
    EmailCfg(
        id='032939',
        recipients=[KATHRYN_RUEMMLER],
        attribution_reason='to "Kathy" about dems, sent from iPad',
        is_attribution_uncertain=True,  # It's actually Kathy R. as t eh recipient that's the uncertain part
    ),
    EmailCfg(id='031428', recipients=[KEN_STARR, LILLY_SANCHEZ, MARTIN_WEINBERG, REID_WEINGARTEN], duplicate_ids=['031388']), # Bad OCR
    EmailCfg(id='025329', recipients=['Nancy Cain', 'Tom', 'Marie Moneysmith', 'Steven Gaydos', 'George Krassner', 'Linda W. Grossman', 'Holly Krassner Dawson', 'Daniel Dawson', 'Danny Goldberg', 'Caryl Ratner', 'Kevin Bright', 'Michael Simmons', SAMUEL_LEFF, 'Bob Fass', 'Lynnie Tofte Fass', 'Barb Cowles', 'Lee Quarnstrom']),
    EmailCfg(id='033568', recipients=['George Krassner', 'Daniel Dawson', 'Danny Goldberg', 'Tom', 'Kevin Bright', 'Walli Leff', 'Michael Simmons', 'Lee Quarnstrom', 'Lanny Swerdlow', 'Larry Sloman', 'W&K', 'Harry Shearer', 'Jay Levin']),
    EmailCfg(id='030522', recipients=[LANDON_THOMAS], is_fwded_article=True),  # Vicky Ward article
    EmailCfg(id='031413', recipients=[LANDON_THOMAS]),
    EmailCfg(id='033591', recipients=[LAWRANCE_VISOSKI], attribution_reason='Reply signature', duplicate_ids=['033591']),
    EmailCfg(id='027097', recipients=[LAWRANCE_VISOSKI], attribution_reason='Reply signature', duplicate_ids=['028787']),
    EmailCfg(id='033466', recipients=[LAWRANCE_VISOSKI], attribution_reason='Reply signature'),
    EmailCfg(id='022250', recipients=[LESLEY_GROFF], attribution_reason='Reply'),
    EmailCfg(id='030242', recipients=[MARIANA_IDZKOWSKA], duplicate_ids=['032048'], dupe_type='redacted'),
    EmailCfg(id='030368', recipients=[MELANIE_SPINELLA], attribution_reason='Actually a self fwd from jeffrey to jeffrey'),
    EmailCfg(id='030369', recipients=[MELANIE_SPINELLA], attribution_reason='Actually a self fwd from jeffrey to jeffrey'),
    EmailCfg(id='030371', recipients=[MELANIE_SPINELLA], attribution_reason='Actually a self fwd from jeffrey to jeffrey'),
    EmailCfg(id='022258', recipients=[NADIA_MARCINKO], attribution_reason='Reply header'),
    EmailCfg(id='033097', recipients=[PAUL_BARRETT, RICHARD_KAHN]),  # Bad OCR
    EmailCfg(id='030506', recipients=[PAULA], attribution_reason=PAULA_REASON, is_attribution_uncertain=True),
    EmailCfg(id='030507', recipients=[PAULA], attribution_reason=PAULA_REASON, is_attribution_uncertain=True),
    EmailCfg(id='030508', recipients=[PAULA], attribution_reason=PAULA_REASON, is_attribution_uncertain=True),
    EmailCfg(id='030509', recipients=[PAULA], attribution_reason=PAULA_REASON, is_attribution_uncertain=True),
    EmailCfg(id='030096', recipients=[PETER_MANDELSON]),
    EmailCfg(id='032951', recipients=[RAAFAT_ALSABBAGH, None], attribution_reason='Redacted'),
    EmailCfg(id='029581', recipients=[RENATA_BOLOTOVA], attribution_reason=BOLOTOVA_REASON),
    EmailCfg(id='030384', recipients=[RICHARD_KAHN, "Alan Dlugash"]),
    EmailCfg(id='019334', recipients=[STEVE_BANNON]),
    EmailCfg(id='021106', recipients=[STEVE_BANNON], attribution_reason='Reply'),
    EmailCfg(id='033050', actual_text='schwartman'),
    EmailCfg(id='023627', description=MICHAEL_WOLFF_ARTICLE_HINT, is_fwded_article=True),
    EmailCfg(id='026298', is_fwded_article=True, duplicate_ids=['026499']),  # Written by someone else?
    EmailCfg(id='026755', is_fwded_article=True),  # HuffPo
    EmailCfg(id='030528', is_fwded_article=True),  # Vicky Ward article
    EmailCfg(id='018197', is_fwded_article=True, duplicate_ids=['028648']),  # Ray Takeyh article fwd
    EmailCfg(id='028728', is_fwded_article=True, duplicate_ids=['027102']),  # WSJ forward to Larry Summers
    EmailCfg(id='028508', is_fwded_article=True),  # nanosatellites article
    EmailCfg(id='028781', is_fwded_article=True, duplicate_ids=['013460']),  # Atlantic on Jim Yong Kim, Obama's World Bank Pick
    EmailCfg(id='019845', is_fwded_article=True),  # Pro Publica article on Preet Bharara
    EmailCfg(id='029021', is_fwded_article=True),  # article about bannon sent by Alain Forget
    EmailCfg(id='031688', is_fwded_article=True),  # Bill Siegel fwd of email about hamas
    EmailCfg(id='026551', is_fwded_article=True),  # Sultan bin Sulayem "Ayatollah between the sheets"
    EmailCfg(id='031768', is_fwded_article=True),  # Sultan bin Sulayem 'Horseface'
    EmailCfg(id='031569', is_fwded_article=True),  # Article by Kathryn Alexeeff fwded to Peter Thiel
    EmailCfg(id='032475', timestamp=parse('2017-02-15 13:31:25')),
    EmailCfg(id='030373', timestamp=parse('2018-10-03 01:49:27')),

    # Configure duplicates
    EmailCfg(id='028768', duplicate_ids=['026563'], dupe_type='redacted'),
    EmailCfg(id='027056', duplicate_ids=['028762'], dupe_type='redacted'),
    EmailCfg(id='032248', duplicate_ids=['032246'], dupe_type='redacted'),
    EmailCfg(id='030628', duplicate_ids=['023065'], dupe_type='redacted'),
    EmailCfg(id='017523', duplicate_ids=['031226'], dupe_type='redacted'),
    EmailCfg(id='031099', duplicate_ids=['031008'], dupe_type='redacted'),
    EmailCfg(id='033596', duplicate_ids=['033463'], dupe_type='redacted'),
    EmailCfg(id='030624', duplicate_ids=['023018'], dupe_type='redacted'),
    EmailCfg(id='030335', duplicate_ids=['030596'], dupe_type='redacted'),
    EmailCfg(id='029841', duplicate_ids=['012711'], dupe_type='redacted'),
    EmailCfg(id='028497', duplicate_ids=['026228']),
    EmailCfg(id='033528', duplicate_ids=['033517']),
    EmailCfg(id='032023', duplicate_ids=['032012']),
    EmailCfg(id='019412', duplicate_ids=['028621']),
    EmailCfg(id='027053', duplicate_ids=['028765']),
    EmailCfg(id='027049', duplicate_ids=['028773']),
    EmailCfg(id='033580', duplicate_ids=['033207']),
    EmailCfg(id='028506', duplicate_ids=['025547']),
    EmailCfg(id='028784', duplicate_ids=['026549']),
    EmailCfg(id='033386', duplicate_ids=['033599']),
    EmailCfg(id='023024', duplicate_ids=['030622']),
    EmailCfg(id='030618', duplicate_ids=['023026']),
    EmailCfg(id='028780', duplicate_ids=['026834']),
    EmailCfg(id='028775', duplicate_ids=['026835']),
    EmailCfg(id='033251', duplicate_ids=['033489']),
    EmailCfg(id='031118', duplicate_ids=['019465']),
    EmailCfg(id='031912', duplicate_ids=['032158']),
    EmailCfg(id='030587', duplicate_ids=['030514']),
    EmailCfg(id='029773', duplicate_ids=['012685']),
    EmailCfg(id='029849', duplicate_ids=['033482']),
    EmailCfg(id='033297', duplicate_ids=['033586']),
    EmailCfg(id='031089', duplicate_ids=['018084']),
    EmailCfg(id='031088', duplicate_ids=['030885']),
    EmailCfg(id='030238', duplicate_ids=['031130']),
    EmailCfg(id='030859', duplicate_ids=['031067']),
    EmailCfg(id='031136', duplicate_ids=['028791']),
    EmailCfg(id='030635', duplicate_ids=['031134']),
    EmailCfg(id='028494', duplicate_ids=['026234']),
    EmailCfg(id='030311', duplicate_ids=['021790']),
    EmailCfg(id='033508', duplicate_ids=['029880']),
    EmailCfg(id='030493', duplicate_ids=['030612']),
    EmailCfg(id='032051', duplicate_ids=['031771']),
    EmailCfg(id='031217', duplicate_ids=['021761']),
    EmailCfg(id='031346', duplicate_ids=['031426']),
    EmailCfg(id='031345', duplicate_ids=['031427']),
    EmailCfg(id='031343', duplicate_ids=['031432']),
    EmailCfg(id='031020', duplicate_ids=['031084']),
    EmailCfg(id='033354', duplicate_ids=['033485']),
    EmailCfg(id='031999', duplicate_ids=['021241']),
    EmailCfg(id='030502', duplicate_ids=['030602']),
    EmailCfg(id='030574', duplicate_ids=['030617']),
    EmailCfg(id='031156', duplicate_ids=['025226']),
    EmailCfg(id='031018', duplicate_ids=['031086']),
    EmailCfg(id='031026', duplicate_ids=['031079']),
    EmailCfg(id='032011', duplicate_ids=['031787']),
    EmailCfg(id='030606', duplicate_ids=['030498']),
    EmailCfg(id='032005', duplicate_ids=['021235']),
    EmailCfg(id='028505', duplicate_ids=['026160']),
    EmailCfg(id='031126', duplicate_ids=['030837']),
    EmailCfg(id='029624', duplicate_ids=['029778']),
    EmailCfg(id='031338', duplicate_ids=['031422']),
    EmailCfg(id='033587', duplicate_ids=['033289']),
    EmailCfg(id='032107', duplicate_ids=['012722']),
    EmailCfg(id='030844', duplicate_ids=['031114']),
    EmailCfg(id='031031', duplicate_ids=['031074']),
    EmailCfg(id='027032', duplicate_ids=['028531']),
    EmailCfg(id='026777', duplicate_ids=['028493']),
    EmailCfg(id='029837', duplicate_ids=['029255']),
    EmailCfg(id='031423', duplicate_ids=['025361']),
    EmailCfg(id='029299', duplicate_ids=['033594']),
    EmailCfg(id='030904', duplicate_ids=['031069']),
    EmailCfg(id='030006', duplicate_ids=['031165']),
    EmailCfg(id='025215', duplicate_ids=['031159']),
    EmailCfg(id='031011', duplicate_ids=['031090']),
    EmailCfg(id='032068', duplicate_ids=['018158']),
    EmailCfg(id='031213', duplicate_ids=['031221']),
    EmailCfg(id='016595', duplicate_ids=['016690']),
    EmailCfg(id='029833', duplicate_ids=['028970']),
    EmailCfg(id='029839', duplicate_ids=['028958']),
    EmailCfg(id='029893', duplicate_ids=['033503']),
    EmailCfg(id='025878', duplicate_ids=['028486']),
    EmailCfg(id='032764', duplicate_ids=['033565']),
    EmailCfg(id='026618', duplicate_ids=['028485']),
    EmailCfg(id='030609', duplicate_ids=['030495']),
    EmailCfg(id='029831', duplicate_ids=['028972']),
    EmailCfg(id='021758', duplicate_ids=['030616']),
    EmailCfg(id='033498', duplicate_ids=['029884']),
    EmailCfg(id='028620', duplicate_ids=['027094']),
    EmailCfg(id='032456', duplicate_ids=['033579']),
    EmailCfg(id='030315', duplicate_ids=['030255']),
    EmailCfg(id='031112', duplicate_ids=['030876']),
    EmailCfg(id='030614', duplicate_ids=['030491']),
    EmailCfg(id='033585', duplicate_ids=['032279']),
    EmailCfg(id='031220', duplicate_ids=['031189']),
    EmailCfg(id='032779', duplicate_ids=['033563']),
    EmailCfg(id='033230', duplicate_ids=['033577']),
    EmailCfg(id='032125', duplicate_ids=['023971']),
    EmailCfg(id='031230', duplicate_ids=['031203']),
    EmailCfg(id='028752', duplicate_ids=['026569']),
    EmailCfg(id='031773', duplicate_ids=['032050']),
    EmailCfg(id='021400', duplicate_ids=['031983']),
    EmailCfg(id='026548', duplicate_ids=['033491']),
    EmailCfg(id='029752', duplicate_ids=['023550']),
    EmailCfg(id='030339', duplicate_ids=['030592']),
    EmailCfg(id='032250', duplicate_ids=['033589']),
]


################################################################################################
####################################### OTHER FILES ############################################
################################################################################################

OTHER_FILES_BOOKS = [
    DocCfg(id='015032', description=f"{BOOK} '60 Years of Investigative Satire: The Best of {PAUL_KRASSNER}'"),
    DocCfg(id='015675', description=f'{BOOK} "Are the Androids Dreaming Yet? Amazing Brain Human Communication, Creativity & Free Will" by James Tagg'),
    DocCfg(id='012899', description=f'{BOOK} "Engineering General Intelligence: A Path to Advanced AGI Via Embodied Learning and Cognitive Synergy" by Ben Goertzel'),
    DocCfg(id='012747', description=f'{BOOK} "Evilicious: Explaining Our Taste For Excessive Harm" by Marc D. Hauser'),
    DocCfg(id='019874', description=f'{BOOK} {FIRE_AND_FURY}', date='2018-01-05'),
    DocCfg(id='032724', description=f'{BOOK} cover of {FIRE_AND_FURY}', date='2018-01-05'),
    DocCfg(id='010912', description=f"{BOOK} 'Free Growth and Other Surprises' by Gordon Getty (draft)", date='2018-10-18'),
    DocCfg(
        id='021247',
        description=f'{BOOK} "Invisible Forces And Powerful Beliefs: Gravity, Gods, And Minds" by The Chicago Social Brain Network',
        date='2010-10-04',
    ),
    DocCfg(id='019477', description=f'{BOOK} "How America Lost Its Secrets: Edward Snowden, the Man, and the Theft" by {EDWARD_JAY_EPSTEIN}'),
    DocCfg(id='017088', description=f'{BOOK} "Taking the Stand: My Life in the Law" by {ALAN_DERSHOWITZ} (draft)'),
    DocCfg(id='023731', description=f'{BOOK} "Teaching Minds How Cognitive Science Can Save Our Schools" by {ROGER_SCHANK}'),
    DocCfg(id='013796', description=f'{BOOK} "The 4-Hour Workweek" by Tim Ferriss'),
    DocCfg(id='021145', description=f'{BOOK} "The Billionaire\'s Playboy Club" by {VIRGINIA_GIUFFRE} (draft?)'),
    DocCfg(id='013501', description=f'{BOOK} "The Nearness Of Grace: A Personal Science Of Spiritual Transformation" by Arnold J. Mandell', date='2005-01-01'),
    DocCfg(id='018438', description=f'{BOOK} "The S&M Feminist" by Clarisse Thorn'),
    DocCfg(id='018232', description=f'{BOOK} "The Seventh Sense: Power, Fortune & Survival in the Age of Networks" by Joshua Cooper Ramo'),
    DocCfg(id='020153', description=f'{BOOK} "The Snowden Affair: A Spy Story In Six Parts" by {EDWARD_JAY_EPSTEIN}'),
    DocCfg(id='021120', description=f'{BOOK} chapter of "Siege: Trump Under Fire" by {MICHAEL_WOLFF}'),
    DocCfg(id='016804', description=DEEP_THINKING_HINT, date='2019-02-19', duplicate_ids=['016221']),
    DocCfg(id='011472', author=EHUD_BARAK, description=NIGHT_FLIGHT_HINT,),
    DocCfg(id='027849', author=EHUD_BARAK, description=NIGHT_FLIGHT_HINT,),
    DocCfg(id='010477', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='010486', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='021958', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='022058', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='022118', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='019111', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='031533', description=f'pages from a book about the Baylor University sexual assault scandal and Sam Ukwuachu'),
]

OTHER_FILES_ARTICLES = [
    DocCfg(id='013275', author=BLOOMBERG, description=f"article on notable 2013 obituaries", date='2013-12-26'),
    DocCfg(id='026543', author=BLOOMBERG, description=f"BNA article about taxes"),
    DocCfg(id='023572', author=CHINA_DAILY, description=f"article on China's Belt & Road Initiative"),
    DocCfg(id='023571', author=CHINA_DAILY, description=f"article on terrorism, Macau, trade initiatives", date='2016-09-18'),
    DocCfg(id='023570', author=CHINA_DAILY, description=f"article on Belt & Road in Central/South America, Xi philosophy", date='2017-05-14'),
    DocCfg(id='025115', author=CHINA_DAILY, description=f"article on China and the US working together", date='2017-05-14'),
    DocCfg(id='025292', author=DAILY_MAIL, description=f"article on Bill Clinton being named in a lawsuit"),
    DocCfg(id='019468', author=DAILY_MAIL, description=f"article on Epstein and Clinton"),
    DocCfg(id='022970', author=DAILY_MAIL, description=f"article on Epstein and Prince Andrew"),
    DocCfg(id='031186', author=DAILY_MAIL, description=f'article on allegations of rape of 13 year old against Trump', date='2016-11-02'),
    DocCfg(id='013437', author=DAILY_TELEGRAPH, description=f"article about Epstein's diary", date='2011-03-05'),
    DocCfg(id='023287', author=DAILY_TELEGRAPH, description=f"article about a play based on the Oslo Accords", date='2017-09-15'),
    DocCfg(id='019206', author=EDWARD_JAY_EPSTEIN, description=f"WSJ article about Edward Snowden", date='2016-12-30'),
    DocCfg(id='029865', author=LA_TIMES, description=f"front page article about {DEEPAK_CHOPRA} and young Iranians", date='2016-11-05'),
    DocCfg(id='026598', author=LA_TIMES, description=f"op-ed about why America needs a Ministry of Culture"),
    DocCfg(id='022707', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='022727', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='022746', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='022844', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='022863', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='022894', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='022952', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='024229', author=MICHAEL_WOLFF, description=MICHAEL_WOLFF_ARTICLE_HINT),
    DocCfg(id='031753', author=PAUL_KRASSNER, description=f'essay for Playboy in the 1980s', date='1985-01-01'),
    DocCfg(id='023638', author=PAUL_KRASSNER, description=f'magazine interview'),
    DocCfg(id='024374', author=PAUL_KRASSNER, description=f"'Remembering Cavalier Magazine'"),
    DocCfg(id='030187', author=PAUL_KRASSNER, description=f'"Remembering Lenny Bruce While We\'re Thinking About Trump" (draft?)'),
    DocCfg(id='019088', author=PAUL_KRASSNER, description=f'"Are Rape Jokes Funny? (draft)', date='2012-07-28'),
    DocCfg(id='012740', author=PEGGY_SIEGAL, description=f"article about Venice Film Festival"),
    DocCfg(id='013442', author=PEGGY_SIEGAL, description=f"draft about Oscars", date='2011-02-27'),
    DocCfg(id='012700', author=PEGGY_SIEGAL, description=f"film events diary", date='2011-02-27'),
    DocCfg(id='012690', author=PEGGY_SIEGAL, description=f"film events diary early draft of 012700", date='2011-02-27'),
    DocCfg(id='013450', author=PEGGY_SIEGAL, description=f"Oscar Diary in Avenue Magazine", date='2011-02-27'),
    DocCfg(id='010715', author=PEGGY_SIEGAL, description=f"Oscar Diary April", date='2012-02-27'),
    DocCfg(id='019849', author=PEGGY_SIEGAL, description=f"Oscar Diary April", date='2017-02-27', duplicate_ids=['019864']),
    DocCfg(id='033253', author=ROBERT_LAWRENCE_KUHN, description=f'{BBC} article about Rohingya in Myanmar'),
    DocCfg(id='026887', author=ROBERT_LAWRENCE_KUHN, description=f'{BBC} "New Tariffs - Trade War"'),
    DocCfg(id='026877', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "New Tariffs - Trade War"'),
    DocCfg(id='026868', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "Quest Means Business New China Tariffs — Trade War"', date='2018-09-18'),
    DocCfg(id='023707', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "Quest Means Business U.S. and China Agree to Pause Trade War"', date='2018-12-03'),
    DocCfg(id='029176', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "U.S. China Tariffs - Trade War"'),
    DocCfg(id='032638', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "Xi Jinping and the New Politburo Committee"'),
    DocCfg(id='023666', author=ROBERT_LAWRENCE_KUHN, description=f"sizzle reel / television appearances"),
    DocCfg(id='025104', author='SCMP', description=f"article about China and globalisation"),
    DocCfg(id='033379', author=WAPO, description=f'How Washington Pivoted From Finger-Wagging to Appeasement (about Viktor Orban)', date='2018-05-25'),
    DocCfg(
        id='031396',
        author=WAPO,
        description=f"DOJ discipline office with limited reach to probe handling of controversial sex abuse case",
        date='2019-02-06',
        duplicate_ids=['031415'],
    ),
    DocCfg(
        id='030199',
        description=f'article about allegations Trump raped a 13 year old girl {JANE_DOE_V_EPSTEIN_TRUMP}',
        date='2017-11-16',
    ),
    DocCfg(id='031725', description=f"article about Gloria Allred and Trump allegations", date='2016-10-10'),
    DocCfg(id='031198', description=f"article about identify of Jane Doe in {JANE_DOE_V_EPSTEIN_TRUMP}"),
    DocCfg(id='012704', description=f"article about {JANE_DOE_V_USA} and {CVRA}", date='2011-04-21'),
    DocCfg(id='026648', description=f'article about {JASTA} lawsuit against Saudi Arabia by 9/11 victims (Russian propaganda?)', date='2017-05-13'),
    DocCfg(id='031776', description=f"article about Michael Avenatti by Andrew Strickler"),
    DocCfg(id='032159', description=f"article about microfinance and cell phones in Zimbabwe, Strive Masiyiwa (Econet Wireless)"),
    DocCfg(id='026584', description=f"article about tax implications of 'disregarded entities'", date='2009-07-01'),
    DocCfg(id='030258', description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030248'),
    DocCfg(id='030248', description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    DocCfg(id='029165', description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    DocCfg(id='033468', description=f'{ARTICLE_DRAFT} Rod Rosenstein', date='2018-09-24'),
    DocCfg(id='030825', description=f'{ARTICLE_DRAFT} Syria'),
    DocCfg(id='030013', description=f'Aviation International News article', date='2012-07-01'),
    DocCfg(id='014865', description=f"Boston Globe article about {ALAN_DERSHOWITZ}"),
    DocCfg(id='033231', description=f"Business Standard article about Trump's visit with India's Modi"),
    DocCfg(id='023567', description=f"Financial Times article about quantitative easing"),
    DocCfg(id='026761', description=f"Forbes article about {BARBRO_C_EHNBOM} 'Swedish American Group Focuses On Cancer'"),
    DocCfg(id='031716', description=f'Fortune Magazine article by {TOM_BARRACK}', date='2016-10-22'),
    DocCfg(
        id='019233',
        description=f"Freedom House: 'Breaking Down Democracy: Goals, Strategies, and Methods of Modern Authoritarians'",
        date='2017-06-02',
    ),
    DocCfg(id='019444', description=f"Frontlines magazine article 'Biologists Dig Deeper'", date='2008-01-01'),
    DocCfg(id='023720', description=f'Future Science article: "Is Shame Necessary?" by {JENNIFER_JACQUET}'),
    DocCfg(id='027051', description=f"German language article about the 2013 Lifeball / AIDS Gala", date='2013-01-01'),
    DocCfg(id='021094', description=f"Globe and Mail article about Gerd Heinrich"),
    DocCfg(id='013268', description=f"JetGala article about airplane interior designer {ERIC_ROTH}"),
    DocCfg(id='033480', description=f"{JOHN_BOLTON_PRESS_CLIPPING}", date='2018-04-06', duplicate_ids=['033481']),
    DocCfg(id='013403', description=f"Lexis Nexis result from The Evening Standard about Bernie Madoff", date='2009-12-24'),
    DocCfg(id='023102', description=f"Litigation Daily article about {REID_WEINGARTEN}", date='2015-09-04'),
    DocCfg(id='029340', description=f'MarketWatch article about estate taxes, particularly Epstein\'s favoured GRATs'),
    DocCfg(
        id='029416',
        description=f"National Enquirer / Radar Online v. FBI FOIA lawsuit court filing",
        date='2017-05-25',
        duplicate_ids=['029405']
    ),
    DocCfg(id='015462', description=f'Nautilus Education magazine (?) issue'),
    DocCfg(id='029925', description=f"New Yorker article about the placebo effect by Michael Specter"),
    DocCfg(id='031972', description=f"{NYT_ARTICLE} #MeToo allegations against {LAWRENCE_KRAUSS}", date='2018-03-07'),
    DocCfg(id='032435', description=f'{NYT_ARTICLE} Chinese butlers'),
    DocCfg(id='029452', description=f"{NYT_ARTICLE} {PETER_THIEL}"),
    DocCfg(id='025328', description=f"{NYT_ARTICLE} radio host Bob Fass and Robert Durst"),
    DocCfg(id='033479', description=f"{NYT_ARTICLE} Rex Tillerson", date='2010-03-14'),
    DocCfg(id='028481', description=f'{NYT_ARTICLE} {STEVE_BANNON}', date='2018-03-09'),
    DocCfg(id='033181', description=f'{NYT_ARTICLE} Trump\'s tax avoidance', date='2016-10-31'),
    DocCfg(id='023097', description=f"{NYT_COLUMN} The Aristocrats by Frank Rich 'The Greatest Dirty Joke Ever Told'"),
    DocCfg(id='033365', description=f'{NYT_COLUMN} trade war with China by Kevin Rudd'),
    DocCfg(id='019439', description=f"{NYT_COLUMN} the Clintons and money by Maureen Dowd", date='2013-08-17'),
    DocCfg(id='021093', description=f"page of unknown article about Epstein and Maxwell"),
    DocCfg(id='013435', description=f"{PALM_BEACH_DAILY_ARTICLE} Epstein's address book", date='2011-03-11'),
    DocCfg(id='013440', description=f"{PALM_BEACH_DAILY_ARTICLE} Epstein's gag order", date='2011-07-13'),
    DocCfg(id='029238', description=f"{PALM_BEACH_DAILY_ARTICLE} Epstein's plea deal"),
    DocCfg(id='021775', description=f"{PALM_BEACH_POST_ARTICLE} 'He Was 50. And They Were Girls'"),
    DocCfg(id='022989', description=f"{PALM_BEACH_POST_ARTICLE} alleged rape of 13 year old by Trump"),
    DocCfg(id='022987', description=f"{PALM_BEACH_POST_ARTICLE} just a headline on Trump and Epstein"),
    DocCfg(id='015028', description=f"{PALM_BEACH_POST_ARTICLE} reopening Epstein's criminal case"),
    DocCfg(id='022990', description=f"{PALM_BEACH_POST_ARTICLE} Trump and Epstein"),
    DocCfg(id='016996', description=f'SciencExpress article "Quantitative Analysis of Culture Using Millions of Digitized Books" by Jean-Baptiste Michel'),
    DocCfg(id='030030', description=SHIMON_POST_ARTICLE, date='2011-03-29'),
    DocCfg(id='025610', description=SHIMON_POST_ARTICLE, date='2011-04-03'),
    DocCfg(id='023458', description=SHIMON_POST_ARTICLE, date='2011-04-17'),
    DocCfg(id='023487', description=SHIMON_POST_ARTICLE, date='2011-04-18'),
    DocCfg(id='030531', description=SHIMON_POST_ARTICLE, date='2011-05-16'),
    DocCfg(id='024958', description=SHIMON_POST_ARTICLE, date='2011-05-08'),
    DocCfg(id='030060', description=SHIMON_POST_ARTICLE, date='2011-05-13'),
    DocCfg(id='031834', description=SHIMON_POST_ARTICLE, date='2011-05-16'),
    DocCfg(id='023517', description=SHIMON_POST_ARTICLE, date='2011-05-26'),
    DocCfg(id='030268', description=SHIMON_POST_ARTICLE, date='2011-05-29'),
    DocCfg(id='029628', description=SHIMON_POST_ARTICLE, date='2011-06-04'),
    DocCfg(id='018085', description=SHIMON_POST_ARTICLE, date='2011-06-07'),
    DocCfg(id='030156', description=SHIMON_POST_ARTICLE, date='2011-06-22'),
    DocCfg(id='031876', description=SHIMON_POST_ARTICLE, date='2011-06-14'),
    DocCfg(id='032171', description=SHIMON_POST_ARTICLE, date='2011-06-26'),
    DocCfg(id='029932', description=SHIMON_POST_ARTICLE, date='2011-07-03'),
    DocCfg(id='031913', description=SHIMON_POST_ARTICLE, date='2011-08-24'),
    DocCfg(id='024592', description=SHIMON_POST_ARTICLE, date='2011-08-25'),
    DocCfg(id='024997', description=SHIMON_POST_ARTICLE, date='2011-09-08'),
    DocCfg(id='031941', description=SHIMON_POST_ARTICLE, date='2011-11-17'),
    DocCfg(id='021092', description=f'{SINGLE_PAGE} Tatler article about {GHISLAINE_MAXWELL} shredding documents', date='2019-08-15'),
    DocCfg(id='031191', description=f"{SINGLE_PAGE} unknown article about Epstein and Trump's relationship in 1997"),
    DocCfg(id='030829', description=f'South Florida Sun Sentinel article about {BRAD_EDWARDS} and {JEFFREY_EPSTEIN}'),
    DocCfg(id='026520', description=f'Spanish language article about {SULTAN_BIN_SULAYEM}', date='2013-09-27'),
    DocCfg(id='030333', description=f'The Independent article about Prince Andrew, Epstein, and Epstein\'s butler who stole his address book'),
    DocCfg(
        id='031736',
        description=f"{TRANSLATION} Arabic article by Abdulnaser Salamah 'Trump; Prince of Believers (Caliph)!'",
        date='2017-05-13',
    ),
    DocCfg(id='025094', description=f'{TRANSLATION} Spanish article about Cuba', date='2015-11-08'),
    DocCfg(id='010754', description=f"U.S. News article about Yitzhak Rabin"),
    DocCfg(id='031794', description=f"very short French magazine clipping"),
    DocCfg(id='014498', description=VI_DAILY_NEWS_ARTICLE, date='2016-12-13'),
    DocCfg(id='031171', description=VI_DAILY_NEWS_ARTICLE, date='2019-02-06'),
    DocCfg(id='023048', description=VI_DAILY_NEWS_ARTICLE, date='2019-02-27'),
    DocCfg(id='023046', description=VI_DAILY_NEWS_ARTICLE, date='2019-02-27'),
    DocCfg(id='031170', description=VI_DAILY_NEWS_ARTICLE, date='2019-03-06'),
    DocCfg(id='016506', description=VI_DAILY_NEWS_ARTICLE, date='2019-02-28'),
    DocCfg(id='016507', description=f"{VI_DAILY_NEWS_ARTICLE} 'Perversion of Justice' by {JULIE_K_BROWN}", date='2018-12-19'),
    DocCfg(id='019212', description=f'{WAPO} and Times Tribune articles about Bannon, Trump, and healthcare execs'),
]

OTHER_FILES_COURT_DOCS = [
    DocCfg(id='025353', author=KEN_STARR, description=KEN_STARR_LETTER, date='2008-05-19', duplicate_ids=['010723', '019224'], dupe_type='redacted'),
    DocCfg(id='025704', author=KEN_STARR, description=KEN_STARR_LETTER, date='2008-05-27', duplicate_ids=['010732', '019221'], dupe_type='redacted'),
    DocCfg(id='012130', author=KEN_STARR, description=KEN_STARR_LETTER, date='2008-06-19', duplicate_ids=['012135']),
    DocCfg(id='011908', description=f"{BRUNEL_V_EPSTEIN} and Tyler McDonald d/b/a YI.org court filing"),
    DocCfg(id='017603', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, date='2019-02-28'),
    DocCfg(id='017635', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, date='2019-02-28'),
    DocCfg(id='016509', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, date='2019-02-28'),
    DocCfg(id='017714', description=DAVID_SCHOEN_CVRA_LEXIS_SEARCH, date='2019-02-28'),
    DocCfg(id='021824', description=f"{EDWARDS_V_DERSHOWITZ} deposition of {PAUL_G_CASSELL}"),
    DocCfg(
        id='010757',
        description=f"{EDWARDS_V_DERSHOWITZ} plaintiff response to Dershowitz Motion to Determine Confidentiality of Court Records",
        date='2015-11-23',
    ),
    DocCfg(
        id='010887',
        description=f"{EDWARDS_V_DERSHOWITZ} Dershowitz Motion for Clarification of Confidentiality Order",
        date='2016-01-29',
    ),
    DocCfg(
        id='015590',
        description=f"{EDWARDS_V_DERSHOWITZ} Dershowitz Redacted Motion to Modify Confidentiality Order",
        date='2016-02-03',
    ),
    DocCfg(
        id='015650',
        description=f"{EDWARDS_V_DERSHOWITZ} Giuffre Response to Dershowitz Motion for Clarification of Confidentiality Order",
        date='2016-02-08',
    ),
    DocCfg(id='010566', description=f"{EPSTEIN_V_ROTHSTEIN_EDWARDS} Statement of Undisputed Facts", date='2010-11-04'),
    DocCfg(id='012707', description=f"{EPSTEIN_V_ROTHSTEIN_EDWARDS} Master Contact List - Privilege Log", date='2011-03-22'),
    DocCfg(id='012103', description=f"{EPSTEIN_V_ROTHSTEIN_EDWARDS} Telephone Interview with {VIRGINIA_GIUFFRE}", date='2011-05-17'),
    DocCfg(id='017488', description=f"{EPSTEIN_V_ROTHSTEIN_EDWARDS} Deposition of Scott Rothstein", date='2012-06-22'),
    DocCfg(id='029315', description=f"{EPSTEIN_V_ROTHSTEIN_EDWARDS} Plaintiff Motion for Summary Judgment by {JACK_SCAROLA}", date='2013-09-13'),
    DocCfg(id='013304', description=f"{EPSTEIN_V_ROTHSTEIN_EDWARDS} Plaintiff Response to Epstein's Motion for Summary Judgment", date='2014-04-17'),
    DocCfg(id='019352', description=FBI_REPORT,),
    DocCfg(id='021434', description=FBI_REPORT,),
    DocCfg(id='018872', description=FBI_SEIZED_PROPERTY,),
    DocCfg(id='021569', description=FBI_SEIZED_PROPERTY,),
    DocCfg(id='017792', description=f"{GIUFFRE_V_DERSHOWITZ} article about {ALAN_DERSHOWITZ}'s appearance on Wolf Blitzer"),
    DocCfg(id='017767', description=f"{GIUFFRE_V_DERSHOWITZ} article about {ALAN_DERSHOWITZ} working with {JEFFREY_EPSTEIN}"),
    DocCfg(id='017796', description=f"{GIUFFRE_V_DERSHOWITZ} article about {ALAN_DERSHOWITZ}"),
    DocCfg(id='017935', description=f"{GIUFFRE_V_DERSHOWITZ} defamation complaint", date='2019-04-16'),
    DocCfg(id='017824', description=f"{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} article by {JULIE_K_BROWN}"),
    DocCfg(
        id='017818',
        description=f"{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} article about accusations against {ALAN_DERSHOWITZ} by {JULIE_K_BROWN}",
        date='2018-12-27',
    ),
    DocCfg(id='017800', description=f'{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} "Perversion of Justice" by {JULIE_K_BROWN}'),
    DocCfg(id='022237', description=f"{GIUFFRE_V_DERSHOWITZ} partial court filing with fact checking questions?"),
    DocCfg(id='016197', description=f"{GIUFFRE_V_DERSHOWITZ} response to Florida Bar complaint by {ALAN_DERSHOWITZ} about David Boies from {PAUL_G_CASSELL}"),
    DocCfg(id='017771', description=f'{GIUFFRE_V_DERSHOWITZ} Vanity Fair article "The Talented Mr. Epstein" by Vicky Ward', date='2011-06-27'),
    DocCfg(id='014118', description=f"{GIUFFRE_V_EPSTEIN} Declaration in Support of Motion to Compel Production of Documents", date='2016-10-21'),
    DocCfg(id='014652', description=f"{GIUFFRE_V_MAXWELL} Complaint", date='2015-04-22'),
    DocCfg(id='015529', description=f"{GIUFFRE_V_MAXWELL} Defamation Complaint", date='2015-09-21'),
    DocCfg(id='014797', description=f"{GIUFFRE_V_MAXWELL} Declaration of Laura A. Menninger in Opposition to Plaintiff's Motion", date='2017-03-17'),
    DocCfg(id='011304', description=f"{GIUFFRE_V_MAXWELL} Oral Argument Transcript", date='2017-03-17'),
    DocCfg(
        id='014788',
        description=f"{GIUFFRE_V_MAXWELL} Maxwell Response to Plaintiff's Omnibus Motion in Limine",
        date='2017-03-17',
        duplicate_ids=['011463'],
    ),
    DocCfg(
        id='019297',
        description=f'{GIUFFRE_V_MAXWELL} letter from {ALAN_DERSHOWITZ} lawyer Andrew G. Celli',
        date='2018-02-07'
    ),
    DocCfg(
        id='025937',
        description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of Tiffany Doe describing Jane Doe being raped by Epstein and Trump',
        date='2016-06-20',
    ),
    DocCfg(id='025939', description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of Jane Doe describing being raped by Epstein', date='2016-06-20'),
    DocCfg(id='013489', description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of {BRAD_EDWARDS}', date='2010-07-20'),
    DocCfg(id='029398', description=f'{JANE_DOE_V_EPSTEIN_TRUMP} article in Law.com'),
    DocCfg(id='026854', description=f"{JANE_DOE_V_EPSTEIN_TRUMP} Civil Docket"),
    DocCfg(id='026384', description=f"{JANE_DOE_V_EPSTEIN_TRUMP} Complaint for rape and sexual abuse", date='2016-06-20'),
    DocCfg(id='013463', description=f'{JANE_DOE_V_EPSTEIN_TRUMP} Deposition of Scott Rothstein', date='2010-03-23'),
    DocCfg(id='029257', description=f'{JANE_DOE_V_EPSTEIN_TRUMP} allegations and identity of plaintiff Katie Johnson', date='2016-04-26'),
    DocCfg(id='032321', description=f"{JANE_DOE_V_EPSTEIN_TRUMP} Notice of Initial Conference", date='2016-10-04'),
    DocCfg(id='010735', description=f"{JANE_DOE_V_USA} Dershowitz Reply in Support of Motion for Limited Intervention", date='2015-02-02'),
    DocCfg(id='014084', description=f"{JANE_DOE_V_USA} Jane Doe Response to Dershowitz's Motion for Limited Intervention", date='2015-03-24'),
    DocCfg(id='023361', description=f"{JASTA_SAUDI_LAWSUIT} legal text and court documents", date='2012-01-20'),
    DocCfg(id='017830', description=f"{JASTA_SAUDI_LAWSUIT} legal text and court documents"),
    DocCfg(id='017904', description=f"{JASTA_SAUDI_LAWSUIT} Westlaw search results", date='2019-01-01'),
    DocCfg(id='014037', description=f"Journal of Criminal Law and Criminology article on {CVRA}"),
    DocCfg(id='020662', description=f"letter from {ALAN_DERSHOWITZ}'s British lawyers Mishcon de Reya to Daily Mail threatening libel suit"),
    DocCfg(
        id='010560',
        description=f"letter from Gloria Allred to {SCOTT_J_LINK} alleging abuse of a girl from Kansas",
        date='2019-06-19',
    ),
    DocCfg(
        id='031447',
        description=f"letter from {MARTIN_WEINBERG} to Melanie Ann Pustay and Sean O'Neill re: an Epstein FOIA request"
    ),
    DocCfg(
        id='028965',
        description=f"letter from {MARTIN_WEINBERG} to ABC / Good Morning America threatening libel lawsuit",
        duplicate_ids=['028928']
    ),
    DocCfg(
        id='026793',
        description=f"letter from {STEVEN_HOFFENBERG}'s lawyers at Mintz Fraade offering to take over Epstein's business and resolve his legal issues",
        date='2018-03-23',
    ),
    DocCfg(
        id='016420',
        description=f"{NEW_YORK_V_EPSTEIN} New York Post Motion to Unseal Appellate Briefs",
        date='2019-01-11',
    ),
    DocCfg(id='028540', description=f"SCOTUS decision in Budha Ismail Jam et al. v. INTERNATIONAL FINANCE CORP"),
    DocCfg(id='012197', description=f"SDFL Response to {JAY_LEFKOWITZ} on Epstein Plea Agreement Compliance"),
    DocCfg(id='022277', description=f"{TEXT_OF_US_LAW} National Labour Relations Board (NLRB)"),
]

OTHER_FILES_CONFERENCES = [
    DocCfg(id='030769', description=f"2017 Independent Filmmaker Project (IFP) Gotham Awards invitation"),
    DocCfg(id='014951', description=f"2017 TED Talks program", date='2017-04-20'),
    DocCfg(id='014315', description=f'{BOFA_MERRILL} 2016 Future of Financials Conference'),
    DocCfg(id='026825', description=f"{DEUTSCHE_BANK} Asset & Wealth Management featured speaker bios"),  # Really "Deutsche Asset" which may not be Deutsche Bank?
    DocCfg(id='017526', description=f'Intellectual Jazz conference brochure f. {DAVID_BLAINE}'),
    DocCfg(id='023120', description=f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more (old draft)"),
    DocCfg(id='023123', description=f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more", duplicate_ids=['023121'], dupe_type='earlier'),
    DocCfg(id='031359', description=f"{NOBEL_CHARITABLE_TRUST} Earth Environment Convention about ESG investing"),
    DocCfg(id='031354', description=f'{NOBEL_CHARITABLE_TRUST} "Thinking About the Environment and Technology" report 2011'),
    DocCfg(id='024179', description=f'president and first lady schedule at 67th U.N. General Assembly', date='2012-09-21'),
    DocCfg(id='029427', description=f"seems related to an IRL meeting about concerns China will attempt to absorb Mongolia"),
    DocCfg(
        id='024185',
        description=f'schedule of 67th U.N. General Assembly w/"Presidents Private Dinner - Jeffrey Epstine (sic)"',
        date='2012-09-21',
    ),
    DocCfg(id='025797', description=f'someone\'s notes from Aspen Strategy Group', date='2013-05-29'),
    DocCfg(id='017524', description=f"{SWEDISH_LIFE_SCIENCES_SUMMIT} 2012 program"),
    DocCfg(id='026747', description=f"{SWEDISH_LIFE_SCIENCES_SUMMIT} 2017 program", date='2017-08-23'),
    DocCfg(id='019300', description=f'{WOMEN_EMPOWERMENT} f. {KATHRYN_RUEMMLER}', date='2019-04-05'),
    DocCfg(id='022267', description=f'{WOMEN_EMPOWERMENT} founder essay about growing the seminar business'),
    DocCfg(id='022407', description=f'{WOMEN_EMPOWERMENT} seminar pitch deck'),
    DocCfg(
        id='017060',
        description=f'World Economic Forum (WEF) Annual Meeting 2011 List of Participants',
        date='2011-01-18',
    ),
]

OTHER_FILES_REPORTS = [
    DocCfg(id='024631', description=f"Ackrell Capital Cannabis Investment Report 2018"),
    DocCfg(id='016111', description=f"{BOFA_MERRILL} 'GEMs Paper #26 Saudi Arabia: beyond oil but not so fast'", date='2016-06-30'),
    DocCfg(id='010609', description=f"{BOFA_MERRILL} 'Liquid Insight Trump\'s effect on MXN'", date='2016-09-22'),
    DocCfg(id='025978', description=f"{BOFA_MERRILL} 'Understanding when risk parity risk Increases'", date='2016-08-09'),
    DocCfg(id='014404', description=f'{BOFA_MERRILL} Japan Investment Strategy Report', date='2016-11-18'),
    DocCfg(id='014410', description=f'{BOFA_MERRILL} Japan Investment Strategy Report', date='2016-11-18'),
    DocCfg(id='014424', description=f"{BOFA_MERRILL} 'Japan Macro Watch'", date='2016-11-14'),
    DocCfg(id='014731', description=f"{BOFA_MERRILL} 'Global Rates, FX & EM 2017 Year Ahead'", date='2016-11-16'),
    DocCfg(id='014432', description=f"{BOFA_MERRILL} 'Global Cross Asset Strategy - Year Ahead The Trump inflection'", date='2016-11-30'),
    DocCfg(id='014460', description=f"{BOFA_MERRILL} 'European Equity Strategy 2017'", date='2016-12-01'),
    DocCfg(id='014972', description=f"{BOFA_MERRILL} 'Global Equity Volatility Insights'", date='2017-06-20'),
    DocCfg(id='014622', description=f"{BOFA_MERRILL} 'Top 10 US Ideas Quarterly'", date='2017-01-03'),
    DocCfg(id='023069', description=f"{BOFA_MERRILL} 'Equity Strategy Focus Point Death and Taxes'", date='2017-01-29'),
    DocCfg(id='014721', description=f"{BOFA_MERRILL} 'Cause and Effect Fade the Trump Risk Premium'", date='2017-02-13'),
    DocCfg(id='014887', description=f"{BOFA_MERRILL} 'Internet / e-Commerce'", date='2017-04-06'),
    DocCfg(id='014873', description=f"{BOFA_MERRILL} 'Hess Corp'", date='2017-04-11'),
    DocCfg(id='023575', description=f"{BOFA_MERRILL} 'Global Equity Volatility Insights'", date='2017-06-01'),
    DocCfg(id='014518', description=f'{BOFA_WEALTH_MGMT} tax alert', date='2016-05-02'),
    DocCfg(id='029438', description=f'{BOFA_WEALTH_MGMT} tax report', date='2018-01-02'),
    DocCfg(id='024271', description=f"Blockchain Capital and Brock Pierce pitch deck", date='2015-10-01'),
    DocCfg(id='024302', description=f"Carvana form 14A SEC filing proxy statement", date='2019-04-23'),
    DocCfg(id='029305', description=f"CCH Tax Briefing on end of Defense of Marriage Act", date='2013-06-27'),
    DocCfg(id='024817', description=f"Cowen's Collective View of CBD / Cannabis report"),
    DocCfg(id='026794', description=f"{DEUTSCHE_BANK} Global Public Affairs report: 'Global Political and Regulatory Risk in 2015/2016'"),
    DocCfg(id='022361', description=DEUTSCHE_BANK_TAX_TOPICS, date='2013-05-01'),
    DocCfg(id='022325', description=DEUTSCHE_BANK_TAX_TOPICS, date='2013-12-20'),
    DocCfg(id='022330', description=f'{DEUTSCHE_BANK_TAX_TOPICS} table of contents', date='2013-12-20'),
    DocCfg(id='019440', description=DEUTSCHE_BANK_TAX_TOPICS, date='2014-01-29'),
    DocCfg(id='024202', description=f"Electron Capital Partners LLC 'Global Utility White Paper'", date='2013-03-08'),
    DocCfg(id='022372', description=f'Ernst & Young 2016 election report'),
    DocCfg(
        id='025663',
        description=f"{GOLDMAN_REPORT} 'An Overview of the Current State of Cryptocurrencies and Blockchain'",
        date='2017-11-15',
    ),
    DocCfg(id='014532', description=f"{GOLDMAN_REPORT} 'Outlook - Half Full'", date='2017-01-01'),
    DocCfg(id='026909', description=f"{GOLDMAN_REPORT} 'The Unsteady Undertow Commands the Seas (Temporarily)'", date='2018-10-14'),
    DocCfg(id='026944', description=f"{GOLDMAN_REPORT} 'Risk of a US-Iran Military Conflict'", date='2019-05-23'),
    DocCfg(id='026679', description=f"Invesco report: 'Global Sovereign Asset Management Study 2017'"),
    DocCfg(id='023096', description=f'{EPSTEIN_FOUNDATION} blog', date='2012-11-15'),
    DocCfg(id='029326', description=f'{EPSTEIN_FOUNDATION} {PRESS_RELEASE}', date='2013-02-15'),
    DocCfg(id='026565', description=f'{EPSTEIN_FOUNDATION} {PRESS_RELEASE}, maybe a draft of 029326', date='2013-02-15'),
    DocCfg(id='026572', description=f"{JP_MORGAN} Global Asset Allocation report", date='2012-11-09'),
    DocCfg(id='030848', description=f"{JP_MORGAN} Global Asset Allocation report", date='2013-03-28'),
    DocCfg(id='030840', description=f"{JP_MORGAN} Market Thoughts"),
    DocCfg(id='022350', description=f"{JP_MORGAN} report on tax efficiency of Intentionally Defective Grantor Trusts (IDGT)"),
    DocCfg(id='025242', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-04-09'),
    DocCfg(id='030010', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-06-14'),
    DocCfg(id='030808', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-07-11'),
    DocCfg(id='025221', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-07-25'),
    DocCfg(id='025229', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-08-04'),
    DocCfg(id='030814', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-11-21'),
    DocCfg(id='024132', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-03-15'),
    DocCfg(id='024194', description=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-10-22'),
    DocCfg(id='025296', description=f'Laffer Associates report predicting Trump win', date='2016-07-06'),
    DocCfg(id='025551', description=f'Morgan Stanley report about alternative asset managers', date='2018-01-30'),
    DocCfg(id='026759', description=f'{PRESS_RELEASE} by Ritz-Carlton club about damage from Hurricane Irma', date='2017-09-13'),
    DocCfg(id='012048', description=f"{PRESS_RELEASE} 'Rockefeller Partners with Gregory J. Fleming to Create Independent Financial Services Firm' and other articles"),
    DocCfg(id='020447', description=f'Promoting Constructive Vigilance: Report of the Working Group on Chinese Influence Activities in the U.S. (Hoover Group/Stanford 2018)'),
    DocCfg(id='025763', description=f"S&P Economic Research: 'How Increasing Income Inequality Is Dampening U.S. Growth'", date='2014-08-05'),
    DocCfg(id='019856', description=f"Sadis Goldberg LLP report on SCOTUS ruling about insider trading"),
    DocCfg(id='026827', description=f'Scowcroft Group report on ISIS', date='2015-11-14'),
    DocCfg(id='033220', description=f"short economic report on defense spending under Trump by Joseph G. Carson"),
    DocCfg(id='026856', author='Kevin Rudd', description=f"speech 'Xi Jinping, China And The Global Order'", date='2018-06-26'),
    DocCfg(id='024135', author=UBS, description=UBS_CIO_REPORT, date='2012-06-29'),
    DocCfg(id='025247', author=UBS, description=UBS_CIO_REPORT, date='2012-10-25'),
    DocCfg(id='025849', description=f"US Office of Government Information Services report: 'Building a Bridge Between FOIA Requesters & Agencies'"),
    DocCfg(id='020824', description=f"USA Inc: A Basic Summary of America's Financial Statements compiled by Mary Meeker", date='2011-02-01'),
]

OTHER_FILES_LETTERS = [
    DocCfg(id='017789', author=ALAN_DERSHOWITZ, description=f'letter to {HARVARD} Crimson complaining he was defamed'),
    DocCfg(
        id='019086',
        author=DAVID_BLAINE,
        description=f"{DAVID_BLAINE_VISA_LETTER} from Russia 'Svet' ({SVETLANA_POZHIDAEVA}?), names Putin puppet regimes",
        date='2015-05-27',  # Date is a guess based on other drafts,
    ),
    DocCfg(
        id='019474',
        author=DAVID_BLAINE,
        description=f"{DAVID_BLAINE_VISA_LETTER} from Russia 'Svetlana' ({SVETLANA_POZHIDAEVA}?)",
        date='2015-05-29',
    ),
    DocCfg(
        id='019476',
        author=DAVID_BLAINE,
        description=f"{DAVID_BLAINE_VISA_LETTER} (probably {SVETLANA_POZHIDAEVA}?)",
        date='2015-06-01',
    ),
    DocCfg(id='031670', description=f"letter from General Mike Flynn's lawyers to senators Mark Warner & Richard Burr about subpoena"),
    DocCfg(
        id='026011',
        author='Gennady Mashtalyar',
        description=f"letter about algorithmic trading",
        date='2016-06-24',  # date is based on Brexit reference but he could be backtesting,
    ),
    DocCfg(id='026248', author='Don McGahn', description=f'letter from Trump lawyer to Devin Nunes (R-CA) about FISA courts and Trump'),
    DocCfg(id='029301', author=MICHAEL_J_BOCCIO, description=f"letter from former lawyer at the Trump Organization", date='2011-08-07'),
    DocCfg(id='022405', author=NOAM_CHOMSKY, description=f"letter attesting to Epstein's good character"),
    DocCfg(id='026134', description=f'letter to someone named George about investment opportunities in the Ukraine banking sector'),
    DocCfg(id='029304', description=f"Trump recommendation letter for recently departed Trump Organization lawyer {MICHAEL_J_BOCCIO}"),
    DocCfg(id='026668', description=f"Boothbay Fund Management 2016-Q4 earnings report signed by Ari Glass"),
]

# private placement memoranda
OTHER_FILES_PRIVATE_PLACEMENT_MEMOS =[
    DocCfg(id='024432', description=f"Michael Milken's Knowledge Universe Education (KUE) $1,000,000 corporate share placement notice (SEC filing?)"),
    DocCfg(id='024003', description=f"New Leaf Ventures private placement memorandum"),
    DocCfg(id='018804', description=f"appraisal of going concern for IGY American Yacht Harbor Marina in {VIRGIN_ISLANDS}"),
]

OTHER_FILES_PROPERTY = [
    DocCfg(id='018743', description=f"Las Vegas property listing"),
    DocCfg(id='016597', description=f'letter from Trump Properties LLC appealing some decision about Mar-a-Lago by {PALM_BEACH} authorities'),
    DocCfg(id='016602', description=PALM_BEACH_CODE_ENFORCEMENT, date='2008-04-17'),
    DocCfg(id='016554', description=PALM_BEACH_CODE_ENFORCEMENT, date='2008-07-17', duplicate_ids=['016616', '016574']),
    DocCfg(id='016695', description=f"{PALM_BEACH} property info (?)"),
    DocCfg(id='016697', description=f"{PALM_BEACH} property tax info (?) that mentions Trump"),
    DocCfg(id='016599', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016600', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016601', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016694', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016552', description=f"{PALM_BEACH_TSV} info"),
    DocCfg(id='016698', description=f"{PALM_BEACH_TSV} info (broken?)"),
    DocCfg(id='016696', description=f"{PALM_BEACH_TSV} info (water quality?"),
    DocCfg(id='016636', description=f"{PALM_BEACH_WATER_COMMITTEE} Meeting on January 29, 2009"),
    DocCfg(id='022417', description=f"Park Partners NYC letter to partners in real estate project with architectural plans"),
    DocCfg(id='027068', author=THE_REAL_DEAL, description=THE_REAL_DEAL_ARTICLE),
    DocCfg(id='029520', author=THE_REAL_DEAL, description=f"{THE_REAL_DEAL_ARTICLE} 'Lost Paradise at the Palm House'", date='2019-06-17'),
    DocCfg(
        id='018727',
        description=f"{VIRGIN_ISLANDS} property deal pitch deck, building will be leased to the U.S. govt GSA",
        date='2014-06-01',
    ),
]

OTHER_FILES_REPUTATION_MGMT = [
    DocCfg(id='026582', description=f"{REPUTATION_MGMT} Epstein's internet search results at start of reputation repair campaign, maybe from {OSBORNE_LLP}"),
    DocCfg(id='030573', description=f"{REPUTATION_MGMT} Epstein's unflattering Google search results, maybe screenshot by {AL_SECKEL} or {OSBORNE_LLP}"),
    DocCfg(id='030875', description=f"{REPUTATION_MGMT} Epstein's Wikipedia page"),
    DocCfg(id='026583', description=f"{REPUTATION_MGMT} Google search results for '{JEFFREY_EPSTEIN}' with analysis ({OSBORNE_LLP}?)"),
    DocCfg(id='029350', description=f"{REPUTATION_MGMT} Microsoft Bing search results for Epstein with sex offender at top, maybe from {TYLER_SHEARS}?"),
    DocCfg(
        id='030426',
        description=f'{REPUTATION_MGMT} {OSBORNE_LLP} reputation repair proposal (cites Michael Milken)',
        date='2011-06-14',
    ),
]

OTHER_FILES_SOCIAL_MEDIA = [    # social media / InsightsPod
    DocCfg(id='028815', author=ZUBAIR_AND_ANYA, description=f"{INSIGHTS_POD} business plan", date='2016-08-20'),
    DocCfg(id='011170', author=ZUBAIR_AND_ANYA, description=f'{INSIGHTS_POD} collected tweets about #Brexit', date='2016-06-23'),
    DocCfg(id='032324', author=ZUBAIR_AND_ANYA, description=f"{INSIGHTS_POD} election social media trend analysis", date='2016-11-05'),
    DocCfg(id='032281', author=ZUBAIR_AND_ANYA, description=f"{INSIGHTS_POD} forecasting election for Trump", date='2016-10-25'),
    DocCfg(id='028988', author=ZUBAIR_AND_ANYA, description=f"{INSIGHTS_POD} pitch deck", date='2016-08-20'),
    DocCfg(id='026627', author=ZUBAIR_AND_ANYA, description=f"{INSIGHTS_POD} report on the presidential debate"),
    DocCfg(id='023050', description=f"{DERSH_GIUFFRE_TWEET}"),
    DocCfg(id='017787', description=f"{DERSH_GIUFFRE_TWEET}"),
    DocCfg(id='033433', description=f"{DERSH_GIUFFRE_TWEET} / David Boies", date='2019-03-02'),
    DocCfg(id='033432', description=f"{DERSH_GIUFFRE_TWEET} / David Boies", date='2019-05-02'),
    DocCfg(id='022213', description=f"{SCREENSHOT} Facebook group called 'Shit Pilots Say' disparaging a 'global girl'"),
    DocCfg(id='030884', description=f"{TWEET} by Ed Krassenstein"),
    DocCfg(id='031546', description=f"{TWEET}s by Donald Trump about Russian collusion", date='2018-01-06'),
    DocCfg(id='033236', description=f'{TWEET}s about Ivanka Trump in Arabic', date='2017-05-20'),
]

OTHER_FILES_POLITICS = [
    DocCfg(id='029918', description=f"{DIANA_DEGETTES_CAMPAIGN} campaign bio", date='2012-01-01'),
    DocCfg(id='031184', description=f"{DIANA_DEGETTES_CAMPAIGN} fundraiser invitation"),
    DocCfg(id='027009', description=f"{EHUD_BARAK} speech to AIPAC", date='2013-03-03'),
    DocCfg(id='026851', description=f"Politifact lying politicians chart", date='2016-07-26'),
    DocCfg(
        id='023133',
        description=f'"The Search for Peace in the Arab-Israeli Conflict" edited by {TERJE_ROD_LARSEN}, Nur Laiq, Fabrice Aidan',
        date='2019-12-09',
    ),
    DocCfg(id='024294', description=f"{STACEY_PLASKETT} campaign flier", date='2016-10-01'),
    DocCfg(
        id='029357',
        description=f"text about Israel's challenges going into 2015, feels like it was extracted from a book",
        date='2015-01-15',  # TODO: this is just a guess
        duplicate_ids=['028887'],
    ),
    DocCfg(id='010617', description=TRUMP_DISCLOSURES, date='2017-01-20'),
    DocCfg(id='016699', description=TRUMP_DISCLOSURES, date='2017-01-20'),
]

OTHER_FILES_ACADEMIA = [
    DocCfg(id='024256', author=JOI_ITO, description=f"article 'Internet & Society: The Technologies and Politics of Control'"),
    DocCfg(id='027004', author=JOSCHA_BACH, description=f"article 'The Computational Structure of Mental Representation'", date='2013-02-26'),
    DocCfg(id='029539', author=LA_TIMES, description=f"Alan Trounson interview on California stem cell research and CIRM"),
    DocCfg(id='027024', author=LA_TIMES, description=f"'Scientists Create Human Embryos to Make Stem Cells'", date='2013-05-15'),
    DocCfg(id='026634', author='Michael Carrier', description=f"comments about an Apollo linked hedge fund 'DE Fund VIII'"),
    DocCfg(id='015501', author=f"{MOSHE_HOFFMAN}, Erez Yoeli, and Carlos David Navarrete", description=f"'Game Theory and Morality'"),
    DocCfg(id='025143', author=ROBERT_TRIVERS, description=f"'Africa, Parasites, Intelligence'", date='2018-06-25'),
    DocCfg(id='029155', author=ROBERT_TRIVERS, description=f'response sent to the Gruterites ({GORDON_GETTY} fans)', date='2018-03-19'),
    DocCfg(
        id='033323',
        author=f"{ROBERT_TRIVERS} and Nathan H. Lents",
        description=f"draft of 'Does Trump Fit the Evolutionary Role of Narcissistic Sociopath?",
        date='2018-12-07',
    ),
    DocCfg(id='014697', description=CHALLENGES_OF_AI, duplicate_ids=['011284']),
    DocCfg(id='026521', description=f"game theory paper by {MARTIN_NOWAK}, Erez Yoeli, and Moshe Hoffman"),
    DocCfg(id='023416', description=HARVARD_POETRY),
    DocCfg(id='023435', description=HARVARD_POETRY),
    DocCfg(id='023450', description=HARVARD_POETRY),
    DocCfg(id='023452', description=HARVARD_POETRY),
    DocCfg(id='029517', description=HARVARD_POETRY),
    DocCfg(id='029543', description=HARVARD_POETRY),
    DocCfg(id='029589', description=HARVARD_POETRY),
    DocCfg(id='029603', description=HARVARD_POETRY),
    DocCfg(id='029298', description=HARVARD_POETRY),
    DocCfg(id='029592', description=HARVARD_POETRY),
    DocCfg(id='019396', description=f'{HARVARD} Economics 1545 Professor Kenneth Rogoff syllabus'),
    DocCfg(id='022445', description=f"Inference: International Review of Science Feedback & Comments", date='2018-11-01'),
    DocCfg(id='029355', description=f'{SCREENSHOT} quote in book about {LARRY_SUMMERS}', duplicate_ids=['029356'], dupe_type='quoted'),  # 029356 is zoomed in corner
    DocCfg(id='026731', description=f"text of speech by Lord Martin Rees at first inaugural Carl Sagan Lecture at Cornell"),
]

# resumes and application letters
OTHER_FILES_RESUMES = [
    DocCfg(id='029102', description=HBS_APPLICATION_NERIO),
    DocCfg(id='029104', description=HBS_APPLICATION_NERIO),
    DocCfg(id='022367', description=f"{RESUME_OF} Jack J Grynberg", date='2014-07-01'),
    DocCfg(
        id='029302',
        description=f"{RESUME_OF} {MICHAEL_J_BOCCIO}, former lawyer at the Trump Organization",
        date='2011-08-07',
    ),
    DocCfg(id='015671', description=f"{RESUME_OF} Robin Solomon", date='2015-06-02'),  # She left Mount Sinai at some point in 2015,
    DocCfg(id='015672', description=f"{RESUME_OF} Robin Solomon", date='2015-06-02'),  # She left Mount Sinai at some point in 2015,
    DocCfg(id='029623', description=f'short bio of Kathleen Harrington, Founding Partner, C/H Global Strategies'),
]

OTHER_FILES_ARTS = [
    DocCfg(id='018703', author=ANDRES_SERRANO, description=f"artist statement about Trump objects"),
    DocCfg(id='028281', description=f'art show flier for "The House Of The Nobleman" curated by Wolfe Von Lenkiewicz & Victoria Golembiovskaya'),
    DocCfg(
        id='025205',
        description=f'Mercury Films partner profiles of Jennifer Baichwal, Nicholas de Pencier, Kermit Blackwood, Travis Rummel',
        date='2010-02-01',
        duplicate_ids=['025210']
    ),
]

OTHER_FILES_MISC = [
    DocCfg(id='031743', description=f'a few pages describing the internet as a "New Nation State" (Network State?)'),
    DocCfg(id='023438', description=f"Brockman announcemeent of auction of 'Noise' by Daniel Kahneman, Olivier Sibony, and Cass Sunstein"),
    DocCfg(
        id='025147',
        description=f'Brockman hot list Frankfurt Book Fair (includes article about Silk Road/Ross Ulbricht)',
        date='2016-10-23',
    ),
    DocCfg(id='031425', description=f'completely redacted email from {SCOTT_J_LINK}'),
    DocCfg(id='018224', description=f"conversation with {LAWRENCE_KRAUSS}?"),
    DocCfg(id='012718', description=f"{CVRA} congressional record", date='2011-06-17'),
    DocCfg(id='025540', description=f"Epstein's rough draft of his side of the story?"),
    DocCfg(id='024117', description=f"FAQ about anti-money laundering (AML) and terrorist financing (CFT) laws in the U.S."),
    DocCfg(id='027071', description=f"{FEMALE_HEALTH_COMPANY} brochure request donations for female condoms in Uganda"),
    DocCfg(id='027074', description=f"{FEMALE_HEALTH_COMPANY} pitch deck (USAID was a customer)"),
    DocCfg(id='022780', description=FLIGHT_LOGS,),
    DocCfg(id='022816', description=FLIGHT_LOGS,),
    DocCfg(id='022494', description=f'Foreign Corrupt Practices Act (FCPA) DOJ Resource Guide'),
    DocCfg(id='032735', description=f"{GORDON_GETTY} on Trump", date='2018-03-20'),  # Dated based on concurrent emails from Getty
    DocCfg(
        id='030142',
        description=f"{JASTA} (Justice Against Sponsors of Terrorism Act) doc that's mostly empty, references suit against Saudi f. {KATHRYN_RUEMMLER} & {KEN_STARR}",
        date='2016-09-01',
    ),
    DocCfg(id='019448', description=f"Haitian business investment proposal called Jacmel"),
    DocCfg(
        id='033338',
        description=f"{PRESS_RELEASE} announcing Donald Trump & {NICHOLAS_RIBIS} ended their working relationship at Trump's casino",
        date='2000-06-07',
    ),
    DocCfg(id='029328', description=f"Rafanelli Events promotional deck"),
    DocCfg(id='033434', description=f"{SCREENSHOT} iPhone chat labeled 'Edwards' at the top"),
    DocCfg(id='023644', description=f"transcription of an interview with MBS from Saudi", date='2016-04-25'),
    DocCfg(id='029475', description=f'{VIRGIN_ISLANDS} Twin City Mobile Integrated Health Services (TCMIH) proposal/request for donation'),
    DocCfg(id='029448', description=f"weird short essay titled 'President Obama and Self-Deception'"),
]

OTHER_FILES_JUNK = [
    DocCfg(id='026678', description=f"fragment of image metadata {QUESTION_MARKS}", date='2017-06-29'),
    DocCfg(id='022986', description=f"fragment of a screenshot {QUESTION_MARKS}"),
    DocCfg(id='033478', description=f'{MEME} Kim Jong Un reading {FIRE_AND_FURY}', date='2018-01-05', duplicate_ids=['032713']),
    DocCfg(id='033177', description=f"{MEME} Trump with text 'WOULD YOU TRUST THIS MAN WITH YOUR DAUGHTER?'"),
    DocCfg(id='029564', description=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029353', description=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029352', description=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029351', description=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029354', description=OBAMA_JOKE, date='2013-07-26'),
]

OTHER_FILES_CATEGORIES = [
    'BOOKS',
    'ARTICLES',
    'COURT_DOCS',
    'CONFERENCES',
    'REPORTS',
    'LETTERS',
    'PRIVATE_PLACEMENT_MEMOS',
    'PROPERTY',
    'REPUTATION_MGMT',
    'SOCIAL_MEDIA',
    'POLITICS',
    'ACADEMIA',
    'RESUMES',
    'ARTS',
    'MISC',
    'JUNK',
]

OTHER_FILES_CONFIG = []

# Collect all OTHER_FILES_ configs into OTHER_FILES_CONFIG
for category in OTHER_FILES_CATEGORIES:
    configs = locals()[f"OTHER_FILES_{category}"]
    OTHER_FILES_CONFIG.extend(configs)

    # Inject category field
    for cfg in configs:
        cfg.category = category.lower()

ALL_CONFIGS = TEXTS_CONFIG + EMAILS_CONFIG + OTHER_FILES_CONFIG
ALL_FILE_CONFIGS: dict[str, DocCfg] = {}

# Create a dict keyed by file_id
for cfg in ALL_CONFIGS:
    ALL_FILE_CONFIGS[cfg.id] = cfg

    # Add extra config objects for duplicate files that match the config of file they are duplicating
    for dupe_cfg in cfg.duplicate_cfgs():
        ALL_FILE_CONFIGS[dupe_cfg.id] = dupe_cfg


# OtherFiles whose description/hints match these prefixes are not displayed unless --all-other-files is used
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
    CHINA_DAILY,
    CNN,
    'completely redacted',
    CVRA,
    DAILY_MAIL,
    DAILY_TELEGRAPH,
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
    JAMES_PATTERSON,
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
    'Sadis',
    'SCMP',
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


# Error checking.
assert len(OTHER_FILES_CONFIG) == 438
encountered_file_ids = set()

for cfg in ALL_CONFIGS:
    if cfg.id in encountered_file_ids:
        raise ValueError(f"{cfg.id} configured twice!\n\n{cfg}\n")
    elif cfg.dupe_of_id and cfg.dupe_of_id == cfg.id:
        raise ValueError(f"Invalid config!\n\n{cfg}\n")

    encountered_file_ids.add(cfg.id)
