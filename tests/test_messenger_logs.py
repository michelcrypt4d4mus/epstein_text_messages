from epstein_files.util.constant.names import *

MESSENGER_LOG_AUTHOR_COUNTS = {
    UNKNOWN: 173,
    ANIL_AMBANI: 22,
    SCARAMUCCI: 57,
    "Ards": 2,
    CELINA_DUBIN: 46,
    "Eva": 8,
    JEFFREY_EPSTEIN: 2560,
    JOI_ITO: 10,
    LARRY_SUMMERS: 29,
    MELANIE_WALKER: 346,
    MICHAEL_WOLFF: 7,
    MIROSLAV_LAJCAK: 56,
    SOON_YI: 28,
    STACEY_PLASKETT: 12,
    STEVE_BANNON: 1303,
    TERJE_ROD_LARSEN: 9,
}


def test_message_counts(epstein_files):
    assert len(epstein_files.imessage_logs) == 77
    assert MESSENGER_LOG_AUTHOR_COUNTS == epstein_files.imessage_sender_counts()
