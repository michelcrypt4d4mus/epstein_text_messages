from epstein_files.documents.config.config_builder import fedex_invoice, important_messages_pad, press_release
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.communication_cfg import imessage_screenshot, skype_log
from epstein_files.documents.documents.categories import Interesting, Neutral
from epstein_files.documents.doj_files.full_text import EFTA00009622_TEXT
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

LUTNICKS_CANTOR = f"Howard Lutnick's {CANTOR_FITZGERALD}"


MISC_CFGS = [
    press_release('015462', 'Nautilus Education', note=f'magazine issue for Epstein foundation {QUESTION_MARKS}', is_interesting=True),
    press_release('029326', EPSTEIN_VI_FOUNDATION, '2013-02-15'),
    press_release('026565', EPSTEIN_VI_FOUNDATION, '2013-02-15', comment=f'maybe a draft of 029326'),
    DocCfg(id='022494', author='DOJ', note=f'Foreign Corrupt Practices Act (FCPA) Resource Guide'),
    DocCfg(id='023096', author=EPSTEIN_VI_FOUNDATION, note=f'blog post', date='2012-11-15'),
    DocCfg(id='027071', author=FEMALE_HEALTH_COMPANY, note=f"brochure requesting donations for female condoms in Uganda"),
    DocCfg(id='027074', author=FEMALE_HEALTH_COMPANY, note=f"pitch deck (USAID was a customer)"),
    DocCfg(id='032735', author=GORDON_GETTY, note=f"on Trump", date='2018-03-20'),  # Dated based on concurrent emails from Getty
    DocCfg(id='025540', author=JEFFREY_EPSTEIN, note=f"rough draft of his side of the story"),
    DocCfg(id='026634', author='Michael Carrier', note=f'comments about an Apollo linked fund "DE Fund VIII"'),
    DocCfg(id='031425', author=SCOTT_J_LINK, note=f'completely redacted email', is_interesting=False),
    DocCfg(id='020447', author='Working Group on Chinese Influence Activities in the US', note=f'Promoting Constructive Vigilance'),
    DocCfg(id='012718', note=f"{CVRA} congressional record", date='2011-06-17'),
    DocCfg(id='019448', note=f"Haitian business investment proposal called Jacmel", attached_to_email_id='019446'),
    DocCfg(id='023644', note=f"interview with Mohammed bin Salman", date='2016-04-25', is_interesting=False),
    DocCfg(
        id='030142',
        author=f"{KATHRYN_RUEMMLER}, {KEN_STARR}",
        date='2016-09-01',
        note=f"mostly empty {JASTA} (Justice Against Sponsors of Terrorism Act) doc referencing suit against Saudis",
    ),
    DocCfg(id='029328', note=f"Rafanelli Events promotional deck", is_interesting=False),
    DocCfg(id='029475', note=f'{VIRGIN_ISLANDS} Twin City Mobile Integrated Health Services (TCMIH) proposal/request for donation', is_interesting=False),
    DocCfg(id='029448', note=f"weird short essay titled 'President Obama and Self-Deception'"),
    press_release(
        '033338',
        NICHOLAS_RIBIS,
        '2000-06-07',
        f"end of {DONALD_TRUMP} & {NICHOLAS_RIBIS} working relationship at Trump's casino",
        is_interesting=True,
    ),

    # DOJ files
    DocCfg(id='EFTA01611898', note=f"screenshot of recent contacts in an iPhone"),
    DocCfg(
        id='EFTA00034357',
        author=BUREAU_OF_PRISONS,
        date='2019-08-10',
        note=f"internal message about discovery of Epstein's body",
        background_color='red'
    ),
    DocCfg(
        id='EFTA01063811',
        date='2014-08-07',
        date_uncertain=True,
        note="1201-1300 of 4,285 Apple Address Book entries from one of Epstein's accounts",
        is_interesting=True,
    ),
    DocCfg(id='EFTA01103465', author=BEN_GOERTZEL, date='2013-12-02', note='funding proposal for AI labs in Africa etc.'),
    DocCfg(id='EFTA00007585', note='various fedex receipts and realtor notes', date='2005-09-20'),
    DocCfg(id='EFTA01193705', note="list of Epstein's known email addresses, internet accounts, cars, boats, airplanes, and telephone numbers"),
    DocCfg(id='EFTA00165515', note="contractor describes Epstein's gun safes", show_full_panel=True),
    DocCfg(id='EFTA00266322', note=f"documents about pitches for non-profits in Australia, including to Effective Altruism"),
    DocCfg(
        id='EFTA00029538',
        note=f"{GHISLAINE_MAXWELL} investigation",
        highlight_quote="the defendant provided Minor Victim-3 with a schoolgirl uniform",
    ),
    DocCfg(id='EFTA00005783', note='heavily redacted handwritten note, 30+ completely redacted pages', date='2019-08-29'),
    DocCfg(id='EFTA00005386', note='heavily redacted photo album, lot of photos of girls'),
    DocCfg(id='EFTA01063691', note='inventory of address books and Skype logs seized from Epstein computers'),
    DocCfg(id='EFTA00024275', note='large Wexner funded payments to OB-GYN'),
    DocCfg(id='EFTA00728783', note='list of names and phone numbers'),
    DocCfg(id='EFTA00298379', note='RSVP list for Yom Kippur dinner', date='2010-09-18'),
    # Urramoor
    DocCfg(
        id='EFTA01107738',
        note=f"creation of {CANTOR_URRAMOOR} with Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA01141453',
        note=f"referral agreement between Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=True,
    ),
    # Replacement text
    DocCfg(
        id='EFTA00009622',
        date='2006-07-19',
        note='handwritten notes from a victim interview transcribed by Claude AI',
        is_interesting=True,
        display_text=EFTA00009622_TEXT,
    ),
    DocCfg(
        id='EFTA00004477',
        is_interesting=True,
        display_text='Epstein 50th birthday photo book 12 "THAIS, MOSCOW GIRLS, AFRICA, HAWAII, [REDACTED] [REDACTED], Zorro, [REDACTED] [REDACTED] [REDACTED], CRACK WHOLE PROPOSAL, BALI/THAILAND/ASIA, RUSSIA, [REDACTED], [REDACTED], NUDES, YOGAL GIRLS',
    ),
    DocCfg(id='EFTA01628970', display_text='redacted pictures of naked women'),
    DocCfg(id='EFTA00004070', display_text="photos of Epstein with handwritten caption that didn't OCR well"),
    DocCfg(id='EFTA02731260', display_text='notebook full of handwritten love letters with terrible OCR text'),
    DocCfg(id='EFTA00006100', display_text='Palm Beach Police fax machine activity log 2005-12-28 to 2006-01-04'),
    DocCfg(
        id='EFTA00003149',
        date='2016-01-01',
        date_uncertain='complete guess',
        note=f"{LITTLE_SAINT_JAMES} staff list",
        show_full_panel=True,
    ),
    # Attachments
    DocCfg(id='EFTA00590685', attached_to_email_id='EFTA00830911'),
    # Dates
    DocCfg(id='EFTA02025218', date='2011-09-09'),
    DocCfg(id='EFTA00007693', note="driving directions from Epstein's house to <REDACTED>, flight details for Sandy Berger"),
    # Misc
    fedex_invoice('EFTA00217072', '2005-06-20'),
    fedex_invoice('EFTA00217080', '2005-06-27'),
    imessage_screenshot(id='033434', author=BRAD_EDWARDS, author_uncertain=f"labeled 'Edwards'", is_interesting=False),
    important_messages_pad('EFTA01719859', '2005-10-03'),
    important_messages_pad('EFTA01682477', '2005-04-01'),
    skype_log('032210', recipients=['linkspirit'], is_interesting=True),
    skype_log('018224', recipients=['linkspirit', LAWRENCE_KRAUSS], is_interesting=True),  # we don't know who linkspirit is yet
    skype_log('EFTA01617727'),
    skype_log(
        id='EFTA00507334',
        recipients=[
            'Aleksandra Eriksson',
            ANASTASIYA_SIROOCHENKO,
            'Catherine',
            DANIEL_SIAD,
            DAVID_STERN,
            EMAD_HANNA,
            'Jade Huang',
            NADIA_MARCINKO,
            'sexysearch2010',
            'sophiembh'
        ],
    ),
    skype_log('EFTA01613143', author=MELANIE_WALKER, date='2017-06-24'),
]
