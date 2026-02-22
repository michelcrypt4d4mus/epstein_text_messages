from datetime import datetime

from epstein_files.documents.email import Email
from epstein_files.util.logging import logger

DILORIO_SPLIT = '\nFrom: Chris'


def split_up_dilorio(dilorio_emails: list[Email]) -> list[Email]:
    """Create emails from gigantic chris dilorio emails and mark the big email with `_was_split_up`."""
    sub_emails = []
    skipped = []

    for big_email in dilorio_emails:
        texts = [
            (f"{DILORIO_SPLIT}{t}" if i > 0 else t).strip()
            for i, t in enumerate(big_email.text.split(DILORIO_SPLIT))
        ]

        logger.warning(f"Parsing {big_email} into {len(texts)} sub emails...")
        big_email._was_split_up = True

        for i, text in enumerate(texts, 1):
            new_file_stem = big_email.file_info.file_stem + f'_{i}.txt'
            email = Email(big_email.file_path.parent.joinpath(new_file_stem), text=text)
            email.extracted_author = big_email.author
            email.extracted_recipients = email.extracted_recipients or ['SEC']

            if not email.actual_text or email.lines[-1].startswith('Subject:'):
                email.warn(f"skipping empty {email.author} email...")
                skipped.append(email)
                continue

            if email.timestamp > datetime(2026, 1, 1):
                big_email.file_info.open()
                big_email.file_info.open_pdf()
                raise ValueError(f"{email} bad timestamp in sub email: {email.timestamp}")

            sub_emails.append(email)

    # Uniquify by timestamp to eliminate dupes
    uniq_emails = {e.timestamp: e for e in sub_emails}

    logger.warning(
        f"Created {len(sub_emails)} ({len(uniq_emails)} unique) Email objs from {len(dilorio_emails)} dilorio emails" \
        f", skipped {len(skipped)} empty"
    )

    return [e for e in uniq_emails.values()]
