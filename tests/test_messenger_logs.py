from epstein_files.documents.messenger_log import sender_counts

MESSENGER_LOG_AUTHOR_COUNTS = {
    "(unknown)": 173,
    "Anil Ambani": 22,
    "Anthony Scaramucci": 57,
    "Ards": 2,
    "Celina Dubin": 46,
    "Eva": 8,
    "Jeffrey Epstein": 2560,
    "Joi Ito": 10,
    "Larry Summers": 29,
    "Melanie Walker": 346,
    "Michael Wolff": 7,
    "Miroslav Lajčák": 56,
    "Soon-Yi Previn": 28,
    "Stacey Plaskett": 12,
    "Steve Bannon": 1303,
    "Terje Rød-Larsen": 9,
}


def test_message_counts(epstein_files):
    assert MESSENGER_LOG_AUTHOR_COUNTS == sender_counts
