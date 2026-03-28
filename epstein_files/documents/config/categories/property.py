from epstein_files.documents.documents.categories import Neutral
from epstein_files.documents.config.config_builder import press_release
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import THE_REAL_DEAL
from epstein_files.util.constant.strings import (PALM_BEACH, PALM_BEACH_CODE_ENFORCEMENT, PALM_BEACH_TSV,
     PALM_BEACH_PROPERTY_INFO, PALM_BEACH_WATER_COMMITTEE, VIRGIN_ISLANDS)

REAL_DEAL_ARTICLE = 'article by Keith Larsen'


def palm_beach_doc(id: str, note: str) -> DocCfg:
    return DocCfg(id=id, note=note, is_valid_for_name_scan=False)


PROPERTY_CFGS = [
    DocCfg(id='016602', author=PALM_BEACH_CODE_ENFORCEMENT, note='board minutes', date='2008-04-17'),
    DocCfg(id='016554', author=PALM_BEACH_CODE_ENFORCEMENT, note='board minutes', date='2008-07-17', duplicate_ids=['016616', '016574']),
    DocCfg(id='016636', author=PALM_BEACH_WATER_COMMITTEE, note=f"Meeting on January 29, 2009"),
    DocCfg(id='022417', author='Park Partners NYC', note=f"letter to partners in real estate project with architectural plans"),
    DocCfg(id='027068', author=THE_REAL_DEAL, note=f"{REAL_DEAL_ARTICLE} Palm House Hotel Bankruptcy and EB-5 Visa Fraud Allegations"),
    DocCfg(id='029520', author=THE_REAL_DEAL, note=f"{REAL_DEAL_ARTICLE} 'Lost Paradise at the Palm House'", date='2019-06-17'),
    DocCfg(id='016597', author='Trump Properties LLC', note=f'appeal of some decision about Mar-a-Lago by {PALM_BEACH} authorities'),
    DocCfg(id='018743', note=f"Las Vegas property listing"),
    DocCfg(
        id='018727',
        note=f"{VIRGIN_ISLANDS} property deal pitch deck, building will be leased to the U.S. govt GSA",
        date='2014-06-01',
    ),
    palm_beach_doc('016695', f"{PALM_BEACH_PROPERTY_INFO} (?)"),
    palm_beach_doc('016697', f"{PALM_BEACH_PROPERTY_INFO} (?) that mentions Trump"),
    palm_beach_doc('016599', f"{PALM_BEACH_TSV} consumption (water?)"),
    palm_beach_doc('016600', f"{PALM_BEACH_TSV} consumption (water?)"),
    palm_beach_doc('016601', f"{PALM_BEACH_TSV} consumption (water?)"),
    palm_beach_doc('016694', f"{PALM_BEACH_TSV} consumption (water?)"),
    palm_beach_doc('016552', f"{PALM_BEACH_TSV} info"),
    palm_beach_doc('016698', f"{PALM_BEACH_TSV} info (broken?)"),
    palm_beach_doc('016696', f"{PALM_BEACH_TSV} info (water quality?"),
    press_release('026759', 'Great Bay Condominium Owners Association', '2017-09-13', 'Hurricane Irma damage', is_interesting=False),

    # Epstein
    DocCfg(id='EFTA00605620', author='Arthur Gensler', note='contract for architectural work', date='2009-10-06'),
    EmailCfg(id='EFTA02505788', note='building tunnels on the island'),
    EmailCfg(id='EFTA02286220', highlight_quote='I saw yesterday work began on tunnels', is_interesting=True),
    EmailCfg(id='EFTA02636770', highlight_quote="after completing the rebuild o= the bunker below 5palms", truncate_to=501),
]
