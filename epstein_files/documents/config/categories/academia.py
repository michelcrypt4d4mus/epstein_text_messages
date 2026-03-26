from pathlib import Path

from epstein_files.documents.config.communication_cfg import TextCfg, imessage_screenshot, skype_log
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *


ACADEMIA_CFGS = [
    DocCfg(id='027004', author=JOSCHA_BACH, note=f"The Computational Structure of Mental Representation", date='2013-02-26'),
    DocCfg(
        id='014697',
        author=ASU_ORIGINS_PROJECT,
        note=f'report: "Challenges of AI: Envisioning and Addressing Adverse Outcomes"',
        duplicate_ids=['011284']
    ),
    DocCfg(id='026731', author='Lord Martin Rees', note=f"speech at first inaugural Cornell Carl Sagan Lecture"),
    DocCfg(id='015501', author=f"{MOSHE_HOFFMAN}, Erez Yoeli, and Carlos David Navarrete", note=f"Game Theory and Morality"),
    DocCfg(
        id='026521',
        author=f"{MOSHE_HOFFMAN}, Erez Yoeli, and {MARTIN_NOWAK}",
        note=f"Cooperating Without Looking: Game Theory Model of Trust and Reciprocal Cooperation"
    ),
    DocCfg(id='022405', author=NOAM_CHOMSKY, note=f"letter attesting to Epstein's good character"),
    DocCfg(id='025143', author=ROBERT_TRIVERS, note=f"Africa, Parasites, Intelligence", date='2018-06-25'),
    DocCfg(id='029155', author=ROBERT_TRIVERS, note=f'response sent to the Gruterites ({GORDON_GETTY} fans)', date='2018-03-19'),
    DocCfg(
        id='033323',
        author=f"{ROBERT_TRIVERS}, Nathan H. Lents",
        note=f"'Does Trump Fit the Evolutionary Role of Narcissistic Sociopath?' (draft)",
        date='2018-12-07',
    ),
    DocCfg(id='023416', note=HARVARD_POETRY),
    DocCfg(id='023435', note=HARVARD_POETRY),
    DocCfg(id='023450', note=HARVARD_POETRY),
    DocCfg(id='023452', note=HARVARD_POETRY),
    DocCfg(id='029517', note=HARVARD_POETRY),
    DocCfg(id='029543', note=HARVARD_POETRY),
    DocCfg(id='029589', note=HARVARD_POETRY),
    DocCfg(id='029603', note=HARVARD_POETRY),
    DocCfg(id='029298', note=HARVARD_POETRY),
    DocCfg(id='029592', note=HARVARD_POETRY),
    DocCfg(id='019396', note=f'{HARVARD} Economics 1545 Professor Kenneth Rogoff syllabus'),
    DocCfg(id='022445', note=f"Inference: International Review of Science Feedback & Comments", date='2018-11-01'),
    DocCfg(
        id='029355',
        note=f'{SCREENSHOT} quote in book about {LARRY_SUMMERS}',
        dupe_type='quoted',
        duplicate_ids=['029356'],  # 029356 is zoomed in corner
        is_interesting=False,
    ),

    # DOJ Files
    DocCfg(
        id='EFTA01103509',
        author=BEN_GOERTZEL,
        date='2013-02-01',
        note='"Creating Robots with Toddler-Level Intelligence Using the OpenCog AGI Architecture" proposal for Epstein Foundation',
    ),
    DocCfg(
        id='EFTA01106148',
        author=GINO_YU,
        date='2011-05-01',
        note='OpenCog Hong Kong Project Interim Report',
    ),
    imessage_screenshot('EFTA01616545', author=DEEPAK_CHOPRA, date='2016-10-09T22:01:25'),
    DocCfg(id='EFTA01114164', author=BEN_GOERTZEL, note='OpenCog Road Map 2011-2023', date='2011-01-01', date_uncertain=True),
    DocCfg(id='EFTA01114145', author=f"{BEN_GOERTZEL}, {GINO_YU}", note="OpenCog AGI Toddler Project", date='2011-06-01', date_uncertain=True),
    EmailCfg(id='EFTA00954900', note=f'Epstein donation to {MOUNT_SINAI}'),
    EmailCfg(id='EFTA00955864', note=f'Epstein donation to {MOUNT_SINAI}', is_interesting=False),
    EmailCfg(id='EFTA02257779', author=LESLEY_GROFF, recipients=['Lisa']),
    EmailCfg(id='EFTA00763822', note=f"{LAWRENCE_KRAUSS} proposal for Epstein image rehabilitation", truncate_to=(1_750, 5_500)),
    imessage_screenshot('EFTA01616222', author=HARRY_FISCH, date='2018-04-23T14:25:30'),
    imessage_screenshot('EFTA01616232', author=HARRY_FISCH, date='2018-04-23T14:25:30'),
    skype_log('032206', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    skype_log('032208', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    skype_log('032209', recipients=[LAWRENCE_KRAUSS], is_interesting=False),
    # Medical
    EmailCfg(id='EFTA01767129', note=f"Epstein paying for {YONI_KOREN}'s medical treatment, routed through {LEON_BLACK}"),
    EmailCfg(id='EFTA01198246', highlight_quote=f"Got a fresh shipment", is_interesting=3),
]
