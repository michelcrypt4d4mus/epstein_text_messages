import re
import urllib.parse
from typing import Callable, Literal

from inflection import parameterize
from rich.text import Text

from epstein_files.util.env import args
from epstein_files.util.constant.output_files import SiteType, link_markup
from epstein_files.util.constant.strings import TEXT_LINK
from epstein_files.util.helpers.file_helper import coerce_file_stem
from epstein_files.util.helpers.string_helper import remove_question_marks

# External site names
ExternalSite = Literal['epstein.media', 'epsteinify', 'EpsteinWeb', 'Jmail', 'RollCall', 'search X']
EPSTEIN_MEDIA = 'epstein.media'
EPSTEIN_WEB = 'EpsteinWeb'
EPSTEINIFY = 'epsteinify'
JMAIL = 'Jmail'
ROLLCALL = 'RollCall'
TWITTER = 'search X'

TO_FROM = 'to/from'

# External URLs
COFFEEZILLA_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'
COURIER_NEWSROOM_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
DOJ_2026_FILE_BASE_URL = "https://www.justice.gov/epstein/files/DataSet%20"
EPSTEIN_DOCS_URL = 'https://epstein-docs.github.io'
OVERSIGHT_REPUBLICANS_PRESSER_URL = 'https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/'
RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL = 'https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_'
SUBSTACK_URL = 'https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great'
# DOJ docs
DOJ_2026_URL = 'https://www.justice.gov/epstein/doj-disclosures'
DOJ_SEARCH_URL = 'https://www.justice.gov/epstein/search'

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

# Misc
URL_SIGNIFIERS = ['?amp', 'amp?', 'cd=', 'click', 'CMP=', 'contentId', 'ft=', 'gclid', 'htm', 'mp=', 'keywords=', 'Id=', 'module=', 'mpweb', 'nlid=', 'ref=', 'smid=', 'sp=', 'usg=', 'utm']


# Epsteinify
epsteinify_api_url = lambda file_stem: f"{EPSTEINIFY_URL}/api/documents/{file_stem}"
epsteinify_doc_link_markup = lambda filename_or_id, style = TEXT_LINK: external_doc_link_markup(EPSTEINIFY, filename_or_id, style)
epsteinify_doc_link_txt = lambda filename_or_id, style = TEXT_LINK: Text.from_markup(external_doc_link_markup(filename_or_id, style))
epsteinify_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[EPSTEINIFY], file_stem)
epsteinify_name_url = lambda name: f"{EPSTEINIFY_URL}/?name={urllib.parse.quote(name)}"

# epstein.media
epstein_media_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[EPSTEIN_MEDIA], file_stem, 'lower')
epstein_media_doc_link_markup = lambda filename_or_id, style = TEXT_LINK: external_doc_link_markup(EPSTEIN_MEDIA, filename_or_id, style)
epstein_media_doc_link_txt = lambda filename_or_id, style = TEXT_LINK: Text.from_markup(epstein_media_doc_link_markup(filename_or_id, style))
epstein_media_person_url = lambda person: f"{EPSTEIN_MEDIA_URL}/people/{parameterize(person)}"

# EpsteinWeb
epstein_web_doc_url = lambda file_stem: f"{DOC_LINK_BASE_URLS[EPSTEIN_WEB]}/{file_stem}.jpg"
epstein_web_person_url = lambda person: f"{EPSTEIN_WEB_URL}/{parameterize(person)}"
epstein_web_search_url = lambda s: f"{EPSTEIN_WEB_URL}/?ewmfileq={urllib.parse.quote(s)}&ewmfilepp=20"

# Roll Call
rollcall_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[ROLLCALL], file_stem, 'title')

# Jmail
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


def doj_2026_file_url(dataset_id: int, file_stem: str) -> str:
    """justice.gov link e.g. 'https://www.justice.gov/epstein/files/DataSet%208/EFTA00009802.pdf'"""
    return f"{DOJ_2026_FILE_BASE_URL}{dataset_id}/{file_stem}.pdf"


def doj_2026_link_markup(dataset_id, file_stem: str, style: str = TEXT_LINK) -> str:
    url = doj_2026_file_url(dataset_id, file_stem)
    return link_markup(url, file_stem, style)


def jmail_doj_2026_file_url(dataset_id: int, file_stem: str) -> str:
    """Link to Jmail backup of DOJ file."""
    return f"{JMAIL_URL}/drive/vol{dataset_id:05}-{file_stem.lower()}-pdf"


def external_doc_link_markup(site: ExternalSite, filename_or_id: int | str, style: str = TEXT_LINK) -> str:
    url = build_doc_url(DOC_LINK_BASE_URLS[site], filename_or_id)
    return link_markup(url, coerce_file_stem(filename_or_id), style)


def external_doc_link_txt(site: ExternalSite, filename_or_id: int | str, style: str = TEXT_LINK) -> Text:
    return Text.from_markup(external_doc_link_markup(site, filename_or_id, style))


def internal_link_url(search_term: str) -> str:
    """Hack a local link with the `#:~text=` url comment."""
    return f"{this_site_url()}#:~:text={urllib.parse.quote(search_term)}"


def internal_person_link_url(name: str) -> str:
    """e.g. https://michelcrypt4d4mus.github.io/epstein_text_messages/all_emails_epstein_files_nov_2025.html#:~:text=to%2Ffrom%20Jack%20Goldberger"""
    return internal_link_url(f"{TO_FROM} {remove_question_marks(name)}")


def other_site_type() -> SiteType:
    return SiteType.CURATED if args._site_type != SiteType.CURATED else SiteType.GROUPED_EMAILS


def other_site_url() -> str:
    return SiteType.get_url(other_site_type())


def this_site_url() -> str:
    return SiteType.get_url(args._site_type)


CRYPTADAMUS_TWITTER = link_markup('https://x.com/cryptadamist', '@cryptadamist')
THE_OTHER_PAGE_MARKUP = link_markup(other_site_url(), 'the other page', style='light_slate_grey bold')
THE_OTHER_PAGE_TXT = Text.from_markup(THE_OTHER_PAGE_MARKUP)
