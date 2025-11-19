import re

from .env import deep_debug, is_debug
from .rich import JOI_ITO, console

DATE_REGEX = re.compile(r'^Date:\s*(.*)\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile(r'^>|ok|((sent|attachments|subject|importance).*|.*(11111111|january|201\d|article 1.?|saved by|talk in|it was a|what do|cc:|call (back|me)).*)$')

BROKEN_EMAIL_REGEX = re.compile(r'^From:\s*\nSent:\s*\nTo:\s*\n(CC:\s*\n)?(Subject:\s*\n)?(To:\s*\n)?(Importance:\s*\n)?(Attachments:\s*\n)?([\w ]{2,}.*)\n')
NUM_CAPTURES_IN_BROKEN_EMAIL_REGEX = 6
BROKEN_CAPTURE_GROUP_IDXS = list(range(NUM_CAPTURES_IN_BROKEN_EMAIL_REGEX, 0, -1))

EMAILER_REGEXES = {
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen', re.IGNORECASE),
    'Boris Nikolic': re.compile(r'boris nikoli', re.IGNORECASE),
    'Darren Indke': re.compile(r'^darren$|darren [il]ndyke', re.IGNORECASE),
    'Ehud Barak': re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    'Ghislaine Maxwell': re.compile(r'g ?max(well)?', re.IGNORECASE),
    'Jeffrey Epstein': re.compile(r'jee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|joichi|^joi$', re.IGNORECASE),
    'Ken Starr': re.compile('starr, ken', re.IGNORECASE),
    'Landon Thomas Jr.': re.compile('landon thomas jr|thomas jr.?, landon', re.IGNORECASE),
    'Larry Summers': re.compile(r'La(wrence|rry).*Summer|^LHS?$', re.IGNORECASE),
    'Martin Weinberg': re.compile(r'martin (g.* )weinberg', re.IGNORECASE),
    'Nicholas Ribis': re.compile(r'Nicholas Rib', re.IGNORECASE),
    'Paul Krassner': re.compile(r'Pa\s+ul Krassner', re.IGNORECASE),
    'Steve Bannon': re.compile(r'steve bannon', re.IGNORECASE),
}

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

EMAILERS = [
    'Al Seckel',
    'Boris Nikolic',
    'Daniel Sabba',
    'Glenn Dubin',
    'Lawrence Krauss',
    'Lesley Groff',
    'Michael Wolff',
    'Peggy Siegal',
    'Richard Kahn',
    'Robert Kuhn',
    'Paul Krassner',
    'Steven Victor MD',
    'Weingarten, Reid',
]


def extract_email_sender(file_text):
    email_match = EMAIL_REGEX.search(file_text)
    broken_match = BROKEN_EMAIL_REGEX.search(file_text)
    date_match = DATE_REGEX.search(file_text)
    emailer = None

    if broken_match:
        for i in BROKEN_CAPTURE_GROUP_IDXS:
            if broken_match.group(i):
                emailer = broken_match.group(i)
                break
    elif email_match:
        emailer = email_match.group(1)

    if not emailer:
        return

    emailer = emailer.strip().lstrip('"').lstrip("'").rstrip('"').rstrip("'")
    emailer = emailer.strip().strip('_').strip('[').strip(']').strip('*').strip('<').strip('•').rstrip(',').strip()
    found_emailer = False

    for name, regex in EMAILER_REGEXES.items():
        if regex.search(emailer):
            emailer = name
            found_emailer = True
            break

    if not found_emailer:
        for possible_emailer in EMAILERS:
            if possible_emailer.lower() in emailer.lower():
                emailer = possible_emailer
                break

    if deep_debug:
        console.print(f"  -> Found email from '{emailer}'", style='dim')

    return emailer.lower()


def replace_signature(file_text: str) -> str:
    return file_text.replace(EPSTEIN_SIGNATURE, '<...clipped epstein legal signature...>')
