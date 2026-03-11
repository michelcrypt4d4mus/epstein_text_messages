from pathlib import Path

from epstein_files.documents.config.doc_cfg import DocCfg, EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


ACADEMIA_CFGS = [
    DocCfg(id='027004', author=JOSCHA_BACH, description=f"The Computational Structure of Mental Representation", date='2013-02-26'),
    DocCfg(
        id='014697',
        author=LAWRENCE_KRAUSS_ASU_ORIGINS,
        description=f'report: "Challenges of AI: Envisioning and Addressing Adverse Outcomes"',
        duplicate_ids=['011284']
    ),
    DocCfg(id='026731', author='Lord Martin Rees', description=f"speech at first inaugural Cornell Carl Sagan Lecture"),
    DocCfg(id='015501', author=f"{MOSHE_HOFFMAN}, Erez Yoeli, and Carlos David Navarrete", description=f"Game Theory and Morality"),
    DocCfg(
        id='026521',
        author=f"{MOSHE_HOFFMAN}, Erez Yoeli, and {MARTIN_NOWAK}",
        description=f"Cooperating Without Looking: Game Theory Model of Trust and Reciprocal Cooperation"
    ),
    DocCfg(id='022405', author=NOAM_CHOMSKY, description=f"letter attesting to Epstein's good character"),
    DocCfg(id='025143', author=ROBERT_TRIVERS, description=f"Africa, Parasites, Intelligence", date='2018-06-25'),
    DocCfg(id='029155', author=ROBERT_TRIVERS, description=f'response sent to the Gruterites ({GORDON_GETTY} fans)', date='2018-03-19'),
    DocCfg(
        id='033323',
        author=f"{ROBERT_TRIVERS} and Nathan H. Lents",
        description=f"'Does Trump Fit the Evolutionary Role of Narcissistic Sociopath?' (draft)",
        date='2018-12-07',
    ),
    DocCfg(id='023416', description=HARVARD_POETRY),
    DocCfg(id='023435', description=HARVARD_POETRY),
    DocCfg(id='023450', description=HARVARD_POETRY),
    DocCfg(id='023452', description=HARVARD_POETRY),
    DocCfg(id='029517', description=HARVARD_POETRY),
    DocCfg(id='029543', description=HARVARD_POETRY),
    DocCfg(id='029589', description=HARVARD_POETRY),
    DocCfg(id='029603', description=HARVARD_POETRY),
    DocCfg(id='029298', description=HARVARD_POETRY),
    DocCfg(id='029592', description=HARVARD_POETRY),
    DocCfg(id='019396', description=f'{HARVARD} Economics 1545 Professor Kenneth Rogoff syllabus'),
    DocCfg(id='022445', description=f"Inference: International Review of Science Feedback & Comments", date='2018-11-01'),
    DocCfg(
        id='029355',
        description=f'{SCREENSHOT} quote in book about {LARRY_SUMMERS}',
        dupe_type='quoted',
        duplicate_ids=['029356'],  # 029356 is zoomed in corner
        is_interesting=False,
    ),

    # DOJ Files
    DocCfg(
        id='EFTA01103509',
        author=BEN_GOERTZEL,
        date='2013-02-01',
        description='"Creating Robots with Toddler-Level Intelligence Using the OpenCog AGI Architecture" proposal for Epstein Foundation',
    ),
    DocCfg(
        id='EFTA01106148',
        author=GINO_YU,
        date='2011-05-01',
        description='OpenCog Hong Kong Project Interim Report',
    ),
    DocCfg(id='EFTA01114164', author=BEN_GOERTZEL, description='OpenCog Road Map 2011-2023', date='2011-01-01', date_uncertain=True),
    DocCfg(id='EFTA01114145', author=f"{BEN_GOERTZEL} and {GINO_YU}", description="OpenCog AGI Toddler Project", date='2011-06-01', date_uncertain=True),
    EmailCfg(id='EFTA00954900', description=f'Epstein donation to {MOUNT_SINAI}'),
    EmailCfg(id='EFTA00955864', description=f'Epstein donation to {MOUNT_SINAI}', is_interesting=False)
]
