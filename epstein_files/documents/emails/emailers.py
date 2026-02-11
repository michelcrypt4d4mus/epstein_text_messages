"""
Regexes and patterns for identifying people in email headers.
"""
import re
from copy import deepcopy

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.data import escape_single_quotes
from epstein_files.util.logging import logger

BAD_EMAILER_REGEX = re.compile(r'^(>|11111111)|agreed|ok|sexy|re:|fwd:|Multiple Senders|((sent|attachments|subject|importance).*|.*(january|201\d|hysterical|i have|image0|so that people|article 1.?|momminnemummin|These conspiracy theories|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)|afiaata|[IM]{4,}).*)$', re.IGNORECASE)
BAD_NAME_CHARS_REGEX = re.compile(r"[\"'\[\]*><•=()‹]")
TIME_REGEX = re.compile(r'^((\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday)|\d{4} ).*')

EMAILER_ID_PATTERNS: dict[str, str] = {
    ADAM_BACK: r"Adam\s*Back?",
    ALAN_DERSHOWITZ: r'(alan.{1,7})?dershowi(lz?|t?z)|AlanDersh',
    ALIREZA_ITTIHADIEH: r'Alireza.[Il]ttihadieh',
    ALISON_J_NATHAN: r"Alison(\s*J\.?)?\s*Nathan|Nathan\s*NYSD\s*Chambers?",
    ANDREW_FARKAS: r"Andrew\s*(L\.\s*)?Farkas|Farkas,\s*Andrew(\s*L\.?)?",
    AMANDA_ENS: r'ens, amanda?|Amanda.Ens',
    AMIR_TAAKI: r'Amir\s*Taaki|genjix',
    ANAS_ALRASHEED: r'anas\s*al\s*rashee[cd]',
    ANDREW_MCCORMACK: r"Andrew\s*McCorm(ack?)?",
    ANIL_AMBANI: r'Anil.Ambani',
    ANN_MARIE_VILLAFANA: r'Villafana, Ann Marie|(A(\.|nn) Marie )?Villafa(c|n|ri)a',
    ANTHONY_SCARAMUCCI: r"mooch|(Anthony ('The Mooch' )?)?Scaramucci",
    ARIANE_DE_ROTHSCHILD: r'AdeR|((Ariane|Edmond) (de )?)?Rothsh?ch?ild|Ariane(?!\s+Dwyer)',
    AUDREY_STRAUSS: fr"{AUDREY_STRAUSS}|Strauss, Audrey",
    BARBRO_C_EHNBOM: r'behnbom@aol.com|(Barbro\s.*)?Ehnbom',
    BARRY_J_COHEN: r'barry\s*((j.?|james)\s*)?cohen?',
    BENNET_MOSKOWITZ: r'Moskowitz.*Bennet|Bennet.*Moskowitz',
    BOB_CROWE: r"[BR]ob Crowe",
    BOBBI_C_STERNHEIM: r"Bobbi C\.? Sternheim",
    BORIS_NIKOLIC: r'(boris )?nikolic?',
    BRAD_EDWARDS: r'Brad(ley)?(\s*J(.?|ames))?\s*Edwards',
    BRAD_KARP: r'Brad (S.? )?Karp|Karp, Brad',
    BUREAU_OF_PRISONS: r"bop\.gov",
    CHRISTIAN_EVERDELL: r"C(hristian\s*)?Everdell?",
    CHRISTOPHER_DILORIO: r"Chris\s*Di[lI]o[nr](io)?",
    DANGENE_AND_JENNIE_ENTERPRISE: r'Dangene and Jennie Enterprise?',
    DANNY_FROST: r'Frost, Danny|frostd@dany.nyc.gov|Danny\s*Frost',
    DARREN_INDYKE: r'darren$|Darren\s*(K\.?\s*)?[il]n[dq]_?yke?|dkiesq',
    DAVID_FISZEL: r'David\s*Fis?zel',
    DAVID_HAIG: fr'{DAVID_HAIG}|Haig, David',
    DAVID_STERN: r'David Stern?',
    DOUGLAS_WIGDOR: r'Doug(las)?\s*(H\.?)?\s*Wigdor',
    EDUARDO_ROBLES: r'Ed(uardo)?\s*Robles',
    EDWARD_JAY_EPSTEIN: r'(?<!Jeffrey )Edward (Jay )?Epstein',
    EHUD_BARAK: r'(ehud|e?h)\s*barak|\behud',
    FAITH_KATES: r'faith kates?',
    GANBAT_CHULUUNKHUU: r"Ganbat(@|\s*Ch(uluunkhuu)?)?",
    GERALD_BARTON: r'Gerald.*Barton',
    GERALD_LEFCOURT: r'Gerald\s*(B\.?\s*)?Lefcourt',
    GHISLAINE_MAXWELL: r'g ?max(well)?|Ghislaine|Maxwell',
    GOOGLE_PLUS: r'Google\+',
    HEATHER_MANN: r'Heather Mann?',
    IAN_ODONNELL: r"Ian O'?Donnell",
    INTELLIGENCE_SQUARED: r'intelligence\s*squared',
    JACKIE_PERCZEK: r'jackie percze[kl]?',
    JABOR_Y: r'[ji]abor\s*y?',
    JAMES_FITZGERALD: r"James Fitz[g ]eral?d?",
    JAMES_HILL: r"hill, james e.|james.e.hill@abc.com",
    JANUSZ_BANASIAK: r"Janu[is]z Banasiak",
    JEAN_HUGUEN: r"Jean[\s.]Huguen",
    JEAN_LUC_BRUNEL: r'Jean[- ]Luc Brunel?|JeanLuc',
    JEANNE_M_CHRISTENSEN: r"Jeanne\s*(M\.?)?\s*Christensen",
    JEFF_FULLER: r"jeff@mc2mm.com|Jeff Fuller",
    JEFFREY_EPSTEIN: r'[djl]\s?ee[vy]acation[©@]?g?(mail.com)?|Epstine|\bJEE?\b|Jeff(rey)? (Edward )?E((sp|ps)tein?)?( VI Foundation)?|jeeproject@yahoo.com|J Jep|Jeffery Edwards|(?<!(Mark L.|ard Jay) )Epstein',
    JESSICA_CADWELL: r'Jessica Cadwell?',
    JOHNNY_EL_HACHEM: r'el hachem johnny|johnny el hachem',
    JOI_ITO: r'ji@media.mit.?edu|(joichi|joi)( Ito)?',
    JOJO_FONTANILLA: r"Jo.. Fontanilla",
    JONATHAN_FARKAS: r'Jonathan Fark(a|u)(s|il)',
    KARYNA_SHULIAK: r"Karyna\s*Shuliak?",
    KATHRYN_RUEMMLER: r'Kathr?yn? Ruemmler?',
    KEN_STARR: r'starr, ken|Ken(neth\s*(W.\s*)?)?\s+starr?|starr',
    LANDON_THOMAS: r'lando[nr] thomas( jr)?|thomas jr.?, lando[nr]',
    LARRY_SUMMERS: r'(La(wrence|rry).{1,5})?Summers?|^LH$|LHS|[Il]hsofficel?',
    LAWRANCE_VISOSKI: r'La(rry|wrance) Visoski?|Lvjet',
    LAWRENCE_KRAUSS: r'Lawrence Kraus[es]?|[jl]awkrauss|kruase',
    LEON_BLACK: r'Leon\s*Black?|(?<!Marc )Leon(?! (Botstein|Jaworski|Wieseltier))',
    LILLY_SANCHEZ: r'Lilly.*Sanchez',
    LISA_NEW: r'E?Lisa New?\b',
    'LinkedIn': r"Linked[Il]n(\s*Updates)?",
    LORENZO_DE_MEDICI: r"Prince\s*Lorenzo|Lorenzo\s*de\s*Medici",
    LYN_FONTANILLA: r"L.n Fontanilla",
    MANUELA_MARTINEZ: fr'Manuela (- Mega Partners|Martinez)',
    MARIANA_IDZKOWSKA: r'Mariana [Il]d[źi]kowska?',
    MARIYA_PRUSAKOVA: r"Ma(sha|riy?a)\s*(Prus(kova|so))",
    MARK_EPSTEIN: r'Mark (L\. )?(Epstein|Lloyd)',
    MARC_LEON: r'Marc[.\s]+(Kensington|Leon)|Kensington2',
    MARTIN_NOWAK: r'(Martin.*?)?No[vw]ak|Nowak, Martin',
    MARTIN_WEINBERG: r'martin.*?weinberg',
    "Matthew Schafer": r"matthew\.?schafer?",
    MELANIE_SPINELLA: r'M?elanie Spine[Il]{2}a',
    MICHAEL_BUCHHOLTZ: r'Michael.*Buchholtz',
    MICHAEL_MILLER: r'Micha(el)? Miller|Miller, Micha(el)?',
    MICHAEL_SITRICK: r'(Mi(chael|ke).{0,5})?[CS]itrick',
    MICHAEL_WOLFF: r'Michael\s*Wol(f[ef]e?|i)|Wolff',
    MIROSLAV_LAJCAK: r"Miro(slav)?(\s+Laj[cč][aá]k)?",
    MOHAMED_WAHEED_HASSAN: r'Mohamed Waheed(\s+Hassan)?',
    NADIA_MARCINKO: r"Na[dď]i?a\s+Marcinko(v[aá])?",
    NEAL_KASSELL: r'Neal\s*Kassell?',
    'Newsmax': r"Newsmax\.com",
    NICHOLAS_RIBIS: r'Nic(holas|k)[\s._]Ribi?s?|Ribbis',
    OFFICE_OF_THE_DEPUTY_ATTORNEY_GENERAL: r"\bODAG\b",
    OLIVIER_COLOM: fr'Colom, Olivier|{OLIVIER_COLOM}',
    PAUL_BARRETT: r'Paul Barre(d|tt)',
    PAUL_KRASSNER: r'Pa\s?ul Krassner',
    PAUL_MORRIS: r'morris, paul|Paul Morris',
    PAULA: r'^Paula( Heil Fisher)?$',
    PEGGY_SIEGAL: r'Peggy Siegal?',
    PETER_ATTIA: r'Peter Attia?',
    PETER_MANDELSON: r"((Lord|Peter) )?Mandelson",
    'pink@mc2mm.com': r"^Pink$|pink@mc2mm\.com",
    PRINCE_ANDREW: r'Prince Andrew|The Duke',
    REID_WEINGARTEN: r'Weingarten, Rei[cdi]|Rei[cdi] Weingarten',
    RENATA_BOLOTOVA: fr"{RENATA_BOLOTOVA}|Rena B|Renata Bo\w+|renbolotova",
    RICHARD_KAHN: r'rich(ard)? kahn?',
    ROBERT_D_CRITTON_JR: r'Robert D.? Critton,? Jr.?',
    ROBERT_LAWRENCE_KUHN: r'Robert\s*(Lawrence)?\s*Kuhn',
    ROBERT_TRIVERS: r'tri[vy]ersr@gmail|Robert\s*Trivers?',
    ROSS_GOW: fr"Ross(acuity)? Gow|(ross@)?acuity\s*reputation(\.com)?",
    SAMUEL_LEFF: r"Sam(uel)?(/Walli)? Leff",
    SCOTT_J_LINK: r'scott j. link?',
    SEAN_BANNON: r'sean bannon?',
    SHAHER_ABDULHAK_BESHER: r'\bShaher(\s*Abdulhak\s*Besher)?\b',
    SOON_YI_PREVIN: r'Soon[- ]Yi Previn?',
    STACEY_RICHMAN: r"srichmanlaw|Stacey\s*Richman",
    STEPHEN_HANSON: r'ste(phen|ve) hanson?|Shanson900',
    STEVE_BANNON: r'steve banno[nr]?',
    STEVEN_SINOFSKY: r'Steven Sinofsky?',
    SULTAN_BIN_SULAYEM: r'Sultan (Ahmed )?bin Sulaye?m?',
    TERJE_ROD_LARSEN: r"Terje(( (R[øo]e?d[- ])?)?Lars[eo]n)?",
    TERRY_KAFKA: r'Terry Kafka?',
    THANU_BOONYAWATANA: r"Thanu (BOONYAWATANA|Cnx)",
    THORBJORN_JAGLAND: r'(Thor.{3,8})?Jag[il]and?',
    TONJA_HADDAD_COLEMAN: r"To(nj|rl)a Haddad Coleman|haddadfm@aol.com",
    TYLER_SHEARS: r"T[vy]ler\s*Shears",
    VINCENZO_IOZZO: r"Vincenzo [IL]ozzo",
}

# If found as substring consider them the author
EMAILERS = [
    'Anne Boyles',
    AL_SECKEL,
    'Ariane Dwyer',
    AZIZA_ALAHMADI,
    'Brittany Henderson',
    BILL_GATES,
    BILL_SIEGEL,
    BRAD_WECHSLER,
    BROCK_PIERCE,
    BRYAN_BISHOP,
    CHRISTINA_GALBRAITH,
    'Coursera',
    DANIEL_SABBA,
    'Danny Goldberg',
    DAVID_SCHOEN,
    DEBBIE_FEIN,
    DEEPAK_CHOPRA,
    ED_BOYLE,
    GLENN_DUBIN,
    GORDON_GETTY,
    'Ike Groff',
    'Jeff Pagliuca',
    'Kevin Bright',
    'Jack Lang',
    JACK_SCAROLA,
    JAY_LEFKOWITZ,
    JEREMY_RUBIN,
    JES_STALEY,
    JOHN_PAGE,
    'Jokeland',
    JOSCHA_BACH,
    'Kathleen Ruderman',
    KENNETH_E_MAPP,
    'Larry Cohen',
    LESLEY_GROFF,
    'lorraine@mc2mm.com',
    LINDA_STONE,
    MARK_TRAMO,
    MASHA_DROKOVA,
    MELANIE_WALKER,
    MERWIN_DELA_CRUZ,
    'Michael Simmons',   # Not the only "To:"
    'middle.east.update@hotmail.com',
    'Nancy Cain',
    'Nancy Dahl',
    'Nancy Portland',
    NICOLE_JUNKERMANN,
    'Oliver Goodenough',
    'Paula Speer',
    'Peter Aldhous',
    'Peter Green',
    ROGER_SCHANK,
    'Roy Black',
    STEVEN_PFEIFFER,
    'Steven Victor MD',
    'Susan Edelman',
    TOM_BARRACK,
    USANYS,
    'USMS',
    'Vahe Stepanian',
    VALAR_VENTURES,
    'Vladimir Yudashkin',
]

EMAILER_ID_REGEXES = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in EMAILER_ID_PATTERNS.items()}
EMAILER_REGEXES = deepcopy(EMAILER_ID_REGEXES)  # Keep a copy without the simple EMAILERS regexes

# Add simple matching regexes for EMAILERS entries to EMAILER_REGEXES
for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer + '?', re.IGNORECASE)  # Last char optional bc OCR sucks

SUPPRESS_LOGS_FOR_AUTHORS = [
    'Multiple Senders Multiple Senders',
    'Undisclosed recipients:',
    'undisclosed-recipients:',
]


def cleanup_str(_str: str) -> str:
    return BAD_NAME_CHARS_REGEX.sub('', _str.replace(REDACTED, '')).strip().strip('_').strip()


def extract_emailer_names(emailer_str: str) -> list[Name]:
    """Return a list of people's names found in `emailer_str` (email author or recipients field)."""
    raw_names = emailer_str.split(';')
    emailer_str = cleanup_str(emailer_str)

    if raw_names == [REDACTED] or raw_names == [UNKNOWN]:
        return [None]
    elif len(emailer_str) == 0:
        return []

    names_found: list[Name] = [name for name, regex in EMAILER_REGEXES.items() if regex.search(emailer_str)]

    if len(emailer_str) <= 2 or BAD_EMAILER_REGEX.match(emailer_str) or TIME_REGEX.match(emailer_str):
        if len(names_found) == 0 and emailer_str not in SUPPRESS_LOGS_FOR_AUTHORS:
            logger.warning(f"No emailer found in '{escape_single_quotes(emailer_str)}'")
        else:
            logger.info(f"Extracted {len(names_found)} names from semi-invalid '{emailer_str}': {names_found}...")

        return names_found

    names_found = names_found or [emailer_str]
    return [reverse_first_and_last_names(name) for name in names_found]
