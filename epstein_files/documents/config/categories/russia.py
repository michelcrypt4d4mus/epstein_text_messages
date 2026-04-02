from epstein_files.documents.config.doc_cfg import NO_TRUNCATE, DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.config.pic_cfg import PicCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


RUSSIA_CFGS = [
    DocCfg(id='EFTA01227877', note='multi entry visa for the Russian Federation', date='2018-06-25', show_full_panel=True),

    # DOJ
    DocCfg(
        id='EFTA00306033',
        author=SERGEY_BELYAKOV,
        is_interesting=10,
        note='Epstein Russian visa',
        pic_cfg=PicCfg(
            id='EFTA00306033',
        ),
        show_full_panel=True,
    ),
    EmailCfg(id='EFTA01974447', highlight_quote='I know you are going to meet putin on the 20th'),
    EmailCfg(
        id='EFTA00993417',
        author=SERGEY_BELYAKOV,
        highlight_quote="discussed it with A.Simanovsky, deputy head of Central Bank, responsible for BRICS currency",
    truncate_to=1_500,
    ),
    EmailCfg(id='EFTA01926669', author=SERGEY_BELYAKOV),
    EmailCfg(id='EFTA00858688', author=SERGEY_BELYAKOV, note=f"Epstein introduces {EHUD_BARAK} to {SERGEY_BELYAKOV}", is_interesting=10),
    EmailCfg(id='EFTA00704085', author=SERGEY_BELYAKOV, author_reason='response to EFTA00835324'),
    EmailCfg(id='EFTA00923902', note=f"Andrey Vavilov offers to buy Epstein's house for $100 million", truncate_to=NO_TRUNCATE, is_interesting=3),
    EmailCfg(id='EFTA01175429', note=f"Andrey Vavilov offers to buy Epstein's house for $100 million", is_interesting=False),
    EmailCfg(
        id='EFTA01970982',
        highlight_quote="Putin asked that i meet him in st petersburg the same time as his economic conference I told him no no, . If he wants to meet he will need to set aside real time and privacy",
        note='Epstein planning a meeting with Vladimir Putin',
        is_interesting=30,
    ),
    EmailCfg(id='EFTA01914954', note='Epstein planning a meeting with Vladimir Putin', is_interesting=3),
    EmailCfg(
        id='030727',
        note='Epstein requesting help for Russia, discussion of unknown dead Chinese shareholder',
        is_interesting=10,
        truncate_to=400,
    ),
    EmailCfg(id='EFTA02455633', note=f"{MASHA_DROKOVA} loves WeWork", truncate_to=NO_TRUNCATE, is_interesting=2),
    EmailCfg(
        id='EFTA00582171',
        author_reason='addressed to "Umar"',
        duplicate_ids=['EFTA02334771', 'EFTA00581170'],
        recipients=[UMAR_DZHABRAILOV],
    ),
    EmailCfg(id='EFTA00582504', recipients=[UMAR_DZHABRAILOV], author_reason='quoted reply'),
    EmailCfg(id='EFTA00850130', recipients=[SERGEY_BELYAKOV]),
    EmailCfg(
        id='EFTA00852324',
        is_interesting=10,
        note=f"Epstein brings {SERGEY_BELYAKOV} to meet {PETER_THIEL}",
        recipients=[SERGEY_BELYAKOV, JEFFREY_EPSTEIN, 'Elena Bolyakina', PETER_THIEL],
    ),
    # Banks
    EmailCfg(id='EFTA01008774', note='$250,000 transfer to Sberbank account'),

]
