from epstein_files.documents.config.doc_cfg import DocCfg, EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

PATTERSON_BOOK_SCANS = f'pages of "Filthy Rich: The Shocking True Story of {JEFFREY_EPSTEIN}"'
STRANGE_BEDFELLOWS = "'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more"
SWEDISH_LIFE_SCIENCES_SUMMIT = f"{BARBRO_C_EHNBOM}'s Swedish American Life Science Summit (SALSS)"


CONFERENCE_CFGS = [
    DocCfg(id='014315', author=BOFA_MERRILL, note=f'2016 Future of Financials Conference', attached_to_email_id='014312'),
    DocCfg(id='026825', author=DEUTSCHE_BANK, note=f"Asset & Wealth Management featured speaker bios"),  # Really "Deutsche Asset" which may not be Deutsche Bank?
    DocCfg(id='023123', author=LAWRENCE_KRAUSS_ASU_ORIGINS, note=f"{STRANGE_BEDFELLOWS} (old draft)"),
    DocCfg(id='023120', author=LAWRENCE_KRAUSS_ASU_ORIGINS, note=STRANGE_BEDFELLOWS, duplicate_ids=['023121'], dupe_type='earlier'),
    DocCfg(id='031359', author=NOBEL_CHARITABLE_TRUST, note=f'"Earth Environment Convention" about ESG investing'),
    DocCfg(id='031354', author=NOBEL_CHARITABLE_TRUST, note=f'"Thinking About the Environment and Technology" report 2011'),
    DocCfg(id='017524', author=SWEDISH_LIFE_SCIENCES_SUMMIT, note=f"2012 program", date='2012-08-18', attached_to_email_id='017523'),
    DocCfg(id='026747', author=SWEDISH_LIFE_SCIENCES_SUMMIT, note=f"2017 program", date='2017-08-23', attached_to_email_id='031215'),
    DocCfg(id='014951', author='TED Talks', note=f"2017 program", date='2017-04-20'),
    DocCfg(
        id='024185',
        author=UN_GENERAL_ASSEMBLY,
        note=f'schedule including "Presidents Private Dinner - Jeffrey Epstine (sic)"',
        date='2012-09-21',
        is_interesting=True,
    ),
    DocCfg(id='024179', author=UN_GENERAL_ASSEMBLY, note=f'president and first lady schedule', date='2012-09-21'),
    DocCfg(
        id='029427',
        note=f"seems related to an IRL meeting about Chinese attempts to absorb Mongolia",
        is_interesting=True,
    ),
    DocCfg(
        id='025797',
        date='2013-05-29',
        note=f"someone's notes from Aspen Strategy Group",
        is_interesting=True,
    ),
    DocCfg(
        id='017060',
        note=f'World Economic Forum (WEF) Annual Meeting 2011 List of Participants',
        date='2011-01-18',
    ),
    DocCfg(id='017526', note=f'Intellectual Jazz conference brochure f. {DAVID_BLAINE}'),
]
