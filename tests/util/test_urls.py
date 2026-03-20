from epstein_files.people.names import *
from epstein_files.util.constant.urls import carstensen_person_url, jmail_doj_2026_file_url


def test_jmail_doj_2026_file_url():
    assert jmail_doj_2026_file_url(12, 'EFTA02730274') == 'https://jmail.world/drive/vol00012-efta02730274-pdf'


def test_carstensen_url():
    assert carstensen_person_url(LANDON_THOMAS) == 'https://tommycarstensen.com/epstein/people/landon-thomas-jr.html'
    assert carstensen_person_url('Stephen Alexander') == 'https://tommycarstensen.com/epstein/people/stephen-alexander.html'
    assert carstensen_person_url('Stephen D. Alexander') == 'https://tommycarstensen.com/epstein/people/stephen-alexander.html'
    assert carstensen_person_url('Dr. Stephen D. Alexander') == 'https://tommycarstensen.com/epstein/people/stephen-alexander.html'
