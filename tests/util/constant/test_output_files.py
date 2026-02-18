from epstein_files.output.sites import HTML_BUILD_FILENAMES, SiteType


for site_type in SiteType:
    assert site_type in HTML_BUILD_FILENAMES
