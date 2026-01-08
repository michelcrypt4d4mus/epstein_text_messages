import json
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
    patterns: list[str] = field(default_factory=list)
    style: str
    regex: re.Pattern = field(init=False)
    theme_style_name: str = field(init=False)
    _capture_group_label: str = field(init=False)
    _match_group_var: str = field(init=False)
    _pattern: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            raise ValueError(f"No label provided for {repr(self)}")

        self._capture_group_label = self.label.lower().replace(' ', '_').replace('-', '_')
        self._match_group_var = fr"?P<{self._capture_group_label}>"
        self.theme_style_name = f"{REGEX_STYLE_PREFIX}.{self._capture_group_label}"
        self._pattern = '|'.join(self.patterns)
        self.regex = re.compile(fr"({self._match_group_var}{self._pattern})", re.IGNORECASE | re.MULTILINE)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(label='{self.label}', pattern='{self._pattern}', style='{self.style}')"


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

    def __post_init__(self):
        if not (self.emailers or self.patterns):
            raise ValueError(f"Must provide either 'emailers' or 'pattern' arg.")
        elif not self.label:
            if len(self.emailers) == 1:
                self.label = [k for k in self.emailers.keys()][0]
            else:
                raise ValueError(f"No label provided for {repr(self)}")

        super().__post_init__()
        self._pattern = '|'.join([self._emailer_pattern(e) for e in self.emailers] + self.patterns)
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
        return super().__str__()

    def __repr__(self) -> str:
        s = f"{type(self).__name__}("

        for property in ['label', 'style', 'category', 'patterns', 'emailers']:
            value = getattr(self, property)

            if not value or (property == 'label' and len(self.emailers) == 1 and not self.patterns):
                continue

            s += f"\n    {property}="

            if isinstance(value, dict):
                s += '{'

                for k, v in value.items():
                    s += f"\n        {constantize_name(k)}: {json.dumps(v).replace('null', 'None')},"

                s += '\n    },'
            elif property == 'patterns':
                s += '[\n        '
                s += repr(value).removeprefix('[').removesuffix(']').replace(', ', ',\n        ')
                s += ',\n    ],'
            else:
                s += f"{json.dumps(value)},"

        return s + '\n)'


HIGHLIGHTED_NAMES = [
    HighlightedNames(
        label='Africa',
        style='light_pink4',
        patterns=[
            r"Buhari",
            r"Econet(\s*Wireless)",
            r"Ghana(ian)?",
            r"Glencore",
            r"Goodluck Jonathan",
            r"Johannesburg",
            r"Kenya",
            r"Nigerian?",
            r"Okey Enelamah",
            r"Senegal(ese)?",
            r"Serengeti",
            r"(South\s*)?African?",
            r"(Strive\s*)?Masiyiwa",
            r"Tanzania",
            r"Ugandan?",
            r"Zimbabwe(an)?",
        ],
        emailers={
            'Abdoulaye Wade': "former president of Senegal, father of Karim Wade",
            'Ivan Glasenberg': "South African former CEO of Glencore, one of the world's largest commodity trading and mining companies",
            'Karim Wade': 'son of the president of Senegal, facing arrest for corruption, email handle is "Afri zp"',
            'Miles Alexander': 'Operations Manager Michaelhouse Balgowan KwaZulu-Natal South Africa',
            'Macky Sall': 'prime minister of Senegal, defeated Abdoulaye Wade',
        },
    ),
    HighlightedNames(
        label='bitcoin',
        style='orange1 bold',
        patterns=[
            r"Balaji",
            r"bitcoin",
            r"block ?chain(\s*capital)?",
            r"Brock(\s*Pierce)?",
            r"coins?",
            r"cr[iy]?pto(currenc(y|ies))?",
            r"e-currency",
            r"(Gavin )?Andressen",
            r"(Howard\s+)?Lutnic?k",
            r"Libra",
            r"Madars",
            r"(Patrick\s*)?Murck",
            r"(Ross\s*)?Ulbricht",
            r"Silk\s*Road",
            r"SpanCash",
            r"Tether",
            r"virtual\s*currenc(ies|y)",
            r"(zero\s+knowledge\s+|zk)pro(of|tocols?)",
        ],
        emailers={
            'Jeffrey Wernick': 'former COO of Parler, involved in numerous crypto companies like Bitforex',
            JEREMY_RUBIN: 'developer/researcher',
            ANTHONY_SCARAMUCCI: 'Skybridge Capital, FTX investor',
        },
    ),
    HighlightedNames(
        label=BUSINESS,
        style='spring_green4',
        patterns=[
            r"((Bill|David)\s*)?Koch(\s*(Bro(s|thers)|Industries))?",
            r"Gruterite",
            r"(John\s*)?Kluge",
            r"Marc Rich",
            r"(Mi(chael|ke)\s*)?Ovitz",
            r"(Steve\s+)?Wynn",
            r"(Les(lie)?\s+)?Wexner",
            r"New Leaf Ventures",
            r"Park Partners",
            r"SALSS",
            r"Swedish[-\s]*American\s*Life\s*Science\s*Summit",
            r"Valhi",
            r"(Yves\s*)?Bouvier",
        ],
        emailers={
            ALIREZA_ITTIHADIEH: 'CEO Freestream Aircraft Limited',
            BARBRO_C_EHNBOM: 'Swedish pharmaceuticals, SALSS',
            FRED_HADDAD: "co-founder of Heck's in West Virginia",
            GERALD_BARTON: "Maryland property developer Landmark Land Company, fan of Trump's Irish golf course",
            GORDON_GETTY: 'heir of oil tycoon J. Paul Getty',
            NICHOLAS_RIBIS: 'Hilton CEO, former president of Trump Organization',
            'Philip Kafka': 'president of Prince Concepts (and son of Terry Kafka?)',
            ROBERT_LAWRENCE_KUHN: 'investment banker, China expert',
            TERRY_KAFKA: 'CEO of Impact Outdoor (highway billboards)',
            TOM_PRITZKER: 'brother of J.B. Pritzker',
        },
    ),
    HighlightedNames(
        label='cannabis',
        style='chartreuse2',
        patterns=[
            r"CBD",
            r"cannabis",
            r"marijuana",
            r"THC",
            r"WEED(guide|maps)?[^s]?",
        ],
    ),
    HighlightedNames(
        label='China',
        style='bright_red',
        patterns=[
            r"Ali.?baba",
            r"Beijing",
            r"CCP",
            r"Chin(a|e?se)(?! Daily)",
            r"DPRK",
            r"Global Times",
            r"Guo",
            r"Hong",
            r"Huaw[ae]i",
            r"Kim\s*Jong\s*Un",
            r"Kong",
            r"Jack\s+Ma",
            r"Kwok",
            r"Ministry\sof\sState\sSecurity",
            r"Mongolian?",
            r"MSS",
            r"North\s*Korea",
            r"Peking",
            r"PRC",
            r"SCMP",
            r"Tai(pei|wan)",
            r"Xi(aomi)?",
            r"Jinping",
        ],
        emailers={
            'Gino Yu': 'professor / game designer in Hong Kong',
        },
    ),
    HighlightedNames(
        label=DEEPAK_CHOPRA,
        style='dark_sea_green4',
        emailers={
            CAROLYN_RANGEL: 'assistant',
            DEEPAK_CHOPRA: 'woo woo',
        },
    ),
    HighlightedNames(
        label='Democrats',
        style='sky_blue1',
        patterns=[
            r"(Al\s*)?Franken",
            r"((Bill|Hillart?y)\s*)?Clinton",
            r"((Chuck|Charles)\s*)?S(ch|hc)umer",
            r"(Diana\s*)?DeGette",
            r"DNC",
            r"Elena\s*Kagan",
            r"(Eliott?\s*)?Spitzer(, Eliot)?",
            r"George\s*Mitchell",
            r"(George\s*)?Soros",
            r"Hill?ary",
            r"Dem(ocrat(ic)?)?",
            r"(Jo(e|seph)\s*)?Biden",
            r"(John\s*)?Kerry",
            r"Lisa Monaco",
            r"(Matteo\s*)?Salvini",
            r"Maxine\s*Waters",
            r"(Barac?k )?Obama",
            r"(Nancy )?Pelosi",
            r"Ron\s*Dellums",
            r"Schumer",
            r"(Tim\s*)?Geithner",
            r"Vernon\s*Jordan",
        ],
    ),
    HighlightedNames(
        label='Dubin family',
        style='medium_orchid1',
        patterns=[r"((Celina|Eva( Anderss?on)?|Glenn) )?Dubin"],
        emailers={
            GLENN_DUBIN: "Highbridge Capital Management, married to Epstein's ex-gf Eva",
            EVA: "possibly Epstein's ex-girlfriend (?)",
        },
    ),
    HighlightedNames(
        label='employee',
        style='deep_sky_blue4',
        patterns=[r"Merwin"],
        emailers={
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
        },
    ),
    HighlightedNames(
        label=ENTERTAINER,
        style='light_steel_blue3',
        patterns=[
            r"(Art )?Spiegelman",
            r"Bobby slayton",
            r"bono\s*mick",
            r"Errol(\s*Morris)?",
            r"Etienne Binant",
            r"(Frank\s)?Gehry",
            r"Jagger",
            r"(Jeffrey\s*)?Katzenberg",
            r"(Johnny\s*)?Depp",
            r"Kid Rock",
            r"Lena\s*Dunham",
            r"Madonna",
            r"Mark\s*Burnett",
            r"Ramsey Elkholy",
            r"shirley maclaine",
            r"Steven Gaydos?",
            r"Woody( Allen)?",
            r"Zach Braff",
        ],
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
        patterns=[
            r"(Barry (E. )?)?Krischer",
            r"Kate Kelly",
            r"Kirkland\s*&\s*Ellis",
            r"(Leon\s*)?Jaworski",
            r"Michael J. Pike",
            r"Paul,?\s*Weiss",
            r"Steptoe",
            r"Wein(berg|garten)",
        ],
        emailers={
            'Alan S Halperin': 'partner at Paul, Weiss',
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
            ROBERT_D_CRITTON_JR: CRIMINAL_DEFENSE_ATTORNEY,
            'Robert Gold': None,
            'Roy Black': CRIMINAL_DEFENSE_2008,
            SCOTT_J_LINK: None,
            TONJA_HADDAD_COLEMAN: f'{EPSTEIN_V_ROTHSTEIN_EDWARDS_ATTORNEY}, maybe daughter of Fred Haddad?',
        },
    ),
    HighlightedNames(
        label=ESTATE_EXECUTOR,
        style='purple3 bold',
        category=EPSTEIN_LAWYER,
        emailers={
            DARREN_INDYKE: EPSTEIN_ESTATE_EXECUTOR,
            RICHARD_KAHN: EPSTEIN_ESTATE_EXECUTOR,
        },
    ),
    HighlightedNames(
        label='Europe',
        style='light_sky_blue3',
        patterns=[
            r"(Angela )?Merk(el|le)",
            r"Austria",
            r"(Benjamin\s*)?Harnwell",
            r"Berlin",
            r"Borge",
            r"Boris\s*Johnson",
            r"Brexit(eers?)?",
            r"Brit(ain|ish)",
            r"Brussels",
            r"Cannes",
            r"(Caroline|Jack)?\s*Lang(, Caroline)?",
            r"Cypr(iot|us)",
            r"Davos",
            r"ECB",
            r"England",
            r"EU",
            r"Europe(an)?(\s*Union)?",
            r"Fr(ance|ench)",
            r"Geneva",
            r"Germany?",
            r"Gillard",
            r"Gree(ce|k)",
            r"Ital(ian|y)",
            r"Jacques",
            r"Le\s*Pen",
            r"London",
            r"Macron",
            r"Melusine",
            r"Munich",
            r"(Natalia\s*)?Veselnitskaya",
            r"(Nicholas\s*)?Sarkozy",
            r"Nigel(\s*Farage)?",
            r"Norw(ay|egian)",
            r"Oslo",
            r"Paris",
            r"Polish",
            r"pope",
            r"(Sebastian )?Kurz",
            r"(Vi(c|k)tor\s+)?Orbah?n",
            r"Edward Rod Larsen",
            r"Strasbourg",
            r"Strauss[- ]?Kahn",
            r"Swed(en|ish)(?![-\s]+America)",
            r"Switzerland",
            r"(Tony\s)?Blair",
            r"U\.?K\.?",
            r"Ukrain(e|ian)",
            r"Vienna",
            r"(Vitaly\s*)?Churkin",
            r"Zug",
        ],
        emailers={
            ANDRZEJ_DUDA: 'former president of Poland',
            MIROSLAV_LAJCAK: 'Russia-friendly Slovakian politician, friend of Steve Bannon',
            PETER_MANDELSON: 'UK politics',
            TERJE_ROD_LARSEN: 'Norwegian diplomat',
            THORBJORN_JAGLAND: 'former prime minister of Norway and head of the Nobel Peace Prize Committee',
        },
    ),
    HighlightedNames(
        label='famous lawyer',
        style='medium_purple3',
        patterns=[
            r"(David\s*)?Bo[il]es",
            r"dersh",
            r"(Gloria\s*)?Allred",
            r"(Mi(chael|ke)\s*)?Avenatti",
        ],
        emailers={
            ALAN_DERSHOWITZ: 'Harvard Law School professor and all around (in)famous American lawyer',
            KEN_STARR: 'head of the Monica Lewinsky investigation against Bill Clinton',
        },
    ),
    HighlightedNames(
        label=FINANCE,
        style='green',
        patterns=[
            r"Apollo",
            r"Ari\s*Glass",
            r"Bank",
            r"(Bernie\s*)?Madoff",
            r"Black(rock|stone)",
            r"B\s*of\s*A",
            r"Boothbay(\sFund\sManagement)?",
            r"Chase\s*Bank",
            r"Credit\s*Suisse",
            r"DB",
            r"Deutsche?\s*(Asset|Bank)",
            r"Electron\s*Capital\s*(Partners)?",
            r"Fenner",
            r"FRBNY",
            r"Goldman(\s*Sachs)",
            r"HSBC",
            r"Invesco",
            r"(Janet\s*)?Yellen",
            r"(Jerome\s*)?Powell(?!M\. Cabot)",
            r"(Jimmy\s*)?Cayne",
            r"JPMC?",
            r"j\.?p\.?\s*morgan(\.?com|\s*Chase)?",
            r"Madoff",
            r"Merrill(\s*Lynch)?",
            r"(Michael\s*)?(Cembalest|Milken)",
            r"Mizrahi\s*Bank",
            r"MLPF&S",
            r"((anti.?)?money\s+)?launder(s?|ers?|ing)?(\s+money)?",
            r"Morgan Stanley",
            r"(Peter L. )?Scher",
            r"(Ray\s*)?Dalio",
            r"(Richard\s*)?LeFrak",
            r"Schwartz?man",
            r"Serageldin",
            r"UBS",
            r"us.gio@jpmorgan.com",
        ],
        emailers={
            AMANDA_ENS: 'Citigroup',
            BRAD_WECHSLER: "head of Leon Black's personal investment vehicle according to FT",
            DANIEL_SABBA: 'UBS Investment Bank',
            DAVID_FISZEL: 'CIO Honeycomb Asset Management',
            JES_STALEY: 'former CEO of Barclays',
            JIDE_ZEITLIN: 'former partner at Goldman Sachs, allegations of sexual misconduct',
            'Laurie Cameron': 'currency trading',
            LEON_BLACK: 'Apollo CEO',
            MARC_LEON: 'Luxury Properties Sari Morrocco',
            MELANIE_SPINELLA: 'representative of Leon Black',
            MORTIMER_ZUCKERMAN: 'business partner of Epstein',
            PAUL_BARRETT: None,
            PAUL_MORRIS: DEUTSCHE_BANK,
            'Steven Elkman': DEUTSCHE_BANK,
        },
    ),
    HighlightedNames(
        label='friend',
        style='tan',
        patterns=[
            r"Andrew Farkas",
            r"Thomas\s*(J\.?\s*)?Barrack(\s*Jr)?",
        ],
        emailers={
            DANGENE_AND_JENNIE_ENTERPRISE: 'founders of the members-only CORE club',
            DAVID_STERN: f'emailed Epstein from Moscow, appears to know chairman of {DEUTSCHE_BANK}',
            JONATHAN_FARKAS: "heir to the Alexander's department store fortune",
            'linkspirit': 'Skype username of someone Epstein communicated with',
            'Peter Thomas Roth': 'student of Epstein at Dalton, skincare company founder',
            STEPHEN_HANSON: None,
            TOM_BARRACK: 'long time friend of Trump',
        },
    ),
    HighlightedNames(
        label=HARVARD,
        style='light_goldenrod3',
        patterns=[
            r"Cambridge",
            r"(Derek\s*)?Bok",
            r"Elisa(\s*New)?",
            r"Harvard(\s*(Business|Law|University)(\s*School)?)?",
            r"(Jonathan\s*)?Zittrain",
            r"(Stephen\s*)?Kosslyn",
        ],
        emailers={
            'Donald Rubin': 'Professor of Statistics',
            'Kelly Friendly': 'longtime aide and spokesperson of Larry Summers',
            LARRY_SUMMERS: 'board of Digital Currency Group (DCG), Harvard president, Obama economic advisor',
            'Leah Reis-Dennis': "producer for Lisa New's Poetry in America",
            LISA_NEW: f'professor of poetry, wife of {LARRY_SUMMERS}, AKA "Elisa New"',
            'Lisa Randall': 'theoretical physicist',
            MARTIN_NOWAK: 'professor of mathematics and biology',
            MOSHE_HOFFMAN: 'lecturer and research scholar in behavioral and evolutionary economics',
        },
    ),
    HighlightedNames(
        label='India',
        style='bright_green',
        patterns=[
            r"Abraaj",
            r"Anna\s*Hazare",
            r"(Arif\s*)?Naqvi",
            r"(Arvind\s*)?Kejriwal",
            r"Bangalore",
            r"Hardeep( Pur[ei]e)?",
            r"Indian?",
            r"InsightsPod",
            r"Modi",
            r"Mumbai",
            r"(New\s*)?Delhi",
            r"Tranchulas",
        ],
        emailers={
            ANIL_AMBANI: 'chairman of Reliance Group',
            VINIT_SAHNI: None,
            ZUBAIR_KHAN: 'cybersecurity firm Tranchulas CEO, InsightsPod founder, based in Islamabad and Dubai',
        },
    ),
    HighlightedNames(
        label='Israel',
        style='dodger_blue2',
        patterns=[
            r"AIPAC",
            r"Bibi",
            r"(eh|(Ehud|Nili Priell) )?barak",
            r"Ehud\s*Barack",
            r"Israeli?",
            r"Jerusalem",
            r"J\s*Street",
            r"Mossad",
            r"Netanyahu",
            r"(Sheldon\s*)?Adelson",
            r"Tel\s*Aviv",
            r"(The\s*)?Shimon\s*Post",
            r"Yitzhak",
            r"Rabin",
            r"YIVO",
            r"zionist",
        ],
        emailers={
            EHUD_BARAK: 'former primer minister',
            'Mitchell Bard': 'director of the American-Israeli Cooperative Enterprise (AICE)',
            'Nili Priell Barak': 'wife of Ehud Barak',
        },
    ),
    HighlightedNames(
        label='Japan',
        style='color(168)',
        patterns=[
            r"BOJ",
            r"(Bank\s+of\s+)?Japan(ese)?",
            r"jpy?(?! Morgan)",
            r"SG",
            r"Singapore",
            r"Toky[op]",
        ],
    ),
    HighlightedNames(
        label=JOURNALIST,
        style='bright_yellow',
        patterns=[
            r"Palm\s*Beach\s*(Daily\s*News|Post)",
            r"ABC(\s*News)?",
            r"Alex\s*Yablon",
            r"(Andrew\s*)?Marra",
            r"Arianna(\s*Huffington)?",
            r"(Arthur\s*)?Kretchmer",
            r"BBC",
            r"Bloomberg",
            r"Breitbart",
            r"Charlie\s*Rose",
            r"China\s*Daily",
            r"CNBC",
            r"CNN(politics?)?",
            r"Con[cs]hita",
            r"Sarnoff",
            r"(?<!Virgin[-\s]Islands[-\s])Daily\s*(Beast|Mail|News|Telegraph)",
            r"(David\s*)?Pecker",
            r"David\s*Brooks",
            r"Ed\s*Krassenstein",
            r"(Emily\s*)?Michot",
            r"Ezra\s*Klein",
            r"(George\s*)?Stephanopoulus",
            r"Globe\s*and\s*Mail",
            r"Good\s*Morning\s*America",
            r"Graydon(\s*Carter)?",
            r"Huffington(\s*Post)?",
            r"Ingram, David",
            r"(James\s*)?(Hill|Patterson)",
            r"Jonathan\s*Karl",
            r"Julie\s*(K.?\s*)?Brown",
            r"(Katie\s*)?Couric",
            r"Keith\s*Larsen",
            r"L\.?A\.?\s*Times",
            r"Miami\s*Herald",
            r"(Michele\s*)?Dargan",
            r"(National\s*)?Enquirer",
            r"(The\s*)?N(ew\s*)?Y(ork\s*)?(P(ost)?|T(imes)?)",
            r"(The\s*)?New\s*Yorker",
            r"NYer",
            r"PERVERSION\s*OF\s*JUSTICE",
            r"Politico",
            r"Pro\s*Publica",
            r"(Sean\s*)?Hannity",
            r"Sulzberger",
            r"SunSentinel",
            r"Susan Edelman",
            r"(Uma\s*)?Sanghvi",
            r"(The\s*)?Wa(shington\s*)?Po(st)?",
            r"Viceland",
            r"Vick[iy]\s*Ward",
            r"Vox",
            r"WGBH",
            r"(The\s*)?Wall\s*Street\s*Journal",
            r"WSJ",
            r"[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk",
        ],
        emailers={
            EDWARD_JAY_EPSTEIN: 'reporter who wrote about the kinds of crimes Epstein was involved in, no relation to Jeffrey',
            JAMES_HILL: 'ABC News',
            JENNIFER_JACQUET: 'Future Science',
            JOHN_BROCKMAN: 'literary agent and author specializing in scientific literature',
            LANDON_THOMAS: 'New York Times',
            MICHAEL_WOLFF: 'Author of "Fire and Fury: Inside the Trump White House"',
            PAUL_KRASSNER: '60s counterculture guy',
            'Tim Zagat': 'Zagat restaurant guide CEO',
        },
    ),
    HighlightedNames(
        label='Latin America',
        style='yellow',
        patterns=[
            r"Argentin(a|ian)",
            r"Bolsonar[aio]",
            r"Bra[sz]il(ian)?",
            r"Bukele",
            r"Caracas",
            r"Castro",
            r"Colombian?",
            r"Cuban?",
            r"El\s*Salvador",
            r"((Enrique )?Pena )?Nieto",
            r"LatAm",
            r"Lula",
            r"Mexic(an|o)",
            r"(Nicolas\s+)?Maduro",
            r"Panama( Papers)?",
            r"Peru",
            r"Venezuelan?",
            r"Zambrano",
        ],
    ),
    HighlightedNames(
        label='law enforcement',
        style='color(24) bold',
        patterns=[
            r"ag",
            r"(Alicia\s*)?Valle",
            r"AML",
            r"(Andrew\s*)?McCabe",
            r"((Bob|Robert)\s*)?Mueller",
            r"(Byung\s)?Pak",
            r"CFTC?",
            r"CIA",
            r"CIS",
            r"CVRA",
            r"Dep(artmen)?t\.?\s*of\s*(the\s*)?(Justice|Treasury)",
            r"DHS",
            r"DOJ",
            r"FBI",
            r"FCPA",
            r"FDIC",
            r"Federal\s*Bureau\s*of\s*Investigation",
            r"FinCEN",
            r"FINRA",
            r"FOIA",
            r"FTC",
            r"IRS",
            r"(James\s*)?Comey",
            r"(Jennifer\s*Shasky\s*)?Calvery",
            r"((Judge|Mark)\s*)?(Carney|Filip)",
            r"(Kirk )?Blouin",
            r"KYC",
            r"NIH",
            r"NS(A|C)",
            r"OCC",
            r"OFAC",
            r"(Lann?a\s*)?Belohlavek",
            r"(Michael\s*)?Reiter",
            r"OGE",
            r"Office\s*of\s*Government\s*Ethics",
            r"Police Code Enforcement",
            r"(Preet\s*)?Bharara",
            r"SCOTUS",
            r"SD(FL|NY)",
            r"SEC",
            r"Secret\s*Service",
            r"Securities\s*and\s*Exchange\s*Commission",
            r"Southern\s*District\s*of\s*(Florida|New\s*York)",
            r"State\s*Dep(artmen)?t",
            r"Strzok",
            r"Supreme\s*Court",
            r"Treasury\s*(Dep(artmen)?t|Secretary)",
            r"TSA",
            r"USAID",
            r"(William\s*J\.?\s*)?Zloch",
        ],
        emailers={
            ANN_MARIE_VILLAFANA: 'southern district of Florida U.S. Attorney',
            DANNY_FROST: 'Director of Communications at Manhattan DA',
        },
    ),
    HighlightedNames(
        label=LOBBYIST,
        style='light_coral',
        patterns=[
            r"[BR]ob Crowe",
            r"CSIS",
            r"(Kevin\s*)?Rudd",
            r"Stanley Rosenberg",
        ],
        emailers={
            'Joshua Cooper Ramo': 'co-CEO of Henry Kissinger Associates',
            KATHERINE_KEATING: 'Daughter of former Australian PM',
            MOHAMED_WAHEED_HASSAN: 'former president of the Maldives',
            OLIVIER_COLOM: 'France',
            'Paul Keating': 'former PM of Australia',
            PUREVSUREN_LUNDEG: 'Mongolian ambassador to the UN',
            'Stanley Rosenberg': 'former President of the Massachusetts Senate',
        },
    ),
    HighlightedNames(
        label='mideast',
        style='dark_sea_green4',
        patterns=[
            r"Abdulmalik Al-Makhlafi",
            r"Abdullah",
            r"Abu\s+Dhabi",
            r"Afghanistan",
            r"Al[-\s]?Qa[ei]da",
            r"Ahmadinejad",
            r"Arab",
            r"Aramco",
            r"Assad",
            r"Ayatollah",
            r"Bahrain",
            r"Basiji?",
            r"Benghazi",
            r"Cairo",
            r"Chagoury",
            r"Dj[iu]bo?uti",
            r"Doha",
            r"[DB]ubai",
            r"Egypt(ian)?",
            r"Emir(at(es?|i))?",
            r"Erdogan",
            r"Fashi",
            r"Gaddafi",
            r"(Hamid\s*)?Karzai",
            r"Hamad\s*bin\s*Jassim",
            r"HBJ",
            r"Houthi",
            r"Imran\s+Khan",
            r"Iran(ian)?",
            r"Isi[ls]",
            r"Islam(abad|ic|ist)?",
            r"Istanbul",
            r"Kh?ashoggi",
            r"(Kairat\s*)?Kelimbetov",
            r"kasshohgi",
            r"Kaz(akh|ich)stan",
            r"Kazakh?",
            r"Kh[ao]menei",
            r"Khalid\s*Sheikh\s*Mohammed",
            r"KSA",
            r"Leban(ese|on)",
            r"Libyan?",
            r"Mahmoud",
            r"Marra[hk]e[cs]h",
            r"MB(N|S|Z)",
            r"Mid(dle)?\s*East",
            r"Mohammed\s+bin\s+Salman",
            r"Morocco",
            r"Mubarak",
            r"Muslim",
            r"Nayaf",
            r"Pakistani?",
            r"Omar",
            r"(Osama\s*)?Bin\s*Laden",
            r"Osama(?! al)",
            r"Palestin(e|ian)",
            r"Persian?",
            r"Riya(dh|nd)",
            r"Saddam",
            r"Salman",
            r"Saudi(\s+Arabian?)?",
            r"Shariah?",
            r"SHC",
            r"sheikh",
            r"shia",
            r"(Sultan\s*)?Yacoub",
            r"Syrian?",
            r"(Tarek\s*)?El\s*Sayed",
            r"Tehran",
            r"Tunisian?",
            r"Turk(ey|ish)",
            r"UAE",
            r"((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        ],
        emailers={
            ANAS_ALRASHEED: 'former information minister of Kuwait (???)',
            AZIZA_ALAHMADI: 'Abu Dhabi Department of Culture & Tourism',
            RAAFAT_ALSABBAGH: 'Saudi royal advisor',
            SHAHER_ABDULHAK_BESHER: 'Yemeni billionaire',
        },
    ),
    HighlightedNames(
        label='modeling',
        style='pale_violet_red1',
        patterns=[
            r"\w+@mc2mm.com",
            r"model(ed|ing)",
            r"(Nicole\s*)?Junkerman",
        ],
        emailers={
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
        },
    ),
    HighlightedNames(
        label=PUBLICIST,
        style='orange_red1',
        patterns=[
            r"(Matt(hew)? )?Hiltzi[gk]",
            REPUTATION_MGMT,
        ],
        emailers={
            AL_SECKEL: 'husband of Isabel Maxwell, Mindshift conference organizer who fell off a cliff',
            'Barnaby Marsh': 'co-founder of Saint Partners, a philanthropy services company',
            CHRISTINA_GALBRAITH: f"{REPUTATION_MGMT}, worked on Epstein's Google search results with Tyler Shears",
            IAN_OSBORNE: f'{OSBORNE_LLP} reputation repairer possibly hired by Epstein ca. 2011-06',
            MICHAEL_SITRICK: 'crisis PR',
            'Owen Blicksilver': 'OBPR, Inc.',
            PEGGY_SIEGAL: 'socialite',
            'R. Couri Hay': None,
            ROSS_GOW: 'Acuity Reputation Management',
            TYLER_SHEARS: f"{REPUTATION_MGMT}, worked on Epstein's Google search results with Christina Galbraith",
        },
    ),
    HighlightedNames(
        label='Republicans',
        style='dark_red bold',
        patterns=[
            r"Alberto\sGonzale[sz]",
            r"(Alex\s*)?Acosta",
            r"(Bill\s*)?Barr",
            r"Bill\s*Shine",
            r"(Bob\s*)?Corker",
            r"(Brett\s*)?Kavanaugh",
            r"Broidy",
            r"(Chris\s)?Christie",
            r"Devin\s*Nunes",
            r"(Don\s*)?McGa[hn]n",
            r"McMaster",
            r"Fox\s*News",
            r"(George\s*)?Nader",
            r"GOP",
            r"(John\s*(R.?\s*)?)Bolton",
            r"Kissinger",
            r"Kobach",
            r"Kolfage",
            r"Kudlow",
            r"Lewandowski",
            r"(Marco\s)?Rubio",
            r"(Mark\s*)Meadows",
            r"Mattis",
            r"McCain",
            r"(?<!Merwin Dela )Cruz",
            r"(Michael\s)?Hayden",
            r"((General|Mike)\s*)?(Flynn|Pence)",
            r"(Mitt\s*)?Romney",
            r"Mnuchin",
            r"Nikki",
            r"Haley",
            r"(Paul\s+)?(Manafort|Volcker)",
            r"(Peter\s)?Navarro",
            r"Pompeo",
            r"Reagan",
            r"Reince",
            r"Priebus",
            r"Republican",
            r"(Rex\s*)?Tillerson",
            r"(?<!Cynthia )(Richard\s*)?Nixon",
            r"Sasse",
            r"Tea\s*Party",
        ],
        emailers={
            RUDY_GIULIANI: None,
            TULSI_GABBARD: None,
        },
    ),
    HighlightedNames(
        label='Rothschild family',
        style='indian_red',
        emailers={
            ARIANE_DE_ROTHSCHILD: 'heiress',
            JOHNNY_EL_HACHEM: f'works with {ARIANE_DE_ROTHSCHILD}',
        },
    ),
    HighlightedNames(
        label='Russia',
        style='red bold',
        patterns=[
            r"Alfa\s*Bank",
            r"Anya\s*Rasulova",
            r"Chernobyl",
            r"Day\s+One\s+Ventures",
            r"(Dmitry\s)?(Kiselyov|(Lana\s*)?Pozhidaeva|Medvedev|Rybolo(o?l?ev|vlev))",
            r"Dmitry",
            r"FSB",
            r"GRU",
            r"KGB",
            r"Kislyak",
            r"Kremlin",
            r"Kuznetsova",
            r"Lavrov",
            r"Lukoil",
            r"Moscow",
            r"(Oleg\s*)?Deripaska",
            r"Oleksandr Vilkul",
            r"Rosneft",
            r"RT",
            r"St.?\s*?Petersburg",
            r'Svet',
            r"Russian?",
            r"Sberbank",
            r"Soviet(\s*Union)?",
            r"USSR",
            r"Vladimir",
            r"(Vladimir\s*)?(Putin|Yudashkin)",
            r"Women\s*Empowerment",
            r"Xitrans",
        ],
        emailers={
            'Dasha Zhukova': 'art collector, daughter of Alexander Zhukov',
            MASHA_DROKOVA: 'silicon valley VC, former Putin Youth',
            RENATA_BOLOTOVA: 'former aspiring model, now fund manager at New York State Insurance Fund',
            SVETLANA_POZHIDAEVA: "Epstein's Russian assistant who was recommended for a visa by Sergei Belyakov (FSB) and David Blaine",
        },
    ),
    HighlightedNames(
        label=ACADEMIA,
        style='light_goldenrod2',
        patterns=[
            r"Alain Forget",
            r"Brotherton",
            r"Carl\s*Sagan",
            r"Columbia",
            r"David Grosof",
            r"J(ames|im)\s*Watson",
            r"(Lord\s*)?Martin\s*Rees",
            r"Massachusetts\s*Institute\s*of\s*Technology",
            r"MIT(\s*Media\s*Lab)?",
            r"Media\s*Lab",
            r"Minsky",
            r"((Noam|Valeria)\s*)?Chomsky",
            r"Norman\s*Finkelstein",
            r"Praluent",
            r"Regeneron",
            r"(Richard\s*)?Dawkins",
            r"Sanofi",
            r"Stanford",
            r"(Stephen\s*)?Hawking",
            r"(Steven?\s*)?Pinker",
            r"UCLA",
        ],
        emailers={
            DAVID_HAIG: 'evolutionary geneticist?',
            JOSCHA_BACH: 'cognitive science / AI research',
            'Daniel Kahneman': 'Nobel economic sciences laureate and cognitivie psychologist (?)',
            'Ed Boyden': f'Associate Professor, {MIT_MEDIA_LAB} neurobiology',
            LAWRENCE_KRAUSS: 'theoretical physicist',
            LINDA_STONE: f'ex-Microsoft, {MIT_MEDIA_LAB}',
            MARK_TRAMO: 'professor of neurology at UCLA',
            'Nancy Dahl': 'wife of Lawrence Krauss',
            NEAL_KASSELL: 'professor of neurosurgery at University of Virginia',
            PETER_ATTIA: 'longevity medicine',
            ROBERT_TRIVERS: 'evolutionary biology',
            ROGER_SCHANK: 'Teachers College, Columbia University',
        },
    ),
    HighlightedNames(
        label='southeast Asia',
        style='light_salmon3 bold',
        patterns=[
            r"Bangkok",
            r"Burm(a|ese)",
            r"Cambodian?",
            r"Laos",
            r"Malaysian?",
            r"Myan?mar",
            r"Thai(land)?",
            r"Vietnam(ese)?",
        ],
    ),
    HighlightedNames(
        label='tech bro',
        style='bright_cyan',
        patterns=[
            r"AG?I",
            r"Chamath",
            r"Palihapitiya",
            r"Danny\s*Hillis",
            r"Drew\s*Houston",
            r"Eric\s*Schmidt",
            r"Greylock(\s*Partners)?",
            r"(?<!(ustin|Moshe)\s)Hoffmand?",
            r"LinkedIn",
            r"(Mark\s*)?Zuckerberg",
            r"Masa(yoshi)?(\sSon)?",
            r"Najeev",
            r"Nathan\s*Myhrvold",
            r"Palantir",
            r"(Peter\s)?Th(ie|ei)l",
            r"Pierre\s*Omidyar",
            r"Sergey\s*Brin",
            r"Silicon\s*Valley",
            r"Softbank",
            r"SpaceX",
            r"Tim\s*Ferriss?",
            r"WikiLeak(ed|s)",
        ],
        emailers={
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
        patterns=[
            r"@?realDonaldTrump",
            r"(Alan\s*)?Weiss?elberg",
            r"\bDJ?T\b",
            r"Donald J. Tramp",
            r"(Donald\s+(J\.\s+)?)?Trump(ism|\s*Properties)?",
            r"Don(ald| *Jr)(?! Rubin)",
            r"Ivank?a",
            r"Jared",
            r"Kushner",
            r"(Madeleine\s*)?Westerhout",
            r"Mar[-\s]*a[-\s]*Lago",
            r"(Marla\s*)?Maples",
            r"(Matt(hew)? )?Calamari",
            r"\bMatt C\b",
            r"Melania",
            r"(Michael (J.? )?)?Boccio",
            r"Rebekah\s*Mercer",
            r"Roger\s+Stone",
            r"rona",
            r"(The\s*)?Art\s*of\s*the\s*Deal",
        ],
        emailers={
            'Bruce Moskowitz': "'Trump's health guy' according to Epstein",
        },
    ),
    HighlightedNames(
        label='victim',
        style='orchid1',
        patterns=[
            r"(Jane|Tiffany)\s*Doe",
            r"Katie\s*Johnson",
            r"(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre",
            r"Virginia\s+Roberts",
        ],
    ),
    HighlightedNames(
        label='victim lawyer',
        style='dark_magenta bold',
        patterns=[
            r"(Alan(\s*P.)?|MINTZ)\s*FRAADE",
            r"Paul\s*(G.\s*)?Cassell",
            r"Rothstein\s*Rosenfeldt\s*Adler",
            r"(Scott\s*)?Rothstein",
            r"(J\.?\s*)?(Stan(ley)?\s*)?Pottinger",
        ],
        emailers={
            BRAD_EDWARDS: 'Rothstein Rosenfeldt Adler (Rothstein was a crook & partner of Roger Stone)',
            JACK_SCAROLA: 'Searcy Denney Scarola Barnhart & Shipley',
        },
    ),
    HighlightedNames(
        label=VIRGIN_ISLANDS,
        style='sea_green1',
        patterns=[
            r"Antigua",
            r"Bahamas",
            r"BVI",
            r"Caribb?ean",
            r"Dominican\s*Republic",
            r"(Great|Little)\s*St.?\s*James",
            r"Haiti(an)?",
            r"(John\s*)deJongh(\s*Jr\.?)",
            r"(Kenneth E\. )?Mapp",
            r"Palm\s*Beach(?!\s*Post)",
            r"PBI",
            r"S(ain)?t.?\s*Thomas",
            r"USVI",
            r"(?<!Epstein )VI",
            r"(The\s*)?Virgin\s*Islands(\s*Daily\s*News)?",
        ],
        emailers={
            CECILE_DE_JONGH: 'first lady 2007-2015',
            KENNETH_E_MAPP: 'Governor',
            STACEY_PLASKETT: 'non-voting member of Congress',
        },
    ),
    HighlightedNames(
        label=BILL_GATES,
        style='turquoise4',
        patterns=[
            r"BG",
            r"b?g?C3",
            r"(Bill\s*((and|or)\s*Melinda\s*)?)?Gates",
            r"Melinda(\s*Gates)?",
            r"Microsoft",
            r"MSFT",
        ],
        emailers={
            BORIS_NIKOLIC: f'biotech VC partner of {BILL_GATES}, {EPSTEIN_ESTATE_EXECUTOR}',
        },
    ),
    HighlightedNames(
        label=STEVE_BANNON,
        style='color(58)',
        patterns=[
            r"(American\s*)?Dharma",
            r"((Steve|Sean)\s*)?Bannon?",
        ],
        emailers={
            STEVE_BANNON: "Trump campaign manager, memecoin grifter, convicted criminal",
        },
    ),
    HighlightedNames(
        style='gold3',
        patterns=[r"(steven?\s*)?hoffenberg?w?"],
        emailers={
            STEVEN_HOFFENBERG: HEADER_ABBREVIATIONS['Hoffenberg'],
        },
    ),
    HighlightedNames(emailers={GHISLAINE_MAXWELL: None}, patterns=[r"gmax(1@ellmax.com)?", r"TerraMar"], style='deep_pink3'),
    HighlightedNames(emailers={JABOR_Y: '"an influential man in Qatar"'}, style='spring_green1'),
    HighlightedNames(
        style='blue1',
        patterns=[
            r"JEGE",
            r"LSJ",
            r"Mark (L. )?Epstein",
        ],
        emailers={
            JEFFREY_EPSTEIN: None,
        },
    ),
    HighlightedNames(emailers={JOI_ITO: HEADER_ABBREVIATIONS['Joi']}, style='gold1'),
    HighlightedNames(emailers={KATHRYN_RUEMMLER: 'former Obama legal counsel'}, style='magenta2'),
    HighlightedNames(emailers={MELANIE_WALKER: 'doctor'}, style='pale_violet_red1'),
    HighlightedNames(emailers={PAULA: "Epstein's ex-girlfriend who is now in the opera world"}, label='paula_heil_fisher', style='pink1'),
    HighlightedNames(emailers={PRINCE_ANDREW: 'British royal family'}, style='dodger_blue1'),
    HighlightedNames(emailers={SOON_YI_PREVIN: 'wife of Woody Allen'}, style='hot_pink'),
    HighlightedNames(emailers={SULTAN_BIN_SULAYEM: 'CEO of DP World, chairman of ports in Dubai'}, style='green1'),

    # HighlightedText not HighlightedNames bc of word boundary issue
    HighlightedText(
        label='unknown',
        style='cyan',
        patterns=[r'\(unknown\)']
    ),
    HighlightedText(
        label='phone_number',
        style='bright_green',
        patterns=[
            r"\+?(1?\(?\d{3}\)?[- ]\d{3}[- ]\d{4}|\d{2}[- ]\(?0?\)?\d{2}[- ]\d{4}[- ]\d{4})",
            r"(\b|\+)[\d+]{10,12}\b",
        ],
    ),
]

# Highlight regexes for things other than names, only used by RegexHighlighter pattern matching
HIGHLIGHTED_TEXTS = [
    HighlightedText(
        label='header_field',
        style='plum4',
        patterns=[r'^(Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):'],
    ),
    HighlightedText(
        label='http_links',
        style=f'{ARCHIVE_LINK_COLOR} underline',
        patterns=[r"https?:[^\s]+"],
    ),
    HighlightedText(
        label='quoted_reply_line',
        style='dim',
        patterns=[REPLY_REGEX.pattern],
    ),
    HighlightedText(
        label='redacted',
        style='grey58',
        patterns=[fr"{REDACTED}|Privileged - Redacted"],
    ),
    HighlightedText(
        label='sent_from',
        style='gray42 italic',
        patterns=[SENT_FROM_REGEX.pattern],
    ),
    HighlightedText(
        label='snipped_signature',
        style='gray19',
        patterns=[r'<\.\.\.(snipped|trimmed).*\.\.\.>'],
    ),
    HighlightedText(
        label='timestamp_2',
        style=TIMESTAMP_STYLE,
        patterns=[r"\d{1,4}[-/]\d{1,2}[-/]\d{2,4} \d{1,2}:\d{2}:\d{2}( [AP]M)?"],
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


def _print_highlighted_names_repr() -> None:
    for hn in HIGHLIGHTED_NAMES:
        if isinstance(hn, HighlightedNames):
            print(indented(repr(hn)) + ',')

    import sys
    sys.exit()
