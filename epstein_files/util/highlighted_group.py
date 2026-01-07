import re
from dataclasses import dataclass, field

from rich.highlighter import RegexHighlighter
from rich.text import Text

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import ARCHIVE_LINK_COLOR
from epstein_files.util.constants import (EMAILER_ID_REGEXES, EPSTEIN_V_ROTHSTEIN_EDWARDS, HEADER_ABBREVIATIONS,
     OSBORNE_LLP, REPLY_REGEX, SENT_FROM_REGEX, VIRGIN_ISLANDS)
from epstein_files.util.doc_cfg import *
from epstein_files.util.data import extract_last_name, listify, without_falsey

CIVIL_ATTORNEY = 'civil attorney'
CRIMINAL_DEFENSE_ATTORNEY = 'criminal defense attorney'
CRIMINAL_DEFENSE_2008 = f"{CRIMINAL_DEFENSE_ATTORNEY} on 2008 case"
EPSTEIN_LAWYER = 'Epstein lawyer'
EPSTEIN_V_ROTHSTEIN_EDWARDS_ATTORNEY = f"{CIVIL_ATTORNEY} working on {EPSTEIN_V_ROTHSTEIN_EDWARDS}"
ESTATE_EXECUTOR = 'estate executor'
EPSTEIN_ESTATE_EXECUTOR = f"Epstein {ESTATE_EXECUTOR}"
REGEX_STYLE_PREFIX = 'regex'
SIMPLE_NAME_REGEX = re.compile(r"^[-\w ]+$", re.IGNORECASE)

CATEGORY_STYLE_MAPPING = {
    ARTICLE: JOURNALIST,
    ARTS: ENTERTAINER,
    BOOK: JOURNALIST,
    LEGAL: EPSTEIN_LAWYER,
    POLITICS: LOBBYIST,
    PROPERTY: BUSINESS,
    REPUTATION: PUBLICIST,
}

CATEGORY_STYLES = {
    JSON: 'dark_red',
    JUNK: 'grey19',
    'letter': 'medium_orchid1'
}


@dataclass(kw_only=True)
class HighlightedText:
    """
    Color highlighting for things other than people's names (e.g. phone numbers, email headers).

    Attributes:
        label (str): RegexHighlighter match group name, defaults to 1st 'emailers' key if only 1 emailer provided
        pattern (str): regex pattern identifying strings matching this group
        regex (re.Pattern): matches self.pattern
        style (str): Rich style to apply to text matching this group
        theme_style_name (str): The style name that must be a part of the rich.Console's theme
    """
    label: str = ''
    pattern: str = ''
    style: str
    regex: re.Pattern = field(init=False)
    theme_style_name: str = field(init=False)
    _capture_group_label: str = field(init=False)
    _match_group_var: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            raise ValueError(f"No label provided for {repr(self)}")

        self._capture_group_label = self.label.lower().replace(' ', '_').replace('-', '_')
        self._match_group_var = fr"?P<{self._capture_group_label}>"
        self.theme_style_name = f"{REGEX_STYLE_PREFIX}.{self._capture_group_label}"
        self.regex = re.compile(fr"({self._match_group_var}{self.pattern})", re.IGNORECASE | re.MULTILINE)

    def __str__(self) -> str:
        return f"{type(self).__name__}(label='{self.label}')"


@dataclass(kw_only=True)
class HighlightedNames(HighlightedText):
    """
    Encapsulates info about people, places, and other strings we want to highlight with RegexHighlighter.
    Constructor must be called with either an 'emailers' arg or a 'pattern' arg (or both).

    Attributes:
        category (str): optional string to use as an override for self.label in some contexts
        emailers (dict[str, str | None]): optional names to construct regexes for (values are descriptions)
        _pattern (str): regex pattern combining 'pattern' with first & last names of all 'emailers'
    """
    category: str = ''
    emailers: dict[str, str | None] = field(default_factory=dict)
    _pattern: str = field(init=False)

    def __post_init__(self):
        if not (self.emailers or self.pattern):
            raise ValueError(f"Must provide either 'emailers' or 'pattern' arg.")
        elif not self.label:
            if len(self.emailers) == 1:
                self.label = [k for k in self.emailers.keys()][0]
            else:
                raise ValueError(f"No label provided for {repr(self)}")

        super().__post_init__()
        self._pattern = '|'.join([self._emailer_pattern(e) for e in self.emailers] + listify(self.pattern))
        self.regex = re.compile(fr"\b({self._match_group_var}({self._pattern})s?)\b", re.IGNORECASE)

    def get_info(self, name: str) -> str | None:
        """Label and additional info for 'name' if 'name' is in self.emailers."""
        info_pieces = [
            None if len(self.emailers) == 1 else (self.category or self.label.replace('_', ' ')),
            self.emailers.get(name),
        ]

        info_pieces = without_falsey(info_pieces)
        return ', '.join(info_pieces) if info_pieces else None

    def _emailer_pattern(self, name: str) -> str:
        """Pattern matching 'name'. Extends value in EMAILER_ID_REGEXES with first/last name if it exists."""
        name = remove_question_marks(name)
        last_name = extract_last_name(name)
        first_name = name.removesuffix(f" {last_name}")

        if name in EMAILER_ID_REGEXES:
            pattern = EMAILER_ID_REGEXES[name].pattern

            # Include regex for first and last names
            for partial_name in [first_name, last_name]:
                if SIMPLE_NAME_REGEX.match(partial_name) and partial_name.lower() not in NAMES_TO_NOT_HIGHLIGHT:
                    pattern += fr"|{partial_name}"

            return pattern
        elif ' ' not in name:
            return name

        name_patterns = [
            n.replace(' ', r"\s+") for n in [name, first_name, last_name]
            if n.lower() not in NAMES_TO_NOT_HIGHLIGHT
        ]

        return '|'.join(name_patterns)

    def __str__(self) -> str:
        return f"{type(self).__name__}(label='{self.label}')"


HIGHLIGHTED_NAMES = [
    HighlightedNames(
        label='Africa',
        style='light_pink4',
        pattern=r'Econet(\s*Wireless)|Ghana(ian)?|Johannesburg|Kenya|Nigerian?|Senegal(ese)?|Serengeti|(South\s*)?African?|(Strive\s*)?Masiyiwa|Tanzania|Ugandan?|Zimbabwe(an)?',
        emailers={
            'Abdoulaye Wade': 'former president of Senegal, father of Karim Wade',
            'Karim Wade': 'son of the president of Senegal, facing arrest for corruption, email handle is "Afri zp"',
            'Miles Alexander': 'Operations Manager Michaelhouse Balgowan KwaZulu-Natal South Africa',  # TODO: what's up with this person?
            'Macky Sall': 'prime minister of Senegal, defeated Abdoulaye Wade',
        },
    ),
    HighlightedNames(
        label='bitcoin',
        style='orange1 bold',
        pattern=r'Balaji|bitcoin|block ?chain(\s*capital)?|Brock(\s*Pierce)?|coins?|cr[iy]?pto(currenc(y|ies))?|e-currency|(Gavin )?Andressen|(Howard\s+)?Lutnic?k|(jeffrey\s+)?wernick|Libra|Madars|(Patrick\s*)?Murck|(Ross\s*)?Ulbricht|Silk\s*Road|SpanCash|Tether|virtual\s*currenc(ies|y)|(zero\s+knowledge\s+|zk)pro(of|tocols?)',
        emailers = {
            JEREMY_RUBIN: 'developer/researcher',
            ANTHONY_SCARAMUCCI: 'Skybridge Capital, FTX investor',
        },
    ),
    HighlightedNames(
        label=BUSINESS,
        style='spring_green4',
        pattern=r'Gruterite|(John\s*)?Kluge|Marc Rich|(Mi(chael|ke)\s*)?Ovitz|(Steve\s+)?Wynn|(Les(lie)?\s+)?Wexner|New Leaf Ventures|Park Partners|SALSS|Swedish[-\s]*American\s*Life\s*Science\s*Summit|Valhi|(Yves\s*)?Bouvier',
        emailers = {
            ALIREZA_ITTIHADIEH: 'CEO Freestream Aircraft Limited',
            BARBRO_C_EHNBOM: 'Swedish pharmaceuticals, SALSS',
            FRED_HADDAD: "co-founder of Heck's in West Virginia",
            GERALD_BARTON: "Maryland property developer Landmark Land Company, fan of Trump's Irish golf course",
            GORDON_GETTY: 'heir of oil tycoon J. Paul Getty',
            NICHOLAS_RIBIS: 'Hilton CEO, former president of Trump Organization',
            'Philip Kafka': 'president of Prince Concepts (and son of Terry Kafka?)',
            ROBERT_LAWRENCE_KUHN: "investment banker, China expert",
            TERRY_KAFKA: 'CEO of Impact Outdoor (highway billboards)',
            TOM_PRITZKER: 'brother of J.B. Pritzker',
        }
    ),
    HighlightedNames(
        label='cannabis',
        style='chartreuse2',
        pattern=r"CBD|cannabis|marijuana|THC|WEED(guide|maps)?[^s]?",
    ),
    HighlightedNames(
        label='China',
        style='bright_red',
        pattern=r"Ali.?baba|Beijing|CCP|Chin(a|e?se)(?! Daily)|DPRK|Global Times|Guo|Hong|Huaw[ae]i|Kim\s*Jong\s*Un|Kong|Jack\s+Ma|Kwok|Ministry\sof\sState\sSecurity|Mongolian?|MSS|North\s*Korea|Peking|PRC|SCMP|Tai(pei|wan)|Xi(aomi)?|Jinping",
        emailers={
            'Gino Yu': 'professor / game designer in Hong Kong',
        }
    ),
    HighlightedNames(
        label='Deepak Chopra',
        style='dark_sea_green4',
        emailers = {
            'Carolyn Rangel': 'assistant',
            DEEPAK_CHOPRA: 'woo woo',
        }
    ),
    HighlightedNames(
        label='Democrats',
        style='sky_blue1',
        pattern=r'(Al\s*)?Franken|((Bill|Hillart?y)\s*)?Clinton|((Chuck|Charles)\s*)?S(ch|hc)umer|(Diana\s*)?DeGette|DNC|Elena\s*Kagan|(Eliott?\s*)?Spitzer(, Eliot)?|George\s*Mitchell|(George\s*)?Soros|Hill?ary|Dem(ocrat(ic)?)?|(Jo(e|seph)\s*)?Biden|(John\s*)?Kerry|Lisa Monaco|(Matteo\s*)?Salvini|Maxine\s*Waters|(Barac?k )?Obama|(Nancy )?Pelosi|Ron\s*Dellums|Schumer|(Tim\s*)?Geithner|Vernon\s*Jordan',
    ),
    HighlightedNames(
        label='Dubin family',
        style='medium_orchid1',
        pattern=r'((Celina|Eva( Anderss?on)?|Glenn) )?Dubin',
        emailers = {
            GLENN_DUBIN: "Highbridge Capital Management, married to Epstein's ex-gf Eva",
            EVA: "possibly Epstein's ex-girlfriend (?)",
        },
    ),
    HighlightedNames(
        label='employee',
        style='deep_sky_blue4',
        pattern=r'Merwin',
        emailers = {
            'Alfredo Rodriguez': "Epstein's butler, stole the journal",
            ERIC_ROTH: 'jet decorator',
            GWENDOLYN_BECK: 'Epstein fund manager in the 90s',
            JEAN_HUGUEN: 'interior design at Alberto Pinto Cabinet',
            LAWRANCE_VISOSKI: 'pilot',
            LESLEY_GROFF: 'assistant',
            'Linda Pinto': 'interior design at Alberto Pinto Cabinet',
            MERWIN_DELA_CRUZ: None,  # HOUSE_OVERSIGHT_032652 Groff says "Jojo and Merwin both requested off Nov. 25 and 26"
            NADIA_MARCINKO: 'pilot',
            'Sean J. Lancaster': 'airplane reseller',
        }
    ),
    HighlightedNames(
        label=ENTERTAINER,
        style='light_steel_blue3',
        pattern=r'(Art )?Spiegelman|Bobby slayton|bono\s*mick|Errol(\s*Morris)?|Etienne Binant|(Frank\s)?Gehry|Jagger|(Jeffrey\s*)?Katzenberg|(Johnny\s*)?Depp|Kid Rock|Lena\s*Dunham|Madonna|Mark\s*Burnett|Ramsey Elkholy|shirley maclaine|Steven Gaydos?|Woody( Allen)?|Zach Braff',
        emailers={
            ANDRES_SERRANO: "'Piss Christ' artist",
            'Barry Josephson': 'American film producer and former music manager, editor FamilySecurityMatters.org',
            BILL_SIEGEL: 'documentary film producer and director',
            DAVID_BLAINE: 'famous magician',
            HENRY_HOLT: f"{MICHAEL_WOLFF}'s book publisher",
            'Richard Merkin': 'painter, illustrator and arts educator',
            STEVEN_PFEIFFER: 'Associate Director at Independent Filmmaker Project (IFP)',
        },
    ),
    HighlightedNames(
        label=EPSTEIN_LAWYER,
        style='purple',
        pattern=r'(Barry (E. )?)?Krischer|Kate Kelly|Kirkland\s*&\s*Ellis|(Leon\s*)?Jaworski|Michael J. Pike|Paul,?\s*Weiss|Steptoe|Wein(berg|garten)',
        emailers = {
            'Alan S Halperin': 'parnter at Paul, Weiss',
            ARDA_BESKARDES: 'NYC immigration attorney allegedly involved in sex-trafficking operations',
            BENNET_MOSKOWITZ: f'represented the {EPSTEIN_ESTATE_EXECUTOR}s',
            BRAD_KARP: 'head of the law firm Paul Weiss',
            DAVID_SCHOEN: f"{CRIMINAL_DEFENSE_ATTORNEY} after 2019 arrest",
            DEBBIE_FEIN: EPSTEIN_V_ROTHSTEIN_EDWARDS_ATTORNEY,
            'Erika Kellerhals': 'attorney in St. Thomas',
            GERALD_LEFCOURT: f'friend of {ALAN_DERSHOWITZ}',
            JACK_GOLDBERGER: CRIMINAL_DEFENSE_2008,
            JACKIE_PERCZEK: CRIMINAL_DEFENSE_2008,
            JAY_LEFKOWITZ: f"Kirkland & Ellis partner, {CRIMINAL_DEFENSE_2008}",
            JESSICA_CADWELL: 'paralegal',  # paralegal, see https://x.com/ImDrinknWyn/status/1993765348898927022
            LILLY_SANCHEZ: CRIMINAL_DEFENSE_ATTORNEY,
            MARTIN_WEINBERG: CRIMINAL_DEFENSE_ATTORNEY,
            MICHAEL_MILLER: 'Steptoe LLP partner',
            REID_WEINGARTEN: 'Steptoe LLP partner',
            ROBERT_D_CRITTON_JR: 'criminal defense attorney',
            'Robert Gold': None,
            'Roy Black': CRIMINAL_DEFENSE_2008,
            SCOTT_J_LINK: None,
            TONJA_HADDAD_COLEMAN: f'{EPSTEIN_V_ROTHSTEIN_EDWARDS_ATTORNEY}, maybe daughter of Fred Haddad?',
        }
    ),
    HighlightedNames(
        label=ESTATE_EXECUTOR,
        style='purple3 bold',
        category='Epstein lawyer',
        emailers = {
            DARREN_INDYKE: EPSTEIN_ESTATE_EXECUTOR,
            RICHARD_KAHN: EPSTEIN_ESTATE_EXECUTOR,
        }
    ),
    HighlightedNames(
        label='europe',
        style='light_sky_blue3',
        pattern=r'(Angela )?Merk(el|le)|Austria|(Benjamin\s*)?Harnwell|Berlin|Borge|Boris\s*Johnson|Brexit(eers?)?|Brit(ain|ish)|Brussels|Cannes|(Caroline|Jack)?\s*Lang(, Caroline)?|Cypr(iot|us)|Davos|ECB|England|EU|Europe(an)?(\s*Union)?|Fr(ance|ench)|Geneva|Germany?|Gillard|Gree(ce|k)|Ital(ian|y)|Jacques|(Kevin\s*)?Rudd|Le\s*Pen|London|Macron|Melusine|Munich|(Natalia\s*)?Veselnitskaya|(Nicholas\s*)?Sarkozy|Nigel(\s*Farage)?|Norw(ay|egian)|Oslo|Paris|Polish|pope|(Sebastian )?Kurz|(Vi(c|k)tor\s+)?Orbah?n|Edward Rod Larsen|Strasbourg|Strauss[- ]?Kahn|Swed(en|ish)(?![-\s]+America)|Switzerland|(Tony\s)?Blair|U\.?K\.?|Ukrain(e|ian)|Vienna|(Vitaly\s*)?Churkin|Zug',
        emailers = {
            ANDRZEJ_DUDA: 'former president of Poland',
            MIROSLAV_LAJCAK: 'Russia-friendly Slovakian politician, friend of Steve Bannon',
            PETER_MANDELSON: 'UK politics',
            TERJE_ROD_LARSEN: 'Norwegian diplomat',
            THORBJORN_JAGLAND: 'former prime minister of Norway and head of the Nobel Peace Prize Committee',
        }
    ),
    HighlightedNames(
        label='famous lawyer',
        style='medium_purple3',
        pattern=r'(David\s*)?Bo[il]es|dersh|(Gloria\s*)?Allred|(Mi(chael|ke)\s*)?Avenatti',
        emailers = {
            ALAN_DERSHOWITZ: 'Harvard Law School professor and all around (in)famous American lawyer',
            KEN_STARR: 'head of the Monica Lewinsky investigation against Bill Clinton',
        }
    ),
    HighlightedNames(
        label=FINANCE,
        style='green',
        pattern=r'Apollo|Ari\s*Glass|Bank|(Bernie\s*)?Madoff|Black(rock|stone)|B\s*of\s*A|Boothbay(\sFund\sManagement)?|Chase\s*Bank|Credit\s*Suisse|DB|Deutsche?\s*(Asset|Bank)|Electron\s*Capital\s*(Partners)?|Fenner|FRBNY|Goldman(\s*Sachs)|HSBC|Invesco|(Janet\s*)?Yellen|(Jerome\s*)?Powell(?!M\. Cabot)|(Jimmy\s*)?Cayne|JPMC?|j\.?p\.?\s*morgan(\.?com|\s*Chase)?|Madoff|Merrill(\s*Lynch)?|(Michael\s*)?(Cembalest|Milken)|Mizrahi\s*Bank|MLPF&S|((anti.?)?money\s+)?launder(s?|ers?|ing)?(\s+money)?|Morgan Stanley|(Peter L. )?Scher|(Ray\s*)?Dalio|(Richard\s*)?LeFrak|Schwartz?man|Serageldin|UBS|us.gio@jpmorgan.com',
        emailers={
            AMANDA_ENS: 'Citigroup',
            BRAD_WECHSLER: f"head of {LEON_BLACK}'s personal investment vehicle according to FT",
            DANIEL_SABBA: 'UBS Investment Bank',
            DAVID_FISZEL: 'CIO Honeycomb Asset Management',
            JES_STALEY: 'former CEO of Barclays',
            JIDE_ZEITLIN: 'former partner at Goldman Sachs, allegations of sexual misconduct',
            'Laurie Cameron': 'currency trading',
            LEON_BLACK: 'Apollo CEO',
            MARC_LEON: 'Luxury Properties Sari Morrocco',
            MELANIE_SPINELLA: f'representative of {LEON_BLACK}',
            MORTIMER_ZUCKERMAN: 'business partner of Epstein',
            PAUL_BARRETT: None,
            PAUL_MORRIS: DEUTSCHE_BANK,
            'Steven Elkman': DEUTSCHE_BANK,
        }
    ),
    HighlightedNames(
        label='friend',
        style='tan',
        pattern=r"Andrew Farkas|Thomas\s*(J\.?\s*)?Barrack(\s*Jr)?",
        emailers = {
            DANGENE_AND_JENNIE_ENTERPRISE: 'founders of the members-only CORE club',
            DAVID_STERN: f'emailed Epstein from Moscow, appears to know chairman of {DEUTSCHE_BANK}',
            JONATHAN_FARKAS: "heir to the Alexander's department store fortune",
            'linkspirit': "Skype username of someone Epstein communicated with",
            'Peter Thomas Roth': 'student of Epstein at Dalton, skincare company founder',
            STEPHEN_HANSON: None,
            TOM_BARRACK: 'long time friend of Trump',
        },
    ),
    HighlightedNames(
        label=HARVARD,
        style='light_goldenrod3',
        pattern=r'Cambridge|(Derek\s*)?Bok|Elisa(\s*New)?|Harvard(\s*(Business|Law|University)(\s*School)?)?|(Jonathan\s*)?Zittrain|(Stephen\s*)?Kosslyn',
        emailers = {
            "Donald Rubin": f"Professor of Statistics",
            "Kelly Friendly": f"longtime aide and spokesperson of {LARRY_SUMMERS}",
            LARRY_SUMMERS: 'board of Digital Currency Group (DCG), Harvard president, Obama economic advisor',
            'Leah Reis-Dennis': 'producer for Lisa New\'s Poetry in America',
            LISA_NEW: f'professor of poetry, wife of {LARRY_SUMMERS}, AKA "Elisa New"',
            'Lisa Randall': 'theoretical physicist',
            MARTIN_NOWAK: 'professor of mathematics and biology',
            MOSHE_HOFFMAN: 'lecturer and research scholar in behavioral and evolutionary economics',
        }
    ),
    HighlightedNames(
        label='India',
        style='bright_green',
        pattern=r'Abraaj|Anna\s*Hazare|(Arif\s*)?Naqvi|(Arvind\s*)?Kejriwal|Bangalore|Hardeep( Pur[ei]e)?|Indian?|InsightsPod|Modi|Mumbai|(New\s*)?Delhi|Tranchulas',
        emailers = {
            ANIL_AMBANI: 'chairman of Reliance Group',
            VINIT_SAHNI: None,
            ZUBAIR_KHAN: 'cybersecurity firm Tranchulas CEO, InsightsPod founder, based in Islamabad and Dubai',
        }
    ),
    HighlightedNames(
        label='Israel',
        style='dodger_blue2',
        pattern=r"AIPAC|Bibi|(eh|(Ehud|Nili Priell) )?barak|Ehud\s*Barack|Israeli?|Jerusalem|J\s*Street|Mossad|Netanyahu|(Sheldon\s*)?Adelson|Tel\s*Aviv|(The\s*)?Shimon\s*Post|Yitzhak|Rabin|YIVO|zionist",
        emailers={
            EHUD_BARAK: 'former primer minister',
            'Mitchell Bard': 'director of the American-Israeli Cooperative Enterprise (AICE)',
            'Nili Priell Barak': f'wife of {EHUD_BARAK}',
        }
    ),
    HighlightedNames(
        label='Japan',
        style='color(168)',
        pattern=r'BOJ|(Bank\s+of\s+)?Japan(ese)?|jpy?(?! Morgan)|SG|Singapore|Toky[op]',
    ),
    HighlightedNames(
        label=JOURNALIST,
        style='bright_yellow',
        pattern=r'Palm\s*Beach\s*(Daily\s*News|Post)|ABC(\s*News)?|Alex\s*Yablon|(Andrew\s*)?Marra|Arianna(\s*Huffington)?|(Arthur\s*)?Kretchmer|BBC|Bloomberg|Breitbart|Charlie\s*Rose|China\s*Daily|CNBC|CNN(politics?)?|Con[cs]hita|Sarnoff|(?<!Virgin[-\s]Islands[-\s])Daily\s*(Beast|Mail|News|Telegraph)|(David\s*)?Pecker|David\s*Brooks|Ed\s*Krassenstein|(Emily\s*)?Michot|Ezra\s*Klein|(George\s*)?Stephanopoulus|Globe\s*and\s*Mail|Good\s*Morning\s*America|Graydon(\s*Carter)?|Huffington(\s*Post)?|Ingram, David|(James\s*)?(Hill|Patterson)|Jonathan\s*Karl|Julie\s*(K.?\s*)?Brown|(Katie\s*)?Couric|Keith\s*Larsen|L\.?A\.?\s*Times|Miami\s*Herald|(Michele\s*)?Dargan|(National\s*)?Enquirer|(The\s*)?N(ew\s*)?Y(ork\s*)?(P(ost)?|T(imes)?)|(The\s*)?New\s*Yorker|NYer|PERVERSION\s*OF\s*JUSTICE|Politico|Pro\s*Publica|(Sean\s*)?Hannity|Sulzberger|SunSentinel|Susan Edelman|(Uma\s*)?Sanghvi|(The\s*)?Wa(shington\s*)?Po(st)?|Viceland|Vick[iy]\s*Ward|Vox|WGBH|(The\s*)?Wall\s*Street\s*Journal|WSJ|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk',
        emailers = {
            EDWARD_JAY_EPSTEIN: 'reporter who wrote about the kinds of crimes Epstein was involved in, no relation to Jeffrey',
            'James Hill': 'ABC News',
            JENNIFER_JACQUET: 'Future Science',
            JOHN_BROCKMAN: 'literary agent and author specializing in scientific literature',
            LANDON_THOMAS: 'New York Times',
            MICHAEL_WOLFF: 'Author of "Fire and Fury: Inside the Trump White House"',
            PAUL_KRASSNER: '60s counterculture guy',
            'Tim Zagat': 'Zagat restaurant guide CEO',
        }
    ),
    HighlightedNames(
        label='Latin America',
        style='yellow',
        pattern=r'Argentin(a|ian)|Bolsonar[aio]|Bra[sz]il(ian)?|Bukele|Caracas|Castro|Colombian?|Cuban?|El\s*Salvador|((Enrique )?Pena )?Nieto|LatAm|Lula|Mexic(an|o)|(Nicolas\s+)?Maduro|Panama( Papers)?|Peru|Venezuelan?|Zambrano',
    ),
    HighlightedNames(
        label='law enforcement',
        style='color(24) bold',
        pattern=r'ag|(Alicia\s*)?Valle|AML|(Andrew\s*)?McCabe|((Bob|Robert)\s*)?Mueller|(Byung\s)?Pak|CFTC?|CIA|CIS|CVRA|Dep(artmen)?t\.?\s*of\s*(the\s*)?(Justice|Treasury)|DHS|DOJ|FBI|FCPA|FDIC|Federal\s*Bureau\s*of\s*Investigation|FinCEN|FINRA|FOIA|FTC|IRS|(James\s*)?Comey|(Jennifer\s*Shasky\s*)?Calvery|((Judge|Mark)\s*)?(Carney|Filip)|(Kirk )?Blouin|KYC|NIH|NS(A|C)|OCC|OFAC|(Lann?a\s*)?Belohlavek|(Michael\s*)?Reiter|OGE|Office\s*of\s*Government\s*Ethics|Police Code Enforcement|(Preet\s*)?Bharara|SCOTUS|SD(FL|NY)|SEC|Secret\s*Service|Securities\s*and\s*Exchange\s*Commission|Southern\s*District\s*of\s*(Florida|New\s*York)|State\s*Dep(artmen)?t|Strzok|Supreme\s*Court|Treasury\s*(Dep(artmen)?t|Secretary)|TSA|USAID|(William\s*J\.?\s*)?Zloch',
        emailers = {
            ANN_MARIE_VILLAFANA: 'southern district of Florida U.S. Attorney',
            DANNY_FROST: 'Director of Communications at Manhattan DA',
        }
    ),
    HighlightedNames(
        label=LOBBYIST,
        style='light_coral',
        pattern=r'[BR]ob Crowe|CSIS|Stanley Rosenberg',
        emailers = {
            'Joshua Cooper Ramo': 'co-CEO of Henry Kissinger Associates',
            KATHERINE_KEATING: 'Daughter of former Australian PM',
            MOHAMED_WAHEED_HASSAN: 'former president of the Maldives',
            OLIVIER_COLOM: 'France',
            'Paul Keating': 'former PM of Australia',
            PUREVSUREN_LUNDEG: 'Mongolian ambassador to the UN',
            'Stanley Rosenberg': 'former President of the Massachusetts Senate',
        }
    ),
    HighlightedNames(
        label='mideast',
        style='dark_sea_green4',
        # something like this won't match ever because of word boundary: [-\s]9/11[\s.]
        pattern=r"Abdulmalik Al-Makhlafi|Abdullah|Abu\s+Dhabi|Afghanistan|Al[-\s]?Qa[ei]da|Ahmadinejad|Arab|Aramco|Assad|Bahrain|Basiji?|Benghazi|Cairo|Chagoury|Dj[iu]bo?uti|Doha|Dubai|Egypt(ian)?|Emir(at(es?|i))?|Erdogan|Fashi|Gaddafi|(Hamid\s*)?Karzai|Hamad\s*bin\s*Jassim|HBJ|Houthi|Imran\s+Khan|Iran(ian)?|Isi[ls]|Islam(abad|ic|ist)?|Istanbul|Kh?ashoggi|(Kairat\s*)?Kelimbetov|kasshohgi|Kaz(akh|ich)stan|Kazakh?|Kh[ao]menei|Khalid\s*Sheikh\s*Mohammed|KSA|Leban(ese|on)|Libyan?|Mahmoud|Marra[hk]e[cs]h|MB(N|S|Z)|Mid(dle)?\s*East|Mohammed\s+bin\s+Salman|Morocco|Mubarak|Muslim|Nayaf|Pakistani?|Omar|(Osama\s*)?Bin\s*Laden|Osama(?! al)|Palestin(e|ian)|Persian?|Riya(dh|nd)|Saddam|Salman|Saudi(\s+Arabian?)?|Shariah?|SHC|sheikh|shia|(Sultan\s*)?Yacoub|Syrian?|(Tarek\s*)?El\s*Sayed|Tehran|Tunisian?|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        emailers = {
            ANAS_ALRASHEED: f'former information minister of Kuwait {QUESTION_MARKS}',
            AZIZA_ALAHMADI: 'Abu Dhabi Department of Culture & Tourism',
            RAAFAT_ALSABBAGH: 'Saudi royal advisor',
            SHAHER_ABDULHAK_BESHER: 'Yemeni billionaire',
        }
    ),
    HighlightedNames(
        label='modeling',
        style='pale_violet_red1',
        pattern=r'\w+@mc2mm.com|model(ed|ing)|(Nicole\s*)?Junkerman',
        emailers = {
            'Abi Schwinck': 'MC2 Model Management (?)',
            DANIEL_SIAD: None,
            FAITH_KATES: 'Next Models co-founder',
            'Gianni Serazzi': 'fashion consultant?',
            HEATHER_MANN: 'South African former model, ex-girlfriend of Prince Andrew (?)',
            JEAN_LUC_BRUNEL: 'MC2 Model Management founder, died by suicide in French jail',
            JEFF_FULLER: 'president of MC2 Model Management USA',
            MANUELA_MARTINEZ: 'Mega Partners (Brazilian agency)',
            MARIANA_IDZKOWSKA: None,
            'Michael Sanka': 'MC2 Model Management (?)',
        }
    ),
    HighlightedNames(
        label=PUBLICIST,
        style='orange_red1',
        pattern=fr"(Matt(hew)? )?Hiltzi[gk]|{REPUTATION_MGMT}",
        emailers = {
            AL_SECKEL: 'husband of Isabel Maxwell, Mindshift conference organizer who fell off a cliff',
            'Barnaby Marsh': 'co-founder of Saint Partners, a philanthropy services company',
            CHRISTINA_GALBRAITH: f"{REPUTATION_MGMT}, worked on Epstein's Google search results with {TYLER_SHEARS}",
            IAN_OSBORNE: f"{OSBORNE_LLP} reputation repairer possibly hired by Epstein ca. 2011-06",
            MICHAEL_SITRICK: 'crisis PR',
            'Owen Blicksilver': 'OBPR, Inc.',
            PEGGY_SIEGAL: 'socialite',
            'R. Couri Hay': None,
            ROSS_GOW: 'Acuity Reputation Management',
            TYLER_SHEARS: f"{REPUTATION_MGMT}, worked on Epstein's Google search results with {CHRISTINA_GALBRAITH}",
        }
    ),
    HighlightedNames(
        label='Republicans',
        style='bold dark_red',
        pattern=r'Alberto\sGonzale[sz]|(Alex\s*)?Acosta|(Bill\s*)?Barr|Bill\s*Shine|(Bob\s*)?Corker|(John\s*(R.?\s*)?)Bolton|Broidy|(Chris\s)?Christie|Devin\s*Nunes|(Don\s*)?McGa[hn]n|McMaster|(George\s*)?Nader|GOP|(Brett\s*)?Kavanaugh|Kissinger|Kobach|Koch\s*Brothers|Kolfage|Kudlow|Lewandowski|(Marco\s)?Rubio|(Mark\s*)Meadows|Mattis|McCain|(?<!Merwin Dela )Cruz|(Michael\s)?Hayden|((General|Mike)\s*)?(Flynn|Pence)|(Mitt\s*)?Romney|Mnuchin|Nikki|Haley|(Paul\s+)?(Manafort|Volcker)|(Peter\s)?Navarro|Pompeo|Reagan|Reince|Priebus|Republican|(Rex\s*)?Tillerson|(?<!Cynthia )(Richard\s*)?Nixon|Sasse|Tea\s*Party',
        # There's no emails from these people, they're just here to automate the regex creation for both first + last names
        emailers = {
            RUDY_GIULIANI: None,
            TULSI_GABBARD: None,
        },
    ),
    HighlightedNames(
        label='Rothschild family',
        style='indian_red',
        emailers={
            ARIANE_DE_ROTHSCHILD: 'heiress',
            JOHNNY_EL_HACHEM: f'Works with {ARIANE_DE_ROTHSCHILD}',
        },
    ),
    HighlightedNames(
        label='Russia',
        style='red bold',
        pattern=r'Alfa\s*Bank|Anya\s*Rasulova|Chernobyl|Day\s+One\s+Ventures|(Dmitry\s)?(Kiselyov|(Lana\s*)?Pozhidaeva|Medvedev|Rybolo(o?l?ev|vlev))|Dmitry|FSB|GRU|KGB|Kislyak|Kremlin|Kuznetsova|Lavrov|Lukoil|Moscow|(Oleg\s*)?Deripaska|Oleksandr Vilkul|Rosneft|RT|St.?\s*?Petersburg|Russian?|Sberbank|Soviet(\s*Union)?|USSR|Vladimir|(Vladimir\s*)?(Putin|Yudashkin)|Women\s*Empowerment|Xitrans',
        emailers = {
            'Dasha Zhukova': 'art collector, daughter of Alexander Zhukov',
            MASHA_DROKOVA: 'silicon valley VC, former Putin Youth',
            RENATA_BOLOTOVA: 'former aspiring model, now fund manager at New York State Insurance Fund',
            SVETLANA_POZHIDAEVA: f'Epstein\'s Russian assistant who was recommended for a visa by Sergei Belyakov (FSB) and {DAVID_BLAINE}',
        }
    ),
    HighlightedNames(
        label=ACADEMIA,
        style='light_goldenrod2',
        pattern=r'Alain Forget|Brotherton|Carl\s*Sagan|Columbia|David Grosof|J(ames|im)\s*Watson|(Lord\s*)?Martin\s*Rees|Massachusetts\s*Institute\s*of\s*Technology|MIT(\s*Media\s*Lab)?|Media\s*Lab|Minsky|((Noam|Valeria)\s*)?Chomsky|Norman\s*Finkelstein|Praluent|Regeneron|(Richard\s*)?Dawkins|Sanofi|Stanford|(Stephen\s*)?Hawking|(Steven?\s*)?Pinker|UCLA',
        emailers = {
            DAVID_HAIG: 'evolutionary geneticist?',
            JOSCHA_BACH: 'cognitive science / AI research',
            'Daniel Kahneman': 'Nobel economic sciences laureate and cognitivie psychologist (?)',
            'Ed Boyden': 'Associate Professor, MIT Media Lab neurobiology',
            LAWRENCE_KRAUSS: 'theoretical physicist',
            LINDA_STONE: 'ex-Microsoft, MIT Media Lab',
            MARK_TRAMO: 'professor of neurology at UCLA',
            'Nancy Dahl': f'wife of {LAWRENCE_KRAUSS}',
            NEAL_KASSELL: 'professor of neurosurgery at University of Virginia',
            PETER_ATTIA: 'longevity medicine',
            ROBERT_TRIVERS: 'evolutionary biology',
            ROGER_SCHANK: 'Teachers College, Columbia University',
        },
    ),
    HighlightedNames(
        label='southeast Asia',
        style='light_salmon3 bold',
        pattern=r'Bangkok|Burm(a|ese)|Cambodian?|Laos|Malaysian?|Myan?mar|Thai(land)?|Vietnam(ese)?',
    ),
    HighlightedNames(
        label='tech bro',
        style='bright_cyan',
        pattern=r"AG?I|Chamath|Palihapitiya|Danny\s*Hillis|Drew\s*Houston|Eric\s*Schmidt|Greylock(\s*Partners)?|(?<!(ustin|Moshe)\s)Hoffmand?|LinkedIn|(Mark\s*)?Zuckerberg|Masa(yoshi)?(\sSon)?|Najeev|Nathan\s*Myhrvold|Palantir|(Peter\s)?Th(ie|ei)l|Pierre\s*Omidyar|Sergey\s*Brin|Silicon\s*Valley|Softbank|SpaceX|Tim\s*Ferriss?|WikiLeak(ed|s)",
        emailers = {
            'Auren Hoffman': 'CEO of SafeGraph (firm that gathers location data from mobile devices) and LiveRamp',
            ELON_MUSK: 'father of Mecha-Hitler',
            PETER_THIEL: 'Paypal mafia member, founder of Palantir, early Facebook investor, reactionary',
            REID_HOFFMAN: 'PayPal mafia member, founder of LinkedIn',
            STEVEN_SINOFSKY: 'ex-Microsoft, loves bitcoin',
        },
    ),
    HighlightedNames(
        label='trump',
        style='red3 bold',
        pattern=r"@?realDonaldTrump|(Alan\s*)?Weiss?elberg|\bDJ?T\b|Donald J. Tramp|(Donald\s+(J\.\s+)?)?Trump(ism|\s*Properties)?|Don(ald| *Jr)(?! Rubin)|Ivank?a|Jared|Kushner|(Madeleine\s*)?Westerhout|Mar[-\s]*a[-\s]*Lago|(Marla\s*)?Maples|(Matt(hew)? )?Calamari|\bMatt C\b|Melania|(Michael (J.? )?)?Boccio|Rebekah\s*Mercer|Roger\s+Stone|rona|(The\s*)?Art\s*of\s*the\s*Deal",
        emailers = {
            'Bruce Moskowitz': "'Trump's health guy' according to Epstein",
        },
    ),
    HighlightedNames(
        label='victim',
        style='orchid1',
        pattern=r'BVI|(Jane|Tiffany)\s*Doe|Katie\s*Johnson|(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts',
    ),
    HighlightedNames(
        label='victim lawyer',
        style='dark_magenta bold',
        pattern=r'(Alan(\s*P.)?|MINTZ)\s*FRAADE|Paul\s*(G.\s*)?Cassell|Rothstein\s*Rosenfeldt\s*Adler|(Scott\s*)?Rothstein|(J\.?\s*)?(Stan(ley)?\s*)?Pottinger',
        emailers = {
            BRAD_EDWARDS: 'Rothstein Rosenfeldt Adler (Rothstein was a crook & partner of Roger Stone)',
            JACK_SCAROLA: 'Searcy Denney Scarola Barnhart & Shipley',
        }
    ),
    HighlightedNames(
        label=VIRGIN_ISLANDS,
        style='sea_green1',
        pattern=r'Antigua|Bahamas|Caribb?ean|Dominican\s*Republic|(Great|Little)\s*St.?\s*James|Haiti(an)?|(John\s*)deJongh(\s*Jr\.?)|(Kenneth E\. )?Mapp|Palm\s*Beach(?!\s*Post)|PBI|S(ain)?t.?\s*Thomas|USVI|(?<!Epstein )VI|(The\s*)?Virgin\s*Islands(\s*Daily\s*News)?',  # TODO: VI Daily News should be yellow but it's hard bc Daily News xists
        emailers = {
            CECILE_DE_JONGH: f'first lady 2007-2015',
            STACEY_PLASKETT: 'non-voting member of Congress',
            KENNETH_E_MAPP: 'Governor',
        },
    ),

    # Individuals
    HighlightedNames(
        label=BILL_GATES,
        style='turquoise4',
        pattern=r'BG|b?g?C3|(Bill\s*((and|or)\s*Melinda\s*)?)?Gates|Melinda(\s*Gates)?|Microsoft|MSFT',
        emailers = {
            BORIS_NIKOLIC: f'biotech VC partner of {BILL_GATES}, {EPSTEIN_ESTATE_EXECUTOR}',
        },
    ),
    HighlightedNames(
        label=STEVE_BANNON,
        style='color(58)',
        pattern=r'((Steve|Sean)\s*)?Bannon?|(American\s*)?Dharma',
        emailers = {
            STEVE_BANNON: 'Trump campaign manager, memecoin grifter, convicted criminal',
        }
    ),
    HighlightedNames(
        emailers={STEVEN_HOFFENBERG: HEADER_ABBREVIATIONS['Hoffenberg']},
        pattern=r'(steven?\s*)?hoffenberg?w?',
        style='gold3'
    ),
    HighlightedNames(emailers={GHISLAINE_MAXWELL: None}, pattern='gmax(1@ellmax.com)?|TerraMar', style='deep_pink3'),
    HighlightedNames(emailers={JABOR_Y: HEADER_ABBREVIATIONS['Jabor']}, style='spring_green1'),
    HighlightedNames(emailers={JEFFREY_EPSTEIN: None}, pattern='JEGE|LSJ|Mark (L. )?Epstein', style='blue1'),
    HighlightedNames(emailers={JOI_ITO: 'former head of MIT Media Lab'}, style='gold1'),
    HighlightedNames(emailers={KATHRYN_RUEMMLER: 'former Obama legal counsel'}, style='magenta2'),
    HighlightedNames(emailers={MELANIE_WALKER: 'doctor'}, style='pale_violet_red1'),
    HighlightedNames(emailers={PAULA: "Epstein's ex-girlfriend who is now in the opera"}, label='paula_heil_fisher', style='pink1'),
    HighlightedNames(emailers={PRINCE_ANDREW: 'British royal family'}, style='dodger_blue1'),
    HighlightedNames(emailers={SOON_YI_PREVIN: "wife of Woody Allen"}, style='hot_pink'),
    HighlightedNames(emailers={SULTAN_BIN_SULAYEM: 'CEO of DP World, chairman of ports in Dubai'}, style='green1'),

    # HighlightedText not HighlightedNames bc of word boundary issue
    HighlightedText(
        label='unknown',
        style='cyan',
        pattern=r'\(unknown\)'
    ),
    HighlightedText(
        label='phone_number',
        style='bright_green',
        pattern=r"\+?(1?\(?\d{3}\)?[- ]\d{3}[- ]\d{4}|\d{2}[- ]\(?0?\)?\d{2}[- ]\d{4}[- ]\d{4})|(\b|\+)[\d+]{10,12}\b",
    ),
]

# Highlight regexes for things other than names, only used by RegexHighlighter pattern matching
HIGHLIGHTED_TEXTS = [
    HighlightedText(
        label='header_field',
        style='plum4',
        pattern=r'^(Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):',
    ),
    HighlightedText(
        label='http_links',
        style=f'{ARCHIVE_LINK_COLOR} underline',
        pattern=r"https?:[^\s]+",
    ),
    HighlightedText(
        label='quoted_reply_line',
        style='dim',
        pattern=REPLY_REGEX.pattern,
    ),
    HighlightedText(
        label='redacted',
        style='grey58',
        pattern=fr"{REDACTED}|Privileged - Redacted",
    ),
    HighlightedText(
        label='sent_from',
        style='gray42 italic',
        pattern=SENT_FROM_REGEX.pattern,
    ),
    HighlightedText(
        label='snipped_signature',
        style='gray19',
        pattern=r'<\.\.\.(snipped|trimmed).*\.\.\.>',
    ),
    HighlightedText(
        label='timestamp_2',
        style=TIMESTAMP_STYLE,
        pattern=r"\d{1,4}[-/]\d{1,2}[-/]\d{2,4} \d{1,2}:\d{2}:\d{2}( [AP]M)?",
    ),
]

ALL_HIGHLIGHTS = HIGHLIGHTED_NAMES + HIGHLIGHTED_TEXTS


class EpsteinHighlighter(RegexHighlighter):
    """Finds and colors interesting keywords based on the above config."""
    base_style = f"{REGEX_STYLE_PREFIX}."
    highlights = [highlight_group.regex for highlight_group in ALL_HIGHLIGHTS]


def get_info_for_name(name: str) -> str | None:
    highlight_group = _get_highlight_group_for_name(name)

    if highlight_group and isinstance(highlight_group, HighlightedNames):
        return highlight_group.get_info(name)


def get_style_for_category(category: str) -> str | None:
    if category in CATEGORY_STYLES:
        return CATEGORY_STYLES[category]
    elif category == CONFERENCE:
        return f"{get_style_for_category(ACADEMIA)} dim"
    elif category == SOCIAL:
        return get_style_for_category(PUBLICIST)

    for highlight_group in HIGHLIGHTED_NAMES:
        if highlight_group.label == CATEGORY_STYLE_MAPPING.get(category, category):
            return highlight_group.style


def get_style_for_name(name: str | None, default_style: str = DEFAULT, allow_bold: bool = True) -> str:
    highlight_group = _get_highlight_group_for_name(name or UNKNOWN)
    style = highlight_group.style if highlight_group else default_style
    return style if allow_bold else style.replace('bold', '').strip()


def styled_category(category: str) -> Text:
    return Text(category, get_style_for_category(category) or 'wheat4')


def _get_highlight_group_for_name(name: str) -> HighlightedNames | None:
    for highlight_group in HIGHLIGHTED_NAMES:
        if highlight_group.regex.search(name):
            return highlight_group
