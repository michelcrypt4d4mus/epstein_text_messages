from epstein_files.util.constant.names import *

MESSENGER_LOG_AUTHOR_COUNTS = {
    None: 67,
    ANIL_AMBANI: 24,
    SCARAMUCCI: 57,
    ARDA_BESKARES: 2,
    CELINA_DUBIN: 48,
    EVA: 12,
    JEFFREY_EPSTEIN: 2561,
    JOI_ITO: 10,
    LARRY_SUMMERS: 31,
    MELANIE_WALKER: 388,
    MICHAEL_WOLFF: 7,
    MIROSLAV_LAJCAK: 58,
    SOON_YI: 29,
    STACEY_PLASKETT: 12,
    STEVE_BANNON: 1352,
    TERJE_ROD_LARSEN: 10,
}


def test_message_counts(epstein_files):
    assert len(epstein_files.imessage_logs) == 77
    assert epstein_files.imessage_sender_counts() == MESSENGER_LOG_AUTHOR_COUNTS
