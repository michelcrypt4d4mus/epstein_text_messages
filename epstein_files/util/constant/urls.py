import re
import urllib.parse

from inflection import parameterize
from rich.text import Text

from epstein_files.util.constant.strings import EMAIL, HOUSE_OVERSIGHT_PREFIX, TEXT_MESSAGE
from epstein_files.util.file_helper import build_filename_for_id

# External site names
EPSTEIN_WEB = 'EpsteinWeb'.lower()
EPSTEINIFY = 'epsteinify'
JMAIL = 'Jmail'

# Style stuff
ARCHIVE_LINK_COLOR = 'slate_blue3'
TEXT_LINK = 'text_link'

# URLs
ATTRIBUTIONS_URL = 'https://github.com/michelcrypt4d4mus/epstein_text_messages/blob/master/epstein_files/util/constants.py'
COFFEEZILLA_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'
COURIER_NEWSROOM_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
EPSTEINIFY_URL = 'https://epsteinify.com'
EPSTEIN_WEB_URL = 'https://epsteinweb.org'
EPSTEIN_WEB_DOC_URL = f'{EPSTEIN_WEB_URL}/wp-content/uploads/epstein_evidence/images'
JMAIL_URL = 'https://jmail.world'
OVERSIGHT_REPUBLICANS_PRESSER_URL = 'https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/'
RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL = 'https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_'
SUBSTACK_URL = 'https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great'

SITE_URLS = {
    EMAIL: 'https://michelcrypt4d4mus.github.io/epstein_emails_house_oversight/',
    TEXT_MESSAGE: 'https://michelcrypt4d4mus.github.io/epstein_text_messages/',
}


epsteinify_api_url = lambda file_id: f"{EPSTEINIFY_URL}/api/documents/HOUSE_OVERSIGHT_{file_id}"
epsteinify_doc_url = lambda file_stem: f"{EPSTEINIFY_URL}/document/{file_stem}"
epsteinify_name_url = lambda name: f"{EPSTEINIFY_URL}/?name={urllib.parse.quote(name)}"

epstein_web_doc_url = lambda file_stem: f"{EPSTEIN_WEB_DOC_URL}/{file_stem}.jpg"
epstein_web_search_url = lambda s: f"{EPSTEIN_WEB_URL}/?ewmfileq={urllib.parse.quote(s)}&ewmfilepp=20"
epstein_web_person_url = lambda person: f"{EPSTEIN_WEB_URL}/{parameterize(person)}"

search_archive_url = lambda txt: f"{COURIER_NEWSROOM_ARCHIVE_URL}&q={urllib.parse.quote(txt)}&p=1"
search_coffeezilla_url = lambda txt: f"{COFFEEZILLA_ARCHIVE_URL}&q={urllib.parse.quote(txt)}&p=1"
search_jmail_url = lambda txt: f"{JMAIL_URL}/search?q={urllib.parse.quote(txt)}"
search_twitter_url = lambda txt: f"https://x.com/search?q={urllib.parse.quote(txt)}&src=typed_query&f=live"


def epsteinify_doc_link_markup(filename_or_id: int | str, style: str = TEXT_LINK) -> str:
    if isinstance(filename_or_id, int) or not filename_or_id.startswith(HOUSE_OVERSIGHT_PREFIX):
        file_stem = build_filename_for_id(filename_or_id)
    else:
        file_stem = str(filename_or_id)

    return link_markup(epsteinify_doc_url(file_stem), file_stem, style)


def epsteinify_doc_link_txt(filename_or_id: int | str, style: str = TEXT_LINK) -> Text:
    return Text.from_markup(epsteinify_doc_link_markup(filename_or_id, style))


def highlight_regex_match(text: str, pattern: re.Pattern, style: str = 'cyan') -> Text:
    """Replace 'pattern' matches with markup of the match colored with 'style'."""
    return Text.from_markup(pattern.sub(rf'[{style}]\1[/{style}]', text))


def link_markup(url: str, link_text: str, style: str | None = ARCHIVE_LINK_COLOR, underline: bool = True) -> str:
    style = (style or '') + (' underline' if underline else '')
    return (f"[{style}][link={url}]{link_text}[/link][/{style}]")


def link_text_obj(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(link_markup(url, link_text, style))


def search_coffeezilla_link(text: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return link_text_obj(search_coffeezilla_url(text), link_txt or text, style)
