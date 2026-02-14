from epstein_files.util.constant.names import *


from epstein_files.util.constant.names import *


# Unhighlighted / uncategorized emailer regexes
CONTACT_INFOS = [
    ContactInfo(
        name=BORIS_NIKOLIC,
        emailer_pattern=r"(boris )?nikolic?",
    ),
    ContactInfo(
        name='Daphne Wallace',
        emailer_pattern=r"Da[p ]hne Wallace",
    ),
    ContactInfo(
        name=INTELLIGENCE_SQUARED,
        emailer_pattern=r"intelligence\s*squared",
    ),
    ContactInfo(
        name='Matthew Schafer',
        emailer_pattern=r"matthew\.?schafer?",
    ),
    ContactInfo(
        name=MICHAEL_BUCHHOLTZ,
        emailer_pattern=r"Michael.*Buchholtz",
    ),
    ContactInfo(
        name=SAMUEL_LEFF,
        emailer_pattern=r"Sam(uel)?(/Walli)? Leff",
    ),
    ContactInfo(
        name=THANU_BOONYAWATANA,
        emailer_pattern=r"Thanu (BOONYAWATANA|Cnx)",
    )
]

CONTACT_INFOS_DICT = {contact.name: contact for contact in CONTACT_INFOS}

