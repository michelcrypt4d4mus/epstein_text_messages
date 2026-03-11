from pathlib import Path

from epstein_files.documents.documents.doc_cfg import DocCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


ARTS_CFGS = [
    DocCfg(id='018703', author=ANDRES_SERRANO, description=f"artist statement about Trump objects"),
    DocCfg(id='023438', author=BROCKMAN_INC, description=f"announcement of auction of 'Noise' by Daniel Kahneman, Olivier Sibony, and Cass Sunstein"),
    DocCfg(
        id='025147',
        author=BROCKMAN_INC,
        date='2016-10-23',
        description=f'Frankfurt Book Fair hot list includes book about Silk Road / Ross Ulbricht',
        is_interesting=True,
    ),
    DocCfg(id='030769', author='Independent Filmmaker Project (IFP)', description=f"2017 Gotham Awards invitation"),
    DocCfg(
        id='025205',
        author='Mercury Films',
        date='2010-02-01',
        description=f'partner profiles of Jennifer Baichwal, Nicholas de Pencier, Kermit Blackwood, Travis Rummel',
        duplicate_ids=['025210']
    ),
    DocCfg(
        id='028281',
        author='Wolfe Von Lenkiewicz & Victoria Golembiovskaya',
        date='2010-10-13',
        description=f'art show flier for "The House Of The Nobleman"',
    ),
]


DocCfg.set_categories(ARTS_CFGS, Path(__file__))
