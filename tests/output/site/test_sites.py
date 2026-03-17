from pathlib import Path

from epstein_files.output.site.sites import *
from epstein_files.util.env import args


def test_custom_html_build_path():
    assert Site.custom_html_build_path(HTML_DIR.joinpath('woof.html')).name == f"{CUSTOM_HTML_PREFIX}woof.html"
    assert Site.custom_html_build_path(Site.CURATED) == HTML_DIR.joinpath(CUSTOM_HTML_PREFIX + 'curated.html')


def test_html_output_path():
    assert Site.html_output_path(Site.CHRONOLOGICAL) == HTML_DIR.joinpath('index.html')
    assert Site.html_output_path(Site.DEVICE_SIGNATURES) == HTML_DIR.joinpath('device_signatures.html')

    old_args_names = args.names
    args.names = ['epstein', 'ghislaine']
    assert Site.html_output_path(Site.NAMES) == HTML_DIR.joinpath(f'{NAMES_PREFIX}epstein__ghislaine.html')
    args.names = old_args_names


def test_mobile_chronological():
    for site in Site:
        if CHRONOLOGICAL in site:
            assert Site.is_chronoligical(site), f"chronological site {site} is not considered chronological!"
        else:
            assert not Site.is_chronoligical(site), f"non-chronological site {site} is considered chronological!"

        if 'mobile' in site:
            assert Site.is_mobile(site), f"mobile site {site} is not considered mobile!"
        else:
            assert not Site.is_mobile(site), f"non-mobile site {site} is considered mobile!"
