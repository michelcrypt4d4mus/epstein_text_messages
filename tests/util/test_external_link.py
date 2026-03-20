from rich.text import Text

from epstein_files.util.external_link import ExternalLink, extract_domain, hyperlink_line
from epstein_files.util.constant.urls import GH_PROJECT_URL, SUBSTACK_POST_TXT_MESSAGES_URL, SUBSTACK_POST_INSIGHTSPOD_URL, MASTODON_POST_URL

BBC_DOMAIN = 'bbc.co.uk'
BBC_URL = f'https://www.{BBC_DOMAIN}/news/world-africa-32020574'
BBC_LINK = ExternalLink(BBC_URL)
URL = 'https://foo.bar'


def test_create_hyperlinks():
    assert hyperlink_line('foobar') == Text('foobar')
    assert hyperlink_line(URL) == Text.from_markup(f"[link={URL}]{URL}[/link]")
    assert hyperlink_line(f"> {URL} blah") == Text('> ').append(Text.from_markup(f"[link={URL}]{URL}[/link]")).append(' blah')


def test_external_link():
    assert ExternalLink('foobar.com').url == 'https://foobar.com'
    assert ExternalLink('http://foobar.com').url == 'http://foobar.com'
    assert ExternalLink('https://foobar.com').url == 'https://foobar.com'
    assert BBC_LINK.domain_link(bracketed=True).plain == '[bbc]'


def test_extract_domain():
    assert extract_domain(BBC_URL) == 'bbc.co.uk'
    assert extract_domain(BBC_URL, strip_tld=True) == 'bbc'


def test_social_link():
    link = ExternalLink.social_link(SUBSTACK_POST_TXT_MESSAGES_URL)
    assert link.link_text == '@substack'
    assert link.domain() == 'cryptadamus.substack.com'
    assert link.domain(True) == 'cryptadamus.substack'  # TODO: not idea
    assert link.domain_stem == 'substack'
    link = ExternalLink.social_link(SUBSTACK_POST_INSIGHTSPOD_URL)
    assert link.link_text == '@substack'
    x = ExternalLink.social_link('https://x.com/Cryptadamist/status/2028867724307316882')
    assert x.link_text == '@twitter'
    assert ExternalLink.social_link(GH_PROJECT_URL).link_text == '@github'
    assert ExternalLink.social_link(MASTODON_POST_URL).link_text == '@mastodon'
