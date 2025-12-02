from os import devnull

import pytest
from rich.console import Console

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
    # @pytest.mark.skip(reason="Messenger Log counts are only built when printed.")
    with open(devnull, "wt") as null_out:
        console = Console(file=null_out)

        for log in epstein_files.imessage_logs:
            console.print(log)

    assert len(epstein_files.imessage_logs) == 77
    assert MESSENGER_LOG_AUTHOR_COUNTS == {k: v for k, v in sender_counts.items()}
