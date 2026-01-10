import json

from rich.padding import Padding

from epstein_files.documents.document import Document
from epstein_files.documents.email import KRASSNER_RECIPIENTS, Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import FIRST_FEW_LINES, OtherFile
from epstein_files.epstein_files import EpsteinFiles, count_by_month
from epstein_files.util.constant import output_files
from epstein_files.util.constant.html import *
from epstein_files.util.constant.names import *
from epstein_files.util.constant.output_files import JSON_FILES_JSON_PATH, JSON_METADATA_PATH
from epstein_files.util.constant.strings import DEFAULT_NAME_STYLE, TIMESTAMP_DIM, TIMESTAMP_STYLE
from epstein_files.util.data import dict_sets_to_lists, sort_dict
from epstein_files.util.env import args
from epstein_files.util.file_helper import log_file_write
from epstein_files.util.highlighted_group import (JUNK_EMAILERS, QUESTION_MARKS_TXT, get_category_txt_for_name,
     get_info_for_name, get_style_for_name, styled_name)
from epstein_files.util.logging import logger
from epstein_files.util.rich import *

OTHER_INTERESTING_EMAILS_SUBTITLE = 'Other Interesting Emails\n(these emails have been flagged as being of particular interest)'
PRINT_COLOR_KEY_EVERY_N_EMAILS = 150
ALT_INFO_STYLE = 'medium_purple4'

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
]

INVALID_FOR_EPSTEIN_WEB = JUNK_EMAILERS + KRASSNER_RECIPIENTS + [
    'ACT for America',
    'BS Stern',
    INTELLIGENCE_SQUARED,
    UNKNOWN,
]


def print_email_timeline(epstein_files: EpsteinFiles) -> None:
    """Print a table of all emails in chronological order."""
    emails = Document.sort_by_timestamp([e for e in epstein_files.non_duplicate_emails() if not e.is_junk_mail()])
    title = f'Table of All {len(emails):,} Non-Junk Emails in Chronological Order (actual emails below)'
    table = Email.build_emails_table(emails, title=title, show_length=True)
    console.print(Padding(table, (2, 0)))
    print_subtitle_panel('The Chronologically Ordered Emails')
    console.line()

    for email in emails:
        console.print(email)


def print_emails_section(epstein_files: EpsteinFiles) -> list[Email]:
    """Returns emails that were printed (may contain dupes if printed for both author and recipient)."""
    print_section_header(('Selections from ' if not args.all_emails else '') + 'His Emails')
    emailers_to_print: list[str | None]
    already_printed_emails: list[Email] = []
    num_emails_printed_since_last_color_key = 0

    if args.names:
        emailers_to_print = args.names
    else:
        if args.all_emails:
            emailers_to_print = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))
        else:
            emailers_to_print = DEFAULT_EMAILERS

        print_other_page_link(epstein_files)
        console.line(2)
        console.print(_table_of_selected_emailers(emailers_to_print, epstein_files))
        console.print(Padding(_all_emailers_table(epstein_files), (2, 0)))

    for author in emailers_to_print:
        author_emails = epstein_files.print_emails_for(author)
        already_printed_emails.extend(author_emails)
        num_emails_printed_since_last_color_key += len(author_emails)

        # Print color key every once in a while
        if num_emails_printed_since_last_color_key > PRINT_COLOR_KEY_EVERY_N_EMAILS:
            print_color_key()
            num_emails_printed_since_last_color_key = 0

    if args.names:
        return already_printed_emails

    # Print other interesting emails
    already_printed_ids = [email.file_id for email in already_printed_emails]
    extra_emails = [e for e in epstein_files.for_ids(INTERESTING_EMAIL_IDS) if e.file_id not in already_printed_ids]
    print_subtitle_panel(OTHER_INTERESTING_EMAILS_SUBTITLE)
    console.line()

    for other_email in extra_emails:
        console.print(other_email)

    epstein_files.print_email_device_info()

    if args.all_emails:
        _verify_all_emails_were_printed(epstein_files, already_printed_emails)

    fwded_articles = [e for e in already_printed_emails if e.config and e.is_fwded_article()]
    log_msg = f"Rewrote {len(Email.rewritten_header_ids)} of {len(already_printed_emails)} email headers"
    logger.warning(f"{log_msg}, {len(fwded_articles)} of the emails were forwarded articles.")
    return already_printed_emails


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
    print_json(f"Email Author Counts", epstein_files.email_author_counts, skip_falsey=True)
    print_json(f"Email Recipient Counts", epstein_files.email_recipient_counts, skip_falsey=True)
    print_json("Email signature_substitution_countss", epstein_files.email_signature_substitution_counts(), skip_falsey=True)
    print_json("email_author_device_signatures", dict_sets_to_lists(epstein_files.email_authors_to_device_signatures))
    print_json("email_sent_from_devices", dict_sets_to_lists(epstein_files.email_device_signatures_to_authors))
    print_json("email_unknown_recipient_file_ids", epstein_files.email_unknown_recipient_file_ids())
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


def _all_emailers_table(epstein_files: EpsteinFiles) -> Table:
    attributed_emails = [e for e in epstein_files.non_duplicate_emails() if e.author]
    footer = f"(identified {len(epstein_files.email_author_counts)} authors of {len(attributed_emails):,}"
    footer = f"{footer} out of {len(epstein_files.non_duplicate_emails()):,} emails)"
    counts_table = build_table("Everyone Who Sent or Received an Email in the Files", caption=footer)

    add_cols_to_table(counts_table, [
        'Name',
        {'name': 'Count', 'justify': 'right', 'style': 'bold bright_white'},
        {'name': 'Sent', 'justify': 'right', 'style': 'gray74'},
        {'name': 'Recv', 'justify': 'right', 'style': 'gray74'},
        {'name': 'First', 'style': TIMESTAMP_STYLE},
        {'name': 'Last', 'style': LAST_TIMESTAMP_STYLE},
        {'name': 'Days', 'justify': 'right', 'style': 'dim'},
        JMAIL,
        EPSTEIN_MEDIA,
        EPSTEIN_WEB,
        'Twitter',
    ])

    emailer_counts = {
        emailer: epstein_files.email_author_counts[emailer] + epstein_files.email_recipient_counts[emailer]
        for emailer in epstein_files.all_emailers(include_useless=True)
    }

    for name, count in sort_dict(emailer_counts):
        style = get_style_for_name(name, default_style=DEFAULT_NAME_STYLE)
        emails = epstein_files.emails_for(name)

        counts_table.add_row(
            Text.from_markup(link_markup(epsteinify_name_url(name or UNKNOWN), name or UNKNOWN, style)),
            f"{count:,}",
            str(epstein_files.email_author_counts[name]),
            str(epstein_files.email_recipient_counts[name]),
            emails[0].date_str(),
            emails[-1].date_str(),
            f"{epstein_files.email_conversation_length_in_days(name)}",
            link_text_obj(search_jmail_url(name), JMAIL) if name else '',
            link_text_obj(epstein_media_person_url(name), EPSTEIN_MEDIA) if _is_ok_for_epstein_web(name) else '',
            link_text_obj(epstein_web_person_url(name), EPSTEIN_WEB) if _is_ok_for_epstein_web(name) else '',
            link_text_obj(search_twitter_url(name), 'search X') if name else '',
        )

    return counts_table


def _is_ok_for_epstein_web(name: str | None) -> bool:
    """Return True if it's likely that EpsteinWeb has a page for this name."""
    if name is None or ' ' not in name:
        return False
    elif '@' in name or '/' in name or '??' in name:
        return False
    elif name in INVALID_FOR_EPSTEIN_WEB:
        return False

    return True


def _table_of_selected_emailers(_list: list[str | None], epstein_files: EpsteinFiles) -> Table:
    """Add the first emailed_at timestamp for each emailer if 'epstein_files' provided."""
    header_pfx = '' if args.all_emails else 'Selected '
    table = build_table(f'{header_pfx}Email Conversations Grouped by Counterparty Will Appear in this Order')
    table.add_column('Start Date')
    table.add_column('Name', max_width=25, no_wrap=True)
    table.add_column('Category', justify='center', style='dim italic')
    table.add_column('Num', justify='right', style='wheat4')
    table.add_column('Info', style='white italic')
    current_year = 1990
    current_year_month = current_year * 12
    grey_idx = 0

    for i, name in enumerate(_list):
        earliest_email_date = (epstein_files.earliest_email_at(name)).date()
        year_months = (earliest_email_date.year * 12) + earliest_email_date.month

        # Color year rollovers more brightly
        if current_year != earliest_email_date.year:
            grey_idx = 0
        elif current_year_month != year_months:
            grey_idx = ((current_year_month - 1) % 12) + 1

        current_year_month = year_months
        current_year = earliest_email_date.year
        category = get_category_txt_for_name(name)
        info = get_info_for_name(name)
        style = get_style_for_name(name, default_style='none')

        if name == JEFFREY_EPSTEIN:
            info = Text('(emails sent by Epstein to himself that would not otherwise be printed)', style=ALT_INFO_STYLE)
        if category and category.plain == 'paula':  # TODO: hacky
            category = None
        elif category and info:
            info = info.removeprefix(f"{category.plain}, ").removeprefix(category.plain)
        elif not name:
            info = Text('(emails whose author or recipient could not be determined)', style=ALT_INFO_STYLE)
        elif style == 'none' and '@' not in name and not (category or info):
            info = QUESTION_MARKS_TXT

        table.add_row(
            Text(str(earliest_email_date), style=f"grey{GREY_NUMBERS[grey_idx]}"),
            styled_name(name, default_style='dim'),
            category,
            f"{len(epstein_files.emails_for(name)):,}",
            info or '',
        )

    return table


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
