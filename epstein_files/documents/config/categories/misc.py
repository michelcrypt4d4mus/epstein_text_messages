from epstein_files.documents.config.config_builder import fedex_invoice, important_messages_pad
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.documents.categories import Interesting, Neutral
from epstein_files.documents.doj_files.full_text import EFTA00009622_TEXT
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

FEMALE_HEALTH_COMPANY = 'Female Health Company (FHC)'
LUTNICKS_CANTOR = f"Howard Lutnick's {CANTOR_FITZGERALD}"


MISC_CFGS = [
    DocCfg(id='029326', category=Neutral.PRESSER, author=EPSTEIN_FOUNDATION, date='2013-02-15'),
    DocCfg(id='026565', category=Neutral.PRESSER, author=EPSTEIN_FOUNDATION, comment=f'maybe a draft of 029326', date='2013-02-15'),
    DocCfg(id='022494', author='DOJ', description=f'Foreign Corrupt Practices Act (FCPA) Resource Guide'),
    DocCfg(id='023096', author=EPSTEIN_FOUNDATION, description=f'blog post', date='2012-11-15'),
    DocCfg(id='027071', author=FEMALE_HEALTH_COMPANY, description=f"brochure requesting donations for female condoms in Uganda"),
    DocCfg(id='027074', author=FEMALE_HEALTH_COMPANY, description=f"pitch deck (USAID was a customer)"),
    DocCfg(id='032735', author=GORDON_GETTY, description=f"on Trump", date='2018-03-20'),  # Dated based on concurrent emails from Getty
    DocCfg(id='025540', author=JEFFREY_EPSTEIN, description=f"rough draft of his side of the story"),
    DocCfg(id='026634', author='Michael Carrier', description=f'comments about an Apollo linked fund "DE Fund VIII"'),
    DocCfg(id='031425', author=SCOTT_J_LINK, description=f'completely redacted email', is_interesting=False),
    DocCfg(id='020447', author='Working Group on Chinese Influence Activities in the US', description=f'Promoting Constructive Vigilance'),
    DocCfg(id='012718', description=f"{CVRA} congressional record", date='2011-06-17'),
    DocCfg(id='019448', description=f"Haitian business investment proposal called Jacmel", attached_to_email_id='019446'),
    DocCfg(id='023644', description=f"interview with Mohammed bin Salman", date='2016-04-25', is_interesting=False),
    DocCfg(
        id='030142',
        author=f"{KATHRYN_RUEMMLER} & {KEN_STARR}",
        date='2016-09-01',
        description=f"mostly empty {JASTA} (Justice Against Sponsors of Terrorism Act) doc referencing suit against Saudis",
    ),
    DocCfg(
        id='033338',
        category=Neutral.PRESSER,
        date='2000-06-07',
        description=f"end of {DONALD_TRUMP} & {NICHOLAS_RIBIS} working relationship at Trump's casino",
        is_interesting=True,
    ),
    DocCfg(id='029328', description=f"Rafanelli Events promotional deck", is_interesting=False),
    DocCfg(id='029475', description=f'{VIRGIN_ISLANDS} Twin City Mobile Integrated Health Services (TCMIH) proposal/request for donation', is_interesting=False),
    DocCfg(id='029448', description=f"weird short essay titled 'President Obama and Self-Deception'"),

    # DOJ files
    DocCfg(
        id='EFTA00034357',
        author=BUREAU_OF_PRISONS,
        date='2019-08-10',
        description=f"internal message about discovery of Epstein's body",
        background_color='red'
    ),
    DocCfg(
        id='EFTA01063811',
        date='2014-08-07',
        date_uncertain=True,
        description="1201-1300 of 4,285 Apple Address Book entries from one of Epstein's accounts",
        is_interesting=True,
    ),
    DocCfg(id='EFTA01103465', author=BEN_GOERTZEL, date='2013-12-02', description='funding proposal for AI labs in Africa etc.'),
    DocCfg(id='EFTA01193705', description="list of Epstein's known email addresses, internet accounts, cars, boats, airplanes, and telephone numbers"),
    DocCfg(id='EFTA00165515', description="contractor describes Epstein's gun safes", show_full_panel=True),
    DocCfg(id='EFTA00266322', description=f"documents about pitches for non-profits in Australia, including to Effective Altruism"),
    DocCfg(
        id='EFTA00029538',
        description=f"{GHISLAINE_MAXWELL} investigation",
        highlight_quote="the defendant provided Minor Victim-3 with a schoolgirl uniform",
    ),
    DocCfg(id='EFTA00005783', description='heavily redacted handwritten note, 30+ completely redacted pages', date='2019-08-29'),
    DocCfg(id='EFTA00005386', description='heavily redacted photo album, lot of photos of girls'),
    DocCfg(id='EFTA01063691', description='inventory of address books and Skype logs seized from Epstein computers'),
    DocCfg(id='EFTA00024275', description='large Wexner funded payments to OB-GYN'),
    DocCfg(id='EFTA00728783', description='list of names and phone numbers'),
    DocCfg(id='EFTA00298379', description='RSVP list for Yom Kippur dinner', date='2010-09-18'),
    # Urramoor
    DocCfg(
        id='EFTA01107738',
        description=f"creation of {CANTOR_URRAMOOR} with Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=True,
    ),
    DocCfg(
        id='EFTA01141453',
        description=f"referral agreement between Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=True,
    ),
    # Replacement text
    DocCfg(
        id='EFTA00009622',
        date='2006-07-19',
        description='handwritten notes from a victim interview transcribed by Claude AI',
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
        description=f"{LITTLE_SAINT_JAMES} staff list",
        show_full_panel=True,
    ),
    # Attachments
    DocCfg(id='EFTA00590685', attached_to_email_id='EFTA00830911'),
    # Dates
    DocCfg(id='EFTA02025218', date='2011-09-09'),
    # FedEx
    fedex_invoice('EFTA00217072', '2005-06-20'),
    fedex_invoice('EFTA00217080', '2005-06-27'),
    # Message pads
    important_messages_pad('EFTA01719859', '2005-10-03'),
    important_messages_pad('EFTA01682477', '2005-04-01'),
]
