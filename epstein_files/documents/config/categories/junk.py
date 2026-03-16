from epstein_files.documents.config.categories.book import FIRE_AND_FURY
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

MEME = 'meme of'
OBAMA_JOKE = 'joke about Obama'


JUNK_CFGS = [
    DocCfg(id='026678', note=f"fragment of image metadata {QUESTION_MARKS}", date='2017-06-29'),
    DocCfg(id='022986', note=f"fragment of a screenshot {QUESTION_MARKS}"),
    DocCfg(id='033478', note=f'{MEME} Kim Jong Un reading {FIRE_AND_FURY}', date='2018-01-05', duplicate_ids=['032713']),
    DocCfg(id='033177', note=f"{MEME} Trump with text 'WOULD YOU TRUST THIS MAN WITH YOUR DAUGHTER?'"),
    DocCfg(id='029564', note=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029353', note=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029352', note=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029351', note=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='029354', note=OBAMA_JOKE, date='2013-07-26'),
    DocCfg(id='031293'),
    # Completely redacted DOJ emails, no timestamp at all
    DocCfg(id='EFTA02731726'),
    DocCfg(id='EFTA02731728'),
]
