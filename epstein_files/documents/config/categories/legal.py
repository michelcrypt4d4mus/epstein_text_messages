from epstein_files.documents.config.config_builder import JANE_DOE_V_USA, letter, starr_letter
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import as_pattern

# Legal cases
BRUNEL_V_EPSTEIN = f"{JEAN_LUC_BRUNEL} v. {JEFFREY_EPSTEIN} and Tyler McDonald d/b/a YI.org"
EDWARDS_V_DERSHOWITZ = f"{BRAD_EDWARDS} & {PAUL_G_CASSELL} v. {ALAN_DERSHOWITZ}"
EPSTEIN_V_ROTHSTEIN_EDWARDS = f"Epstein v. {SCOTT_ROTHSTEIN}, {BRAD_EDWARDS}, & L.M."
GIUFFRE_V_DERSHOWITZ = f"{VIRGINIA_GIUFFRE} v. {ALAN_DERSHOWITZ}"
GIUFFRE_V_EPSTEIN = f"{VIRGINIA_GIUFFRE} v. {JEFFREY_EPSTEIN}"
GIUFFRE_V_MAXWELL = f"{VIRGINIA_GIUFFRE} v. {GHISLAINE_MAXWELL}"
JANE_DOE_V_EPSTEIN_TRUMP = f"Jane Doe v. Donald Trump and {JEFFREY_EPSTEIN}"
JANE_DOE_2_V_EPSTEIN = f'Jane Doe #2 v. {JEFFREY_EPSTEIN}'
JASTA_SAUDI_LAWSUIT = f"{JASTA} lawsuit against Saudi Arabia by 9/11 victims"
NEW_YORK_V_EPSTEIN = f"New York v. {JEFFREY_EPSTEIN}"
REDACTED_V_EPSTEIN_ESATE = f"{REDACTED} v. Estate of Jeffrey Epstein, {GHISLAINE_MAXWELL}"

# Misc
LEXIS_NEXIS_CVRA_SEARCH = f"{LEXIS_NEXIS} search for case law around the {CVRA}"


LEGAL_CFGS = [
    DocCfg(id='017789', author=ALAN_DERSHOWITZ, note=f'letter to {HARVARD} Crimson complaining he was defamed'),
    DocCfg(id='011908', author=BRUNEL_V_EPSTEIN, note=f"court filing"),
    DocCfg(id='017603', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='017635', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='016509', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(id='017714', author=DAVID_SCHOEN, note=LEXIS_NEXIS_CVRA_SEARCH, date='2019-02-28'),
    DocCfg(
        id='010757',
        author=EDWARDS_V_DERSHOWITZ,
        note=f"plaintiff response to Dershowitz Motion to Determine Confidentiality of Court Records",
        date='2015-11-23',
    ),
    DocCfg(
        id='010887',
        author=EDWARDS_V_DERSHOWITZ,
        note=f"Dershowitz Motion for Clarification of Confidentiality Order",
        date='2016-01-29',
    ),
    DocCfg(
        id='015590',
        author=EDWARDS_V_DERSHOWITZ,
        note=f"Dershowitz Redacted Motion to Modify Confidentiality Order",
        date='2016-02-03',
    ),
    DocCfg(
        id='015650',
        author=EDWARDS_V_DERSHOWITZ,
        note=f"Giuffre Response to Dershowitz Motion for Clarification of Confidentiality Order",
        date='2016-02-08',
    ),
    DocCfg(id='010566', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, note=f"Statement of Undisputed Facts", date='2010-11-04'),
    DocCfg(id='012707', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, note=f"Master Contact List - Privilege Log", date='2011-03-22'),
    DocCfg(id='012103', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, note=f"Telephone Interview with {VIRGINIA_GIUFFRE}", date='2011-05-17'),
    DocCfg(id='029315', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, note=f"Plaintiff Motion for Summary Judgment by {JACK_SCAROLA}", date='2013-09-13'),
    DocCfg(id='013304', author=EPSTEIN_V_ROTHSTEIN_EDWARDS, note=f"Plaintiff Response to Epstein's Motion for Summary Judgment", date='2014-04-17'),
    DocCfg(id='017792', author=GIUFFRE_V_DERSHOWITZ, note=f"article about {ALAN_DERSHOWITZ}'s appearance on Wolf Blitzer"),
    DocCfg(id='017767', author=GIUFFRE_V_DERSHOWITZ, note=f"article about {ALAN_DERSHOWITZ} working with {JEFFREY_EPSTEIN}"),
    DocCfg(id='017796', author=GIUFFRE_V_DERSHOWITZ, note=f"article about {ALAN_DERSHOWITZ}"),
    DocCfg(id='017935', author=GIUFFRE_V_DERSHOWITZ, note=f"defamation complaint", date='2019-04-16'),
    DocCfg(id='017824', author=GIUFFRE_V_DERSHOWITZ, note=f"{MIAMI_HERALD} article by {JULIE_K_BROWN}"),
    DocCfg(
        id='017818',
        author=GIUFFRE_V_DERSHOWITZ,
        note=f"{MIAMI_HERALD} article about accusations against {ALAN_DERSHOWITZ} by {JULIE_K_BROWN}",
        date='2018-12-27',
    ),
    DocCfg(id='017800', author=GIUFFRE_V_DERSHOWITZ, note=f'{MIAMI_HERALD} "Perversion of Justice" by {JULIE_K_BROWN}'),
    DocCfg(id='022237', author=GIUFFRE_V_DERSHOWITZ, note=f"partial court filing with fact checking questions?"),
    DocCfg(id='016197', author=GIUFFRE_V_DERSHOWITZ, note=f"response to Florida Bar complaint by {ALAN_DERSHOWITZ} about David Boies from {PAUL_G_CASSELL}"),
    DocCfg(id='017771', author=GIUFFRE_V_DERSHOWITZ, note=f'Vanity Fair article "The Talented Mr. Epstein" by Vicky Ward', date='2011-06-27'),
    DocCfg(id='014118', author=GIUFFRE_V_EPSTEIN, note=f"Declaration in Support of Motion to Compel Production of Documents", date='2016-10-21'),
    DocCfg(id='014652', author=GIUFFRE_V_MAXWELL, note=f"Complaint", date='2015-04-22'),
    DocCfg(id='015529', author=GIUFFRE_V_MAXWELL, note=f"Defamation Complaint", date='2015-09-21'),
    DocCfg(
        id='014797',
        author=GIUFFRE_V_MAXWELL,
        date='2017-03-17',
        note=f"Declaration of {LAURA_A_MENNINGER} in Opposition to Plaintiff's Motion",
    ),
    DocCfg(id='011304', author=GIUFFRE_V_MAXWELL, note=f"Oral Argument Transcript", date='2017-03-17'),
    DocCfg(
        id='014788',
        author=GIUFFRE_V_MAXWELL,
        date='2017-03-17',
        note=f"Maxwell Response to Plaintiff's Omnibus Motion in Limine",
        duplicate_ids=['011463'],
    ),
    DocCfg(
        id='025937',
        author=JANE_DOE_V_EPSTEIN_TRUMP,
        note=f'Affidavit of Tiffany Doe describing Jane Doe being raped by Epstein and Trump',
        date='2016-06-20',
    ),
    DocCfg(id='025939', author=JANE_DOE_V_EPSTEIN_TRUMP, note=f'Affidavit of Jane Doe describing being raped by Epstein', date='2016-06-20'),
    DocCfg(id='013489', author=JANE_DOE_V_EPSTEIN_TRUMP, note=f'Affidavit of {BRAD_EDWARDS}', date='2010-07-20'),
    DocCfg(id='029398', author=JANE_DOE_V_EPSTEIN_TRUMP, note=f'article in Law.com'),
    DocCfg(id='026854', author=JANE_DOE_V_EPSTEIN_TRUMP, note=f"Civil Docket"),
    DocCfg(id='026384', author=JANE_DOE_V_EPSTEIN_TRUMP, note=f"Complaint for rape and sexual abuse", date='2016-06-20', attached_to_email_id='029837'),
    DocCfg(id='029257', author=JANE_DOE_V_EPSTEIN_TRUMP, note=f'allegations and identity of plaintiff Katie Johnson', date='2016-04-26'),
    DocCfg(id='032321', author=JANE_DOE_V_EPSTEIN_TRUMP, note=f"Notice of Initial Conference", date='2016-10-04'),
    DocCfg(id='010735', author=JANE_DOE_V_USA, note=f"Dershowitz Reply in Support of Motion for Limited Intervention", date='2015-02-02'),
    DocCfg(id='014084', author=JANE_DOE_V_USA, note=f"Jane Doe Response to Dershowitz's Motion for Limited Intervention", date='2015-03-24'),
    DocCfg(
        id='EFTA00020729',
        author=JANE_DOE_V_USA, note=f"declaration of {VIRGINIA_GIUFFRE} claiming threats",
        date='2015-02-06',
        highlight_quote='a call from this supposed FBI Agent made me very scared',
        truncate_to=AUTO,
    ),
    DocCfg(id='023361', author=JASTA_SAUDI_LAWSUIT, note=f"legal text and court documents", date='2012-01-20'),
    DocCfg(id='017830', author=JASTA_SAUDI_LAWSUIT, note=f"legal text and court documents"),
    DocCfg(id='017904', author=JASTA_SAUDI_LAWSUIT, note=f"Westlaw search results", date='2019-01-01'),
    DocCfg(id='014037', author='Journal of Criminal Law and Criminology', note=f"article on {CVRA}"),
    DocCfg(
        id='029416',
        author="National Enquirer / Radar Online v. FBI",
        note=f"FOIA lawsuit filing",
        date='2017-05-25',
        duplicate_ids=['029405']
    ),
    DocCfg(
        id='016420',
        author=NEW_YORK_V_EPSTEIN,
        note=f"New York Post Motion to Unseal Appellate Briefs",
        date='2019-01-11',
    ),
    DocCfg(id='028540', author='SCOTUS', note=f"decision in Budha Ismail Jam et al. v. INTERNATIONAL FINANCE CORP"),
    DocCfg(id='012197', author='SDFL', note=f"response to {JAY_LEFKOWITZ} on Epstein Plea Agreement Compliance"),
    DocCfg(id='022277', note=f"text of National Labour Relations Board (NLRB) law", is_interesting=False),

    # legal letters
    letter(
        '019297',
        "Andrew G. Celli",
        [STANLEY_POTTINGER, PAUL_G_CASSELL, LAURA_A_MENNINGER, 'Sigrid S. McCawley'],
        f"threatening sanctions re: {GIUFFRE_V_MAXWELL}",
    ),
    letter(
        id='026793',
        author=f"Mintz Fraade",
        date='2018-03-23',
        note=f"offering to take over Epstein's business and resolve his legal issues",
        recipients=[DARREN_INDYKE],
    ),
    letter('010560', GLORIA_ALLRED, [SCOTT_J_LINK], "alleging abuse of a girl from Kansas", '2019-06-19'),
    letter('028965', MARTIN_WEINBERG, ['Good Morning America'], "threatening libel lawsuit against ABC", duplicate_ids=['028928']),
    letter('031447', MARTIN_WEINBERG, ['Melanie Ann Pustay', "Sean O'Neill"], "re: Epstein FOIA request", '2015-08-19'),
    letter('020662', f"Mishcon de Reya", ['Daily Mail'], f"threatening libel lawsuit"),
    starr_letter('025353', '2008-05-19', ['010723', '019224'], 'redacted', non_participants=[LANDON_THOMAS]),
    starr_letter('025704', '2008-05-27', ['010732', '019221'], 'redacted'),
    starr_letter('012130', '2008-06-19', ['012135'], non_participants=[LESLEY_GROFF]),

    # DOJ files
    DocCfg(id='EFTA01106135', author=BILL_GATES, note=f"gives Epstein power to negotiate on behalf of {BORIS_NIKOLIC}"),
    DocCfg(id='EFTA01112265', author=EDWARDS_V_DERSHOWITZ, note='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA01125109', author=EDWARDS_V_DERSHOWITZ, note='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA01139414', author=EDWARDS_V_DERSHOWITZ, note='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA00211168', author=JANE_DOE_V_EPSTEIN_TRUMP, note='Epstein employee affidavit alleging sexual assaults'),
    DocCfg(id='EFTA00177201', author=JANE_DOE_V_USA, note='court docket and many filings', is_interesting=True),
    DocCfg(id='EFTA00590940', author=JANE_DOE_V_USA, note='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA01081391', author=JANE_DOE_V_USA, note='interview with minor victim', is_interesting=True),
    DocCfg(id='EFTA00727684', author=f"{REDACTED} v. {JEFFREY_EPSTEIN}", note='sworn testimony, list of co-conspirators'),
    DocCfg(id='EFTA00009440', note='FBI agent testimony on subpoenas of JP Morgan, Western Union, Adult Video Warehouse'),
    DocCfg(id='EFTA00796700', note=f"detailed notes on Epstein's relationship with {ALAN_DERSHOWITZ}", is_interesting=True),
    DocCfg(id='EFTA00143492', note=f"court filing in which a victim calls Giuffre lawyer {STANLEY_POTTINGER} an abuser"),
    DocCfg(id='EFTA00039817', note='notice of hearing', date='2021-04-19', duplicate_ids=['EFTA00039791'], is_interesting=False),
    DocCfg(id='EFTA00005586', display_text='completely redacted 69 pages labeled "Grand Jury - NY"'),

    # emails
    EmailCfg(id='EFTA00039794', recipients=['Michael Danchuk', USANYS]),
]
