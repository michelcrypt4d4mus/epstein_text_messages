"""
Politics related files. By default uninteresting.
"""
from epstein_files.documents.config.communication_cfg import CommunicationCfg, imessage_screenshot, imessage_log
from epstein_files.documents.config.config_builder import letter, passenger_manifest
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.config.pic_cfg import PicCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import join_truthy, quote

DIANA_DEGETTE_CAMPAIGN = "Colorado legislator Diana DeGette's campaign"
TRUMP_DISCLOSURES = f"Donald Trump financial disclosures from U.S. Office of Government Ethics"


def bannon_imessage(id: str, date: str = '', **kwargs) -> CommunicationCfg:
    return imessage_screenshot(id, date=date, recipients=[STEVE_BANNON], **kwargs)


POLITICS_CFGS = [
    DocCfg(id='030258', author=ALAN_DERSHOWITZ, note=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030248'),
    DocCfg(id='030248', author=ALAN_DERSHOWITZ, note=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    DocCfg(id='029165', author=ALAN_DERSHOWITZ, note=f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258'),
    DocCfg(id='029918', author=DIANA_DEGETTE_CAMPAIGN, note=f"bio", date='2012-09-27'),
    DocCfg(id='031184', author=DIANA_DEGETTE_CAMPAIGN, note=f"invitation to fundraiser hosted by {BARBRO_C_EHNBOM}", date='2012-09-27'),
    DocCfg(id='026248', author='Don McGahn', note=f'letter from Trump lawyer to Devin Nunes (R-CA) about FISA courts and Trump'),
    DocCfg(id='027009', author=EHUD_BARAK, note=f"speech to AIPAC", date='2013-03-03'),
    DocCfg(
        id='019233',
        author='Freedom House',
        date='2017-06-02',
        note=f"'Breaking Down Democracy: Goals, Strategies, and Methods of Modern Authoritarians'",
    ),
    DocCfg(id='026856', author='Kevin Rudd', note=f'speech "Xi Jinping, China And The Global Order"', date='2018-06-26'),
    DocCfg(id='026827', author='Scowcroft Group', note=f'report on ISIS', date='2015-11-14'),
    DocCfg(id='024294', author=STACEY_PLASKETT, note=f"campaign flier", date='2016-10-01'),
    DocCfg(
        id='023133',
        author=f"{TERJE_ROD_LARSEN}, Nur Laiq, Fabrice Aidan",
        date='2014-12-09',
        note=f'The Search for Peace in the Arab-Israeli Conflict',
    ),
    DocCfg(id='033468', note=f'{ARTICLE_DRAFT} Rod Rosenstein', date='2018-09-24'),
    DocCfg(id='025849', author=US_GIS, note=quote('Building a Bridge Between FOIA Requesters & Agencies')),
    # CommunicationCfg(id='031670', author="General Mike Flynn's lawyers", recipients=['Sen. Mark Warner & Richard Burr'], description=f"about subpoena"),
    DocCfg(id='031670', note=f"letter from General Mike Flynn's lawyers to senators Mark Warner & Richard Burr about subpoena"),
    DocCfg(
        id='029357',
        date='2015-01-15',
        date_uncertain='a guess',
        note=f"possibly book extract about Israel's challenges entering 2015",
        duplicate_ids=['028887'],
    ),
    DocCfg(id='010617', note=TRUMP_DISCLOSURES, date='2017-01-20', is_interesting=True, attached_to_email_id='033091'),
    DocCfg(id='016699', note=TRUMP_DISCLOSURES, date='2017-01-20', is_interesting=True, attached_to_email_id='033091'),
    DocCfg(id='EFTA00607327', author=INTERNATIONAL_PEACE_INSTITUTE),
    letter(id='EFTA02731023', author='Senator Ron Wyden', recipients=[LEON_BLACK], is_interesting=False),
    letter(id='EFTA02731018', author='Senator Ron Wyden', recipients=['Marc Rowan'], is_interesting=False),
    letter('EFTA00173350', 'Senator Dick Durban', ['Senator Chuck Grassley', 'Pam Bondi']),
    passenger_manifest('007300', '2006-03-03', f"current US Navy Secretary Navy {JOHN_PHELAN} and {JEAN_LUC_BRUNEL}", truncate_to=650),


    # Emails
    EmailCfg(
        id='025879',
        note="internal email from Epstein's island manager to Epstein's lawyer saying Bill Clinton was never on the island",
        is_interesting=True
    ),
    EmailCfg(id='030878', is_fwded_article=True, comment="Steve Bannon almost appeared in Michael Moore's 'Fahrenheit 11/9'"),
    EmailCfg(id='029679', highlight_quote='his driver MAtt was the bag man', note="(re: Trump)"),
    EmailCfg(id='026505', highlight_quote='I know how dirty donald is', truncate_to=670),
    EmailCfg(id='031659', highlight_quote='i have met some very bad people „ none as bad as trump', truncate_to=250),
    EmailCfg(id='031326', highlight_quote='that dog that hasn\'t barked is trump'),
    EmailCfg(id='031451', highlight_quote='would you like photso of donald and girls in bikinis in my kitchen'),
    EmailCfg(id='031596', highlight_quote='would you like photso of donald and girls in bikinis in my kitchen', truncate_to=500),
    EmailCfg(id='031601', highlight_quote='Old gf i gave to donald', truncate_to=2_000),
    EmailCfg(id='029299', is_interesting=True, note='letter of recommendation from Trump', duplicate_ids=['033594']),
    EmailCfg(id='030714', is_interesting=True, note='Bannon gets a shout out from Russian nationalist Alexander Dugan'),
    EmailCfg(id='029342', is_interesting=True, note='Hakeem Jeffries fundraiser', truncate_to=2_000),
    # DOJ emails
    EmailCfg(
        id='EFTA02605815',
        comment=KATHRYN_RUEMMLER,
        highlight_quote="Am totally tricked out by Uncle Jeffrey today! Jeffrey boots, handbag, and w=tch!",
        is_interesting=10,
    ),
    EmailCfg(
        id='EFTA00661468',
        highlight_quote='carpets and all', note="the prince of Saudi Arabia sent Epstein a tent",
        is_interesting=5,
        truncate_to=500,
    ),
    EmailCfg(id='EFTA00319913', note=f'Epstein buys {KATHRYN_RUEMMLER} a Hermes handbag'),
    EmailCfg(id='EFTA00819729', note=f'Epstein buys {KATHRYN_RUEMMLER} a Hermes handbag'),

    # Bannon
    bannon_imessage(
        'EFTA01620912',
        highlight_quote="first we need to push back on the lies ; then crush the pedo/trafficking narrative ; then rebuild your image as philanthropist",
        truncate_to=(950, 2_500),
    ),
    bannon_imessage('EFTA01615703', date='2019-04-01'),
    bannon_imessage('EFTA01620249', date='2019-03-04'),
    bannon_imessage('EFTA01615720', date='2019-04-05'),
    bannon_imessage('EFTA01615642', date='2019-03-01'),
    bannon_imessage('EFTA01615808'),
    bannon_imessage('EFTA01615165', '2018-06-29'),
    bannon_imessage('EFTA00783660', date='2019-02-06'),
    bannon_imessage('EFTA01615587', date='2019-01-22'),
    bannon_imessage('EFTA01615683', date='2019-03-29'),
    EmailCfg(id='EFTA01014138', highlight_quote="do you know bill barr. CIA", truncate_to=222),
    DocCfg(id='EFTA00296095', note=f"Mitt Romney victory party"),
    imessage_log('EFTA01612618', author=BORGE_BRENDE, date='2018-03-17'),
    imessage_log('EFTA01212310', date='2019-03-28'),
    imessage_log('EFTA01618718', date='2019-06-07'),

    # Albert Bryan
    EmailCfg(id='EFTA02258597', recipients=[ALBERT_BRYAN, DAPHNE_WALLACE]),
    EmailCfg(id='EFTA02258608', author=DAPHNE_WALLACE, recipients=[ALBERT_BRYAN, JOHN_ENGERMAN]),

    # USVI
    EmailCfg(id='EFTA00705527', note='acquiring a Virgin Islands radio station', visible_in_id='EFTA01053946'),
    EmailCfg(id='EFTA01053946', note='acquiring a Virgin Islands radio station', is_interesting=True, truncate_to=2_500),
    EmailCfg(id='EFTA00750027', note=f"Epstein paying {CECILE_DE_JONGH}'s children's tuition", is_interesting=True),

    # Ehud
    EmailCfg(id='EFTA00873126', note=f"Epstein emailing {EHUD_BARAK} hoping for a U.S. attack on Iran", is_interesting=10),
    EmailCfg(
        id='EFTA01013193',
        highlight_quote="you should make clear that i dont work for mossad. :)",
        is_interesting=True,
        truncate_to=AUTO,
    ),
    EmailCfg(
        id='EFTA02421875',
        highlight_quote="They are checking with Peres people now",
        note=f"Epstein dines with the president of Israel Shimon Peres",
    ),
    EmailCfg(id='EFTA00338727', note=f'dinner with the president of Mongolia', is_interesting=2),

    # Terje
    imessage_log('EFTA01621521', author=TERJE_ROD_LARSEN, note=f"{TERJE_ROD_LARSEN} and Epstein meet former CIA head Bill Burns ('BB')"),

    # Trump
    EmailCfg(id='EFTA01058838', highlight_quote="come to visit the island. new adminstration people visiting"),
]
