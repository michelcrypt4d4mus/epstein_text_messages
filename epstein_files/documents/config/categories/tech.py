from epstein_files.documents.config.communication_cfg import sms
from epstein_files.documents.config.config_builder import fedex_invoice
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


TECH_CFGS = [
    fedex_invoice('EFTA01317889', '2002-11-04', note=DANNY_HILLIS),
    sms(
        'EFTA01614950',
        date='2018-08-17',
        highlight_quote="Musk - fun",
        recipients=[JAMES_STEWART],
        truncate_to=(810, 930),
    ),
    EmailCfg(id='EFTA02226642', note=f"{NATHAN_MYHRVOLD} introduces Epstein to {MIROSLAV_LAJCAK}"),
    EmailCfg(id='EFTA01003346', note=f"{PETER_THIEL} tells Epstein to invest in his fund", is_interesting=True),
    EmailCfg(
        id='EFTA02186054',
        author_reason='Laurie visible in EFTA02226642',
        recipients=['Claudia Leschuck', 'Laurie Eisenhart'],
        note=f'{NATHAN_MYHRVOLD} meeting',
        truncate_to=1_500,
    ),
]
