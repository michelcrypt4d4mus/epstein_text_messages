import re

from .env import deep_debug
from .rich import JOI_ITO, LARRY_SUMMERS, console

DATE_REGEX = re.compile(r'^Date:\s*(.*)\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
EMAIL_HEADER_REGEX = re.compile(r'^(((Date|Subject):.*\n)*From:.*\n((Date|Sent|To|CC|Importance|Subject|Attachments):.*\n)+)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile(r'^>|ok|((sent|attachments|subject|importance).*|.*(11111111|january|201\d|hysterical|article 1.?|momminnemummin|talk in|it was a|what do|cc:|call (back|me)).*)$', re.IGNORECASE)
EMPTY_HEADER_REGEX = re.compile(r'From:\s*\n((Date|Sent|To|CC|Importance|Subject|Attachments):\s*\n)+')
BROKEN_EMAIL_REGEX = re.compile(r'^From:\s*\nSent:\s*\nTo:\s*\n(?:(?:CC|Importance|Subject|Attachments):\s*\n)*(?!CC|Importance|Subject|Attachments)([a-zA-Z]{2,}.*|\[triyersr@gmail.com\])\n')
REPLY_REGEX = re.compile(r'(On ([A-Z][a-z]{2,9},)?\s*?[A-Z][a-z]{2,9}\s*\d+,\s*\d{4},?\s*(at\s*\d+:\d+\s*(AM|PM))?,?.*wrote:|-+Original\s*Message-+)')
NOT_REDACTED_EMAILER_REGEX = re.compile(r'saved by internet', re.IGNORECASE)

DARREN_INDKE = 'Darren Indke'
EDWARD_EPSTEIN = 'Edward Epstein'
JEFFREY_EPSTEIN = 'Jeffrey Epstein'
JOHN_PAGE = 'John Page'
JONATHAN_FARKAS = 'Jonathan Farkas'
LAWRENCE_KRAUSS = 'Lawrence Krauss'

EMAILERS = [
    'Al Seckel',
    'Daniel Sabba',
    'Glenn Dubin',
    'Jessica Cadwell',
    JOHN_PAGE,
    'Jokeland',
    'Kathleen Ruderman',
    'Lesley Groff',
    'Michael Wolff',
    JONATHAN_FARKAS,
    'Peggy Siegal',
    'Richard Kahn',
    'Robert Kuhn',
    'Robert Trivers',
    'Sample, Elizabeth',
    'Steven Victor MD',
    'Weingarten, Reid',
]

EMAILER_REGEXES = {
    'Amanda Ens': re.compile(r'ens, amand', re.IGNORECASE),
    "Barbro Ehnbom": re.compile(r'behnbom@aol.com|Barbro\s.*Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen?', re.IGNORECASE),
    'Boris Nikolic': re.compile(r'boris nikoli', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterpris', re.IGNORECASE),
    DARREN_INDKE: re.compile(r'^darren$|darren [il]ndyke', re.IGNORECASE),
    'David Stern': re.compile(r'David Stern?', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    'Ehud Barak': re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    'Ghislaine Maxwell': re.compile(r'g ?max(well)?', re.IGNORECASE),
    'Google Alerts': re.compile(r'google\s?alerts', re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'jee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|joichi|^joi$', re.IGNORECASE),
    'Kathy Ruemmler': re.compile(r'Kathy Ruemmle', re.IGNORECASE),
    'Ken Starr': re.compile('starr, ken', re.IGNORECASE),
    'Landon Thomas Jr.': re.compile('landon thomas jr|thomas jr.?, landon', re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r'La(wrence|rry).*Summer|^LHS?$', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus', re.IGNORECASE),
    'Lisa New': re.compile(r'Lisa New?$', re.IGNORECASE),
    'Mohamed Waheed Hassan': re.compile(r'Mohamed Waheed', re.IGNORECASE),
    'Martin Weinberg': re.compile(r'martin (g.* )weinberg', re.IGNORECASE),
    'Nicholas Ribis': re.compile(r'Nicholas Rib', re.IGNORECASE),
    'Paul Krassner': re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    'Robert Lawrence Kuhn': re.compile(r'Robert\s*(Lawrence\s*)?Kuhn', re.IGNORECASE),
    'Scott J. Link': re.compile(r'scott j. lin', re.IGNORECASE),
    'Sean Bannon': re.compile(r'sean banno', re.IGNORECASE),
    'Stephen Hanson': re.compile(r'ste(phen|ve) hanson|Shanson900', re.IGNORECASE),
    'Steve Bannon': re.compile(r'steve banno[nr]?', re.IGNORECASE),
}

KNOWN_EMAILS = {
    '026625': DARREN_INDKE,
    '031120': 'Gwendolyn',        # Signature
    '029692': JEFFREY_EPSTEIN,
    '031624': JEFFREY_EPSTEIN,
    '016692': JOHN_PAGE,
    '031732': JONATHAN_FARKAS,
    '029196': LAWRENCE_KRAUSS,
    '028789': 'Lawrance Visoski',
    '029020': 'Renata Bolotova',   # Signature
}

for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer, re.IGNORECASE)

EPSTEIN_SIGNATURE = re.compile(
r"""please note
The information contained in this communication is
confidential, may be attorney-client privileged, may
constitute inside information, and is intended only for
the use of the addressee. It is the property of
JEE
Unauthorized use, disclosure or copying of this
communication or any part thereof is strictly prohibited
and may be unlawful. If you have received this
communication in error, please notify us immediately by(\n\d\s*)?
return e-mail or by e-mail to jeevacation.*gmail.com, and
destroy this communication and all copies thereof,
including all attachments. copyright -all rights reserved"""
)


def extract_email_sender(file_text):
    email_match = EMAIL_REGEX.search(file_text)
    broken_match = BROKEN_EMAIL_REGEX.search(file_text)
    date_match = DATE_REGEX.search(file_text)
    emailer = None

    if broken_match:
        emailer = broken_match.group(1)
    elif email_match:
        emailer = email_match.group(1)

    if not emailer:
        return

    emailer = emailer.strip().lstrip('"').lstrip("'").rstrip('"').rstrip("'").strip()
    emailer = emailer.strip('_').strip('[').strip(']').strip('*').strip('<').strip('•').rstrip(',').strip()

    for name, regex in EMAILER_REGEXES.items():
        if regex.search(emailer):
            emailer = name
            break

    if ' [' in emailer:
        emailer = emailer.split(' [')[0]

    if not valid_emailer(emailer):
        return
    elif emailer == 'Ed' and 'EDWARD JAY EPSTEIN' in file_text:
        return EDWARD_EPSTEIN

    return emailer


def cleanup_email_txt(file_text: str) -> str:
    if not EMPTY_HEADER_REGEX.search(file_text):
        file_text = EMAIL_HEADER_REGEX.sub(r'\1\n', file_text, 1)

    file_text = REPLY_REGEX.sub(r'\n\1', file_text)
    return EPSTEIN_SIGNATURE.sub('<...clipped epstein legal signature...>', file_text)


valid_emailer = lambda emailer: not BAD_EMAILER_REGEX.match(emailer)
