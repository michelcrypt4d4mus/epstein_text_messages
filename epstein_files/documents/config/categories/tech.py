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
    EmailCfg(id='EFTA02226642', note=f"Myrhvold introduces Epstein to {MIROSLAV_LAJCAK}"),
]
