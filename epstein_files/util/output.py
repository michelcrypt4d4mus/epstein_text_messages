import json
from os import unlink
from typing import cast

from rich.padding import Padding

from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import FIRST_FEW_LINES, OtherFile
from epstein_files.epstein_files import EpsteinFiles, count_by_month
from epstein_files.person import Person
from epstein_files.util.constant import output_files
from epstein_files.util.constant.html import *
from epstein_files.util.constant.names import *
from epstein_files.util.constant.output_files import EMAILERS_TABLE_PNG_PATH, JSON_FILES_JSON_PATH, JSON_METADATA_PATH
from epstein_files.util.constant.strings import AUTHOR, TIMESTAMP_STYLE
from epstein_files.util.data import dict_sets_to_lists, uniquify
from epstein_files.util.env import args
from epstein_files.util.file_helper import log_file_write
from epstein_files.util.logging import logger
from epstein_files.util.rich import *

DEVICE_SIGNATURE_SUBTITLE = f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown"
DEVICE_SIGNATURE = 'Device Signature'
DEVICE_SIGNATURE_PADDING = (1, 0)
OTHER_INTERESTING_EMAILS_SUBTITLE = 'Other Interesting Emails\n(these emails have been flagged as being of particular interest)'
PRINT_COLOR_KEY_EVERY_N_EMAILS = 150

# Order matters. Default names to print emails for.
DEFAULT_EMAILERS = [
    JEREMY_RUBIN,
    JABOR_Y,
    JOI_ITO,
    STEVEN_SINOFSKY,
    AL_SECKEL,
    DANIEL_SIAD,
    JEAN_LUC_BRUNEL,
    RENATA_BOLOTOVA,
    STEVEN_HOFFENBERG,
    MASHA_DROKOVA,
    EHUD_BARAK,
    MARTIN_NOWAK,
    STEVE_BANNON,
    TYLER_SHEARS,
    JIDE_ZEITLIN,
    CHRISTINA_GALBRAITH,
    DAVID_STERN,
    MOHAMED_WAHEED_HASSAN,
    JENNIFER_JACQUET,
    ZUBAIR_KHAN,
    None,
    JEFFREY_EPSTEIN,
]

INTERESTING_EMAIL_IDS = [
    '032229',  # Michael Wolff on strategy
    '028784',  # seminars: Money / Power
    '029342',  # Hakeem Jeffries
    '023454',  # Email invitation sent to tech CEOs + Epstein
    '030630',  # 'What happens with zubair's project?'
    '033178',  # 'How is it going with Zubair?'
    '022396',  # Ukraine friend
    '026505',  # I know how dirty trump is
    '029679',  # Trump's driver was the bag man
    '030781', '026258', '026260',  # Bannon cripto coin issues
    '023627',  # Michael Wolff article w/Brock
    '032359',  # Jabor e-currency
    #'023208',  # Extremely long Leon Black email chain
]


def print_email_timeline(epstein_files: EpsteinFiles) -> None:
    """Print a table of all emails in chronological order."""
    emails = Document.sort_by_timestamp([e for e in epstein_files.non_duplicate_emails() if not e.is_mailing_list()])
    title = f'Table of All {len(emails):,} Non-Junk Emails in Chronological Order (actual emails below)'
    table = Email.build_emails_table(emails, title=title, show_length=True)
    console.print(Padding(table, (2, 0)))
    print_subtitle_panel('The Chronologically Ordered Emails')
    console.line()

    for email in emails:
        console.print(email)


def print_emailers_info_png(epstein_files: EpsteinFiles) -> None:
    """Print tbe summary table of everyone in the files to an image."""
    print_color_key()
    console.line()
    all_emailers = sorted(epstein_files.emailers(), key=lambda person: person.sort_key())
    console.print(Person.emailer_info_table(all_emailers))
    svg_path = f"{EMAILERS_TABLE_PNG_PATH}.svg"
    console.save_svg(svg_path, theme=HTML_TERMINAL_THEME, title="Epstein Emailers")
    log_file_write(svg_path)
    import cairosvg
    cairosvg.svg2png(url=svg_path, write_to=str(EMAILERS_TABLE_PNG_PATH))
    log_file_write(EMAILERS_TABLE_PNG_PATH)
    unlink(svg_path)


def print_emails_section(epstein_files: EpsteinFiles) -> list[Email]:
    """Returns emails that were printed (may contain dupes if printed for both author and recipient)."""
    print_section_header(('Selections from ' if not args.all_emails else '') + 'His Emails')
    all_emailers = sorted(epstein_files.emailers(), key=lambda person: person.earliest_email_at())
    num_emails_printed_since_last_color_key = 0
    printed_emails: list[Email] = []
    people_to_print: list[Person]

    if args.names:
        people_to_print = epstein_files.person_objs(args.names)
    else:
        if args.all_emails:
            people_to_print = all_emailers
        else:
            people_to_print = epstein_files.person_objs(DEFAULT_EMAILERS)

        print_other_page_link(epstein_files)
        print_centered(Padding(Person.emailer_info_table(all_emailers, people_to_print), (2, 0, 1, 0)))

    for person in people_to_print:
        if person.name in epstein_files.uninteresting_emailers() and not args.names:
            continue

        printed_person_emails = person.print_emails()
        printed_emails.extend(printed_person_emails)
        num_emails_printed_since_last_color_key += len(printed_person_emails)

        # Print color key every once in a while
        if num_emails_printed_since_last_color_key > PRINT_COLOR_KEY_EVERY_N_EMAILS:
            print_color_key()
            num_emails_printed_since_last_color_key = 0

    if args.names:
        return printed_emails

    # Print other interesting emails
    printed_email_ids = [email.file_id for email in printed_emails]
    extra_emails = [e for e in epstein_files.for_ids(INTERESTING_EMAIL_IDS) if e.file_id not in printed_email_ids]

    if len(extra_emails) > 0:
        print_subtitle_panel(OTHER_INTERESTING_EMAILS_SUBTITLE)
        console.line()

        for other_email in extra_emails:
            console.print(other_email)
            printed_emails.append(cast(Email, other_email))

    if args.all_emails:
        _verify_all_emails_were_printed(epstein_files, printed_emails)

    _print_email_device_info(epstein_files)
    fwded_articles = [e for e in printed_emails if e.config and e.is_fwded_article()]
    log_msg = f"Rewrote {len(Email.rewritten_header_ids)} of {len(printed_emails)} email headers"
    logger.warning(f"{log_msg}, {len(fwded_articles)} of the emails were forwarded articles.")
    return printed_emails


def print_json_files(epstein_files: EpsteinFiles):
    """Print all the JsonFile objects"""
    if args.build:
        json_data = {jf.url_slug: jf.json_data() for jf in epstein_files.json_files}

        with open(JSON_FILES_JSON_PATH, 'w') as f:
            f.write(json.dumps(json_data, sort_keys=True))
            log_file_write(JSON_FILES_JSON_PATH)
    else:
        for json_file in epstein_files.json_files:
            console.line(2)
            console.print(json_file.summary_panel())
            console.print_json(json_file.json_str(), indent=4, sort_keys=False)


def print_json_metadata(epstein_files: EpsteinFiles) -> None:
    json_str = epstein_files.json_metadata()

    if args.build:
        with open(JSON_METADATA_PATH, 'w') as f:
            f.write(json_str)
            log_file_write(JSON_METADATA_PATH)
    else:
        console.print_json(json_str, indent=4, sort_keys=True)


def print_json_stats(epstein_files: EpsteinFiles) -> None:
    console.line(5)
    console.print(Panel('JSON Stats Dump', expand=True, style='reverse bold'), '\n')
    print_json(f"MessengerLog Sender Counts", MessengerLog.count_authors(epstein_files.imessage_logs), skip_falsey=True)
    print_json(f"Email Author Counts", epstein_files.email_author_counts(), skip_falsey=True)
    print_json(f"Email Recipient Counts", epstein_files.email_recipient_counts(), skip_falsey=True)
    print_json("Email signature_substitution_countss", epstein_files.email_signature_substitution_counts(), skip_falsey=True)
    print_json("email_author_device_signatures", dict_sets_to_lists(epstein_files.email_authors_to_device_signatures()))
    print_json("email_sent_from_devices", dict_sets_to_lists(epstein_files.email_device_signatures_to_authors()))
    print_json("unknown_recipient_ids", epstein_files.unknown_recipient_ids())
    print_json("count_by_month", count_by_month(epstein_files.all_documents()))


def print_other_files_section(files: list[OtherFile], epstein_files: EpsteinFiles) -> None:
    """Returns the OtherFile objects that were interesting enough to print."""
    title_pfx = '' if args.all_other_files else 'Selected '
    category_table = OtherFile.count_by_category_table(files, title_pfx=title_pfx)
    other_files_preview_table = OtherFile.files_preview_table(files, title_pfx=title_pfx)
    print_section_header(f"{FIRST_FEW_LINES} of {len(files)} {title_pfx}Files That Are Neither Emails Nor Text Messages")
    print_other_page_link(epstein_files)
    print_centered(Padding(category_table, (2, 0)))
    console.print(other_files_preview_table)


def print_text_messages_section(imessage_logs: list[MessengerLog]) -> None:
    """Print summary table and stats for text messages."""
    if not imessage_logs:
        logger.warning(f"No MessengerLog objects to output...")
        return

    print_section_header('All of His Text Messages')
    print_centered("(conversations are sorted chronologically based on timestamp of first message in the log file)", style='dim')
    console.line(2)

    if not args.names:
        print_centered(MessengerLog.summary_table(imessage_logs))
        console.line(2)

    for log_file in imessage_logs:
        console.print(Padding(log_file))
        console.line(2)


def write_urls() -> None:
    """Write _URL style constant variables to URLS_ENV file so bash scripts can load as env vars."""
    url_vars = {k: v for k, v in vars(output_files).items() if k.endswith('URL') and not k.startswith('GH')}

    if not args.suppress_output:
        console.line()

    with open(URLS_ENV, 'w') as f:
        for var_name, url in url_vars.items():
            key_value = f"{var_name}='{url}'"

            if not args.suppress_output:
                console.print(key_value, style='dim')

            f.write(f"{key_value}\n")

    if not args.suppress_output:
        console.line()

    logger.warning(f"Wrote {len(url_vars)} URL variables to '{URLS_ENV}'\n")


def _print_email_device_info(epstein_files: EpsteinFiles) -> None:
    print_subtitle_panel(DEVICE_SIGNATURE_SUBTITLE)
    console.print(_signature_table(epstein_files.email_device_signatures_to_authors(), (DEVICE_SIGNATURE, AUTHOR), ', '))
    console.print(_signature_table(epstein_files.email_authors_to_device_signatures(), (AUTHOR, DEVICE_SIGNATURE)))


def _signature_table(keyed_sets: dict[str, set[str]], cols: tuple[str, str], join_char: str = '\n') -> Padding:
    """Build table for who signed emails with 'Sent from my iPhone' etc."""
    title = 'Email Signatures Used By Authors' if cols[0] == AUTHOR else 'Authors Seen Using Email Signatures'
    table = build_table(title, header_style="bold reverse", show_lines=True)

    for i, col in enumerate(cols):
        table.add_column(col.title() + ('s' if i == 1 else ''))

    new_dict = dict_sets_to_lists(keyed_sets)

    for k in sorted(new_dict.keys()):
        table.add_row(highlighter(k or UNKNOWN), highlighter(join_char.join(sorted(new_dict[k]))))

    return Padding(table, DEVICE_SIGNATURE_PADDING)


def _verify_all_emails_were_printed(epstein_files: EpsteinFiles, already_printed_emails: list[Email]) -> None:
    """Log warnings if some emails were never printed."""
    email_ids_that_were_printed = set([email.file_id for email in already_printed_emails])
    logger.warning(f"Printed {len(already_printed_emails):,} emails of {len(email_ids_that_were_printed):,} unique file IDs.")
    missed_an_email = False

    for email in epstein_files.non_duplicate_emails():
        if email.file_id not in email_ids_that_were_printed:
            logger.warning(f"Failed to print {email.summary()}")
            missed_an_email = True

    if not missed_an_email:
        logger.warning(f"All {len(epstein_files.emails):,} emails printed at least once.")
