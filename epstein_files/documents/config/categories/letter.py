from epstein_files.documents.config.config_builder import blaine_letter
from epstein_files.documents.config.doc_cfg import CommunicationCfg
from epstein_files.people.names import LEON_BLACK


# This category makes is_interesting default to True
LETTER_CFGS = [
    CommunicationCfg(
        id='026011',
        author='Gennady Mashtalyar',
        date='2016-06-24',  # date is based on Brexit reference but he could be backtesting,
        description=f"about algorithmic trading",
    ),
    CommunicationCfg(id='026134', recipients=['George'], description=f'about opportunities to buy banks in Ukraine'),
    blaine_letter(id='019086', date='2015-05-27', suffix='naming various Putin puppet regimes', show_full_panel=True),
    blaine_letter(id='019474', date='2015-05-29'),
    blaine_letter(id='019476', date='2015-06-01'),

    # DOJ files
    CommunicationCfg(id='EFTA00007609', recipients=['Alberto'], duplicate_ids=['EFTA00007582']),
    CommunicationCfg(id='EFTA02731023', author='Senator Ron Wyden', recipients=[LEON_BLACK], is_interesting=False),
    CommunicationCfg(id='EFTA02731018', author='Senator Ron Wyden', recipients=['Marc Rowan'], is_interesting=False),
]
