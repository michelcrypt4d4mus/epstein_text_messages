from datetime import datetime

from epstein_files.util.constant.names import CECILE_DE_JONGH, JEFFREY_EPSTEIN


def test_debug_dict(email):
    debug_dict = email._debug_dict()
    debug_dict.pop('file_info.local_path')

    assert debug_dict == {
        'EmailCfg.author': 'Christina Galbraith',
        'EmailCfg.author_reason': 'from "Christina media/PR"',
        'email.attachments': ['DSC_0418.JPG', 'DSC_0419.JPG', 'DSC_0424.JPG', 'Cefotaj Business Plan Final 5-18-11(1).docx'],
        'email.author': 'Christina Galbraith',
        'email.category': 'email',
        'email.is_interesting': None,
        'email.num_lines': 47,
        'email.recipients': [CECILE_DE_JONGH, JEFFREY_EPSTEIN],
        'email.subject': 'From Christina: Fwd: Project in Haiti: CEFOTAJ, SA',
        'email.timestamp': datetime(2012, 6, 22, 23, 8),
        'file_info.external_url': 'https://epstein.media/files/house_oversight_019446',
        'file_info.file_id': '019446',
        'file_info.file_size': 2923,
        'file_info.filename': 'HOUSE_OVERSIGHT_019446.txt',
        'file_info.url_slug': 'HOUSE_OVERSIGHT_019446',
    }


def test_is_doj_file(doj_file, messenger_log):
    assert doj_file.file_info.is_doj_file is True
    assert messenger_log.file_info.is_doj_file is False
