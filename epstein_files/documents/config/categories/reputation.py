from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

AL_SECKEL_BILL_FIGHT = f"{AL_SECKEL} and Epstein fight about the bill for reputation management services"


REPUTATION_CFGS = [
    DocCfg(id='030426', author=IAN_OSBORNE, note=f"reputation repair proposal citing Michael Milken", date='2011-06-14'),
    DocCfg(id='026582', note=f"Epstein's internet search results at start of reputation repair campaign, maybe from {OSBORNE_LLP}"),
    DocCfg(id='030573', note=f"Epstein's unflattering Google search results, maybe screenshot by {AL_SECKEL} or {OSBORNE_LLP}"),
    DocCfg(id='030875', note=f"Epstein's Wikipedia page", date='2014-02-08'),  # Date is based on tyler shears; seckel was 2010
    DocCfg(id='026583', note=f"Google search results for '{JEFFREY_EPSTEIN}' with analysis ({OSBORNE_LLP}?)"),
    DocCfg(id='029350', note=f"Microsoft Bing search results for Epstein with sex offender at top", attached_to_email_id='EFTA00675542'),
    EmailCfg(id='022203', note=AL_SECKEL_BILL_FIGHT, truncate_to=500),
    EmailCfg(id='022219', note=AL_SECKEL_BILL_FIGHT, truncate_to=2404),

    # DOJ files
    EmailCfg(id='EFTA01830035', note=AL_SECKEL_BILL_FIGHT),
    DocCfg(
        id='EFTA01810372',
        author=TYLER_SHEARS,
        note=f'invoice for reputation management work',
        is_interesting=True,
        attached_to_email_id='EFTA01931256'
    ),
]
