from epstein_files.util.helpers.link_helper import ExternalLink
from epstein_files.util.constant.urls import GH_PROJECT_URL, SUBSTACK_URL, SUBSTACK_INSIGHTS_POD


def test_external_link():
    pass


def test_social_link():
    link = ExternalLink.social_link(SUBSTACK_URL)
    assert link.link_text == '@substack'
    link = ExternalLink.social_link(SUBSTACK_INSIGHTS_POD)
    assert link.link_text == '@substack'
    x = ExternalLink.social_link('https://x.com/Cryptadamist/status/1990866804630036988')
    assert x.link_text == '@twitter'
    assert ExternalLink.social_link(GH_PROJECT_URL).link_text == '@github'
