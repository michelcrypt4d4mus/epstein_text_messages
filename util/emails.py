import re

from .env import deep_debug
from .rich import JOI_ITO, console

DATE_REGEX = re.compile(r'^Date:\s*(.*)\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile(r'^>|ok|((sent|attachments|subject|importance).*|.*(11111111|january|201\d|article 1.?|saved by|momminnemummin|talk in|it was a|what do|cc:|call (back|me)).*)$', re.IGNORECASE)
BROKEN_EMAIL_REGEX = re.compile(r'^From:\s*\nSent:\s*\nTo:\s*\n(?:(?:CC|Importance|Subject|Attachments):\s*\n)*(?!CC|Importance|Subject|Attachments)([a-zA-Z]{2,}.*|\[triyersr@gmail.com\])\n')
REPLY_REGEX = re.compile(r'(On ([A-Z][a-z]{2},)?\s*?[A-Z][a-z]{2}\s*\d+,\s*\d{4},\s*at\s*\d+:\d+\s*(AM|PM),.*wrote:)')


EMAILERS = [
    'Al Seckel',
    'Daniel Sabba',
    'Glenn Dubin',
    'Kathleen Ruderman',
    'Lesley Groff',
    'Michael Wolff',
    'Peggy Siegal',
    'Richard Kahn',
    'Robert Kuhn',
    'Steven Victor MD',
    'Weingarten, Reid',
]

EMAILER_REGEXES = {
    'Amanda Ens': re.compile(r'ens, amand', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen', re.IGNORECASE),
    'Boris Nikolic': re.compile(r'boris nikoli', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterpris', re.IGNORECASE),
    'Darren Indke': re.compile(r'^darren$|darren [il]ndyke', re.IGNORECASE),
    'Ehud Barak': re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    'Ghislaine Maxwell': re.compile(r'g ?max(well)?', re.IGNORECASE),
    'Google Alerts': re.compile(r'google\s?alerts', re.IGNORECASE),
    'Jeffrey Epstein': re.compile(r'jee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|joichi|^joi$', re.IGNORECASE),
    'Kathy Ruemmler': re.compile(r'Kathy Ruemmle', re.IGNORECASE),
    'Ken Starr': re.compile('starr, ken', re.IGNORECASE),
    'Landon Thomas Jr.': re.compile('landon thomas jr|thomas jr.?, landon', re.IGNORECASE),
    'Larry Summers': re.compile(r'La(wrence|rry).*Summer|^LHS?$', re.IGNORECASE),
    'Lawrence Krauss': re.compile(r'Lawrence Kraus', re.IGNORECASE),
    'Lisa New': re.compile(r'Lisa New?$', re.IGNORECASE),
    'Martin Weinberg': re.compile(r'martin (g.* )weinberg', re.IGNORECASE),
    'Nicholas Ribis': re.compile(r'Nicholas Rib', re.IGNORECASE),
    'Paul Krassner': re.compile(r'Pa\s+ul Krassner', re.IGNORECASE),
    'Steve Bannon': re.compile(r'steve bannon', re.IGNORECASE),
}

for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer, re.IGNORECASE)

EPSTEIN_SIGNATURE = """
please note
The information contained in this communication is
confidential, may be attorney-client privileged, may
constitute inside information, and is intended only for
the use of the addressee. It is the property of
JEE
Unauthorized use, disclosure or copying of this
communication or any part thereof is strictly prohibited
and may be unlawful. If you have received this
communication in error, please notify us immediately by
return e-mail or by e-mail to jeevacation@gmail.com, and
destroy this communication and all copies thereof,
including all attachments. copyright -all rights reserved
""".strip()


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

    if emailer == 'Ed' and 'EDWARD JAY EPSTEIN' in file_text:
        return 'Edward Jay Epstein'

    return emailer


def replace_signature(file_text: str) -> str:
    # file_text = REPLY_REGEX.sub(file_text, 'fooo')
    file_text = re.sub(r'(On ([A-Z][a-z]{2},)?\s*?[A-Z][a-z]{2}\s*\d+,\s*\d{4},\s*at\s*\d+:\d+\s*(AM|PM),.*wrote:)', r'\n\1', file_text)
    return file_text.replace(EPSTEIN_SIGNATURE, '<...clipped epstein legal signature...>')


valid_emailer = lambda emailer: not BAD_EMAILER_REGEX.match(emailer)
