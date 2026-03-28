"""
Epstein money related files. This category makes is_interesting = True.
"""
import re

from epstein_files.documents.config.config_builder import inventory, letter, memo
from epstein_files.documents.config.doc_cfg import EMAIL_TRUNCATE_TO, NO_TRUNCATE, DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.entity import epstein_trust_name
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.env import args
from epstein_files.util.helpers.string_helper import join_truthy

PURCHASE_OF_BIN_ENNAKHILL = 'purchase of Bin Ennakhill palace in Marrakech'
VALAR_FUND = f"{PETER_THIEL}'s {VALAR_VENTURES} fund"

MONEY_OCR_REPAIRS: OcrRepair = {
    re.compile(r"to[ ,]*if[\n ](s?he)[\n ]survives me"): fr"to {REDACTED}, if \1 survives me",
    re.compile(r"[\n ]if[\n ](s?he)[\n ]survives me"): r" if \1 survives me",
    re.compile(r"I give to[\s,]+if (s?he) survives me"): fr"I give to {REDACTED}, if \1 survives me",
    re.compile(r"DB-SDN ?Y-\n(\d{6,7})"): fr"DB-SDNY \1 ",
    'c/o\nApollo Management\nSouthern Trust Company,\nInc.\n':  'c/o Apollo Management Southern Trust Company, Inc.',
    'Southern Trust Company,\nInc.\n$': 'Southern Trust Company, Inc $',
    'Black do\nApollo Management': 'Black c/o Apollo Management',
    re.compile(r'Boothbay Absolute Strategies\nFund LP\n\$'): "Boothbay Absolute Strategies Fund LP $",
    'D.B. Zwim': 'D.B. Zwirn',
}


def cabinet_inventory(id: str, container: str, **kwargs) -> DocCfg:
    """Assumes created 1. by police 2. on Epstein's arrest in 2019, either/both of which may not be true."""
    return inventory(id, container, date='2019-07-06', date_uncertain='assumption', show_full_panel=True, **kwargs)


def deutsche_bank_doc(id: str, note: str, date: str = '', **kwargs) -> DocCfg:
    return DocCfg(id=id, author=DEUTSCHE_BANK, date=date, note=note, **kwargs)


def jpm_doc(id: str, note: str, date: str = '', **kwargs) -> DocCfg:
    return DocCfg(id=id, author=JP_MORGAN, date=date, note=note, **kwargs)


def schwab_doc(id: str, **kwargs) -> DocCfg:
    return DocCfg(id=id, author='Charles Schwab', **kwargs)


def epstein_will(
    id: str,
    date: str = '',
    executors: list[str] | None = None,
    trust: str = '',
    note: str = '',
    **kwargs
) -> DocCfg:
    if trust:
        executor_label = 'trustee'
        will_type = f"death bequests of {epstein_trust_name(trust)}"
    else:
        executor_label = 'executor'
        will_type = "last will and testament"

    note = join_truthy(f"Epstein {will_type}", note)

    if executors:
        executors = sorted(executors)
        note += f" naming {', '.join(executors)} as {executor_label}" + ('s' if len(executors) > 1 else '')

    return DocCfg(id=id, date=date, is_interesting=20, note=note, show_full_panel=True, **kwargs)


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
    DocCfg(id='EFTA00007781', display_text='paychecks signed by Epstein deposited at Colonial Bank', date='2005-08-12'),
    DocCfg(id='EFTA00000476', display_text='photo of JEFFREY EPSTEIN CASH DISBURSEMENTS', date='2006-09-01', is_interesting=False),
    DocCfg(id='EFTA00606411', display_text='proposed jet ownership structure flowchart', date='2017-01-01', date_uncertain='guess'),
    DocCfg(id='EFTA01282282', author=BUTTERFLY_TRUST, note=f"almost completely redacted list of beneficiaries"),
    DocCfg(id='EFTA00803405', author=HONEYCOMB_ASSET_MANAGEMENT, note="fund brochure"),
    DocCfg(id='EFTA02710849', author='Pensum', note='BJAV Marine Ltd / Arcadia Group invoice', is_in_chrono=False),
    DocCfg(
        id='EFTA01413294',
        comment='related to EFTA01357341, EFTA01363125, + more based on Vavilov Street address',
        date='2016-12-16',
        date_uncertain='hard to tell',
        note='compliance report on payment from Epstein to Sberbank account of Nikolay Aleksandrovich Gyrov',
    ),
    DocCfg(
        id='EFTA01480940',
        author=JP_MORGAN,
        date='2011-01-01',
        date_uncertain='tax lien filed 2009-07-21, mentions visits to Epstein in jail',
        highlight_quote='two outstanding federal tax liens totaling $593,789',
        is_interesting=True,
        note=f'due diligence report on {MC2_MODEL_MGMT}',
        truncate_to=(200, 500) if args.output_most_interesting else NO_TRUNCATE
    ),
    DocCfg(
        id='EFTA01111057',
        author=MORTIMER_ZUCKERMAN,
        date='2014-07-10',
        note='Mortimer B. Zuckerman Management Trust',
        non_participants=['Marla Maples'],
    ),
    DocCfg(
        id='EFTA00006069',
        author='NES LLC',
        display_text='W-2 tax form issued for <REDACTED> employee whom Epstein paid $185,323',
        date='2006-01-01'
    ),
    DocCfg(id='EFTA01478313', note=f'list of investments (maybe of {LEON_BLACK})', date='2016-03-31'),
    DocCfg(id='EFTA01222951', note=f"credit card expenses for Carlos L Rodriguez using Plum Card", date='2019-02-12'),
    DocCfg(id='EFTA01583819', note=f"Epstein had control of {JAMES_CAYNE}'s assets"),
    DocCfg(id='EFTA01265973', note="large transfers around time of Epstein arrest", show_full_panel=True),
    DocCfg(id='EFTA01087311', note=f'{LEON_BLACK} Family Partners cash projections'),
    DocCfg(id='EFTA01086463', note=f"{MORTIMER_ZUCKERMAN}'s art collection valuations", is_valid_for_name_scan=False),
    DocCfg(id='EFTA01273102', note=f"payment from Epstein to {RENATA_BOLOTOVA}'s father's account at Sberbank"),
    DocCfg(id='EFTA00238499', note='wire transfer to Signature Bank account'),
    deutsche_bank_doc('EFTA01436428', f"client list showing Hillspire, Third Lake, Southern Financial, Elysium all managed by {STEWART_OLDFIELD}"),
    deutsche_bank_doc('EFTA00166863', f"Southern Financial Know Your Customer form filled out by {PAUL_MORRIS}", date='2019-07-30', truncate_to=(8_400, 10_500)),
    deutsche_bank_doc('EFTA01286706', f"Plan D, LLC bank statement showing $22,500,000 incoming and $15,000,000 outgoing"),
    deutsche_bank_doc('EFTA01361270', f"$60,000 transfer from {SOUTHERN_TRUST_COMPANY} to {BEN_GOERTZEL}'s Novamente", date='2014-01-02'),
    deutsche_bank_doc('EFTA00101280', f"Epstein's {DEUTSCHE_BANK} accounts", show_full_panel=True),
    deutsche_bank_doc('EFTA01681865', "explanations of all of Epstein's large payments prepared for DOJ", '2019-09-12', is_interesting=20),
    deutsche_bank_doc('EFTA00166317', "statement for Epstein's account 690519", date='2016-05-30'),
    deutsche_bank_doc('EFTA01285411', f"statement for Epstein's {SOUTHERN_TRUST_COMPANY} showing $82 million balance"),
    deutsche_bank_doc('EFTA00167059', 'KYC showing Caroline Lang co-ownership with Epstein (?)'),
    deutsche_bank_doc('EFTA00168946', 'KYC information about Southern Financial', '2019-07-11'),
    deutsche_bank_doc('EFTA00165652', 'showing Caroline Lang co-ownership with Epstein (?)'),
    epstein_will(
        'EFTA01266457',
        '2018-05-08',
        [DARREN_INDYKE, RICHARD_KAHN, KATHRYN_RUEMMLER],
        '2018',
        truncate_to=(4_500, 17_000),
    ),
    epstein_will(
        'EFTA01266204',
        '2019-08-08',
        [DARREN_INDYKE, RICHARD_KAHN],
        THE_1953_TRUST,
        "amended 2 days before death",
        truncate_to=(5_500, 15_000),
    ),
    epstein_will(
        'EFTA00099303',  # TODO: dupe of EFTA01266204?
        '2019-08-08',
        [DARREN_INDYKE, RICHARD_KAHN],
        THE_1953_TRUST,
        truncate_to=14_000,
    ),
    epstein_will(
        'EFTA00089546',
        '2007-09-20',
        [HENRY_JARECKI, JAMES_CAYNE, PAUL_HOFFMAN],
        note='codicil',
        truncate_to=(12_870, 13_500),
        # non_participants=[JOI_ITO],
    ),
    epstein_will(
        'EFTA01266268',
        '2017-06-29',
        [DARREN_INDYKE, EVA_DUBIN, KATHRYN_RUEMMLER, RICHARD_KAHN, TERJE_ROD_LARSEN],
        note=f'witnessed by {LEO_LOKING} and {KARYNA_SHULIAK}',
    ),
    epstein_will(
        'EFTA01266403',
        '2015-05-20',
        [DARREN_INDYKE, DAVID_MITCHELL, JES_STALEY],
        '2014',
        note='amendment',
        truncate_to=(4_000, 8_000),
    ),
    epstein_will(
        'EFTA01266298',
        '2003-06-27',
        [GHISLAINE_MAXWELL, IRA_ZICHERMAN],
        '2001',
        note='amendment removing Jeffrey A. Schantz as trustee',
        truncate_to=(4_800, 8_600),
    ),
    epstein_will(
        'EFTA00098341',
        '2019-01-18',
        [DARREN_INDYKE, RICHARD_KAHN],
        truncate_to=(5_000, 16_000),
    ),
    epstein_will('EFTA00099424', '2017-01-30', [DARREN_INDYKE, EVA_DUBIN, RICHARD_KAHN], '2017', truncate_to=(4_600, 14_000)),
    epstein_will('EFTA00016884', '2014-11-18', [DARREN_INDYKE, JES_STALEY, DAVID_MITCHELL, LARRY_SUMMERS], truncate_to=2_500),
    epstein_will('EFTA01266380', '2014-11-18', [DARREN_INDYKE, JES_STALEY, DAVID_MITCHELL], '2014', truncate_to=(4_500, 13_000)),
    cabinet_inventory('EFTA00299850', 'FILE CABINET ONE'),
    cabinet_inventory('EFTA00299927', 'FILE CABINET TWO', note=f"{JAMES_CAYNE} estate plan"),
    inventory('EFTA00300480', 'document binders related to financial transactions', highlight_quote='Sale of 727 to Qatar', truncate_to=1_000),
    memo('EFTA01366011', DARREN_INDYKE, f"$3,000 expense reimbursement for {LASMA_KUHTARSKA}", show_with_name=LASMA_KUHTARSKA),  # TODO: to "marjorie"
    letter('EFTA00587879', DARREN_INDYKE, ['BV70 LLC'], "extremely dodgy charitable donation to Epstein associated co. Gratitude", is_interesting=11),
    DocCfg(id='EFTA00622816', note="Plan D note promising $8,000,000 to Leon Black's BV70 LLC", date='2017-04-17', is_interesting=10, truncate_to=500),
    DocCfg(
        id='EFTA00709105',
        note="Epstein employee payroll 2010",
        date='2011-01-15',
        date_uncertain='approx',
        is_interesting=15,
        show_full_panel=True, # TODO: show image?
        truncate_to=1_600,
    ),
    DocCfg(
        id='EFTA00076491',
        note="inventory of Epstein's estate",
        date='2019-12-31',
        is_interesting=15,
        no_doublespace=True,
        truncate_to=10_000,
    ),

    # JPM
    jpm_doc('EFTA01480542', 'Epstein source of wealth filing'),
    jpm_doc('EFTA01480623', f"was going to drop Epstein as a client until {JES_STALEY} intervened", is_interesting=5, truncate_to=2_050),
    jpm_doc('EFTA01480690', f"Know Your Customer information", date='2013-11-01', date_uncertain="asked to leave Aug 2013"),

    # Jeepers, Inc.
    DocCfg(id='EFTA01255549', note=f'due diligence on {JEEPERS_INC} amusement park owned by Epstein', date='2018-09-27'),
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
        truncate_to=(552, 1_300),
    ),

    # Rothschild
    EmailCfg(
        id='EFTA02586251',
        highlight_quote="please keep Mr Jeffrey Epstein fully informed of the state of our=negotiations with the DOJ",
        recipients=[JEFFREY_EPSTEIN, YVES_PERRIER],
    ),
    EmailCfg(
        id='EFTA01732655',
        is_interesting=10,
        note=f"Epstein and {KATHRYN_RUEMMLER} plan fees for resolving {EDMOND_DE_ROTHSCHILD}'s money laundering issues",
        truncate_to=1_390,
    ),
    EmailCfg(id='EFTA02477238', is_interesting=10, note=f"Epstein sends $250,000 to {TERJE_ROD_LARSEN}", truncate_to=700),
    EmailCfg(id='EFTA01732929', is_interesting=10, note=f"$250,000 to {TERJE_ROD_LARSEN} from {SOUTHERN_TRUST_COMPANY}", truncate_to=500),

    # Schwab
    schwab_doc('EFTA01265978', date='2019-07-10', note='account opened 3 months before death'),

    # Wexner
    letter('EFTA01110729', None, [LES_WEXNER], highlight_quote='You and I had " gang stuff " for over 15 years'),

    # Emails
    EmailCfg(id='032458', note='discussion of acquiring pieces for Epstein\'s art collection', truncate_to=NO_TRUNCATE),
    EmailCfg(id='EFTA00649282', note=f"planning {BILL_GATES} donor advised fund with {JES_STALEY} on board"),
    EmailCfg(id='EFTA02246580', note=f"Epstein commissioning painting of little girl", truncate_to=305),
    EmailCfg(id='EFTA00037187', note=f"Epstein's {DEUTSCHE_BANK} banker Paul Morris lawyers up immediately when contacted by the FBI", is_interesting=5),
    EmailCfg(
        id='EFTA00091269',
        highlight_quote="two weeks before Epstein's arrest, there were several large garbage bags with shredded documents",
    ),
    EmailCfg(
        id='EFTA01409449',
        note=f"{DEUTSCHE_BANK} employees scrubbing Epstein's name off his Souther Financial account (and its TWTR (Twitter) trades)",
        is_interesting=20,
        truncate_to=(10_800, 14_500),
    ),
    EmailCfg(
        id='EFTA00461557',
        author=LESLEY_GROFF,
        author_uncertain='schedule',
        is_interesting=10,
        note=f"{ARIANE_DE_ROTHSCHILD} and {SERGEY_BELYAKOV} visiting at the same time",
    ),
    EmailCfg(
        id='EFTA02189550',
        author='Ike Groff',
        author_uncertain=True,
        note=f"Ike Groff invests $250,000 in Mangrove Partners managed by Nathaniel August",
    ),
    EmailCfg(
        id='EFTA01769169',
        is_interesting=10,
        note='Epstein tells Jean Luc Brunel he can spend up to $25 million (on what?)',
        truncate_to=NO_TRUNCATE,
    ),
    EmailCfg(id='EFTA00570566', truncate_to=500),
    EmailCfg(id='EFTA00457596', note=f"Epstein asking to see Ron Lauder's tax return and will"),
    EmailCfg(id='EFTA01430282', note=f"{DEUTSCHE_BANK} internal discussion of Epstein leaving money to {CELINA_DUBIN} and account closures"),
    EmailCfg(id='EFTA01036804', note=f"Epstein's lawyers advise against his {PURCHASE_OF_BIN_ENNAKHILL}"),
    EmailCfg(id='EFTA00080250', note=f"{LEON_BLACK} / Rothschild Group {DEUTSCHE_BANK} transactions, source of some of Epstein's wealth", is_interesting=10),
    EmailCfg(id='EFTA02633194', note=f'{NICOLE_JUNKERMANN} quotes an appraisal by "FSB (Russians)"', is_interesting=10),
    EmailCfg(id='EFTA01435454', note=f"{DEUTSCHE_BANK} finally sets up a trading account for Epstein's Southern Financial"),
    EmailCfg(id='EFTA02630431', note=f"{CARBYNE} is an Israeli company invested in by Epstein, {NICOLE_JUNKERMANN}, & {EHUD_BARAK}"),
    EmailCfg(
        id='EFTA01375243',
        is_interesting=6,
        note=f"{DEUTSCHE_BANK} anti-money laundering team flags Epstein's $237,270 transfer to {SVETLANA_POZHIDAEVA}'s family",
    ),
    EmailCfg(id='EFTA00836182', note=f'email to investors in {VALAR_FUND}'),
    EmailCfg(id='EFTA00382048', note=f'setting up an ISDA (special account for high volume traders) with {DEUTSCHE_BANK}'),
    EmailCfg(id='EFTA00629657', note=f"arranging {LEON_BLACK}'s finances"),
    EmailCfg(id='EFTA00371120', note=f"Epstein appears to invest in {ATORUS}"),
    EmailCfg(id='EFTA00652799', note=f'Epstein calls Ari Glass "a bit sketchy" despite investing ~$50 million in his fund Boothbay'),
    EmailCfg(id='EFTA01900599', note=f'{JES_STALEY} calls Epstein "boss"'),
    EmailCfg(id='EFTA01388422', note='Nadean Novogratz is probably the sister-in-law of crypto ponzi billionaire Mike Novogratz'),
    EmailCfg(id='EFTA01802355', note=f'{MC2_MODEL_MGMT} line of credit and other people Epstein owes money to/is owed money by'),
    EmailCfg(id='EFTA01870235', note=f'{MC2_MODEL_MGMT} IRS woes and line of credit repayment'),
    EmailCfg(id='EFTA01942664', note=f'payment from {MC2_MODEL_MGMT}'),
    EmailCfg(id='EFTA00552943', note=PURCHASE_OF_BIN_ENNAKHILL),
    EmailCfg(id='EFTA00669222', note=PURCHASE_OF_BIN_ENNAKHILL),
    DocCfg(id='EFTA00585171', note=PURCHASE_OF_BIN_ENNAKHILL),
    EmailCfg(id='EFTA00552220', note=f"{PURCHASE_OF_BIN_ENNAKHILL} (by {KARYNA_SHULIAK}??)", is_interesting=7),
    EmailCfg(
        id='EFTA01816514',
        comment='Different Gary, different Gensler',
        is_interesting=3,
        non_participants=['Gary Gensler'],
        note=f"discussion of open invoices includes $854,598 line of credit for {MC2_MODEL_MGMT}, also Ossa Properties (Mark Epstein)",
        truncate_to=(2_200, 2_900),
    ),
    sar('EFTA01648787', JP_MORGAN, "$1.1 billion in Epstein transfers"),
    EmailCfg(
        id='EFTA01299330',
        note=f"AML / Suspicious Activity report on structured deposits by {DARREN_INDYKE}",
    ),

    # Leon Black
    DocCfg(
        id='EFTA00599517',
        is_interesting=6,
        note=f'list of {LEON_BLACK} companies that {EILEEN_ALEXANDERSON} can make financial transactions for',
        truncate_to=EMAIL_TRUNCATE_TO,
    ),
    EmailCfg(
        id='EFTA01389074',
        author=RICHARD_KAHN,
        date='2017-04-11 18:30:00',
        date_uncertain='based on reply',
        recipients=['Cynthia Rodriguez'],
        show_with_name=LEON_BLACK,
    ),
    EmailCfg(id='EFTA01915851', highlight_quote="we need to create a lie for leon and ronald lauder to own the painting"),
    EmailCfg(id='EFTA01018608', note=f'BV70 and {DEUTSCHE_BANK}'),
    EmailCfg(id='EFTA01376515', show_with_name=LEON_BLACK),
    EmailCfg(id='EFTA00697318', show_with_name=LEON_BLACK),
    EmailCfg(id='EFTA01404535', truncate_to=(1_150, 2_200)),
    EmailCfg(
        id='EFTA00647703',
        highlight_quote='client buying a huge art work, what form should he buy it in',
        is_interesting=True,
        truncate_to=AUTO,
    ),

    # David Stern
    EmailCfg(
        id='EFTA02410642',
        is_interesting=2,
        note=f'"PA" is probably {PRINCE_ANDREW} plus a meeting with {NICOLE_JUNKERMANN}',
        show_with_name=NICOLE_JUNKERMANN,
    ),

    # Joi Ito
    EmailCfg(id='EFTA01964198'),  # no profits/charity
    EmailCfg(id='EFTA01754913'),  # no profits/charity

    # Ehud / Yoni
    EmailCfg(id='EFTA00863806', highlight_quote='please send 10k dollars to yoni'),
    deutsche_bank_doc(id='EFTA01401501', note=f'$10,000 transfer to {YONI_KOREN}'),

    # Trivers
    EmailCfg(id='EFTA00641250', note=f"money for {ROBERT_TRIVERS}", is_in_chrono=False),

    # Misc
    DocCfg(id='EFTA00186431', author='NES, LLC', display_text='159 pages of documents related to finances etc.', is_interesting=True),
    EmailCfg(id='EFTA00420694', note='Offshore Reinsurance', is_in_chrono=False),
    EmailCfg(id='EFTA01030932', note="someone is in a hurry to buy Epstein's jet", is_interesting=True),
]
