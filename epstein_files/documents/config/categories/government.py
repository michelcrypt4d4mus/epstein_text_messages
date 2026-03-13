from epstein_files.documents.config.config_builder import fbi_defense_witness, fbi_interview, fbi_tip, fbi_report, letter
from epstein_files.documents.config.doc_cfg import NO_TRUNCATE, DocCfg, EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.helpers.string_helper import join_truthy, quote
from epstein_files.util.logging import logger


def bop_doc(id: str, description: str = '', date: str = '', display_text: str = '', **kwargs) -> DocCfg:
    return DocCfg(
        id=id,
        author=BUREAU_OF_PRISONS,
        description=description,
        date=date,
        display_text=display_text,
        **kwargs
    )


def bop_policy_doc(id: str, display_text: str, date: str = '') -> DocCfg:
    """Bureau of prison brochures, poliicy statements, etc."""
    return bop_doc(id, date=date, display_text=display_text)


GOVERNMENT_CFGS = [
    DocCfg(
        id='024117',
        description=f"anti-money laundering (AML), Bank Secrecy Act (BSA), & terrorist financing (CFT) US law FAQ",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA00315076',
        date='2008-06-01',
        date_uncertain=True,
        description=f"visitor list during Epstein's 2009 incarceration in {PALM_BEACH}",
        show_full_panel=True,
    ),
    DocCfg(
        id='EFTA00306074',
        date='2008-06-01',
        date_uncertain=True,
        description=f"approved mail list during Epstein's 2009 incarceration in {PALM_BEACH}",
        show_full_panel=True,
    ),
    bop_doc('EFTA00109783', 'prisoner assignments', '2019-08-03'),
    bop_doc('EFTA00035921', "Lieutenant's Logs", '2019-08-06'),
    bop_doc('EFTA00039153', 'List of Exhibits, Chapter 2', '2019-01-06'),
    bop_doc('EFTA00109163', 'Metropolitan Correctional Center forms showing Konstantin Ignatov', '2019-08-08', is_interesting=True),
    bop_doc('EFTA00120617', '"Prisoner Remand or Order to Deliver" forms', '2019-07-30'),
    bop_doc('EFTA00109654', 'roster of inmates at Metropolitan Correctional Center', '2019-08-08'),
    bop_doc('EFTA00108533', 'roster of inmates at Metropolitan Correctional Center', '2019-07-23'),
    bop_doc('EFTA00108552', 'roster of inmates at Metropolitan Correctional Center', '2019-07-23'),
    bop_doc('EFTA00039025', "report on death of Jeffrey Epstein", is_interesting=True),
    bop_doc('EFTA00039190', 'Special Housing Units', '2016-11-23', is_interesting=False),
    bop_policy_doc('EFTA00120459', 'handwritten log of prisoner movements', date='2019-08-09'),
    bop_policy_doc('EFTA00039227', 'Inmate Discipline Program Statement'),
    bop_policy_doc('EFTA00039295', 'Inmate Telephone Privileges Program Statement'),
    bop_policy_doc('EFTA00039312', 'Program Statement / Memo about BOP Pharmacy Program'),
    bop_policy_doc('EFTA00039351', 'Program Statement / Memo about BOP Pharmacy Program'),
    bop_policy_doc('EFTA00039156', 'Standards of Employee Conduct'),
    DocCfg(
        id='EFTA01125108',
        author='DHS',
        description=f'receipt for I129 Petition for a Nonimmigrant Worker filed by Sublime Art LLC, {ARDA_BESKARDES}',
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA00164939',
        author=DOJ,
        date='2025-09-01',
        date_uncertain='approximate',
        description='Powerpoint summary of Child Sex Trafficking Task Force Epstein investigation',
        is_interesting=True,
    ),
    DocCfg(id='EFTA02731200', author=DOJ, description="memo about potential prosecution of Epstein's assistant"),
    DocCfg(id='EFTA02731082', author=DOJ, description="memo about investigation into Epstein's co-conspirators"),
    DocCfg(id='EFTA02730741', author=DOJ, date='2025-05-01', date_uncertain=True, description="Evidence list for 50D-NY-3027571 Filtering On 'Type(s): 1B'"),
    DocCfg(id='EFTA02730486', author=DOJ, date='2025-05-01', date_uncertain=True, description="Evidence list for 50D-NY-3027571 Filtering On '1A'"),
    DocCfg(id='EFTA00040006', author=DOJ, date='2019-08-27', description='Personal History of Defendant Jeffrey Epstein + grand jury indictment'),
    DocCfg(id='EFTA02731226', author=DOJ, date='2021-03-14', description=f'memo seeking authorization to charge {GHISLAINE_MAXWELL} with additional offenses'),
    DocCfg(id='EFTA00023055', author=FBI, description="evidence of notes left about newly recruited underage girls by girls giving massages"),
    DocCfg(id='EFTA01731217', author=FBI, description=f'requesting INS allow {NADIA_MARCINKO} be allowed to stay in the US because of an ongoing sex-trafficking case', is_interesting=True),
    DocCfg(id='EFTA00247131', author=FBI, description='search warrant for New York house', date='2019-07-07'),
    fbi_defense_witness('EFTA02730267', 'Malcolm Grumbridge', '2022-04-14'),
    fbi_defense_witness('EFTA02730271', REDACTED, '2022-03-22'),
    fbi_defense_witness('EFTA02730477', 'Roderic Alexander', '2022-01-19'),
    # FBI interviews
    fbi_interview('EFTA02858481', 'Jennifer Aros', 'Epstein victim'),
    fbi_interview('EFTA00174375', LUKE_D_THORBURN, f"lot of takes on Epstein, China, and {STEVE_BANNON}"),
    fbi_interview('EFTA00081226', 'minor victim'),
    fbi_interview('EFTA00038915', 'minor victim', 'claims Epstein knew she was 14'),
    fbi_interview('EFTA01246710', PERRY_LANG, "Epstein's chef claims Donald Trump came to Epstein's house for dinner", truncate_to=(6000, 7500)),
    fbi_interview('EFTA00101927', None, f'claims au pair of Glenn and {EVA_DUBIN} was held against her will'),
    fbi_interview('EFTA00159321', None, f'covers {PAOLO_ZAMPOLLI}, Epstein, and the possibility Epstein introduced Melania to Donald Trump'),
    # FBI reports
    fbi_report(
        '018872',
        non_participants=[
            BILL_GATES,
            BILL_RICHARDSON,
            EDUARDO_ROBLES,
            'Eliot Spitzer',
            GERALD_LEFCOURT,
            GLENN_DUBIN,
            JEAN_LUC_BRUNEL,
            JOI_ITO,
            LARRY_SUMMERS,
            LAWRANCE_VISOSKI,  # Just bc his deposition comes soon after
            MARK_EPSTEIN,
            MARTIN_NOWAK,
            MORTIMER_ZUCKERMAN,
            PRINCE_ANDREW,
            SECURITIES_AND_EXCHANGE_COMMISSION,
            STEVEN_HOFFENBERG,
            SVETLANA_POZHIDAEVA
        ],
    ),
    fbi_report('021569'),
    fbi_report('021434', is_valid_for_name_scan=False),
    fbi_report('019352', f"contains clippings of various press items about Epstein"),
    fbi_report(
        'EFTA00129085',
        'wiretap linking phone number in John Gotti / Gambino / Michael Bilotti investigation to phone in Epstein investigation',
        is_interesting=True,
    ),
    fbi_report('EFTA01688746'),
    fbi_report('EFTA00151754', 'declaration of Law Enforcement Officer for Victim of Trafficking', is_interesting=True),
    fbi_report('EFTA00222943', "agent believes computers were removed from Epstein's residence"),
    fbi_report('EFTA01249591', f"allegations against {HENRY_JARECKI}"),
    fbi_report('EFTA00173569', 'hack of FBI Epstein files repository by foreign actor', is_interesting=True),
    fbi_report('EFTA00020506', highlight_quote='chauffeur also told Epstein "I have something on you remember what I buried!"'),
    # FBI tips
    fbi_tip(
        'EFTA01660676',
        "about recently convicted rapists Tal and Oren Alexander at Epstein's house",
        show_full_panel=True,
        url='https://www.bbc.com/news/articles/c6271ngl014o',
    ),
    fbi_tip('EFTA00020490', 'from woman who thinks she encountered Epstein as a young girl'),
    fbi_tip('EFTA00090314', f'about {MASHA_DROKOVA}, Jared Kushner, Ivanka Trump, Chabad, {ALAN_DERSHOWITZ}, etc.', is_interesting=True),
    DocCfg(id='EFTA00084614', author=PALM_BEACH_POLICE, description='incident report detailing the investigation into Jeffrey Epstein'),
    DocCfg(id='EFTA00007893', author=PALM_BEACH_POLICE, description=f"receipts, notes, bank statements of {GHISLAINE_MAXWELL}"),
    DocCfg(id='EFTA00005569', author=PALM_BEACH_POLICE, display_text='photo lineup featuring Epstein', date='2005-03-17'),
    DocCfg(id='EFTA01227877', description='multi entry visa for the Russian Federation', date='2018-06-25', show_full_panel=True),
    DocCfg(id='EFTA00128379', description='analysis of two of Epstein\'s desktop computers', date='2019-01-06', is_interesting=True),
    DocCfg(id='EFTA02730274', description='evidence inventory that appears to have since been deleted from the DOJ website'),
    DocCfg(id='EFTA00263284', description='notes about deceit and sexual manipulation by Australian professor Vincent Bulone', is_interesting=True),
    DocCfg(id='EFTA00001884', description='photo of letter from Virgin Islands DOJ to Epstein', date='2019-03-14'),
    DocCfg(id='EFTA00074744', description="USVI court filing about Epstein will and estate"),
    DocCfg(id='EFTA00007157', description='victim list and police log'),
    letter('EFTA01653121', FBI, ['USCIS'], "regarding an individual's cooperation in the investigation of Epstein and Maxwell"),
    letter('EFTA00098456', PAUL_G_CASSELL, ['Scotland Yard'], 'International Sex Trafficking by Jeffrey Epstein, contains court filings'),

    # Emails
    EmailCfg(
        id='EFTA00129096',
        date='2025-04-03 7:13:35 PM',
        description=f'background check on Tim Draper and {MASHA_DROKOVA}',
        show_full_panel=True,
        truncate_to=NO_TRUNCATE,  # TODO this shouldn't be necessary?
    ),
    EmailCfg(id='EFTA02730483', author=FBI, date='2023-07-11T08:25:00', date_uncertain='actually reply timestamp'),
    EmailCfg(id='EFTA02731552', author=FBI, recipients=[USANYS], date='2021-05-26 16:12:00', recipient_uncertain=True),
    EmailCfg(id='EFTA00039971', author=FBI, recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA00037683', description=f"tip that the murder of DC Madam Jeanne Palfrey might be connected to Epstein's network"),
]
