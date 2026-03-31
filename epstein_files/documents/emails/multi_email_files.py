import re
from datetime import datetime

from epstein_files.documents.documents.doc_list import DocList
from epstein_files.documents.email import Email
from epstein_files.output.rich import console
from epstein_files.people.names import (ADA_CLAPP, CHRISTOPHER_DILORIO, HEATHER_GRAY, JEFFREY_EPSTEIN,
     LEON_BLACK, MELANIE_SPINELLA, sort_names)
from epstein_files.util.constant.strings import LEON_BLACK_EMAIL_ID, OcrRepair
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import groupby
from epstein_files.util.logging import logger

DILORIO_SPLIT = '\nFrom: Chris'
LEON_BLACK_EMAIL_REGEX = re.compile(r"^(From: .{,50}\nDate:|Date: ).*?(?=(From|Date|\Z))", re.DOTALL | re.MULTILINE)
LEON_BLACK_FWD_REGEX = re.compile(r"^-+(Forwarded|Original) message-+", re.MULTILINE)
LEON_BLACK_OCR_REPAIRS: OcrRepair = {re.compile('^ate: ', re.MULTILINE): 'Date: '}
TO_JEFFREY_REGEX = re.compile(r"^Jeffrey-", re.MULTILINE)
TO_LEON_REGEX = re.compile(r"^Leon,", re.MULTILINE)


def split_up_multi_email_files(big_emails: list[Email]) -> list[Email]:
    """
    Some files have 100+ emails concatenated into one file so we split them up in a bespoke way.
    Has side effect of setting `_was_split_up=True` for all `big_emails` which removes them from
    `EpsteinFiles.documents` list so they can only be accessed through `EpsteinFiles._documents`.
    """
    author_emails = groupby(big_emails, lambda e: e.author)
    authors = sort_names([name for name in author_emails.keys()])
    assert authors == [None, CHRISTOPHER_DILORIO], f"Unexpected author in big_emails: {authors}"

    for big_email in big_emails:
        big_email._was_split_up = True

    return [
        *_split_up_dilorio_whistleblower_emails(author_emails[CHRISTOPHER_DILORIO]),
        *_split_up_leon_black(author_emails[None]),
    ]


def _split_up_dilorio_whistleblower_emails(dilorio_emails: list[Email]) -> list[Email]:
    """Dilorio is some kind of finance whistleblower. his emails are not Epstein related but very interesting."""
    sub_emails = []
    skipped = []

    for big_email in dilorio_emails:
        texts = [
            (f"{DILORIO_SPLIT}{t}" if i > 0 else t).strip()
            for i, t in enumerate(big_email.text.split(DILORIO_SPLIT))
        ]

        logger.warning(f"Parsing {big_email} into {len(texts)} sub emails...")

        for i, text in enumerate(texts, 1):
            new_file_stem = _new_file_stem(big_email, i)
            email = Email(big_email.file_path.parent.joinpath(new_file_stem), text=text)
            email.extracted_author = big_email.author
            email.extracted_recipients = [] if email.extracted_recipients == ['Rnignc Lapnai PP'] else email.extracted_recipients
            email.extracted_recipients = email.extracted_recipients or ['SEC']
            email.header.to = email.header.to or ['SEC']  # avoids email being considered as having unknown recipient

            if not email.actual_text or email.lines[-1].startswith('Subject:'):
                email._warn(f"skipping empty {email.author} email...")
                skipped.append(email)
                continue

            sub_emails.append(email)

    return _uniquify_by_timestamp(sub_emails, dilorio_emails, 'dilorio', len(skipped))


def _split_up_leon_black(big_emails: list[Email]) -> list[Email]:
    """Create emails from gigantic Leon Black email."""
    assert len(big_emails) == 1, f"have {len(big_emails)} Leon Black emails, should have 1"
    big_email = big_emails[0]
    assert big_email.file_id == LEON_BLACK_EMAIL_ID, f"wrong Leon Black email {big_email.file_id}"
    big_text = big_email.repair_ocr_text(LEON_BLACK_OCR_REPAIRS, big_email.text)
    emails: list[Email] = []
    skipped = []
    fwded_email_text = ''

    for i, match in enumerate(LEON_BLACK_EMAIL_REGEX.finditer(big_text), 1):
        text = match.group(0)
        new_file_stem = _new_file_stem(big_email, i)

        if LEON_BLACK_FWD_REGEX.search(text):
            logger.warning(f"Fwded email detected in Leon Black email body, appending next email...")
            fwded_email_text = fwded_email_text + text
            continue
        else:
            email_text = fwded_email_text + text
            fwded_email_text = ''

        email = Email(big_email.file_path.parent.joinpath(new_file_stem), text=email_text)
        text_to_scan_for_recipients = email.actual_text[:120]

        if email.actual_text.strip().endswith("\nHeather"):
            email.extracted_author = HEATHER_GRAY
            email.extracted_recipients = [JEFFREY_EPSTEIN]

        if (TO_LEON_REGEX.search(email.text) and LEON_BLACK not in email.extracted_recipients) \
                or email.extracted_recipients == [MELANIE_SPINELLA]:
            email.extracted_recipients = sort_names(email.extracted_recipients + [LEON_BLACK])

        if 'Clapp' in text_to_scan_for_recipients:
            email.extracted_recipients += [ADA_CLAPP]

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

    return _uniquify_by_timestamp(emails, [big_email], LEON_BLACK, len(skipped))


def _new_file_stem(email: Email, i: int) -> str:
    return email.file_info.file_stem + f'_{i}.txt'


# TODO: move to DocList?
def _uniquify_by_timestamp(emails: list[Email], from_emails: list[Email], label: str, num_skipped: int = 0) -> list[Email]:
    """Uniquify by timestamp to eliminate dupes."""
    # Validate timestamps
    for email in emails:
        if email.timestamp is None or email.timestamp > Email.MAX_TIMESTAMP:
            raise ValueError(f"{email} bad timestamp in extracted email: {email.timestamp}")

    email_at_timestamp = {e.timestamp: e for e in DocList.sort_by_id(emails)}

    logger.warning(
        f"Created {len(emails)} ({len(email_at_timestamp)} unique) Emails from {len(from_emails)} {label} emails" \
        f", skipped {num_skipped} empty sub emails"
    )

    return [e for e in email_at_timestamp.values()]
