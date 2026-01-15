import json
import re
from collections import defaultdict
from dataclasses import dataclass, field

from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.text import Text

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import ARCHIVE_LINK_COLOR
from epstein_files.util.constants import (EMAILER_ID_REGEXES, EPSTEIN_V_ROTHSTEIN_EDWARDS,
     OSBORNE_LLP, REPLY_REGEX, SENT_FROM_REGEX)
from epstein_files.util.data import sort_dict, without_falsey
from epstein_files.util.doc_cfg import *
from epstein_files.util.env import args
from epstein_files.util.logging import logger

CIVIL_ATTORNEY = 'civil attorney'
CRIMINAL_DEFENSE_ATTORNEY = 'criminal defense attorney'
CRIMINAL_DEFENSE_2008 = f"{CRIMINAL_DEFENSE_ATTORNEY} on 2008 case"
EPSTEIN_LAWYER = 'lawyer'
EPSTEIN_V_ROTHSTEIN_EDWARDS_ATTORNEY = f"{CIVIL_ATTORNEY} {EPSTEIN_V_ROTHSTEIN_EDWARDS}"
ESTATE_EXECUTOR = 'estate executor'
EPSTEIN_ESTATE_EXECUTOR = f"Epstein {ESTATE_EXECUTOR}"
MC2_MODEL_MANAGEMENT = f"{JEAN_LUC_BRUNEL}'s MC2 Model Management"
MIDEAST = 'mideast'
QUESTION_MARKS_TXT = Text(QUESTION_MARKS, style='grey50')
REGEX_STYLE_PREFIX = 'regex'
SIMPLE_NAME_REGEX = re.compile(r"^[-\w, ]+$", re.IGNORECASE)
TECH_BRO = 'tech bro'

CATEGORY_STYLE_MAPPING = {
    ARTICLE: JOURNALIST,
    BOOK: JOURNALIST,
    LEGAL: EPSTEIN_LAWYER,
    POLITICS: LOBBYIST,
    PROPERTY: BUSINESS,
    REPUTATION: PUBLICIST,
}

CATEGORY_STYLES = {
    JSON: 'dark_red',
    'letter': 'medium_orchid1'
}

debug_console = Console(color_system='256')


@dataclass(kw_only=True)
class BaseHighlight:
    """
    Regex and style information for things we want to highlight.

    Attributes:
        label (str): RegexHighlighter match group name
        pattern (str): regex pattern identifying strings matching this group
        style (str): Rich style to apply to text matching this group
        theme_style_name (str): The style name that must be a part of the rich.Console's theme
    """
    label: str = ''
    regex: re.Pattern = field(init=False)
    style: str
    theme_style_name: str = field(init=False)
    _capture_group_label: str = field(init=False)
    _match_group_var: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            raise ValueError(f'Missing label for {self}')

        self._capture_group_label = self.label.lower().replace(' ', '_').replace('-', '_')
        self._match_group_var = fr"?P<{self._capture_group_label}>"
        self.theme_style_name = f"{REGEX_STYLE_PREFIX}.{self._capture_group_label}"


@dataclass(kw_only=True)
class HighlightedText(BaseHighlight):
    """
    Color highlighting for things other than people's names (e.g. phone numbers, email headers).

    Attributes:
        label (str): RegexHighlighter match group name, defaults to 1st 'emailers' key if only 1 emailer provided
        patterns (list[str]): regex patterns identifying strings matching this group
    """
    patterns: list[str] = field(default_factory=list)
    _pattern: str = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        if not self.label:
            raise ValueError(f"No label provided for {repr(self)}")

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
    should_match_first_last_name: bool = True

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

    def category_str(self) -> str:
        if self.category:
            return self.category
        elif len(self.emailers) == 1 and self.label == [k for k in self.emailers.keys()][0]:
            return ''
        else:
            return self.label.replace('_', ' ')

    def info_for(self, name: str, include_category: bool = False) -> str | None:
        """Label and additional info for 'name' if 'name' is in self.emailers."""
        info_pieces = [self.category_str()] if include_category else []
        info_pieces.append(self.emailers.get(name) or '')
        info_pieces = without_falsey(info_pieces)
        return ', '.join(info_pieces) if info_pieces else None

    def _emailer_pattern(self, name: str) -> str:
        """Pattern matching 'name'. Extends value in EMAILER_ID_REGEXES with first/last name if it exists."""
        if not self.should_match_first_last_name:
            return name

        if name in EMAILER_ID_REGEXES:
            name_patterns = [EMAILER_ID_REGEXES[name].pattern]
        else:
            name_patterns = [remove_question_marks(name).replace(' ', r"\s+")]

        if ' ' in name:
            for partial_name in [reversed_name(name), extract_first_name(name), extract_last_name(name)]:  # Order matters
                if partial_name.lower() not in NAMES_TO_NOT_HIGHLIGHT and SIMPLE_NAME_REGEX.match(partial_name):
                    name_patterns.append(partial_name.replace(' ', r"\s+"))

        pattern = '|'.join(name_patterns)

        if args.deep_debug:
            debug_console.print(Text('').append(f"{name:25s}", style=self.style).append(f" '{pattern}'", style='dim'))

        return pattern

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


@dataclass(kw_only=True)
class ManualHighlight(BaseHighlight):
    """For when you can't construct the regex."""
    pattern: str

    def __post_init__(self):
        super().__post_init__()

        if self._match_group_var not in self.pattern:
            raise ValueError(f"Label '{self.label}' must appear in regex pattern '{self.pattern}'")

        self.regex = re.compile(self.pattern, re.MULTILINE)


HIGHLIGHTED_NAMES = [
    # This has to come first to get both stylings applied to the email subjects
    ManualHighlight(
        label='email_subject',
        style='light_yellow3',
        pattern=r"^(> )?(Classification|Flag|Subject): (?P<email_subject>.*)",
    ),
    HighlightedNames(
        label=ACADEMIA,
        style='light_goldenrod2',
        emailers={
            'Daniel Kahneman': 'Nobel economic sciences laureate and cognitivie psychologist (?)',
            DAVID_HAIG: 'evolutionary geneticist?',
            'David Grosof': 'MIT Sloan School of Management',
            'Ed Boyden': f'{MIT_MEDIA_LAB} neurobiology professor',
            'Harry Fisch': "men's health expert at New York-Presbyterian / Weill Cornell (?)",
            JOSCHA_BACH: 'cognitive science / AI research',
            LAWRENCE_KRAUSS: 'theoretical physicist with #MeToo problems',
            LINDA_STONE: f'ex-Microsoft, {MIT_MEDIA_LAB}',
            MARK_TRAMO: 'professor of neurology at UCLA',
            'Nancy Dahl': f'wife of {LAWRENCE_KRAUSS}',
            NEAL_KASSELL: 'professor of neurosurgery at University of Virginia',
            NOAM_CHOMSKY: f"professor of linguistics at MIT",
            'Norman Finkelstein': 'scholar, well known critic of Israel',
            PETER_ATTIA: 'longevity medicine',
            ROBERT_TRIVERS: 'evolutionary biology',
            ROGER_SCHANK: 'Teachers College, Columbia University',
            'Valeria Chomsky': f"wife of {NOAM_CHOMSKY}",
        },
        patterns=[
            r"Andy\s*Lippman",  # Media Lab
            r"Arizona\s*State\s*University",
            r"Bard\s+((Early )?College|High School|Schools)",
            r"Brotherton",
            r"Carl\s*Sagan",
            r"Columbia",
            r"Dan(iel|ny) Kahneman",
            r"(Francis\s*)?Crick",
            r"J(ames|im)\s*Watson",
            r"(Lord\s*)?Martin\s*Rees",
            r"Massachusetts\s*Institute\s*of\s*Technology",
            r"Media\s*Lab",
            r"(Marvin\s*)?Minsky",
            r"MIT(\s*Media\s*Lab)?",
            r"Norman\s*Finkelstein",
            r"Oxford(?! Analytica)",
            r"Praluent",
            r"Princeton(\s*University)?",
            r"Regeneron",
            r"(Richard\s*)?Dawkins",
            r"(Sandy\s*)?Pentland",  # Media Lab
            r"Sanofi",
            r"Stanford(\s*University)?(\s*Hospital)?",
            r"(Stephen\s*)?Hawking",
            r"(Steven?\s*)?Pinker",
            r"Texas\s*A&M",
            r"Tulane",
            r"UCLA",
        ],
    ),
    HighlightedNames(
        label='Africa',
        style='light_pink4',
        emailers={
            'Abdoulaye Wade': "former president of Senegal, father of Karim Wade",
            'Ivan Glasenberg': "South African former CEO of Glencore, one of the world's largest commodity trading and mining companies",
            'Karim Wade': 'son of the president of Senegal, facing arrest for corruption, email handle is "Afri zp"',
            'Miles Alexander': 'Operations Manager Michaelhouse Balgowan KwaZulu-Natal South Africa',
            'Macky Sall': 'prime minister of Senegal, defeated Abdoulaye Wade',
        },
        patterns=[
            r"Buhari",
            r"Econet(\s*Wireless)",
            r"Ethiopian?",
            r"Ghana(ian)?",
            r"Glencore",
            r"Goodluck Jonathan",
            r"Johannesburg",
            r"Kenyan?",
            r"Nigerian?",
            r"Okey Enelamah",
            r"(Paul\s*)?Kagame",
            r"Rwandan?",
            r"Senegal(ese)?",
            r"Serengeti",
            r"(South\s*)?African?",
            r"(Strive\s*)?Masiyiwa",
            r"Tanzanian?",
            r"Ugandan?",
            r"(Yoweri\s*)?Museveni",
            r"Zimbabwe(an)?",
        ],
    ),
    HighlightedNames(
        label=ARTS,
        style='light_steel_blue3',
        emailers={
            ANDRES_SERRANO: "'Piss Christ' artist",
            'Barry Josephson': 'American film producer, editor FamilySecurityMatters.org',
            BILL_SIEGEL: 'documentary film producer and director',
            DAVID_BLAINE: 'famous magician',
            'David Brenner': 'American comedian and actor',
            'Richard Merkin': 'painter, illustrator and arts educator',
            STEVEN_PFEIFFER: 'Associate Director at Independent Filmmaker Project (IFP)',
            'Steven Gaydos': 'American screenwriter and journalist',
        },
        patterns=[
            r"(Art )?Spiegelman",
            r"Artspace",
            r"Bobby slayton",
            r"bono\s*mick",
            r"Errol(\s*Morris)?",
            r"Etienne Binant",
            r"(Frank\s)?Gehry",
            r"Harvey\s*Weinstein", r"wientstein", r"Weinstein\s*Co(s?|mpany)",
            r"IFP",
            r"Independent\s*Filmmaker\s*Project",
            r"Jagger",
            r"(Jeffrey\s*)?Katzenberg",
            r"(Johnny\s*)?Depp",
            r"Kid Rock",
            r"(Larry\s*)?Gagosian",
            r"Lena\s*Dunham",
            r"Madonna",
            r"Mark\s*Burnett",
            r"New York Film Festival",
            r"Peter Getzels",
            r"Phaidon",
            r"Ramsey Elkholy",
            r"Regan arts",
            r"shirley maclaine",
            r"Woody( Allen)?",
            r"Zach Braff",
        ],
    ),
    HighlightedNames(
        label=BILL_GATES,
        style='turquoise4',
        category=TECH_BRO,
        emailers={
            BILL_GATES: 'ex-Microsoft, Gates Foundation, bgC3',
            BORIS_NIKOLIC: f'biotech VC partner of {BILL_GATES}, {EPSTEIN_ESTATE_EXECUTOR}',
        },
        patterns=[
            r"BG",
            r"b?g?C3",
            r"(Bill\s*((and|or|&)\s*Melinda\s*)?)?Gates(\s*Foundation)?",
            r"Kofi\s*Rashid",
            r"Melinda(\s*Gates)?",
            r"Microsoft",
            r"MSFT",
        ],
    ),
    HighlightedNames(
        label='bitcoin',
        style='orange1 bold',
        emailers={
            JEFFREY_WERNICK: 'former COO of Parler, involved in numerous crypto companies like Bitforex',
            JEREMY_RUBIN: 'developer/researcher',
            JOI_ITO: f"former head of {MIT_MEDIA_LAB} and MIT Digital Currency Initiative",
            ANTHONY_SCARAMUCCI: 'Skybridge Capital, FTX investor',
        },
        patterns=[
            r"Balaji",
            r"bitcoin(\s*Foundation)?",
            r"block ?chain(\s*capital)?",
            r"Brian Forde",
            r"Brock(\s*Pierce)?",
            r"coins?",
            r"Cory\s*Fields",  # bitcoin dev
            r"cr[iy]?pto(currenc(y|ies))?",
            r"Digital\s*Currenc(ies|y)(\s*Initiative)?",
            r"e-currency",
            r"(Gavin )?Andress?en",  # bitcoin dev
            r"(Howard\s+)?Lutnic?k",
            r"(Jim\s*)Pallotta",  # Media lab advisory board
            r"Libra",
            r"Madars",
            r"Mi(chael|ke)\s*Novogratz",
            r"(Patrick\s*)?Murck",
            r"Ron Rivest",
            r"(Ross\s*)?Ulbricht",
            r"Silk\s*Road",
            r"SpanCash",
            r"Tether",
            r"virtual\s*currenc(ies|y)",
            r"Wladimir( van der Laan)?",  # bitcoin dev
            r"(zero\s+knowledge\s+|zk)pro(of|tocols?)",
        ],
    ),
    HighlightedNames(
        label=BUSINESS,
        style='spring_green4',
        emailers={
            ALIREZA_ITTIHADIEH: 'CEO Freestream Aircraft Limited',
            BARBRO_C_EHNBOM: 'Swedish pharmaceuticals, SALSS',
            BARRY_J_COHEN: None,
            'David Mitchell': 'Mitchell Holdings, New York real estate developer',
            GERALD_BARTON: "Maryland property developer Landmark Land Company",
            GORDON_GETTY: 'heir to oil tycoon J. Paul Getty',
            'Philip Kafka': 'president of Prince Concepts (and son of Terry Kafka?)',
            ROBERT_LAWRENCE_KUHN: 'investment banker, China expert',
            TERRY_KAFKA: 'CEO of Impact Outdoor (highway billboards)',
            TOM_PRITZKER: 'chairman of The Pritzker Organization and Hyatt Hotels',
        },
        patterns=[
            r"((Bill|David)\s*)?Koch(\s*(Bro(s|thers)|Industries))?",
            r"Gruterite",
            r"((John|Patricia)\s*)?Kluge",
            r"Marc Rich",
            r"(Mi(chael|ke)\s*)?Ovitz",
            r"(Steve\s+)?Wynn",
            r"(Les(lie)?\s+)?Wexner",
            r"New Leaf Ventures",
            r"Park Partners",
            r"SALSS",
            r"Swedish[-\s]*American\s*Life\s*Science\s*Summit",
            r"Trilateral Commission",
            r"Valhi",
            r"(Yves\s*)?Bouvier",
        ],
    ),
    HighlightedNames(
        label='cannabis',
        style='chartreuse2',
        patterns=[
            r"CBD",
            r"cannabis",
            r"marijuana",
            r"psychedelic",
            r"THC",
            r"WEED(guide|maps)?[^s]?",
        ],
    ),
    HighlightedNames(
        label='China',
        style='bright_red',
        emailers={
            'Gino Yu': 'professor / game designer in Hong Kong',
        },
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
            r"North\s*Korean?",
            r"Peking",
            r"PRC",
            r"Pyongyang",
            r"SCMP",
            r"Xi(aomi)?",
            r"Jinping",
        ],
    ),
    HighlightedNames(
        label='deepak',
        style='dark_sea_green4',
        emailers={
            CAROLYN_RANGEL: f"Deepak Chopra's assistant {QUESTION_MARKS}",
            DEEPAK_CHOPRA: 'woo woo',
        },
    ),
    HighlightedNames(
        label='Democrat',
        style='sky_blue1',
        emailers={
            PAUL_PROSPERI: 'friend of Bill Clinton',
        },
        patterns=[
            r"(Al\s*)?Franken",
            r"Al\s*Gore",
            r"(Barac?k )?Obama",
            r"((Bill|Hillart?y)\s*)?Clinton",
            r"((Chuck|Charles)\s*)?S(ch|hc)umer",
            r"Debbie\s*Wasserman\s*Schultz",
            r"Dem(ocrat(ic)?)?",
            r"(Diana\s*)?DeGette",
            r"DNC",
            r"(Ed(ward)?\s*)?Mezvinsky",
            r"Elena\s*Kagan",
            r"(Eliott?\s*)?Spitzer(, Eliot)?",
            r"Eric Holder",
            r"George\s*Mitchell",
            r"(George\s*)?Soros",
            r"Hakeem\s*Jeffries",
            r"Hill?ary",
            r"HRC",
            r"(Jo(e|seph)\s*)?Biden",
            r"(John\s*)?Kerry",
            r"Lisa Monaco",
            r"(Matteo\s*)?Salvini",
            r"Maxine\s*Waters",
            r"(Nancy )?Pelosi",
            r"Open Society( Global Board)?",
            r"Ron\s*Dellums",
            r"Schumer",
            r"(Tim(othy)?\s*)?Geithner",
            r"Tom McMillen",
            r"Vernon\s*Jordan",
        ],
    ),
    HighlightedNames(
        label='Dubins',
        style='medium_orchid1',
        emailers={
            GLENN_DUBIN: "Highbridge Capital Management, married to Epstein's ex-gf Eva",
            EVA: "possibly Epstein's ex-girlfriend (?)",
            'Eva Dubin': f"Epstein's ex-girlfriend now married to {GLENN_DUBIN}",
        },
        patterns=[r"((Celina|Eva( Anderss?on)?|Glenn?) )?Dubin"],
    ),
    HighlightedNames(
        label='employee',
        style='medium_purple4',
        emailers={
            'Alfredo Rodriguez': "Epstein's butler, stole the journal",
            'Bernard Kruger': "Epstein's doctor",
            EDUARDO_ROBLES: f'home builder at Creative Kingdom Dubai',
            ERIC_ROTH: 'jet decorator at International Jet',
            GWENDOLYN_BECK: 'Epstein fund manager in the 90s',
            JANUSZ_BANASIAK: "Epstein's house manager",
            "John Allessi": "Epstein's houseman",
            JEAN_HUGUEN: 'interior design at Alberto Pinto Cabinet',
            LAWRANCE_VISOSKI: "Epstein's pilot",
            LESLEY_GROFF: f"Epstein's assistant",
            'Linda Pinto': 'interior design at Alberto Pinto Cabinet',
            MERWIN_DELA_CRUZ: None,  # HOUSE_OVERSIGHT_032652 Groff says "Jojo and Merwin both requested off Nov. 25 and 26"
            NADIA_MARCINKO: "Epstein's pilot",
            'Sean J. Lancaster': 'airplane reseller',
            ZUBAIR_KHAN: 'Tranchulas cybersecurity, InsightsPod founder, Islamabad / Dubai',
        },
        patterns=[
            r"Adriana\s*Ross",
            r"Merwin",
            r"(Sarah\s*)?Kellen", r"Vickers",  # Married name is Metiers
        ],
    ),
    HighlightedNames(
        label='Epstein',
        style='blue1',
        emailers={
            JEFFREY_EPSTEIN: None,
            MARK_EPSTEIN: 'brother of Jeffrey',
        },
        patterns=[
            r"JEGE(\s*Inc)?",
            r"LSJ",
        ],
    ),
    HighlightedNames(
        label=EPSTEIN_LAWYER,
        style='purple',
        emailers={
            'Alan S Halperin': 'partner at Paul, Weiss',
            ALAN_DERSHOWITZ: 'Harvard Law School professor',
            ARDA_BESKARDES: 'NYC immigration attorney allegedly involved in sex-trafficking operations',
            BENNET_MOSKOWITZ: f'represented the {EPSTEIN_ESTATE_EXECUTOR}s',
            BRAD_KARP: 'head of the law firm Paul Weiss',
            'Connie Zaguirre': f"office of {ROBERT_D_CRITTON_JR}",
            DAVID_SCHOEN: f"{CRIMINAL_DEFENSE_ATTORNEY} after 2019 arrest",
            DEBBIE_FEIN: EPSTEIN_V_ROTHSTEIN_EDWARDS_ATTORNEY,
            'Erika Kellerhals': 'attorney in St. Thomas',
            FRED_HADDAD: "co-founder of Heck's in West Virginia",
            GERALD_LEFCOURT: f'friend of {ALAN_DERSHOWITZ}',
            'Howard Rubenstein': f"Epstein's former spokesman",
            JACK_GOLDBERGER: CRIMINAL_DEFENSE_2008,
            JACKIE_PERCZEK: CRIMINAL_DEFENSE_2008,
            JAY_LEFKOWITZ: f"Kirkland & Ellis partner, {CRIMINAL_DEFENSE_2008}",
            JESSICA_CADWELL: f'paralegal to {ROBERT_D_CRITTON_JR}',  # house_oversight_030464
            KEN_STARR: 'head of the Monica Lewinsky investigation against Bill Clinton',
            LILLY_SANCHEZ: CRIMINAL_DEFENSE_ATTORNEY,
            MARTIN_WEINBERG: CRIMINAL_DEFENSE_ATTORNEY,
            MICHAEL_MILLER: 'Steptoe LLP partner',
            REID_WEINGARTEN: 'Steptoe LLP partner',
            ROBERT_D_CRITTON_JR: CRIMINAL_DEFENSE_ATTORNEY,
            'Robert Gold': 'helped Epstein track down money belonging to Spanish families',
            'Roy Black': CRIMINAL_DEFENSE_2008,
            SCOTT_J_LINK: CRIMINAL_DEFENSE_ATTORNEY,
            TONJA_HADDAD_COLEMAN: f'{EPSTEIN_V_ROTHSTEIN_EDWARDS_ATTORNEY}',  # relation of Fred Haddad?
        },
        patterns=[
            r"(Barry (E. )?)?Krischer",
            r"dersh",
            r"Kate Kelly",
            r"Kirkland\s*&\s*Ellis",
            r"(Leon\s*)?Jaworski",
            r"Michael J. Pike",
            r"Paul,?\s*Weiss",
            r"Steptoe(\s*& Johnson)?(\s*LLP)?",
            r"Wein(berg|garten)",
        ],
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
        emailers={
            ANDRZEJ_DUDA: 'former president of Poland',
            'Caroline Lang': 'daughter of Jack Lang',
            EDWARD_ROD_LARSEN: f"son of {TERJE_ROD_LARSEN}",
            'Fabrice Aidan': f'diplomat who worked with {TERJE_ROD_LARSEN}',
            'Jack Lang': 'former French Minister of National Education',
            MIROSLAV_LAJCAK: 'Russia-friendly Slovakian politician, friend of Steve Bannon',
            PETER_MANDELSON: 'UK politics',
            TERJE_ROD_LARSEN: 'Norwegian diplomat',
            THORBJORN_JAGLAND: 'former prime minister of Norway, Nobel Peace Prize Committee',
        },
        patterns=[
            r"AfD",
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
            r"Cypr(iot|us)",
            r"David\s*Cameron",
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
            r"Ibiza",
            r"Ital(ian|y)",
            r"Jacques",
            r"Kiev",
            r"Le\s*Pen",
            r"London",
            r"Macron",
            r"Melusine",
            r"MI\s*5",
            r"Munich",
            r"NATO",
            r"(Nicholas\s*)?Sarkozy",
            r"Nigel(\s*Farage)?",
            r"Norw(ay|egian)",
            r"Oslo",
            r"Paris",
            r"Polish",
            r"pope",
            r"Scotland",
            r"(Sebastian )?Kurz",
            r"Stockholm",
            r"Strasbourg",
            r"Strauss[- ]?Kahn",
            r"Swed(en|ish)(?![-\s]+American Life Scienc)",
            r"Swi(ss|tzerland)",
            r"(Tony\s)?Blair",
            r"U\.K\.",
            r"Ukrain(e|ian)",
            r"Venice",
            r"(Vi(c|k)tor\s+)?Orbah?n",
            r"Vienna",
            r"Zug",
            r"Zurich",
        ],
    ),
    HighlightedNames(
        label=FINANCE,
        style='green',
        emailers={
            AMANDA_ENS: 'Citigroup',
            BRAD_WECHSLER: f"head of {LEON_BLACK}'s personal investment vehicle according to FT",
            CECILIA_STEEN: None,
            DANIEL_SABBA: 'UBS Investment Bank',
            DAVID_FISZEL: 'CIO Honeycomb Asset Management',
            JES_STALEY: 'former CEO of Barclays',
            JIDE_ZEITLIN: 'former partner at Goldman Sachs, allegations of sexual misconduct',
            'Laurie Cameron': 'currency trading',
            LEON_BLACK: 'Apollo CEO who paid Epstein tens of millions for tax advice',
            MARC_LEON: 'Luxury Properties Sari Morrocco',
            MELANIE_SPINELLA: 'representative of Leon Black',
            MORTIMER_ZUCKERMAN: 'business partner of Epstein, newspaper publisher',
            NORMAN_D_RAU: 'managing director at Morgan Stanley',
            PAUL_BARRETT: None,
            PAUL_MORRIS: DEUTSCHE_BANK,
            'Skip Rimer': 'Milken Institute (Michael Milken)',
            'Steven Elkman': DEUTSCHE_BANK,
            'Vahe Stepanian': 'Cetera Financial Group',
            VINIT_SAHNI: f"analyst at {DEUTSCHE_BANK} and {GOLDMAN_SACHS}",
        },
        patterns=[
            r"Ace\s*Greenberg",
            r"AIG",
            r"((anti.?)?money\s+)?launder(s?|ers?|ing)?(\s+money)?",
            r"Apollo",
            r"Ari\s*Glass",
            r"Bank(\s*of\s*Scotland)",
            r"Bear\s*Stearns",
            r"(Bernie\s*)?Madoff",
            r"Black(rock|stone)",
            r"B\s*of\s*A",
            r"Boothbay(\sFund\sManagement)?",
            r"Chase\s*Bank",
            r"Conrad B",
            r"Credit\s*Suisse",
            r"DB",
            r"Deutsche?\s*(Asset|Bank)",
            r"Electron\s*Capital\s*(Partners)?",
            r"Fenner",
            r"FRBNY",
            r"Goldman(\s*Sachs)",
            r"GRAT",
            r"Gratitude (America|& Enhanced)",  # Leon Black and/or Epstein charity?
            r"Hank\s*Greenburg",
            r"HSBC",
            r"Invesco",
            r"Jamie\s*D(imon)?",
            r"(Janet\s*)?Yellen",
            r"(Jerome\s*)?Powell(?! M\. Cabot)",
            r"(Jimmy\s*)?Cayne",
            r"JPMC?",
            r"j\.?p\.?\s*morgan(\.?com|\s*Chase)?",
            r"Madoff",
            r"Merrill(\s*Lynch)?",
            r"(Michael\s*)?Cembalest",
            r"(Mi(chael|ke)\s*)?Milken(\s*Conference|Institute)?",
            r"Mizrahi\s*Bank",
            r"MLPF&S",
            r"Morgan Stanley",
            r"(Peter L. )?Scher",
            r"(Ray\s*)?Dalio",
            r"(Richard\s*)?LeFrak",
            r"(Ste(phen|ve)\s*)?Schwart?z?man",
            r"Serageldin",
            r"UBS",
            r"us.gio@jpmorgan.com",
            r"Wall\s*Street(?!\s*Jour)",
        ],
    ),
    HighlightedNames(
        label=FRIEND,
        style='tan',
        emailers={
            DANGENE_AND_JENNIE_ENTERPRISE: 'founders of the members-only CORE club',
            DAVID_STERN: f'emailed Epstein from Moscow, knows chairman of {DEUTSCHE_BANK} (?)',
            JONATHAN_FARKAS: "heir to the Alexander's department store fortune",
            'linkspirit': 'Skype username of someone Epstein communicated with',
            'Peter Thomas Roth': 'student of Epstein at Dalton, skincare company founder',
            STEPHEN_HANSON: None,
            TOM_BARRACK: 'long time friend of Trump',
        },
        patterns=[
            r"Andrew Farkas",
            r"Jonanthan and Kimberly Farkus",
            r"Thomas\s*(J\.?\s*)?Barrack(\s*Jr)?",
        ],
    ),
    HighlightedNames(
        label='government',
        style='color(24) bold',
        emailers={
            ANN_MARIE_VILLAFANA: 'Southern District of Florida (SDFL) U.S. Attorney',
            DANNY_FROST: 'Director of Communications at Manhattan D.A.',
            'Police Code Enforcement': f"{PALM_BEACH} buildings code enforcement",
        },
        patterns=[
            r"AG",
            r"(Alicia\s*)?Valle",
            r'Alice\s*Fisher|Fisher, Alice',
            r"AML",
            r"(Andrew\s*)?(McCabe|Natsios)",
            r"Attorney General",
            r"((Bob|Robert)\s*)?Mueller",
            r"(Byung\s)?Pak",
            r"Case 1:19-cv-03377(-LAP)?",
            r"(CENT|NORTH|SOUTH)COM",
            r"CFTC?",
            r"CIA",
            r"CIS",
            r"CVRA",
            r"DARPA",
            r"Dep(artmen)?t\.?\s*of\s*(the\s*)?(Justice|Treasury)",
            r"DHS",
            r"DOJ",
            r"FBI",
            r"FCPA",
            r"FDIC",
            r"FDLE",
            r"Federal\s*Bureau\s*of\s*Investigation",
            r"FinCEN",
            r"FINRA",
            r"FOIA",
            r"FTC",
            r"(General\s*)?P(a|e)traeus",
            r"Geoff\s*Ling",
            r"IRS",
            r"(James\s*)?Comey",
            r"(Jennifer\s*Shasky\s*)?Calvery",
            r"((Judge|Mark)\s*)?(Carney|Filip)",
            r"(Judge\s*)?(Kenneth\s*)?(A\.?\s*)?Marra",
            r"(Justice|Treasury)\s*Dep(t|artment)",
            r"(Kirk )?Blouin",
            r"KYC",
            r"(Lann?a\s*)?Belohlavek",
            r"NIH",
            r"NPA",
            r"NS(A|C)",
            r"OCC",
            r"OFAC",
            r"(Michael\s*)?Reiter",
            r"OGE",
            r"Office\s*of\s*Government\s*Ethics",
            r"police",
            r"(Preet\s*)?Bharara",
            r"SCOTUS",
            r"SD(FL|NY)",
            r"SEC",
            r"Secret\s*Service",
            r"Securities\s*and\s*Exchange\s*Commission",
            r"Southern\s*District(\s*of\s*(Florida|New\s*York))?",
            r"State\s*Dep(artmen)?t",
            r"Strzok",
            r"Supreme\s*Court",
            r"Treasury\s*(Dep(artmen)?t|Secretary)",
            r"TSA",
            r"U\.?S\.? attorney",
            r"USAID",
            r"US\s*(AF|Army|Air\s*Force)",
            r"Walter\s*Reed(\s*Army\s*Institute\s*of\s*Research)?",
            r"(William\s*J\.?\s*)?Zloch",
            r"WRAIR",
        ],
    ),
    HighlightedNames(
        label=HARVARD,
        style='light_goldenrod3',
        emailers={
            'Donald Rubin': 'Professor of Statistics',
            'Kelly Friendly': 'longtime aide and spokesperson of Larry Summers',
            LARRY_SUMMERS: 'board of Digital Currency Group (DCG), Obama economic advisor',
            'Leah Reis-Dennis': "producer for Lisa New's Poetry in America",
            LISA_NEW: f'professor of poetry, wife of {LARRY_SUMMERS}, AKA "Elisa New"',
            'Lisa Randall': 'theoretical physicist',
            MARTIN_NOWAK: 'professor of mathematics and biology',
            MOSHE_HOFFMAN: 'behavioral and evolutionary economics',
        },
        patterns=[
            r"Cambridge",
            r"(Derek\s*)?Bok",
            r"Elisa(\s*New)?",
            r"Harvard(\s*(Business|Law|University)(\s*School)?)?",
            r"(Jonathan\s*)?Zittrain",
            r"Poetry\s*in\s*America",
            r"(Stephen\s*)?Kosslyn",
        ],
    ),
    HighlightedNames(
        label='India',
        style='bright_green',
        emailers={
            ANIL_AMBANI: 'billionaire chairman of Reliance Group',
        },
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
    ),
    HighlightedNames(
        label='Israel',
        style='dodger_blue2',
        emailers={
            EHUD_BARAK: 'former prime minister of Israel, Epstein business partner',
            'Mitchell Bard': 'director of the American-Israeli Cooperative Enterprise (AICE)',
            NILI_PRIELL_BARAK: 'wife of Ehud Barak',
        },
        patterns=[
            r"AIPAC",
            r"Bibi",
            r"(eh|(Ehud|Nili Priell)\s*)?barak",
            r"EB",
            r"Ehud\s*Barack",
            r"Israeli?",
            r"Jerusalem",
            r"J\s*Street",
            r"Menachem\s*Begin",
            r"Mossad",
            r"Netanyahu",
            r"(Sheldon\s*)?Adelson",
            r"Tel\s*Aviv",
            r"(The\s*)?Shimon\s*Post",
            r"Yitzhak", r"Rabin",
            r"YIVO",
            r"zionist",
        ],
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
        emailers={
            'Alain Forget': 'author of "How To Get Out Of This World ALIVE"',
            'Alex Yablon': 'New York Magazine fact checker (?)',
            EDWARD_JAY_EPSTEIN: 'no relation, wrote books about spies',
            HENRY_HOLT: f"{MICHAEL_WOLFF}'s book publisher (company not a person)",
            JAMES_HILL: 'ABC News',
            JENNIFER_JACQUET: 'Future Science magazine',
            JOHN_BROCKMAN: 'literary agent and author specializing in scientific literature',
            LANDON_THOMAS: 'New York Times financial reporter',
            MICHAEL_WOLFF: 'Author of "Fire and Fury: Inside the Trump White House"',
            PAUL_KRASSNER: '60s counterculture guy',
            'Peter Aldhous': 'Buzzfeed science reporter',
            "Susan Edelman": 'New York Post reporter',
            'Tim Zagat': 'Zagat restaurant guide CEO',
        },
        patterns=[
            r"ABC(\s*News)?",
            r"Alexandra Wolfe|Wolfe, Alexandra",
            r"AlterNet",
            r"Arianna(\s*Huffington)?",
            r"(Arthur\s*)?Kretchmer",
            r'Associated\s*Press',
            r"Axios",
            r"BBC",
            r"(Bob|Robert)\s*Costa",
            r"Breitbart",
            r"BuzzFeed(\s*News)?",
            r"C-?Span",
            r"CBS(\s*(4|Corp|News))?",
            r"Charlie\s*Rose",
            r"China\s*Daily",
            r"(C|MS)?NBC(\s*News)?",
            r"CNN(politics?)?",
            r"Con[cs]hita", r"Sarnoff",
            r"Daily Business Review",
            r"(?<!Virgin[-\s]Islands[-\s])(The\s*)?Daily\s*(Beast|Mail|News|Telegraph)",
            r"(David\s*)?(Pecker|Pegg)",
            r"David\s*Brooks",
            r"Ed\s*Krassenstein",
            r"(Emily\s*)?Michot",
            r"Ezra\s*Klein",
            r"Fire\s*and\s*Fury",
            r"Forbes",
            r"Fortune\s*Magazine",
            r"Fox\s*News(\.com)?",
            r"FrontPage Magazine",
            r"FT",
            r"(George\s*)?Stephanopoulus",
            r"Ger(ald|ry)\s*Baker",
            r"Globe\s*and\s*Mail",
            r"Good\s*Morning\s*America",
            r"Graydon(\s*Carter)?",
            r"Huff(ington)?(\s*Po(st)?)?",
            r"Ingram, David",
            r"James\s*Hill",
            r"(James\s*)?Patterson",
            r"Jesse Kornbluth",
            r"John\s*Connolly",
            r"Jonathan\s*Karl",
            r"Julie\s*(K.?\s*)?Brown", r'jbrown@miamiherald.com',
            r"(Katie\s*)?Couric",
            r"Keith\s*Larsen",
            r"L\.?A\.?\s*Times",
            r"Law(360|\.com|fare)",
            r"(Les\s*)?Moonves",
            r"MarketWatch",
            r"Miami\s*Herald",
            r"(Mi(chael|ke)\s*)?Bloomber[gq](\s*News)?",
            r"(Michele\s*)?Dargan",
            r"Morning News USA",
            r"(National\s*)?Enquirer",
            r"News(max|week)",
            r"NYer",
            r"Palm\s*Beach\s*(Daily\s*News|Post)",
            r"PERVERSION\s*OF\s*JUSTICE",
            r"Politico",
            r"Pro\s*Publica",
            r"Reuters",
            r"(Sean\s*)?Hannity",
            r"Sharon Churcher",  # Daily Mail
            r"Sulzberger",
            r"SunSentinel",
            r"(The\s*)?Financial\s*Times",
            r"The\s*Guardian",
            r"TheHill",
            r"(The\s*)?Mail\s*On\s*Sunday",
            r"(The\s*)?N(ew\s*)?Y(ork)?\s*(Magazine|Observer|P(ost)?|T(imes)?)",
            r"(The\s*)?New\s*Yorker",
            r"(The\s*)?Wall\s*Street\s*Journal",
            r"(The\s*)?Wa(shington\s*)?Po(st)?",
            r"(Uma\s*)?Sanghvi",
            r"Vanity\s*Fair",
            r"Viceland",
            r"Vick[iy]\s*Ward",
            r"Vox",
            r"WGBH",
            r"WSJ",
            r"[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk",
        ],
    ),
    HighlightedNames(
        label=JUNK,
        style='gray46',
        emailers={
            'asmallworld@travel.asmallworld.net': None,
            "digest-noreply@quora.com": None,
            'editorialstaff@flipboard.com': None,
            'How To Academy': None,
            'Jokeland': None,
        },
        should_match_first_last_name=False,
    ),
    HighlightedNames(
        label='Latin America',
        style='yellow',
        patterns=[
            r"Argentin(a|ian)",
            r"Bolsonar[aio]",
            r"Bra[sz]il(ian)?",
            r"Caracas",
            r"Castro",
            r"Chile",
            r"Colombian?",
            r"Cuban?",
            r"El\s*Salvador",
            r"((Enrique )?Pena )?Nieto",
            r"Lat(in)?\s*Am(erican?)?",
            r"Lula",
            r"(?<!New )Mexic(an|o)",
            r"(Nicolas\s+)?Maduro",
            r"Panama( Papers)?",
            r"Peru(vian)?",
            r"Venezuelan?",
            r"Zambrano",
        ],
    ),
    HighlightedNames(
        label=LOBBYIST,
        style='light_coral',
        emailers={
            BOB_CROWE: 'partner at Nelson Mullins',
            'Joshua Cooper Ramo': 'co-CEO of Henry Kissinger Associates',
            KATHERINE_KEATING: 'daughter of former Australian prime minister',
            MOHAMED_WAHEED_HASSAN: 'former president of the Maldives',
            OLIVIER_COLOM: 'France',
            'Paul Keating': 'former prime minister of Australia',
            PUREVSUREN_LUNDEG: 'Mongolian ambassador to the UN',
            'Stanley Rosenberg': 'former President of the Massachusetts Senate',
        },
        patterns=[
            r"CSIS",
            r"elisabeth\s*feliho",
            r"(Kevin\s*)?Rudd",
            r"Stanley Rosenberg",
            r"Vinoda\s*Basnayake",
        ],
    ),
    HighlightedNames(
        label='locations',
        style='cornsilk1',
        patterns=[
            r"Alabama",
            r"Arizona(?! State University)",
            r"Aspen",
            r"Berkeley",
            r"Brooklyn",
            r"California",
            r"Canada",
            r"Cape Cod",
            r"Charlottesville",
            r"Connecticut",
            r"Florida",
            r"Loudoun\s*County?",
            r"Martha's\s*Vineyard",
            r"Miami(?!\s?Herald)",
            r"Nantucket",
            r"New\s*(Jersey|Mexico)",
            r"(North|South)\s*Carolina",
            r"NY(C|\s*State)",
            r"Orange\s*County",
            r"Oregon",
            r"Phoenix",
            r"Portland",
            r"Santa\s*Fe",
            r"Telluride",
            r"Teterboro",
            r"Texas(?! A&M)",
            r"Toronto",
            r"Tu(sc|cs)on",
            r"Vermont",
            r"Washington(\s*D\.?C)?(?!\s*Post)",
            r"Westchester",
        ],
    ),
    HighlightedNames(
        label=MIDEAST,
        style='dark_sea_green4',
        emailers={
            ANAS_ALRASHEED: 'former information minister of Kuwait (???)',
            AZIZA_ALAHMADI: 'Abu Dhabi Department of Culture & Tourism',
            RAAFAT_ALSABBAGH: 'Saudi royal advisor',
            SHAHER_ABDULHAK_BESHER: 'Yemeni billionaire',
        },
        patterns=[
            r"Abdulmalik Al-Makhlafi",
            r"Abdullah",
            r"Abu\s+Dhabi",
            r"Afghanistan",
            r"Al[-\s]?Qa[ei]da",
            r"Ahmadinejad",
            r"Arab",
            r"Aramco",
            r"Armenia",
            r"Assad",
            r"Ayatollah",
            r"Bahrain",
            r"Basiji?",
            r"Beirut",
            r"Benghazi",
            r"Brunei",
            r"Cairo",
            r"Chagoury",
            r"Damascus",
            r"Dj[iu]bo?uti",
            r"Doha",
            r"[DB]ubai",
            r"Egypt(ian)?",
            r"Emir(at(es?|i))?",
            r"Erdogan",
            r"Fashi",
            r"Gaddafi",
            r"Gulf\s*Cooperation\s*Council",
            r"GCC",
            r"(Hamid\s*)?Karzai",
            r"Hamad\s*bin\s*Jassim",
            r"Hamas",
            r"Hezbollah",
            r"HBJ",
            r"Houthi",
            r"Imran\s+Khan",
            r"Iran(ian)?([-\s]Contra)?",
            r"Isi[ls]",
            r"Islam(abad|ic|ist)?",
            r"Istanbul",
            r"Kabul",
            r"(Kairat\s*)?Kelimbetov",
            r"kasshohgi",
            r"Kaz(akh|ich)stan",
            r"Kazakh?",
            r"Kh[ao]menei",
            r"Khalid\s*Sheikh\s*Mohammed",
            r"Kh?ashoggi",
            r"KSA",
            r"Leban(ese|on)",
            r"Libyan?",
            r"Mahmoud",
            r"Marra[hk]e[cs]h",
            r"MB(N|S|Z)",
            r"Mid(dle)?\s*East(ern)?",
            r"Mohammed\s+bin\s+Salman",
            r"Morocc(an|o)",
            r"Mubarak",
            r"Muslim(\s*Brotherhood)?",
            r"Nayaf",
            r"Pakistani?",
            r"Omar",
            r"(Osama\s*)?Bin\s*Laden",
            r"Osama(?! al)",
            r"Palestin(e|ian)",
            r"Persian?(\s*Gulf)?",
            r"Riya(dh|nd)",
            r"Saddam",
            r"Salman",
            r"Saudi(\s+Arabian?)?",
            r"Shariah?",
            r"SHC",
            r"sheikh",
            r"shia",
            r"(Sultan\s*)?Yacoub",
            r"Sultan(?! Ahmed)",
            r"Syrian?",
            r"(Tarek\s*)?El\s*Sayed",
            r"Tehran",
            r"Tripoli",
            r"Tunisian?",
            r"Turk(ey|ish)",
            r"Turks(?! & Caicos)",
            r"UAE",
            r"((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        ],
    ),
    HighlightedNames(
        label='modeling',
        style='pale_violet_red1',
        emailers={
            'Abi Schwinck': f'{MC2_MODEL_MANAGEMENT} {QUESTION_MARKS}',
            DANIEL_SIAD: None,
            FAITH_KATES: 'Next Models co-founder',
            'Gianni Serazzi': 'fashion consultant?',
            HEATHER_MANN: 'South African former model, ex-girlfriend of Prince Andrew (?)',
            JEAN_LUC_BRUNEL: f'MC2 Model Management founder, died by suicide in French jail',
            JEFF_FULLER: f'president of {MC2_MODEL_MANAGEMENT} USA',
            'lorraine@mc2mm.com': f'{MC2_MODEL_MANAGEMENT}',
            'pink@mc2mm.com': f'{MC2_MODEL_MANAGEMENT}',
            MANUELA_MARTINEZ: 'Mega Partners (Brazilian agency)',
            MARIANA_IDZKOWSKA: None,
            'Michael Sanka': f'{MC2_MODEL_MANAGEMENT} {QUESTION_MARKS}',
            'Vladimir Yudashkin': 'director of the 1 Mother Agency',
        },
        patterns=[
            r"\w+@mc2mm.com",
            r"MC2",
            r"(Nicole\s*)?Junkerman",  # Also a venture fund manager now
            r"Tigrane",
        ],
    ),
    HighlightedNames(
        label=PUBLICIST,
        style='orange_red1',
        emailers={
            AL_SECKEL: "Isabel Maxwell's husband, Mindshift conference, fell off a cliff",
            'Barnaby Marsh': 'co-founder of philanthropy services company Saint Partners',
            CHRISTINA_GALBRAITH: f"{EPSTEIN_FOUNDATION} Media/PR, worked with {TYLER_SHEARS}",  # Title in 031441
            IAN_OSBORNE: f'{OSBORNE_LLP} reputation repairer hired in 2011',
            MATTHEW_HILTZIK: 'crisis PR at Hiltzik Strategies',
            MICHAEL_SITRICK: 'crisis PR',
            'Owen Blicksilver': 'OBPR, Inc.',
            PEGGY_SIEGAL: 'socialite, movie promoter',
            'R. Couri Hay': None,
            ROSS_GOW: 'Acuity Reputation Management',
            TYLER_SHEARS: f"{REPUTATION_MGMT}, worked on with {CHRISTINA_GALBRAITH}",
        },
        patterns=[
            r"(Matt(hew)? )?Hiltzi[gk]",
            r"PR\s*Newswire",
            REPUTATION_MGMT,
            r"Reputation.com",
            r"(Robert L\. )?Dilenschneider",
        ],
    ),
    HighlightedNames(
        label='Republican',
        style='dark_red bold',
        emailers={
            "Juleanna Glover": 'CEO of D.C. public affairs advisory firm Ridgely|Walsh',
            RUDY_GIULIANI: None,
            TULSI_GABBARD: None,
        },
        patterns=[
            r"Alberto\sGonzale[sz]",
            r"(Alex\s*)?Acosta",
            r"(Ben\s*)?Sasse",
            r"Betsy Devos",
            r"((Bill|William)\s*)?Barr",
            r"Bill\s*Shine",
            r"Blackwater",
            r"(Bob\s*)?Corker",
            r"(Brett\s*)?Kavanaugh",
            r"Broidy",
            r"(Chris\s)?Christie",
            r"(?<!Merwin Dela )Cruz",
            r"Devin\s*Nunes",
            r"(Don\s*)?McGa[hn]n",
            r"Erik Prince",
            r"Gary\s*Cohn",
            r"George\s*(H\.?\s*)?(W\.?\s*)?Bush",
            r"(George\s*)?Nader",
            r"GOP",
            r"Jeff(rey)?\s*Sessions",
            r"(John\s*(R.?\s*)?)?Bolton",
            r"Kasich",
            r"Keith\s*Schiller",
            r"Kelly(\s*Anne?)?\s*Conway|Kellyanne",
            r"Kissinger",
            r"Kobach",
            r"Kolfage",
            r"(Larry\s*)?Kudlow",
            r"Lewandowski",
            r"(Marco\s)?Rubio",
            r"(Mark\s*)Meadows",
            r"Mattis",
            r"McCain",
            r"McMaster",
            r"(Michael\s)?Hayden",
            r"((General|Mike)\s*)?(Flynn|Pence)",
            r"(Mitt\s*)?Romney",
            r"Mnuchin",
            r"(Newt\s*)Gingrich",
            r"Nikki",
            r"Haley",
            r"(Paul\s*)?(Manafort|Volcker)",
            r"(Peter\s*)?Navarro",
            r"Pompeo",
            r"Reagan",
            r"Reince", r"Priebus",
            r"Republican",
            r"(Rex\s*)?Till?erson",
            r"(?<!Cynthia )(Richard\s*)?Nixon",
            r"RNC",
            r"Tea\s*Party",
        ],
    ),
    HighlightedNames(
        label='Rothschild',
        style='indian_red',
        emailers={
            ARIANE_DE_ROTHSCHILD: 'heiress',
            JOHNNY_EL_HACHEM: f'Edmond de Rothschild Private Equity',
        },
        patterns=['AdR'],
    ),
    HighlightedNames(
        label='Russia',
        style='red bold',
        emailers={
            'Dasha Zhukova': 'art collector, daughter of Alexander Zhukov',
            MASHA_DROKOVA: 'silicon valley VC, former Putin Youth member',
            RENATA_BOLOTOVA: 'former model, fund manager at New York State Insurance Fund',
            SVETLANA_POZHIDAEVA: "Epstein's Russian assistant who was recommended for a visa by Sergei Belyakov (FSB) and David Blaine",
        },
        patterns=[
            r"Alfa\s*Bank",
            r"Anya\s*Rasulova",
            r"Chernobyl",
            r"Crimea",
            r"Day\s+One\s+Ventures",
            r"(Dmitry\s)?(Kiselyov|(Lana\s*)?Pozhidaeva|Medvedev|Rybolo(o?l?ev|vlev))",
            r"Dmitry",
            r"FSB",
            r"GRU",
            r"KGB",
            r"Kislyak",
            r"Kremlin",
            r"(Anastasia\s*)?Kuznetsova",
            r"Lavrov",
            r"Lukoil",
            r"Moscow",
            r"(Natalia\s*)?Veselnitskaya",
            r"(Oleg\s*)?Deripaska",
            r"Oleksandr Vilkul",
            r"Onexim",  # Prokhorov investment vehicle
            r"Prokhorov",
            r"Rosneft",
            r"RT",
            r"St.?\s*?Petersburg",
            r'Svet',
            r"Russian?",
            r"Sberbank",
            r"Soviet(\s*Union)?",
            r"Timur\s*Kulibayev",
            r"USSR",
            r"Vlad(imir)?(?! Yudash)",
            r"(Vladimir\s*)?Putin",
            r"Women\s*Empowerment",
            r"Xitrans",
            r"(Vitaly\s*)?Churkin",
        ],
    ),
    HighlightedNames(
        label='Southeast Asia',
        style='light_salmon3 bold',
        patterns=[
            r"Australian?(?! Ave)",
            r"Bangkok",
            r"Burm(a|ese)",
            r"Cambodian?",
            r"Laos",
            r"Malaysian?",
            r"Maldives",
            r"Myan?mar",
            r"New\s*Zealand",
            r"Philippines",
            r"South\s*Korean?",
            r"Tai(pei|wan)",
            r"Thai(land)?",
            r"Vietnam(ese)?",
        ],
    ),
    HighlightedNames(
        label=TECH_BRO,
        style='bright_cyan',
        emailers={
            'Auren Hoffman': 'CEO of SafeGraph (firm that gathers location data from mobile devices) and LiveRamp',
            ELON_MUSK: 'father of Mecha-Hitler',
            PETER_THIEL: 'Paypal mafia member, founder of Palantir, Facebook investor',
            REID_HOFFMAN: 'PayPal mafia member, founder of LinkedIn',
            STEVEN_SINOFSKY: 'ex-Microsoft, loves bitcoin',
            VINCENZO_IOZZO: 'CEO of the identity-security company SlashID',
        },
        patterns=[
            r"AG?I",
            r"Artificial\s*(General\s*)?Intelligence",
            r"Chamath", r"Palihapitiya",
            r"Danny\s*Hillis",
            r"deep learning",
            r"Drew\s*Houston",
            r"Eric\s*Schmidt",
            r"Greylock(\s*Partners)?",
            r"(?<!(ustin|Moshe)\s)Hoffmand?",
            r"(Jeff\s*)?Bezos",
            r"Larry Page",
            r"LinkedIn",
            r"(Marc\s*)?Andreess?en",
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
    ),
    HighlightedNames(
        label='Trump',
        style='red3 bold',
        emailers={
            'Bruce Moskowitz': "'Trump's health guy' according to Epstein",
            NICHOLAS_RIBIS: 'Hilton CEO, former president of Trump Organization',
        },
        patterns=[
            r"@?realDonaldTrump",
            r"(Alan\s*)?Weiss?elberg",
            r"Alex\s*Jones",
            r"\bDJ?T\b",
            r"Donald J. Tramp",
            r"(Donald\s+(J\.\s+)?)?Trump(ism|\s*(Org(anization)?|Properties)(\s*LLC)?)?",
            r"Don(ald| *Jr)(?! (B|Rubin))",
            r"Ivank?a",
            r"Jared", r"(?<!Tony )Kushner",
            r"(Madeleine\s*)?Westerhout",
            r"Mar[-\s]*a[-\s]*Lago",
            r"(Marla\s*)?Maples",
            r"(Matt(hew)? )?Calamari",
            r"\bMatt C\b",
            r"Michael\s*(D\.?\s*)?Cohen",
            r"Melania",
            r"(Michael (J.? )?)?Boccio",
            r"Paul Rampell",
            r"Rebekah\s*Mercer",
            r"Roger\s+Stone",
            r"rona",
            r"(The\s*)?Art\s*of\s*the\s*Deal",
        ],
    ),
    HighlightedNames(
        label='USVI',
        style='sea_green1',
        emailers={
            CECILE_DE_JONGH: 'Virgin Islands first lady 2007-2015',
            KENNETH_E_MAPP: 'Virgin Islands Governor',
            STACEY_PLASKETT: 'Virgin Islands non-voting member of Congress',
        },
        patterns=[
            r"Antigua",
            r"Bahamas",
            r"BVI",
            r"Caribb?ean",
            r"Dominican\s*Republic",
            r"(Great|Little)\s*St.?\s*James",
            r"Haiti(an)?",
            r"Jamaican?",
            r"(John\s*)deJongh(\s*Jr\.?)",
            r"(Kenneth E\. )?Mapp",
            r"PBI",
            r"Puerto\s*Ric(an|o)",
            r"S(ain)?t.?\s*Thomas",
            r"USVI",
            r"(?<!stein |vis-a-)VI(?!s-a-)",
            r"(The\s*)?Virgin\s*Is(al|la)nds(\s*Daily\s*News)?",  # Hard to make this work right
            r"(West\s*)?Palm\s*Beach(\s*County)?(?!\s*(Daily|Post))",
        ],
    ),
    HighlightedNames(
        label='victim',
        style='orchid1',
        patterns=[
            r"#metoo",
            r"(David\s*)?Bo[il]es(,?\s*Schiller( & Flexner)?)?",
            r"(Gloria\s*)?Allred",
            r"(Jane|Tiffany)\s*Doe",
            r"Katie\s*Johnson",
            r"pedophile",
            r"Stephanie\s*Clifford",
            r"Stormy\s*Daniels",
            r"(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre",
            r"Virginia\s+Roberts",
        ],
    ),
    HighlightedNames(
        label='victim lawyer',
        style='medium_orchid1',
        emailers={
            BRAD_EDWARDS: ROTHSTEIN_ROSENFELDT_ADLER,
            'Grant J. Smith': ROTHSTEIN_ROSENFELDT_ADLER,
            JACK_SCAROLA: 'Searcy Denney Scarola Barnhart & Shipley',
            KEN_JENNE: ROTHSTEIN_ROSENFELDT_ADLER,
        },
        patterns=[
            r"(Alan(\s*P.)?|MINTZ)\s*FRAADE",
            r"(J\.?\s*)?(Stan(ley)?\s*)?Pottinger",
            r"(Mi(chael|ke)\s*)?Avenatti",
            r"Paul\s*(G.\s*)?Cassell",
            r"Rothstein\s*Rosenfeldt\s*Adler",
            r"(Scott\s*)?Rothstein",
        ],
    ),
    HighlightedNames(
        label=STEVE_BANNON,
        style='color(58)',
        category='Republican',
        emailers={
            SEAN_BANNON: f"{STEVE_BANNON}'s brother",
            STEVE_BANNON: "Trump campaign manager, memecoin grifter",
        },
        patterns=[
            r"(American\s*)?Dharma",
            r"Biosphere",
        ],
    ),

    # Individuals
    HighlightedNames(
        emailers={STEVEN_HOFFENBERG: "Epstein's Towers Financial ponzi partner, prison for 18 years"},
        style='dark_olive_green3',
        category=FINANCE,
        patterns=[r"(steven?\s*)?hoffenberg?w?"],
    ),
    HighlightedNames(
        emailers={GHISLAINE_MAXWELL: "Epstein's girlfriend, daughter of the spy Robert Maxwell"},
        category='Epstein',
        patterns=[r"gmax(1@ellmax.com)?", r"(The )?TerraMar Project"],
        style='deep_pink3',
    ),
    HighlightedNames(emailers={JABOR_Y: '"an influential man in Qatar"'}, category=MIDEAST, style='spring_green1'),
    HighlightedNames(emailers={KATHRYN_RUEMMLER: 'former Obama legal counsel'}, style='magenta2', category=FRIEND),
    HighlightedNames(emailers={MELANIE_WALKER: f"doctor, friend of {BILL_GATES}"}, style='pale_violet_red1', category=FRIEND),
    HighlightedNames(emailers={PAULA: "Epstein's ex-girlfriend who is now in the opera world"}, label='paula', style='pink1', category=FRIEND),
    HighlightedNames(emailers={PRINCE_ANDREW: 'British royal family'}, style='dodger_blue1', category='Europe'),
    HighlightedNames(emailers={SOON_YI_PREVIN: 'wife of Woody Allen'}, style='hot_pink', category=ARTS),
    HighlightedNames(emailers={SULTAN_BIN_SULAYEM: 'chairman of ports in Dubai, CEO of DP World'}, style='green1', category=MIDEAST),

    # HighlightedText not HighlightedNames bc of word boundary issue
    HighlightedText(
        label='phone_number',
        style='bright_green',
        patterns=[
            r"\+?(1?\(?\d{3}\)?[- ]\d{3}[- ]\d{4}|\d{2}[- ]\(?0?\)?\d{2}[- ]\d{4}[- ]\d{4})",
            r"(\b|\+)[\d+]{10,12}\b",
        ],
    ),
    HighlightedText(
        label='unknown',
        style='cyan',
        patterns=[r'\(unknown\)']
    ),
]

# Highlight regexes for things other than names, only used by RegexHighlighter pattern matching
HIGHLIGHTED_TEXTS = [
    HighlightedText(
        label='header_field',
        style='plum4',
        patterns=[r'^[> ]{,3}(Date|From|Sent|To|C[cC]|Importance|Reply[- ]?To|Subject|Bee|B[cC]{2}|Attachments|Flag|Classification|((A|De(stinataire)?|Envoye|Expe(cl|d)iteur|Objet|Q) ?)):'],
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

    # Manual regexes
    ManualHighlight(
        label='email_attachments',
        style='gray30 italic',
        pattern=r"^(> )?Attachments: (?P<email_attachments>.*)",
    ),
    ManualHighlight(
        label='email_timestamp',
        style=TIMESTAMP_STYLE,
        pattern=r"^(> )?(Date|Sent): (?P<email_timestamp>.*)",
    ),
]

ALL_HIGHLIGHTS = HIGHLIGHTED_NAMES + HIGHLIGHTED_TEXTS
JUNK_EMAILERS = [name for name in [hn for hn in HIGHLIGHTED_NAMES if hn.label == JUNK][0].emailers.keys()]


class EpsteinHighlighter(RegexHighlighter):
    """Finds and colors interesting keywords based on the above config."""
    base_style = f"{REGEX_STYLE_PREFIX}."
    highlights = [highlight_group.regex for highlight_group in ALL_HIGHLIGHTS]
    highlight_counts = defaultdict(int)

    def highlight(self, text: Text) -> None:
        """overrides https://rich.readthedocs.io/en/latest/_modules/rich/highlighter.html#RegexHighlighter"""
        highlight_regex = text.highlight_regex

        for re_highlight in self.highlights:
            highlight_regex(re_highlight, style_prefix=self.base_style)

            if args.debug and isinstance(re_highlight, re.Pattern):
                for match in re_highlight.finditer(text.plain):
                    type(self).highlight_counts[(match.group(1) or 'None').replace('\n', ' ')] += 1

    def print_highlight_counts(self, console: Console) -> None:
        """Print counts of how many times strings were highlighted."""
        highlight_counts = deepcopy(self.highlight_counts)
        weak_date_regex = re.compile(r"^(\d\d?/|20|http|On ).*")

        for highlighted, count in sort_dict(highlight_counts):
            if highlighted is None or weak_date_regex.match(highlighted):
                continue

            try:
                console.print(f"{highlighted:25s} highlighted {count} times")
            except Exception as e:
                logger.error(f"Failed to print highlight count {count} for {highlighted}")


def get_highlight_group_for_name(name: str | None) -> HighlightedNames | None:
    if name is None:
        return None

    for highlight_group in HIGHLIGHTED_NAMES:
        if highlight_group.regex.search(name):
            return highlight_group


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


def get_style_for_name(name: str | None, default_style: str = DEFAULT_NAME_STYLE, allow_bold: bool = True) -> str:
    highlight_group = get_highlight_group_for_name(name or UNKNOWN)
    style = highlight_group.style if highlight_group else default_style
    style = style if allow_bold else style.replace('bold', '').strip()
    logger.debug(f"get_style_for_name('{name}', '{default_style}', '{allow_bold}') yielded '{style}'")
    return style


def styled_category(category: str | None) -> Text:
    if not category:
        return QUESTION_MARKS_TXT

    category_str = 'resumé' if category == 'resume' else category.lower()
    return Text(category_str, get_style_for_category(category) or 'wheat4')


def styled_name(name: str | None, default_style: str = DEFAULT_NAME_STYLE) -> Text:
    return Text(name or UNKNOWN, style=get_style_for_name(name, default_style=default_style))


def _print_highlighted_names_repr() -> None:
    for hn in HIGHLIGHTED_NAMES:
        if isinstance(hn, HighlightedNames):
            print(indented(repr(hn)) + ',')
            print(f"pattern: '{hn.regex.pattern}'")

    import sys
    sys.exit()

#_print_highlighted_names_repr()
