"""
Custom configurations for various files.
"""
from itertools import groupby

from epstein_files.documents.config.categories.emails import EMAILS_CONFIG
from epstein_files.documents.config.categories.imessage_logs import TEXTS_CONFIG
# These imports are actually used, but through a dynamic locals() reference
from epstein_files.documents.config.categories.academia import ACADEMIA_CFGS
from epstein_files.documents.config.categories.article import ARTICLE_CFGS
from epstein_files.documents.config.categories.arts import ARTS_CFGS
from epstein_files.documents.config.categories.book import BOOK_CFGS
from epstein_files.documents.config.categories.conference import CONFERENCE_CFGS
from epstein_files.documents.config.categories.crypto import CRYPTO_CFGS
from epstein_files.documents.config.categories.deposition import DEPOSITION_CFGS
from epstein_files.documents.config.categories.finance import FINANCE_CFGS
from epstein_files.documents.config.categories.girls import GIRLS_CFGS
from epstein_files.documents.config.categories.government import GOVERNMENT_CFGS
from epstein_files.documents.config.categories.junk import JUNK_CFGS
from epstein_files.documents.config.categories.legal import LEGAL_CFGS
from epstein_files.documents.config.categories.misc import MISC_CFGS
from epstein_files.documents.config.categories.money import MONEY_CFGS
from epstein_files.documents.config.categories.phone_bill import PHONE_BILL_CFGS
from epstein_files.documents.config.categories.politics import POLITICS_CFGS
from epstein_files.documents.config.categories.property import PROPERTY_CFGS
from epstein_files.documents.config.categories.reputation import REPUTATION_CFGS
from epstein_files.documents.config.categories.resume import RESUMÉ_CFGS
from epstein_files.documents.config.categories.russia import RUSSIA_CFGS
from epstein_files.documents.config.categories.social import SOCIAL_CFGS, TWEET_CFGS
from epstein_files.documents.config.categories.tech import TECH_CFGS
from epstein_files.documents.config.config_builder import victim_diary
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.config.pic_cfg import PIC_CFGS, PicCfg
from epstein_files.documents.documents.categories import Category, Interesting, Neutral, Uninteresting
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import join_truthy, quote
from epstein_files.util.logging import logger

CFGS_SUFFIX = '_CFGS'
PARTICIPANTS_FIELD = 'Participants: field'

HEADER_ABBREVIATIONS = {
    "Barak": f"former Israeli prime minister {EHUD_BARAK}",
    'BG, Bill': "Bill Gates",
    "Brock": 'Brock Pierce (crypto bro with a very sordid past)',
    "GRAT": "Grantor Retained Annuity Trust (tax shelter)",
    'HBJ, Jabor Y': "Sheikh Hamad bin Jassim (former Qatari prime minister)",
    'Jared': "Jared Kushner",
    'Joi': f"Joi Ito ({MIT_MEDIA_LAB}, MIT Digital Currency Initiative)",
    'KSA': "Kingdom of Saudi Arabia",
    'LSJ': "Little St. James (Epstein's island)",
    'Madars': 'Madars Virza (co-founder of privacy crypto ZCash)',
    'MBS': "Mohammed bin Salman Al Saud (Saudi ruler)",
    'MBZ': "Mohamed bin Zayed Al Nahyan (Emirates sheikh)",
    "Mooch": "Anthony 'The Mooch' Scaramucci (Skybridge crypto bro)",
    "NPA": 'non-prosecution agreement',
    "PA": PRINCE_ANDREW,
    "Terje": TERJE_ROD_LARSEN,
    "VI": f"U.S. {VIRGIN_ISLANDS}",
    "Woody": "Woody Allen",
}

TEXT_MSG_ABBREVIATIONS = {
    "AD": "Abu Dhabi",
    "Barrack": "Tom Barrack (Trump ally)",
    "DB": "Deutsche Bank (maybe??)",
    "Hoffenberg": f"{STEVEN_HOFFENBERG} (Epstein's ponzi scheme partner)",
    'Jagland': 'Thorbjørn Jagland (former Norwegian prime minister)',
    'Kwok': "Chinese criminal Miles Kwok AKA Miles Guo AKA Guo Wengui",
    'Kurz': 'Sebastian Kurz (former Austrian Chancellor)',
    'Mapp': f'{KENNETH_E_MAPP} (Governor of {VIRGIN_ISLANDS})',
    "Miro": MIROSLAV_LAJCAK,
}


################################################################################################
####################################### DOC CONFIGS ############################################
################################################################################################

DIARY_CFGS = [
    victim_diary('EFTA02731465', f"naming {JES_STALEY}, {TED_LEONSIS}, {GEORGE_VRADENBURG}, references tinkerbell"),
    victim_diary('EFTA02731420', f'naming {LARRY_SUMMERS}, {PRINCE_ANDREW}, Dan Snyder, {LEON_BLACK}, {TED_LEONSIS}'),
]

FLIGHT_LOG_CFGS = [
    DocCfg(id='022780'),
    DocCfg(id='022816'),
    DocCfg(id='EFTA00623147', author=DAVID_RODGERS, date='2016-06-30', date_uncertain='guess based on employment history'),
]

# Interesting / uninteresting
MOST_INTERESTING_EMAIL_IDS = [
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
    'EFTA01750836',
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
    # Bella Klein
    'EFTA02253705',
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
    # Danny Hillis
    'EFTA01880902',
    # David Stern
    'EFTA02507454',
    'EFTA02478704',
    'EFTA01862308',
    'EFTA02570707',
    'EFTA02501645',
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
    # exsbank
    'EFTA02166987',
    # FBI
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
    'EFTA01822611',
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
    'EFTA00554702',
    # Krassner
    '033345',
    # Leon Black related
    '023208_24',
    '023208_26',
    # Lesley?
    'EFTA00324390',
    'EFTA02229402',
    'EFTA02229659',
    'EFTA01987383',
    'EFTA02067872',
    # Madars Virza
    'EFTA02614678',
    # Maria Prusakova
    'EFTA01772533',
    'EFTA01740489',
    # Martin Weinberg
    '030149',
    # Nadia Marcinko
    'EFTA02409863',
    # Peter Thiel
    'EFTA01003336',
    # Philip Rosedale
    'EFTA01903448',
    'EFTA01899565',
    # Ramsey Elkholy
    'EFTA02438522',  # visible elsewhere
    'EFTA00658028',  # visible in EFTA00743526
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
    'EFTA00995559',
    'EFTA01748575',
    # Scott Link
    '022998',
    # Svetlana
    'EFTA01772677',
    # Tyler Shears
    'EFTA02511281',
    # USANYS / DOJ
    'EFTA00039420',
    'EFTA00039799',
    'EFTA02730469',
    'EFTA02730471',
    'EFTA02731662',
    'EFTA02731648',
    'EFTA02731473',
    'EFTA02731735',
    'EFTA00016800',
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
    'EFTA00039867',
    'EFTA00039981',
    'EFTA00104945',  # Quoted (i think)
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
    'EFTA00020508',  # Proffer
    'EFTA00023292',  # out of office
    'EFTA00037454',  # federal soup
]

UNINTERESTING_OTHER_FILE_IDS = [
    # FBI
    'EFTA01217787',
    'EFTA00005716',
    'EFTA00005705',
    'EFTA00005717',
]

# Not uninteresting enough to be permanently marked as such but not good enough for --output-chrono
NOT_CHRONOLOGICAL_VIEW_IDS = [cfg.id for cfg in FLIGHT_LOG_CFGS] + [
    'EFTA00006069',  # W-2 for employee
    'EFTA00507334',  # skype log w/lots of people
    'EFTA00751119',  # Valdson
    # Austin Hill
    'EFTA01917472',
    # Karim Wade
    'EFTA01063216',  # canceled trip
    'EFTA01738267',  # canceled trip
    'EFTA00677266',
    # Ehud barak
    '032336',
    # Brock
    'EFTA02590000',
    # Peter Mandelson
    '029914',
    '033338',
    # Ike Groff
    'EFTA02189550',
    # Daniel Siad
    'EFTA02434790',
    # FBI
    'EFTA00019169',
    # Ben Goertzel
    'EFTA00756577',
    'EFTA00995144',
    # David Stern
    'EFTA00756817',
    'EFTA01775500',
    # Jeremy Rubin
    'EFTA00367406',
    # MC2
    'EFTA01870235',
    # Story Cowles
    'EFTA00563586',
    #
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
    # Chris Poole
    'EFTA02175423',
    'EFTA02179653',
    'EFTA02179926',
    # Christina Galbraith
    'EFTA00941810',
    # '031826',
    '031826',
    '019446',  #Haiti jacmel
    # Ian Osbourne
    'EFTA01856718',
    'EFTA00718804',
    # Jean Luc visa etc
    'EFTA02515416',
    'EFTA02516675',
    '011908_6',
    # Jabor
    # Joi Ito
    '024256',
    'EFTA01058627',
    'EFTA02387540',
    # Lesley Groff
    'EFTA02266060',
    # Maria Prusakova / Miranda
    'EFTA01775280',
    'EFTA01990879',
    'EFTA00719146',
    'EFTA02026255',
    # Ramsey
    'EFTA01803353',
    # Steven Alexander
    'EFTA01798486',
    # Deepak
    'EFTA02342230',
    # Gulsum
    'EFTA01840139',
    # Misc
    'EFTA00329334',
    # Renata Bolotova
    'EFTA00667441',
    'EFTA01811230',
    'EFTA01985762',
    'EFTA01843319',
    'EFTA02018237',  # maybe about visa/ IPI?
    # Sean Lancaster
    '033155',
    # Tyler Shears
    'EFTA02372294',
    'EFTA01851487',
    'EFTA02518357',
    '028965',
    # unknown girl
    'EFTA00897668',
    'EFTA00625796',
    # Al Seckel
    'EFTA00709313',
    'EFTA00751523',
    # Jacquet
    'EFTA02027091',
    # Vincenzo
    'EFTA01749028',
    'EFTA01747994',
    #
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
    # unknown
    'EFTA00888467',  # mj
    'EFTA01848947',
    '030244',
    '028757',
    'EFTA02418669',  # unknown atty?
    'EFTA00364437',  # ivory coast
    'EFTA02422954',  # Celinas clothers
    'EFTA02514663',
    # '024185', # UN
]

# These are the categories we expect to see as a [category]_CFGS variable in constants.py
CATEGORIES_WITH_CFGS_VAR = [
    c for c in Category if c not in [
        Neutral.BUSINESS,
        Neutral.PRESSER,
        Uninteresting.JSON,
    ]
]

# Build config list by combining [BLAH]_CFGS variables and setting category to [BLAH] for each
CATEGORY_CONFIGS: list[DocCfg] = []

for category in CATEGORIES_WITH_CFGS_VAR:
    if (var_name := f"{category.upper()}{CFGS_SUFFIX}") not in locals():
        logger.error(f"Document config variable '{var_name}' is not defined!")
        continue

    category_cfgs = locals()[var_name]
    DocCfg.set_categories(category_cfgs, category)
    CATEGORY_CONFIGS.extend(category_cfgs)

ALL_CONFIGS = CATEGORY_CONFIGS + EMAILS_CONFIG + PIC_CFGS + TEXTS_CONFIG
DocCfg.update_or_create_cfgs(UNINTERESTING_OTHER_FILE_IDS, ALL_CONFIGS, 'is_interesting', False)
EmailCfg.update_or_create_cfgs(MOST_INTERESTING_EMAIL_IDS, ALL_CONFIGS, 'is_interesting', 10)
EmailCfg.update_or_create_cfgs(UNINTERESTING_EMAIL_IDS, ALL_CONFIGS, 'is_interesting', False)
EmailCfg.update_or_create_cfgs(NOT_CHRONOLOGICAL_VIEW_IDS, ALL_CONFIGS, 'is_in_chrono', False)
CONFIGS_BY_ID = {cfg.id: cfg for cfg in ALL_CONFIGS}

# Add synthetic Cfg objects for duplicate docs with same props as the DocCfg they are a duplicate of
for cfg in ALL_CONFIGS:
    for dupe_cfg in cfg.duplicate_cfgs():
        CONFIGS_BY_ID[dupe_cfg.id] = dupe_cfg


# Collect special docs to show with special people
SHOW_WITH_DOCS = {
    id: list(cfgs)
    for id, cfgs in groupby(ALL_CONFIGS, lambda cfg: cfg.show_with_name)
    if id
}


def check_no_overlapping_configs():
    encountered_file_ids = set()

    for cfg in ALL_CONFIGS:
        if cfg.duplicate_of_id:
            assert cfg.duplicate_of_id != cfg.id, f"Bad config! {cfg}"

        if cfg.id in encountered_file_ids:
            raise RuntimeError(f"{cfg.id} configured twice!")

        encountered_file_ids.add(cfg.id)


check_no_overlapping_configs()
