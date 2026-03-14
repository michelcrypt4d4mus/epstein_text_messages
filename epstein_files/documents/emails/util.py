import re
from datetime import datetime

from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.output.rich import console
from epstein_files.people.names import JEFFREY_EPSTEIN, LEON_BLACK, MELANIE_SPINELLA, sort_names
from epstein_files.util.constant.strings import LEON_BLACK_EMAIL_ID
from epstein_files.util.env import args
from epstein_files.util.logging import logger

DILORIO_SPLIT = '\nFrom: Chris'
LEON_BLACK_EMAIL_REGEX = re.compile(r"^(From: .{,50}\nDate:|Date: ).*?(?=(From|Date|\Z))", re.DOTALL | re.MULTILINE)
LEON_BLACK_FWD_REGEX = re.compile(r"^-+(Forwarded|Original) message-+", re.MULTILINE)
TO_LEON_REGEX = re.compile(r"^Leon,", re.MULTILINE)
TO_JEFFREY_REGEX = re.compile(r"^Jeffrey-", re.MULTILINE)

LEON_BLACK_OCR_REPAIRS = {
    re.compile('^ate: ', re.MULTILINE): 'Date: ',
}


def split_up_dilorio_whistleblower_emails(dilorio_emails: list[Email]) -> list[Email]:
    """
    1. Create multiple `Email`s from huge Dilorio email files (each Dilorio file is actually many smaller emails concatenated).
    2. Mark the original big email with `_was_split_up=True`.
    """
    sub_emails = []
    skipped = []

    for big_email in dilorio_emails:
        texts = [
            (f"{DILORIO_SPLIT}{t}" if i > 0 else t).strip()
            for i, t in enumerate(big_email.text.split(DILORIO_SPLIT))
        ]

        big_email._was_split_up = True
        logger.warning(f"Parsing {big_email} into {len(texts)} sub emails...")

        for i, text in enumerate(texts, 1):
            new_file_stem = _new_file_stem(big_email, i)
            email = Email(big_email.file_path.parent.joinpath(new_file_stem), text=text)
            email.extracted_author = big_email.author
            email.extracted_recipients = email.extracted_recipients or ['SEC']

            if not email.actual_text or email.lines[-1].startswith('Subject:'):
                email._warn(f"skipping empty {email.author} email...")
                skipped.append(email)
                continue

            sub_emails.append(email)

    return _uniquify_by_timestamp(sub_emails, dilorio_emails, 'dilorio', len(skipped))


def split_up_leon_black(big_email: Email) -> list[Email]:
    """Create emails from gigantic Leon Black emails and mark the big email with `_was_split_up`."""
    if big_email.file_id != LEON_BLACK_EMAIL_ID:
        raise ValueError(f"wrong Leon Black email")

    big_text = big_email.repair_ocr_text(LEON_BLACK_OCR_REPAIRS, big_email.text)
    emails: list[Email] = []
    skipped = []
    fwded_email_text = ''

    for i, match in enumerate(LEON_BLACK_EMAIL_REGEX.finditer(big_text), 1):
        text = match.group(0)
        new_file_stem = _new_file_stem(big_email, i)

        if LEON_BLACK_FWD_REGEX.search(text):
            logger.warning(f"Fwded email detected, appending next email...")
            fwded_email_text = fwded_email_text + text
            continue
        else:
            email_text = fwded_email_text + text
            fwded_email_text = ''

        if len(email_text) < 80:
            logger.warning(f"Skipping {new_file_stem} because it's too short...")
            skipped.append(email_text)
            continue

        email = Email(big_email.file_path.parent.joinpath(new_file_stem), text=email_text)
        text_to_scan_for_recipients = email.actual_text[:120]

        if (TO_LEON_REGEX.search(email.text) and LEON_BLACK not in email.extracted_recipients) \
                or email.extracted_recipients == [MELANIE_SPINELLA]:
            email.extracted_recipients = sort_names(email.extracted_recipients + [LEON_BLACK])

        if 'Clapp' in text_to_scan_for_recipients:
            email.extracted_recipients += ['Ada Clapp']

        if 'Avantario' in text_to_scan_for_recipients:
            email.extracted_recipients += ['Joe Avantario']

        if email.recipients and not (email.extracted_author or TO_JEFFREY_REGEX.search(text_to_scan_for_recipients)):
            email.extracted_author = JEFFREY_EPSTEIN

            if JEFFREY_EPSTEIN in email.extracted_recipients:
                email.extracted_recipients = [r for r in email.extracted_recipients if r != JEFFREY_EPSTEIN]

        if args.raw or args.debug:
            print(f"\n--- RAW TEXT {new_file_stem} ---\n{email_text}\n--- END RAW TEXT {new_file_stem} ---\n")
            console.print(email)
            console.print(email._debug_txt())

        emails.append(email)

    big_email._was_split_up = True
    return _uniquify_by_timestamp(emails, [big_email], LEON_BLACK, len(skipped))


def _new_file_stem(email: Email, i: int) -> str:
    return email.file_info.file_stem + f'_{i}.txt'


def _uniquify_by_timestamp(emails: list[Email], from_emails: list[Email], label: str, num_skipped: int = 0) -> list[Email]:
    """Uniquify by timestamp to eliminate dupes."""
    # Validate timestamps
    for email in emails:
        if email.timestamp is None or email.timestamp > Email.MAX_TIMESTAMP:
            raise ValueError(f"{email} bad timestamp in extracted email: {email.timestamp}")

    email_at_timestamp = {e.timestamp: e for e in Document.sort_by_id(emails)}

    logger.warning(
        f"Created {len(emails)} ({len(email_at_timestamp)} unique) Emails from {len(from_emails)} {label} emails" \
        f", skipped {num_skipped} empty sub emails"
    )

    return [e for e in email_at_timestamp.values()]
