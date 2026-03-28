from epstein_files.documents.config.config_builder import fedex_invoice, important_messages_pad, inventory, letter, memo, press_release
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.communication_cfg import imessage_screenshot, skype_log
from epstein_files.documents.documents.categories import Interesting, Neutral
from epstein_files.output.site.sites import Site
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import JMAIL_JCAL_URL

LUTNICKS_CANTOR = f"Howard Lutnick's {CANTOR_FITZGERALD}"


def daily_schedule(id: str, date: str, **kwargs) -> DocCfg:
    return DocCfg(id=id, date=date, note='daily schedule', url=JMAIL_JCAL_URL, **kwargs)


MISC_CFGS = [
    letter(
        id='026011',
        author='Gennady Mashtalyar',
        date='2016-06-24',  # date is based on Brexit reference but he could be backtesting,
        note=f"about algorithmic trading",
    ),
    memo('EFTA00577389', JEFFREY_EPSTEIN, 'reporting responsibilities', '2004-07-26'),
    press_release('015462', 'Nautilus Education', note=f'magazine issue for Epstein foundation {QUESTION_MARKS}', is_interesting=True),
    press_release('029326', EPSTEIN_VI_FOUNDATION, '2013-02-15'),
    press_release('026565', EPSTEIN_VI_FOUNDATION, '2013-02-15', comment=f'maybe a draft of 029326'),
    DocCfg(id='022494', author='DOJ', note=f'Foreign Corrupt Practices Act (FCPA) Resource Guide'),
    DocCfg(id='EFTA00616025', author='Alberto Pinto Cabinet', note='furniture inventory', truncate_to=900),
    DocCfg(id='023096', author=EPSTEIN_VI_FOUNDATION, note=f'blog post', date='2012-11-15'),
    DocCfg(id='027071', author=FEMALE_HEALTH_COMPANY, note=f"brochure requesting donations for female condoms in Uganda"),
    DocCfg(id='027074', author=FEMALE_HEALTH_COMPANY, note=f"pitch deck (USAID was a customer)"),
    DocCfg(id='032735', author=GORDON_GETTY, note=f"on Trump", date='2018-03-20'),  # Dated based on concurrent emails from Getty
    DocCfg(id='025540', author=JEFFREY_EPSTEIN, note=f"rough draft of his side of the story"),
    DocCfg(id='026634', author='Michael Carrier', note=f'comments about an Apollo linked fund "DE Fund VIII"'),
    DocCfg(id='031425', author=SCOTT_J_LINK, note=f'completely redacted email', is_interesting=False),
    DocCfg(id='020447', author='Working Group on Chinese Influence Activities in the US', note=f'Promoting Constructive Vigilance'),
    DocCfg(id='EFTA00298515', date='2010-09-10', note=f"guest list for a get together with {EHUD_BARAK}", show_full_panel=True),
    DocCfg(id='EFTA00587235', note="Epstein's website", date='2012-11-14'),
    DocCfg(id='EFTA00432804', note='recorded conversation of Epstein', highlight_quote="Katie Couric, I thought, was going to start to vomit", truncate_to=AUTO, is_interesting=True),
    DocCfg(id='EFTA00582807', note=f"plans for a media empire involved buying {VI_DAILY_NEWS} which had criticized Epstein", is_interesting=5, truncate_to=(2_500, 5_000)),
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
    press_release('EFTA00613875', f"Virgin Islands Legislature", '2014-06-16'),

    # DOJ files
    DocCfg(
        id='EFTA00003149',
        date='2016-01-01',
        date_uncertain='complete guess',
        note=f"{LITTLE_SAINT_JAMES} staff list",
        show_full_panel=True,
    ),
    DocCfg(
        id='EFTA01063811',
        date='2014-08-07',
        date_uncertain=True,
        note="1201-1300 of 4,285 Apple Address Book entries from one of Epstein's accounts",
        is_interesting=True,
    ),
    DocCfg(id='EFTA01103465', author=BEN_GOERTZEL, date='2013-12-02', note='funding proposal for AI labs in Africa etc.'),
    DocCfg(id='EFTA00006085', author='Broward Center for the Performing Arts', display_text='Front of House Managers Report including ticket sales'),
    DocCfg(
        id='EFTA00029538',
        note=f"{GHISLAINE_MAXWELL} investigation",
        highlight_quote="the defendant provided Minor Victim-3 with a schoolgirl uniform",
    ),
    DocCfg(
        id='EFTA01242527',
        display_text='3,000 pages of Epstein phone logs, call to Scott Shay at Hyperion Partners, see link for call counts',
        is_interesting=True,
        is_valid_for_name_scan=False,
        url=Site.get_url(Site.PHONE_NUMBERS),
    ),
    DocCfg(
        id='EFTA00522943',
        date='2006-07-27',
        date_uncertain='using date of Epstein arrest',
        is_interesting=10,
        note=f"Epstein's medicine cabinet includes fertility drugs, two kinds of benzos (like Xanax), low level opioids, ED drugs, stimulants, and syringes",
        show_full_panel=True,
        truncate_to=(1_220, 2_400),
    ),
    DocCfg(id='EFTA00579398', date='2003-11-26'),
    DocCfg(id='EFTA00416586', date='2012-03-29'),
    DocCfg(id='EFTA00314072', author='Darius Paduch', note=f"confirms he was Epstein's doctor", is_interesting=6, date='2018-09-26'),
    DocCfg(
        id='EFTA00586992',
        author=NEWGRANGE_CONSULTING,
        note='contract with Island Global Yachting',
        date='2010-08-01',
        date_uncertain='August',
        truncate_to=1_600,
    ),
    DocCfg(id='EFTA00309068', note='personal cell phone and email address list', is_interesting=5),
    DocCfg(id='EFTA00221072', note=f"Operation Leap Year contact list", is_interesting=True),
    DocCfg(id='EFTA00315184', note="pre-printed welcome cards for Epstein's apartments"),
    DocCfg(id='EFTA00313981', note='architectural plans for chateau on Great St. James island'),
    DocCfg(id='EFTA00285041', note='birthday book list', date='2015-11-15', show_full_panel=True, truncate_to=1_600),
    DocCfg(id='EFTA00000019', note=f"{MERWIN_DELA_CRUZ} cooling tower maintenance", date='2018-12-10', is_interesting=False),
    DocCfg(id='EFTA00008486', note=f"chain of custody evidence envelope", date='2009-11-02'),
    DocCfg(id='EFTA00006378', note=f"message pad with {LES_WEXNER}'s name", date='2003-03-14'),
    DocCfg(id='EFTA00165515', note="contractor describes Epstein's gun safes", show_full_panel=True),
    DocCfg(id='EFTA00266322', note=f"documents about pitches for non-profits in Australia, including to Effective Altruism"),
    DocCfg(id='EFTA00005783', note='heavily redacted handwritten note, 30+ completely redacted pages', date='2019-08-29'),
    DocCfg(id='EFTA02697975', note='island employee list', show_full_panel=True, is_interesting=2),
    DocCfg(id='EFTA00024275', note='large Wexner funded payments to OB-GYN'),
    DocCfg(id='EFTA01193705', note="list of Epstein's known email addresses, internet accounts, cars, boats, airplanes, and telephone numbers"),
    DocCfg(id='EFTA00728783', note='list of names and phone numbers'),
    DocCfg(id='EFTA00298379', note='RSVP list for Yom Kippur dinner', date='2010-09-18'),
    DocCfg(id='EFTA01611898', note=f"screenshot of recent contacts in an iPhone"),
    DocCfg(id='EFTA00007585', note='various fedex receipts and realtor notes', date='2005-09-20'),
    DocCfg(id='EFTA00191467', display_text=f"Epstein's black book with contacts", is_interesting=10, date='2015-06-01', date_uncertain='leaked some time 2015'),
    daily_schedule('EFTA00314248', '2010-04-07'),
    daily_schedule('EFTA00304809', '2011-01-05', date_uncertain=True),
    daily_schedule('EFTA00308123', '2012-11-08'),
    daily_schedule('EFTA00301520', '2013-01-26'),
    daily_schedule('EFTA00284890', '2014-01-01'),
    daily_schedule('EFTA00293621', '2016-03-01'),
    daily_schedule('EFTA00285309', '2017-04-01'),
    daily_schedule('EFTA00285408', '2017-10-01'),
    daily_schedule('EFTA00285597', '2018-09-01'),
    daily_schedule('EFTA00285783', '2019-03-01'),
    inventory('EFTA01063691', 'address books and Skype logs seized from Epstein computers'),
    # Urramoor
    DocCfg(
        id='EFTA01107738',
        note=f"creation of {CANTOR_URRAMOOR} with Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=10,
    ),
    DocCfg(
        id='EFTA01141453',
        note=f"referral agreement between Mr. T's (Prince Andrew?) Urramoor and {LUTNICKS_CANTOR}",
        is_interesting=10,
    ),
    # Replacement text
    DocCfg(
        id='EFTA00004477',
        is_interesting=True,
        display_text='Epstein 50th birthday photo book 12 "THAIS, MOSCOW GIRLS, AFRICA, HAWAII, [REDACTED] [REDACTED], Zorro, [REDACTED] [REDACTED] [REDACTED], CRACK WHOLE PROPOSAL, BALI/THAILAND/ASIA, RUSSIA, [REDACTED], [REDACTED], NUDES, YOGAL GIRLS',
    ),
    DocCfg(id='EFTA00001487', display_text="architectural drawing of one floor of Epstein's NYC residence"),
    DocCfg(id='EFTA00005386', display_text='heavily redacted photo album, lot of photos of girls'),
    DocCfg(id='EFTA01628970', display_text='redacted pictures of naked women'),
    DocCfg(id='EFTA00004070', display_text="photos of Epstein with handwritten caption that didn't OCR well"),
    DocCfg(id='EFTA02731260', display_text='notebook full of handwritten love letters with terrible OCR text', date='2012-07-16'),
    DocCfg(id='EFTA00006100', display_text='Palm Beach Police fax machine activity log 2005-12-28 to 2006-01-04'),
    # Attachments
    DocCfg(id='EFTA00590685', attached_to_email_id='EFTA00830911'),
    # Dates
    DocCfg(id='EFTA02025218', date='2011-09-09'),
    DocCfg(id='EFTA00007693', note="driving directions from Epstein's house to <REDACTED>, flight details for Sandy Berger"),

    # Misc
    DocCfg(
        id='EFTA00159394',
        note='notes from interview with employee and copy of 2005 household manual for Palm Beach residence',
        date='2021-09-30',
    ),
    DocCfg(id='EFTA00728864', note=f'security orders for {EL_BRILLO_ADDRESS} showing {IGOR_ZINOVIEV} had door power'),
    DocCfg(id='EFTA00305998', note='inventory and TODO list'),
    fedex_invoice('EFTA00219491', '2001-04-30'),
    fedex_invoice('EFTA00217257', '2001-12-31'),
    fedex_invoice('EFTA00082601', '2002-10-14'),
    fedex_invoice('EFTA00040687', '2002-10-14'),
    fedex_invoice('EFTA00218262', '2003-03-10'),
    fedex_invoice('EFTA00218394', '2003-04-21'),
    fedex_invoice('EFTA00218870', '2003-11-24'),
    fedex_invoice('EFTA00217072', '2005-06-20'),
    fedex_invoice('EFTA00217080', '2005-06-27'),
    imessage_screenshot(id='033434', author=BRAD_EDWARDS, author_uncertain=f"labeled 'Edwards'", is_interesting=False),
    important_messages_pad('EFTA01719859', '2005-10-03'),
    important_messages_pad('EFTA01682477', '2005-04-01'),
    letter('EFTA00090261', INTERLOCHEN_CENTER_FOR_THE_ARTS, [JEFFREY_EPSTEIN], "thanking him for donations", '1997-09-18'),
    letter('EFTA00007609', recipients=['Alberto Pinto'], duplicate_ids=['EFTA00007582']),
    skype_log('032210', recipients=['linkspirit'], is_interesting=True),
    skype_log('018224', recipients=['linkspirit', LAWRENCE_KRAUSS], is_interesting=True),  # we don't know who linkspirit is yet
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
    skype_log('EFTA01616004', recipients=[VALDAS_PETREIKIS]),
    skype_log('EFTA01617727'),
]
