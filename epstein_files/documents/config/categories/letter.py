from epstein_files.documents.config.communication_cfg import CommunicationCfg
from epstein_files.documents.config.config_builder import blaine_letter, immigration_letter
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *


# This category makes is_interesting default to True
LETTER_CFGS = [
    CommunicationCfg(
        id='026011',
        author='Gennady Mashtalyar',
        date='2016-06-24',  # date is based on Brexit reference but he could be backtesting,
        note=f"about algorithmic trading",
    ),
    CommunicationCfg(id='026134', recipients=['George'], note=f'about opportunities to buy banks in Ukraine'),
    blaine_letter(id='019086', date='2015-05-27', suffix='naming various Putin puppet regimes', show_full_panel=True),
    blaine_letter(id='019474', date='2015-05-29'),
    blaine_letter(id='019476', date='2015-06-01'),
    immigration_letter('EFTA02389172', 'Michael Harrigan'),
    immigration_letter('EFTA00314931', TERJE_ROD_LARSEN, '2017-06-08', 'speaking for the International Peace Institute', show_with_name=MASHA_DROKOVA),
    immigration_letter('EFTA00308104', MARTIN_NOWAK, '2017-06-06', f'possibly about {MASHA_DROKOVA} visa', show_with_name=MASHA_DROKOVA),
    immigration_letter('EFTA00589797', TERJE_ROD_LARSEN, '2015-05-02'),
    immigration_letter('EFTA01086449', ARIANE_DE_ROTHSCHILD),
    immigration_letter('EFTA01143800', None, show_with_name=SVETLANA_POZHIDAEVA),
    immigration_letter('EFTA00537633', MARK_ZEFF, '2012-03-19', 'about SLK Designs, someone in interior design industry'),
    EmailCfg(id='EFTA02652017', note="inquiry about someone's immigration asylum application", is_interesting=True),

    # DOJ files
    CommunicationCfg(id='EFTA00007609', recipients=['Alberto'], duplicate_ids=['EFTA00007582']),
    CommunicationCfg(id='EFTA02731023', author='Senator Ron Wyden', recipients=[LEON_BLACK], is_interesting=False),
    CommunicationCfg(id='EFTA02731018', author='Senator Ron Wyden', recipients=['Marc Rowan'], is_interesting=False),
]
