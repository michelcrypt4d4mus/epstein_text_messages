from epstein_files.documents.documents.categories import CONSTANT_CATEGORIES, Interesting, Neutral
from epstein_files.documents.documents.config_builder import FBI_REPORT, fbi_defense_witness, fbi_report, letter
from epstein_files.documents.documents.doc_cfg import NO_TRUNCATE, DocCfg, EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import join_truthy, quote
from epstein_files.util.logging import logger


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
    DocCfg(id='EFTA00109783', author=BUREAU_OF_PRISONS, description='prisoner assignments', date='2019-08-03'),
    DocCfg(id='EFTA00035921', author=BUREAU_OF_PRISONS, description="Lieutenant's Logs", date='2019-08-06'),
    DocCfg(id='EFTA00120617', author=BUREAU_OF_PRISONS, description='"Prisoner Remand or Order to Deliver" forms', date='2019-07-30'),
    DocCfg(id='EFTA00109163', author=BUREAU_OF_PRISONS, description='various Metropolitan Correctional Center forms showing Konstantin Ignatov', date='2019-08-08', is_interesting=True),
    DocCfg(id='EFTA00109654', author=BUREAU_OF_PRISONS, description='roster of inmates at Metropolitan Correctional Center', date='2019-08-08'),
    DocCfg(id='EFTA00108533', author=BUREAU_OF_PRISONS, description='roster of inmates at Metropolitan Correctional Center', date='2019-07-23'),
    DocCfg(id='EFTA00108552', author=BUREAU_OF_PRISONS, description='roster of inmates at Metropolitan Correctional Center', date='2019-07-23'),
    DocCfg(id='EFTA00039153', author=BUREAU_OF_PRISONS, description='List of Exhibits, Chapter 2', date='2019-01-06'),
    DocCfg(id='EFTA00039025', author=BUREAU_OF_PRISONS, description="report on death of Jeffrey Epstein", is_interesting=True),
    DocCfg(id='EFTA00039190', author=BUREAU_OF_PRISONS, description='Special Housing Units', date='2016-11-23', is_interesting=False),
    DocCfg(id='EFTA00120459', author=BUREAU_OF_PRISONS, replace_text_with='handwritten log of prisoner movements', date='2019-08-09'),
    DocCfg(id='EFTA00039227', author=BUREAU_OF_PRISONS, replace_text_with='Inmate Discipline Program Statement'),
    DocCfg(id='EFTA00039295', author=BUREAU_OF_PRISONS, replace_text_with='Inmate Telephone Privileges Program Statement'),
    DocCfg(id='EFTA00039312', author=BUREAU_OF_PRISONS, replace_text_with='Program Statement / Memo about BOP Pharmacy Program'),
    DocCfg(id='EFTA00039351', author=BUREAU_OF_PRISONS, replace_text_with='Program Statement / Memo about BOP Pharmacy Program'),
    DocCfg(id='EFTA00039156', author=BUREAU_OF_PRISONS, replace_text_with='Standards of Employee Conduct'),
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
    DocCfg(
        id='EFTA01246710',
        author=FBI,
        description="interview where Epstein's chef says Donald Trump came to Epstein's house for dinner",
        truncate_to=(6000, 7500),
    ),
    DocCfg(
        id='EFTA00174375',
        author=FBI,
        date='2022-11-18',
        description=f"interview of {LUKE_D_THORBURN} with a lot of takes on Epstein, China, and {STEVE_BANNON}",
    ),
    DocCfg(
        id='EFTA00159321',
        author=FBI,
        description='interview re: Paolo Zampolli, Epstein assaults, and the possibility Epstein introduced Melania to Donald Trump',
    ),
    # https://www.bbc.com/news/articles/c6271ngl014o
    DocCfg(
        id='EFTA01660676',
        author=FBI,
        description='tip about recently convicted rapists Tal and Oren Alexander at Epstein\'s house',
        show_full_panel=True,
    ),
    DocCfg(id='EFTA02858481', author=FBI, description='interview with victim Jennifer Aros'),
    DocCfg(id='EFTA00101927', author=FBI, description=f'interview with someone who mentions au pair of Glenn and {EVA_DUBIN} held against her will'),
    DocCfg(id='EFTA00247131', author=FBI, description='search warrant for New York house', date='2019-07-07'),
    DocCfg(id='EFTA01249591', author=FBI, description=f"allegations against {HENRY_JARECKI}"),
    DocCfg(id='EFTA00081226', author=FBI, description='interview with minor victim'),
    DocCfg(id='EFTA00038915', author=FBI, description='interview with minor victim who said Epstein knew she was 14'),
    DocCfg(id='EFTA00023055', author=FBI, description="evidence of notes left about newly recruited underage girls by girls giving massages"),
    DocCfg(id='EFTA00222943', author=FBI, description=f"agent believes computers were removed from Epstein's residence"),
    DocCfg(id='EFTA00020506', author=FBI, description='"chauffeur told Epstein \'I have something on you, remember what I buried!\'"', show_full_panel=True),
    DocCfg(id='EFTA00084614', author=PALM_BEACH_POLICE, description='incident report detailing the investigation into Jeffrey Epstein'),
    DocCfg(id='EFTA00007893', author=PALM_BEACH_POLICE, description=f"receipts, notes, bank statements of {GHISLAINE_MAXWELL}"),
    DocCfg(id='EFTA00005569', author=PALM_BEACH_POLICE, replace_text_with='photo lineup featuring Epstein', date='2005-03-17'),
    DocCfg(id='EFTA01227877', description='multi entry visa for the Russian Federation', date='2018-06-25', show_full_panel=True),
    DocCfg(id='EFTA00128379', description='analysis of two of Epstein\'s desktop computers', date='2019-01-06', is_interesting=True),
    DocCfg(id='EFTA02730274', description='evidence inventory that appears to have since been deleted from the DOJ website'),
    DocCfg(id='EFTA00263284', description='notes about deceit and sexual manipulation by Australian professor Vincent Bulone', is_interesting=True),
    DocCfg(id='EFTA00001884', description='photo of letter from Virgin Islands DOJ to Epstein', date='2019-03-14'),
    DocCfg(id='EFTA00074744', description="USVI court filing about Epstein will and estate"),
    DocCfg(id='EFTA00007157', description='victim list and police log'),
    fbi_defense_witness('EFTA02730267', 'Malcolm Grumbridge', '2022-04-14'),
    fbi_defense_witness('EFTA02730271', REDACTED, '2022-03-22'),
    fbi_defense_witness('EFTA02730477', 'Roderic Alexander', '2022-01-19'),
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
