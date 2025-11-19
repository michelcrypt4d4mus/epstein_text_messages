import re

from rich.console import Console

from .env import deep_debug, is_debug

DATE_REGEX = re.compile(r'^Date:\s*(.*)\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile('^>|ok|((sent|attachments|subject|importance).*|.*(11111111111|january|201\d|saved by|talk in|it was a|what do|cc:|call (back|me)).*)$')
EPSTEIN_EMAIL_REGEX = re.compile(r'jee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE)
GHISLAINE_EMAIL_REGEX = re.compile(r'g ?max(well)?', re.IGNORECASE)
EHUD_BARAK_EMAIL_REGEX = re.compile(r'(ehud|h)\s*barak', re.IGNORECASE)
BANNON_EMAIL_REGEX = re.compile(r'steve bannon', re.IGNORECASE)
LARRY_SUMMERS_EMAIL_REGEX = re.compile(r'La(wrence|rry).*Summer|^LHS?$', re.IGNORECASE)
DARREN_INDKE = re.compile(r'^darren$|darren [il]ndyke', re.IGNORECASE)

BROKEN_EMAIL_REGEX = re.compile(r'^From:\s*\nSent:\s*\nTo:\s*\n(CC:\s*\n)?(Subject:\s*\n)?(To:\s*\n)?(Importance:\s*\n)?(Attachments:\s*\n)?([\w ]{2,}.*)\n')
NUM_CAPTURES_IN_BROKEN_EMAIL_REGEX = 6
BROKEN_CAPTURE_GROUP_IDXS = list(range(NUM_CAPTURES_IN_BROKEN_EMAIL_REGEX, 0, -1))

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

console = Console(color_system='256')


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

    if EPSTEIN_EMAIL_REGEX.search(emailer):
        emailer = 'Jeffrey Epstein'
    elif GHISLAINE_EMAIL_REGEX.search(emailer):
        emailer = 'Ghislaine Maxwell'
    elif emailer == 'ji@media.mitedu' or 'joichi ito' in emailer.lower() or emailer.lower() == 'joi':
        emailer = 'Joi Ito'
    elif EHUD_BARAK_EMAIL_REGEX.search(emailer):
        emailer = 'Ehud Barak'
    elif BANNON_EMAIL_REGEX.search(emailer):
        emailer = 'Steve Bannon'
    elif LARRY_SUMMERS_EMAIL_REGEX.search(emailer):
        emailer = 'Larry Summers'
    elif DARREN_INDKE.search(emailer):
        emailer = 'Darren Indke'
    elif 'starr, ken' in emailer.lower():
        emailer = 'Ken Starr'
    elif 'boris nikoli' in emailer.lower():
        emailer = 'Boris Nikolice'
    elif emailer.lower().startswith('nicholas rib'):
        emailer = 'Nicholas Ribis'
    elif emailer.lower().startswith('barry j. cohe'):
        emailer = 'barry j. cohen'
    elif emailer.lower().startswith('pa ul krassner'):
        emailer = 'Paul Krassner'
    else:
        for possible_emailer in EMAILERS:
            if possible_emailer.lower() in emailer.lower():
                emailer = possible_emailer
                break

    if deep_debug:
        console.print(f"  -> Found email from '{emailer}'", style='dim')

    return emailer.lower()
