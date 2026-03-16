from epstein_files.documents.config.doc_cfg import CommunicationCfg, DocCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


TEXT_MSG_CFGS = [
    DocCfg(id='033434', description=f"{SCREENSHOT} iMessage chat labeled 'Edwards'"),
    DocCfg(
        id='EFTA01620764',
        author=MELANIE_WALKER,
        author_uncertain=True,
        description=f'conversation about crypto philanthropy and Bill Gates being drunk all the time',
        truncate_to=(250, 3_500),
    ),
    DocCfg(id='EFTA01618381', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01622387', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01618494', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01618400', author=RENATA_BOLOTOVA, description=f'iMessage screenshots', author_uncertain='sneaky'),
    DocCfg(id='EFTA01611898', description=f"screenshot of recent contacts in an iPhone"),
    CommunicationCfg(
        id='EFTA02731576',
        description=f"making contemporaneous accusations",
        recipients=[LEON_BLACK],
        show_full_panel=True,
    ),
    CommunicationCfg(id='EFTA01611042', author=ED_BOYLE, recipients=[None, MARIA_PRUSAKOVA]),
    CommunicationCfg(id='EFTA02731525', author=LEON_BLACK, author_uncertain=True, show_full_panel=True),
    # TODO: convert to MessengerLogPdf
    CommunicationCfg(
        id='EFTA01612665',
        description='Epstein gives advice on how to recruit girls',
        highlight_quote="stressed about finding girls. It's hard",
    ),
]
