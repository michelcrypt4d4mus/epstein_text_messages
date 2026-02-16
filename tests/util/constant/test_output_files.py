from epstein_files.util.constant.output_files import HTML_BUILD_FILENAMES, SiteType


for site_type in SiteType:
    assert site_type in HTML_BUILD_FILENAMES
