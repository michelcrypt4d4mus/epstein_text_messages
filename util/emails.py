import re

from rich.console import Console

from .env import is_debug

DATE_REGEX = re.compile(r'^Date:\s*(.*)\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BROKEN_EMAIL_REEGEX = re.compile(r'^From:\s*\nSent:\s*\nTo:\s*\n(CC:\s*\n)?Subject:\s*\n(Importance:\s*\n)?(Attachments:\s*\n)?([\w ]{2,}.*)\n')
BAD_EMAILER_REGEX = re.compile('^(sent|attachments)|.*(11111111111|january|2016).*')
EPSTEIN_EMAIL_REGEX = re.compile(r'jee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE)
GHISLAINE_EMAIL_REGEX = re.compile(r'g ?max(well)?', re.IGNORECASE)
EHUD_BARAK_EMAIL_REGEX = re.compile(r'(ehud|h)\s*barak', re.IGNORECASE)
BANNON_EMAIL_REGEX = re.compile(r'steve bannon', re.IGNORECASE)
LARRY_SUMMERS_EMAIL_REGEX = re.compile(r'La(wrence|rry).*Summers', re.IGNORECASE)
DARREN_INDKE = re.compile(r'darren [il]ndyke', re.IGNORECASE)

EMAILERS = [
    'Al Seckel',
    'Boris Nikolic',
    'Glenn Dubin',
    'Lesley Groff',
    'Michael Wolff',
    'Richard Kahn',
    'Paul Krassner',
]

console = Console(color_system='256')


def extract_email_sender(file_text):
    email_match = EMAIL_REGEX.search(file_text)
    broken_match = BROKEN_EMAIL_REEGEX.search(file_text)
    date_match = DATE_REGEX.search(file_text)
    emailer = None

    if broken_match:
        emailer = broken_match.group(4) or broken_match.group(3) or broken_match.group(2) or broken_match.group(1)
    elif email_match:
        emailer = email_match.group(1)
    else:
        if is_debug:
            console.print(f"Failed to find an email pattern match!")

        return

    emailer = emailer.strip().strip('_').strip('[').strip(']').strip('*').strip('<').strip()

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
    else:
        for possible_emailer in EMAILERS:
            if possible_emailer.lower() in emailer.lower():
                emailer = possible_emailer
                break

    if is_debug:
        console.print(f"  -> Found email from '{emailer}'", style='dim')

    return emailer
