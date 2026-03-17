from epstein_files.documents.config.categories.girls import PRUSAKOVA_BERKELY
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

DERSH_GIUFFRE_TWEET = f"about {VIRGINIA_GIUFFRE}"


SOCIAL_CFGS = [
    DocCfg(id='028815', author=INSIGHTS_POD, note=f"business plan", date='2016-08-20', attached_to_email_id='033171'),
    DocCfg(id='011170', author=INSIGHTS_POD, note=f'case study of social media vibe analysis using tweets from #Brexit', date='2016-06-23', attached_to_email_id='033171'),
    DocCfg(id='032324', author=INSIGHTS_POD, note=f"social media election sentiment analysis", date='2016-11-05', attached_to_email_id='032323'),
    DocCfg(id='032281', author=INSIGHTS_POD, note=f"social media election sentiment report", date='2016-10-25', attached_to_email_id='032280'),
    DocCfg(id='028988', author=INSIGHTS_POD, note=f"pitch deck", date='2016-08-20', attached_to_email_id='033171'),
    DocCfg(id='026627', author=INSIGHTS_POD, note=f"report on impact of presidential debate", attached_to_email_id='026626'),
    DocCfg(id='022213', note=f"{SCREENSHOT} Facebook group called 'Shit Pilots Say' disparaging a 'global girl'", is_interesting=False),
    EmailCfg(id='033171', is_interesting=True, comment='Zubair'),
    EmailCfg(
        id='030630',
        author=MARIA_PRUSAKOVA,
        author_reason=PRUSAKOVA_BERKELY,
        note=f'Masha Prusso / {MARIA_PRUSAKOVA} asks about Zubair Khan and {INSIGHTS_POD}',
        is_interesting=True,
    ),
    EmailCfg(
        id='032319',
        note=f"{ZUBAIR_KHAN} says social media vibes are good for Trump in last week before the 2016 election",
        dupe_type='quoted',
        duplicate_ids=['032283'],
        is_interesting=True,
    ),
    EmailCfg(
        id='032325',
        note=f"{ZUBAIR_KHAN} predicts Trump winning in 2016",
        dupe_type='quoted',
        duplicate_ids=['026014'],
        is_interesting=True,
    ),
    EmailCfg(
        id='EFTA00719854',
        note=f'{BORIS_NIKOLIC} introduces Epstein to Chris Poole AKA "moot", the founder of 4chan',
        is_interesting=True,
        show_with_name=CHRIS_POOLE
    ),
    EmailCfg(
        id='EFTA00922824',
        note=f"Epstein meets with {CHRIS_POOLE} (founder of 4chan) the day the infamous /pol/ board is created",
        is_interesting=True,
        show_with_name=CHRIS_POOLE,
    ),
]


TWEET_CFGS = [
    DocCfg(id='023050', author=ALAN_DERSHOWITZ, note=DERSH_GIUFFRE_TWEET),
    DocCfg(id='017787', author=ALAN_DERSHOWITZ, note=DERSH_GIUFFRE_TWEET),
    DocCfg(id='033433', author=ALAN_DERSHOWITZ, note=f"{DERSH_GIUFFRE_TWEET} / David Boies", date='2019-03-02'),
    DocCfg(id='033432', author=ALAN_DERSHOWITZ, note=f"{DERSH_GIUFFRE_TWEET} / David Boies", date='2019-05-02'),
    DocCfg(id='031546', author=DONALD_TRUMP, note=f"about Russian collusion", date='2018-01-06'),
    DocCfg(id='030884', author='Ed Krassenstein'),
    DocCfg(id='033236', note=f'selection about Ivanka Trump in Arabic', date='2017-05-20'),
]
