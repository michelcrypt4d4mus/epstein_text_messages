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
    EmailCfg(id='025233', is_interesting=True, note='Reputation.com discussion'),
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
    DocCfg(id='EFTA00306981', is_interesting=False),
    skype_log('EFTA01217787', recipients=[TYLER_SHEARS, HANNA_TRAFF]),
    skype_log('EFTA01217703', recipients=[ATHENA_ZELCOVICH, JOSCHA_BACH, LAWRENCE_KRAUSS, TYLER_SHEARS]),
    skype_log('EFTA01217736', recipients=[ATHENA_ZELCOVICH, TYLER_SHEARS], truncate_to=(5_000, 5_800)),
    EmailCfg(id='EFTA01851487', author=CHRISTINA_GALBRAITH, author_reason='topic, cell: in redacted sig'),
    EmailCfg(id='EFTA01851738', author=CHRISTINA_GALBRAITH, author_reason='topic, cell: in redacted sig'),
    EmailCfg(id='EFTA01947908', author=CHRISTINA_GALBRAITH, author_reason='"Christina" appears in EFTA01950559'),
    EmailCfg(id='EFTA01940349', author=CHRISTINA_GALBRAITH, author_uncertain='subject matter'),
    EmailCfg(
        id='EFTA00751527',
        author_reason='visible in EFTA00751523',
        note=f"more details of {AL_SECKEL}'s approach to online reputation repair",
        recipients=[JEFFREY_EPSTEIN, JESSICA_BANKS],
    ),
    EmailCfg(
        id='EFTA01913311',
        duplicate_ids=['EFTA00994273'],
        is_interesting=15,
        note='login/password for jeffreyepsteinnet@gmail.com',
        recipients=[CHRISTINA_GALBRAITH],
    ),
    EmailCfg(id='EFTA01950559', recipients=[CHRISTINA_GALBRAITH], recipient_uncertain='"Christina" in thread'),
    EmailCfg(id='EFTA01745739', recipients=[CHRISTINA_GALBRAITH, JEFFREY_EPSTEIN], author_reason='topic, cell: in redacted sig'),
    EmailCfg(id='EFTA02518357', recipients=[CHRISTINA_GALBRAITH, RICHARD_KAHN], author_reason='"Christina" appears in email'),
    EmailCfg(id='EFTA01830035', note=AL_SECKEL_BILL_FIGHT),
    EmailCfg(id='EFTA00901970', note=f"{AL_SECKEL}'s response to Epstein's forged email", is_interesting=10, truncate_to=3_000),
    EmailCfg(id='EFTA02417620', note=f"{AL_SECKEL} is creating a fake Jeffrey Epstein to improve the real Epstein's Google search results"),
    EmailCfg(id='EFTA00751523', truncate_to=2_100),
    EmailCfg(id='EFTA01838653', note="PR drafts of public statements retracting allegations against Epstein"),
    EmailCfg(id='EFTA00682303', highlight_quote="Harvey Levin, who runs TMZ, is a good friend", is_interesting=True),
]
