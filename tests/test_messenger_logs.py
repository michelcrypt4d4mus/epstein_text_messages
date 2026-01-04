from epstein_files.util.constant.names import *
from epstein_files.documents.messenger_log import MessengerLog

MESSENGER_LOG_AUTHOR_COUNTS = {
    None: 59,
    ANDRZEJ_DUDA: 8,
    ANIL_AMBANI: 24,
    ANTHONY_SCARAMUCCI: 57,
    ARDA_BESKARDES: 2,
    CELINA_DUBIN: 48,
    EVA: 12,
    JEFFREY_EPSTEIN: 2561,
    JOI_ITO: 10,
    LARRY_SUMMERS: 31,
    MELANIE_WALKER: 388,
    MICHAEL_WOLFF: 7,
    MIROSLAV_LAJCAK: 58,
    SOON_YI_PREVIN: 29,
    STACEY_PLASKETT: 12,
    STEVE_BANNON: 1352,
    TERJE_ROD_LARSEN: 10,
}


def test_message_counts(epstein_files):
    assert len(epstein_files.imessage_logs) == 77
    assert MessengerLog.count_authors(epstein_files.imessage_logs) == MESSENGER_LOG_AUTHOR_COUNTS
