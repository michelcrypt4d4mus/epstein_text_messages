from epstein_files.documents.config.communication_cfg import skype_log
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


RUSSIA_CFGS = [
    DocCfg(id='EFTA01227877', note='multi entry visa for the Russian Federation', date='2018-06-25', show_full_panel=True),
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
]
