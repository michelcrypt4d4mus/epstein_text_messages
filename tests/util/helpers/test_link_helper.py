from epstein_files.util.helpers.link_helper import ExternalLink
from epstein_files.util.constant.urls import GH_PROJECT_URL, SUBSTACK_POST_TXT_MESSAGES_URL, SUBSTACK_POST_INSIGHTSPOD_URL, MASTODON_POST_URL


def test_external_link():
    assert ExternalLink('foobar.com').url == 'https://foobar.com'
    assert ExternalLink('http://foobar.com').url == 'http://foobar.com'
    assert ExternalLink('https://foobar.com').url == 'https://foobar.com'


def test_social_link():
    link = ExternalLink.social_link(SUBSTACK_POST_TXT_MESSAGES_URL)
    assert link.link_text == '@substack'
    assert link.domain == 'cryptadamus.substack.com'
    assert link.domain_stem == 'substack'
    link = ExternalLink.social_link(SUBSTACK_POST_INSIGHTSPOD_URL)
    assert link.link_text == '@substack'
    x = ExternalLink.social_link('https://x.com/Cryptadamist/status/2028867724307316882')
    assert x.link_text == '@twitter'
    assert ExternalLink.social_link(GH_PROJECT_URL).link_text == '@github'
    assert ExternalLink.social_link(MASTODON_POST_URL).link_text == '@mastodon'
