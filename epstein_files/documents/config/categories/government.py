from epstein_files.documents.config.communication_cfg import CommunicationCfg
from epstein_files.documents.config.config_builder import Cfg, fbi_doc, grand_jury, interview, inventory, letter, memo
from epstein_files.documents.config.doc_cfg import EMAIL_TRUNCATE_TO, NO_TRUNCATE, SHORT_TRUNCATE_TO, DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.config.pic_cfg import PicCfg
from epstein_files.documents.documents.categories import Neutral
from epstein_files.people.names import *
from epstein_files.util.constant.strings import AUTO, CVRA, MINOR_VICTIM, REDACTED
from epstein_files.util.helpers.string_helper import join_truthy, quote
from epstein_files.util.logging import logger

ALESSI_WITNESS_PREP = f"witness prep of {JUAN_ALESSI} (Epstein's Palm Beach house manager)"

FBI_REPORT_FIELDS = [
    'Approved By',
    'Case Agent Name',
    'Case ID #',
    'City',
    'Classified By',
    'Contact',
    'Country',
    'Date of Contact',
    'Date of Report',
    'Declassify On',
    'Derived From',
    'Drafted By',
    'Date/Time Received',
    'Details',
    'Field Office/Division',
    'Form Type',
    'Precedence',
    'SentinelCaseld',
    'SentToSentinel',
    'Source ID',
    'Squad',
    'State',
    'Synopsis',
    'Title',
    'Type of Contact',
]


def bop_doc(id: str, note: str = '', date: str = '', display_text: str = '', **kwargs) -> DocCfg:
    return DocCfg(
        id=id,
        author=BUREAU_OF_PRISONS,
        note=note,
        date=date,
        display_text=display_text,
        **kwargs
    )


def bop_internal(id: str, **kwargs) -> EmailCfg:
    return EmailCfg(
        id=id,
        author=BUREAU_OF_PRISONS,
        author_uncertain=True,
        recipients=[BUREAU_OF_PRISONS],
        recipient_uncertain=True,
        **kwargs
    )


def bop_memo(id: str, note: str, date: str = '', **kwargs) -> DocCfg:
    return memo(id, BUREAU_OF_PRISONS, note, date, **kwargs)


def bop_policy_doc(id: str, display_text: str, date: str = '') -> DocCfg:
    """Bureau of prison brochures, poliicy statements, etc."""
    return bop_doc(id, date=date, display_text=display_text)


def doj_doc(id: str, note: str, **kwargs) -> DocCfg:
    return DocCfg(id=id, note=note, author=DOJ, **kwargs)


def doj_memo(id: str, note: str, date: str = '', **kwargs) -> DocCfg:
    return memo(id, DOJ, note, date, **kwargs)


def fbi_defense_witness(id: str, witness: Name, date: str = '') -> DocCfg:
    note = f'Research and Key Findings for {witness or UNKNOWN}, defense witness for {GHISLAINE_MAXWELL}'
    return _set_fbi_doc_fields(DocCfg(id=id, date=date, note=note))


def fbi_evidence_review(id: str) -> EmailCfg:
    return EmailCfg(id=id, author=FBI, recipients=[FBI, NYPD], note='summary of pictures and videos from Epstein computers')


def fbi_internal(id: str, **kwargs) -> EmailCfg:
    return EmailCfg(id=id, author=FBI, recipients=[FBI], **kwargs)


def fbi_interview(id: str, interviewee: Name, note: str = '', date: str = '', **kwargs) -> CommunicationCfg:
    cfg = interview(id, FBI, interviewee, note, date=date, **kwargs)

    if interviewee == MINOR_VICTIM:
        cfg.is_interesting = True

    return _set_fbi_doc_fields(cfg)


def fbi_tip(id: str, tipster: Name, about: str = '', **kwargs) -> DocCfg:
    note_pfx = join_truthy('tip', tipster, ' from ')
    note = join_truthy(note_pfx, about, ' about ')
    return _set_fbi_doc_fields(DocCfg(id=id, note=note, **kwargs))


def fincen_sar(id: str, bank: str, subject: str, activity: str, is_interesting=5, **kwargs) -> DocCfg:
    note = f"Suspicious Activity Report filed by {bank} about {subject} for {activity}"
    return DocCfg(id=id, author=FINCEN, note=note, is_interesting=is_interesting, **kwargs)


def sdfl_internal_email(id: str, **kwargs) -> EmailCfg:
    return EmailCfg(id=id, author=SDFL, recipients=[SDFL], author_uncertain=True, recipient_uncertain=True, **kwargs)


def usanys_internal_email(id: str, **kwargs) -> EmailCfg:
    return EmailCfg(id=id, author=USANYS, recipients=[USANYS], author_uncertain=True, **kwargs)


def _set_fbi_doc_fields(cfg: Cfg) -> Cfg:
    """Mutate `cfg` to set FBI related properties. Returns `cfg` argument for convenience."""
    cfg.author = FBI
    cfg.category = Neutral.GOVERNMENT
    return cfg


GOVERNMENT_CFGS = [
    DocCfg(
        id='024117',
        note=f"anti-money laundering (AML), Bank Secrecy Act (BSA), & terrorist financing (CFT) US law FAQ",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA00315076',
        date='2008-06-01',
        date_uncertain=True,
        note=f"visitor list during Epstein's 2009 incarceration in {PALM_BEACH}",
        show_full_panel=True,
    ),
    DocCfg(
        id='EFTA00173953',
        author=OCDETF,
        date='2015-05-18',
        is_interesting=20,
        note=f"heavily redacted report on Epstein's potential involvement in Caribbean drug money laundering, {MARIANA_IDZKOWSKA}'s name is unredacted",
        truncate_to=(7_700, 12_600),
    ),
    DocCfg(
        id='EFTA00003095',
        date='2019-08-12',
        display_text=f"handwritten evidence inventory of photos from Little St. James Island",
        # TODO: show list image?
    ),

    # OIG
    interview(
        'EFTA00063136',
        DOJ_OIG,
        "BOP employee Hughwon <REDACTED>",
        "about cameras at MCC",
        date='2021-09-29',
    ),
    interview('EFTA00115744', DOJ_OIG, f"{BUREAU_OF_PRISONS} employee retired 2019-12", 'about death of Epstein', date='2021-10-13'),
    interview('EFTA00061927', DOJ_OIG, f"{BUREAU_OF_PRISONS} employee", 'about death of Epstein', date='2021-10-13'),
    DocCfg(id='EFTA00141250', author=DOJ_OIG, note='Q&A on death of Jeffrey Epstein'),
    DocCfg(id='EFTA00062045', author=DOJ_OIG, note='surveillance video analysis', duplicate_ids=['EFTA00141688']),

    interview(
        'EFTA01333100',
        PALM_BEACH_POLICE,
        f"{HALEY_ROBSON} and other victims",
        date='2006-05-01',
        highlight_quote='He told her the younger the better',
        truncate_to=AUTO,
    ),
    interview('EFTA00173820', DOJ, 'possibly employee', 'concerning large sums of money Epstein started giving to employees as he was about to be indicted'),
    bop_doc(
        'EFTA00034357',  # TODO: show an image?
        "internal message about discovery of Epstein's body",
        '2019-08-10',
        background_color='red',
        pic_cfg=PicCfg(
            id='EFTA00034357',
            is_horizontal=True,
        ),
        is_displayed_as_img=True,
    ),
    bop_doc(
        'EFTA00034275',
        "initial form filed about Epstein's suicide attempt",
        '2019-07-23',
        comment='visible in EFTA00019348',
        is_interesting=False,
    ),
    bop_doc(
        'EFTA00019348',
        "report on Epstein's failed suicide attempt",
        '2019-08-02',
        highlight_quote='staff observed inmate Epstein, Jeffrey lying in the fetal position on the floor with a homemade fashioned noose around his neck',
        truncate_to=(7_500, 12_500),
    ),
    bop_doc('EFTA00056410', display_text='suicide watch log from MCC', is_interesting=True),
    bop_doc('EFTA00139235', 'psychological profile of Jeffrey Epstein', date='2020-05-14', is_interesting=True),
    bop_doc('EFTA00035921', "Lieutenant's Logs", '2019-08-06'),
    bop_doc('EFTA00039153', 'List of Exhibits, Chapter 2', '2019-01-06'),
    bop_doc('EFTA00109163', 'Metropolitan Correctional Center forms showing Konstantin Ignatov', '2019-08-08', is_interesting=True),
    bop_doc('EFTA00120617', '"Prisoner Remand or Order to Deliver" forms', '2019-07-30'),
    bop_doc('EFTA00109783', 'prisoner assignments', '2019-08-03'),
    bop_doc('EFTA00109654', 'roster of inmates at Metropolitan Correctional Center', '2019-08-08'),
    bop_doc('EFTA00108533', 'roster of inmates at Metropolitan Correctional Center', '2019-07-23'),
    bop_doc('EFTA00108552', 'roster of inmates at Metropolitan Correctional Center', '2019-07-23'),
    bop_doc('EFTA00039025', "report on death of Jeffrey Epstein", '2023-06-22', is_interesting=10),
    bop_doc('EFTA00039190', 'Special Housing Units', '2016-11-23', is_interesting=False),
    bop_doc('EFTA00142820', 'After Action Review on death of Jeffrey Epstein', date='2019-08-10'),
    bop_memo(
        'EFTA00036336',
        f"Epstein's final phone call (he claime it was to his mother, it was to {KARYNA_SHULIAK})",
        date='2019-08-10',
        duplicate_ids=['EFTA00033630'],
        show_full_panel=True,
        truncate_to=(100, 1_200),
    ),  # TODO: show image?
    bop_memo('EFTA00036136', 'camera project'),
    bop_memo('EFTA00143071', 'Epstein and his cellmate Efrain Reyes', is_interesting=True),
    bop_policy_doc('EFTA00120459', 'handwritten log of prisoner movements', date='2019-08-09'),
    bop_policy_doc('EFTA00039227', 'Inmate Discipline Program Statement'),
    bop_policy_doc('EFTA00039295', 'Inmate Telephone Privileges Program Statement'),
    bop_policy_doc('EFTA00039312', 'Program Statement / Memo about BOP Pharmacy Program'),
    bop_policy_doc('EFTA00039351', 'Program Statement / Memo about BOP Pharmacy Program', date='2004-11-17'),
    bop_policy_doc('EFTA00039156', 'Standards of Employee Conduct'),
    bop_internal('EFTA00035881', highlight_quote="Inmate Epstein seems psychologically stable"),
    bop_internal('EFTA00037760'),
    bop_internal('EFTA00038006'),
    bop_internal('EFTA00037757'),
    bop_internal('EFTA00036154', highlight_quote="Injury report for inmate Epstein"),
    EmailCfg(
        id='EFTA00020596',
        note='Ghislaine has complaints',
        recipients=[BUREAU_OF_PRISONS, CHRISTIAN_EVERDELL],
        recipient_uncertain=True,
    ),

    # DHS
    DocCfg(
        id='EFTA01125108',
        author='DHS',
        note=f'receipt for I129 Petition for a Nonimmigrant Worker filed by Sublime Art LLC, {ARDA_BESKARDES}',
        is_interesting=True,
    ),
    EmailCfg(id='EFTA00109000', author='DHS', recipients=[BUREAU_OF_PRISONS], recipient_uncertain=True),
    EmailCfg(id='EFTA00109041', author='DHS', recipients=[BUREAU_OF_PRISONS], date='2019-10-01', date_uncertain=True),

    # DOJ
    DocCfg(
        id='EFTA00164939',
        author=DOJ,
        date='2025-09-01',
        date_uncertain='approximate',
        duplicate_ids=['EFTA01660622'],
        note='Powerpoint summary of Epstein investigation by Child Sex Trafficking Task Force',
        is_interesting=10,
    ),
    fbi_interview('EFTA01245890', 'girl?', date='2008-01-31', note='meeting on state of Epstein case?'),
    fbi_doc('EFTA00172113', 'case summary'),
    fbi_doc('EFTA00172119', 'case summary', duplicate_ids=['EFTA01649149']),
    fbi_doc('EFTA00173740', 'application for special crime victim visa', is_interesting=True, truncate_to=5_000),
    doj_doc('EFTA00071665', "press release announcing arrest of Jeffrey Epstein", is_interesting=True, truncate_to=4_000),
    doj_doc('EFTA00076023', "press release announcing arrest of Jeffrey Epstein", is_interesting=True, truncate_to=4_000),
    doj_doc('EFTA00157634', ALESSI_WITNESS_PREP, date='2021-12-01', is_interesting=True),
    doj_doc('EFTA00025091', f"arrest warrant and other discovery materials"),
    doj_doc('EFTA00009809', f"sealed indictment of Jeffrey Epstein", date='2019-07-02', is_interesting=2),
    doj_doc('EFTA00191264', "indictment and statement of undisputed facts", is_interesting=6, date='2014-05-02', date_uncertain=True, truncate_to=5_000),
    doj_doc('EFTA00186835', f"subpoena of {PERRY_BARD}", date='2007-03-13'),
    doj_doc('EFTA00163964', 'summary of Epstein and Maxwell Related Investigations', is_interesting=True),
    doj_doc('EFTA01683641', f"video download of MCC cameras failed", date='2019-08-22'),
    doj_memo('EFTA02731039', f'prosecution memo naming {LESLEY_GROFF}', is_interesting=10),
    doj_memo('EFTA02731200', "potential prosecution of Epstein's assistant", is_interesting=10, truncate_to=(14_000, 18_500)),
    doj_memo('EFTA02731082', "investigation into Epstein's co-conspirators"),
    doj_memo('EFTA02731226', f"charging {GHISLAINE_MAXWELL} with additional offenses", '2021-03-14'),
    letter('EFTA00091391', DOJ, [BOBBI_C_STERNHEIM, CHRISTIAN_EVERDELL, LAURA_A_MENNINGER], "evidence list", '2020-10-20'),
    letter('EFTA00141295', BUREAU_OF_PRISONS, [DOJ_OIG], date='2024-07-15'),
    DocCfg(
        id='EFTA00157613',
        author=DOJ,
        date='2021-06-08',
        note=f"witness prep of Juan Alessi (Epstein's former house manager in Palm Beach), describes Trump's visits",
        truncate_to=(6_000, 7_000),
        show_full_panel=True,  # TODO: show pic
    ),
    DocCfg(
        id='EFTA00014822',
        date='1982-06-01',
        date_uncertain=True,
        note=f"fake Austrian passport under the name Marius Robert Fortelni with Saudi Arabian home address that Epstein used to enter several countries, expired in 1987",
        is_displayed_as_img=True,
        url='https://nypost.com/2025/12/23/us-news/jeffrey-epsteins-fake-austrian-passport-pictured-in-latest-doj-document-dump/',
    ),
    DocCfg(id='EFTA02730741', author=DOJ, date='2025-05-01', date_uncertain=True, note="Evidence list for 50D-NY-3027571 Filtering On 'Type(s): 1B'"),
    DocCfg(id='EFTA02730486', author=DOJ, date='2025-05-01', date_uncertain=True, note="Evidence list for 50D-NY-3027571 Filtering On '1A'"),
    DocCfg(id='EFTA00040006', author=DOJ, date='2019-08-27', note='Personal History of Defendant Jeffrey Epstein + grand jury indictment'),
    EmailCfg(id='EFTA00162988', author='DOJ', recipients=['DOJ', FBI], recipient_uncertain=True),
    DocCfg(id='EFTA00042963', note='emails from barket epstein lawfirm?', is_interesting=False),
    DocCfg(id='EFTA01248315', note="list of persons of interest in the Epstein investigation with photos", is_interesting=4),
    DocCfg(id='EFTA00025010', author=SDNY, note='statement of office priorities', is_interesting=False),

    # FBI
    DocCfg(id='EFTA00020832', author=FBI, note='subpoena of Experian'),
    fbi_defense_witness('EFTA02730267', 'Malcolm Grumbridge', '2022-04-14'),
    fbi_defense_witness('EFTA02730477', 'Roderic Alexander', '2022-01-19'),
    fbi_defense_witness('EFTA02730271', None, '2022-03-22'),
    # FBI interviews
    fbi_interview(
        'EFTA00173834',
        'victim',
        author_uncertain=True,
        date='2008-04-01',
        date_uncertain='guess',
        highlight_quote='ZAMPOLLI was "sleazy"',
        show_with_name=PAOLO_ZAMPOLLI,
        truncate_to=AUTO,
    ),
    fbi_interview(
        'EFTA00153851',
        UNKNOWN_GIRL,
        f"{DAVID_BLAINE} and Epstein",
        highlight_quote='BURKLE told that EPSTEIN earned all of this money from having sex with LES WEXNER',
        date='2008-04-01',
        date_uncertain='guess',
        truncate_to=AUTO,
    ),
    fbi_interview('EFTA01246987', MINOR_VICTIM, is_interesting=True, truncate_to=5_000),
    fbi_interview('EFTA00214142', UNKNOWN_GIRL, is_interesting=True, truncate_to=5_000),
    fbi_interview(
        'EFTA00064309',
        'MCC camera technician',
        quote("Only one hard drive of the camera system was working at the time of [Epstein's death]"),
        '2020-03-12',
        highlight_quote='advised that he knew that by replacing both hard drives, the system would be wiped'
    ),
    fbi_interview(
        'EFTA00126948',
        f'{BUREAU_OF_PRISONS} personnel',
        highlight_quote='EPSTEIN claimed that his cellmate, NICHOLAS TARTAGLIONE, tried to take his life',
        truncate_to=(4_250, 5_500),
    ),
    fbi_interview(
        'EFTA01246710',
        PERRY_LANG,
        "Epstein's chef who says Donald Trump came to Epstein's house for dinner",
        is_interesting=10,
        truncate_to=(6_000, 7_500),
    ),
    fbi_interview(
        'EFTA02858481',
        'Jennifer Aros',
        'Epstein and Trump accuser',
        '2019-08-07',
        is_interesting=True,
        truncate_to=(16_500, 20_000),
    ),
    fbi_interview(
        'EFTA01246216',
        LESLEY_GROFF,
        date='2021-09-24',
        highlight_quote="he did not have the number of a trader. GROFF had anxiety trying to get a trader. EPSTEIN did a lot with politics",
        truncate_to=AUTO,
    ),
    fbi_interview('EFTA00004070', 'victim represented by Gloria Allred', 'handwritten notes with pictures', '2019-07-31'),
    fbi_interview('EFTA00270160', UNKNOWN_GIRL),
    fbi_interview('EFTA00112070', 'MCC Psychologist', date='2019-09-04'),
    fbi_interview('EFTA01248273', UNKNOWN_GIRL, date='2020-12-02'),
    fbi_interview('EFTA00153918', 'Gloria Allred', date='2020-01-14'),
    fbi_interview('EFTA00153737', None, f'maybe PBPD police chief {QUESTION_MARKS}'),
    fbi_interview('EFTA01249718', MICHAEL_REITER, date='2020-04-30'),
    fbi_interview('EFTA01249968', UNKNOWN_GIRL, date='2021-01-12'),
    fbi_interview('EFTA01248266', STEVEN_HOFFENBERG, date='2010-12-10'),
    fbi_interview('EFTA01248259', 'Robert Couturier', date='2010-11-16'),
    fbi_interview('EFTA00210958', VIRGINIA_GIUFFRE, date='2013-07-05', is_interesting=True, highlight_quote="1999 began working at Donald Trump's  Mar-A-Lago", truncate_to=AUTO),
    fbi_interview('EFTA00158608', f"{INTERLOCHEN_CENTER_FOR_THE_ARTS} related", date='2020-03-11'),
    fbi_interview('EFTA01309589', ANTHONY_FIGUEROA, 'recruiting from high schools', '2020-08-27', is_interesting=True),
    fbi_interview('EFTA00129035', 'Denise George', date='2023-10-02'),
    fbi_interview('EFTA00086868', 'employee of Next Models', date='2020-04-23', is_interesting=True),
    fbi_interview('EFTA00182344', f"Epstein employee", highlight_quote='I asked you about David Copperfield', is_interesting=True, truncate_to=AUTO),
    fbi_interview('EFTA00159180', DAVID_RODGERS, date='2020-04-23'),
    fbi_interview('EFTA00090339', "Epstein employee", date='2020-11-04'),
    fbi_interview('EFTA00156204', f"{GHISLAINE_MAXWELL}'s receptionist", date='2021-10-08', is_interesting=True),
    fbi_interview('EFTA00159380', '<REDACTED> former Epstein employee', date='2021-05-14', is_interesting=True),
    fbi_interview('EFTA01249911', f"{INTERLOCHEN_CENTER_FOR_THE_ARTS} vice president", date='2021-09-17'),
    fbi_interview('EFTA00174375', LUKE_D_THORBURN, f"lots of takes on Epstein, China, and {STEVE_BANNON}"),
    fbi_interview('EFTA00090600', 'Michael Turnball', date='2020-01-10'),
    fbi_interview('EFTA00040794', "prison guard OFFICER 1", "death of Epstein", date='2019-08-19'),
    fbi_interview('EFTA00075281', "prison guard", "death of Epstein", date='2019-08-16'),
    fbi_interview('EFTA00084954', "prison guard", "death of Epstein", date='2019-08-19'),
    fbi_interview('EFTA00135082', "prison guard", "death of Epstein", date='2019-08-16'),
    fbi_interview('EFTA00081226', MINOR_VICTIM),
    fbi_interview('EFTA00086877', 'victim', date='2020-04-23'),
    fbi_interview('EFTA00105454', MINOR_VICTIM, date='2019-03-22'),
    fbi_interview('EFTA00038915', MINOR_VICTIM, 'claims Epstein knew she was 14'),
    fbi_interview('EFTA00090602', STEVE_SCULLY, date='2019-08-09', show_full_panel=True),
    fbi_interview('EFTA01699136', f"{VIRGINIA_GIUFFRE} and other victims", f'"Turkish girl" might be {GULSUM_OSMANOVA}', date='2011-03-17'),
    fbi_interview('EFTA00101927', None, f"claims Glenn and {EVA_DUBIN}'s Swiss au pair was being held against her will"),
    fbi_interview('EFTA00159321', None, f'covers {PAOLO_ZAMPOLLI}, Epstein, and the possibility Epstein introduced Melania to Donald Trump'),
    # FBI reports
    fbi_doc(
        '018872',
        non_participants=[
            BILL_GATES,
            BILL_RICHARDSON,
            EDUARDO_ROBLES,
            'Eliot Spitzer',
            GERALD_LEFCOURT,
            GLENN_DUBIN,
            JEAN_LUC_BRUNEL,
            # JOI_ITO,
            # LARRY_SUMMERS,
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
    fbi_doc('EFTA00161021', "Director's AM News Briefing", date='2019-09-24'),
    fbi_doc('EFTA00261437', 'review of phone numbers connected to human trafficking', is_interesting=True, truncate_to=4_000),
    fbi_doc('EFTA01301660', f"arrest of {GHISLAINE_MAXWELL}", date='2020-07-21', truncate_to=500, is_interesting=5),
    fbi_doc(
        'EFTA00173481',
        'statement of Aaron E. Spivack re: investigation into missing evidence and cyber intrusion',
        date='2024-01-26',
        highlight_quote="Special Agent Aaron E. Spivack improperly handled, documented, and stored digital evidence and failed to secure CSAM within policy, resulting in a cyber intrusion",
        is_interesting=4,
        truncate_to=EMAIL_TRUNCATE_TO,
        url='https://www.wired.com/story/security-news-this-week-a-hacker-accidentally-broke-into-the-fbis-epstein-files/',
    ),
    fbi_doc('021569'),
    fbi_doc('021434', is_valid_for_name_scan=False),
    fbi_doc('019352', f"contains clippings of various press items about Epstein"),
    fbi_doc(
        'EFTA00129085',
        'wiretap linking phone number in John Gotti / Gambino / Michael Bilotti investigation to phone in Epstein investigation',
        is_interesting=True,
    ),
    fbi_doc('EFTA01688746'),
    fbi_doc('EFTA00036859', date='2019-09-24'),
    fbi_doc(
        'EFTA01682078',
        'investigation targets',
        is_displayed_as_img=True,
        pic_cfg=PicCfg(
            id='EFTA01682078',
            is_horizontal=True,
        ),
    ),
    fbi_doc(
        'EFTA00164480',
        'Epstein death investigation (Powerpoint slides)',
        # background_color='dark_red',
        date='2019-09-01',
        date_uncertain='after death, before scheduled interviews Oct. 18th',
        is_interesting=4,
    ),
    fbi_doc('EFTA00154692', 'Case Initiation Summary', is_interesting=True, truncate_to=5_000),
    fbi_doc('EFTA00172473', 'executive summary of Epstein file release', date='2025-05-01', date_uncertain=True),
    fbi_doc('EFTA00151754', 'declaration of Law Enforcement Officer for Victim of Trafficking', is_interesting=True),
    fbi_doc('EFTA00173569', 'hack of FBI Epstein files repository by foreign actor', is_interesting=True),
    fbi_doc('EFTA00020506', highlight_quote='chauffeur also told Epstein "I have something on you, remember what I buried!"'),
    fbi_doc('EFTA02729877', '"MCC Corruption Case" is about guards on duty when Epstein died', is_interesting=True),
    fbi_doc('EFTA00147020', "status of Epstein death investigation", date='2019-08-13'),
    fbi_doc('EFTA00165518', 'investigation update', date='2019-08-29'),
    fbi_doc('EFTA00129637', 'return of property / case closed / transfer files'),
    fbi_doc('EFTA01731021', 'Serial Number Export Manifest', is_interesting=True, truncate_to=3_000),
    fbi_doc('EFTA00270345', "investigation of Epstein possibly connection to murder of Arthur Shapiro"),
    fbi_doc('EFTA00023055', "evidence of notes left about newly recruited underage girls by girls giving massages"),
    fbi_doc(
        'EFTA01731217',
        f'requesting INS allow {NADIA_MARCINKO} be allowed to stay in the US because of an ongoing sex-trafficking case',
        is_interesting=True,
        show_with_name=NADIA_MARCINKO,
    ),
    fbi_doc('EFTA00247131', 'search warrant for New York house', date='2019-07-07'),
    fbi_doc('EFTA00104913', 'news clips', date='2020-02-12'),
    fbi_doc(
        'EFTA00261337',
        'Bank Secrecy Act, firearm, and border crossing information',
        date='2019-08-29',
        is_interesting=True,
        truncate_to=(19_000, 19_900),
    ),
    fbi_doc('EFTA00108872', f"{STEVEN_HOFFENBERG} info request", is_interesting=False, date='2010-10-25'),
    fbi_doc(
        'EFTA00161465',
        'evidence inventory including',
        date='2025-03-25',
        highlight_quote='List of Absent Items',
        is_interesting=4,
        truncate_to=AUTO,
    ),
    # FBI tips
    fbi_tip(
        'EFTA01660676',
        None,
        "about recently convicted rapists Tal and Oren Alexander at Epstein's house",
        date='2019-08-08',
        highlight_quote="<REDACTED> stated Oren raped <REDACTED> and Oren's brother, Tal, raped a 14 year old girl named <REDACTED>. <REDACTED> tried to slit her wrist after the incident",
        show_full_panel=True,
        truncate_to=AUTO,
        url='https://www.bbc.com/news/articles/c6271ngl014o',
    ),
    fbi_tip(
        'EFTA01249602',
        None,
        highlight_quote="in return for the janitor's silence that Epstein paid the tuition costs for the janitor's son",
        truncate_to=AUTO,
    ),
    fbi_tip('EFTA01249586', None, 'abduction by Jay-Z, Harvey Weinstein, and Jeffrey Epstein', is_interesting=False),
    fbi_tip('EFTA01249232', None, 'Epstein party with little girls and boys', is_interesting=False),
    fbi_tip('EFTA01249591', None, HENRY_JARECKI, show_full_panel=True, show_with_name=HENRY_JARECKI),
    fbi_tip('EFTA01249593', None, LES_WEXNER, show_with_name=LES_WEXNER),
    fbi_tip('EFTA01244950', None, 'Lolita Express'),
    fbi_tip('EFTA00090314', None, f'{MASHA_DROKOVA}, Jared Kushner, Ivanka Trump, Chabad, {ALAN_DERSHOWITZ}, etc.', is_interesting=True),
    fbi_tip('EFTA01246263', None, 'recruiting'),
    fbi_tip('EFTA01244926', None, "Rupert Murdoch's granddaughter", is_interesting=True),
    fbi_tip('EFTA01245217', None, 'trafficking', date='2019-07-29'),
    fbi_tip('EFTA00174720', None, 'trafficking', is_in_chrono=False, comment='not super credible'),
    fbi_tip(
        'EFTA01683874',
        'Confidential Human Source',
        '"Epstein\'s personal hacker"',
        date='2017-11-27',
        is_interesting=10,
        truncate_to=(853, 4_200),
    ),
    fbi_tip('EFTA01249848', 'Erez Zadok', "Epstein's connection to the Wexner Foundation", show_full_panel=True),
    fbi_tip('EFTA01249296', 'former escort', 'Alexander Guest, Ghislaine, and Epstein'),
    fbi_tip('EFTA01249294', 'former escort', 'Alexander Guest, Ghislaine, and Epstein'),
    fbi_tip('EFTA01249291', 'former escort', 'Alexander Guest, Ghislaine, and Epstein'),
    fbi_tip('EFTA01249562', 'John Houshmand', 'cameras'),
    fbi_tip('EFTA01249191', f"{LES_WEXNER}'s former bodyguard", is_interesting=4, show_full_panel=True, show_with_name=LES_WEXNER),
    fbi_tip('EFTA01249623', 'New Mexico police officer', 'Zorro Ranch'),
    fbi_tip('EFTA00128750', 'Reynaldo Clark', "Epstein bribing USVI elected officials", date='2022-10-24', is_interesting=3),
    fbi_tip('EFTA01249643', 'Robert Morosky', LES_WEXNER, is_interesting=6, show_full_panel=True, show_with_name=LES_WEXNER),
    fbi_tip(
        'EFTA00108851',
        STEVEN_HOFFENBERG,
        "Epstein and the murder of Arthur Shapiro",
        date='2010-09-02',
        is_interesting=2,
        truncate_to=(1_700, 2_600),
    ),
    fbi_tip('EFTA01249281', UNKNOWN_GIRL),
    fbi_tip('EFTA00090717', 'victim lawyer', f"allegations against {JES_STALEY}", show_with_name=JES_STALEY),
    fbi_tip(
        'EFTA00096249',
        'whistleblower',
        f"Epstein wiring money to {ALBERT_BRYAN} and other corruption in the Virgin Islands",
        date='2019-07-29',
        truncate_to=(4_200, 5_000),
    ),
    fbi_tip('EFTA00020490', 'woman who thinks she encountered Epstein as a young girl', is_in_chrono=False),
    fbi_tip('EFTA01245108', 'Yaqub Ali', 'reddit username u/Maxwellhill', show_with_name=GHISLAINE_MAXWELL),
    letter('EFTA01249854', 'Erez Zadok', [FBI], "tip about Wexner Foundatoin and Epstein", '2019-08-26', is_interesting=5),

    # Questionable
    fbi_tip('EFTA00099817', None, f"rape at knifepoint by Epstein", is_interesting=False),
    EmailCfg(id='EFTA00154698', note="FBI tip about Marshall Mathers", is_interesting=False),
    EmailCfg(id='EFTA00148385', note='inventory of seized devices', is_interesting=9),
    EmailCfg(id='EFTA01660868', note="re: Epstein's suicide attempt", truncate_to=(1044, 2_600)),
    EmailCfg(
        id='EFTA00172146',
        author=FBI,
        highlight_quote="people inside the FBI have been working night and day to destroy files on these servers",
        recipients=[FBI],
        recipient_uncertain=True,
        truncate_to=AUTO,
    ),
    fbi_internal('EFTA00149112'),
    fbi_internal('EFTA00074466'),
    fbi_internal('EFTA00156644'),
    fbi_internal('EFTA00161528'),
    fbi_internal('EFTA00175111'),
    fbi_internal('EFTA00174043', note=f'death of {JEAN_LUC_BRUNEL}'),
    fbi_internal('EFTA00038448', note=f"Maria Farmer 1996 complaint {QUESTION_MARKS}"),
    fbi_internal('EFTA00037703', note='photos of Epstein cell in MCC'),
    fbi_internal('EFTA00164742', note='summary of video evidence', is_interesting=10),
    fbi_internal('EFTA00078171', note=f're: murder of Arthur Shapiro and {STEVEN_HOFFENBERG}'),
    EmailCfg(
        id='EFTA00146839',
        highlight_quote="did not support federal criminal activity, specifically Obstruction of Justice",
        is_interesting=True,
        is_in_chrono=False,
        truncate_to=AUTO,
    ),
    EmailCfg(id='EFTA00101087', note=f"discussion of scanning of evidence"),
    EmailCfg(id='EFTA00038617', note='scheduling a call', is_interesting=False),
    EmailCfg(id='EFTA00173330', note='concerning destruction of evidence'),

    # FinCEN
    fincen_sar(
        'EFTA01654856',
        'UBS',
        BORGE_BRENDE,
        "peak balance $23.5 million",
        date='2020-03-11',
        truncate_to=(3_600, 9_000),
    ),
    fincen_sar('EFTA01656415', 'Charles Schwab', RICHARD_KAHN, "$45 million transaction"),
    fincen_sar('EFTA01656409', DEUTSCHE_BANK, DARREN_INDYKE, 'structured transactions'),
    fincen_sar('EFTA01656524', 'TD Bank', BELLA_KLEIN, f"millions in transfers involving {NADIA_MARCINKO}'s Aviloop, {RICHARD_KAHN}'s HBRK, and more"),

    # Grand Jury
    grand_jury(
        'EFTA00222943',
        highlight_quote="I believe that certain items were purposely removed from Mr. Epstein's home in anticipation of an execution of a search warrant",
        note='FBI agent testimony',
        truncate_to=AUTO,
    ),
    grand_jury(
        'EFTA00009632',
        date='2007-02-06',
        is_interesting=True,
        note='FBI agent testimony',
        truncate_to=(2_300, 3_500),
    ),
    grand_jury(
        'EFTA01379915',
        date='2020-06-29',
        date_uncertain='Ghislaine grand jury date',
        is_interesting=True,
        note="subpoena of Eric Schmidt's Hillspire",
    ),
    grand_jury('EFTA00016349', note='charge list', date='2008-02-01', date_uncertain='before the arrest?'),
    grand_jury('EFTA00223910', note='FBI agent testimony', date='2007-02-06'),
    DocCfg(id='EFTA00084614', author=PALM_BEACH_POLICE, note='incident report detailing the investigation into Jeffrey Epstein'),
    DocCfg(id='EFTA00007893', author=PALM_BEACH_POLICE, note=f"receipts, notes, bank statements of {GHISLAINE_MAXWELL}"),
    DocCfg(id='EFTA00005569', author=PALM_BEACH_POLICE, display_text='photo lineup featuring Epstein', date='2005-03-17'),
    DocCfg(id='EFTA00003868', author=PALM_BEACH_POLICE, display_text='photo lineup featuring Epstein', date='2006-08-09'),
    DocCfg(id='EFTA00128379', note='analysis of two of Epstein\'s desktop computers', date='2020-01-08', is_interesting=True),
    DocCfg(id='EFTA02730274', note='evidence inventory that appears to have since been deleted from the DOJ website'),
    DocCfg(id='EFTA00263284', note='notes about deceit and sexual manipulation by Australian professor Vincent Bulone', is_interesting=True),
    DocCfg(id='EFTA00001884', note='photo of letter from Virgin Islands DOJ to Epstein', date='2019-03-14'),
    DocCfg(id='EFTA00007157', note='victim list and police log'),
    DocCfg(id='EFTA01649103', date='2025-03-17T22:33:37', note='"MCC Corruption Case" is about guards on duty when Epstein died'),
    DocCfg(id='EFTA00029805', author=DOJ, note='policy doc', is_interesting=False),
    DocCfg(
        id='EFTA00095751',
        author=DOJ,
        is_interesting=10,
        note=f"63 page evidence list from {GHISLAINE_MAXWELL} trial, removed from DOJ site by Pam Bondi DOJ",
        truncate_to=12_000,
    ),
    letter('EFTA01653121', FBI, ['USCIS'], "regarding an individual's cooperation in the investigation of Epstein and Maxwell"),
    letter('EFTA00098456', PAUL_G_CASSELL, ['Scotland Yard'], 'International Sex Trafficking by Jeffrey Epstein, contains court filings'),
    letter(
        'EFTA00016124',
        SDNY,
        [CHRISTIAN_EVERDELL, LAURA_A_MENNINGER, BOBBI_C_STERNHEIM],
        "re: unsearched Epstein computer backups that are no inaccessible",
        '2019-04-09',
        highlight_quote='the Government cannot permit you to review the contents of the Discs',
        truncate_to=(2_900, 3_900),
    ),

    # Emails
    EmailCfg(
        id='EFTA00129096',
        date='2025-04-03 7:13:35 PM',
        note=f'background check on Tim Draper and {MASHA_DROKOVA}',
        show_full_panel=True,
        truncate_to=NO_TRUNCATE,  # TODO this shouldn't be necessary?
    ),
    EmailCfg(id='EFTA00039878', author=BUREAU_OF_PRISONS, author_uncertain=True, recipients=[BUREAU_OF_PRISONS]),
    EmailCfg(id='EFTA00037692', author=BUREAU_OF_PRISONS, author_uncertain=True, recipients=[BUREAU_OF_PRISONS], recipient_uncertain=True),
    EmailCfg(id='EFTA00019994', author=BUREAU_OF_PRISONS, author_uncertain=True, recipients=[BUREAU_OF_PRISONS], recipient_uncertain=True),
    EmailCfg(id='EFTA00037759', author=BUREAU_OF_PRISONS, author_uncertain=True, recipients=[BUREAU_OF_PRISONS], recipient_uncertain=True),
    EmailCfg(id='EFTA00018398', author=BUREAU_OF_PRISONS, author_uncertain=True, recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA00037551', author=BUREAU_OF_PRISONS, recipients=[BUREAU_OF_PRISONS], recipient_uncertain=True),
    EmailCfg(id='EFTA00036630', author=BUREAU_OF_PRISONS, recipients=[BUREAU_OF_PRISONS], note='about cameras'),
    EmailCfg(id='EFTA00039357', author=BUREAU_OF_PRISONS, recipients=[DOJ_OIG]),
    EmailCfg(id='EFTA00019169', author=FBI, author_uncertain=True, recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA02730483', author=FBI, date='2023-07-11T08:25:00', date_uncertain='actually reply timestamp'),
    EmailCfg(id='EFTA02731552', author=FBI, recipients=[USANYS], recipient_uncertain=True, date='2021-05-26 16:12:00'),
    EmailCfg(id='EFTA00039971', author=FBI, recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA00163507', author=FBI, note="quotes from Epstein's cellmate", is_interesting=True),
    EmailCfg(id='EFTA01649194', highlight_quote='Attached please find an updated list of the discrepancies'),
    DocCfg(id='EFTA01649074', attached_to_email_id='EFTA01649194'),
    EmailCfg(id='EFTA00037683', note=f"tip that the murder of DC Madam Jeanne Palfrey might be connected to Epstein's network"),
    EmailCfg(
        id='EFTA00215004',
        author='Alex Acosta',
        highlight_quote='Please do whatever you can to keep this from becoming public',
        note=f"Epstein's lawyer asks Acosta to (illegally) keep the non-prosecution agreement a secret",
        recipients=['USAFLS'],
        truncate_to=1_000,
    ),
    EmailCfg(
        id='EFTA00214992',
        highlight_quote='marching orders regarding what they can tell the girls',
        note=f"not informing victims is a violation of the {CVRA}",
        truncate_to=515,
    ),
    fbi_evidence_review('EFTA01657122'),
    fbi_evidence_review('EFTA01657117'),
    fbi_evidence_review('EFTA01657113'),
    fbi_evidence_review('EFTA01657121'),
    fbi_evidence_review('EFTA01657111'),
    fbi_evidence_review('EFTA01657107'),
    fbi_evidence_review('EFTA01657097'),
    fbi_evidence_review('EFTA01657119'),
    fbi_evidence_review('EFTA01657124'),
    fbi_internal('EFTA01731011'),
    fbi_internal(
        'EFTA00172840',
        note=f'FBI investigation of {DAVID_COPPERFIELD} for rape of a young female closed by prosecutors',
        highlight_quote=f'weak and intimidated by the financial resources of Copperfield',
    ),
    fbi_internal(
        'EFTA01657299',
        highlight_quote='Brunel uses MC2 as a legitimate transport agency of underage girls into America for purposes of sex',
        note=f'interview of {JEAN_LUC_BRUNEL} partner Sergio Cordero',
        truncate_to=(10_240, 14_500),
    ),
    fbi_internal('EFTA00144222'),
    fbi_internal('EFTA01648955'),
    fbi_internal('EFTA00037690', highlight_quote='seems to be a conduit for money paid to female victims', note=BUTTERFLY_TRUST),
    inventory('EFTA00066350', 'Epstein evidence box never obtained from SDFL prosecutor office', is_interesting=10),

    # DOJ / USANYS emails
    EmailCfg(id='EFTA00039967', author='DOJ London', recipients=[USANYS]),
    EmailCfg(
        id='EFTA00039660',
        author='DOJ Chief Psychologist',
        note="report on Epstein's psychological state in jail",
        is_interesting=5,
        recipients=[USANYS],
    ),
    EmailCfg(id='EFTA00040145', date='2021-11-09 17:24:30', is_interesting=False),
    EmailCfg(
        id='EFTA00277089',
        author=USANYS,
        duplicate_ids=['EFTA00151184'],
        note="tip for the FBI / DOJ that Swedish billionaire Johan Eliasch may be connected to Epstein's crimes",
        recipients=[USANYS],
    ),
    EmailCfg(
        id='EFTA00157083',
        author=USANYS,
        highlight_quote='In his keychain he had the following passwords',
        note='list of passwords commonly used by Epstein',
        truncate_to=(1_054, 6_400),
    ),
    EmailCfg(id='EFTA00165126', author=UNKNOWN_GIRL, recipients=[FBI], note='sending a tip about Epstein to [someone]', recipient_uncertain=True),
    EmailCfg(id='EFTA00039796', author=SDNY, recipients=[USANYS]),
    fbi_internal('EFTA00021353'),
    fbi_internal('EFTA00147046'),
    fbi_internal('EFTA00148374'),

    # SDFL
    DocCfg(
        id='EFTA00181807',
        author='Florida Dept of Corrections',
        date='2010-07-21',
        is_interesting=10,
        note='probation records for Jeffrey Epstein',
        truncate_to=400,
    ),
    DocCfg(id='EFTA00225378', author=SDFL, note="NYC travel authorization", date='2008-06-20'),
    sdfl_internal_email('EFTA00215139'),
    sdfl_internal_email('EFTA00214699'),
    sdfl_internal_email('EFTA00179797', note=f"many emails concerning {DAVID_COPPERFIELD} investigation and more"),  # TODO: split up
    sdfl_internal_email(
        'EFTA00223748',
        highlight_quote="We are pretty sure we can charge DC and his assistants with a conspiracy of 1201 (kidnapping)",
        note=f'investigation of {DAVID_COPPERFIELD}',
        truncate_to=AUTO,
    ),
    EmailCfg(id='EFTA00095379', author=SDFL),
    EmailCfg(id='EFTA00176910', author='USAFLS', author_uncertain=True),
    EmailCfg(id='EFTA00211910', author='USAFLS', recipients=['USAWAW']),

    # USANYS
    EmailCfg(
        id='EFTA00039989',
        is_interesting=4,
        note=f"ICE has an immigration hold on a man who might have important info about the Epstein case",
    ),
    EmailCfg(id='EFTA00094900', author=USANYS, recipients=[BUREAU_OF_PRISONS], recipient_uncertain=True),
    EmailCfg(id='EFTA00068446', author=USANYS, author_uncertain=True, recipients=['NY FBI'], note='evidence discussion'),
    EmailCfg(id='EFTA00089743', author=USANYS, note='evidence discussion'),
    EmailCfg(id='EFTA00019171', author=USANYS, is_interesting=False),
    EmailCfg(id='EFTA00090656', author=FBI, recipients=[USANYS], recipient_uncertain=True, note='evidence discussion'),
    EmailCfg(id='EFTA00076059', author='SDNY Public Corruption Unit', recipients=[USANYS], duplicate_ids=['EFTA00076060', 'EFTA00097444']),
    usanys_internal_email('EFTA00009965', is_fwded_article=True),
    usanys_internal_email('EFTA00019177', is_fwded_article=True),
    usanys_internal_email('EFTA00031633', is_interesting=False),
    usanys_internal_email('EFTA00096366', note=f"allegations against {LEON_BLACK}", is_interesting=True),
    usanys_internal_email('EFTA00098000', note='evidence discussion'),
    usanys_internal_email('EFTA01660651', note='list of Trump accusers', is_interesting=10),
    usanys_internal_email('EFTA00105304', note='overfiew of financial activity', is_interesting=True),
    usanys_internal_email('EFTA00101557', note='press release info around Epstein 2019 arrest'),
    usanys_internal_email('EFTA00079595', note=f'request for info on {JEAN_LUC_BRUNEL} from French police'),
    usanys_internal_email('EFTA00098034', duplicate_ids=['EFTA00089863']),
    usanys_internal_email('EFTA00020141', truncate_to=NO_TRUNCATE),
    usanys_internal_email('EFTA00164897', note='video inventory'),
    usanys_internal_email('EFTA00018778'),
    usanys_internal_email('EFTA00212635'),
    usanys_internal_email('EFTA00009802'),
    usanys_internal_email('EFTA00010440'),
    usanys_internal_email('EFTA02731615'),
    usanys_internal_email('EFTA00211150'),
    usanys_internal_email('EFTA00030842'),
    usanys_internal_email('EFTA00099174'),
    usanys_internal_email('EFTA02731684'),
    usanys_internal_email('EFTA02731485'),
    usanys_internal_email('EFTA00100420'),
    usanys_internal_email('EFTA02731736'),
    usanys_internal_email('EFTA02731478'),
    usanys_internal_email('EFTA00039872'),
    usanys_internal_email('EFTA00039868'),
    usanys_internal_email('EFTA02731490'),
    usanys_internal_email('EFTA02731477'),
    usanys_internal_email('EFTA02731660'),
    usanys_internal_email('EFTA00039820'),
    usanys_internal_email('EFTA02731638'),
    usanys_internal_email('EFTA00211839'),
    usanys_internal_email('EFTA00064799'),
    usanys_internal_email('EFTA02731636'),
    usanys_internal_email('EFTA02731637'),
    usanys_internal_email('EFTA02731659'),
    usanys_internal_email('EFTA02731781'),
    usanys_internal_email('EFTA00022364'),
    usanys_internal_email('EFTA02731774'),
    usanys_internal_email('EFTA02731724'),
    usanys_internal_email('EFTA02731771'),
    usanys_internal_email('EFTA02731486'),
    usanys_internal_email('EFTA02731604'),
    usanys_internal_email('EFTA00078263'),
    usanys_internal_email('EFTA02731618'),
    usanys_internal_email('EFTA02731608'),
    usanys_internal_email('EFTA02731612'),
    usanys_internal_email('EFTA02731729'),
    usanys_internal_email('EFTA02731484'),
    usanys_internal_email('EFTA00209896'),
    usanys_internal_email('EFTA02731757'),
    usanys_internal_email('EFTA02731623'),
    usanys_internal_email('EFTA00077309'),
    usanys_internal_email(
        'EFTA00089649',
        note=f"128,175 email attachments permanently lost",
        highlight_quote="FBI's technology was not able to extract the full emails and attachments",
        is_interesting=True,
        # truncate_to=(2_000, 3_000),
        truncate_to=AUTO,
    ),
    usanys_internal_email(
        'EFTA00097133',
        highlight_quote="the Wexner Foundation donated $185,000 for the Epstein Lodge",
        note='Interlochen donations',
        truncate_to=AUTO,
    ),
    usanys_internal_email('EFTA00013640', note='list of devices', truncate_to=(600, 1_700)),
    usanys_internal_email('EFTA02731488', note=f"possible evidence of girls being trafficked to {LEON_BLACK}", is_interesting=10),
    usanys_internal_email('EFTA02731655', note=f"specific allegations against {LEON_BLACK}", is_interesting=10),
    usanys_internal_email('EFTA02731689', date='2023-06-09 20:14:00', truncate_to=SHORT_TRUNCATE_TO),
    usanys_internal_email('EFTA02731733', date='2021-05-17 17:29:00'),
    usanys_internal_email('EFTA02731754', date='2024-03-06T23:24:00'),
    usanys_internal_email('EFTA02731732', date='2024-03-06T12:21:00'),
    usanys_internal_email('EFTA02731528', date='2021-05-06 09:39:15'),
    usanys_internal_email('EFTA02731475', date='2023-05-31T20:53:00'),
    usanys_internal_email('EFTA02731697', date='2021-06-07 17:33:00'),
    usanys_internal_email('EFTA02731583', date='2022-01-21 17:28:00'),
    usanys_internal_email('EFTA02731587', date='2022-01-21 17:28:00'),
    usanys_internal_email('EFTA00214043', show_with_name='Conchita Sarnoff'),
    EmailCfg(
        id='EFTA02731737',
        author=USANYS,
        author_uncertain=True,
        date='2023-06-30T16:05:00',
        highlight_quote='Described him looking like Shrek',
        is_interesting=10,
        note=f'allegations against {LEON_BLACK}',
        recipients=[FBI],
        truncate_to=(800, 4_800),
    ),
    EmailCfg(
        id='EFTA00090614',
        author=USANYS,
        author_uncertain=True,
        note='alleges cover up of crimes of wealthy / powerful people by DA Cyrus Vance',
        recipients=[FBI],
        recipient_uncertain=True,
        truncate_to=7000,
    ),
    EmailCfg(id='EFTA00029435', author=USANYS),
    EmailCfg(id='EFTA02731755', author=USANYS),
    EmailCfg(id='EFTA00039662', author=USANYS),
    EmailCfg(id='EFTA00040141', author=USANYS),
    EmailCfg(id='EFTA02731644', author=USANYS),
    EmailCfg(id='EFTA00040144', author=USANYS),
    EmailCfg(id='EFTA00039813', author=USANYS),
    EmailCfg(id='EFTA02731783', author=USANYS, date='2022-01-21 17:28:00'),
    EmailCfg(id='EFTA02731578', author=USANYS, date='2021-05-28 10:00:00'),
    EmailCfg(id='EFTA00024819', is_interesting=False),
    EmailCfg(id='EFTA00039995', author=USANYS, is_interesting=False),
    EmailCfg(id='EFTA00039890', author=USANYS, is_interesting=False),
    EmailCfg(id='EFTA00039815', author=USANYS, is_interesting=False),
    EmailCfg(id='EFTA00039825', author=USANYS, is_interesting=False),
    EmailCfg(id='EFTA00039983', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA00039886', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA02731651', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA02731775', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA02731646', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA02731640', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA02731643', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA02731501', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA02731633', author=USANYS, author_uncertain=True),
    EmailCfg(id='EFTA00040121', author=USANYS, recipients=[ATT_COURT_APPEARANCE_TEAM]),
    EmailCfg(id='EFTA02731630', author=USANYS, recipients=[FBI]),
    EmailCfg(id='EFTA00014718', author=USANYS, recipients=['Daily Beast']),
    EmailCfg(id='EFTA02731593', author=USANYS, recipients=['Manhattan DA']),
    EmailCfg(id='EFTA00039419', author=USANYS, recipients=['Manhattan DA']),
    EmailCfg(id='EFTA02731617', author=USANYS, recipients=[SDNY], date='2021-04-28T15:05:41'),
    EmailCfg(id='EFTA00151184', author=USANYS, recipients=[USANYS]),
    EmailCfg(id='EFTA01660679', author=USANYS, author_uncertain=True, recipients=[FBI], recipient_uncertain=True),
    EmailCfg(id='EFTA02731699', author=USANYS, author_uncertain=True, recipients=[FBI], date='2021-05-27 10:19:00'),
    EmailCfg(id='EFTA00014767', author=USANYS, author_uncertain=True, recipients=[USANYS], is_interesting=False),
    EmailCfg(id='EFTA00015851', author=USANYS, author_uncertain=True, recipients=[USANYS], is_interesting=False),
    EmailCfg(id='EFTA02730468', author=USANYS, recipients=[USANYS], date='2019-07-11T08:25:00', date_uncertain='just wrong'),
    EmailCfg(id='EFTA00019925', author=USANYS, recipients=[USANYS], note="death of Epstein's cellmate Efrain Reyes"),
    EmailCfg(id='EFTA00039879', author=USANYS, recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA02731632', recipients=[OFFICE_OF_THE_DEPUTY_ATTORNEY_GENERAL]),
    EmailCfg(id='EFTA02731721', recipients=[USANYS]),
    EmailCfg(id='EFTA02731582', recipients=[USANYS]),
    EmailCfg(id='EFTA00039884', recipients=[USANYS]),
    EmailCfg(id='EFTA02731514', recipients=[USANYS], comment='journal upload followup'),
    EmailCfg(id='EFTA02731511', recipients=[USANYS], comment='journal upload followup'),
    EmailCfg(id='EFTA02731515', recipients=[USANYS], comment='journal upload followup'),
    EmailCfg(id='EFTA02731512', recipients=[USANYS], note=f'specific allegations against {GHISLAINE_MAXWELL}'),
    EmailCfg(id='EFTA01250175', recipients=[USANYS], note='urging DOJ to not allow Epstein out on bail because he will flee', is_interesting=True),
    EmailCfg(id='EFTA02731735', recipients=[USANYS], recipient_uncertain=True, date='2024-03-04T05:04:00'),
    EmailCfg(id='EFTA02731480', recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA02731482', recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA02731713', recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA02731718', recipients=[USANYS], recipient_uncertain=True),
    EmailCfg(id='EFTA02731715', recipients=[USANYS], duplicate_ids=['EFTA02731762']),

    # USVI
    DocCfg(id='EFTA00129040', note='subpoena'),
    DocCfg(
        id='EFTA00155032',
        author='USVI',
        date='2023-01-20',
        note=f"$62.5 million settlement payment from {LEON_BLACK}",
        is_interesting=10,
    ),
]
