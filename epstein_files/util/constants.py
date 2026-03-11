"""
Custom configurations for various files.
"""
from itertools import groupby

from epstein_files.documents.config.imessage_logs import TEXTS_CONFIG
from epstein_files.documents.config.emails import EMAILS_CONFIG, PRUSAKOVA_BERKELY
from epstein_files.documents.documents.categories import CONSTANT_CATEGORIES, Interesting, Neutral
from epstein_files.documents.documents.config_builder import (FBI_REPORT, JANE_DOE_V_USA, blaine_letter,
     fbi_defense_witness, fbi_report, fedex_invoice, important_messages_pad, letter,
     phone_bill_cfg, starr_letter, whistleblower_cfg, victim_diary, wolff_draft_cfg)
from epstein_files.documents.documents.doc_cfg import (DEFAULT_TRUNCATE_TO, GOLDMAN_INVESTMENT_MGMT,
     SHORT_TRUNCATE_TO, NO_TRUNCATE, CommunicationCfg, DocCfg, EmailCfg)
from epstein_files.documents.doj_files.full_text import EFTA00009622_TEXT
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import join_truthy, quote
from epstein_files.util.logging import logger

OTHER_FILES_PFX = 'OTHER_FILES_'
PARTICIPANTS_FIELD = 'Participants: field'
VALAR_FUND = f"{PETER_THIEL}'s {VALAR_VENTURES} fund"

HEADER_ABBREVIATIONS = {
    "AD": "Abu Dhabi",
    "Barak": f"former Israeli prime minister {EHUD_BARAK}",
    "Barrack": "Tom Barrack (Trump ally)",
    'BG, Bill': "Bill Gates",
    "Brock": 'Brock Pierce (crypto bro with a very sordid past)',
    "DB": "Deutsche Bank (maybe??)",
    "GRAT": "Grantor Retained Annuity Trust (tax shelter)",
    'HBJ, Jabor Y': "Sheikh Hamad bin Jassim (former Qatari prime minister)",
    'Jared': "Jared Kushner",
    'Jagland': 'Thorbjørn Jagland (former Norwegian prime minister)',
    'Joi': f"Joi Ito ({MIT_MEDIA_LAB}, MIT Digital Currency Initiative)",
    "Hoffenberg": f"{STEVEN_HOFFENBERG} (Epstein's ponzi scheme partner)",
    'KSA': "Kingdom of Saudi Arabia",
    'Kurz': 'Sebastian Kurz (former Austrian Chancellor)',
    'Kwok': "Chinese criminal Miles Kwok AKA Miles Guo AKA Guo Wengui",
    'LSJ': "Little St. James (Epstein's island)",
    'Madars': 'Madars Virza (co-founder of privacy crypto ZCash)',
    'Mapp': f'{KENNETH_E_MAPP} (Governor of {VIRGIN_ISLANDS})',
    'MBS': "Mohammed bin Salman Al Saud (Saudi ruler)",
    'MBZ': "Mohamed bin Zayed Al Nahyan (Emirates sheikh)",
    "Miro": MIROSLAV_LAJCAK,
    "Mooch": "Anthony 'The Mooch' Scaramucci (Skybridge crypto bro)",
    "NPA": 'non-prosecution agreement',
    "PA": PRINCE_ANDREW,
    "Terje": TERJE_ROD_LARSEN,
    "VI": f"U.S. {VIRGIN_ISLANDS}",
    "Woody": "Woody Allen",
}


########################################################################################################
################################################ EMAILS ################################################
########################################################################################################

# Descriptions
AL_SECKEL_BILL_FIGHT = f"{AL_SECKEL} and Epstein fight about the bill for reputation management services"
BEN_LAWSKY_NYDFS = f'head of NY Dept of Financial Services {BEN_LAWSKY}'
KYARA_FUND = f"Epstein crypto fund {KYARA_INVESTMENT}"
RIOT_BLOCKCHAIN_DESCRIPTION = 'RIOT Blockchain (FKA "Bioptix") is a sketchy bitcoin miner in Texas'


################################################################################################
####################################### OTHER FILES ############################################
################################################################################################

# strings
MEME = 'meme of'
RESUME_OF = 'professional resumé'
SCREENSHOT = 'screenshot of'
TRANSLATION = 'translation of'

# Legal cases
BRUNEL_V_EPSTEIN = f"{JEAN_LUC_BRUNEL} v. {JEFFREY_EPSTEIN} and Tyler McDonald d/b/a YI.org"
EDWARDS_V_DERSHOWITZ = f"{BRAD_EDWARDS} & {PAUL_G_CASSELL} v. {ALAN_DERSHOWITZ}"
EPSTEIN_V_ROTHSTEIN_EDWARDS = f"Epstein v. Scott Rothstein, {BRAD_EDWARDS}, & L.M."
GIUFFRE_V_DERSHOWITZ = f"{VIRGINIA_GIUFFRE} v. {ALAN_DERSHOWITZ}"
GIUFFRE_V_EPSTEIN = f"{VIRGINIA_GIUFFRE} v. {JEFFREY_EPSTEIN}"
GIUFFRE_V_MAXWELL = f"{VIRGINIA_GIUFFRE} v. {GHISLAINE_MAXWELL}"
JANE_DOE_V_EPSTEIN_TRUMP = f"Jane Doe v. Donald Trump and {JEFFREY_EPSTEIN}"
JANE_DOE_2_V_EPSTEIN = f'Jane Doe #2 v. {JEFFREY_EPSTEIN}'
NEW_YORK_V_EPSTEIN = f"New York v. {JEFFREY_EPSTEIN}"
REDACTED_V_EPSTEIN_ESATE = f"{REDACTED} v. Estate of Jeffrey Epstein, {GHISLAINE_MAXWELL}"

# Descriptions of non-email, non-text message files
ARTICLE_DRAFT = 'draft of an article about'
BOFA_WEALTH_MGMT = f'{BOFA} Wealth Management'
DERSH_GIUFFRE_TWEET = f"about {VIRGINIA_GIUFFRE}"
DEUTSCHE_BANK_TAX_TOPICS = f'{DEUTSCHE_BANK} Wealth Management Tax Topics'
DIANA_DEGETTE_CAMPAIGN = "Colorado legislator Diana DeGette's campaign"
FBI_SEIZED_PROPERTY = f"seized property inventory"  # (redacted)
FEMALE_HEALTH_COMPANY = 'Female Health Company (FHC)'
FIRE_AND_FURY = f"Fire And Fury"
HBS_APPLICATION = f"{HARVARD} Business School application letter"
HONEYCOMB_FUND = 'Honeycomb Asset Management (Spotify and Tencent investors)'
JASTA_SAUDI_LAWSUIT = f"{JASTA} lawsuit against Saudi Arabia by 9/11 victims"
JP_MORGAN_EYE_ON_THE_MARKET = f"Eye On The Market"
LAWRENCE_KRAUSS_ASU_ORIGINS = f"{LAWRENCE_KRAUSS}'s ASU Origins Project"
KEN_STARR_LETTER = f"letter to judge overseeing Epstein's criminal prosecution, mentions Alex Acosta"
LEXIS_NEXIS_CVRA_SEARCH = f"{LEXIS_NEXIS} search for case law around the {CVRA}"
LUTNICKS_CANTOR = f"Howard Lutnick's {CANTOR}"
OBAMA_JOKE = 'joke about Obama'
PATTERSON_BOOK_SCANS = f'pages of "Filthy Rich: The Shocking True Story of {JEFFREY_EPSTEIN}"'
REAL_DEAL_ARTICLE = 'article by Keith Larsen'
SHIMON_POST_ARTICLE = f'selection of articles about the mideast'
SKYPE_CONVERSATION = 'Skype conversation with'
STRANGE_BEDFELLOWS = "'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more"
SWEDISH_LIFE_SCIENCES_SUMMIT = f"{BARBRO_C_EHNBOM}'s Swedish American Life Science Summit (SALSS)"
TRUMP_DISCLOSURES = f"Donald Trump financial disclosures from U.S. Office of Government Ethics"
UBS_CIO_REPORT = 'CIO Monthly Extended report'
WOMEN_EMPOWERMENT = f"Women Empowerment (WE) conference"


OTHER_FILES_ACADEMIA = [
    DocCfg(id='027004', author=JOSCHA_BACH, description=f"The Computational Structure of Mental Representation", date='2013-02-26'),
    DocCfg(
        id='014697',
        author=LAWRENCE_KRAUSS_ASU_ORIGINS,
        description=f'report: "Challenges of AI: Envisioning and Addressing Adverse Outcomes"',
        duplicate_ids=['011284']
    ),
    DocCfg(id='026731', author='Lord Martin Rees', description=f"speech at first inaugural Cornell Carl Sagan Lecture"),
    DocCfg(id='015501', author=f"{MOSHE_HOFFMAN}, Erez Yoeli, and Carlos David Navarrete", description=f"Game Theory and Morality"),
    DocCfg(
        id='026521',
        author=f"{MOSHE_HOFFMAN}, Erez Yoeli, and {MARTIN_NOWAK}",
        description=f"Cooperating Without Looking: Game Theory Model of Trust and Reciprocal Cooperation"
    ),
    DocCfg(id='022405', author=NOAM_CHOMSKY, description=f"letter attesting to Epstein's good character"),
    DocCfg(id='025143', author=ROBERT_TRIVERS, description=f"Africa, Parasites, Intelligence", date='2018-06-25'),
    DocCfg(id='029155', author=ROBERT_TRIVERS, description=f'response sent to the Gruterites ({GORDON_GETTY} fans)', date='2018-03-19'),
    DocCfg(
        id='033323',
        author=f"{ROBERT_TRIVERS} and Nathan H. Lents",
        description=f"'Does Trump Fit the Evolutionary Role of Narcissistic Sociopath?' (draft)",
        date='2018-12-07',
    ),
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
    DocCfg(
        id='029355',
        description=f'{SCREENSHOT} quote in book about {LARRY_SUMMERS}',
        dupe_type='quoted',
        duplicate_ids=['029356'],  # 029356 is zoomed in corner
        is_interesting=False,
    ),
    DocCfg(
        id='EFTA01103509',
        author=BEN_GOERTZEL,
        date='2013-02-01',
        description='"Creating Robots with Toddler-Level Intelligence Using the OpenCog AGI Architecture" proposal for Epstein Foundation',
    ),
    DocCfg(
        id='EFTA01106148',
        author=GINO_YU,
        date='2011-05-01',
        description='OpenCog Hong Kong Project Interim Report',
    ),
    DocCfg(id='EFTA01114164', author=BEN_GOERTZEL, description='OpenCog Road Map 2011-2023', date='2011-01-01', date_uncertain=True),
    DocCfg(id='EFTA01114145', author=f"{BEN_GOERTZEL} and {GINO_YU}", description="OpenCog AGI Toddler Project", date='2011-06-01', date_uncertain=True),
    EmailCfg(id='EFTA00954900', description=f'Epstein donation to {MOUNT_SINAI}'),
    EmailCfg(id='EFTA00955864', description=f'Epstein donation to {MOUNT_SINAI}', is_interesting=False)
]


OTHER_FILES_ARTICLE = [
    DocCfg(id='030013', author='Aviation International News', description=f'article', date='2012-07-01'),
    DocCfg(id='013275', author=BLOOMBERG, description=f"article on notable 2013 obituaries", date='2013-12-26'),
    DocCfg(id='026543', author=BLOOMBERG, description=f"BNA article about taxes"),
    DocCfg(id='014865', author='Boston Globe', description=f"article about {ALAN_DERSHOWITZ}"),
    DocCfg(id='033231', author='Business Standard', description=f"article about Trump's visit with India's Modi"),
    DocCfg(id='023572', author=CHINA_DAILY, description=f"article on China's Belt & Road Initiative"),
    DocCfg(id='023571', author=CHINA_DAILY, description=f"article on terrorism, Macau, trade initiatives", date='2016-09-18'),
    DocCfg(id='023570', author=CHINA_DAILY, description=f"article on Belt & Road in Central/South America, Xi philosophy", date='2017-05-14'),
    DocCfg(id='025115', author=CHINA_DAILY, description=f"article on China and the US working together", date='2017-05-14'),
    DocCfg(id='012704', author='Daily Business Review', description=f"article about {JANE_DOE_V_USA} and {CVRA}", date='2011-04-21'),
    DocCfg(id='025292', author=DAILY_MAIL, description=f"article on Bill Clinton being named in a lawsuit"),
    DocCfg(id='019468', author=DAILY_MAIL, description=f"article on Epstein and Clinton"),
    DocCfg(id='022970', author=DAILY_MAIL, description=f"article on Epstein and Prince Andrew"),
    DocCfg(id='031186', author=DAILY_MAIL, description=f'article on allegations of rape of 13 year old against Trump', date='2016-11-02'),
    DocCfg(id='013437', author=DAILY_TELEGRAPH, description=f"article about Epstein's diary", date='2011-03-05'),
    DocCfg(id='023287', author=DAILY_TELEGRAPH, description=f"article about a play based on the Oslo Accords", date='2017-09-15'),
    DocCfg(id='019206', author=EDWARD_JAY_EPSTEIN, description=f"WSJ article about Edward Snowden", date='2016-12-30'),
    DocCfg(id='023567', author='Financial Times', description=f"article about quantitative easing"),
    DocCfg(id='026761', author='Forbes', description=f"article about {BARBRO_C_EHNBOM} 'Swedish American Group Focuses On Cancer'"),
    DocCfg(id='031716', author='Fortune Magazine', description=f'article by {TOM_BARRACK}', date='2016-10-22'),
    DocCfg(id='019444', author='Frontlines magazine', description=f"article 'Biologists Dig Deeper'", date='2008-01-01'),
    DocCfg(id='023720', author='Future Science', description=f'article: "Is Shame Necessary?" by {JENNIFER_JACQUET}'),
    DocCfg(id='021094', author='Globe and Mail', description=f"article about Gerd Heinrich"),
    DocCfg(id='013268', author='JetGala', description=f"article about airplane interior designer {ERIC_ROTH}"),
    DocCfg(id='029539', author=LA_TIMES, description=f"Alan Trounson interview on California stem cell research and CIRM"),
    DocCfg(id='029865', author=LA_TIMES, description=f"front page article about {DEEPAK_CHOPRA} and young Iranians", date='2016-11-05'),
    DocCfg(id='026598', author=LA_TIMES, description=f"op-ed about why America needs a Ministry of Culture"),
    DocCfg(id='027024', author=LA_TIMES, description=f"Scientists Create Human Embryos to Make Stem Cells", date='2013-05-15'),
    DocCfg(id='022811', author='Law.com', description='Sarah Ransome Identifies Herself in Epstein Sex Trafficking Case', date='2018-01-09'),
    DocCfg(id='031776', author='Law360', description=f"article about Michael Avenatti by Andrew Strickler"),
    DocCfg(id='023102', author='Litigation Daily', description=f"article about {REID_WEINGARTEN}", date='2015-09-04'),
    DocCfg(id='029340', author='MarketWatch', description=f'article about estate taxes, particularly Epstein\'s favoured GRATs'),
    # wolff_draft_cfg
    wolff_draft_cfg('022707'),
    wolff_draft_cfg('022727'),
    wolff_draft_cfg('022746'),
    wolff_draft_cfg('022844'),
    wolff_draft_cfg('022863'),
    wolff_draft_cfg('022952'),
    wolff_draft_cfg('024229'),
    wolff_draft_cfg(
        '022894',
        f"claiming Kelimbetov, {BROCK_PIERCE}, and {LARRY_SUMMERS} all visited Epstein around the time Tether was founded",
        show_with_name=BROCK_PIERCE,
        truncate_to=(13_500, 16_000),
    ),
    DocCfg(id='031198', author='Morning News USA', description=f"article about identify of Jane Doe in {JANE_DOE_V_EPSTEIN_TRUMP}"),
    DocCfg(id='015462', author='Nautilus Education', description=f'magazine (?) issue'),
    DocCfg(id='031972', author=NYT, description=f"article about #MeToo allegations against {LAWRENCE_KRAUSS}", date='2018-03-07'),
    DocCfg(id='032435', author=NYT, description=f'article about Chinese butlers'),
    DocCfg(id='029452', author=NYT, description=f"article about {PETER_THIEL}"),
    DocCfg(id='025328', author=NYT, description=f"article about radio host Bob Fass and Robert Durst"),
    DocCfg(id='033479', author=NYT, description=f"article about Rex Tillerson", date='2010-03-14'),
    DocCfg(id='028481', author=NYT, description=f'article about {STEVE_BANNON}', date='2018-03-09'),
    DocCfg(id='033181', author=NYT, description=f"article about Trump's tax avoidance", date='2016-10-31'),
    DocCfg(id='023097', author=NYT, description=f"column about The Aristocrats by Frank Rich 'The Greatest Dirty Joke Ever Told'"),
    DocCfg(id='033365', author=NYT, description=f'column about trade war with China by Kevin Rudd'),
    DocCfg(id='019439', author=NYT, description=f"column about the Clintons and money by Maureen Dowd", date='2013-08-17'),
    DocCfg(id='EFTA00040076', author=NYT, description=f"article about Epstein's death", date='2019-07-08'),
    DocCfg(id='029925', author='New Yorker', description=f"article about the placebo effect by Michael Specter"),
    DocCfg(id='013435', author=PALM_BEACH_DAILY_NEWS, description=f"article about Epstein's address book", date='2011-03-11'),
    DocCfg(id='013440', author=PALM_BEACH_DAILY_NEWS, description=f"article about Epstein's gag order", date='2011-07-13'),
    DocCfg(id='029238', author=PALM_BEACH_DAILY_NEWS, description=f"article about Epstein's plea deal"),
    DocCfg(id='021775', author=PALM_BEACH_POST, description="article about 'He Was 50. And They Were Girls'", attached_to_email_id='021764'),
    DocCfg(id='022989', author=PALM_BEACH_POST, description="article about alleged rape of 13 year old by Trump"),
    DocCfg(id='022987', author=PALM_BEACH_POST, description="article about just a headline on Trump and Epstein"),
    DocCfg(id='015028', author=PALM_BEACH_POST, description="article about reopening Epstein's criminal case"),
    DocCfg(id='022990', author=PALM_BEACH_POST, description="article about Trump and Epstein"),
    DocCfg(id='031753', author=PAUL_KRASSNER, description=f'essay for Playboy in the 1980s', date='1985-01-01'),
    DocCfg(id='023638', author=PAUL_KRASSNER, description=f'magazine interview'),
    DocCfg(id='024374', author=PAUL_KRASSNER, description=f"Remembering Cavalier Magazine"),
    DocCfg(id='030187', author=PAUL_KRASSNER, description=f'"Remembering Lenny Bruce While We\'re Thinking About Trump" (draft?)'),
    DocCfg(id='019088', author=PAUL_KRASSNER, description=f'"Are Rape Jokes Funny?" (draft)', date='2012-07-28'),
    DocCfg(id='012740', author=PEGGY_SIEGAL, description=f"article about Venice Film Festival"),
    DocCfg(id='013442', author=PEGGY_SIEGAL, description=f"draft about Oscars", date='2011-02-27'),
    DocCfg(id='012700', author=PEGGY_SIEGAL, description=f"film events diary", date='2011-02-27'),
    DocCfg(id='012690', author=PEGGY_SIEGAL, description=f"film events diary early draft of 012700", date='2011-02-27'),
    DocCfg(id='013450', author=PEGGY_SIEGAL, description=f"Oscar Diary in Avenue Magazine", date='2011-02-27'),
    DocCfg(id='010715', author=PEGGY_SIEGAL, description=f"Oscar Diary April", date='2012-02-27'),
    DocCfg(id='019849', author=PEGGY_SIEGAL, description=f"Oscar Diary April", date='2017-02-27', duplicate_ids=['019864']),
    DocCfg(id='026851', author='Politifact', description=f"lying politicians chart", date='2016-07-26'),
    DocCfg(id='033253', author=ROBERT_LAWRENCE_KUHN, description=f'{BBC} article about Rohingya in Myanmar', attached_to_email_id='033252'),
    DocCfg(id='026887', author=ROBERT_LAWRENCE_KUHN, description=f'{BBC} "New Tariffs - Trade War"'),
    DocCfg(id='026877', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "New Tariffs - Trade War"'),
    DocCfg(id='026868', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "Quest Means Business New China Tariffs — Trade War"', date='2018-09-18'),
    DocCfg(id='023707', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "Quest Means Business U.S. and China Agree to Pause Trade War"', date='2018-12-03'),
    DocCfg(id='029176', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "U.S. China Tariffs - Trade War"', attached_to_email_id='029174'),
    DocCfg(id='032638', author=ROBERT_LAWRENCE_KUHN, description=f'{CNN} "Xi Jinping and the New Politburo Committee"', attached_to_email_id='032637'),
    DocCfg(id='023666', author=ROBERT_LAWRENCE_KUHN, description=f"sizzle reel / television appearances", date='2018-09-30', attached_to_email_id='033252'),
    DocCfg(id='016996', author='SciencExpress', description=f'article "Quantitative Analysis of Culture Using Millions of Digitized Books" by Jean-Baptiste Michel'),
    DocCfg(id='025104', author='SCMP', description=f"article about China and globalisation"),
    DocCfg(id='030030', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-03-29'),
    DocCfg(id='025610', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-04-03'),
    DocCfg(id='023458', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-04-17'),
    DocCfg(id='023487', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-04-18'),
    DocCfg(id='030531', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-05-16'),
    DocCfg(id='024958', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-05-08'),
    DocCfg(id='030060', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-05-13'),
    DocCfg(id='031834', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-05-16'),
    DocCfg(id='023517', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-05-26'),
    DocCfg(id='030268', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-05-29'),
    DocCfg(id='029628', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-06-04'),
    DocCfg(id='018085', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-06-07'),
    DocCfg(id='030156', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-06-22'),
    DocCfg(id='031876', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-06-14'),
    DocCfg(id='032171', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-06-26'),
    DocCfg(id='029932', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-07-03'),
    DocCfg(id='031913', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-08-24'),
    DocCfg(id='024592', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-08-25'),
    DocCfg(id='024997', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-09-08'),
    DocCfg(id='031941', author=SHIMON_POST, description=SHIMON_POST_ARTICLE, date='2011-11-17'),
    DocCfg(id='030829', author='South Florida Sun Sentinel', description=f'article about {BRAD_EDWARDS} and {JEFFREY_EPSTEIN}'),
    DocCfg(id='021092', author='Tatler', description=f'single page of article about {GHISLAINE_MAXWELL} shredding documents'),
    DocCfg(id='030333', author='The Independent', description=f'article about Prince Andrew, Epstein, and Epstein\'s butler who stole his address book'),
    DocCfg(id='010754', author='U.S. News', description=f"article about Yitzhak Rabin"),
    DocCfg(id='014498', author=VI_DAILY_NEWS, description='article', date='2016-12-13'),
    DocCfg(id='031171', author=VI_DAILY_NEWS, description='article', date='2019-02-06'),
    DocCfg(id='023048', author=VI_DAILY_NEWS, description='article', date='2019-02-27'),
    DocCfg(id='023046', author=VI_DAILY_NEWS, description='article', date='2019-02-27'),
    DocCfg(id='031170', author=VI_DAILY_NEWS, description='article', date='2019-03-06'),
    DocCfg(id='016506', author=VI_DAILY_NEWS, description='article', date='2019-02-28'),
    DocCfg(id='018862', author=VI_DAILY_NEWS, description='articles about Sen. Alvin Williams Jr. Fraud case, arson', date='2012-11-09'),
    DocCfg(id='016507', author=VI_DAILY_NEWS, description=f'"Perversion of Justice" by {JULIE_K_BROWN}', date='2018-12-19'),
    DocCfg(id='019212', author=WAPO, description=f'and Times Tribune articles about Bannon, Trump, and healthcare execs'),
    DocCfg(id='033379', author=WAPO, description=f'"How Washington Pivoted From Finger-Wagging to Appeasement" (about Viktor Orban)', date='2018-05-25'),
    DocCfg(
        id='031396',
        author=WAPO,
        description=f"DOJ discipline office with limited reach to probe handling of controversial sex abuse case",
        date='2019-02-06',
        duplicate_ids=['031415'],
    ),
    DocCfg(id='030199', description=f'article about Trump rape allegations in {JANE_DOE_V_EPSTEIN_TRUMP}', date='2017-11-16'),
    DocCfg(id='031725', description=f"article about Gloria Allred and Trump allegations", date='2016-10-10'),
    DocCfg(id='026648', description=f'article about {JASTA} lawsuit against Saudi Arabia by 9/11 victims (Russian propaganda?)', date='2017-05-13'),
    DocCfg(id='032159', description=f"article about microfinance and cell phones in Zimbabwe, Strive Masiyiwa (Econet Wireless)"),
    DocCfg(id='030825', description=f'{ARTICLE_DRAFT} Syria'),
    DocCfg(id='027051', description=f"German article about the 2013 Lifeball / AIDS Gala", date='2013-01-01', attached_to_email_id='027049'),
    DocCfg(id='033480', description=f"John Bolton press clipping", date='2018-04-06', duplicate_ids=['033481']),
    DocCfg(id='013403', description=f"{LEXIS_NEXIS} result from The Evening Standard about Bernie Madoff", date='2009-12-24'),
    DocCfg(id='021093', description=f"page of unknown article about Epstein and Maxwell"),
    DocCfg(id='031191', description=f"single page of unknown article about Epstein and Trump's relationship in 1997"),
    DocCfg(id='026520', description=f'Spanish article about {SULTAN_BIN_SULAYEM}', date='2013-09-27'),
    DocCfg(
        id='031736',
        author='Abdulnaser Salamah',
        description=f'{TRANSLATION} Arabic article "Trump; Prince of Believers (Caliph)!"',
        date='2017-05-13',
    ),
    DocCfg(id='025094', description=f'{TRANSLATION} Spanish article about Cuba', date='2015-11-08'),
    DocCfg(id='031794', description=f"very short French magazine clipping"),

    # DOJ files
    DocCfg(
        id='EFTA02711825',
        author='Techonomy',
        author_uncertain='either this or EFTA01139627 are referenced in email EFTA01745739',
        description='article titled "Artificial Intelligence Ignites in Ethiopia"',
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA01139627',
        author='Techonomy',
        author_uncertain='either this or EFTA02711825 are referenced in email EFTA01745739',
        date='2014-08-15',
        date_uncertain=f'using date of {BEN_GOERTZEL} email',
        description='article about iCog Labs titled "A Harvard Financier, Jeffrey Epstein, Advances Artificial Intelligence in Ethiopia"',
        is_interesting=True,
    ),
]


OTHER_FILES_ARTS = [
    DocCfg(id='018703', author=ANDRES_SERRANO, description=f"artist statement about Trump objects"),
    DocCfg(id='023438', author=BROCKMAN_INC, description=f"announcement of auction of 'Noise' by Daniel Kahneman, Olivier Sibony, and Cass Sunstein"),
    DocCfg(
        id='025147',
        author=BROCKMAN_INC,
        date='2016-10-23',
        description=f'Frankfurt Book Fair hot list includes book about Silk Road / Ross Ulbricht',
        is_interesting=True,
    ),
    DocCfg(id='030769', author='Independent Filmmaker Project (IFP)', description=f"2017 Gotham Awards invitation"),
    DocCfg(
        id='025205',
        author='Mercury Films',
        date='2010-02-01',
        description=f'partner profiles of Jennifer Baichwal, Nicholas de Pencier, Kermit Blackwood, Travis Rummel',
        duplicate_ids=['025210']
    ),
    DocCfg(
        id='028281',
        author='Wolfe Von Lenkiewicz & Victoria Golembiovskaya',
        date='2010-10-13',
        description=f'art show flier for "The House Of The Nobleman"',
    ),
]

OTHER_FILES_BOOK = [
    DocCfg(id='017088', author=ALAN_DERSHOWITZ, description=f'"Taking the Stand: My Life in the Law" (draft)', date='2012-04-02'),  # Slow file
    DocCfg(id='013501', author='Arnold J. Mandell', description=f'The Nearness Of Grace: A Personal Science Of Spiritual Transformation', date='2005-01-01'),
    DocCfg(id='012899', author='Ben Goertzel', description=f'Engineering General Intelligence: A Path to Advanced AGI Via Embodied Learning and Cognitive Synergy', date='2013-09-19'),
    DocCfg(id='018438', author='Clarisse Thorn', description=f'The S&M Feminist', date='2012-05-14'),
    DocCfg(id='019477', author=EDWARD_JAY_EPSTEIN, description=f'How America Lost Its Secrets: Edward Snowden, the Man, and the Theft'),
    DocCfg(id='020153', author=EDWARD_JAY_EPSTEIN, description=f'The Snowden Affair: A Spy Story In Six Parts'),
    DocCfg(id='011472', author=EHUD_BARAK, description=f'"Night Flight" (draft)', date='2006-07-12', duplicate_ids=['027849'], is_interesting=False),  # date from _extract_timestamp()
    DocCfg(id='010912', author=GORDON_GETTY, description=f'"Free Growth and Other Surprises" (draft)', date='2018-10-18'),
    DocCfg(id='010477', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='010486', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='021958', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='022058', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='022118', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='019111', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='015675', author='James Tagg', description=f'Are the Androids Dreaming Yet? Amazing Brain Human Communication, Creativity & Free Will', date='2015-06-01'),  # Slow file
    DocCfg(id='016804', author=JOHN_BROCKMAN, description='Deep Thinking: Twenty-Five Ways of Looking at AI', date='2019-02-19', duplicate_ids=['016221']),
    DocCfg(id='018232', author='Joshua Cooper Ramo', description=f'The Seventh Sense: Power, Fortune & Survival in the Age of Networks', date='2015-03-11'),
    DocCfg(id='012747', author='Marc D. Hauser', description=f'Evilicious: Explaining Our Taste For Excessive Harm'),
    DocCfg(id='032724', author=MICHAEL_WOLFF, description=f'cover of "{FIRE_AND_FURY}"', date='2018-01-05', is_interesting=False),
    DocCfg(id='021120', author=MICHAEL_WOLFF, description=f'chapter of "Siege: Trump Under Fire"'),
    DocCfg(id='019874', author=MICHAEL_WOLFF, description=FIRE_AND_FURY, date='2018-01-05', is_interesting=False),
    DocCfg(id='015032', author=PAUL_KRASSNER, description=f"60 Years of Investigative Satire: The Best of {PAUL_KRASSNER}"),
    DocCfg(id='023731', author=ROGER_SCHANK, description=f'Teaching Minds How Cognitive Science Can Save Our Schools'),
    DocCfg(id='021247', author='The Chicago Social Brain Network', description=f'Invisible Forces And Powerful Beliefs: Gravity, Gods, And Minds', date='2010-10-04'),
    DocCfg(id='013796', author='Tim Ferriss', description=f'The 4-Hour Workweek'),
    DocCfg(id='021145', author=VIRGINIA_GIUFFRE, description=f'"The Billionaire\'s Playboy Club" (draft?)'),
    DocCfg(id='031533', description=f'pages from a book about the Baylor University sexual assault scandal and Sam Ukwuachu'),
    # DOJ files
    DocCfg(id='EFTA00008020', replace_text_with='"Massage for Dummies"'),
    DocCfg(id='EFTA00008320', replace_text_with='"Massage for Dummies (???)"'),
    DocCfg(id='EFTA00008220', replace_text_with='"Massage book: Chapter 11: Putting the Moves Together"'),
    DocCfg(id='EFTA00008120', replace_text_with='"Part II: The Art of Receiving a Massage"'),
]


OTHER_FILES_DEPOSITION = [
    DocCfg(id='021824', author=PAUL_G_CASSELL, description=f"from {EDWARDS_V_DERSHOWITZ}"),
    DocCfg(id='013463', author='Scott Rothstein', description=f"from {JANE_DOE_V_EPSTEIN_TRUMP}", date='2010-03-23'),
    DocCfg(id='017488', author='Scott Rothstein', description=f"from {EPSTEIN_V_ROTHSTEIN_EDWARDS}", date='2012-06-22'),
    # DOJ
    DocCfg(id='EFTA00615804', author=ALAN_DERSHOWITZ, date='2016-01-12', description='pages 334-461 (heavily redacted)'),
    DocCfg(
        id='EFTA00159483',
        author=LAWRANCE_VISOSKI,
        is_interesting=True,
        non_participants=[EHUD_BARAK, GLENN_DUBIN, LARRY_SUMMERS, NAOMI_CAMPBELL],
    ),
    DocCfg(id='EFTA00009229', author='Alex Acosta', description='pages 1-100', date='2020-04-30', is_interesting=True),
    DocCfg(id='EFTA00009329', author='Alex Acosta', description='pages 101-200', date='2020-04-30', is_interesting=True),
    DocCfg(id='EFTA00009016', author='Alex Acosta', description='pages 201-300', date='2020-04-30', is_interesting=True),
    DocCfg(id='EFTA00009116', author='Alex Acosta', description='pages 300-411', date='2020-04-30', is_interesting=True),
    DocCfg(
        id='EFTA00008744',
        author='FBI',
        date='2021-03-29',
        description='grand jury testimony of Child Exploitation & Human Trafficking Task Force member',
    ),
    DocCfg(id='EFTA01108807', author='Jane Doe', date='2010-02-09', description='vol. III of IV'),
    DocCfg(id='EFTA00023557', author='victim', description=f'who says {GHISLAINE_MAXWELL} and Epstein pay for nudes'),
    # DocCfg(id='EFTA00064843', author=UNKNOWN_GIRL, description=f'{GHISLAINE_MAXWELL} "relentless"'),
    DocCfg(id='EFTA00078311', author=REDACTED_V_EPSTEIN_ESATE, description=f'Boies Schiller filing about sexual abuse of their client'),
    DocCfg(id='EFTA00105975', author=REDACTED_V_EPSTEIN_ESATE, description=f'{GHISLAINE_MAXWELL} "was relentless"'),
    DocCfg(id='EFTA00158752', author=REDACTED_V_EPSTEIN_ESATE, description=f'{GHISLAINE_MAXWELL} "was relentless"'),
    DocCfg(id='EFTA01246559', author=JANE_DOE_2_V_EPSTEIN, date='2010-04-09'),
]


OTHER_FILES_CONFERENCE = [
    DocCfg(id='014315', author=BOFA_MERRILL, description=f'2016 Future of Financials Conference', attached_to_email_id='014312'),
    DocCfg(id='026825', author=DEUTSCHE_BANK, description=f"Asset & Wealth Management featured speaker bios"),  # Really "Deutsche Asset" which may not be Deutsche Bank?
    DocCfg(id='023123', author=LAWRENCE_KRAUSS_ASU_ORIGINS, description=f"{STRANGE_BEDFELLOWS} (old draft)"),
    DocCfg(id='023120', author=LAWRENCE_KRAUSS_ASU_ORIGINS, description=STRANGE_BEDFELLOWS, duplicate_ids=['023121'], dupe_type='earlier'),
    DocCfg(id='031359', author=NOBEL_CHARITABLE_TRUST, description=f'"Earth Environment Convention" about ESG investing'),
    DocCfg(id='031354', author=NOBEL_CHARITABLE_TRUST, description=f'"Thinking About the Environment and Technology" report 2011'),
    DocCfg(id='019300', author=SVETLANA_POZHIDAEVA, description=f'{WOMEN_EMPOWERMENT} f. {KATHRYN_RUEMMLER}', date='2019-04-05', show_full_panel=True),
    DocCfg(id='022267', author=SVETLANA_POZHIDAEVA, description=f'{WOMEN_EMPOWERMENT} founder essay about growing the seminar business'),
    DocCfg(id='022407', author=SVETLANA_POZHIDAEVA, description=f'{WOMEN_EMPOWERMENT} seminar pitch deck'),
    DocCfg(id='017524', author=SWEDISH_LIFE_SCIENCES_SUMMIT, description=f"2012 program", date='2012-08-18', attached_to_email_id='017523'),
    DocCfg(id='026747', author=SWEDISH_LIFE_SCIENCES_SUMMIT, description=f"2017 program", date='2017-08-23', attached_to_email_id='031215'),
    DocCfg(id='014951', author='TED Talks', description=f"2017 program", date='2017-04-20'),
    DocCfg(
        id='024185',
        author=UN_GENERAL_ASSEMBLY,
        description=f'schedule including "Presidents Private Dinner - Jeffrey Epstine (sic)"',
        date='2012-09-21',
        is_interesting=True,
    ),
    DocCfg(id='024179', author=UN_GENERAL_ASSEMBLY, description=f'president and first lady schedule', date='2012-09-21'),
    DocCfg(
        id='029427',
        description=f"seems related to an IRL meeting about Chinese attempts to absorb Mongolia",
        is_interesting=True,
    ),
    DocCfg(
        id='025797',
        date='2013-05-29',
        description=f"someone's notes from Aspen Strategy Group",
        is_interesting=True,
    ),
    DocCfg(
        id='017060',
        description=f'World Economic Forum (WEF) Annual Meeting 2011 List of Participants',
        date='2011-01-18',
    ),
    DocCfg(id='017526', description=f'Intellectual Jazz conference brochure f. {DAVID_BLAINE}'),
]


# This category is automatically 'interesting', see OtherFile class
OTHER_FILES_CRYPTO = [
    DocCfg(id='031743', description=f'a few pages describing the internet as a "New Nation State" (Network State?)'),
    DocCfg(
        id='025663',
        author=GOLDMAN_INVESTMENT_MGMT,
        description=f"An Overview of the Current State of Cryptocurrencies and Blockchain",
        date='2017-11-15',
        duplicate_ids=['EFTA00793120'],
    ),
    # Alternative currencies
    EmailCfg(
        id='EFTA02021870',
        author=BARNABY_MARSH,
        date='2012-01-29 11:15:00',
        highlight_quote="I would like to see you alone to discuss alternative currencies",
        recipients=[JEFFREY_EPSTEIN],
    ),
    EmailCfg(
        id='EFTA00941810',
        author_reason='"chris" in reply, "cell:/email" in signature',
        recipients=[CHRISTINA_GALBRAITH],
        truncate_to=1_000,
    ),
    EmailCfg(id='EFTA01852443'),
    EmailCfg(id='EFTA01754301'),
    EmailCfg(id='EFTA02361956', author=LINDA_STONE, author_reason='signature'),
    EmailCfg(id='EFTA02575430', description='alternative currencies group'),
    EmailCfg(id='EFTA00660838', description=f"Epstein says his trip to Ivory Coast was amazing", truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA02391375', highlight_quote="Have you heard of the alternative currency"),
    # Bannon
    EmailCfg(id='030711', description='Epstein says "we can discuss michael and his coins", unclear what that means'),
    EmailCfg(id='026260', comment='Bannon cripto coin issues'),
    EmailCfg(id='026258', description=f'Bannon suggests {JEFFREY_WERNICK}, Parler COO and man affiliated with many shady crypto businesses, can help'),
    EmailCfg(id='030781', description="Esptein says the crypto coin issues they're having are 'US based'"),
    EmailCfg(id='026255', description='Epstein requests help with "coin issues" and "prohibitions foreign donor" (sic)', is_interesting=True),
    EmailCfg(id='EFTA02521522'),
    EmailCfg(id='EFTA02524752', description=f'{STEVE_BANNON} "is thinking of combining crypto with his politcial movement"', show_with_name=STEVE_BANNON),
    EmailCfg(id='EFTA01020383', description='Epstein emails Bannon a quote about the use of crypto to evade capital controls'),
    EmailCfg(id='EFTA00874793', description=f'Bannon says that they need to stop EU regulation of crypto scams "dead in its tracks"', is_interesting=True),
    EmailCfg(id='EFTA02517572', description=f'Bannon says that they need to stop EU regulation of crypto scams "dead in its tracks"'),
    EmailCfg(id='EFTA00881711', description=f"Bannon and Epstein discuss bitcoin and crypto donations", is_interesting=True),
    EmailCfg(id='EFTA00881759', description=f"Epstein and {STEVE_BANNON} discuss collection donations in bitcoin", is_interesting=True),
    # Bill Gates
    EmailCfg(id='EFTA02639760', description='Epstein pushing cryptocurrency on Bill Gates'),
    # Bitmain
    EmailCfg(id='EFTA01004576'),
    # Blockstream
    DocCfg(id='EFTA00797613', description='Alphabit crypto fund pitch deck', attached_to_email_id='EFTA00955063'),
    EmailCfg(id='EFTA02229342', author=AUSTIN_HILL),
    EmailCfg(
        id='EFTA02406818',
        author=AUSTIN_HILL,
        author_reason='unique email signature',
        description=f"{AUSTIN_HILL} asks Epstein about how the Treasury Dept. will treat dollar backed stablecoins like Tether",
    ),
    EmailCfg(
        id='EFTA00955063',
        description=f'{AUSTIN_HILL} explains that some crypto funds are engaged in fraudulent wash trading (the attached Excel sheet listing those funds has not been found)',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA00673841',
        description="@pmarca is Marc Andreessen (a16z)",
        highlight_quote='business, Bitcoin, personal & esoteric mind games that we play',
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(id='EFTA02529170', description=f"Blockstream set up a special company to invest in an Asian ride hailing service"),
    EmailCfg(id='EFTA01917402', description=f'discussion of Epstein investment in Blockstream funneled through {JOI_ITO}', is_interesting=True),
    EmailCfg(id='EFTA00999897', description=f"Epstein claims he's a fan of {ADAM_BACK} (who has recently claimed he had nothing to do with Epstein)"),
    EmailCfg(id='EFTA01915883', description=f"{JOI_ITO} doesn't trust {AUSTIN_HILL} (for good reason)"),
    EmailCfg(id='EFTA00988395', description=f'"Andy Back" is probably Blockstream bitcoin dev {ADAM_BACK}', duplicate_ids=['EFTA01928856']),
    EmailCfg(id='EFTA01925969', description=f"{AUSTIN_HILL} and {ADAM_BACK} and some women plan a trip to Epstein's island", is_interesting=True),
    EmailCfg(id='EFTA00929418', description=f"Epstein forwards information from {AUSTIN_HILL} about fraudulent crypto trading operations to {PAUL_BARRETT}"),
    EmailCfg(id='EFTA01010209', description=f"{AUSTIN_HILL} calls {AMIR_TAAKI} \"a bit crazy\'"),
    EmailCfg(id='EFTA01788532', description=f"{AUSTIN_HILL} asking about Jeffrey Katzenberg's contact info"),
    EmailCfg(id='EFTA02515798', recipients=[LINDA_STONE], description='Epstein confirms he invested in Blockstream'),  # response to EFTA02515756
    # Blockchain Capital / Brock Pierce / Crypto Currency Partners
    DocCfg(id='024271', author=BLOCKCHAIN_CAPITAL, description="pitch deck", date='2015-10-01'),
    EmailCfg(
        id='EFTA00689503',
        description=f"{BROCK_PIERCE} posts review of infamous Russian criminal crypto exchange BTC-e to LinkedIn",
        is_interesting=True,
        show_with_name=BROCK_PIERCE,
        # truncate_to=(1_400, 3_050),  # TODO: enable excerpts in emails
    ),
    DocCfg(id='EFTA01088644', author=BLOCKCHAIN_CAPITAL, description="pitch deck", date='2015-10-01'),
    DocCfg(id='EFTA00604942', author=BLOCKCHAIN_CAPITAL, description="Investor Update", date='2015-10-01'),
    DocCfg(id='EFTA01089535', author=CRYPTO_CURRENCY_PARTNERS_II, description=f"investor report", date='2014-10-01'),
    DocCfg(id='EFTA01089506', author=CRYPTO_CURRENCY_PARTNERS_II, description=f"investor report", date='2014-11-01'),
    DocCfg(id='EFTA01089500', author=CRYPTO_CURRENCY_PARTNERS_II, description=f"investor report", date='2015-01-01'),
    DocCfg(id='EFTA00621239', author=CRYPTO_CURRENCY_PARTNERS_II, description=f"investor report", date='2014-10-01'),
    DocCfg(id='EFTA01089526', author=CRYPTO_CURRENCY_PARTNERS_II, description=f"investor report", date='2014-08-01', attached_to_email_id='EFTA00997803'),
    DocCfg(id='EFTA01089485', author=CRYPTO_CURRENCY_PARTNERS_II, description=f"investor report", date='2014-09-01', attached_to_email_id='EFTA00693621'),
    DocCfg(id='EFTA01093509', author=CRYPTO_CURRENCY_PARTNERS_II, description=f"partnership draft", truncate_to=DEFAULT_TRUNCATE_TO * 2),
    DocCfg(id='EFTA01093444', author=CRYPTO_CURRENCY_PARTNERS_II, description='application form', attached_to_email_id='EFTA00626220'),  #EFTA02708994
    DocCfg(id='EFTA01093471', author=CRYPTO_CURRENCY_PARTNERS_II, description='operating agreement', attached_to_email_id='EFTA00626220'),
    DocCfg(id='EFTA01126582', author=EXPRESSCOIN, description=f"pitch deck for {BROCK_PIERCE} co.", attached_to_email_id='EFTA00990186'),
    DocCfg(id='EFTA01125964', author=EXPRESSCOIN, description=f"pitch deck for {BROCK_PIERCE} co.", attached_to_email_id='EFTA00985076'),
    EmailCfg(id='EFTA02465656', description=f"{BROCK_PIERCE} describes investment in video game items company"),
    EmailCfg(id='EFTA00673123', description=f"{BROCK_PIERCE} and Epstein invested in Coinbase which would turn out to be extremely lucrative", duplicate_ids=['EFTA02371875']),
    EmailCfg(id='EFTA01051074', description=f'{BROCK_PIERCE} arranging meeting between Bannon and Epstein (in Doha?)'),
    EmailCfg(id='EFTA02361144', description=f'{BROCK_PIERCE} brings Epstein an opportunity to invest in Blockstream, bitcoin developer {ADAM_BACK}\'s company'),
    EmailCfg(id='EFTA00999392', description=f"{BROCK_PIERCE} discussing a possibly sham marriage to someone named Sue for immigration purposes"),
    EmailCfg(id='EFTA02514539', description=f"{BROCK_PIERCE} has tax problems (hasn't filed a tax return in 5 years)", is_interesting=True),
    EmailCfg(id='EFTA00658457', description=f'{BROCK_PIERCE} says they will not invest in Bitfury', truncate_to=700),
    EmailCfg(id='EFTA00998595', description=f'{BROCK_PIERCE} and Epstein discuss structure of crypto investments'),
    EmailCfg(id='EFTA01000882', description=f"{BROCK_PIERCE} asks for Epstein's permission to disclose his name to Coinbase team", is_interesting=True),
    EmailCfg(id='EFTA00664424', description=f"{BROCK_PIERCE} suggests {LARRY_SUMMERS} could get involved with Tether and Noble Bank"),
    EmailCfg(id='EFTA01139067', description=f'Epstein tells Farkas he has not invested in {CRYPTO_CURRENCY_PARTNERS_II}', is_interesting=True),
    EmailCfg(id='EFTA00752383', description=f"Mindshift conference attendee list including {BROCK_PIERCE}", is_interesting=True),
    EmailCfg(id='EFTA00626220', description=f'setting up "sidecar fund" with {BROCK_PIERCE} / {CRYPTO_CURRENCY_PARTNERS_II}'),
    # Boris Nikolic
    EmailCfg(id='EFTA00844780'),
    EmailCfg(id='EFTA01770220'),
    EmailCfg(id='EFTA02037504'),
    EmailCfg(id='EFTA00972689', description=f"Epstein and Nikolic ruminate on the Silk Road bust", truncate_to=NO_TRUNCATE),
    EmailCfg(
        id='EFTA02436105',
        description="one of Epstein's goals in life was to make a lot of money in virtual currency",
        is_interesting=True,
    ),
    # Coinbase
    DocCfg(
        id='EFTA01082451',
        author=BLOCKCHAIN_CAPITAL,
        date='2014-11-10',
        description=f'/ {COINBASE} nondisclosure agreement possibly regarding Epstein investment',
        is_interesting=True,
        truncate_to=2000,
    ),
    DocCfg(id='EFTA01401059', description=f"{DEUTSCHE_BANK} wire transfer receipt for Epstein's investment in {BLOCKSTREAM}"),
    DocCfg(id='EFTA01092555', author=COINBASE, description='certificate of incorporation', date='2013-12-12', truncate_to=SHORT_TRUNCATE_TO),
    DocCfg(id='EFTA01120975', author=COINBASE, description='Series B stock purchase', date='2013-12-12', truncate_to=DEFAULT_TRUNCATE_TO),
    DocCfg(id='EFTA01121035', author=COINBASE, description='Series C preferred stock purchase', date='2014-10-24'),
    EmailCfg(id='EFTA02606117', comment='Coinbase valuation'),
    EmailCfg(id='EFTA02608112', comment='Coinbase valuation'),
    EmailCfg(id='EFTA00901772', description=f"Epstein's investment in {COINBASE} would earn him most of $100 million", is_interesting=True),
    EmailCfg(id='EFTA00900908', description="negotiation of repurchase of part of Epstein's stake in Coinbase"),
    # Crypto PR Lab
    DocCfg(id='EFTA00295126', author=CRYPTO_PR_LAB, description="accounting statement", show_full_panel=True),
    DocCfg(id='EFTA01299820', author=CRYPTO_PR_LAB, description="bank transfer", date='2018-12-18'),
    DocCfg(id='EFTA00309271', author=CRYPTO_PR_LAB, description='financial statement'),
    DocCfg(id='EFTA01613759', author=CRYPTO_PR_LAB, description="letter of intent of acquisitionfrom Transform Group"),
    DocCfg(id='EFTA01613762', author=CRYPTO_PR_LAB, description=f"WhatsApp convo with {MARIA_PRUSAKOVA}", date='2019-05-21'),
    DocCfg(id='EFTA01612721', author=CRYPTO_PR_LAB, description=f"WhatsApp convo with {MARIA_PRUSAKOVA}", date='2019-05-21'),
    EmailCfg(id='033255', description=f"{MASHA_DROKOVA}'s friend Dylan Love suggests he could quote Epstein explaining \"proper implementation of crypto might solve financial corruption issues\""),
    EmailCfg(id='EFTA01013266', description=f"{MARIA_PRUSAKOVA}'s {CRYPTO_PR_LAB} request for payment for Davos", is_interesting=True),
    EmailCfg(id='EFTA02285514', description=f"Medici Bank and {MARIA_PRUSAKOVA} meeting", is_interesting=True),
    EmailCfg(id='EFTA01013922', description=f"{CRYPTO_PR_LAB} business plan", is_interesting=True),
    EmailCfg(id='EFTA00495349', author=MARIA_PRUSAKOVA, author_reason=CRYPTO_PR_LAB, description='Ed Boyle / Medici Bank'),
    EmailCfg(
        id='EFTA02267133',
        author=LESLEY_GROFF,
        recipients=[MARIA_PRUSAKOVA],
        recipient_uncertain=f"{CRYPTO_PR_LAB} signature, could be Prusakova's partner",
        truncate_to=NO_TRUNCATE
    ),
    EmailCfg(
        id='EFTA02349697',
        author=MARIA_PRUSAKOVA,
        author_reason='boyfriend Christian, same as 032374',
        description=f'{MARIA_PRUSAKOVA} says she is starting a crypto company with {ZUBAIR_KHAN}',
    ),
    # Crypto PR Lab / Medici Bank
    DocCfg(id='EFTA01613731', description='Medici Bank conversation on Whatsapp'),
    DocCfg(id='EFTA00805569', description='Mercantile Global Holdings, San Juan Mercantile Bank & Trust, Noble Bank + Signature Bank + BitGo'),
    DocCfg(id='EFTA01088079', description="someone's thoughts on bitcoin"),
    EmailCfg(id='EFTA00495372', description=f'discussion of Medici Bank, a new successor to Noble Bank as a crypto bank', is_interesting=True),
    EmailCfg(
        id='EFTA01030070',
        description="Bo Collins inspired by Epstein to set up Mercantile Global Holdings crypto trading offering stablecoins to people who can't get bank accounts",
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA02603577',
        description='meeting with Mercantile Global Holdings Bo Collins, who would testify in the trial of Miles Guo',
        is_interesting=True
    ),
    # David Stern
    EmailCfg(
        id='EFTA02494305',
        description=f"planning a crypto exchange in Belarus, {DAVID_STERN}'s \"Chinese guys\" can't do it because of the PRC's crackdown on crypto",
    ),
    EmailCfg(id='EFTA00886763', description=f"documents are being prepared to license Epstein and {DAVID_STERN}'s crypto exchange in Belarus"),
    EmailCfg(
        id='EFTA02494000',
        description=f'Epstein says a crypto exchange in Belarus could be "very useful", {DAVID_STERN}\'s Chinese guys could have brought "significant volume"',
        is_interesting=True,
    ),
    # Honeycomb
    DocCfg(id='EFTA00803491', author=HONEYCOMB_FUND, description="deck", is_interesting=True),
    DocCfg(id='EFTA00803459', author=HONEYCOMB_FUND, description="January 2019 report", is_interesting=True),
    DocCfg(id='EFTA00603445', author=HONEYCOMB_FUND, description="July 2017 report", is_interesting=True),
    DocCfg(id='EFTA00803464', author=HONEYCOMB_FUND, description="July 2018 report", date='2018-07-17', is_interesting=True),
    # Howard Lutnick
    DocCfg(id='EFTA01582043', description=f"{DEUTSCHE_BANK} / {CANTOR} transaction"),
    DocCfg(id='EFTA01230639', date='2012-12-22', date_uncertain=True, show_full_panel=True),
    DocCfg(id='EFTA00434306', description='calendar reminder for call with Howard Lutnick', date='2011-04-26', show_full_panel=True),
    DocCfg(
        id='EFTA00020515',
        author=FBI,
        description='tip about Howard Lutnick and financial irregularities',
        is_interesting=True,
        show_full_panel=True,
    ),
    DocCfg(
        id='EFTA00289560',
        date='2012-12-28',
        description=f'{HOWARD_LUTNICK} and Epstein business deal for Adfin Solutions, Inc. (Southern Trust is Epstein)',
        truncate_to=(160_000, 162_000),
    ),
    DocCfg(
        id='EFTA01249210',
        author=FBI,
        description="tip linking American commerce secretary and Tether asset custodian Howard Lutnick to Ponzi schemes and Russian money",
        is_interesting=True,
        show_with_name=BROCK_PIERCE,
    ),
    DocCfg(
        id='EFTA01733746',
        date='2011-05-18',
        description=f'schedule showing "drinks" with {HOWARD_LUTNICK}',
        is_valid_for_name_scan=False,
        show_full_panel=True,
        truncate_to=700,
    ),
    DocCfg(
        id='EFTA01249207',
        author=FBI,
        description="tip linking American commerce secretary and Tether asset custodian Howard Lutnick to Ponzi schemes and Russian money",
        show_full_panel=True,
        show_with_name=BROCK_PIERCE,
    ),
    DocCfg(
        id='EFTA01684300',
        author=FBI,
        description=f'evidence list w/tip about {HOWARD_LUTNICK}, Cantor Fitzgerald, and BGC from an employee who had already blown the whistle successfully',
        truncate_to=(77_000, 77_300),
    ),
    EmailCfg(
        id='EFTA00173881',
        author='US Secret Service',
        recipients=['Enterprise Vetting Center'],
        show_with_name=HOWARD_LUTNICK,
        truncate_to=800
    ),
    EmailCfg(
        id='EFTA00873541',
        description=f"Epstein says his neighbor {HOWARD_LUTNICK} (recently seen with {PRINCE_ANDREW}) is smart",
        show_with_name=HOWARD_LUTNICK,
    ),
    EmailCfg(id='EFTA02374900', description=f'article about {HOWARD_LUTNICK} real estate purchase'),
    EmailCfg(id='EFTA00685520', description=f'call with {HOWARD_LUTNICK}'),
    EmailCfg(id='EFTA00436468', description=f'call with {HOWARD_LUTNICK} after he goes overseas', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA00462693', description=f"Epstein gets a table for 10 at the dinner honouring {HOWARD_LUTNICK}"),
    EmailCfg(id='EFTA00398744', description=f"{HOWARD_LUTNICK} thanks Epstein for the island vacay"),
    EmailCfg(id='EFTA00474452', description=f"{HOWARD_LUTNICK} and {JEFFREY_EPSTEIN}, NIMBYs"),
    EmailCfg(id='EFTA00398719', description=f'{HOWARD_LUTNICK} visit to the island', truncate_to=2500),
    EmailCfg(id='EFTA00401065', description=f'{HOWARD_LUTNICK} visit to the island', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA00398853', description=f'{HOWARD_LUTNICK} visit to the island', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA00873540', description=f'{HOWARD_LUTNICK} and {PRINCE_ANDREW}'),
    EmailCfg(id='EFTA00443752', description=f"invitation from {HOWARD_LUTNICK}"),
    EmailCfg(id='EFTA00957552', description=f'thank you note for a $50,000 donation in honor of Tether banker {HOWARD_LUTNICK}'),
    EmailCfg(id='EFTA00970606', show_with_name=HOWARD_LUTNICK),
    EmailCfg(id='EFTA01778423', show_with_name=HOWARD_LUTNICK),
    # Jem Bendell
    EmailCfg(
        id='EFTA01005603',
        author=JEM_BENDELL,
        author_reason='sig',
        highlight_quote="if you are interested in blockchain and alternative currencies",
    ),
    EmailCfg(id='EFTA00630785', description='alternative currencies discussion'),
    EmailCfg(id='EFTA02724230', description='alternative currencies discussion', truncate_to=NO_TRUNCATE),
    # Jeremy Rubin
    EmailCfg(id='EFTA02466979', description='"AID Coin"'),
    EmailCfg(id='EFTA02343669', description='rumours that people are using bitcoin to exfiltrate capital from China'),
    # Joi Ito / Kyara
    DocCfg(id='024256', author=JOI_ITO, description=f"Internet & Society: The Technologies and Politics of Control"),
    EmailCfg(id='025598', is_interesting=False),
    EmailCfg(id='028847', description=f"the announcement of a hunt for Putin's money seems to greatly concern Epstein and {JOI_ITO}"),
    EmailCfg(id='026360', description=f"{JOI_ITO} writes to Epstein to thank him for providing funding for the bitcoin core development team"),
    EmailCfg(id='025603', description=f"Epstein funnels money from {ANDREW_FARKAS} to {MIT_MEDIA_LAB} / {JOI_ITO}", truncate_to=850),
    DocCfg(id='EFTA00805860', description=f"{JOI_ITO}'s Neoteny 3 fund investor update / portfolio"),
    DocCfg(id='EFTA01118268', description=f"{JOI_ITO}'s Neoteny 3 fund investor update", date='2015-06-30'),
    DocCfg(id='EFTA01116280', description=f"{KYARA_FUND} I LLC (Physical Graph Corporation) operating agreement with edits"),
    DocCfg(id='EFTA01108775', description=f"{KYARA_FUND} I LLC (Physical Graph Corporation) operating agreement"),
    DocCfg(id='EFTA00605699', description=f"{KYARA_FUND} II LLC incorporation papers"),
    DocCfg(id='EFTA01186455', description=f"{KYARA_FUND} II LLC operating agreement"),
    DocCfg(id='EFTA00584696', description=f"{KYARA_FUND} III LLC operating agreement"),
    EmailCfg(
        id='EFTA02376268',
        description=f"introduction to {JEREMY_RUBIN}",
        recipients=[JEFFREY_EPSTEIN, JEREMY_RUBIN, LINDA_STONE, None],
    ),
    EmailCfg(id='EFTA02342561', description=f"China, {REID_HOFFMAN}, bitcoin", is_interesting=True),
    EmailCfg(id='EFTA02601259', description=f"discussion of investments hidden through {JOI_ITO}"),
    EmailCfg(id='EFTA00989593', description=f'donations from {LEON_BLACK} to {MIT_MEDIA_LAB} / Digital Currency Initiative {QUESTION_MARKS}'),
    EmailCfg(id='EFTA00999549', description=f"{JOI_ITO} and {JEREMY_RUBIN} meet {LARRY_SUMMERS} to discuss bitcoin", is_interesting=True),
    EmailCfg(id='EFTA01752601', description=f"{JOI_ITO} and Epstein name their new fund Kyara"),
    EmailCfg(id='EFTA02703885', author=LINDA_STONE, author_reason='sig', description=f"{LINDA_STONE} introducing Epstein to {JEREMY_RUBIN}"),
    EmailCfg(id='EFTA02505439', description=f'summary of {KYARA_INVESTMENT} shell companies with {JOI_ITO}'),
    EmailCfg(id='EFTA01973301', recipients=[LINDA_STONE], author_reason='signature'),
    EmailCfg(id='EFTA00473175', truncate_to=1000),
    # Kushner
    DocCfg(id='EFTA00128987', description='suspicious activity report (SAR) about Kushner co. crypto payments to suspicious Russian person'),
    # Masha Drokova
    EmailCfg(
        id='EFTA01003115',
        author=MASHA_DROKOVA,
        author_reason='"masha" in quoted',
        description='"Dylan" is probably Dylan Love who wrote a story about Epstein and bitcoin arranged by Masha Drokova',
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(id='EFTA01010171'),
    EmailCfg(id='EFTA01010128'),
    # Misc
    DocCfg(
        id='EFTA02005667',
        author='Clearstone',
        date='2011-02-01',
        date_uncertain=True,
        description='Online Gaming Fund pitch deck',
        non_participants=[AUSTIN_HILL],
    ),
    DocCfg(
        id='EFTA01388197',
        attached_to_email_id='EFTA01388354',
        author=DEUTSCHE_BANK,
        date='2018-04-03',
        description='bitcoin and blockchain symposium',
    ),
    DocCfg(
        id='EFTA01074293',
        author='Jerry Brito, Houman Shadab, & Andrea Castillo',
        date='2014-04-10',
        description='discussion draft of "Bitcoin Financial Regulation" paper',
    ),
    DocCfg(
        id='EFTA00797937',
        author='John Pfeffer',
        date='2017-12-24',
        description="An (Institutional) Investor's Take on Cryptoassets",
    ),
    DocCfg(
        id='EFTA01612888',
        author='Kevin Peterson, Bammohan Deeduvanu, Pradip Kanjamala, and Kelly Boles',
        description='A Blockchain-Based Approach to Health Information Exchange Networks',
    ),
    DocCfg(
        id='EFTA02725909',
        date='2016-01-01',
        description=f'memo to NYDFS of NYC Bitcoin Exchange, Balaji Srinivisan & {ANDREW_FARKAS} on board',
        date_uncertain='mentions ethereum so must be after 2015-06',
    ),
    DocCfg(id='EFTA00811666', description='asset valuations of Epstein\'s holdings, includes "Coinbase via grat"', date='2018-01-31'),
    DocCfg(id='EFTA01734786', description='LedgerX Series B pitch deck'),
    DocCfg(id='EFTA00605996', description='Wedbush BUY rating on Digital Currency Group GBTC', is_interesting=False),
    EmailCfg(id='EFTA00867030', author='Kathy', description='discussion of a crypto token based on GDAX (whatever that means)', is_interesting=True),
    EmailCfg(id='EFTA01060993', description=f"Epstein says he knows \"a few\" guys who hold over $50 million in bitcoin", is_interesting=True),
    EmailCfg(id='EFTA01915234', description='discussion of crypto regulations', is_interesting=True),
    EmailCfg(id='EFTA01004753', description=f"founder of Layer1 is the only guy in crypto who doesn't want to meet Epstein (didn't last though)"),
    EmailCfg(id='EFTA02601503', description=f"discussion of investing in Layer1, an important crypto business"),
    EmailCfg(id='EFTA02517623', description=f"{VINCENZO_IOZZO} explains to Epstein how to deanonymize bitcoin", is_interesting=True),
    EmailCfg(id='EFTA00699275', description=f"'Fred' is probably Coinbase co-founder Fred Ehrsam"),
    EmailCfg(id='EFTA00830911', description='fundraising email for LedgerX which was later acquired by FTX for $298 million'),
    EmailCfg(id='EFTA01750652', description=f"discussion of using blockchains in the repo markets", is_interesting=True),
    EmailCfg(id='EFTA02002675', description=f"{JASON_CALACANIS} passes Epstein the names of the bitcoin core developers"),
    # Reid Hoffman
    EmailCfg(id='EFTA00820371', description='bank digital currencies article', is_interesting=True),
    # Russia
    EmailCfg(id='EFTA02591998', description='Epstein spoke to Vladimir Putin about digital currency', is_interesting=True),
    # SEC / NYDFS
    EmailCfg(id='EFTA00668932', description=f"pressing Farkas for a meeting with {BEN_LAWSKY_NYDFS}"),
    EmailCfg(id='EFTA01747752', description=f"Farkas delivering {BEN_LAWSKY_NYDFS}", truncate_to=700),
    EmailCfg(id='EFTA02588398', description=f"Epstein went to the Treasury Dept of the US to talk about bitcoin", is_interesting=True),
    EmailCfg(id='EFTA00987194', description=f"Epstein proposes {BEN_LAWSKY_NYDFS} get rid of sales tax on bitcoin", is_interesting=True),
    EmailCfg(id='EFTA02591315', description=f"{ANDREW_FARKAS} arranging for Epstein to meet {BEN_LAWSKY_NYDFS}", is_interesting=True, truncate_to=1900),
    EmailCfg(id='EFTA01002518', description=f"confirmation that Epstein did indeed meet {BEN_LAWSKY_NYDFS} to discuss a 'high yield product'"),
    EmailCfg(id='EFTA02587320', author=KATHRYN_RUEMMLER, description=f"Kathy Ruemmler, crypto bro-ette", is_interesting=True),
    EmailCfg(
        id='EFTA00357845',
        description=f"Epstein and {KATHRYN_RUEMMLER} meet with {BEN_LAWSKY_NYDFS} to discuss bitcoin",
        is_interesting=True,
        recipients=[LESLEY_GROFF],
        recipient_uncertain=True,
    ),
    # Sharia coin
    EmailCfg(id='032359', description='HBJ brings up "e-currency" (Sharia Coin, probably)'),
    EmailCfg(id='EFTA00964459', description=f'discussion of sharia compliant crypto token', is_interesting=True),
    EmailCfg(id='EFTA00990442', description=f"Epstein offers to cover all costs for Sharia Coin", is_interesting=True),
    EmailCfg(id='EFTA02396341', description='the Sharia Coin gambit', is_interesting=True),
    EmailCfg(id='EFTA01005117', description='announcement that the Stellar blockchain is Sharia compliant'),
    # Steven Sinofsky / a16z
    EmailCfg(id='EFTA01804670', highlight_quote='Andreessen really into this whole virtual money space', truncate_to=700),
    # Valar
    DocCfg(
        id='EFTA00591045',
        attached_to_email_id='EFTA01001339',
        author=VALAR_FUND,
        description='pitch deck',
        non_participants=[MASAYOSHI_SON],
    ),
    DocCfg(id='EFTA00810239', author=VALAR_FUND, description='pitch deck'),
    DocCfg(id='EFTA00810510', author=VALAR_FUND, description='Fall 2016 Update'),
    DocCfg(id='EFTA00810474', author=VALAR_FUND, description='Fall 2018 Update'),
    DocCfg(id='EFTA01121910', author=VALAR_VENTURES, description="contract", truncate_to=DEFAULT_TRUNCATE_TO),
    DocCfg(id='EFTA00808277', author=VALAR_VENTURES, description="contract", truncate_to=DEFAULT_TRUNCATE_TO),
    DocCfg(id='EFTA01088484', author=VALAR_VENTURES, description="contract", truncate_to=DEFAULT_TRUNCATE_TO),
    DocCfg(id='EFTA00591691', author=VALAR_VENTURES, description="contract", truncate_to=DEFAULT_TRUNCATE_TO),
    DocCfg(id='EFTA00810362', author=VALAR_VENTURES, description="investor questionnaire", truncate_to=DEFAULT_TRUNCATE_TO),
    EmailCfg(id='EFTA01001339', description=f"{PETER_THIEL} introduces Epstein to the {VALAR_VENTURES} founders"),
    # Vincenzo
    EmailCfg(id='EFTA00637023', description=f"discussion of getting around money laundering laws in places like Myanmar + Mongolia"),
    EmailCfg(id='EFTA02588723', description=f'discussion of crypto food stamps debit cards', is_interesting=True),
    EmailCfg(id='EFTA02588748', description=f'discussion of crypto food stamps debit cards', is_interesting=True, truncate_to=800),
    EmailCfg(id='EFTA02584771', description=f"discussion of decentralized prediction markets (e.g. Polymarket)", is_interesting=True),
    EmailCfg(id='EFTA01008242', description='Epstein passes on an investment in Radius'),
    EmailCfg(id='EFTA00995269', description=f"Epstein suggests Monaco and Vatican City as good places for crypto"),
    # ZCash / Madars Virza
    DocCfg(id='EFTA00811130', author=PERKINS_COIE, description='tax opinion on ZCash tokens'),
    DocCfg(id='EFTA00603348', description=f"Electric Coin Company created the untraceable crypto ZCash funded by {LARRY_SUMMERS}'s DCG"),
    DocCfg(id='EFTA00803405', description=f"Honeycomb Asset Management fund brochure", truncate_to=DEFAULT_TRUNCATE_TO),
    EmailCfg(id='EFTA02282357', author=DAPHNE_WALLACE, author_uncertain='could be Lesley'),
    EmailCfg(id='EFTA02283028', author=DAPHNE_WALLACE, author_uncertain='could be Lesley'),
    EmailCfg(id='EFTA02620980', description=f"{MADARS_VIRZA} says Tether was created to avoid anti-money laundering laws"),
    EmailCfg(id='EFTA01781741', description=f'{JOI_ITO} introduces Epstein to {MADARS_VIRZA} and the untraceable private crypto ZCash'),
    EmailCfg(id='EFTA02645742', description=f"tax implications of the untraceable 'privacy coin' ZCash", is_interesting=True),
    EmailCfg(
        id='EFTA02374960',
        description=f"Epstein says that he will fund a seat at MIT Media Lab for ZCash founder {MADARS_VIRZA}",
        is_interesting=True,
    ),
    # Unsorted
    EmailCfg(
        id='EFTA00096009',
        author='SDNY Cybercrimes',
        description='Epstein legal defense team requested bail hearing transcript of OneCoin fraudster Konstantin Ignatova',
        recipients=[USANYS],
    ),
    EmailCfg(id='EFTA00629471', author=JOHN_BROCKMAN, non_participants=[AUSTIN_HILL, 'David Geffen'], truncate_to=3000),
    EmailCfg(id='EFTA01762201', highlight_quote='indoctrinating kids into an economy', show_with_name=BOBBY_KOTICK),
    EmailCfg(id='EFTA02414991', description=f"Epstein signs up for World of Warcraft", truncate_to=350),
    EmailCfg(id='EFTA01388354', description=f"invitation to {DEUTSCHE_BANK} blockchain event with Mike Novogratz"),
    EmailCfg(id='EFTA01434500', description=f"everyone assumes Epstein's banker {PAUL_BARRETT} will want to know about the blockchain event"),
    EmailCfg(id='EFTA00993615', description=f"{MASHA_DROKOVA} explains the price of bitcoin can be manipulated if Epstein makes public comments"),
    EmailCfg(id='EFTA01784901', description=f"{JEREMY_RUBIN} has cashed multiple checks directly from Epstein", is_interesting=True),
    EmailCfg(
        id='EFTA01007544',
        description=f'{JEREMY_RUBIN} describes "grey area between pump and develop" when Epstein objects on ethical grounds',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA01748990',
        description=f"{AUSTIN_HILL} is upset that Ito and Epstein seem to have invested in Stellar and Ripple, competing blockchain ecosystems",
        is_interesting=True,
    ),
    EmailCfg(id='EFTA01943067', description=f'comments on {ARIANE_DE_ROTHSCHILD} and bitcoin', is_interesting=True),
    EmailCfg(id='EFTA00835324', recipients=[SERGEY_BELYAKOV], description='assessment of Mycelium bitcoin wallet'),
    EmailCfg(id='EFTA00368659', description=f"meeting with {REID_HOFFMAN} about bitcoin", is_interesting=True),
    EmailCfg(id='EFTA01039626'),
    EmailCfg(
        id='EFTA02035756',
        description=f"{AL_SECKEL} introduces Epstein to Bannon business partner {BROCK_PIERCE} of Tether/{BLOCKCHAIN_CAPITAL}",
        is_interesting=True,
    ),
    EmailCfg(id='EFTA02372964', description='an "ICO" or "initial coin offering" was a very popular type of crypto scam at this time'),
    EmailCfg(
        id='EFTA02177147',
        author=LINDA_STONE,
        author_uncertain='"Hi Linda"',
        description=f"Epstein planning a symposium \"on Alternative Money or Complementary Currency\" in 2012",
        is_interesting=True,
        recipients=[LESLEY_GROFF],
    ),
    EmailCfg(
        id='EFTA01965506',
        author=LINDA_STONE,
        author_reason='"iPhone word substitution" in signature, which is traced back to "Linda, thanks" in EFTA00961792',
        description='Barry Silbert became the CEO of Digital Currency Group, a huge US crypto fund w/Larry Summers on the board',
        is_interesting=True,
    ),
    EmailCfg(id='EFTA00899331', truncate_to=NO_TRUNCATE),
]


# All authors of documents in this category will be marked uninteresting
OTHER_FILES_FINANCE = [
    DocCfg(id='024631', author='Ackrell Capital', description=f"Cannabis Investment Report 2018", is_interesting=True),
    DocCfg(id='016111', author=BOFA_MERRILL, description=f"GEMs Paper #26 Saudi Arabia: beyond oil but not so fast", date='2016-06-30'),
    DocCfg(id='010609', author=BOFA_MERRILL, description=f"Liquid Insight Trump's effect on MXN", date='2016-09-22'),
    DocCfg(id='025978', author=BOFA_MERRILL, description=f"Understanding when risk parity risk Increases", date='2016-08-09'),
    DocCfg(id='014404', author=BOFA_MERRILL, description=f'Japan Investment Strategy Report', date='2016-11-18'),
    DocCfg(id='014410', author=BOFA_MERRILL, description=f'Japan Investment Strategy Report', date='2016-11-18'),
    DocCfg(id='014424', author=BOFA_MERRILL, description=f"Japan Macro Watch", date='2016-11-14'),
    DocCfg(id='014731', author=BOFA_MERRILL, description=f"Global Rates, FX & EM 2017 Year Ahead", date='2016-11-16'),
    DocCfg(id='014432', author=BOFA_MERRILL, description=f"Global Cross Asset Strategy - Year Ahead The Trump inflection", date='2016-11-30'),
    DocCfg(id='014460', author=BOFA_MERRILL, description=f"European Equity Strategy 2017", date='2016-12-01'),
    DocCfg(id='014972', author=BOFA_MERRILL, description=f"Global Equity Volatility Insights", date='2017-06-20'),
    DocCfg(id='014622', author=BOFA_MERRILL, description=f"Top 10 US Ideas Quarterly", date='2017-01-03'),
    DocCfg(id='023069', author=BOFA_MERRILL, description=f"Equity Strategy Focus Point Death and Taxes", date='2017-01-29'),
    DocCfg(id='014721', author=BOFA_MERRILL, description=f"Cause and Effect Fade the Trump Risk Premium", date='2017-02-13'),
    DocCfg(id='014887', author=BOFA_MERRILL, description=f"Internet / e-Commerce", date='2017-04-06'),
    DocCfg(id='014873', author=BOFA_MERRILL, description=f"Hess Corp", date='2017-04-11'),
    DocCfg(id='023575', author=BOFA_MERRILL, description=f"Global Equity Volatility Insights", date='2017-06-01'),
    DocCfg(id='014518', author=BOFA_WEALTH_MGMT, description=f'tax alert', date='2016-05-02'),
    DocCfg(id='029438', author=BOFA_WEALTH_MGMT, description=f'tax report', date='2018-01-02'),
    DocCfg(id='026668', author="Boothbay Fund Management", description=f"2016-Q4 earnings report signed by Ari Glass", is_interesting=True),
    DocCfg(id='024302', author='Carvana', description=f"form 14A SEC filing proxy statement", date='2019-04-23'),
    DocCfg(id='029305', author='CCH Tax', description=f"Briefing on end of Defense of Marriage Act", date='2013-06-27'),
    DocCfg(id='026794', author=DEUTSCHE_BANK, description=f"Global Political and Regulatory Risk in 2015/2016"),
    DocCfg(id='022361', author=DEUTSCHE_BANK_TAX_TOPICS, date='2013-05-01', attached_to_email_id='022359'),
    DocCfg(id='022325', author=DEUTSCHE_BANK_TAX_TOPICS, date='2013-12-20'),
    DocCfg(id='022330', author=DEUTSCHE_BANK_TAX_TOPICS, date='2013-12-20', description='table of contents'),
    DocCfg(id='019440', author=DEUTSCHE_BANK_TAX_TOPICS, date='2014-01-29'),
    DocCfg(id='024202', author=ELECTRON_CAPITAL_PARTNERS, description=f"Global Utility White Paper", date='2013-03-08'),
    DocCfg(id='022372', author='Ernst & Young', date='2016-11-09', description=f'2016 election report'),
    DocCfg(id='014532', author=GOLDMAN_INVESTMENT_MGMT, description=f"Outlook - Half Full", date='2017-01-01'),
    DocCfg(
        id='026909',
        attached_to_email_id='026893',
        author=GOLDMAN_INVESTMENT_MGMT,
        description=f"The Unsteady Undertow Commands the Seas (Temporarily)",
        date='2018-10-14',
    ),
    DocCfg(id='026944', author=GOLDMAN_INVESTMENT_MGMT, description=f"Risk of a US-Iran Military Conflict", date='2019-05-23'),
    DocCfg(id='018804', author='Integra Realty Resources', description=f"appraisal of going concern for IGY American Yacht Harbor Marina in {VIRGIN_ISLANDS}"),
    DocCfg(id='026679', author='Invesco', description=f"Global Sovereign Asset Management Study 2017"),
    DocCfg(
        id='033220',
        author='Joseph G. Carson',
        description=f"short economic report on defense spending under Trump",
        is_interesting=True,
    ),
    DocCfg(id='026572', author=JP_MORGAN, description=f"Global Asset Allocation report", date='2012-11-09'),
    DocCfg(id='030848', author=JP_MORGAN, description=f"Global Asset Allocation report", date='2013-03-28'),
    DocCfg(id='030840', author=JP_MORGAN, description=f"Market Thoughts"),
    DocCfg(id='022350', author=JP_MORGAN, description=f"tax efficiency of Intentionally Defective Grantor Trusts (IDGT)"),
    DocCfg(id='025242', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-04-09'),
    DocCfg(id='030010', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, attached_to_email_id='030006', date='2011-06-14'),
    DocCfg(id='030808', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-07-11'),
    DocCfg(id='025221', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-07-25'),
    DocCfg(id='025229', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-08-04'),
    DocCfg(id='030814', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-11-21'),
    DocCfg(id='024132', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-03-15'),
    DocCfg(id='024194', author=JP_MORGAN, description=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-10-22'),
    DocCfg(id='025296', author='Laffer Associates', description=f'report predicting Trump win', date='2016-07-06'),
    DocCfg(
        id='020824',
        author='Mary Meeker',
        date='2011-02-01',
        description=f"USA Inc: A Basic Summary of America's Financial Statements compiled",
    ),
    DocCfg(id='025551', author='Morgan Stanley', description=f'report about alternative asset managers', date='2018-01-30'),
    DocCfg(id='019856', author='Sadis Goldberg LLP', description=f"report on SCOTUS ruling about insider trading", is_interesting=True),
    DocCfg(id='025763', author='S&P', description=f"Economic Research: How Increasing Income Inequality Is Dampening U.S. Growth", date='2014-08-05'),
    DocCfg(id='024135', author=UBS, description=UBS_CIO_REPORT, date='2012-06-29'),
    DocCfg(id='025247', author=UBS, description=UBS_CIO_REPORT, date='2012-10-25'),
    DocCfg(id='026584', description="article about tax implications of disregarded entities", date='2009-07-01', is_interesting=True),
    DocCfg(id='024817', description="Cowen's CBD / Cannabis report", date='2019-02-25', is_interesting=True),
    DocCfg(
        id='012048',
        category=Neutral.PRESSER,
        description=f"Rockefeller Partners with Gregory J. Fleming to Create Independent Financial Services Firm and other articles",
        is_interesting=False,
    ),

    # DOJ
    DocCfg(id='EFTA00286949', author='Nathaniel August', description='Mangrove Partners valuation report', date='2016-11-03'),
    DocCfg(id='EFTA01078403', author=ATORUS, description='investment adviser uniform application', date='2014-05-14'),
    DocCfg(id='EFTA02690885', author=ATORUS, description='pitch deck'),
    DocCfg(id='EFTA00593276', author=EDMOND_DE_ROTHSCHILD, description='org chart', is_interesting=True),
    # Prop trading / HFT
    DocCfg(id='EFTA00611806', author='Adam Campbell', description='CEA, LLC High Liquidity Trading Program presentation'),
    DocCfg(id='EFTA01088824', author='Boothbay', description='Absolute Return Strategies Fund pitch deck'),
    DocCfg(id='EFTA00556664', author='Qarmin', description='high frequency trading pitch deck'),
]


OTHER_FILES_DIARY = [
    victim_diary('EFTA02731465', f"naming {JES_STALEY}, {TED_LEONSIS}, {GEORGE_VRADENBURG}, references tinkerbell"),
    victim_diary('EFTA02731420', f'naming {LARRY_SUMMERS}, {PRINCE_ANDREW}, Dan Snyder, {LEON_BLACK}, {TED_LEONSIS}'),
]


OTHER_FILES_FLIGHT_LOG = [
    DocCfg(id='022780'),
    DocCfg(id='022816'),
    DocCfg(id='EFTA00623147', author=DAVID_RODGERS, date='2016-06-30', date_uncertain='guess based on employment history'),
]


OTHER_FILES_GIRLS = [
    EmailCfg(id='025874', description=f"possibly about {VIRGINIA_GIUFFRE} {QUESTION_MARKS}"),
    EmailCfg(id='030609', duplicate_ids=['030495']),
    letter('EFTA00078198', 'Marsh Law Firm', [USANYS], "allegations of sexual abuse at Epstein's house", '2020-11-10'),
    DocCfg(id='EFTA00306033', author=SERGEY_BELYAKOV, description='Epstein Russian visa', show_full_panel=True),
    DocCfg(id='EFTA00014648', description='former employee "understood that all the girls were school girls"', show_full_panel=True),
    DocCfg(
        id='EFTA00077200',
        author='French Ministry of Justice',
        date='2020-07-08',
        description=f'allegations that {JEAN_LUC_BRUNEL} drugged a model and Epstein + Ghislaine assaulted a minor',
    ),
    DocCfg(
        id='EFTA00079597',
        author='French Ministry of Justice',
        description=f"allegations of sexual assault by {JEAN_LUC_BRUNEL}",
        date='2020-07-08',
    ),
    CommunicationCfg(
        id='EFTA01612733',
        author=MARIA_PRUSAKOVA,
        author_uncertain=True,
        comment='WhatsApp',
        # TODO: highlight_quote
        description=f'says being Epstein\'s lawyer would be "way better than supplying ladies", also discusses Medici Bank',
        show_full_panel=True,
    ),
    CommunicationCfg(
        id='EFTA01616933',
        description='"now im finding pussy for you" / "no one can beat your pussy network"',  # TODO: should be highlight_quote
        show_full_panel=True,
    ),
    EmailCfg(
        id='EFTA02339926',
        author=JULIA_SANTOS,
        author_uncertain='https://www.reddit.com/r/Epstein/comments/1qwbn5i/trafficker_julia_santos/',
        highlight_quote='very sweet and might be naughty t=o',
    ),
    EmailCfg(id='EFTA01781620', author=KIRA_DIKHTYAR, author_uncertain='"Sent from AOL Mobile Mail" in chain'),
    EmailCfg(id='EFTA01805304', author=KIRA_DIKHTYAR, author_reason='Jmail', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA01766199', author=KIRA_DIKHTYAR, author_reason='reply', truncate_to=NO_TRUNCATE),
    EmailCfg(
        id='033178',
        author=MARIA_PRUSAKOVA,
        author_reason=PRUSAKOVA_BERKELY,
        description='Masha Prusso asks about Zubair Khan, discusses recruiting girls for Epstein',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA00669538',
        author=MARIA_PRUSAKOVA,
        author_uncertain='discussion of "experiments"',
        description='blowjob instructions, sexual experiments',
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(
        id='EFTA02010589',
        author=MARIA_PRUSAKOVA,
        date='2012-01-31 9:16 PM',
        description=f'raunchy email mentioning "Sasha Grey guy", note {BORIS_NIKOLIC} and bgC3 in SMTP info at end',
        is_interesting=True,
        recipients=[JEFFREY_EPSTEIN],
    ),
    EmailCfg(
        id='EFTA00928879',
        author=MARIA_PRUSAKOVA,
        author_uncertain='sounds like Prusakova',
        description=f'raunchy email, "find fun girls"',
    ),
    EmailCfg(
        id='EFTA01841553',
        author=MARIA_PRUSAKOVA,
        author_uncertain=True,
        highlight_quote='being fucked in the ass hurts me a lot',
        truncate_to=900,
    ),
    EmailCfg(id='EFTA01990168', author=MARIA_PRUSAKOVA, author_uncertain='"experiments"', is_interesting=True),
    EmailCfg(id='EFTA00671662', author='Miranda', author_reason='quoted signature', description="yet another girl finder"),
    EmailCfg(id='EFTA02441035', author=STEVEN_VICTOR_MD, description="complaints about free medical treatment for Epstein's girls"),
    EmailCfg(
        id='EFTA00659941',
        author=SVETLANA_POZHIDAEVA,
        author_reason='https://tommycarstensen.com/epstein/findings.html#victim-diary-names-multiple-men',
        description=f'{SVETLANA_POZHIDAEVA} forwarding her intimate conversations with {JOSHUA_FINK} to Epstein (to what end?)',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA01844498',
        author=SVETLANA_POZHIDAEVA,
        author_reason='mentions Josh (Fink), BlackBerry signature',
        description=f"{JOSHUA_FINK} thinks Svetlana had an affair with Navalny {QUESTION_MARKS}",
    ),
    EmailCfg(
        id='EFTA01868066',
        # author=SVETLANA_POZHIDAEVA,
        # author_uncertain=f"{JOSHUA_FINK} + Sent from Blackberry",
        description=f'impersonating [someone] talking to {JOSHUA_FINK}',
        duplicate_ids=['EFTA01995523'],
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA01870453',
        author=SVETLANA_POZHIDAEVA,
        author_uncertain=f"{JOSHUA_FINK} texts",
        description=f'{JOSHUA_FINK} and {SVETLANA_POZHIDAEVA} discuss an abortion ("You have known you are preg for a week")',
    ),
    EmailCfg(id='EFTA01877224', author=SVETLANA_POZHIDAEVA, author_uncertain=f"{JOSHUA_FINK} texts"),
    EmailCfg(id='EFTA00937507', author=SVETLANA_POZHIDAEVA, author_uncertain=f"{JOSHUA_FINK} texts"),
    EmailCfg(
        id='EFTA01991293',
        author=SVETLANA_POZHIDAEVA,
        author_reason=f"convo about {JOSHUA_FINK} breakup",
        description=f'did {ELON_MUSK} date {SVETLANA_POZHIDAEVA} after she blackmailed {JOSHUA_FINK}? ("he asked 6 times if Elon [gave] me anything")',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA01998247',
        author=SVETLANA_POZHIDAEVA,
        author_uncertain='device signature',
        description=f'trying to recruit {ELON_MUSK}?',
        is_interesting=True,
        show_with_name=ELON_MUSK,
    ),
    EmailCfg(
        id='EFTA01772677',
        author=SVETLANA_POZHIDAEVA,
        author_uncertain='device signature',
    ),
    EmailCfg(id='EFTA02431535', author=UNKNOWN_GIRL),
    EmailCfg(id='EFTA01875607', author=UNKNOWN_GIRL),
    EmailCfg(id='EFTA00901581', author=UNKNOWN_GIRL),
    EmailCfg(id='EFTA02449477', author=UNKNOWN_GIRL, description='argument about finding girls for Epstein', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA01782788', author=UNKNOWN_GIRL, description='"I need 21-24, wiling to travel and work hard"', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA02027844', author=UNKNOWN_GIRL, description='permission to "fuck someone with a condom"', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA00763537', author=UNKNOWN_GIRL, highlight_quote="19 but I look younger than her"),
    EmailCfg(id='EFTA00738485', recipients=[STEVEN_VICTOR_MD], truncate_to=640),

    # Recipients
    EmailCfg(
        id='EFTA02223525',
        recipients=[ANNA_KASATKINA, BELLA_KLEIN, JANUSZ_BANASIAK],
        recipient_uncertain='https://www.reddit.com/r/Epstein/comments/1qwbn5i/trafficker_julia_santos/',
        truncate_to=800
    ),
    EmailCfg(
        id='EFTA01857628',
        recipients=[RENATA_BOLOTOVA],
        recipient_uncertain='https://x.com/FlippersUpNow/status/2023457206109155345',
        description='"igrushki" means "toys" in Russian',
    ),
    EmailCfg(
        id='EFTA00857669',
        description=f"{SANITA} is maybe the only great girl with right thinking",
        recipients=[SANITA],
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(
        id='EFTA02560884',
        description=f"is Epstein drafting {SVETLANA_POZHIDAEVA}'s responses to {JOSHUA_FINK} {QUESTION_MARKS}",
        recipients=[SVETLANA_POZHIDAEVA],
        recipient_uncertain=f"{JOSHUA_FINK} texts",
    ),
    EmailCfg(
        id='EFTA02543909',
        author_reason='p.selena@yahoo.com in replies',
        description=f'{SVETLANA_POZHIDAEVA}\'s relationship with "J" ({JOSHUA_FINK}?) and "B" {QUESTION_MARKS}',
        recipients=[SVETLANA_POZHIDAEVA],
    ),
    EmailCfg(
        id='EFTA00888467',
        description=f'very strange conversation about "Peter" (maybe {PETER_MANDELSON}?) and "mj" (maybe {HASSAN_JAMEEL}?)',
        is_interesting=True,
        recipients=[UNKNOWN_GIRL],
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(id='EFTA00897668', recipients=[UNKNOWN_GIRL], people=[JEAN_LUC_BRUNEL, JEFFREY_EPSTEIN, UNKNOWN_GIRL]),
    EmailCfg(id='EFTA00848644', recipients=[UNKNOWN_GIRL], is_interesting=True, description='"take a picture of your pussy"'),
    EmailCfg(
        id='EFTA01026268',
        author_reason='juliador89®mail.ru is unredacted',
        description=f"Epstein pressuring {YULIA_DOROKHINA} to find girls in Russia and send him nude pics and videos",
        recipients=[YULIA_DOROKHINA],
        truncate_to=3100,
    ),
    EmailCfg(id='EFTA00078209', description='allegations about Russian organized crime, sex trafficking', truncate_to=8500),
    EmailCfg(id='EFTA01648951', description=f'allegations against Trump, {HOWARD_LUTNICK}, Glen Dubin, {LEON_BLACK}, {JES_STALEY}'),
    EmailCfg(id='EFTA00950368', description='"any [girl] friends for me?"', truncate_to=NO_TRUNCATE),
    EmailCfg(
        id='EFTA00883738',
        description=f'Epstein recruiter {DASHA_GRUPMAN} looking to spend $50,000 to rent a townhouse for "diplomats"',
        show_with_name=DASHA_GRUPMAN,
    ),
    EmailCfg(
        id='EFTA00577409',
        date='2003-06-01',
        date_uncertain='just a guess, string is 4501 which is NULL in Microsoft Outlook',
        description='Epstein and Ghislaine discuss girl "from donad trumps party" who blackmailed [someone]',
    ),
    EmailCfg(
        id='EFTA01877084',
        comment='https://x.com/HansMahncke/status/2024351830998994979',
        description=f'Epstein and {JEAN_LUC_BRUNEL} "managing" {JOSHUA_FINK}\'s relationship with {SVETLANA_POZHIDAEVA}',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA00704924',
        description=f"stalking Josh Fink (attachment is pic of {JOSHUA_FINK} and {FILIPA_PEROVIC} who later married)",
        show_with_name=JOSHUA_FINK,
    ),
    EmailCfg(
        id='EFTA02217672',
        description=f"{DAVID_L_NEUHAUSER} is raising money for a {JOSHUA_FINK} fund, promises Epstein he won't reveal they're talking",
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA01907281',
        description=f"Epstein asks about {JOSHUA_FINK}, pretends it's because {TANCREDI_MARCHIOLO} asked *him* (Epstein asked Marchiolo)",
        show_with_name=JOSHUA_FINK,
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA02007083',
        description=f"{BORIS_NIKOLIC} encourages {KIMBAL_MUSK} to ditch his girlfriend for Epstein's girl {JENNIFER_KALIN} (and he says yes)",
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(
        id='EFTA00412260',
        author=LESLEY_GROFF,
        date='2012-05-25 19:51:20',
        description=f'Epstein really wants "*your friend*" (emphasis {LESLEY_GROFF}\'s) to meet {PETER_MANDELSON}',
        truncate_to=4_000,
    ),
    EmailCfg(id='EFTA01047249', author=NADIA_MARCINKO, author_reason='Miro, https://archive.ph/Qa6vU#selection-1621.160-1621.184'),

    # Quotes
    EmailCfg(
        id='EFTA02504370',
        highlight_quote=f'lovely girl with financial troubles',
        recipients=[KIRA_DIKHTYAR],
        recipient_uncertain='"Sent from AOL Mobile Mail"',
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(
        id='EFTA01022353',
        highlight_quote='she said she was 14-15 yo',
        description='(George Models is basically a porn site)',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA01885139',
        description=f'({JENNIFER_KALIN}, Epstein\'s girl whom {KIMBAL_MUSK} soon dated)',
        highlight_quote='Kimbal really like Jen',
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA02415420',
        highlight_quote="I have a friend of Putin,s",
        is_interesting=True,
    ),
    EmailCfg(id='EFTA01965732', highlight_quote='facilictating his illicit trysts, with married women, to being asked to provide adderall fro bridge tournamnts'),
    EmailCfg(id='EFTA01768670', highlight_quote='find girls for the agency', description=f'but {BORIS_NIKOLIC} is a "biotech investor"...'),
    EmailCfg(id='EFTA01905320', highlight_quote='girls and i are going to see elon musk at space x tomorrow', is_interesting=True),
    EmailCfg(id='EFTA01803353', highlight_quote='having problems with regina', description='(Ramsey?)'),
    EmailCfg(id='EFTA01858707', highlight_quote='How is the marriage plan going'),
    EmailCfg(id='EFTA00950394', highlight_quote='how old will you go?'),
    EmailCfg(id='EFTA02499884', highlight_quote='I gave another girl to kimball and he is thrilled', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA02557757', highlight_quote="I have a girl Sana working half time/who by the way you'd like"),
    EmailCfg(id='EFTA00771856', highlight_quote="I know 23 is on the old side for you", is_interesting=True),
    EmailCfg(id='EFTA01974447', highlight_quote='I know you are going to meet putin on the 20th', is_interesting=True),
    EmailCfg(id='EFTA01767237', highlight_quote='is 24 too old for you?', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA00854166', highlight_quote='kazak contract will be ready for your review', is_interesting=True, truncate_to=1100),
    EmailCfg(
        id='EFTA00878421',
        highlight_quote="said that she felt gods presence next to her when she was in bed",
        is_interesting=True,
        recipients=[NADIA_MARCINKO],
        recipient_uncertain='https://archive.ph/Qa6vU',  # https://www.nybooks.com/articles/2026/03/26/the-devil-himself-jeffrey-epstein-enright/
    ),
    EmailCfg(id='EFTA00894079', highlight_quote='say hi to Snow White'),
    EmailCfg(id='EFTA00775255', highlight_quote='she is 20 years old but she looks younger', non_participants=[BROCK_PIERCE]),
    EmailCfg(id='EFTA02387676', highlight_quote="thats the closest i get to karyna providing me new pussy"),
    EmailCfg(id='EFTA00908180', highlight_quote='two cinderellas'),
    EmailCfg(id='EFTA01930285', highlight_quote='ukraine upheaval should provide many opportunites'),
    EmailCfg(id='EFTA00751119', highlight_quote='Valdson to teach girls how to serve'),
    EmailCfg(id='EFTA01995972', highlight_quote='you are meeting elon tmr for lunch'),
    EmailCfg(id='EFTA01998027', highlight_quote="What day/night will be the wildest party on your island?", is_interesting=True),
    EmailCfg(id='EFTA01930501', highlight_quote="Your littlest girl was a little naughty"),
    EmailCfg(id='DropSite 2006-05-29 1329', highlight_quote='I am giving the little girl a modeling\n> lesson'),

    # Descriptions
    EmailCfg(id='EFTA01816788', description=f"Russian girl for {PRINCE_ANDREW}"),
    EmailCfg(id='EFTA00572157', description='translation: "Congratulations on the new addition!!! What did you name the little miracle?"'),
    EmailCfg(id='EFTA02559808', description=f"{EVA_DUBIN} delivering amphetamines (adderall) to Epstein", is_interesting=True, truncate_to=200),
    EmailCfg(id='EFTA01840103', description="Epstein apparently suggesting amphetamines (adderall)", is_interesting=True),
    EmailCfg(id='EFTA01987855', description=f'Epstein, Brunel, and {SULTAN_BIN_SULAYEM} very interested in a Liberian sex scandal'),
    EmailCfg(id='EFTA01817903', description=f'Epstein, Brunel, and {SULTAN_BIN_SULAYEM} sharing news of a Liberian sex scandal', is_interesting=True),
    EmailCfg(id='EFTA01818540', description=f'Epstein forwarding news of the Liberian sex scandal to {JES_STALEY}'),
    EmailCfg(id='EFTA01140210', description='Epstein asks about fake Instagram followers', is_interesting=True),
    EmailCfg(id='EFTA00937981', description=f"Epstein looking for {JOSHUA_FINK} (again)"),
    EmailCfg(id='EFTA00668344', description=f"Epstein looking for {JOSHUA_FINK} (again)"),
    EmailCfg(id='EFTA01856467', description=f"Epstein looking for {JOSHUA_FINK} (again)", truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA01854125', description=f'Epstein says to {HENRY_JARECKI} "you torture, and mistreat each" girl'),
    EmailCfg(id='EFTA01936438', description=f'Epstein\'s standard password might be "MVEMJSNUP"', is_interesting=True),
    EmailCfg(id='EFTA01953412', description=f'{EVA_DUBIN} suggests Epstein endow "The Epstein Floor For Women" at Mt. Sinai'),
    EmailCfg(id='EFTA00658028', description=f'{FAITH_KATES} trying to get a modeling contract for "Regina"?'),
    EmailCfg(id='EFTA00855566', description=f"introducing {SANITA}", truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA01145923', description=f"{JEAN_LUC_BRUNEL} modeling contract for {MC2_MODEL_MGMT}"),
    EmailCfg(id='EFTA01660651', description='list of Trump accusers', is_interesting=True),
    EmailCfg(id='EFTA02609062', description=f"{MASHA_DROKOVA} is assembling a team", is_interesting=True),
    EmailCfg(id='EFTA02557291', description='possibly recruiting girls'),
    EmailCfg(
        id='EFTA01811230',
        description=f'"Renat" is probably {RENATA_BOLOTOVA}, {REDACTED} might be "Irina" or {SVETLANA_POZHIDAEVA}',
        duplicate_ids=['EFTA00732294'],
    ),
    EmailCfg(id='EFTA00901905', description="smoking in the house oh no!"),
    EmailCfg(id='EFTA00914505', description=f'{SVETLANA_POZHIDAEVA} and {JOSHUA_FINK}...', duplicate_ids=['EFTA01999588']),
    EmailCfg(id='EFTA01798715', description=f"taking an interest in {JOSHUA_FINK}'s investments in Eritrea in between hair gigs"),
    EmailCfg(id='EFTA00631762', description="visa problems for Epstein's South African friend"),
    EmailCfg(
        id='EFTA02434682',
        description=f"Epstein and {JEAN_LUC_BRUNEL} courting a finance bro with women",
        is_interesting=True,
        truncate_to=1500,
    ),
    EmailCfg(
        id='EFTA00927927',
        description=f"reads like {RENATA_BOLOTOVA} talking about recruiting girls for Epstein",
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA01745650',
        author=KIRA_DIKHTYAR,
        author_uncertain='AOL signature',
        description=f'{SANITA} is mad at Epstein (and "makes lists")',
        show_with_name=SANITA,
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(id='EFTA00376832', show_with_name=MARIANA_IDZKOWSKA),
    EmailCfg(id='EFTA00743526', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA02664956', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA00689698', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA02702141', truncate_to=NO_TRUNCATE, comment=ELON_MUSK),
    EmailCfg(id='EFTA00819508', truncate_to=NO_TRUNCATE, comment=JULIA_SANTOS),
    EmailCfg(id='EFTA00460312', truncate_to=NO_TRUNCATE, comment=JULIA_SANTOS),
    EmailCfg(id='EFTA00878255', comment=BORIS_NIKOLIC),
    EmailCfg(id='EFTA02551185', comment=BORIS_NIKOLIC),
    EmailCfg(id='EFTA02538269', comment=BORIS_NIKOLIC, duplicate_ids=['EFTA01866636']),
    EmailCfg(id='EFTA00736518', comment=JES_STALEY + ' beauty and the beast'),
    EmailCfg(id='EFTA02344845', comment=JULIA_SANTOS),
    EmailCfg(id='EFTA02491007', comment=JULIA_SANTOS),
    EmailCfg(id='EFTA00633284', comment=JULIA_SANTOS),
    EmailCfg(id='EFTA00664521', comment=JULIA_SANTOS),
    EmailCfg(id='EFTA00997666', comment=JULIA_SANTOS),
    EmailCfg(id='EFTA00964428', comment=JULIA_SANTOS + ' Valdson'),
    EmailCfg(id='EFTA02398135', comment=JULIA_SANTOS + ' "Sochi"'),
    EmailCfg(id='EFTA00766770'),
]


OTHER_FILES_GOVERNMENT = [
    DocCfg(
        id='024117',
        description=f"anti-money laundering (AML), Bank Secrecy Act (BSA), & terrorist financing (CFT) US law FAQ",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA00315076',
        date='2008-06-01',
        date_uncertain=True,
        description=f"visitor list during Epstein's 2009 incarceration in {PALM_BEACH}",
        show_full_panel=True,
    ),
    DocCfg(
        id='EFTA00306074',
        date='2008-06-01',
        date_uncertain=True,
        description=f"approved mail list during Epstein's 2009 incarceration in {PALM_BEACH}",
        show_full_panel=True,
    ),
    DocCfg(id='EFTA00109783', author=BUREAU_OF_PRISONS, description='prisoner assignments', date='2019-08-03'),
    DocCfg(id='EFTA00035921', author=BUREAU_OF_PRISONS, description="Lieutenant's Logs", date='2019-08-06'),
    DocCfg(id='EFTA00120617', author=BUREAU_OF_PRISONS, description='"Prisoner Remand or Order to Deliver" forms', date='2019-07-30'),
    DocCfg(id='EFTA00109163', author=BUREAU_OF_PRISONS, description='various Metropolitan Correctional Center forms showing Konstantin Ignatov', date='2019-08-08', is_interesting=True),
    DocCfg(id='EFTA00109654', author=BUREAU_OF_PRISONS, description='roster of inmates at Metropolitan Correctional Center', date='2019-08-08'),
    DocCfg(id='EFTA00108533', author=BUREAU_OF_PRISONS, description='roster of inmates at Metropolitan Correctional Center', date='2019-07-23'),
    DocCfg(id='EFTA00108552', author=BUREAU_OF_PRISONS, description='roster of inmates at Metropolitan Correctional Center', date='2019-07-23'),
    DocCfg(id='EFTA00039153', author=BUREAU_OF_PRISONS, description='List of Exhibits, Chapter 2', date='2019-01-06'),
    DocCfg(id='EFTA00039025', author=BUREAU_OF_PRISONS, description="report on death of Jeffrey Epstein", is_interesting=True),
    DocCfg(id='EFTA00039190', author=BUREAU_OF_PRISONS, description='Special Housing Units', date='2016-11-23', is_interesting=False),
    DocCfg(id='EFTA00120459', author=BUREAU_OF_PRISONS, replace_text_with='handwritten log of prisoner movements', date='2019-08-09'),
    DocCfg(id='EFTA00039227', author=BUREAU_OF_PRISONS, replace_text_with='Inmate Discipline Program Statement'),
    DocCfg(id='EFTA00039295', author=BUREAU_OF_PRISONS, replace_text_with='Inmate Telephone Privileges Program Statement'),
    DocCfg(id='EFTA00039312', author=BUREAU_OF_PRISONS, replace_text_with='Program Statement / Memo about BOP Pharmacy Program'),
    DocCfg(id='EFTA00039351', author=BUREAU_OF_PRISONS, replace_text_with='Program Statement / Memo about BOP Pharmacy Program'),
    DocCfg(id='EFTA00039156', author=BUREAU_OF_PRISONS, replace_text_with='Standards of Employee Conduct'),
    DocCfg(
        id='EFTA00164939',
        author=DOJ,
        date='2025-09-01',
        date_uncertain='approximate',
        description='Powerpoint summary of Child Sex Trafficking Task Force Epstein investigation',
        is_interesting=True,
    ),
    DocCfg(id='EFTA02731200', author=DOJ, description="memo about potential prosecution of Epstein's assistant"),
    DocCfg(id='EFTA02731082', author=DOJ, description="memo about investigation into Epstein's co-conspirators"),
    DocCfg(id='EFTA02730741', author=DOJ, date='2025-05-01', date_uncertain=True, description="Evidence list for 50D-NY-3027571 Filtering On 'Type(s): 1B'"),
    DocCfg(id='EFTA02730486', author=DOJ, date='2025-05-01', date_uncertain=True, description="Evidence list for 50D-NY-3027571 Filtering On '1A'"),
    DocCfg(id='EFTA00040006', author=DOJ, date='2019-08-27', description='Personal History of Defendant Jeffrey Epstein + grand jury indictment'),
    DocCfg(id='EFTA02731226', author=DOJ, date='2021-03-14', description=f'memo seeking authorization to charge {GHISLAINE_MAXWELL} with additional offenses'),
    DocCfg(
        id='EFTA01246710',
        author=FBI,
        description="interview where Epstein's chef says Donald Trump came to Epstein's house for dinner",
        truncate_to=(6000, 7500),
    ),
    DocCfg(
        id='EFTA00174375',
        author=FBI,
        date='2022-11-18',
        description=f"interview of {LUKE_D_THORBURN} with a lot of takes on Epstein, China, and {STEVE_BANNON}",
    ),
    DocCfg(
        id='EFTA00159321',
        author=FBI,
        description='interview re: Paolo Zampolli, Epstein assaults, and the possibility Epstein introduced Melania to Donald Trump',
    ),
    # https://www.bbc.com/news/articles/c6271ngl014o
    DocCfg(
        id='EFTA01660676',
        author=FBI,
        description='tip about recently convicted rapists Tal and Oren Alexander at Epstein\'s house',
        show_full_panel=True,
    ),
    DocCfg(id='EFTA02858481', author=FBI, description='interview with victim Jennifer Aros'),
    DocCfg(id='EFTA00101927', author=FBI, description=f'interview with someone who mentions au pair of Glenn and {EVA_DUBIN} held against her will'),
    DocCfg(id='EFTA00247131', author=FBI, description='search warrant for New York house', date='2019-07-07'),
    DocCfg(id='EFTA01249591', author=FBI, description=f"allegations against {HENRY_JARECKI}"),
    DocCfg(id='EFTA00081226', author=FBI, description='interview with minor victim'),
    DocCfg(id='EFTA00038915', author=FBI, description='interview with minor victim who said Epstein knew she was 14'),
    DocCfg(id='EFTA00023055', author=FBI, description="evidence of notes left about newly recruited underage girls by girls giving massages"),
    DocCfg(id='EFTA00222943', author=FBI, description=f"agent believes computers were removed from Epstein's residence"),
    DocCfg(id='EFTA00020506', author=FBI, description='"chauffeur told Epstein \'I have something on you, remember what I buried!\'"', show_full_panel=True),
    DocCfg(id='EFTA00084614', author=PALM_BEACH_POLICE, description='incident report detailing the investigation into Jeffrey Epstein'),
    DocCfg(id='EFTA00007893', author=PALM_BEACH_POLICE, description=f"receipts, notes, bank statements of {GHISLAINE_MAXWELL}"),
    DocCfg(id='EFTA00005569', author=PALM_BEACH_POLICE, replace_text_with='photo lineup featuring Epstein', date='2005-03-17'),
    DocCfg(id='EFTA01227877', description='multi entry visa for the Russian Federation', date='2018-06-25', show_full_panel=True),
    DocCfg(id='EFTA00128379', description='analysis of two of Epstein\'s desktop computers', date='2019-01-06', is_interesting=True),
    DocCfg(id='EFTA02730274', description='evidence inventory that appears to have since been deleted from the DOJ website'),
    DocCfg(id='EFTA00263284', description='notes about deceit and sexual manipulation by Australian professor Vincent Bulone', is_interesting=True),
    DocCfg(id='EFTA00001884', description='photo of letter from Virgin Islands DOJ to Epstein', date='2019-03-14'),
    DocCfg(id='EFTA00074744', description="USVI court filing about Epstein will and estate"),
    DocCfg(id='EFTA00007157', description='victim list and police log'),
    fbi_defense_witness('EFTA02730267', 'Malcolm Grumbridge', '2022-04-14'),
    fbi_defense_witness('EFTA02730271', REDACTED, '2022-03-22'),
    fbi_defense_witness('EFTA02730477', 'Roderic Alexander', '2022-01-19'),
    letter('EFTA00098456', PAUL_G_CASSELL, ['Scotland Yard'], 'International Sex Trafficking by Jeffrey Epstein, contains court filings'),

    # Emails
    EmailCfg(
        id='EFTA00129096',
        date='2025-04-03 7:13:35 PM',
        description=f'background check on Tim Draper and {MASHA_DROKOVA}',
        show_full_panel=True,
        truncate_to=NO_TRUNCATE,  # TODO this shouldn't be necessary?
    ),
    EmailCfg(id='EFTA02730483', author=FBI, date='2023-07-11T08:25:00', date_uncertain='actually reply timestamp'),
    EmailCfg(id='EFTA02731552', author=FBI, recipients=[USANYS], date='2021-05-26 16:12:00', recipient_uncertain=True),
    EmailCfg(id='EFTA00039971', author=FBI, recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA00037683', description=f"tip that the murder of DC Madam Jeanne Palfrey might be connected to Epstein's network"),
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
    DocCfg(id='031293'),
    # Completely redacted DOJ emails, no timestamp at all
    DocCfg(id='EFTA02731726'),
    DocCfg(id='EFTA02731728'),
]


OTHER_FILES_LEGAL = [
    DocCfg(id='017789', author=ALAN_DERSHOWITZ, description=f'letter to {HARVARD} Crimson complaining he was defamed'),
    DocCfg(id='011908', author=BRUNEL_V_EPSTEIN, description=f"court filing"),
    DocCfg(id='017603', author=DAVID_SCHOEN, description=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='017635', author=DAVID_SCHOEN, description=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='016509', author=DAVID_SCHOEN, description=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='017714', author=DAVID_SCHOEN, description=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(
        id='010757',
        author=EDWARDS_V_DERSHOWITZ,
        description=f"plaintiff response to Dershowitz Motion to Determine Confidentiality of Court Records",
        date='2015-11-23',
    ),
    DocCfg(
        id='010887',
        author=EDWARDS_V_DERSHOWITZ,
        description=f"Dershowitz Motion for Clarification of Confidentiality Order",
        date='2016-01-29',
    ),
    DocCfg(
        id='015590',
        author=EDWARDS_V_DERSHOWITZ,
        description=f"Dershowitz Redacted Motion to Modify Confidentiality Order",
        date='2016-02-03',
    ),
    DocCfg(
        id='015650',
        author=EDWARDS_V_DERSHOWITZ,
        description=f"Giuffre Response to Dershowitz Motion for Clarification of Confidentiality Order",
        date='2016-02-08',
    ),
    DocCfg(id='010566', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, description=f"Statement of Undisputed Facts", date='2010-11-04'),
    DocCfg(id='012707', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, description=f"Master Contact List - Privilege Log", date='2011-03-22'),
    DocCfg(id='012103', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, description=f"Telephone Interview with {VIRGINIA_GIUFFRE}", date='2011-05-17'),
    DocCfg(id='029315', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, description=f"Plaintiff Motion for Summary Judgment by {JACK_SCAROLA}", date='2013-09-13'),
    DocCfg(id='013304', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, description=f"Plaintiff Response to Epstein's Motion for Summary Judgment", date='2014-04-17'),
    DocCfg(id='017792', author=GIUFFRE_V_DERSHOWITZ, description=f"article about {ALAN_DERSHOWITZ}'s appearance on Wolf Blitzer"),
    DocCfg(id='017767', author=GIUFFRE_V_DERSHOWITZ, description=f"article about {ALAN_DERSHOWITZ} working with {JEFFREY_EPSTEIN}"),
    DocCfg(id='017796', author=GIUFFRE_V_DERSHOWITZ, description=f"article about {ALAN_DERSHOWITZ}"),
    DocCfg(id='017935', author=GIUFFRE_V_DERSHOWITZ, description=f"defamation complaint", date='2019-04-16'),
    DocCfg(id='017824', author=GIUFFRE_V_DERSHOWITZ, description=f"{MIAMI_HERALD} article by {JULIE_K_BROWN}"),
    DocCfg(
        id='017818',
        author=GIUFFRE_V_DERSHOWITZ,
        description=f"{MIAMI_HERALD} article about accusations against {ALAN_DERSHOWITZ} by {JULIE_K_BROWN}",
        date='2018-12-27',
    ),
    DocCfg(id='017800', author=GIUFFRE_V_DERSHOWITZ, description=f'{MIAMI_HERALD} "Perversion of Justice" by {JULIE_K_BROWN}'),
    DocCfg(id='022237', author=GIUFFRE_V_DERSHOWITZ, description=f"partial court filing with fact checking questions?"),
    DocCfg(id='016197', author=GIUFFRE_V_DERSHOWITZ, description=f"response to Florida Bar complaint by {ALAN_DERSHOWITZ} about David Boies from {PAUL_G_CASSELL}"),
    DocCfg(id='017771', author=GIUFFRE_V_DERSHOWITZ, description=f'Vanity Fair article "The Talented Mr. Epstein" by Vicky Ward', date='2011-06-27'),
    DocCfg(id='014118', author=GIUFFRE_V_EPSTEIN, description=f"Declaration in Support of Motion to Compel Production of Documents", date='2016-10-21'),
    DocCfg(id='014652', author=GIUFFRE_V_MAXWELL, description=f"Complaint", date='2015-04-22'),
    DocCfg(id='015529', author=GIUFFRE_V_MAXWELL, description=f"Defamation Complaint", date='2015-09-21'),
    DocCfg(
        id='014797',
        author=GIUFFRE_V_MAXWELL,
        date='2017-03-17',
        description=f"Declaration of {LAURA_A_MENNINGER} in Opposition to Plaintiff's Motion",
    ),
    DocCfg(id='011304', author=GIUFFRE_V_MAXWELL, description=f"Oral Argument Transcript", date='2017-03-17'),
    DocCfg(
        id='014788',
        author=GIUFFRE_V_MAXWELL,
        date='2017-03-17',
        description=f"Maxwell Response to Plaintiff's Omnibus Motion in Limine",
        duplicate_ids=['011463'],
    ),
    DocCfg(
        id='025937',
        author=JANE_DOE_V_EPSTEIN_TRUMP,
        description=f'Affidavit of Tiffany Doe describing Jane Doe being raped by Epstein and Trump',
        date='2016-06-20',
    ),
    DocCfg(id='025939', author=JANE_DOE_V_EPSTEIN_TRUMP, description=f'Affidavit of Jane Doe describing being raped by Epstein', date='2016-06-20'),
    DocCfg(id='013489', author=JANE_DOE_V_EPSTEIN_TRUMP, description=f'Affidavit of {BRAD_EDWARDS}', date='2010-07-20'),
    DocCfg(id='029398', author=JANE_DOE_V_EPSTEIN_TRUMP, description=f'article in Law.com'),
    DocCfg(id='026854', author=JANE_DOE_V_EPSTEIN_TRUMP, description=f"Civil Docket"),
    DocCfg(id='026384', author=JANE_DOE_V_EPSTEIN_TRUMP, description=f"Complaint for rape and sexual abuse", date='2016-06-20', attached_to_email_id='029837'),
    DocCfg(id='029257', author=JANE_DOE_V_EPSTEIN_TRUMP, description=f'allegations and identity of plaintiff Katie Johnson', date='2016-04-26'),
    DocCfg(id='032321', author=JANE_DOE_V_EPSTEIN_TRUMP, description=f"Notice of Initial Conference", date='2016-10-04'),
    DocCfg(id='010735', author=JANE_DOE_V_USA, description=f"Dershowitz Reply in Support of Motion for Limited Intervention", date='2015-02-02'),
    DocCfg(id='014084', author=JANE_DOE_V_USA, description=f"Jane Doe Response to Dershowitz's Motion for Limited Intervention", date='2015-03-24'),
    DocCfg(id='023361', author=JASTA_SAUDI_LAWSUIT, description=f"legal text and court documents", date='2012-01-20'),
    DocCfg(id='017830', author=JASTA_SAUDI_LAWSUIT, description=f"legal text and court documents"),
    DocCfg(id='017904', author=JASTA_SAUDI_LAWSUIT, description=f"Westlaw search results", date='2019-01-01'),
    DocCfg(id='014037', author='Journal of Criminal Law and Criminology', description=f"article on {CVRA}"),
    DocCfg(
        id='029416',
        author="National Enquirer / Radar Online v. FBI",
        description=f"FOIA lawsuit filing",
        date='2017-05-25',
        duplicate_ids=['029405']
    ),
    DocCfg(
        id='016420',
        author=NEW_YORK_V_EPSTEIN,
        description=f"New York Post Motion to Unseal Appellate Briefs",
        date='2019-01-11',
    ),
    DocCfg(id='028540', author='SCOTUS', description=f"decision in Budha Ismail Jam et al. v. INTERNATIONAL FINANCE CORP"),
    DocCfg(id='012197', author='SDFL', description=f"response to {JAY_LEFKOWITZ} on Epstein Plea Agreement Compliance"),
    DocCfg(id='022277', description=f"text of National Labour Relations Board (NLRB) law", is_interesting=False),
    fbi_report('019352', f"{FBI_REPORT} containing clippings of various press items"),
    fbi_report('021434', is_valid_for_name_scan=False),
    fbi_report(
        '018872',
        non_participants=[
            BILL_GATES,
            BILL_RICHARDSON,
            EDUARDO_ROBLES,
            'Eliot Spitzer',
            GERALD_LEFCOURT,
            GLENN_DUBIN,
            JEAN_LUC_BRUNEL,
            JOI_ITO,
            LARRY_SUMMERS,
            LAWRANCE_VISOSKI,  # Just bc his deposition comes soon after
            MARK_EPSTEIN,
            MARTIN_NOWAK,
            MORTIMER_ZUCKERMAN,
            PRINCE_ANDREW,
            SECURITIES_AND_EXCHANGE_COMMISSION,
            STEVEN_HOFFENBERG,
            SVETLANA_POZHIDAEVA
        ],
    ),
    fbi_report('021569'),
    fbi_report('EFTA01688746'),
    fbi_report('EFTA00090314', f'tips about Jared Kushner, Ivanka Trump, Chabad, {ALAN_DERSHOWITZ}, etc.', is_interesting=True),
    fbi_report(
        'EFTA00129085',
        'wiretap report linking phone number in John Gotti / Gambino / Michael Bilotti investigation to number in Epstein investigation',
        is_interesting=True,
    ),

    # legal letters
    letter(
        '019297',
        f"{ALAN_DERSHOWITZ}'s lawyer Andrew G. Celli",
        [STANLEY_POTTINGER, PAUL_G_CASSELL, LAURA_A_MENNINGER, 'Sigrid S. McCawley'],
        f"threatening sanctions re: {GIUFFRE_V_MAXWELL}",
    ),
    letter(
        id='026793',
        author=f"Mintz Fraade ({STEVEN_HOFFENBERG}'s lawyers)",
        date='2018-03-23',
        description=f"offering to take over Epstein's business and resolve his legal issues",
        recipients=[DARREN_INDYKE],
    ),
    letter(
        id='020662',
        author=f"Mishcon de Reya ({ALAN_DERSHOWITZ}'s UK lawyers)",
        description=f"threatening libel lawsuit",
        recipients=['Daily Mail'],
    ),
    letter('010560', GLORIA_ALLRED, [SCOTT_J_LINK], "alleging abuse of a girl from Kansas", '2019-06-19'),
    letter('028965', MARTIN_WEINBERG, ['ABC / Good Morning America'], "threatening libel lawsuit", duplicate_ids=['028928']),
    letter('031447', MARTIN_WEINBERG, ['Melanie Ann Pustay', "Sean O'Neill"], "re: Epstein FOIA request", '2015-08-19'),
    starr_letter('025353', '2008-05-19', ['010723', '019224'], 'redacted', non_participants=[LANDON_THOMAS]),
    starr_letter('025704', '2008-05-27', ['010732', '019221'], 'redacted'),
    starr_letter('012130', '2008-06-19', ['012135'], non_participants=[LESLEY_GROFF]),

    # DOJ files
    DocCfg(id='EFTA01106135', author=BILL_GATES, description=f"gives Epstein power to negotiate on behalf of {BORIS_NIKOLIC}"),
    DocCfg(id='EFTA01112265', author=EDWARDS_V_DERSHOWITZ, description='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA01125109', author=EDWARDS_V_DERSHOWITZ, description='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA01139414', author=EDWARDS_V_DERSHOWITZ, description='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA00211168', author=JANE_DOE_V_EPSTEIN_TRUMP, description='Epstein employee affidavit alleging sexual assaults'),
    DocCfg(id='EFTA00177201', author=JANE_DOE_V_USA, description='court docket and many filings', is_interesting=True),
    DocCfg(id='EFTA00590940', author=JANE_DOE_V_USA, description='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA01081391', author=JANE_DOE_V_USA, description='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA00727684', author=f"{REDACTED} v. {JEFFREY_EPSTEIN}", description='sworn testimony, list of co-conspirators'),
    DocCfg(id='EFTA00796700', description=f"detailed notes on Epstein's relationship with {ALAN_DERSHOWITZ}", is_interesting=True),
    DocCfg(id='EFTA00143492', description=f"court filing in which a victim calls Giuffre lawyer {STANLEY_POTTINGER} an abuser"),
    DocCfg(id='EFTA00039817', description='notice of hearing', date='2021-04-19', duplicate_ids=['EFTA00039791'], is_interesting=False),
    DocCfg(id='EFTA00005586', replace_text_with='completely redacted 69 pages labeled "Grand Jury - NY"'),
]


# This category makes is_interesting default to True
OTHER_FILES_LETTER = [
    CommunicationCfg(
        id='026011',
        author='Gennady Mashtalyar',
        date='2016-06-24',  # date is based on Brexit reference but he could be backtesting,
        description=f"about algorithmic trading",
    ),
    CommunicationCfg(id='026134', recipients=['George'], description=f'about opportunities to buy banks in Ukraine'),
    blaine_letter(id='019086', date='2015-05-27', suffix='naming various Putin puppet regimes', show_full_panel=True),
    blaine_letter(id='019474', date='2015-05-29'),
    blaine_letter(id='019476', date='2015-06-01'),

    # DOJ files
    CommunicationCfg(id='EFTA00007609', recipients=['Alberto'], duplicate_ids=['EFTA00007582']),
    CommunicationCfg(id='EFTA02731023', author='Senator Ron Wyden', recipients=[LEON_BLACK], is_interesting=False),
    CommunicationCfg(id='EFTA02731018', author='Senator Ron Wyden', recipients=['Marc Rowan'], is_interesting=False),
]


OTHER_FILES_MISC = [
    DocCfg(id='029326', category=Neutral.PRESSER, author=EPSTEIN_FOUNDATION, date='2013-02-15'),
    DocCfg(id='026565', category=Neutral.PRESSER, author=EPSTEIN_FOUNDATION, comment=f'maybe a draft of 029326', date='2013-02-15'),
    DocCfg(id='022494', author='DOJ', description=f'Foreign Corrupt Practices Act (FCPA) Resource Guide'),
    DocCfg(id='023096', author=EPSTEIN_FOUNDATION, description=f'blog post', date='2012-11-15'),
    DocCfg(id='027071', author=FEMALE_HEALTH_COMPANY, description=f"brochure requesting donations for female condoms in Uganda"),
    DocCfg(id='027074', author=FEMALE_HEALTH_COMPANY, description=f"pitch deck (USAID was a customer)"),
    DocCfg(id='032735', author=GORDON_GETTY, description=f"on Trump", date='2018-03-20'),  # Dated based on concurrent emails from Getty
    DocCfg(id='025540', author=JEFFREY_EPSTEIN, description=f"rough draft of his side of the story"),
    DocCfg(id='026634', author='Michael Carrier', description=f'comments about an Apollo linked fund "DE Fund VIII"'),
    DocCfg(id='031425', author=SCOTT_J_LINK, description=f'completely redacted email', is_interesting=False),
    DocCfg(id='020447', author='Working Group on Chinese Influence Activities in the US', description=f'Promoting Constructive Vigilance'),
    DocCfg(id='012718', description=f"{CVRA} congressional record", date='2011-06-17'),
    DocCfg(id='019448', description=f"Haitian business investment proposal called Jacmel", attached_to_email_id='019446'),
    DocCfg(id='023644', description=f"interview with Mohammed bin Salman", date='2016-04-25', is_interesting=False),
    DocCfg(
        id='030142',
        author=f"{KATHRYN_RUEMMLER} & {KEN_STARR}",
        date='2016-09-01',
        description=f"mostly empty {JASTA} (Justice Against Sponsors of Terrorism Act) doc referencing suit against Saudis",
    ),
    DocCfg(
        id='033338',
        category=Neutral.PRESSER,
        date='2000-06-07',
        description=f"end of {DONALD_TRUMP} & {NICHOLAS_RIBIS} working relationship at Trump's casino",
        is_interesting=True,
    ),
    DocCfg(id='029328', description=f"Rafanelli Events promotional deck", is_interesting=False),
    DocCfg(id='029475', description=f'{VIRGIN_ISLANDS} Twin City Mobile Integrated Health Services (TCMIH) proposal/request for donation', is_interesting=False),
    DocCfg(id='029448', description=f"weird short essay titled 'President Obama and Self-Deception'"),

    # DOJ files
    DocCfg(
        id='EFTA00034357',
        author=BUREAU_OF_PRISONS,
        date='2019-08-10',
        description=f"internal message about discovery of Epstein's body",
        background_color='red'
    ),
    DocCfg(id='EFTA01103465', author=BEN_GOERTZEL, date='2013-12-02', description='funding proposal for AI labs in Africa etc.'),
    DocCfg(id='EFTA00165515', description="contractor describes Epstein's gun safes", show_full_panel=True),
    DocCfg(id='EFTA00266322', description=f"documents about pitches for non-profits in Australia, including to Effective Altruism"),
    DocCfg(id='EFTA00029538', description=f"{GHISLAINE_MAXWELL} provided school girl uniforms", show_full_panel=True),
    DocCfg(id='EFTA00005783', description='heavily redacted handwritten note, 30+ completely redacted pages', date='2019-08-29'),
    DocCfg(id='EFTA00005386', description='heavily redacted photo album, lot of photos of girls'),
    DocCfg(id='EFTA01063691', description='inventory of address books and Skype logs seized from Epstein computers'),
    DocCfg(id='EFTA00024275', description='large Wexner funded payments to OB-GYN'),
    DocCfg(id='EFTA00728783', description='list of names and phone numbers'),
    DocCfg(id='EFTA00298379', description='RSVP list for Yom Kippur dinner', date='2010-09-18'),
    # Urramoor
    DocCfg(
        id='EFTA01107738',
        description=f"creation of {CANTOR_URRAMOOR} with Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA01141453',
        description=f"referral agreement between Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=True,
    ),
    # Replacement text
    DocCfg(
        id='EFTA00009622',
        date='2006-07-19',
        description='handwritten notes from a victim interview transcribed by Claude AI',
        is_interesting=True,
        replace_text_with=EFTA00009622_TEXT,
    ),
    DocCfg(
        id='EFTA00004477',
        is_interesting=True,
        replace_text_with='Epstein 50th birthday photo book 12 "THAIS, MOSCOW GIRLS, AFRICA, HAWAII, [REDACTED] [REDACTED], Zorro, [REDACTED] [REDACTED] [REDACTED], CRACK WHOLE PROPOSAL, BALI/THAILAND/ASIA, RUSSIA, [REDACTED], [REDACTED], NUDES, YOGAL GIRLS',
    ),
    DocCfg(id='EFTA01628970', replace_text_with='redacted pictures of naked women'),
    DocCfg(id='EFTA00004070', replace_text_with="photos of Epstein with handwritten caption that didn't OCR well"),
    DocCfg(id='EFTA02731260', replace_text_with='notebook full of handwritten love letters with terrible OCR text'),
    DocCfg(id='EFTA00006100', replace_text_with='Palm Beach Police fax machine activity log 2005-12-28 to 2006-01-04'),
    DocCfg(
        id='EFTA00003149',
        date='2016-01-01',
        date_uncertain='complete guess',
        description=f"{LITTLE_SAINT_JAMES} staff list",
        show_full_panel=True,
    ),
    # Attachments
    DocCfg(id='EFTA00590685', attached_to_email_id='EFTA00830911'),
    # Dates
    DocCfg(id='EFTA02025218', date='2011-09-09'),
    # FedEx
    fedex_invoice('EFTA00217072', '2005-06-20'),
    fedex_invoice('EFTA00217080', '2005-06-27'),
    # Message pads
    important_messages_pad('EFTA01719859', '2005-10-03'),
    important_messages_pad('EFTA01682477', '2005-04-01'),
]


# Epstein money. This category makes is_interesting = True
OTHER_FILES_MONEY = [
    # private placement memoranda
    DocCfg(
        id='024432',
        date='2006-09-27',
        description=f"Michael Milken's Knowledge Universe Education (KUE) $1,000,000 corporate share placement notice (SEC filing?)"
    ),
    DocCfg(id='024003', description=f"New Leaf Ventures ($375 million biotech fund) private placement memorandum"),

    # DOJ files
    DocCfg(
        id='EFTA01413294',
        comment='related to EFTA01357341, efta01363125, + more based on Vavilov Street address',
        date='2016-12-16',
        date_uncertain='hard to tell',
        description='compliance report on payment from Epstein to Sberbank account of Nikolay Aleksandrovich Gyrov',
    ),
    DocCfg(
        id='EFTA00173953',
        author='Organized Crime Drug Enforcement Task Force',
        description='report on DEA investigations into Epstein related drug money laundering',
    ),
    DocCfg(
        id='EFTA01681865',
        author=DEUTSCHE_BANK,
        description="explanations of all of Epstein's large payments prepared for DOJ",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA01361270',
        author=DEUTSCHE_BANK,
        date='2014-01-02',
        description=f"$60,000 transfer from {SOUTHERN_TRUST_COMPANY} to {BEN_GOERTZEL}'s Novamente",
    ),
    DocCfg(
        id='EFTA01111057',
        author=MORTIMER_ZUCKERMAN,
        date='2014-07-10',
        description='Mortimer B. Zuckerman Management Trust',
        non_participants=['Marla Maples'],
    ),
    DocCfg(id='EFTA01285411', description=f"bank statement for Epstein's {SOUTHERN_TRUST_COMPANY} showing $82 million balance"),
    DocCfg(id='EFTA01222951', description=f"credit card expenses for Carlos L Rodriguez using Plum Card", date='2019-02-12'),
    DocCfg(id='EFTA00016884', description="Epstein's last will and testament", date='2014-11-18'),
    DocCfg(
        id='EFTA00089546',
        description=f"Epstein last will and testament codicil naming {JAMES_CAYNE} an executor",
        date='2007-09-20',
        non_participants=[JOI_ITO],
    ),
    DocCfg(id='EFTA01266380', description="Epstein's 2014 Trust with bequests"),
    DocCfg(id='EFTA01282282', description=f"Epstein Butterfly Trust (sole beneficiary {KARYNA_SHULIAK})"),
    DocCfg(id='EFTA01583819', description=f"Epstein had control of {JAMES_CAYNE}'s assets"),
    DocCfg(id='EFTA00099424', description=f"Epstein 2017 Trust (Eva Andersson Dubin, {DARREN_INDYKE}, {RICHARD_KAHN})"),
    DocCfg(id='EFTA01266457', description=f"Epstein 2018 Trust ({KATHRYN_RUEMMLER}, {DARREN_INDYKE}, {RICHARD_KAHN})"),
    DocCfg(id='EFTA01266204', description=f"Epstein The 1953 Trust ({DARREN_INDYKE}, {RICHARD_KAHN})", date='2019-08-08'),
    DocCfg(id='EFTA00299927', description=f"estate plan for {JAMES_CAYNE} found in Epstein's possession"),
    DocCfg(id='EFTA01265973', description="large transfers around time of Epstein arrest", show_full_panel=True),
    DocCfg(id='EFTA01087311', description=f'{LEON_BLACK} Family Partners cash projections'),
    DocCfg(id='EFTA01086463', description=f"{MORTIMER_ZUCKERMAN}'s art collection valuations", is_valid_for_name_scan=False),
    DocCfg(id='EFTA00007781', description='paychecks signed by Epstein deposited at Colonial Bank', date='2005-08-12'),
    DocCfg(id='EFTA01273102', description=f"payment from Epstein to {RENATA_BOLOTOVA}'s father's account at Sberbank"),
    DocCfg(id='EFTA00238499', description='wire transfer to Signature Bank account'),
    DocCfg(id='EFTA00000476', replace_text_with='photo of JEFFREY EPSTEIN CASH DISBURSEMENTS for the month 2006-09', date='2006-09-01'),
    # Emails
    EmailCfg(id='EFTA00037187', is_interesting=True),
    EmailCfg(id='EFTA02189550', author='Ike Groff', author_uncertain=True, description=f"Ike Groff invests $250,000 in Mangrove Partners managed by Nathaniel August"),
    EmailCfg(id='EFTA00371120', description=f"Epstein appears to invest in {ATORUS}"),
    EmailCfg(id='EFTA00652799', description=f'Epstein calls Ari Glass "a bit sketchy" despite investing ~$50 million in his fund Boothbay'),
]


OTHER_FILES_PHONE_BILL = [
    phone_bill_cfg('EFTA00007070', 'MetroPCS', '2006'),
    phone_bill_cfg('EFTA00006770', 'MetroPCS', '2006-02-01 to 2006-06-16'),
    phone_bill_cfg('EFTA00006870', 'MetroPCS', '2006-02-09 to 2006-07'),
    phone_bill_cfg('EFTA00006970', 'MetroPCS', '2006-04-15 to 2006-07-16'),
    phone_bill_cfg('EFTA00007401', 'T-Mobile', '2004-08-25 to 2005-07-13'),
    phone_bill_cfg('EFTA00007501', 'T-Mobile', '2005'),
    phone_bill_cfg('EFTA00006487', 'T-Mobile', '2006'),
    phone_bill_cfg('EFTA00006387', 'T-Mobile', '2006-06-15 to 2006-07-23'),
    phone_bill_cfg('EFTA00006587', 'T-Mobile', '2006-09-04 to 2016-10-15'),
    phone_bill_cfg('EFTA00006687', 'T-Mobile', '2006-10-31 to 2006-12-25'),
    # These two are subpoena response letters w/attached phone bill)
    phone_bill_cfg('EFTA00007301', 'T-Mobile', 'Blackberry phone logs for 2005', date='2007-03-23'),
    phone_bill_cfg('EFTA00007253', 'T-Mobile', date='2007-03-23'),
]


OTHER_FILES_POLITICS = [
    DocCfg(id='030258', author=ALAN_DERSHOWITZ, description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030248'),
    DocCfg(id='030248', author=ALAN_DERSHOWITZ, description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    DocCfg(id='029165', author=ALAN_DERSHOWITZ, description=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    DocCfg(id='029918', author=DIANA_DEGETTE_CAMPAIGN, description=f"bio", date='2012-09-27'),
    DocCfg(id='031184', author=DIANA_DEGETTE_CAMPAIGN, description=f"invitation to fundraiser hosted by {BARBRO_C_EHNBOM}", date='2012-09-27'),
    DocCfg(id='026248', author='Don McGahn', description=f'letter from Trump lawyer to Devin Nunes (R-CA) about FISA courts and Trump'),
    DocCfg(id='027009', author=EHUD_BARAK, description=f"speech to AIPAC", date='2013-03-03'),
    DocCfg(
        id='019233',
        author='Freedom House',
        date='2017-06-02',
        description=f"'Breaking Down Democracy: Goals, Strategies, and Methods of Modern Authoritarians'",
    ),
    DocCfg(id='026856', author='Kevin Rudd', description=f'speech "Xi Jinping, China And The Global Order"', date='2018-06-26'),
    DocCfg(id='026827', author='Scowcroft Group', description=f'report on ISIS', date='2015-11-14'),
    DocCfg(id='024294', author=STACEY_PLASKETT, description=f"campaign flier", date='2016-10-01'),
    DocCfg(
        id='023133',
        author=f"{TERJE_ROD_LARSEN}, Nur Laiq, Fabrice Aidan",
        date='2014-12-09',
        description=f'The Search for Peace in the Arab-Israeli Conflict',
    ),
    DocCfg(id='033468', description=f'{ARTICLE_DRAFT} Rod Rosenstein', date='2018-09-24'),
    DocCfg(id='025849', author=US_ORG, description=quote('Building a Bridge Between FOIA Requesters & Agencies')),
    # CommunicationCfg(id='031670', author="General Mike Flynn's lawyers", recipients=['Sen. Mark Warner & Richard Burr'], description=f"about subpoena"),
    DocCfg(id='031670', description=f"letter from General Mike Flynn's lawyers to senators Mark Warner & Richard Burr about subpoena"),
    DocCfg(
        id='029357',
        date='2015-01-15',
        date_uncertain='a guess',
        description=f"possibly book extract about Israel's challenges entering 2015",
        duplicate_ids=['028887'],
    ),
    DocCfg(id='010617', description=TRUMP_DISCLOSURES, date='2017-01-20', is_interesting=True, attached_to_email_id='033091'),
    DocCfg(id='016699', description=TRUMP_DISCLOSURES, date='2017-01-20', is_interesting=True, attached_to_email_id='033091'),
]


OTHER_FILES_PROPERTY = [
    DocCfg(
        id='026759',
        author='Great Bay Condominium Owners Association',
        category=Neutral.PRESSER,
        description=f'Hurricane Irma damage',
        date='2017-09-13',
        is_interesting=False,
    ),
    DocCfg(id='016602', author=PALM_BEACH_CODE_ENFORCEMENT, description='board minutes', date='2008-04-17'),
    DocCfg(id='016554', author=PALM_BEACH_CODE_ENFORCEMENT, description='board minutes', date='2008-07-17', duplicate_ids=['016616', '016574']),
    DocCfg(id='016636', author=PALM_BEACH_WATER_COMMITTEE, description=f"Meeting on January 29, 2009"),
    DocCfg(id='022417', author='Park Partners NYC', description=f"letter to partners in real estate project with architectural plans"),
    DocCfg(id='027068', author=THE_REAL_DEAL, description=f"{REAL_DEAL_ARTICLE} Palm House Hotel Bankruptcy and EB-5 Visa Fraud Allegations"),
    DocCfg(id='029520', author=THE_REAL_DEAL, description=f"{REAL_DEAL_ARTICLE} 'Lost Paradise at the Palm House'", date='2019-06-17'),
    DocCfg(id='016597', author='Trump Properties LLC', description=f'appeal of some decision about Mar-a-Lago by {PALM_BEACH} authorities'),
    DocCfg(id='018743', description=f"Las Vegas property listing"),
    DocCfg(id='016695', description=f"{PALM_BEACH_PROPERTY_INFO} (?)"),
    DocCfg(id='016697', description=f"{PALM_BEACH_PROPERTY_INFO} (?) that mentions Trump"),
    DocCfg(id='016599', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016600', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016601', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016694', description=f"{PALM_BEACH_TSV} consumption (water?)"),
    DocCfg(id='016552', description=f"{PALM_BEACH_TSV} info"),
    DocCfg(id='016698', description=f"{PALM_BEACH_TSV} info (broken?)"),
    DocCfg(id='016696', description=f"{PALM_BEACH_TSV} info (water quality?"),
    DocCfg(
        id='018727',
        description=f"{VIRGIN_ISLANDS} property deal pitch deck, building will be leased to the U.S. govt GSA",
        date='2014-06-01',
    ),
]


OTHER_FILES_REPUTATION = [
    DocCfg(id='030426', author=IAN_OSBORNE, description=f"reputation repair proposal citing Michael Milken", date='2011-06-14'),
    DocCfg(id='026582', description=f"Epstein's internet search results at start of reputation repair campaign, maybe from {OSBORNE_LLP}"),
    DocCfg(id='030573', description=f"Epstein's unflattering Google search results, maybe screenshot by {AL_SECKEL} or {OSBORNE_LLP}"),
    DocCfg(id='030875', description=f"Epstein's Wikipedia page", date='2014-02-08'),  # Date is based on tyler shears; seckel was 2010
    DocCfg(id='026583', description=f"Google search results for '{JEFFREY_EPSTEIN}' with analysis ({OSBORNE_LLP}?)"),
    DocCfg(id='029350', description=f"Microsoft Bing search results for Epstein with sex offender at top", attached_to_email_id='EFTA00675542'),
    EmailCfg(id='022203', description=AL_SECKEL_BILL_FIGHT, truncate_to=500),
    EmailCfg(id='022219', description=AL_SECKEL_BILL_FIGHT, truncate_to=2404),

    # DOJ files
    EmailCfg(id='EFTA01830035', description=AL_SECKEL_BILL_FIGHT),
    DocCfg(
        id='EFTA01810372',
        author=TYLER_SHEARS,
        description=f'invoice for reputation management work',
        is_interesting=True,
        attached_to_email_id='EFTA01931256'
    ),
]


# resumes and application letters
OTHER_FILES_RESUMÉ = [
    DocCfg(
        id='029304',
        attached_to_email_id='029299',
        author=MICHAEL_J_BOCCIO,
        description=f"recommendation letter by {DONALD_TRUMP}",
    ),
    DocCfg(id='022367', author='Jack J. Grynberg', description=RESUME_OF, date='2014-07-01'),
    DocCfg(
        id='029302',
        attached_to_email_id='029299',
        author=MICHAEL_J_BOCCIO,
        description=f"{RESUME_OF} (former lawyer at the {TRUMP_ORG})",
        date='2011-08-07',
    ),
    DocCfg(
        id='029301',
        attached_to_email_id='029299',
        author=MICHAEL_J_BOCCIO,
        description=f"letter from former lawyer at the {TRUMP_ORG}",
        date='2011-08-07',
    ),
    DocCfg(id='029102', author=NERIO_ALESSANDRI, description=HBS_APPLICATION),
    DocCfg(id='029104', author=NERIO_ALESSANDRI, description=HBS_APPLICATION),
    DocCfg(id='015671', author='Robin Solomon', description=RESUME_OF, date='2015-06-02'),  # She left Mount Sinai at some point in 2015,
    DocCfg(id='015672', author='Robin Solomon', description=RESUME_OF, date='2015-06-02'),  # She left Mount Sinai at some point in 2015,
    DocCfg(id='029623', description=f'bio of Kathleen Harrington, Founding Partner, C/H Global Strategies'),
]


OTHER_FILES_SKYPE_LOG = [
    CommunicationCfg(id='032206', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    CommunicationCfg(id='032208', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    CommunicationCfg(id='032209', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    CommunicationCfg(id='032210', recipients=['linkspirit'], is_interesting=True),
    CommunicationCfg(id='018224', recipients=['linkspirit', LAWRENCE_KRAUSS], is_interesting=True),  # we don't know who linkspirit is yet
    CommunicationCfg(id='EFTA01617727'),
    CommunicationCfg(
        id='EFTA00507334',
        recipients=[
            'Aleksandra Eriksson',
            ANASTASIYA_SIROOCHENKO,
            'Catherine',
            DANIEL_SIAD,
            DAVID_STERN,
            EMAD_HANNA,
            'Jade Huang',
            NADIA_MARCINKO,
            'sexysearch2010',
            'sophiembh'
        ],
    ),
    CommunicationCfg(id='EFTA01613143', author=MELANIE_WALKER, date='2017-06-24'),
    CommunicationCfg(id='EFTA01217787', recipients=[TYLER_SHEARS, 'Hanna Traff at Spotify'], is_interesting=True),
    CommunicationCfg(id='EFTA01217703', recipients=['actress Athena Zelcovich', JOSCHA_BACH, LAWRENCE_KRAUSS]),
    CommunicationCfg(id='EFTA01217736', recipients=['actress Athena Zelcovich', TYLER_SHEARS]),
    CommunicationCfg(
        id='EFTA01623342',
        author=ANNA_KASATKINA,
        author_uncertain='https://www.reddit.com/r/Epstein/comments/1qwbn5i/trafficker_julia_santos/',
        description='recruiting russian girls',
        is_interesting=True,
    ),
]


OTHER_FILES_SOCIAL = [
    DocCfg(id='028815', author=INSIGHTS_POD, description=f"business plan", date='2016-08-20', attached_to_email_id='033171'),
    DocCfg(id='011170', author=INSIGHTS_POD, description=f'case study of social media vibe analysis using tweets from #Brexit', date='2016-06-23', attached_to_email_id='033171'),
    DocCfg(id='032324', author=INSIGHTS_POD, description=f"social media election sentiment analysis", date='2016-11-05', attached_to_email_id='032323'),
    DocCfg(id='032281', author=INSIGHTS_POD, description=f"social media election sentiment report", date='2016-10-25', attached_to_email_id='032280'),
    DocCfg(id='028988', author=INSIGHTS_POD, description=f"pitch deck", date='2016-08-20', attached_to_email_id='033171'),
    DocCfg(id='026627', author=INSIGHTS_POD, description=f"report on impact of presidential debate", attached_to_email_id='026626'),
    DocCfg(id='022213', description=f"{SCREENSHOT} Facebook group called 'Shit Pilots Say' disparaging a 'global girl'", is_interesting=False),
    EmailCfg(id='033171', is_interesting=True, comment='Zubair'),
    EmailCfg(
        id='030630',
        author=MARIA_PRUSAKOVA,
        author_reason=PRUSAKOVA_BERKELY,
        description=f'Masha Prusso / {MARIA_PRUSAKOVA} asks about Zubair Khan and {INSIGHTS_POD}',
        is_interesting=True,
    ),
    EmailCfg(
        id='032319',
        description=f"{ZUBAIR_KHAN} says social media vibes are good for Trump in last week before the 2016 election",
        dupe_type='quoted',
        duplicate_ids=['032283'],
        is_interesting=True,
    ),
    EmailCfg(
        id='032325',
        description=f"{ZUBAIR_KHAN} predicts Trump winning in 2016",
        dupe_type='quoted',
        duplicate_ids=['026014'],
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA00719854',
        description=f'{BORIS_NIKOLIC} introduces Epstein to Chris Poole AKA "moot", the founder of 4chan',
        is_interesting=True,
        show_with_name=CHRIS_POOLE
    ),
    EmailCfg(
        id='EFTA00922824',
        description=f"Epstein meets with {CHRIS_POOLE} (founder of 4chan) the day the infamous /pol/ board is created",
        is_interesting=True,
        show_with_name=CHRIS_POOLE,
    ),
]


OTHER_FILES_TEXT_MSG = [
    DocCfg(id='033434', description=f"{SCREENSHOT} iMessage chat labeled 'Edwards'"),
    DocCfg(
        id='EFTA01620764',
        author=MELANIE_WALKER,
        author_uncertain=True,
        description=f'conversation about crypto philanthropy and Bill Gates being drunk all the time',
        is_interesting=True,
        truncate_to=(250, 3500)
    ),
    DocCfg(id='EFTA01618381', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01622387', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01618494', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01618400', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01611898', description=f"screenshot of recent contacts in an iPhone"),
    CommunicationCfg(
        id='EFTA02731576',
        description=f"making contemporaneous accusations",
        recipients=[LEON_BLACK],
        show_full_panel=True
    ),
    CommunicationCfg(id='EFTA01611042', author=ED_BOYLE, recipients=[None, MARIA_PRUSAKOVA]),
    CommunicationCfg(id='EFTA02731525', author=LEON_BLACK, author_uncertain=True, show_full_panel=True),
    CommunicationCfg(
        id='EFTA01612665',
        description='sender is "stressed about finding girls", Epstein gives advice on how to find them',
        is_interesting=True
    ),
]


OTHER_FILES_TWEET = [
    DocCfg(id='023050', author=ALAN_DERSHOWITZ, description=DERSH_GIUFFRE_TWEET),
    DocCfg(id='017787', author=ALAN_DERSHOWITZ, description=DERSH_GIUFFRE_TWEET),
    DocCfg(id='033433', author=ALAN_DERSHOWITZ, description=f"{DERSH_GIUFFRE_TWEET} / David Boies", date='2019-03-02'),
    DocCfg(id='033432', author=ALAN_DERSHOWITZ, description=f"{DERSH_GIUFFRE_TWEET} / David Boies", date='2019-05-02'),
    DocCfg(id='031546', author=DONALD_TRUMP, description=f"about Russian collusion", date='2018-01-06'),
    DocCfg(id='030884', author='Ed Krassenstein'),
    DocCfg(id='033236', description=f'selection about Ivanka Trump in Arabic', date='2017-05-20'),
]


WHISTLEBLOWER_IDS = {
    'EFTA00093702_37': '',
    'EFTA00093702_13': '',
    'EFTA00093702_21': RIOT_BLOCKCHAIN_DESCRIPTION,
    'EFTA00093702_30': f"Signature Bank failed in 2023, {RIOT_BLOCKCHAIN_DESCRIPTION}",
    'EFTA00093702_29': RIOT_BLOCKCHAIN_DESCRIPTION,
    'EFTA00093702_28': RIOT_BLOCKCHAIN_DESCRIPTION,
    'EFTA00093702_27': RIOT_BLOCKCHAIN_DESCRIPTION,
    'EFTA00093702_26': RIOT_BLOCKCHAIN_DESCRIPTION,
}

OTHER_FILES_CRYPTO.extend([whistleblower_cfg(id, desc) for id, desc in WHISTLEBLOWER_IDS.items()])


# Interesting / uninteresting
INTERESTING_EMAIL_IDS = [
    '033096',
    'EFTA02516264',
]

# These emails will be suppressed in the curated views
UNINTERESTING_EMAIL_IDS = [
    # Alan Dlugash
    'EFTA02367999',
    # Amir Taaki
    'EFTA01983108',
    # Austin Hill
    'EFTA01024046',
    'EFTA01010209',
    'EFTA00461202',
    'EFTA02229342',
    'EFTA01005712',
    'EFTA01005715',
    'EFTA02228570',
    # Bannon
    'EFTA02517956',
    '030710',
    '030954',
    '030956',
    '027585',  # texts
    '020440',
    '019338',
    '019343',
    '026304',
    '030372',
    '030408',
    '026310',
    '030736',
    '020443',
    '030983',
    '030958',
    '026477',
    # Ben Goertzel
    'EFTA01745739',
    # Brock
    'EFTA02174702',
    'EFTA00371547',
    'EFTA00405824',
    'EFTA00361736',
    'EFTA02160842',
    'EFTA00405795',
    'EFTA00362148',
    'EFTA00362163',
    'EFTA00997253',
    'EFTA00997251',
    'EFTA00362171',
    'EFTA00693620',
    'EFTA02092108',
    'EFTA00645400',
    'EFTA01002109',
    'EFTA02365466',
    'EFTA00709543',
    'EFTA00419736',  # visible elsewhere
    'EFTA01001754',  # visible elsewhere
    'EFTA00699275',
    'EFTA00864590',
    'EFTA00875181',
    # Christina Galbraith
    '031591',
    # David Stern
    'EFTA02507454',
    'EFTA02478704',
    'EFTA01862308',
    'EFTA02570707',
    '030724',
    # Ehud Barak
    '025878',
    '026354',
    '026618',
    # Epstein
    '030997',
    '033428',
    '030154',
    # Eric Roth
    '033386',
    # FBI
    'EFTA00005705',
    'EFTA00005716',
    'EFTA00005717',
    'EFTA00039971',  # Attached 302 is missing?
    # Ganbat
    'EFTA02469375',
    # Ghislaine
    'EFTA00582171',  # Visible in other files
    # Ian Osborne
    'EFTA01763771',
    'EFTA00932122',
    # Jabor
    '030786',
    '033011',
    # Jean Luc Brunel
    'EFTA01987855',  # TODO not entirely uninteresting...
    # Jeremy Rubin
    'EFTA00714127',
    # John Page
    '016693',
    # Joi Ito
    '029500',
    '029279',
    '029088',
    '029204',
    '029094',
    '029096',
    '028924',  # visible elsewhere
    '029224',  # visible elsewhere
    '029429',
    '029587',
    '029237',
    '029499',
    'EFTA02363524',  # visible in EFTA00676383
    'EFTA00649516',
    'EFTA02593836',
    'EFTA00697880',
    'EFTA02647229',
    'EFTA02238841',
    # Karyna Shuliak
    'EFTA02318365',
    # Krassner
    '033345',
    # Leon Black related
    '023208_24',
    '023208_26',
    # Lesley?
    'EFTA02229402',
    'EFTA02229659',
    'EFTA01987383',
    'EFTA02067872',
    # Maria Prusakova
    'EFTA01772533',
    'EFTA01740489',
    # Peter Thiel
    'EFTA01003336',
    # Philip Rosedale
    'EFTA01903448',
    'EFTA01899565',
    # Ramsey Elkholy
    'EFTA02438522',  # visible elsewhere
    # Rasseck Bourgi
    'EFTA01990389',  # visible in EFTA01988194
    # Renata Bolotova
    'EFTA01903041',
    'EFTA01969322',
    'EFTA01035614',
    'EFTA02719248',
    'EFTA02696764',
    'EFTA00927986',
    'EFTA00667874',
    # Svetlana
    'EFTA01772677',
    # Tyler Shears
    'EFTA02511281',
    # USANYS / DOJ
    'EFTA00039799',
    'EFTA02730469',
    'EFTA02730471',
    'EFTA02731662',
    'EFTA02731648',
    'EFTA02731473',
    'EFTA02731735',
    'EFTA02731734',
    'EFTA02731628',
    'EFTA00040144',
    'EFTA00040105',
    'EFTA00040118',
    'EFTA00040124',
    'EFTA02730468',
    'EFTA00040141',
    'EFTA02730485',
    'EFTA02731526',
    'EFTA00039802',
    'EFTA00039867',
    'EFTA00039995',
    'EFTA00039981',
    'EFTA00104945',
    'EFTA00039893',
    'EFTA02385456',
    'EFTA02730481',
    'EFTA02730483',
    # TODO: These have UNKNOWN recipient so they currently get printed but we should configure it so they don't
    'EFTA00039894',
    'EFTA00039878',
    # Valdson
    'EFTA02303690',
    # Vincenzo Iozzo
    '033280',
    'EFTA02624738',
    'EFTA01751416',  # Visible in EFTA02584771
    # Wolff
    '021120',
    # Unknown
    '030992',
    '032213',
    '029206',
    '031822',
    '031705',
    '030768',
    '026659',
    '032951',
    '023062',
    '030324',
    '031990',
    '024930',
    '029982',
    '022187',
    '033486',
    '029446',
    '019873',
    '030823',  # "little hodiaki"
    '027009',
    '026273',
    'EFTA02431535',  # visible in EFTA00888467
    'EFTA00363992',  # car rental
    'EFTA02187735',  # housekeeping
]

# Not uninteresting enough to be permanently marked as such but not good enough for --output-chrono
NOT_CHRONOLOGICAL_VIEW_IDS = [cfg.id for cfg in OTHER_FILES_FLIGHT_LOG] + [
    # Karim Wade
    'EFTA01063216',  # canceled trip
    'EFTA01738267',  # canceled trip
    # Ehud barak
    '032336',
    '033338',
    'EFTA00582504',
    '024432',
    '019352',
    'EFTA02053321',  # Ike Groff
    'EFTA00915298',
    'EFTA02423635',
    'EFTA00007781',
    'EFTA00770066',
    '016692',
    'EFTA01823635',
    'EFTA00747181',
    'EFTA00758140',
    'EFTA01979689',
    'EFTA00878255',
    'EFTA00766770',
    'EFTA00384774',
    'EFTA00892654',  # Mandelson
    'EFTA02437992',  # Ben Goertzel
    'EFTA01613143',  # Melanie Walker
    'EFTA02144766',  # Zorro Ranch
    'EFTA02308934',  # Yoed Nir
    'EFTA02009735',  # Boris email about Regina Dugan
    'EFTA00719151',  # Boris Regina TED
    '030609',
    '022247',
    '030095',
    '022234',
    '030470',
    '030222',
    # Christina Galbraith
    'EFTA00941810'
    # '031826',
    '031826',
    '019446',  #Haiti jacmel
    # Jean Luc visa etc
    'EFTA02515416',
    'EFTA02516675',
    '011908_6',
    # Jabor
    # Joi Ito
    'EFTA01058627',
    # Deepak
    'EFTA02342230',
    # Misc
    'EFTA00329334',
    # Renata Bolotova
    'EFTA00667441',
    # Tyler Shears
    'EFTA02372294',
    '028965',
    # --- #
    'EFTA02048499',
    'EFTA00322570',
    'EFTA02001536',
    'EFTA01773417',
    'EFTA01987283',
    'EFTA01778423',
    'EFTA01798022',
    'EFTA00845330',
    'EFTA00840747',
    'EFTA02475571',
    '030807',
    '032842',
    'EFTA00434111',
    'EFTA00432352',
    '026583',
    '031986',
    '026584',
    '029973',
    '031038',
    '028760',
    '029976',
    '026320',
    '031169',
    'EFTA01757037',
    '030211',
    '031964',
    '027032',
    '027126',
    '030881',
    'EFTA00373948',
    'EFTA00659818',
    'EFTA01931339',
    'EFTA01923844',
    'EFTA00998902',
    '011908_4',
    '030874',
    'EFTA02396796',
    '031320',
    '026254',
    '026473',
    '026474',
    '025517',
    '025520',
    '030721',
    '030785',
    '029497',
    '030795',
    'EFTA00848188',
    'EFTA02465832',
    'EFTA02430577',
    '030444',
    '030788',
    '020815',
    '021106',
    '027044',
    '025429',
    '027583',
    '025426',
    '025423',
    '027707',
    '019302',
    '019305',
    '019334',
    '019308',
    '019312',
    '026311',
    '027067',
    '030966',
    '030967',
    '030986',
    '029583',
    '017827',
    # '024185', # UN
]

# Build OtherFile / DojFile config list by combining OTHER_FILES_[BLAH] variables
ALL_OTHER_FILES_CONFIGS: list[DocCfg] = []

for category in CONSTANT_CATEGORIES:
    var_name = f"{OTHER_FILES_PFX}{category.upper()}"

    if var_name not in locals():
        logger.warning(f"Document config variable '{var_name}' is not defined!")
        continue

    for cfg in locals()[var_name]:
        cfg.set_category(cfg.category or category)  # Set category to OTHER_FILES_ var name suffix
        ALL_OTHER_FILES_CONFIGS.append(cfg)

ALL_CONFIGS = EMAILS_CONFIG + ALL_OTHER_FILES_CONFIGS + TEXTS_CONFIG
EmailCfg.create_or_set_prop(INTERESTING_EMAIL_IDS, ALL_CONFIGS, 'is_interesting', True)
EmailCfg.create_or_set_prop(UNINTERESTING_EMAIL_IDS, ALL_CONFIGS, 'is_interesting', False)
EmailCfg.create_or_set_prop(NOT_CHRONOLOGICAL_VIEW_IDS, ALL_CONFIGS, 'is_in_chrono', False)
CONFIGS_BY_ID = {cfg.id: cfg for cfg in ALL_CONFIGS}

# Add synthetic Cfg objects for duplicate docs with same props as the DocCfg they are a duplicate of
for cfg in ALL_CONFIGS:
    for dupe_cfg in cfg.duplicate_cfgs():
        CONFIGS_BY_ID[dupe_cfg.id] = dupe_cfg


# Collect special docs to show with special people
SHOW_WITH_DOCS = {id: list(cfgs) for id, cfgs in groupby(ALL_CONFIGS, lambda cfg: cfg.show_with_name) if id}


def check_no_overlapping_configs():
    encountered_file_ids = set()

    for cfg in ALL_CONFIGS:
        if cfg.duplicate_of_id:
            assert cfg.duplicate_of_id != cfg.id, f"Bad config! {cfg}"

        if cfg.id in encountered_file_ids:
            raise RuntimeError(f"{cfg.id} configured twice!")

        encountered_file_ids.add(cfg.id)


check_no_overlapping_configs()
