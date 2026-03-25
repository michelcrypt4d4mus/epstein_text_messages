"""
Politics related files. By default uninteresting.
"""
from epstein_files.documents.config.config_builder import letter, passenger_manifest
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.helpers.string_helper import join_truthy, quote

DIANA_DEGETTE_CAMPAIGN = "Colorado legislator Diana DeGette's campaign"
TRUMP_DISCLOSURES = f"Donald Trump financial disclosures from U.S. Office of Government Ethics"


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
    letter(id='EFTA02731023', author='Senator Ron Wyden', recipients=[LEON_BLACK], is_interesting=False),
    letter(id='EFTA02731018', author='Senator Ron Wyden', recipients=['Marc Rowan'], is_interesting=False),
    passenger_manifest('007300', '2006-03-03', f"current US Navy Secretary Navy {JOHN_PHELAN} and {JEAN_LUC_BRUNEL}", truncate_to=650),

    # Emails
    EmailCfg(
        id='025879',
        note="internal email from Epstein's island manager to Epstein's lawyer saying Bill Clinton was never on the island",
        is_interesting=True
    ),
    EmailCfg(id='030878', is_fwded_article=True, comment="Steve Bannon almost appeared in Michael Moore's 'Fahrenheit 11/9'"),
    EmailCfg(id='029679', highlight_quote='his driver MAtt was the bag man', note="(re: Trump)"),
    EmailCfg(id='026505', highlight_quote='I know how dirty donald is'),
    EmailCfg(id='031659', highlight_quote='i have met some very bad people „ none as bad as trump'),
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
    EmailCfg(id='EFTA00661468', note="the prince of Saudi Arabia sent Epstein a whole tent", is_interesting=5),
]
