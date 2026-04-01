from epstein_files.documents.config.categories.legal import (EDWARDS_V_DERSHOWITZ, JANE_DOE_V_EPSTEIN_TRUMP,
     JANE_DOE_2_V_EPSTEIN, EPSTEIN_V_ROTHSTEIN_EDWARDS, REDACTED_V_EPSTEIN_ESATE)
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


DEPOSITION_CFGS = [
    DocCfg(id='021824', author=PAUL_G_CASSELL, note=f"from {EDWARDS_V_DERSHOWITZ}"),
    DocCfg(id='013463', author=SCOTT_ROTHSTEIN, note=f"from {JANE_DOE_V_EPSTEIN_TRUMP}", date='2010-03-23'),
    DocCfg(id='017488', author=SCOTT_ROTHSTEIN, note=f"from {EPSTEIN_V_ROTHSTEIN_EDWARDS}", date='2012-06-22'),
    # DOJ
    DocCfg(id='EFTA00615804', author=ALAN_DERSHOWITZ, date='2016-01-12', note='pages 334-461 (heavily redacted)'),
    DocCfg(
        id='EFTA00800508',
        author=BRAD_EDWARDS,
        highlight_quote="cars, boats, houses that were placed in Larry Visoski's name",
        note=EPSTEIN_V_ROTHSTEIN_EDWARDS,
        truncate_to=AUTO,
    ),
    DocCfg(
        id='EFTA00159483',
        author=LAWRANCE_VISOSKI,
        is_interesting=True,
        non_participants=[EHUD_BARAK, GLENN_DUBIN, LARRY_SUMMERS, NAOMI_CAMPBELL],
    ),
    DocCfg(id='EFTA00181472', author='Louella Rabuyo', date='2009-10-20'),
    DocCfg(id='EFTA00009229', author='Alex Acosta', note='pages 1-100', date='2020-04-30', is_interesting=10),
    DocCfg(id='EFTA00009329', author='Alex Acosta', note='pages 101-200', date='2020-04-30', is_interesting=10),
    DocCfg(id='EFTA00009016', author='Alex Acosta', note='pages 201-300', date='2020-04-30', is_interesting=10),
    DocCfg(id='EFTA00009116', author='Alex Acosta', note='pages 300-411', date='2020-04-30', is_interesting=10),
    DocCfg(id='EFTA00806751', author=IGOR_ZINOVIEV, note='notice of subpoena'),
    DocCfg(
        id='EFTA00008744',
        author='FBI',
        date='2021-03-29',
        note='grand jury testimony of Child Exploitation & Human Trafficking Task Force member',
    ),
    DocCfg(id='EFTA01108807', author='Jane Doe', date='2010-02-09', note='vol. III of IV'),
    DocCfg(id='EFTA01103374', author=JEFFREY_EPSTEIN, note=f'taken as part of {JANE_DOE_2_V_EPSTEIN}', is_interesting=9, truncate_to=5_000),
    DocCfg(id='EFTA00023557', author='victim', note=f'who says {GHISLAINE_MAXWELL} and Epstein pay for nudes'),
    # DocCfg(id='EFTA00064843', author=UNKNOWN_GIRL, note=f'{GHISLAINE_MAXWELL} "relentless"'),
    DocCfg(id='EFTA00078311', author=REDACTED_V_EPSTEIN_ESATE, note=f'Boies Schiller filing about sexual abuse of their client'),
    DocCfg(id='EFTA00105975', author=REDACTED_V_EPSTEIN_ESATE, note=f'{GHISLAINE_MAXWELL} "was relentless"'),
    DocCfg(id='EFTA00158752', author=REDACTED_V_EPSTEIN_ESATE, note=f'{GHISLAINE_MAXWELL} "was relentless"'),
    DocCfg(id='EFTA00182418', author=JANE_DOE_2_V_EPSTEIN, date='2010-03-15'),
    DocCfg(id='EFTA01246559', author=JANE_DOE_2_V_EPSTEIN, date='2010-04-09'),
    DocCfg(id='EFTA00181769', author=JANE_DOE_2_V_EPSTEIN, date='2010-04-13', note=f'questions about {STORY_COWLES}'),
    DocCfg(id='EFTA00298214', author='Joseph Recarey'),
]
