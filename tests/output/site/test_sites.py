from pathlib import Path

from epstein_files.output.site.sites import *


def test_custom_html_build_path():
    assert SiteType.custom_html_build_path(HTML_DIR.joinpath('woof.html')).name == f"{CUSTOM_HTML_PREFIX}woof.html"
    assert SiteType.custom_html_build_path(SiteType.CURATED) == HTML_DIR.joinpath(CUSTOM_HTML_PREFIX + 'curated.html')


def test_html_output_path():
    assert SiteType.html_output_path(SiteType.CHRONOLOGICAL) == HTML_DIR.joinpath('index.html')
    assert SiteType.html_output_path(SiteType.DEVICE_SIGNATURES) == HTML_DIR.joinpath('device_signatures.html')
    assert SiteType.html_output_path(SiteType.NAMES) == HTML_DIR.joinpath('names.html')
