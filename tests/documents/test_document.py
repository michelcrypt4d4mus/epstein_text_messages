from datetime import datetime

from epstein_files.util.constant.names import CECILE_DE_JONGH, JEFFREY_EPSTEIN


def test_debug_dict(email):
    debug_dict = email._debug_dict()
    debug_dict['FileInfo'].pop('local_path')

    assert debug_dict == {
       'EmailCfg': {
            'author': 'Christina Galbraith',
            'author_reason': 'from "Christina media/PR"',
            'is_of_interest': True,
        },
        'FileInfo': {
            'external_url': 'https://epstein.media/files/house_oversight_019446',
            'file_id': '019446',
            'file_size': 2923,
            'filename': 'HOUSE_OVERSIGHT_019446.txt',
            'url_slug': 'HOUSE_OVERSIGHT_019446',
        },
        'email.attachments': [
            'DSC_0418.JPG',
            'DSC_0419.JPG',
            'DSC_0424.JPG',
            'Cefotaj Business Plan Final 5-18-11(1).docx'
        ],
        'email.author': 'Christina Galbraith',
        'email.category': 'email',
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
        'email.num_lines': 47,
        'email.recipients': [CECILE_DE_JONGH, JEFFREY_EPSTEIN],
        'email.timestamp': datetime(2012, 6, 22, 23, 8),
    }


def test_is_doj_file(doj_file, messenger_log):
    assert doj_file.file_info.is_doj_file is True
    assert messenger_log.file_info.is_doj_file is False
