"""
Resumes and application letters.
"""
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

HBS_APPLICATION = f"{HARVARD} Business School application letter"
RESUME_OF = 'professional resumé'


RESUMÉ_CFGS = [
    DocCfg(
        id='029304',
        attached_to_email_id='029299',
        author=MICHAEL_J_BOCCIO,
        description=f"recommendation letter by {DONALD_TRUMP}",
    ),
    DocCfg(id='022367', author='Jack J. Grynberg', description=RESUME_OF, date='2014-07-01'),
    DocCfg(
        id='029302',
        attached_to_email_id='029299',
        author=MICHAEL_J_BOCCIO,
        description=f"{RESUME_OF} (former lawyer at the {TRUMP_ORG})",
        date='2011-08-07',
    ),
    DocCfg(
        id='029301',
        attached_to_email_id='029299',
        author=MICHAEL_J_BOCCIO,
        description=f"letter from former lawyer at the {TRUMP_ORG}",
        date='2011-08-07',
    ),
    DocCfg(id='029102', author=NERIO_ALESSANDRI, description=HBS_APPLICATION),
    DocCfg(id='029104', author=NERIO_ALESSANDRI, description=HBS_APPLICATION),
    DocCfg(id='015671', author='Robin Solomon', description=RESUME_OF, date='2015-06-02'),  # She left Mount Sinai at some point in 2015,
    DocCfg(id='015672', author='Robin Solomon', description=RESUME_OF, date='2015-06-02'),  # She left Mount Sinai at some point in 2015,
    DocCfg(id='029623', description=f'bio of Kathleen Harrington, Founding Partner, C/H Global Strategies'),
    DocCfg(id='EFTA00522933', author='Maria Macaraeg', description="applied to be housekeeper for Epstein", is_interesting=False),
]
