import re
import urllib.parse
from typing import Literal

from inflection import parameterize
from rich.text import Text

from epstein_files.util.constant.strings import EMAIL, TEXT_MESSAGE, SiteType
from epstein_files.util.file_helper import JSON_METADATA_PATH, WORD_COUNT_HTML_PATH, coerce_file_stem

# Style stuff
ARCHIVE_LINK_COLOR = 'slate_blue3'
TEXT_LINK = 'text_link'

# External site names
ExternalSite = Literal['epstein.media', 'epsteinify', 'EpsteinWeb']

EPSTEIN_MEDIA = 'epstein.media'
EPSTEIN_WEB = 'EpsteinWeb'
EPSTEINIFY = 'epsteinify'
JMAIL = 'Jmail'


# Cryptadamus URLs
GH_PAGES_BASE_URL = 'https://michelcrypt4d4mus.github.io'
TEXT_MSGS_BASE_URL = f"{GH_PAGES_BASE_URL}/epstein_text_messages"
JSON_METADATA_URL = f'{TEXT_MSGS_BASE_URL}/{JSON_METADATA_PATH.name}'
WORD_COUNT_URL = f'{TEXT_MSGS_BASE_URL}/{WORD_COUNT_HTML_PATH.name}'

SITE_URLS: dict[SiteType, str] = {
    EMAIL: f'{GH_PAGES_BASE_URL}/epstein_emails_house_oversight/',  # TODO should just be same repo
    TEXT_MESSAGE: TEXT_MSGS_BASE_URL,
}

GH_PROJECT_URL = 'https://github.com/michelcrypt4d4mus/epstein_text_messages'
GH_MASTER_URL = f"{GH_PROJECT_URL}/blob/master"
ATTRIBUTIONS_URL = f'{GH_MASTER_URL}/epstein_files/util/constants.py'
EXTRACTS_BASE_URL = f'{GH_MASTER_URL}/emails_extracted_from_legal_filings'

extracted_file_url = lambda f: f"{EXTRACTS_BASE_URL}/{f}"


# External URLs
COFFEEZILLA_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'
COURIER_NEWSROOM_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
EPSTEINIFY_URL = 'https://epsteinify.com'
EPSTEIN_MEDIA_URL = 'https://www.epstein.media'
EPSTEIN_WEB_URL = 'https://epsteinweb.org'
JMAIL_URL = 'https://jmail.world'
OVERSIGHT_REPUBLICANS_PRESSER_URL = 'https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/'
RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL = 'https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_'
SUBSTACK_URL = 'https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great'

DOC_LINK_BASE_URLS: dict[ExternalSite, str] = {
    EPSTEIN_MEDIA: f"{EPSTEIN_MEDIA_URL}/files",
    EPSTEIN_WEB: f'{EPSTEIN_WEB_URL}/wp-content/uploads/epstein_evidence/images',
    EPSTEINIFY: f"{EPSTEINIFY_URL}/document",
}


# TODO: epsteinify.com seems to be down as of 2025-12-30, switched to epstein.web for links
epsteinify_api_url = lambda file_id: f"{EPSTEINIFY_URL}/api/documents/HOUSE_OVERSIGHT_{file_id}"
epsteinify_doc_link_markup = lambda filename_or_id, style = TEXT_LINK: external_doc_link_markup(EPSTEINIFY, filename_or_id, style)
epsteinify_doc_link_txt = lambda filename_or_id, style = TEXT_LINK: Text.from_markup(external_doc_link_markup(filename_or_id, style))
epsteinify_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[EPSTEINIFY], file_stem)
epsteinify_name_url = lambda name: f"{EPSTEINIFY_URL}/?name={urllib.parse.quote(name)}"

epstein_media_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[EPSTEIN_MEDIA], file_stem, True)
epstein_media_doc_link_markup = lambda filename_or_id, style = TEXT_LINK: external_doc_link_markup(EPSTEIN_MEDIA, filename_or_id, style)
epstein_media_doc_link_txt = lambda filename_or_id, style = TEXT_LINK: Text.from_markup(epstein_media_doc_link_markup(filename_or_id, style))

epstein_web_doc_url = lambda file_stem: f"{DOC_LINK_BASE_URLS[EPSTEIN_WEB]}/{file_stem}.jpg"
epstein_web_person_url = lambda person: f"{EPSTEIN_WEB_URL}/{parameterize(person)}"
epstein_web_search_url = lambda s: f"{EPSTEIN_WEB_URL}/?ewmfileq={urllib.parse.quote(s)}&ewmfilepp=20"

search_archive_url = lambda txt: f"{COURIER_NEWSROOM_ARCHIVE_URL}&q={urllib.parse.quote(txt)}&p=1"
search_coffeezilla_url = lambda txt: f"{COFFEEZILLA_ARCHIVE_URL}&q={urllib.parse.quote(txt)}&p=1"
search_jmail_url = lambda txt: f"{JMAIL_URL}/search?q={urllib.parse.quote(txt)}"
search_twitter_url = lambda txt: f"https://x.com/search?q={urllib.parse.quote(txt)}&src=typed_query&f=live"


def build_doc_url(base_url: str, filename_or_id: int | str, lowercase: bool = False) -> str:
    file_stem = coerce_file_stem(filename_or_id)
    file_stem = file_stem.lower() if lowercase else file_stem
    return f"{base_url}/{file_stem}"


def external_doc_link_markup(site: ExternalSite, filename_or_id: int | str, style: str = TEXT_LINK) -> str:
    url = build_doc_url(DOC_LINK_BASE_URLS[site], filename_or_id)
    return link_markup(url, coerce_file_stem(filename_or_id), style)


def external_doc_link_txt(site: ExternalSite, filename_or_id: int | str, style: str = TEXT_LINK) -> Text:
    return Text.from_markup(external_doc_link_markup(site, filename_or_id, style))


def link_markup(
    url: str,
    link_text: str | None = None,
    style: str | None = ARCHIVE_LINK_COLOR,
    underline: bool = True
) -> str:
    link_text = link_text or url.removeprefix('https://')
    style = ((style or '') + (' underline' if underline else '')).strip()
    return (f"[{style}][link={url}]{link_text}[/link][/{style}]")


def link_text_obj(url: str, link_text: str | None = None, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(link_markup(url, link_text, style))


def search_coffeezilla_link(text: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return link_text_obj(search_coffeezilla_url(text), link_txt or text, style)


CRYPTADAMUS_TWITTER = link_markup('https://x.com/cryptadamist', '@cryptadamist')
