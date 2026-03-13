from epstein_files.documents.config.doc_cfg import DocCfg, EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

FIRE_AND_FURY = f"Fire And Fury"
PATTERSON_BOOK_SCANS = f'pages of "Filthy Rich: The Shocking True Story of {JEFFREY_EPSTEIN}"'


BOOK_CFGS = [
    DocCfg(id='017088', author=ALAN_DERSHOWITZ, description=f'"Taking the Stand: My Life in the Law" (draft)', date='2012-04-02'),  # Slow file
    DocCfg(id='013501', author='Arnold J. Mandell', description=f'The Nearness Of Grace: A Personal Science Of Spiritual Transformation', date='2005-01-01'),
    DocCfg(id='012899', author='Ben Goertzel', description=f'Engineering General Intelligence: A Path to Advanced AGI Via Embodied Learning and Cognitive Synergy', date='2013-09-19'),
    DocCfg(id='018438', author='Clarisse Thorn', description=f'The S&M Feminist', date='2012-05-14'),
    DocCfg(id='019477', author=EDWARD_JAY_EPSTEIN, description=f'How America Lost Its Secrets: Edward Snowden, the Man, and the Theft'),
    DocCfg(id='020153', author=EDWARD_JAY_EPSTEIN, description=f'The Snowden Affair: A Spy Story In Six Parts'),
    DocCfg(id='011472', author=EHUD_BARAK, description=f'"Night Flight" (draft)', date='2006-07-12', duplicate_ids=['027849'], is_interesting=False),  # date from extract_timestamp()
    DocCfg(id='010912', author=GORDON_GETTY, description=f'"Free Growth and Other Surprises" (draft)', date='2018-10-18'),
    DocCfg(id='010477', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='010486', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='021958', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='022058', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='022118', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='019111', author=JAMES_PATTERSON, description=PATTERSON_BOOK_SCANS, date='2016-10-10'),
    DocCfg(id='015675', author='James Tagg', description=f'Are the Androids Dreaming Yet? Amazing Brain Human Communication, Creativity & Free Will', date='2015-06-01'),  # Slow file
    DocCfg(id='016804', author=JOHN_BROCKMAN, description='Deep Thinking: Twenty-Five Ways of Looking at AI', date='2019-02-19', duplicate_ids=['016221']),
    DocCfg(id='018232', author='Joshua Cooper Ramo', description=f'The Seventh Sense: Power, Fortune & Survival in the Age of Networks', date='2015-03-11'),
    DocCfg(id='012747', author='Marc D. Hauser', description=f'Evilicious: Explaining Our Taste For Excessive Harm'),
    DocCfg(id='032724', author=MICHAEL_WOLFF, description=f'cover of "{FIRE_AND_FURY}"', date='2018-01-05', is_interesting=False),
    DocCfg(id='021120', author=MICHAEL_WOLFF, description=f'chapter of "Siege: Trump Under Fire"'),
    DocCfg(id='019874', author=MICHAEL_WOLFF, description=FIRE_AND_FURY, date='2018-01-05', is_interesting=False),
    DocCfg(id='015032', author=PAUL_KRASSNER, description=f"60 Years of Investigative Satire: The Best of {PAUL_KRASSNER}"),
    DocCfg(id='023731', author=ROGER_SCHANK, description=f'Teaching Minds How Cognitive Science Can Save Our Schools'),
    DocCfg(id='021247', author='The Chicago Social Brain Network', description=f'Invisible Forces And Powerful Beliefs: Gravity, Gods, And Minds', date='2010-10-04'),
    DocCfg(id='013796', author='Tim Ferriss', description=f'The 4-Hour Workweek'),
    DocCfg(id='021145', author=VIRGINIA_GIUFFRE, description=f'"The Billionaire\'s Playboy Club" (draft?)'),
    DocCfg(id='031533', description=f'pages from a book about the Baylor University sexual assault scandal and Sam Ukwuachu'),
    # DOJ files
    DocCfg(id='EFTA00008020', display_text='"Massage for Dummies"'),
    DocCfg(id='EFTA00008320', display_text='"Massage for Dummies (???)"'),
    DocCfg(id='EFTA00008220', display_text='"Massage book: Chapter 11: Putting the Moves Together"'),
    DocCfg(id='EFTA00008120', display_text='"Part II: The Art of Receiving a Massage"'),
]
