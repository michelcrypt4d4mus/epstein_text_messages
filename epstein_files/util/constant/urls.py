import re
import urllib.parse
from typing import Callable, Literal

from inflection import parameterize
from rich.text import Text

from epstein_files.util.constant.output_files import *
from epstein_files.util.env import args
from epstein_files.util.file_helper import coerce_file_stem

# Style stuff
ARCHIVE_LINK_COLOR = 'slate_blue3'
TEXT_LINK = 'text_link'

# External site names
ExternalSite = Literal['epstein.media', 'epsteinify', 'EpsteinWeb', 'Jmail', 'RollCall', 'search X']
EPSTEIN_MEDIA = 'epstein.media'
EPSTEIN_WEB = 'EpsteinWeb'
EPSTEINIFY = 'epsteinify'
JMAIL = 'Jmail'
ROLLCALL = 'RollCall'
TWITTER = 'search X'

GH_PROJECT_URL = 'https://github.com/michelcrypt4d4mus/epstein_text_messages'
GH_MASTER_URL = f"{GH_PROJECT_URL}/blob/master"
ATTRIBUTIONS_URL = f'{GH_MASTER_URL}/epstein_files/util/constants.py'
EXTRACTS_BASE_URL = f'{GH_MASTER_URL}/emails_extracted_from_legal_filings'

extracted_file_url = lambda f: f"{EXTRACTS_BASE_URL}/{f}"


# External URLs
COFFEEZILLA_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'
COURIER_NEWSROOM_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
OVERSIGHT_REPUBLICANS_PRESSER_URL = 'https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/'
RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL = 'https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_'
SUBSTACK_URL = 'https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great'

# Document source sites
EPSTEINIFY_URL = 'https://epsteinify.com'
EPSTEIN_MEDIA_URL = 'https://epstein.media'
EPSTEIN_WEB_URL = 'https://epsteinweb.org'
JMAIL_URL = 'https://jmail.world'

DOC_LINK_BASE_URLS: dict[ExternalSite, str] = {
    EPSTEIN_MEDIA: f"{EPSTEIN_MEDIA_URL}/files/",
    EPSTEIN_WEB: f'{EPSTEIN_WEB_URL}/wp-content/uploads/epstein_evidence/images/',
    EPSTEINIFY: f"{EPSTEINIFY_URL}/document/",
    ROLLCALL: f'https://rollcall.com/factbase/epstein/file?id=',
}


epsteinify_api_url = lambda file_stem: f"{EPSTEINIFY_URL}/api/documents/{file_stem}"
epsteinify_doc_link_markup = lambda filename_or_id, style = TEXT_LINK: external_doc_link_markup(EPSTEINIFY, filename_or_id, style)
epsteinify_doc_link_txt = lambda filename_or_id, style = TEXT_LINK: Text.from_markup(external_doc_link_markup(filename_or_id, style))
epsteinify_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[EPSTEINIFY], file_stem)
epsteinify_name_url = lambda name: f"{EPSTEINIFY_URL}/?name={urllib.parse.quote(name)}"

epstein_media_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[EPSTEIN_MEDIA], file_stem, 'lower')
epstein_media_doc_link_markup = lambda filename_or_id, style = TEXT_LINK: external_doc_link_markup(EPSTEIN_MEDIA, filename_or_id, style)
epstein_media_doc_link_txt = lambda filename_or_id, style = TEXT_LINK: Text.from_markup(epstein_media_doc_link_markup(filename_or_id, style))
epstein_media_person_url = lambda person: f"{EPSTEIN_MEDIA_URL}/people/{parameterize(person)}"

epstein_web_doc_url = lambda file_stem: f"{DOC_LINK_BASE_URLS[EPSTEIN_WEB]}/{file_stem}.jpg"
epstein_web_person_url = lambda person: f"{EPSTEIN_WEB_URL}/{parameterize(person)}"
epstein_web_search_url = lambda s: f"{EPSTEIN_WEB_URL}/?ewmfileq={urllib.parse.quote(s)}&ewmfilepp=20"

rollcall_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[ROLLCALL], file_stem, 'title')

search_jmail_url = lambda txt: f"{JMAIL_URL}/search?q={urllib.parse.quote(txt)}"
search_twitter_url = lambda txt: f"https://x.com/search?q={urllib.parse.quote(txt)}&src=typed_query&f=live"


PERSON_LINK_BUILDERS: dict[ExternalSite, Callable[[str], str]] = {
    EPSTEIN_MEDIA: epstein_media_person_url,
    EPSTEIN_WEB: epstein_web_person_url,
    EPSTEINIFY: epsteinify_name_url,
    JMAIL: search_jmail_url,
    TWITTER: search_twitter_url,
}


def build_doc_url(base_url: str, filename_or_id: int | str, case: Literal['lower', 'title'] | None = None) -> str:
    file_stem = coerce_file_stem(filename_or_id)
    file_stem = file_stem.lower() if case == 'lower' or EPSTEIN_MEDIA in base_url else file_stem
    file_stem = file_stem.title() if case == 'title' else file_stem
    return f"{base_url}{file_stem}"


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


def other_site_type() -> SiteType:
    return TEXT_MESSAGE if args.all_emails else EMAIL


def other_site_url() -> str:
    return SITE_URLS[other_site_type()]


CRYPTADAMUS_TWITTER = link_markup('https://x.com/cryptadamist', '@cryptadamist')
THE_OTHER_PAGE_MARKUP = link_markup(other_site_url(), 'the other page', style='light_slate_grey bold')
THE_OTHER_PAGE_TXT = Text.from_markup(THE_OTHER_PAGE_MARKUP)
