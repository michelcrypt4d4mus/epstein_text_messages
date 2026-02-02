from epstein_files.util.constant.urls import jmail_doj_2026_file_url


def test_jmail_doj_2026_file_url():
    assert jmail_doj_2026_file_url(12, 'EFTA02730274') == 'https://jmail.world/drive/vol00012-efta02730274-pdf'
