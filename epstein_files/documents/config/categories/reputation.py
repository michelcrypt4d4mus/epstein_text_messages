from epstein_files.documents.config.communication_cfg import skype_log
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

AL_SECKEL_BILL_FIGHT = f"{AL_SECKEL} and Epstein fight about the bill for reputation management services"


REPUTATION_CFGS = [
    DocCfg(
        id='030426',
        author=IAN_OSBORNE,
        date='2011-06-14',
        is_interesting=10,
        note=f"Epstein reputation repair proposal citing Michael Milken",
        show_full_panel=True,
    ),
    DocCfg(id='026582', note=f"Epstein's internet search results at start of reputation repair campaign, maybe from {OSBORNE_LLP}"),
    DocCfg(id='030573', note=f"Epstein's unflattering Google search results, maybe screenshot by {AL_SECKEL} or {OSBORNE_LLP}"),
    DocCfg(id='030875', note=f"Epstein's Wikipedia page", date='2014-02-08'),  # Date is based on tyler shears; seckel was 2010
    DocCfg(id='026583', note=f"Google search results for '{JEFFREY_EPSTEIN}' with analysis ({OSBORNE_LLP}?)"),
    DocCfg(id='029350', note=f"Microsoft Bing search results for Epstein with sex offender at top", attached_to_email_id='EFTA00675542'),
    EmailCfg(id='022203', note=AL_SECKEL_BILL_FIGHT, truncate_to=500),
    EmailCfg(id='022219', note=AL_SECKEL_BILL_FIGHT, truncate_to=2404),

    # DOJ files
    DocCfg(
        id='EFTA01810372',
        author=TYLER_SHEARS,
        note=f'invoice for reputation management work',
        is_interesting=True,
        attached_to_email_id='EFTA01931256'
    ),
    skype_log('EFTA01217787', recipients=[TYLER_SHEARS, HANNA_TRAFF]),
    skype_log('EFTA01217703', recipients=[ATHENA_ZELCOVICH, JOSCHA_BACH, LAWRENCE_KRAUSS, TYLER_SHEARS]),
    skype_log('EFTA01217736', recipients=[ATHENA_ZELCOVICH, TYLER_SHEARS], truncate_to=(5000, 5800)),
    EmailCfg(id='EFTA02417620', note=f"{AL_SECKEL} is creating a fake Jeffrey Epstein to improve the real Epstein's Google search results"),
    EmailCfg(id='EFTA00751527', note=f"more details of {AL_SECKEL}'s approach to online reputation repair", recipients=[JEFFREY_EPSTEIN, JESSICA_BANKS], author_reason='visible in EFTA00751523'),
    EmailCfg(id='EFTA01830035', note=AL_SECKEL_BILL_FIGHT),
    EmailCfg(id='EFTA00751523', truncate_to=2_100),
]
