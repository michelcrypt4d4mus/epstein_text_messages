from datetime import datetime

from epstein_files.people.names import *
from epstein_files.util.helpers.data_helpers import coerce_utc_strict


def test_debug_dict(email):
    debug_dict = email._debug_dict()
    debug_dict.pop('file_info.local_path')

    assert debug_dict == {
        'EmailCfg.author': 'Christina Galbraith',
        'EmailCfg.author_reason': 'from "Christina media/PR", "Dear Unik" for recipient',
        'EmailCfg.is_in_chrono': False,
        'EmailCfg.is_of_interest': True,
        'EmailCfg.is_valid_for_name_scan': True,
        'EmailCfg.recipients': [
            'Cecile de Jongh',
            'Jeffrey Epstein',
            'Unik',
        ],
        'file_info.external_url': 'https://epstein.media/files/house_oversight_019446',
        'file_info.file_id': '019446',
        'file_info.file_size': 2923,
        'file_info.filename': 'HOUSE_OVERSIGHT_019446.txt',
        'file_info.url_slug': 'HOUSE_OVERSIGHT_019446',
        'email.attachments': [
            'DSC_0418.JPG',
            'DSC_0419.JPG',
            'DSC_0424.JPG',
            'Cefotaj Business Plan Final 5-18-11(1).docx'
        ],
        'email.author': 'Christina Galbraith',
        'email.category': 'email',
        'email.entities': [
            CECILE_DE_JONGH,
            CHRISTINA_GALBRAITH,
            JEFFREY_EPSTEIN,
            EPSTEIN_VI_FOUNDATION,
            'Unik',
        ],
        'email.extracted_recipients': [],
        'email.header': {
            'attachments': 'DSC_0418.JPG; DSC_0419.JPG; DSC_0424.JPG; Cefotaj Business Plan Final 5-18-11(1).docx',
            'author': 'Jeffrey Epstein <jeffreyepsteinorg©gmail.com >',
            'cc': [
                'Jeffrey Epstein <jeevacation@gmail.com>',
                'Cecile de Jongh',
            ],
            'sent_at': 'Friday, June 22 2012 11:08 PM',
            'subject': 'From Christina: Fwd: Project in Haiti: CEFOTAJ, SA',
        },
        'email.is_interesting': True,
        'email.is_word_count_worthy': True,
        'email.num_lines': 51,
        'email.recipients': [CECILE_DE_JONGH, JEFFREY_EPSTEIN, 'Unik'],
        'email.timestamp': coerce_utc_strict(datetime(2012, 6, 22, 23, 8)),
    }


def test_entities(get_doj_file):
    doc = get_doj_file('EFTA01582043')
    assert doc.entity_names == [CANTOR_FITZGERALD, DEUTSCHE_BANK, JP_MORGAN, SDNY]
    entity_names = [e.name for e in doc.entity_scan(exclude=[SDNY])]
    assert entity_names == [CANTOR_FITZGERALD, DEUTSCHE_BANK, JP_MORGAN]


def test_is_doj_file(doj_file, messenger_log):
    assert doj_file.file_info.is_doj_file is True
    assert messenger_log.file_info.is_doj_file is False
