from pathlib import Path

from epstein_files.output.site.sites import *


def test_build_path():
    assert SiteType.build_path(SiteType.CHRONOLOGICAL) == HTML_DIR.joinpath('index.html')
    assert SiteType.build_path(SiteType.DEVICE_SIGNATURES) == HTML_DIR.joinpath('device_signatures.html')
