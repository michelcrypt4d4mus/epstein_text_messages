"""
Epstein money related files. This category makes is_interesting = True.
"""
from epstein_files.documents.config.doc_cfg import DocCfg, EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


MONEY_CFGS = [
    # private placement memoranda
    DocCfg(
        id='024432',
        date='2006-09-27',
        description=f"Michael Milken's Knowledge Universe Education (KUE) $1,000,000 corporate share placement notice (SEC filing?)"
    ),
    DocCfg(id='024003', description=f"New Leaf Ventures ($375 million biotech fund) private placement memorandum"),

    # DOJ files
    DocCfg(
        id='EFTA01413294',
        comment='related to EFTA01357341, efta01363125, + more based on Vavilov Street address',
        date='2016-12-16',
        date_uncertain='hard to tell',
        description='compliance report on payment from Epstein to Sberbank account of Nikolay Aleksandrovich Gyrov',
    ),
    DocCfg(
        id='EFTA00173953',
        author=OCDETF,
        description='report on investigations of Epstein related drug money laundering',
        is_very_interesting=True,
    ),
    DocCfg(
        id='EFTA01681865',
        author=DEUTSCHE_BANK,
        description="explanations of all of Epstein's large payments prepared for DOJ",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA01361270',
        author=DEUTSCHE_BANK,
        date='2014-01-02',
        description=f"$60,000 transfer from {SOUTHERN_TRUST_COMPANY} to {BEN_GOERTZEL}'s Novamente",
    ),
    DocCfg(
        id='EFTA01111057',
        author=MORTIMER_ZUCKERMAN,
        date='2014-07-10',
        description='Mortimer B. Zuckerman Management Trust',
        non_participants=['Marla Maples'],
    ),
    DocCfg(id='EFTA01285411', description=f"bank statement for Epstein's {SOUTHERN_TRUST_COMPANY} showing $82 million balance"),
    DocCfg(id='EFTA01222951', description=f"credit card expenses for Carlos L Rodriguez using Plum Card", date='2019-02-12'),
    DocCfg(id='EFTA00016884', description="Epstein's last will and testament", date='2014-11-18'),
    DocCfg(
        id='EFTA00089546',
        description=f"Epstein last will and testament codicil naming {JAMES_CAYNE} an executor",
        date='2007-09-20',
        non_participants=[JOI_ITO],
    ),
    DocCfg(id='EFTA01266380', description="Epstein's 2014 Trust with bequests"),
    DocCfg(id='EFTA01282282', description=f"Epstein Butterfly Trust (sole beneficiary {KARYNA_SHULIAK})"),
    DocCfg(id='EFTA01583819', description=f"Epstein had control of {JAMES_CAYNE}'s assets"),
    DocCfg(id='EFTA00099424', description=f"Epstein 2017 Trust (Eva Andersson Dubin, {DARREN_INDYKE}, {RICHARD_KAHN})"),
    DocCfg(id='EFTA01266457', description=f"Epstein 2018 Trust ({KATHRYN_RUEMMLER}, {DARREN_INDYKE}, {RICHARD_KAHN})"),
    DocCfg(id='EFTA01266204', description=f"Epstein The 1953 Trust ({DARREN_INDYKE}, {RICHARD_KAHN})", date='2019-08-08'),
    DocCfg(id='EFTA00299927', description=f"estate plan for {JAMES_CAYNE} found in Epstein's possession"),
    DocCfg(id='EFTA01265973', description="large transfers around time of Epstein arrest", show_full_panel=True),
    DocCfg(id='EFTA01087311', description=f'{LEON_BLACK} Family Partners cash projections'),
    DocCfg(id='EFTA01366011', description=f"memo requesting $3,000 payment to {LASMA_KUHTARSKA}", show_with_name=LASMA_KUHTARSKA),
    DocCfg(id='EFTA01086463', description=f"{MORTIMER_ZUCKERMAN}'s art collection valuations", is_valid_for_name_scan=False),
    DocCfg(id='EFTA00007781', description='paychecks signed by Epstein deposited at Colonial Bank', date='2005-08-12'),
    DocCfg(id='EFTA01273102', description=f"payment from Epstein to {RENATA_BOLOTOVA}'s father's account at Sberbank"),
    DocCfg(id='EFTA00238499', description='wire transfer to Signature Bank account'),
    DocCfg(id='EFTA00000476', display_text='photo of JEFFREY EPSTEIN CASH DISBURSEMENTS', date='2006-09-01'),

    # Emails
    EmailCfg(id='EFTA00037187', is_interesting=True),
    EmailCfg(
        id='EFTA01409449',
        description=f"{DEUTSCHE_BANK} employees scrubbing Epstein's name off his TWTR (Twitter) trades",
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA00461557',
        author=LESLEY_GROFF,
        author_uncertain='schedule',
        description=f"{ARIANE_DE_ROTHSCHILD} and {SERGEY_BELYAKOV} visiting at the same time",
    ),
    EmailCfg(
        id='EFTA02189550',
        author='Ike Groff',
        author_uncertain=True,
        description=f"Ike Groff invests $250,000 in Mangrove Partners managed by Nathaniel August",
    ),
    EmailCfg(id='EFTA00371120', description=f"Epstein appears to invest in {ATORUS}"),
    EmailCfg(id='EFTA00652799', description=f'Epstein calls Ari Glass "a bit sketchy" despite investing ~$50 million in his fund Boothbay'),
    EmailCfg(id='EFTA01388422', description='Nadean Novogratz is probably the sister-in-law of crypto ponzi billionaire Mike Novogratz'),
]
