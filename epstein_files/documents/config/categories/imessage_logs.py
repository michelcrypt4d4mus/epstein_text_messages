"""
Custom configurations for iMessage logs.
"""
from epstein_files.documents.documents.categories import Interesting
from epstein_files.documents.config.communication_cfg import TextCfg
from epstein_files.people.names import *
from epstein_files.util.constant.strings import AUTO

PARTICIPANTS_FIELD = 'Participants: field'


################################################################################################
############################################ TEXTS #############################################
################################################################################################

CONFIRMED_TEXTS_CONFIG = [
    TextCfg(id='031042', author=ANIL_AMBANI, author_reason=PARTICIPANTS_FIELD),
    TextCfg(id='027225', author=ANIL_AMBANI, author_reason="birthday mentioned in texts is confirmed as Ambani's"),
    TextCfg(id='031054', author=ANTHONY_SCARAMUCCI, author_reason="Scaramucci's phone number is at top of raw file"),
    TextCfg(id='027333', author=ANTHONY_SCARAMUCCI, author_reason="Scaramucci's phone number is in one of the messages"),
    TextCfg(id='031173', author=ARDA_BESKARDES, author_reason=PARTICIPANTS_FIELD),
    TextCfg(id='027401', author=EVA_DUBIN, author_uncertain=PARTICIPANTS_FIELD),
    TextCfg(id='027650', author=JOI_ITO, author_reason=PARTICIPANTS_FIELD),
    TextCfg(id='027777', author=LARRY_SUMMERS, author_reason=PARTICIPANTS_FIELD),
    TextCfg(id='027515', author=MIROSLAV_LAJCAK, author_reason='https://x.com/ImDrinknWyn/status/1990210266114789713'),
    TextCfg(
        id='027165',
        author=MELANIE_WALKER,
        author_reason='says "it\'s Melanie", also https://www.wired.com/story/jeffrey-epstein-claimed-intimate-knowledge-of-donald-trumps-views-in-texts-with-bill-gates-adviser/',
        category=Interesting.CRYPTO,
        comment='crypto health'
    ),
    TextCfg(id='027248', author=MELANIE_WALKER, author_reason='says "we met through Trump" which is confirmed by Melanie in 032803'),
    TextCfg(id='025429', author=STACEY_PLASKETT, author_reason='widely reported'),
    TextCfg(id='027128', author=SOON_YI_PREVIN, author_reason='https://x.com/ImDrinknWyn/status/1990227281101434923'),
    TextCfg(id='027217', author=SOON_YI_PREVIN, author_reason='refs marriage to Woody Allen'),
    TextCfg(id='027244', author=SOON_YI_PREVIN, author_reason='refs Woody Allen'),
    TextCfg(id='027257', author=SOON_YI_PREVIN, author_reason=f"Woody Allen in {PARTICIPANTS_FIELD}"),
    TextCfg(
        id='027460',
        author=STEVE_BANNON,
        author_reason='Discusses leaving scotland when Bannon was confirmed in Scotland, also NYT',
        is_interesting=6,
        comment='bannon and jabor',
        duplicate_ids=['EFTA01615422'],
    ),
    TextCfg(id='027307', author=STEVE_BANNON, author_reason='texts mention "Epstein Bannon Kurz"'),
    TextCfg(id='027278', author=TERJE_ROD_LARSEN, author_reason=PARTICIPANTS_FIELD, is_interesting=True),
    TextCfg(id='027255', author=TERJE_ROD_LARSEN, author_reason=PARTICIPANTS_FIELD),
]

UNCONFIRMED_TEXTS_CONFIG = [
    TextCfg(id='027762', author=ANDRZEJ_DUDA, author_uncertain=f"Duda in NY at that time, took train"),
    TextCfg(id='027774', author=ANDRZEJ_DUDA, author_uncertain=f"Duda in NY at that time, took train"),
    TextCfg(id='027221', author=ANIL_AMBANI),
    TextCfg(id='027396', author=ANTHONY_SCARAMUCCI, author_uncertain='says "I need to make peace with Bannon"'),
    TextCfg(id='025436', author=CELINA_DUBIN),
    TextCfg(id='027576', author=MELANIE_WALKER, author_uncertain='https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.023700'),
    TextCfg(id='027141', author=MELANIE_WALKER),
    TextCfg(id='027232', author=MELANIE_WALKER),
    TextCfg(id='027133', author=MELANIE_WALKER),
    TextCfg(id='027184', author=MELANIE_WALKER),
    TextCfg(id='027214', author=MELANIE_WALKER),
    TextCfg(id='027148', author=MELANIE_WALKER),
    TextCfg(id='027440', author=MICHAEL_WOLFF, author_uncertain='AI says Trump book/journalism project'),
    TextCfg(id='027568', author=STEVE_BANNON),
    TextCfg(id='027695', author=STEVE_BANNON, note='"kazak daughter the key" may be about Dariga Nazarbayeva (low confidence)'),
    TextCfg(id='027594', author=STEVE_BANNON),
    TextCfg(id='027549', author=STEVE_BANNON),
    TextCfg(id='027764', author=STEVE_BANNON, note=f"includes discussion of Facebook's attempt at crypto called Libra", is_interesting=True),
    TextCfg(id='027585', author=STEVE_BANNON, author_uncertain='references Tokyo trip', duplicate_ids=['EFTA01615642'], dupe_type='screenshot'),  # TODO: something with screenshots
    TextCfg(id='027434', author=STEVE_BANNON, author_uncertain='references Maher appearance'),
    TextCfg(id='027428', author=STEVE_BANNON, author_uncertain='references HBJ meeting on 9/28 from other Bannon/Epstein convo'),
    TextCfg(id='027374', author=STEVE_BANNON, author_uncertain='AI says China strategy and geopolitics'),
    TextCfg(id='027455', author=STEVE_BANNON, author_uncertain='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='027536', author=STEVE_BANNON, author_uncertain='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='025479', author=STEVE_BANNON, author_uncertain='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='025734', author=STEVE_BANNON, author_uncertain='AI says China strategy and geopolitics; Trump discussions'),
    TextCfg(id='027707', author=STEVE_BANNON, author_uncertain='AI says Italian politics; Trump discussions'),
    TextCfg(id='025400', author=STEVE_BANNON, author_uncertain='AI says Trump NYT article criticism; Hannity media strategy'),
    TextCfg(id='025408', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='025452', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='027281', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='027346', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='027365', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage', duplicate_ids=['EFTA01615218']),
    TextCfg(id='027406', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='027655', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='027722', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage', duplicate_ids=['027720']),
    TextCfg(id='027735', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage', note=f"Bannon just returned from Kazakhstan"),
    TextCfg(id='027794', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='025368', author=STEVE_BANNON, author_uncertain='AI', is_interesting=True, comment='obama slander'),
    TextCfg(id='025707', author=STEVE_BANNON, author_uncertain='AI', is_interesting=True, comment='mentions thiel, dubai'),
    TextCfg(id='025363', author=STEVE_BANNON, author_uncertain='AI', is_interesting=True, comment='mooch discussion'),
    TextCfg(id='027445', author=STEVE_BANNON, author_uncertain='AI', is_interesting=True),
    TextCfg(id='027260', author=STEVE_BANNON, author_uncertain='AI', is_interesting=True),
    TextCfg(
        id='029744',
        author=STEVE_BANNON,
        author_uncertain='AI says Trump + NYT coverage',
        note='contains discussion of Chinese criminal Miles Guo AKA Miles Kwok',
        entity_names=[MILES_GUO],
        is_interesting=10,
    ),
    TextCfg(id='031045', author=STEVE_BANNON, author_uncertain='AI says Trump and New York Times coverage'),
    TextCfg(id='027275', is_interesting=True, comment='"Crypto- Kerry- Qatar -sessions"'),
    TextCfg(id='027792', duplicate_ids=['027694'], dupe_type='quoted'),

    # DOJ PDFs
    TextCfg(
        id='EFTA00786793',
        author_reason='/Users/jee/Library/Messages/Archive/2018-07-04/Karina',
        note=f"Eptein and {SOON_YI_PREVIN} talk shit about {ALAN_DERSHOWITZ}, {EVA_DUBIN} asks for medical advice",
        recipients=[KARYNA_SHULIAK, STEVE_BANNON, TERJE_ROD_LARSEN, WOODY_ALLEN, None],
    ),
    TextCfg(
        id='EFTA01209934',
        recipients=[ANIL_AMBANI, WOODY_ALLEN, None],
    ),
    TextCfg(
        id='EFTA00508054',
        note=f'Multiple counterparties, at least some Bannon. Epstein brings up the suicide of {RUSLANA_KORSHUNOVA} whom he "knew very well".'
    ),
    TextCfg(
        id='EFTA00509584',
        note='multiple counterparties',
        highlight_quote="each girl knew why she was coming to the house massage with extra , hardly coercion",
        truncate_to=AUTO,
    ),
    TextCfg(id='EFTA01619635', author=DEEPAK_CHOPRA, date='2019-01-27'),
    TextCfg(id='EFTA01612358', author='Dan Nardello', date='2019-06-02'),
]

# Necessary because some of these will be marked uninteresting, which overrides the config
UNKNOWN_TXT_MSG_LOGS = [
    TextCfg(id='025423'),
    TextCfg(id='025426'),
    TextCfg(id='027583'),
]

for cfg in UNCONFIRMED_TEXTS_CONFIG:
    cfg.author_uncertain = cfg.author_uncertain or True

TEXTS_CONFIG = CONFIRMED_TEXTS_CONFIG + UNCONFIRMED_TEXTS_CONFIG + UNKNOWN_TXT_MSG_LOGS
