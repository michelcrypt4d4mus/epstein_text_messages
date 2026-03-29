from epstein_files.documents.config.config_builder import GIUFFRE_V_MAXWELL, JANE_DOE_V_USA, JANE_DOE_2_V_EPSTEIN, letter, memo
from epstein_files.documents.config.communication_cfg import CommunicationCfg
from epstein_files.documents.config.doc_cfg import NO_TRUNCATE, DocCfg, DuplicateType
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import join_truthy

# Legal cases
BRUNEL_V_EPSTEIN = f"{JEAN_LUC_BRUNEL} v. {JEFFREY_EPSTEIN} and Tyler McDonald d/b/a YI.org"
EDWARDS_V_DERSHOWITZ = f"{BRAD_EDWARDS} & {PAUL_G_CASSELL} v. {ALAN_DERSHOWITZ}"
EPSTEIN_V_ROTHSTEIN_EDWARDS = f"Epstein v. {SCOTT_ROTHSTEIN}, {BRAD_EDWARDS}, & L.M."
GIUFFRE_V_DERSHOWITZ = f"{VIRGINIA_GIUFFRE} v. {ALAN_DERSHOWITZ}"
GIUFFRE_V_EPSTEIN = f"{VIRGINIA_GIUFFRE} v. {JEFFREY_EPSTEIN}"
# JANE_DOE_V_EPSTEIN = f"Jane Doe v. {JEFFREY_EPSTEIN}"
JANE_DOE_V_EPSTEIN_TRUMP = f"Jane Doe v. Donald Trump and {JEFFREY_EPSTEIN}"
JASTA_SAUDI_LAWSUIT = f"{JASTA} lawsuit against Saudi Arabia by 9/11 victims"
NEW_YORK_V_EPSTEIN = f"New York v. {JEFFREY_EPSTEIN}"
REDACTED_V_EPSTEIN_ESATE = f"{REDACTED} v. Estate of Jeffrey Epstein, {GHISLAINE_MAXWELL}"
US_V_EPSTEIN = f'U.S. v. {JEFFREY_EPSTEIN}'
US_V_GHISLAINE = f"U.S. v. {GHISLAINE_MAXWELL}"

# Misc
LEXIS_NEXIS_CVRA_SEARCH = f"{LEXIS_NEXIS} search for case law around the {CVRA}"


def legal_filing(id: str, case_name: str, author: Name = None, note: str = '', date: str = '', **kwargs) -> DocCfg:
    _note = join_truthy(f"court filing", case_name, ' in ')

    return DocCfg(
        id=id,
        author=author,
        note=join_truthy(_note, note, ': '),
        date=date,
        **kwargs
    )


def starr_letter(id: str, date: str, duplicate_ids: list[str], dupe_type: DuplicateType = 'same', **kwargs) -> CommunicationCfg:
    return letter(
        id=id,
        author=KEN_STARR,
        date=date,
        duplicate_ids=duplicate_ids,
        dupe_type=dupe_type,
        note="requesting lenient treatment for Epstein",
        recipients=['Judge Mark Filip'],
        **kwargs
    )


LEGAL_CFGS = [
    DocCfg(id='017789', author=ALAN_DERSHOWITZ, note=f'letter to {HARVARD} Crimson complaining he was defamed'),
    DocCfg(id='017603', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='017635', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='016509', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='017714', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    legal_filing(
        '011908',
        BRUNEL_V_EPSTEIN,
        JEAN_LUC_BRUNEL,
        'Amended Complaint',
        '2015-02-09',
        duplicate_ids=['EFTA00599855'],
        is_interesting=9,
    ),
    legal_filing(
        '010757',
        EDWARDS_V_DERSHOWITZ,
        BRAD_EDWARDS,
        'plaintiff response to Dershowitz Motion to Determine Confidentiality of Court Records',
        '2015-11-23',
    ),
    legal_filing(
        '010887',
        EDWARDS_V_DERSHOWITZ,
        ALAN_DERSHOWITZ,
        'Motion for Clarification of Confidentiality Order',
        '2016-01-29',
    ),
    legal_filing(
        '015590',
        EDWARDS_V_DERSHOWITZ,
        ALAN_DERSHOWITZ,
        'Dershowitz Redacted Motion to Modify Confidentiality Order',
        '2016-02-03',
    ),
    legal_filing(
        '015650',
        EDWARDS_V_DERSHOWITZ,
        VIRGINIA_GIUFFRE,
        'Giuffre Response to Dershowitz Motion for Clarification of Confidentiality Order',
        '2016-02-08',
    ),
    legal_filing(
        'EFTA01102188',
        EPSTEIN_V_ROTHSTEIN_EDWARDS,
        JEFFREY_EPSTEIN,
        'motion to block statements to the press',
        '2011-03-31',
    ),
    legal_filing('010566', EPSTEIN_V_ROTHSTEIN_EDWARDS, note=f"Statement of Undisputed Facts", date='2010-11-04', is_interesting=4),
    legal_filing('012707', EPSTEIN_V_ROTHSTEIN_EDWARDS, note=f"Master Contact List - Privilege Log", date='2011-03-22', is_interesting=9),
    legal_filing('012103', EPSTEIN_V_ROTHSTEIN_EDWARDS, VIRGINIA_GIUFFRE, f"Telephone Interview", '2011-05-17'),
    legal_filing('029315', EPSTEIN_V_ROTHSTEIN_EDWARDS, JACK_SCAROLA, f"Plaintiff Motion for Summary Judgment", '2013-09-13'),
    legal_filing('013304', EPSTEIN_V_ROTHSTEIN_EDWARDS, BRAD_EDWARDS, f"Plaintiff Response to Motion for Summary Judgment", '2014-04-17'),
    legal_filing('EFTA00598330', EPSTEIN_V_ROTHSTEIN_EDWARDS, note='Motion To Preclude At Trial The Use Of The Following Items', date='2013-09-27'),
    legal_filing('017792', GIUFFRE_V_DERSHOWITZ, note=f"article about {ALAN_DERSHOWITZ}'s appearance on Wolf Blitzer"),
    legal_filing('017767', GIUFFRE_V_DERSHOWITZ, note=f"article about {ALAN_DERSHOWITZ} working with {JEFFREY_EPSTEIN}"),
    legal_filing('017796', GIUFFRE_V_DERSHOWITZ, note=f"article about {ALAN_DERSHOWITZ}"),
    legal_filing('017935', GIUFFRE_V_DERSHOWITZ, VIRGINIA_GIUFFRE, "defamation complaint", '2019-04-16'),
    legal_filing('017824', GIUFFRE_V_DERSHOWITZ, JULIE_K_BROWN, f"{MIAMI_HERALD} article"),
    legal_filing(
        '017818',
        GIUFFRE_V_DERSHOWITZ,
        note=f"{MIAMI_HERALD} article about accusations against {ALAN_DERSHOWITZ} by {JULIE_K_BROWN}",
        date='2018-12-27',
    ),
    legal_filing('017800', GIUFFRE_V_DERSHOWITZ, note=f'{MIAMI_HERALD} "Perversion of Justice" by {JULIE_K_BROWN}'),
    legal_filing('022237', GIUFFRE_V_DERSHOWITZ, note=f"partial court filing with fact checking questions?", is_interesting=9),
    legal_filing('016197', GIUFFRE_V_DERSHOWITZ, PAUL_G_CASSELL, f"response to Florida Bar complaint by {ALAN_DERSHOWITZ} about David Boies"),
    legal_filing('017771', GIUFFRE_V_DERSHOWITZ, note=f'Vanity Fair article "The Talented Mr. Epstein" by Vicky Ward', date='2011-06-27'),
    legal_filing('014118', GIUFFRE_V_EPSTEIN, note=f"Declaration in Support of Motion to Compel Production of Documents", date='2016-10-21'),
    legal_filing('014652', GIUFFRE_V_MAXWELL, note=f"Complaint", date='2015-04-22'),
    legal_filing('015529', GIUFFRE_V_MAXWELL, note=f"Defamation Complaint", date='2015-09-21'),
    legal_filing(
        '014797',
        GIUFFRE_V_MAXWELL,
        LAURA_A_MENNINGER,
        "Opposition to Plaintiff's Motion",
        '2017-03-17',
    ),
    legal_filing('011304', GIUFFRE_V_MAXWELL, note=f"Oral Argument Transcript", date='2017-03-17'),
    legal_filing(
        '014788',
        GIUFFRE_V_MAXWELL,
        GHISLAINE_MAXWELL,
        "Response to Plaintiff's Omnibus Motion in Limine",
        date='2017-03-17',
        duplicate_ids=['011463'],
    ),
    legal_filing(
        '025937',
        JANE_DOE_V_EPSTEIN_TRUMP,
        TIFFANY_DOE,
        note=f'Affidavit describing Jane Doe being raped by Epstein and Trump',
        date='2016-06-20',
    ),
    DocCfg(
        id='EFTA00235326',
        # author=JANE_DOE_V_USA,
        date='2007-09-12',
        highlight_quote='spending some quality time with Title 18 looking for misdemeanors',
        non_participants=['MCC'],
        note='long and chummy conversation between Epstein defense attorneys and Florida prosecutors',
        is_interesting=9,
        truncate_to=AUTO
    ),
    legal_filing('EFTA00728793', JANE_DOE_2_V_EPSTEIN, JANE_DOE, note='alleging harassment by private investigators', date='2010-07-02', truncate_to=(1_110, 2_000)),
    legal_filing('025939', JANE_DOE_V_EPSTEIN_TRUMP, JANE_DOE, f'Affidavit describing being raped by Epstein', date='2016-06-20'),
    legal_filing('013489', JANE_DOE_V_EPSTEIN_TRUMP, BRAD_EDWARDS, f'Affidavit', date='2010-07-20'),
    legal_filing('029398', JANE_DOE_V_EPSTEIN_TRUMP, note='article in Law.com'),
    legal_filing('026854', JANE_DOE_V_EPSTEIN_TRUMP, note="Civil Docket"),
    legal_filing('026384', JANE_DOE_V_EPSTEIN_TRUMP, note="Complaint for rape and sexual abuse", date='2016-06-20', attached_to_email_id='029837'),
    legal_filing('029257', JANE_DOE_V_EPSTEIN_TRUMP, 'Katie Johnson', 'allegations and identity of plaintiff', date='2016-04-26'),
    legal_filing('032321', JANE_DOE_V_EPSTEIN_TRUMP, note=f"Notice of Initial Conference", date='2016-10-04'),
    legal_filing('EFTA00206732', JANE_DOE_V_EPSTEIN_TRUMP, note="statement of facts", date='2010-10-30', date_uncertain='approx'),
    legal_filing('010735', JANE_DOE_V_USA, ALAN_DERSHOWITZ, note="Reply in Support of Motion for Limited Intervention", date='2015-02-02'),
    legal_filing('014084', JANE_DOE_V_USA, JANE_DOE, "Response to Motion for Limited Intervention", date='2015-03-24'),
    legal_filing('EFTA00191148', JANE_DOE_V_USA, date='2013-06-19', truncate_to=2_000),
    legal_filing(
        'EFTA00020729',
        JANE_DOE_V_USA,
        VIRGINIA_GIUFFRE,
        "claiming threats from men impersonating FBI agents",
        '2015-02-06',
        highlight_quote='a call from this supposed FBI Agent made me very scared',
        truncate_to=AUTO,
    ),
    legal_filing('023361', JASTA_SAUDI_LAWSUIT, note=f"legal text and court documents", date='2012-01-20'),
    legal_filing('017830', JASTA_SAUDI_LAWSUIT, note=f"legal text and court documents"),
    legal_filing('017904', JASTA_SAUDI_LAWSUIT, note=f"Westlaw search results", date='2019-01-01'),
    legal_filing(
        'EFTA00725932',
        REDACTED_V_EPSTEIN_ESATE,
        JANE_DOE,
        'response to Defendant interrogatories',
        '2009-08-04',
        truncate_to=(3_300, 14_000),
    ),
    legal_filing(
        'EFTA00068582',
        US_V_GHISLAINE,
        note='trial transcript',
        is_interesting=9,
        truncate_to=4_000,
    ),
    DocCfg(
        id='EFTA00129013',
        author=VI_DAILY_NEWS,
        date='2023-05-26',
        note=f"{JP_MORGAN} calls {CECILE_DE_JONGH} Epstein's local fixer",
        truncate_to=(400, 1_400),
    ),
    legal_filing(
        '029416',
        "National Enquirer / Radar Online v. FBI",
        note=f"FOIA lawsuit filing",
        date='2017-05-25',
        duplicate_ids=['029405']
    ),
    legal_filing('016420', NEW_YORK_V_EPSTEIN, 'New York Post', "Motion to Unseal Appellate Briefs", '2019-01-11'),
    DocCfg(id='028540', author='SCOTUS', note=f"decision in Budha Ismail Jam et al. v. INTERNATIONAL FINANCE CORP"),

    # legal letters
    letter(
        '019297',
        "Andrew G. Celli",
        [STANLEY_POTTINGER, PAUL_G_CASSELL, LAURA_A_MENNINGER, 'Sigrid S. McCawley'],
        f"threatening sanctions re: {GIUFFRE_V_MAXWELL}",
    ),
    letter(
        id='026793',
        author='Mintz Fraade',
        date='2018-03-23',
        note="offering to take over Epstein's business and resolve his legal issues",
        recipients=[DARREN_INDYKE],
    ),
    letter('010560', GLORIA_ALLRED, [SCOTT_J_LINK], "alleging abuse of a girl from Kansas", '2019-06-19'),
    letter('028965', MARTIN_WEINBERG, ['Good Morning America'], "threatening libel lawsuit against ABC", duplicate_ids=['028928']),
    letter('031447', MARTIN_WEINBERG, ['Melanie Ann Pustay', "Sean O'Neill"], "re: Epstein FOIA request", '2015-08-19'),
    letter('020662', f"Mishcon de Reya", ['Daily Mail'], f"threatening libel lawsuit"),
    letter('012197', SDFL, [JAY_LEFKOWITZ], "re: Epstein plea agreement compliance w/many legal filings", '2008-05-19'),
    letter(
        'EFTA00177459',
        SDFL,
        ['Robert Josefsberg'],
        'with victim notifications, Palm Beach police investigation, affidavit',
        truncate_to=1200,
        date='2008-09-15',
    ),
    letter('EFTA00625093', MARTIN_WEINBERG, [KATHRYN_RUEMMLER], date='2014-06-01', date_uncertain='guess'),
    letter('EFTA00180294', JAY_LEFKOWITZ, [SDFL], date='2011-07-29'),
    letter('EFTA00210074', 'Kirkland & Ellis', [SDFL], date='2008-09-01', date_uncertain='approx'),
    letter('EFTA00223149', 'Roy Black', [SDFL], 'non-prosecution agreement and more', date='2008-11-24'),
    letter('EFTA01099834', BRAD_EDWARDS, [DOJ], f'filed in {JANE_DOE_V_USA} (multiple letters)', date='2008-10-16'),
    memo(
        'EFTA00727491',
        DARREN_INDYKE,
        f"Epstein whining that his highly paid lawyers couldn't get him off",
        date='2008-09-25',
        is_interesting=10,
        truncate_to=(7_100, 8_600),
    ),
    starr_letter('025353', '2008-05-19', ['010723', '019224'], 'redacted', non_participants=[LANDON_THOMAS]),
    starr_letter('025704', '2008-05-27', ['010732', '019221', 'EFTA00605382'], 'redacted'),
    starr_letter('012130', '2008-06-19', ['012135'], non_participants=[LESLEY_GROFF]),

    # DOJ files
    DocCfg(id='EFTA01106135', author=BILL_GATES, note=f"gives Epstein power to negotiate on behalf of {BORIS_NIKOLIC}"),
    legal_filing('EFTA01112265', EDWARDS_V_DERSHOWITZ, note='interview with minor victim', is_interesting=10),
    legal_filing('EFTA01125109', EDWARDS_V_DERSHOWITZ, note='interview with minor victim', is_interesting=10),
    legal_filing('EFTA01139414', EDWARDS_V_DERSHOWITZ, note='interview with minor victim', is_interesting=10),
    legal_filing('EFTA00211168', JANE_DOE_V_EPSTEIN_TRUMP, note='Epstein employee affidavit alleging sexual assaults', is_interesting=10),
    legal_filing('EFTA00177201', JANE_DOE_V_USA, note='court docket and many filings', is_interesting=10),
    legal_filing('EFTA00590940', JANE_DOE_V_USA, note='interview with minor victim', is_interesting=10),
    legal_filing('EFTA01081391', JANE_DOE_V_USA, note='interview with minor victim', is_interesting=10),
    legal_filing('EFTA00159250', JANE_DOE_2_V_EPSTEIN, note='deposition of witness', is_interesting=10),
    legal_filing('EFTA00727684', f"{REDACTED} v. {JEFFREY_EPSTEIN}", note='sworn testimony, list of co-conspirators', is_interesting=10),
    DocCfg(id='EFTA00143492', note=f"court filing in which a victim calls Giuffre lawyer {STANLEY_POTTINGER} an abuser"),
    DocCfg(id='EFTA00796700', note=f"detailed notes on Epstein's relationship with {ALAN_DERSHOWITZ}", is_interesting=True),
    DocCfg(id='EFTA00009440', note='FBI agent testimony on subpoenas of JP Morgan, Western Union, Adult Video Warehouse'),
    DocCfg(id='EFTA00074744', note="USVI court filing about Epstein will and estate"),
    DocCfg(id='EFTA00005586', display_text='completely redacted 69 pages labeled "Grand Jury - NY"'),
    DocCfg(
        id='EFTA00194840',
        author=DOJ,
        note=f"criminal indictment of {JEFFREY_EPSTEIN}",
        date='2006-07-01',
        date_uncertain='approx',
        is_interesting=5,
        show_full_panel=True,
        truncate_to=(1_400, 2_600),
    ),

    # emails
    EmailCfg(id='EFTA00407717', recipients=[KEN_STARR]),
    EmailCfg(id='EFTA00039794', recipients=['Michael Danchuk', USANYS]),
    EmailCfg(id='EFTA00188608', note=f"contains filing in {JANE_DOE_V_USA}"),

    # uninteresting
    DocCfg(id='022277', note=f"text of National Labour Relations Board (NLRB) law", is_interesting=False),
    DocCfg(id='EFTA00039817', note='notice of hearing', date='2021-04-19', duplicate_ids=['EFTA00039791'], is_interesting=False),
    EmailCfg(id='EFTA00039816', is_interesting=False),
]
