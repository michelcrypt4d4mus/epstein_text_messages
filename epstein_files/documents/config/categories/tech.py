from epstein_files.documents.config.communication_cfg import sms
from epstein_files.documents.config.config_builder import fedex_invoice
from epstein_files.documents.config.doc_cfg import NO_TRUNCATE, DocCfg
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

    # Emails
    EmailCfg(id='EFTA02068282', recipients=[ANDREW_MCCORMACK]),
    EmailCfg(id='EFTA00955694', note=f"Epstein thanks {ELON_MUSK} for the SpaceX tour that Musk claimed never happened", is_interesting=10),
    EmailCfg(id='EFTA02226642', note=f"{NATHAN_MYHRVOLD} introduces Epstein to {MIROSLAV_LAJCAK}"),
    EmailCfg(id='EFTA01003346', note=f"{PETER_THIEL} tells Epstein to invest in his fund", is_interesting=True),
    EmailCfg(id='EFTA02561277', note=f"planning for {ELON_MUSK} to get a massage", is_interesting=10),
    EmailCfg(
        id='EFTA02186054',
        author_reason='Laurie visible in EFTA02226642',
        recipients=['Claudia Leschuck', 'Laurie Eisenhart'],
        note=f'{NATHAN_MYHRVOLD} meeting',
        truncate_to=1_500,
    ),
    # Chris Poole
    EmailCfg(id='EFTA01848168', show_with_name=CHRIS_POOLE),
    EmailCfg(id='EFTA01849797', show_with_name=CHRIS_POOLE),
    EmailCfg(id='EFTA02179653', show_with_name=CHRIS_POOLE),
    EmailCfg(id='EFTA01987383', show_with_name=CHRIS_POOLE),
    # Diamandis
    EmailCfg(id='EFTA01780987', note='Diamandis claimed he met Epstein in 2013, not 2009'),
    # Valar Ventures
    DocCfg(
        id='EFTA00591045',
        attached_to_email_id='EFTA01001339',
        author=VALAR_VENTURES,
        is_interesting=True,
        note='pitch deck',
        non_participants=[MASAYOSHI_SON],
    ),
    DocCfg(id='EFTA00810239', author=VALAR_VENTURES, note='pitch deck', is_interesting=True),
    DocCfg(id='EFTA00810510', author=VALAR_VENTURES, note='Fall 2016 Update', is_interesting=True),
    DocCfg(id='EFTA00810474', author=VALAR_VENTURES, note='Fall 2018 Update', is_interesting=True),
    DocCfg(id='EFTA01121910', author=VALAR_VENTURES, note="contract", is_interesting=True),
    DocCfg(id='EFTA00808277', author=VALAR_VENTURES, note="contract", is_interesting=True),
    DocCfg(id='EFTA01088484', author=VALAR_VENTURES, note="contract", is_interesting=True),
    DocCfg(id='EFTA00591691', author=VALAR_VENTURES, note="contract", is_interesting=True),
    DocCfg(id='EFTA00810362', author=VALAR_VENTURES, note="investor questionnaire", is_interesting=True),
    DocCfg(id='EFTA00511309', author=KARYNA_SHULIAK, note='personal address book', truncate_to=800),
    DocCfg(id='EFTA00512483', author=KARYNA_SHULIAK, note='personal address book', truncate_to=800),
    EmailCfg(id='EFTA01001339', note=f"{PETER_THIEL} introduces Epstein to the {VALAR_VENTURES} founders", is_interesting=10),
    # Google guys
    EmailCfg(
        id='EFTA02335254',
        date='2003-04-12 19:00:00',
        date_uncertain='approximate based on reply',
        highlight_quote="eric schmidt is founder of google, big supporter of ours",
    ),
    EmailCfg(id='EFTA00958075', truncate_to=NO_TRUNCATE),
    # Evidence
    EmailCfg(id='EFTA00775324', comment='Citrix'),
    EmailCfg(id='EFTA02190185', recipients=[LESLEY_GROFF]),
    EmailCfg(id='EFTA00435053'),
    EmailCfg(id='EFTA00955649', highlight_quote='wipe both', is_interesting=True),
    EmailCfg(id='EFTA02190190', author=LESLEY_GROFF, author_uncertain=True),
    EmailCfg(id='EFTA02190192', author=LESLEY_GROFF, author_uncertain=True),
    EmailCfg(id='EFTA02143396', recipients=[LESLEY_GROFF], is_interesting=10, note='inviting CEO of Google to dinner'),
    EmailCfg(id='EFTA00560756', note="Epstein moving computers out of the house, getting rid of Citrix", is_interesting=4),
    EmailCfg(id='EFTA00705965', note='installing 7 cameras'),
    # Misc
    EmailCfg(id='EFTA00442950', highlight_quote="old hard drives Darren had me review & erase", is_interesting=True, truncate_to=AUTO),
    EmailCfg(id='EFTA02283085', highlight_quote="dont use my name. set a call today with Lori Goler"),
    EmailCfg(id='EFTA00501483', highlight_quote="Jeffrey has asked that James wipe clean"),
    EmailCfg(id='EFTA00501484', highlight_quote="Jeffrey has asked that James wipe clean old computer"),
    EmailCfg(
        id='EFTA02355429',
        highlight_quote="Sh abdallah accepts the dinner with b gates",
        is_interesting=True,
        url='https://x.com/sayerjigmi/status/2037207142101303428',
    ),
    EmailCfg(id='EFTA00853250', highlight_quote='there is talk about the possibility of Clapper attending', truncate_to=AUTO),
]
