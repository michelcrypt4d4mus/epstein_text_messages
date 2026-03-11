from epstein_files.documents.documents.categories import Neutral
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.people.names import THE_REAL_DEAL
from epstein_files.util.constant.strings import (PALM_BEACH, PALM_BEACH_CODE_ENFORCEMENT, PALM_BEACH_TSV,
     PALM_BEACH_PROPERTY_INFO, PALM_BEACH_WATER_COMMITTEE, VIRGIN_ISLANDS)

REAL_DEAL_ARTICLE = 'article by Keith Larsen'


PROPERTY_CFGS = [
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
