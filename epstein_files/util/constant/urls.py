import re
import urllib.parse
from pathlib import Path
from typing import Callable, Literal

import requests
from inflection import parameterize
from rich.text import Text
from yaralyzer.util.helpers.interaction_helper import ask_to_proceed

from epstein_files.output.site.internal_links import TO_FROM
from epstein_files.output.site.sites import GH_PROJECT_URL, Site
from epstein_files.util.env import args
from epstein_files.util.constant.strings import TEXT_LINK
from epstein_files.util.external_link import SUBSTACK_POST_LINK_STYLE, ExternalLink, link_markup, link_text_obj
from epstein_files.util.helpers.file_helper import coerce_file_stem, local_doj_file_path, log_file_write
from epstein_files.util.helpers.string_helper import remove_question_marks
from epstein_files.util.logging import logger

# DOJ docs
DOJ_2026_URL = 'https://www.justice.gov/epstein/doj-disclosures'
DOJ_SEARCH_URL = 'https://www.justice.gov/epstein/search'

# External URLs
CARSTENSEN_URL = 'https://tommycarstensen.com/epstein'
CARSTENSEN_PEOPLE_URL = f"{CARSTENSEN_URL}/people"
COFFEEZILLA_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'
COURIER_NEWSROOM_ARCHIVE_URL = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
DOJ_2026_FILE_BASE_URL = "https://www.justice.gov/epstein/files/DataSet%20"
EPSTEIN_DOCS_URL = 'https://epstein-docs.github.io'
OVERSIGHT_REPUBS_PRESSER_URL = 'https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/'
OVERSIGHT_DRIVE_URL = 'https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_'
STANDARD_WORKS_URL = 'https://standardworks.ai/public-archives/epstein-files/'
# Articles
SVETLANA_NEWSGROUND = 'https://thenewsground.com/epstein-insider-revealed-as-daughter-of-fsb-translator-who-held-sensitive-russian-government-security-jobs/'

# External site names
EpsteinSite = Literal['Carstensen', 'epstein.media', 'epsteinify', 'EpsteinWeb', 'Jmail', 'RollCall', 'search X']

CARSTENSEN = 'Carstensen'
EPSTEIN_MEDIA = 'epstein.media'
EPSTEIN_WEB = 'EpsteinWeb'
EPSTEINIFY = 'epsteinify'
JMAIL = 'Jmail'
ROLLCALL = 'RollCall'
TWITTER = 'search X'

# Document source URLs
EPSTEINIFY_URL = f'https://{EPSTEINIFY}.com'
EPSTEIN_MEDIA_URL = f'https://{EPSTEIN_MEDIA}'
EPSTEIN_WEB_URL = 'https://epsteinweb.org'
JMAIL_URL = 'https://jmail.world'
JMAIL_RAW_URL = 'https://assets.getkino.com/documents'

DOC_LINK_BASE_URLS: dict[EpsteinSite, str] = {
    EPSTEIN_MEDIA: f"{EPSTEIN_MEDIA_URL}/files/",
    EPSTEIN_WEB: f'{EPSTEIN_WEB_URL}/wp-content/uploads/epstein_evidence/images/',
    EPSTEINIFY: f"{EPSTEINIFY_URL}/document/",
    ROLLCALL: f'https://rollcall.com/factbase/epstein/file?id=',
}

OFFICIAL_LINKS = [
    ExternalLink.official_link(
        DOJ_2026_URL,
        'DOJ Epstein Files Transparency Act Disclosures',
        comment='search',
        comment_url=DOJ_SEARCH_URL,
    ),
    ExternalLink.official_link(
        OVERSIGHT_REPUBS_PRESSER_URL,
        '2025 Oversight Committee Press Release',
        comment='raw files',
        comment_url=OVERSIGHT_DRIVE_URL,
    ),
]

EXTERNAL_LINKS = OFFICIAL_LINKS + [
    # ExternalLink(EPSTEIN_WEB_URL, 'biographies', link_text='EpsteinWeb'),
    ExternalLink(
        'randallscott25-star.github.io/epstein-forensic-finance/narratives/19_grand_opus_narrative.html',
        'Epstein Audit',
        comment='money',
    ),
    ExternalLink(JMAIL_URL, 'Jmail', 'read His Emails via Gmail interface'),
    ExternalLink(
        CARSTENSEN_URL,
        'Carstensen Epstein Archive',
        comment='findings',
        comment_url=f"{CARSTENSEN_URL}/findings.html",
        comment_style='light_sea_green italic',
    ),
    # ExternalLink(EPSTEIN_DOCS_URL, 'old docs', link_text='epstein-docs'),
    ExternalLink(EPSTEIN_MEDIA_URL, comment='raw document images'),
    # ExternalLink(EPSTEINIFY_URL, 'raw images alt', link_text='Epsteinify'),
    ExternalLink('bitcoinprotocol.org/epstein-bitcoin-emails', 'Epstein Bitcoin Emails', 'crypto'),
    ExternalLink('efta-search.vercel.app', 'EFTA Search', 'search filters'),
    ExternalLink('epsteinexposed.com', 'Epstein Exposed'),
    # ExternalLink('epsteinsearch.info'),  # Paid site
]


# Social media links
X_BASE_URL = 'https://x.com'
CRYPTADAMUS_X_URL = f'{X_BASE_URL}/Cryptadamist'
CRYPTADAMUS_X_LINK_MARKUP = link_markup(CRYPTADAMUS_X_URL, '@cryptadamist')
# Mastodon
MASTODON_POST_URL = 'universeodon.com/@cryptadamist/115572634993386057'
# Substack
SUBSTACK_BASE_URL = 'https://cryptadamus.substack.com'
SUBSTACK_POST_BASE_URL = f"{SUBSTACK_BASE_URL}/p"
SUBSTACK_POST_TXT_MESSAGES_URL = f'{SUBSTACK_POST_BASE_URL}/i-made-epsteins-text-messages-great'
SUBSTACK_POST_INSIGHTSPOD_URL = f'{SUBSTACK_POST_BASE_URL}/maybe-the-russian-bots-were-jeffrey'

SUBSTACK_POST_TXT_MSGS_LINK = ExternalLink(
    SUBSTACK_POST_TXT_MESSAGES_URL,
    "I Made Epstein's Text Messages Great Again (And You Should Read Them)",
    link_style=f'{SUBSTACK_POST_LINK_STYLE} bold'
)

SUBSTACK_INSIGHTS_LINK = ExternalLink(
    SUBSTACK_POST_INSIGHTSPOD_URL,
    '"Maybe The Russian Bots Were Jeffrey Epstein The Whole Time"',
    link_style=SUBSTACK_POST_LINK_STYLE
)

CRYPTADAMUS_SOCIAL_LINKS = [
    ExternalLink.social_link(MASTODON_POST_URL),
    ExternalLink.social_link(SUBSTACK_POST_TXT_MESSAGES_URL),
    ExternalLink.social_link(f'{CRYPTADAMUS_X_URL}/status/2028867724307316882'),
    ExternalLink.social_link(GH_PROJECT_URL),
]

# biographical links
DITE_ANATA_JUILLIARD_URL = 'https://usatoday.com/story/news/politics/2026/02/19/jeffrey-epstein-emails-files-power-for-benefit/88701802007/'
JULIA_SANTOS_REDDIT_URL = 'https://www.reddit.com/r/Epstein/comments/1qwbn5i/trafficker_julia_santos/'

EPSTEIN_DOCTORS_LINKS = [
    'https://www.nytimes.com/2026/02/28/us/jeffrey-epstein-doctors.html?unlocked_article_code=1.PlA.f4B2.BgLoXD-aVKkw&smid=url-share',
    'https://www.bloomberg.com/news/features/2026-02-28/epstein-emails-show-reliance-on-eva-dubin-mount-sinai-in-doj-files',
]


# Misc
PDF_MIME_TYPE = {'Accept': 'application/pdf'}
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

# Jmail
search_jmail_url = lambda txt: f"{JMAIL_URL}/search?q={urllib.parse.quote(txt)}"

# Roll Call
rollcall_doc_url = lambda file_stem: build_doc_url(DOC_LINK_BASE_URLS[ROLLCALL], file_stem, 'title')

# Twitter
search_twitter_url = lambda txt: f"{X_BASE_URL}/search?q={urllib.parse.quote(txt)}&src=typed_query&f=live"

# Wikipedia
wikipedia_url = lambda s: f"https://en.wikipedia.org/wiki/" + s.replace(' ', '_').replace('-', '_')


def build_doc_url(base_url: str, filename_or_id: int | str, case: Literal['lower', 'title'] | None = None) -> str:
    file_stem = coerce_file_stem(filename_or_id)
    file_stem = file_stem.lower() if case == 'lower' or EPSTEIN_MEDIA in base_url else file_stem
    file_stem = file_stem.title() if case == 'title' else file_stem
    return f"{base_url}{file_stem}"


def carstensen_person_url(name: str) -> str:
    name_parts = name.replace('.', '').removeprefix('Dr ').split()

    if len(name_parts) > 3 or (len(name_parts) == 3 and len(name_parts[1]) == 1):
        name = f"{name_parts[0]} {name_parts[-1]}"

    return f"{CARSTENSEN_PEOPLE_URL}/{name.replace(' ', '-')}.html".lower()


def doj_2026_file_url(dataset_id: int, file_stem: str) -> str:
    """justice.gov link e.g. 'https://www.justice.gov/epstein/files/DataSet%208/EFTA00009802.pdf'"""
    return f"{DOJ_2026_FILE_BASE_URL}{dataset_id}/{file_stem}.pdf"


def doj_2026_link_markup(dataset_id, file_stem: str, style: str = TEXT_LINK) -> str:
    url = doj_2026_file_url(dataset_id, file_stem)
    return link_markup(url, file_stem, style)


def download_jmail_pdf(file_id: str, data_set_id: int) -> Path:
    url = f"{JMAIL_RAW_URL}/{file_id}.pdf"
    output_path = local_doj_file_path(file_id, data_set_id)

    if output_path.exists():
        ask_to_proceed(f"File '{output_path}' already exists. Overwrite?")

    logger.warning(f"Downloading '{url}' to '{output_path}'...")
    response = requests.get(url, headers=PDF_MIME_TYPE, stream=True)
    response.raw.decode_content = True

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=100 * 1024):
            f.write(chunk)

    log_file_write(output_path)
    return output_path


def jmail_doj_2026_file_url(dataset_id: int, file_stem: str) -> str:
    """Link to Jmail backup of DOJ file."""
    return f"{JMAIL_URL}/drive/vol{dataset_id:05}-{file_stem.lower()}-pdf"


def external_doc_link_markup(site: EpsteinSite, filename_or_id: int | str, style: str = TEXT_LINK) -> str:
    url = build_doc_url(DOC_LINK_BASE_URLS[site], filename_or_id)
    return link_markup(url, coerce_file_stem(filename_or_id), style)


def external_doc_link_txt(site: EpsteinSite, filename_or_id: int | str, style: str = TEXT_LINK) -> Text:
    return Text.from_markup(external_doc_link_markup(site, filename_or_id, style))


def internal_link_url(search_term: str) -> str:
    """Hack a local link with the `#:~text=` url comment."""
    return f"{this_site_url()}#:~:text={urllib.parse.quote(search_term)}"


def internal_person_link_url(name: str) -> str:
    """Use the 'link to search term' magic URL comment to link to a person's emails, e.g. '#:~:text=to%2Ffrom%20Jack%20Gold"""
    return internal_link_url(f"{TO_FROM} {remove_question_marks(name)}")


def other_site() -> Site:
    return Site.CURATED if args._site != Site.CURATED else Site.EMAILERS


def other_site_url() -> str:
    return Site.get_url(other_site())


def this_site_url() -> str:
    return Site.get_url(args._site)


THE_OTHER_PAGE_MARKUP = link_markup(other_site_url(), 'the other page', style='light_slate_grey bold')
THE_OTHER_PAGE_TXT = Text.from_markup(THE_OTHER_PAGE_MARKUP)


PERSON_LINK_BUILDERS: dict[EpsteinSite, Callable[[str], str]] = {
    CARSTENSEN: carstensen_person_url,
    EPSTEIN_MEDIA: epstein_media_person_url,
    EPSTEIN_WEB: epstein_web_person_url,
    EPSTEINIFY: epsteinify_name_url,
    JMAIL: search_jmail_url,
    TWITTER: search_twitter_url,
}
