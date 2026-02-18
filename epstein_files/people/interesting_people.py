from rich.text import Text

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import PALM_BEACH_CODE_ENFORCEMENT, PALM_BEACH_WATER_COMMITTEE, UN_GENERAL_ASSEMBLY
from epstein_files.util.helpers.link_helper import SUBSTACK_POST_LINK_STYLE, link_text_obj
from epstein_files.util.constant.urls import SUBSTACK_INSIGHTS_LINK

# People who are of interest as authors of non-emails
AUTHORS_OF_INTEREST = [
    EDWARD_JAY_EPSTEIN,
    INSIGHTS_POD,
    # NOAM_CHOMSKY,
    MICHAEL_WOLFF,
    SVETLANA_POZHIDAEVA,
]

# List of people whose files to print in curated site. Order matters.
EMAILERS_OF_INTEREST = [
    BROCK_PIERCE,
    JABOR_Y,
    JOI_ITO,
    STEVEN_SINOFSKY,
    AMIR_TAAKI,
    DANIEL_SIAD,
    AL_SECKEL,
    AUSTIN_HILL,
    VINCENZO_IOZZO,
    MARIA_PRUSAKOVA,
    JEREMY_RUBIN,
    JEAN_LUC_BRUNEL,
    DAVID_STERN,
    STEVEN_HOFFENBERG,
    EHUD_BARAK,
    MASHA_DROKOVA,
    STEVE_BANNON,
    JULIA_SANTOS,
    TYLER_SHEARS,
    SERGEY_BELYAKOV,
    GANBAT_CHULUUNKHUU,
    RENATA_BOLOTOVA,
    CHRISTINA_GALBRAITH,
    PHILIP_ROSEDALE,
    MOHAMED_WAHEED_HASSAN,
    JENNIFER_JACQUET,
    ZUBAIR_KHAN,
    ROSS_GOW,
    DAVID_BLAINE,
    None,
]

EMAILERS_OF_INTEREST_SET: set[Name] = set(EMAILERS_OF_INTEREST)
EMAILERS_TO_PRINT = EMAILERS_OF_INTEREST + [JEFFREY_EPSTEIN]

TEXTERS_OF_INTEREST = [
    ANTHONY_SCARAMUCCI,
    ANIL_AMBANI,
    STACEY_PLASKETT,
]

PERSONS_OF_INTEREST: set[Name] = set(EMAILERS_OF_INTEREST + AUTHORS_OF_INTEREST + TEXTERS_OF_INTEREST)

UNINTERESTING_AUTHORS = [
    GORDON_GETTY,
    LAWRENCE_KRAUSS,
    NOBEL_CHARITABLE_TRUST,
    PALM_BEACH_CODE_ENFORCEMENT,
    PALM_BEACH_WATER_COMMITTEE,
    UN_GENERAL_ASSEMBLY,
]

SPECIAL_NOTES = {
    ZUBAIR_KHAN: Text('', 'bold', justify='center').append(SUBSTACK_INSIGHTS_LINK) + \
        Text('\n(a post by me about the social media work Zubair Khan was doing for Epstein during the 2016 election)', 'italic'),
}
