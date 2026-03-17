"""
Skype conversation logs.
"""
from epstein_files.documents.config.communication_cfg import CommunicationCfg, skype_log
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


SKYPE_LOG_CFGS = [
    skype_log('032206', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    skype_log('032208', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    skype_log('032209', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    skype_log('032210', recipients=['linkspirit'], is_interesting=True),
    skype_log('018224', recipients=['linkspirit', LAWRENCE_KRAUSS], is_interesting=True),  # we don't know who linkspirit is yet
    skype_log('EFTA01617727'),
    skype_log(
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
    skype_log('EFTA01613143', author=MELANIE_WALKER, date='2017-06-24'),
    skype_log('EFTA01217703', recipients=[ATHENA_ZELCOVICH, JOSCHA_BACH, LAWRENCE_KRAUSS]),
    skype_log('EFTA01217736', recipients=[ATHENA_ZELCOVICH, TYLER_SHEARS]),
    skype_log('EFTA01217787', recipients=[TYLER_SHEARS, HANNA_TRAFF], is_interesting=True),
]
