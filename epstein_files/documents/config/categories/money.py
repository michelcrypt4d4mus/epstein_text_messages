"""
Epstein money related files. This category makes is_interesting = True.
"""
from epstein_files.documents.config.categories.crypto import VALAR_FUND
from epstein_files.documents.config.config_builder import letter
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import join_truthy


def deutsche_bank(id: str, note: str, date: str = '', **kwargs) -> DocCfg:
    return DocCfg(id=id, author=DEUTSCHE_BANK, date=date, note=note, **kwargs)


def epstein_will(id: str, date: str = '', executors: list[str] | None = None, note: str = '', **kwargs) -> DocCfg:
    note = join_truthy(f"Epstein last will and testament", note)

    if executors:
        note += f" naming {', '.join(executors)} as executor" + ('s' if len(executors) > 1 else '')

    return DocCfg(id=id, date=date, is_interesting=10, note=note, **kwargs)


def sar(id: str, author: str, note: str = '') -> DocCfg:
    return DocCfg(
        id=id,
        author=author,
        is_interesting=10,
        note=join_truthy("Suspicious Activity Report (SAR)", note, ' about '),
        show_full_panel=True,
    )


MONEY_CFGS = [
    # private placement memoranda
    DocCfg(
        id='024432',
        date='2006-09-27',
        note=f"Michael Milken's Knowledge Universe Education (KUE) $1,000,000 corporate share placement notice (SEC filing?)"
    ),
    DocCfg(id='024003', note=f"New Leaf Ventures ($375 million biotech fund) private placement memorandum"),
    letter(id='026134', recipients=['George'], note=f'about opportunities to buy banks in Ukraine'),

    # DOJ files
    DocCfg(id='EFTA01282282', author=BUTTERFLY_TRUST, note=f"almost completely redacted list of beneficiaries"),
    DocCfg(id='EFTA00803405', author=HONEYCOMB_ASSET_MANAGEMENT, note="fund brochure"),
    DocCfg(
        id='EFTA00006069',
        author='NES LLC',
        display_text='W-2 tax form issued for <REDACTED> employee whom Epstein paid $185,323 in 2005',
        date='2006-01-01'
    ),
    DocCfg(
        id='EFTA01413294',
        comment='related to EFTA01357341, EFTA01363125, + more based on Vavilov Street address',
        date='2016-12-16',
        date_uncertain='hard to tell',
        note='compliance report on payment from Epstein to Sberbank account of Nikolay Aleksandrovich Gyrov',
    ),
    DocCfg(
        id='EFTA00173953',
        author=OCDETF,
        note='report on investigations of Epstein related drug money laundering',
        is_interesting=10,
    ),
    deutsche_bank('EFTA01681865', "explanations of all of Epstein's large payments prepared for DOJ", '2019-09-12', is_interesting=20),
    deutsche_bank('EFTA00101280', f"Epstein's {DEUTSCHE_BANK} accounts", show_full_panel=True),
    deutsche_bank('EFTA01361270', f"$60,000 transfer from {SOUTHERN_TRUST_COMPANY} to {BEN_GOERTZEL}'s Novamente", date='2014-01-02'),
    DocCfg(
        id='EFTA01111057',
        author=MORTIMER_ZUCKERMAN,
        date='2014-07-10',
        note='Mortimer B. Zuckerman Management Trust',
        non_participants=['Marla Maples'],
    ),
    DocCfg(
        id='EFTA01480940',
        author=JP_MORGAN,
        highlight_quote='two outstanding federal tax liens totaling $593,789',
        note=f'due diligence report on {MC2_MODEL_MGMT}',
    ),
    DocCfg(id='EFTA01478313', note=f'list of investments (maybe of {LEON_BLACK})', date='2016-03-31'),
    DocCfg(id='EFTA01285411', note=f"bank statement for Epstein's {SOUTHERN_TRUST_COMPANY} showing $82 million balance"),
    DocCfg(id='EFTA01222951', note=f"credit card expenses for Carlos L Rodriguez using Plum Card", date='2019-02-12'),
    DocCfg(
        id='EFTA00257211',
        date='2005-04-05',
        is_interesting=20,
        note=f"call log shows Bank Hapoalim director / future crypto bank SBNY founder Scott Shay selling Epstein investment ideas weeks after Hapoalim money laundering issues, also Steve Cohen and Barry Diller",
        truncate_to=7_700,
    ),
    DocCfg(id='EFTA01266380', note="Epstein's 2014 Trust with bequests"),
    DocCfg(id='EFTA01583819', note=f"Epstein had control of {JAMES_CAYNE}'s assets"),
    DocCfg(id='EFTA00099424', note=f"Epstein 2017 Trust (Eva Andersson Dubin, {DARREN_INDYKE}, {RICHARD_KAHN})"),
    DocCfg(id='EFTA01266457', note=f"Epstein 2018 Trust ({KATHRYN_RUEMMLER}, {DARREN_INDYKE}, {RICHARD_KAHN})"),
    DocCfg(
        id='EFTA01266204',
        note=f"Epstein The 1953 Trust ({DARREN_INDYKE}, {RICHARD_KAHN}) amendment 2 days before death",
        date='2019-08-08',
        is_interesting=20,
        truncate_to=(5_500, 15_000),
    ),
    DocCfg(id='EFTA00299927', note=f"estate plan for {JAMES_CAYNE} found in Epstein's possession"),
    DocCfg(id='EFTA01265973', note="large transfers around time of Epstein arrest", show_full_panel=True),
    DocCfg(id='EFTA01087311', note=f'{LEON_BLACK} Family Partners cash projections'),
    DocCfg(id='EFTA01366011', note=f"memo requesting $3,000 payment to {LASMA_KUHTARSKA}", show_with_name=LASMA_KUHTARSKA),
    DocCfg(id='EFTA01086463', note=f"{MORTIMER_ZUCKERMAN}'s art collection valuations", is_valid_for_name_scan=False),
    DocCfg(id='EFTA00007781', display_text='paychecks signed by Epstein deposited at Colonial Bank', date='2005-08-12'),
    DocCfg(id='EFTA01273102', note=f"payment from Epstein to {RENATA_BOLOTOVA}'s father's account at Sberbank"),
    DocCfg(id='EFTA00000476', display_text='photo of JEFFREY EPSTEIN CASH DISBURSEMENTS', date='2006-09-01', is_interesting=False),
    DocCfg(id='EFTA00238499', note='wire transfer to Signature Bank account'),
    DocCfg(id='EFTA00606411', display_text='proposed jet ownership structure flowchart', date='2017-01-01', date_uncertain='guess'),
    epstein_will('EFTA00016884', '2014-11-18'),
    epstein_will('EFTA00089546', '2007-09-20', [JAMES_CAYNE], 'codicil', non_participants=[JOI_ITO]),

    # Jeepers, Inc.
    DocCfg(id='EFTA01286368', author=DEUTSCHE_BANK, note=f'bank statements showing receipt of $2 million from {JEEPERS_INC}'),
    EmailCfg(id='EFTA01424585', note=f'{DEUTSCHE_BANK} anti-money laundering review of "high risk" {JEEPERS_INC}'),
    EmailCfg(
        id='EFTA01416658',
        highlight_quote="Southern Financial — one of the most complicated client situations I've seen",
        note=f"asking for a promotion based on work on Epstein's account",
        truncate_to=(2_600, 3_600),
    ),
    letter(
        'EFTA00591276',
        'Susman Godfrey',
        ['Fortress Investment Group'],
        highlight_quote='I represent Jeepers, Inc., Financial Trust Company, Inc., and Jeffrey Epstein',
        note="concerning Jeepers, the children's theme park owned by Epstein",
        truncate_to=(500, 1_800),
    ),

    # Emails
    EmailCfg(id='EFTA00037187', is_interesting=True),
    EmailCfg(id='EFTA00994380', highlight_quote='please confirm $500 to Sergey Pozhidaev', truncate_to=500),
    EmailCfg(
        id='EFTA01409449',
        note=f"{DEUTSCHE_BANK} employees scrubbing Epstein's name off his TWTR (Twitter) trades",
        is_interesting=10,
    ),
    EmailCfg(
        id='EFTA00461557',
        author=LESLEY_GROFF,
        author_uncertain='schedule',
        note=f"{ARIANE_DE_ROTHSCHILD} and {SERGEY_BELYAKOV} visiting at the same time",
    ),
    EmailCfg(
        id='EFTA02189550',
        author='Ike Groff',
        author_uncertain=True,
        note=f"Ike Groff invests $250,000 in Mangrove Partners managed by Nathaniel August",
    ),
    EmailCfg(id='EFTA01435454', note=f"{DEUTSCHE_BANK} finally sets up a trading account for Epstein's Southern Financial"),
    EmailCfg(id='EFTA02630431', note=f"{CARBYNE} is an Israeli company invested in by Epstein, {NICOLE_JUNKERMANN}, & {EHUD_BARAK}"),
    EmailCfg(id='EFTA01375243', note=f"{DEUTSCHE_BANK} anti-money laundering team flags Epstein's $237k transfer to {SVETLANA_POZHIDAEVA}'s family"),
    EmailCfg(id='EFTA00836182', note=f'email to investors in {VALAR_FUND}'),
    EmailCfg(id='EFTA00382048', note=f'setting up an ISDA (special account for high volume traders) with {DEUTSCHE_BANK}'),
    EmailCfg(id='EFTA00629657', note=f"arranging {LEON_BLACK}'s finances"),
    EmailCfg(id='EFTA00371120', note=f"Epstein appears to invest in {ATORUS}"),
    EmailCfg(id='EFTA00652799', note=f'Epstein calls Ari Glass "a bit sketchy" despite investing ~$50 million in his fund Boothbay'),
    EmailCfg(id='EFTA01388422', note='Nadean Novogratz is probably the sister-in-law of crypto ponzi billionaire Mike Novogratz'),
    EmailCfg(id='EFTA01802355', note=f'{MC2_MODEL_MGMT} line of credit'),
    EmailCfg(id='EFTA01870235', note=f'{MC2_MODEL_MGMT} line of credit repayment'),
    EmailCfg(id='EFTA01942664', note=f'payment from {MC2_MODEL_MGMT}'),
    EmailCfg(id='EFTA01816514', note=f"list of Epstein's outstanding invoices"),
    sar('EFTA01648787', JP_MORGAN, "$1.1 billion in Epstein transfers"),
]
