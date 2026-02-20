"""
Constants used in the parsing and presentation of emails.
"""
import re

from dateutil.parser import parse

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import REDACTED

FALLBACK_TIMESTAMP = parse("1/1/2051 12:01:01 AM")
XML_STRIPPED_MSG = '<...removed Apple XML plist...>'

# Reply line regexes
FORWARDED_LINE_PATTERN = r"-+ ?(Forwarded|Original)\s*Message ?-*|Begin forwarded message:?"
FRENCH_REPLY_PATTERN = r"Le .* a ecrit:"
GERMAN_REPLY_PATTERN = r"Am \d\d\.\d\d\..*schrieb.*"
NORWEGAIN_REPLY_PATTERN = r"(Den .* folgende|(fre|lor|son)\. .* skrev .*):"
REPLY_LINE_IN_A_MSG_PATTERN = r"In a message dated \d+/\d+/\d+.*writes:"
REPLY_LINE_ENDING_PATTERN = r"[_ \n](AM|PM|[<_]|w?rote:?)"
REPLY_LINE_ON_NUMERIC_DATE_PATTERN = fr"(?<!M)On \d+[-/][\d\w]+[-/]\d+[, ].*{REPLY_LINE_ENDING_PATTERN}"
REPLY_LINE_ON_DATE_PATTERN = fr"On (\d+ )?((Mon|Tues?|Wed(nes)?|Thu(rs)?|Fri|Sat(ur)?|Sun)(day)?|(Ja.|Fe(b|vr\.)|Ma.|Ap.|Ma.|Ju.|Ju.|Au.|Se.|Oc.|No.|De.)\w*)[, ].*{REPLY_LINE_ENDING_PATTERN}"
REPLY_LINE_PATTERN = rf"^([>» •]*({FRENCH_REPLY_PATTERN}|{GERMAN_REPLY_PATTERN}|{NORWEGAIN_REPLY_PATTERN}|{REPLY_LINE_IN_A_MSG_PATTERN}|{REPLY_LINE_ON_NUMERIC_DATE_PATTERN}|{REPLY_LINE_ON_DATE_PATTERN}|{FORWARDED_LINE_PATTERN}))"
REPLY_REGEX = re.compile(REPLY_LINE_PATTERN, re.IGNORECASE | re.MULTILINE)

# Header fields
FIELD_PATTERNS = [
    'Date',
    'From',
    'Sent',
    'To',
    r"C[cC]",
    r"B[cC][cC]",
    'Importance',
    'Subject',
    'Attachments',
    'Attached',
    'Classification',
    'Flag',
    'Reply-To',
    'Inline-Images'
]

FIELDS_PATTERN = '|'.join(FIELD_PATTERNS)
FIELDS_COLON_PATTERN = fr"^({FIELDS_PATTERN}):"

# DojFile specific repairs must be applied before checking doc.is_email
DOJ_EMAIL_OCR_REPAIRS: dict[str | re.Pattern, str] = {
    re.compile(r"^Sent (Sun|Mon|Tue|Wed|Thu|Fri|Sat)", re.MULTILINE): r"Sent: \1",
    re.compile(fr"({FIELDS_COLON_PATTERN}.*\n)\nSubject:", re.MULTILINE): r'\1Subject:',
    re.compile(r"^Subject[•]", re.MULTILINE): 'Subject:',
    re.compile(r"^Fran:", re.MULTILINE): 'From:',
}

# "Sent from my iPhone" regexes
DEVICE_PATTERNS = [
    r"and string",
    r"AT&T",
    r"Droid",
    r"iPad",
    r"Phone",
    r"Mail",
    r"Surface(\s+RT)?",
    r"BlackBerry(.*(smartphone|device|Handheld|AT&T|T- ?Mobile))?",
]

SIGNATURE_PATTERNS = [
    r"Co-authored with iPhone auto-correct",
    r"(i Phone feature:|Pls excuse) tupos & abbrvtns",
    r"Typos,? misspellings courtesy of iPhone(\s*word & thought substitution|Send from my mobile...please excuse typos)?"
]

DEVICE_PATTERN = r"(Envoyé de mon|Sent (from|via)).*(" + '|'.join(DEVICE_PATTERNS) + r")"
EPSTEIN_TYPO_PREFIX = r"((Please forgive|Sorry for all the) typos.{1,4})"
SENT_FROM_DEVICE_PATTERN = '|'.join([DEVICE_PATTERN] + SIGNATURE_PATTERNS)
SENT_FROM_REGEX = re.compile(fr'^{EPSTEIN_TYPO_PREFIX}?({SENT_FROM_DEVICE_PATTERN})\.?', re.M | re.I)

# Misc
MAILING_LISTS = [
    CAROLYN_RANGEL,
    INTELLIGENCE_SQUARED,
    JP_MORGAN_USGIO,
    'middle.east.update@hotmail.com',
]

TRUNCATE_EMAILS_FROM_OR_TO = [
    AMANDA_ENS,
    ANTHONY_BARRETT,
    DANIEL_SABBA,
    DIANE_ZIMAN,
    JOSCHA_BACH,
    KATHERINE_KEATING,
    LAWRANCE_VISOSKI,
    LAWRENCE_KRAUSS,
    LISA_NEW,
    MOSHE_HOFFMAN,
    NILI_PRIELL_BARAK,
    PAUL_KRASSNER,
    PAUL_PROSPERI,
    'Susan Edelman',
    TERRY_KAFKA,
]

TRUNCATE_EMAILS_FROM = TRUNCATE_EMAILS_FROM_OR_TO + [
    'Alan S Halperin',
    'Alain Forget',
    ARIANE_DE_ROTHSCHILD,
    AZIZA_ALAHMADI,
    BILL_SIEGEL,
    DAVID_HAIG,
    EDWARD_ROD_LARSEN,
    JOHNNY_EL_HACHEM,
    'Mark Green',
    MELANIE_WALKER,
    'Mitchell Bard',
    PEGGY_SIEGAL,
    ROBERT_LAWRENCE_KUHN,
    ROBERT_TRIVERS,
    'Skip Rimer',
    'Steven Elkman',
    STEVEN_PFEIFFER,
    'Steven Victor MD',
    TERRY_KAFKA,
]

EMAIL_SIGNATURE_REGEXES = {
    ARIANE_DE_ROTHSCHILD: re.compile(r"Ensemble.*\nCe.*\ndestinataires.*\nremercions.*\nautorisee.*\nd.*\nLe.*\ncontenues.*\nEdmond.*\nRoth.*\nlo.*\nRoth.*\ninfo.*\nFranc.*\n.2.*", re.I),
    BARBRO_C_EHNBOM: re.compile(r"Barbro C.? Ehn.*\nChairman, Swedish-American.*\n((Office|Cell|Sweden):.*\n)*(360.*\nNew York.*)?"),
    BRAD_KARP: re.compile(r"This message is intended only for the use of the Addressee and may contain information.*\nnot the intended recipient, you are hereby notified.*\nreceived this communication in error.*"),
    BROCK_PIERCE: re.compile(r"Best regards,\nBrock Pierce|IMPORTANT NOTICE: This.*\n(individual.*\nthat is.*\nlaw.*\nemployee.*\nrecipient.*|may contain info.*\nreader of this.*)|(Mobile?:?.*\n)?(Skype:.*\n)?E:?.*\n(W:.*\n)?(Follow me.*\n)?Co-invest.*(\nLinked.*)?"),
    DANIEL_SIAD: re.compile(r"Confidentiality Notice: The information contained in this electronic message is PRIVILEGED and confidential information intended only for the use of the individual entity or entities named as recipient or recipients. If the reader is not the intended recipient, be hereby notified that any dissemination, distribution or copy of this communication is strictly prohibited. If you have received this communication in error, please notify me immediately by electronic mail or by telephone and permanently delete this message from your computer system. Thank you.".replace(' ', r'\s*'), re.IGNORECASE),
    DANNY_FROST: re.compile(r"Danny Frost\nDirector.*\nManhattan District.*\n212.*", re.IGNORECASE),
    DARREN_INDYKE: re.compile(r"DARREN K. INDYKE.*?\**\nThe information contained in this communication.*?Darren K.[\n\s]+?[Il]ndyke(, PLLC)? — All rights reserved\.? ?\n\*{50,120}(\n\**)?", re.DOTALL),
    DAVID_FISZEL: re.compile(r"This e-mail and any file.*\nmail and/or any file.*\nmail or any.*\nreceived.*\nmisdirected.*"),
    DAVID_INGRAM: re.compile(r"Thank you in advance.*\nDavid Ingram.*\nCorrespondent\nReuters.*\nThomson.*(\n(Office|Mobile|Reuters.com).*)*"),
    DAVID_STERN: re.compile(r"This message is confidential. It.{350,420}Asia Gateway.{,50}nor endorsed by it\.?", re.DOTALL),
    DEEPAK_CHOPRA: re.compile(fr"({DEEPAK_CHOPRA}( MD)?\n)?2013 Costa Del Mar Road\nCarlsbad, CA 92009(\n(Chopra Foundation|Super Genes: Unlock.*))?(\nJiyo)?(\nChopra Center for Wellbeing)?(\nHome: Where Everyone is Welcome)?"),
    EDUARDO_ROBLES: re.compile(r"(• )?email:.*\n(• )?email:\n(• )?website: www.creativekingdom.com\n(• )?address: 5th Floor Office No:504 Aspect Tower,\nBusiness Bay, Dubai United Arab Emirates."),
    'Erika Kellerhals': re.compile(r"Notice: This communica.ion may contain privileged or other confidential.{,310}delete the copy you recei.ed. Thank you.?", re.DOTALL),
    ERIC_ROTH: re.compile(r"2221 Smithtown Avenue\nLong Island.*\nRonkonkoma.*\n(.1. )?Phone\nFax\nCell\ne-mail"),
    FRANCESCA_HALL: re.compile(r"The contents of this e-mail message and.{,600}message and its attachments[.,]? if any", re.DOTALL),
    GHISLAINE_MAXWELL: re.compile(r"FACEBOOK\nTWITTER\nG\+\nPINTEREST\nINSTAGRAM\nPLEDGE\nTHE DAILY CATCH"),
    JEANNE_M_CHRISTENSEN: re.compile(r"[A ]*(Please consider the environment before printing this e-mail.{,5})?This communication may contain Confidential.{,500}(facsimile|mail)\s+or\s+phone. Thank you\.?|Partner\s+WIGDOR.{,12}New York,? NY 10003\s.{,15}com", re.DOTALL),
    JEFFREY_EPSTEIN: re.compile(r"(([* =0,]+|please .ote.{,6})\s+)?([>»•]+ )*The info.mation containe. i. th.s..ommunicati.{,558}all\s+([>»] )*.ttachm..t..(\s+copyright\s+.all\s+rights\s+reserved?)?", re.DOTALL),
    JESSICA_CADWELL: re.compile(r"(f.*\n)?Certified Para.*\nFlorida.*\nBURMAN.*\n515.*\nSuite.*\nWest Palm.*(\nTel:.*)?(\nEmail:.*)?", re.IGNORECASE),
    KEN_JENNE: re.compile(r"Ken Jenne\nRothstein.*\n401 E.*\nFort Lauderdale.*", re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r"Please direct all scheduling.*\nFollow me on twitter.*\nwww.larrysummers.*", re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r"Lawrence (M. )?Krauss\n(Director.*\n)?(Co-director.*\n)?Foundation.*\nSchool.*\n(Co-director.*\n)?(and Director.*\n)?Arizona.*(\nResearch.*\nOri.*\n(krauss.*\n)?origins.*)?", re.IGNORECASE),
    LEON_BLACK: re.compile(r"This email and any files transmitted with it are confidential and intended solely.*\n(they|whom).*\ndissemination.*\nother.*\nand delete.*"),
    LISA_NEW: re.compile(r"Elisa New\nPowell M. Cabot.*\n(Director.*\n)?Harvard.*\n148.*\n([1I] )?12.*\nCambridge.*\n([1I] )?02138"),
    MARTIN_WEINBERG: re.compile(r"(Martin G. Weinberg, Esq.\n20 Park Plaza((, )|\n)Suite 1000\nBoston, MA 02116(\n61.*?)?(\n.*?([cC]ell|Office))*\n)?This Electronic Message contains.*?contents of this message is.*?prohibited.", re.DOTALL),
    MICHAEL_MILLER: re.compile(r"Michael C. Miller\nPartner\nwww.steptoe.com/mmiller\nSteptoe\n(Privileged.*\n)?(\+1\s+)?direct.*\n(\+1\s+)?(\+1\s+)?fax.*\n(\+1.*)?cell.*\n(www.steptoe.com\n)?This message and any.*\nyou are not.*\nnotify the sender.*"),
    NICHOLAS_RIBIS: re.compile(r"60 Morris Turnpike 2FL\nSummit,? NJ.*\n0:\nF:\n\*{20,}\nCONFIDENTIALITY NOTICE.*\nattachments.*\ncopying.*\nIf you have.*\nthe copy.*\nThank.*\n\*{20,}"),
    PETER_MANDELSON: re.compile(r'Disclaimer This email and any attachments to it may be.*?with[ \n]+number(.*?EC4V[ \n]+6BJ)?', re.DOTALL | re.IGNORECASE),
    PAUL_BARRETT: re.compile(r"Paul Barrett[\n\s]+Alpha Group Capital LLC[\n\s]+(142 W 57th Street, 11th Floor, New York, NY 10019?[\n\s]+)?(al?[\n\s]*)?ALPHA GROUP[\n\s]+CAPITAL"),
    PETER_ATTIA: re.compile(r"The information contained in this transmission may contain.*\n(laws|patient).*\n(distribution|named).*\n(distribution.*\nplease.*|copies.*)"),
    RICHARD_KAHN: re.compile(fr'Richard Kahn\s+HBRK Associates Inc.?\s+((301 East 66th Street, Suite 1OF|575 Lexington Avenue,? 4th Floor,?)\s+)?New York[.,]? (NY|New York) 100(22|65)(\s+(Tel?|Phone)( I|{REDACTED})?\s+Fa[x",]?(_|{REDACTED})*\s+[Ce]el?l?)?', re.IGNORECASE),
    ROSS_GOW: re.compile(r"Ross Gow\nManaging Partner\nACUITY Reputation Limited\n23 Berkeley Square\nLondon.*\nMobile.*\nTel"),
    STEPHEN_HANSON: re.compile(r"(> )?Confidentiality Notice: This e-mail transmission.*\n(which it is addressed )?and may contain.*\n(applicable law. If you are not the intended )?recipient you are hereby.*\n(information contained in or attached to this transmission is )?STRICTLY PROHIBITED.*"),
    STEVEN_PFEIFFER: re.compile(r"Steven\nSteven .*\nAssociate.*\nIndependent Filmmaker Project\nMade in NY.*\n30 .*\nBrooklyn.*\n(p:.*\n)?www\.ifp.*", re.IGNORECASE),
    'Susan Edelman': re.compile(r'Susan Edel.*\nReporter\n1211.*\n917.*\nsedelman.*', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r"((>|I) )?Terry B.? Kafka.*\n(> )?Impact Outdoor.*\n(> )?5454.*\n(> )?Dallas.*\n((> )?c?ell.*\n)?(> )?Impactoutdoor.*(\n(> )?cell.*)?", re.IGNORECASE),
    TOM_PRITZKER: re.compile(r"The contents of this email message.*\ncontain confidential.*\n(not )?the intended.*\n(error|please).*\n(you )?(are )?not the.*\n(this )?message.*"),
    TONJA_HADDAD_COLEMAN: re.compile(fr"Tonja Haddad Coleman.*\nTonja Haddad.*\nAdvocate Building\n315 SE 7th.*(\nSuite.*)?\nFort Lauderdale.*(\n({REDACTED} )?facsimile)?(\nwww.tonjahaddad.com?)?(\nPlease add this efiling.*\nThe information.*\nyou are not.*\nyou are not.*)?", re.IGNORECASE),
    UNKNOWN: re.compile(r"(This message is directed to and is for the use of the above-noted addressee only.*\nhereon\.)", re.DOTALL),
    'W Bradford Stephens': re.compile(r"This email \(including.*\n(please.*\n)?it.*\nand do not.*\n(does.*\n)?constitute.*\ninvestment.*\n(info.*\n)?contained.*\nthe.*\s*(sender.*\n)?update.*\nthis.*(\nemail.*)?"),
}

# Some emails have a lot of uninteresting CCs
FLIGHT_IN_2012_PEOPLE: list[Name] = ['Francis Derby', JANUSZ_BANASIAK, 'Louella Rabuyo', 'Richard Barnnet']

IRAN_DEAL_RECIPIENTS: list[Name] = [
    'Allen West',
    'Rafael Bardaji',
    'Philip Kafka',
    'Herb Goodman',
    'Grant Seeger',
    'Lisa Albert',
    'Janet Kafka',
    'James Ramsey',
    'ACT for America',
    'John Zouzelka',
    'Joel Dunn',
    'Nate McClain',
    'Bennet Greenwald',
    'Taal Safdie',
    'Uri Fouzailov',
    'Neil Anderson',
    'Nate White',
    'Rita Hortenstine',
    'Henry Hortenstine',
    'Gary Gross',
    'Forrest Miller',
    'Bennett Schmidt',
    'Val Sherman',
    'Marcie Brown',
    'Michael Horowitz',
    'Marshall Funk'
]

TRIVERS_CCS: list[Name] = [
    "Alan Rogers",
    "Anna Dreber",
    "Anula Jayasuriya",
    "Bill Prezant",
    "Bobby McCormick",
    "Clive Crook",
    "Dane Stangler",
    "Ron Bailey",
    "Ditsa Pines",
    "David Darst",
    "Gerry Ohrstrom",
    "Paul Romer",
    "John Mallen",
    "Jim Halligan",
    "Lee Silver",
    "Monika Gruter Cheney",
    "Marguerite Atkins",
    "Matt Ridley",
    "Mike Cagney",
    "Evan Smith",
    "Roger Edelen",
    "Oliver Goodenough",
    "Paul Zak",
    "Peter J Richerson",
    "Clair Brown",
    "Terry Anderson",
    "Tim Kane",
    "Rob Hanson",
    "president@usfca.edu",
]

# No point in ever displaying these; their emails show up elsewhere because they're mostly CC recipients
UNINTERESTING_EMAILERS = FLIGHT_IN_2012_PEOPLE + IRAN_DEAL_RECIPIENTS + TRIVERS_CCS + [
    'Alan Rogers',                           # Random CC
    'Andrew Friendly',                       # Presumably some relation of Kelly Friendly
    'Ariane Dwyer',                          # Daniel Sabba CC
    'Cheryl Kleen',                          # One email from Anne Boyles is displayed under Anne Boyles
    'Connie Zaguirre',                       # Random CC
    'Dan Fleuette',                          # Sean Bannon CC
    'Danny Goldberg',                        # Paul Krassner CC
    GERALD_LEFCOURT,                         # Single CC
    GORDON_GETTY,                            # Random CC
    'Grant J. Smith',                        # Ken Jenne CC
    JEFF_FULLER,                             # Jean Luc Brunel CC
    JOJO_FONTANILLA,                         # housekeeper
    'Joseph Vinciguerra',                    # Random CC
    'Kirk Blouin',                           # John Page / Police Code Enforcement chain
    'Larry Cohen',                           # Bill Gates CC
    LYN_FONTANILLA,                          # housekeeper
    'Mark Albert',                           # Random CC
    'Matthew Schafer',                       # Random CC
    MICHAEL_BUCHHOLTZ,                       # Terry Kafka CC
    'Nancy Dahl',                            # covered by Lawrence Krauss (her husband)
    'Michael Simmons',                       # Random CC
    'Nancy Portland',                        # Lawrence Krauss CC
    'Oliver Goodenough',                     # Robert Trivers CC
    'Peter Aldhous',                         # Lawrence Krauss CC
    'Peter Green',  # Farkas emailer
    'Players2',                              # Hoffenberg CC
    'Police Code Enforcement',               # Kirk Blouin / John Page CC
    'Sam Harris',                            # Lawrence Krauss CC
    SAMUEL_LEFF,                             # Random CC
    'Sean T Lehane',                         # Random CC
    'Stephen Rubin',                         # Random CC
    THANU_BOONYAWATANA,                      # Eduardo Robles CC
    'Tim Kane',                              # Random CC
    'Travis Pangburn',                       # Random CC
    'Vahe Stepanian',                        # Random CC
]

# These are long forwarded articles so we force a trim to 1,333 chars if these strings exist
TRUNCATE_TERMS = [
    'The rebuilding of Indonesia',  # Vikcy ward article
    'a sleek, briskly paced film whose title suggests a heist movie',  # Inside Job
    'Calendar of Major Events, Openings, and Fundraisers',
    'sent over from Marshall Heyman at the WSJ',
    "In recent months, China's BAT collapse",
    'President Obama introduces Jim Yong Kim as his nominee',
    'Trump appears with mobster-affiliated felon at New',
    'Congratulations to the 2019 Hillman Prize recipients',
    "Special counsel Robert Mueller's investigation may face a serious legal obstacle",
    "nearly leak-proof since its inception more than a year ago",
    # Nikolic
    'Nuclear Operator Raises Alarm on Crisis',
    'as responsible for the democratisation of computing and',
    'AROUND 1,000 operational satellites are circling the Earth',
    # Sultan Sulayem
    'co-inventor of the GTX Smart Shoe',
    'my latest Washington Post column',
    # Bannon
    'As Steve Bannon continues his tour of Europe',
    "Bannon the European: He's opening the populist fort in Brussels",
    "Steve Bannon doesn't do subtle.",
    'The Department of Justice lost its latest battle with Congress',
    'pedophile Jeffrey Epstein bought his way out',
    # lawyers
    'recuses itself from Jeffrey Epstein case',
    # Misc
    'people from LifeBall',  # Nikolic
    "It began with deep worries regarding China's growth path",  # Paul Morris
    'A friendly discussion about Syria with a former US State Department',  # Fabrice Aidan
    'The US trade war against China: The view from Beijing',  # Robert Kuhn / Groff
    'This much we know - the Fall elections are shaping up',  # Juleanna Glover / Bannon
]

# Arguments to Email._merge_lines(). Note the line repair happens *after* 'Importance: High' is removed
LINE_REPAIR_MERGES = {
    '013405': [[4]] * 2,
    '013415': [[4]] * 2,
    '014397': [[4]] * 2,
    '014860': [[3], [4], [4]],
    '017523': [[4]],
    '030367': [[1, 4], [2, 4]],
    '019105': [[5]] * 4,
    '019407': [[2, 4]],
    '022187': [[1, 8], [2, 8], [3, 8], [4, 8]],
    '021729': [[2]],
    '032896': [[2]],
    '033050': [[0, 6], [1, 6], [2, 6], [3, 6], [4, 6]],
    '022949': [[0, 4], [1, 4]],
    '022197': [[0, 5], [1, 5], [3, 5]],
    '021814': [[1, 6], [2, 6], [3, 6], [4, 6]],
    '022190': [[1, 7], [0, 6], [3, 6], [4, 6]],
    '029582': [[0, 5], [1, 5], [3, 5], [3, 5]],
    '022673': [[9]],
    '022684': [[9]],
    '026625': [[0, 7], [1, 7], [2, 7], [3, 7], [4, 7], [5, 7]],
    '026659': [[0, 5], [1, 5]],
    '026764': [[0, 6], [1, 6]],
    '022695': [[4]],
    '022977': [[9]] * 10,
    '023001': [[5]] * 3,
    '023067': [[3]],
    '025233': [[4]] * 2,
    '025329': [[2]] * 9,
    '025790': [[2]],
    '025812': [[3]] * 2,
    '025589': [[3]] * 12,
    '026345': [[3]],
    '026609': [[4]],
    '028921': [[5, 4], [4, 5]],
    '026620': ([[20]] * 4) + [[3, 2]] + ([[2]] * 15) + [[2, 4]],
    '026829': [[3]],
    '026924': [[2, 4]],
    '028728': [[3]],
    '026451': [[3, 5]] * 2,
    '028931': [[3, 6]],
    '029154': [[2, 5]],
    '029163': [[2, 5]],
    '029282': [[2]],
    '029402': [[5]],
    '029433': [[3]],
    '029458': [[4]] * 3,
    '029498': [[2], [2, 4]],
    '029501': [[2]],
    '029545': [[3, 5]],
    '029773': [[2, 5]],
    '029831': [[3, 6]],
    '029835': [[2, 4]],
    '029841': [[3]],
    '029889': [[2], [2, 5]],
    '029976': [[3]],
    '029977': ([[2]] * 4) + [[4], [2, 4]],
    '030299': [[7, 10]],
    '030315': [[3, 5]],
    '030318': [[3, 5]],
    '030381': [[2, 4]],
    '030384': [[2, 4]],
    '030626': [[2], [4]],
    '030861': [[3, 8]],
    '030999': [[2, 4]],
    '031384': [[2]],
    '031428': [[2], [2, 4]],
    '031442': [[0]],
    '031489': [[2, 4], [3, 4], [3, 4], [10]],
    '031619': [[7], [17], [17]],
    '031748': [[3]] * 2,
    '031764': [[3], [8]],  # 8 is just for style fix internally, not header
    '031980': [[2, 4]],
    '032063': [[3, 5]],
    '032272': [[2, 10], [3]],
    '032405': [[4]],
    '032637': [[9]] * 3,
    '033097': [[2]],
    '033144': [[2, 4]],
    '033217': [[3]],
    '033228': [[3, 5]],
    '033252': [[9]] * 2,
    '033271': [[3]],
    '033299': [[3]],
    '033357': [[2, 4]],
    '033486': [[7, 9]],
    '033512': [[2]],
    '026024': [[1, 3], [2, 3]],
    '024923': [[0, 5], [2]],
    '033568': [[5]] * 5,
    '033575': [[2, 4]],
    '033576': [[3]],
    '033583': [[2]],

    # Note DOJ file line adjustments happen *after* DojFile._repair() is called
    'EFTA00039689': [[4]],
}

KNOWN_SIGNATURES = {
    'tupos & abbrvtns': LINDA_STONE,
    'Typos, misspellings courtesy of iPhone': LINDA_STONE,
}
