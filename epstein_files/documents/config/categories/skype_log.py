"""
Skype conversation logs.
"""
from epstein_files.documents.config.communication_cfg import CommunicationCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


SKYPE_LOG_CFGS = [
    CommunicationCfg(id='032206', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    CommunicationCfg(id='032208', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    CommunicationCfg(id='032209', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    CommunicationCfg(id='032210', recipients=['linkspirit'], is_interesting=True),
    CommunicationCfg(id='018224', recipients=['linkspirit', LAWRENCE_KRAUSS], is_interesting=True),  # we don't know who linkspirit is yet
    CommunicationCfg(id='EFTA01617727'),
    CommunicationCfg(
        id='EFTA00507334',
        recipients=[
            'Aleksandra Eriksson',
            ANASTASIYA_SIROOCHENKO,
            'Catherine',
            DANIEL_SIAD,
            DAVID_STERN,
            EMAD_HANNA,
            'Jade Huang',
            NADIA_MARCINKO,
            'sexysearch2010',
            'sophiembh'
        ],
    ),
    CommunicationCfg(id='EFTA01613143', author=MELANIE_WALKER, date='2017-06-24'),
    CommunicationCfg(id='EFTA01217787', recipients=[TYLER_SHEARS, HANNA_TRAFF], is_interesting=True),
    CommunicationCfg(id='EFTA01217703', recipients=[ATHENA_ZELCOVICH, JOSCHA_BACH, LAWRENCE_KRAUSS]),
    CommunicationCfg(id='EFTA01217736', recipients=[ATHENA_ZELCOVICH, TYLER_SHEARS]),
    CommunicationCfg(
        id='EFTA01623342',
        author=ANNA_KASATKINA,
        author_uncertain='https://www.reddit.com/r/Epstein/comments/1qwbn5i/trafficker_julia_santos/',
        note='recruiting russian girls',
        is_interesting=True,
    ),
]
