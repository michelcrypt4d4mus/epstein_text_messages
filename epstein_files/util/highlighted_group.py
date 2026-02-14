import json
import re
from collections import defaultdict
from dataclasses import dataclass, field

from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.text import Text

from epstein_files.people.contact_info import ContactInfo
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import ARCHIVE_LINK_COLOR
from epstein_files.util.constants import EPSTEIN_V_ROTHSTEIN_EDWARDS, OSBORNE_LLP, REPLY_REGEX, SENT_FROM_REGEX
from epstein_files.util.data import sort_dict, without_falsey
from epstein_files.util.doc_cfg import *
from epstein_files.util.env import args
from epstein_files.util.helpers.string_helper import indented
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
TECH_BRO = 'tech bro'

VICTIM_COLOR = 'orchid1'

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
        contacts (list[ContactInfo]): optional ContactInfo objects with names and regexes
        _pattern (str): regex pattern combining 'pattern' with first & last names of all 'emailers'
    """
    category: str = ''
    contacts: list[ContactInfo] = field(default_factory=list)
    contacts_lookup: dict[Name, ContactInfo] = field(default_factory=dict)
    should_match_first_last_name: bool = True

    def __post_init__(self):
        if not (self.patterns or self.contacts):
            raise ValueError(f"Must provide either 'emailers' or 'pattern' arg.")
        elif not self.label:
            if len(self.contacts) == 1 and self.contacts[0].name:
                self.label = self.contacts[0].name
            else:
                raise ValueError(f"No label provided for {repr(self)}")

        super().__post_init__()
        self._pattern = '|'.join([contact.highlight_pattern for contact in self.contacts] + self.patterns)
        self.regex = re.compile(fr"\b({self._match_group_var}({self._pattern})s?)\b", re.IGNORECASE)
        self.contacts_lookup = ContactInfo.build_name_lookup(self.contacts)

    def category_str(self) -> str:
        if self.category:
            return self.category
        elif len(self.contacts) == 1 and self.label == self.contacts[0].name:
            return ''
        else:
            return self.label.replace('_', ' ')

    def info_for(self, name: str, include_category: bool = False) -> str | None:
        """Label and additional info for 'name' if 'name' is in `self.contacts`."""
        info_pieces = [self.category_str()] if include_category else []

        if (contact := self.contacts_lookup.get(name)):
            info_pieces.append(contact.info)

        info_pieces = without_falsey(info_pieces)
        return ', '.join(info_pieces) if info_pieces else None

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        s = f"{type(self).__name__}("

        for property in ['label', 'style', 'category', 'patterns', 'contacts']:
            value = getattr(self, property)

            if not value or (property == 'label' and len(self.contacts) == 1 and not self.patterns):
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
        pattern=r"^(> )?(Classification|Flag|Subject|Sujet ?): (?P<email_subject>.*)",
    ),
    HighlightedNames(
        label=ACADEMIA,
        style='light_goldenrod2',
        contacts=[
            ContactInfo('Daniel Kahneman', "Nobel economic sciences laureate and cognitivie psychologist (?)"),
            ContactInfo(DAVID_HAIG, "evolutionary geneticist?", emailer_pattern=r"David Haig|Haig, David"),
            ContactInfo('David Grosof', "MIT Sloan School of Management"),
            ContactInfo('Ed Boyden', f"{MIT_MEDIA_LAB} neurobiology professor"),
            ContactInfo('Harry Fisch', "men's health expert at New York-Presbyterian / Weill Cornell (?)"),
            ContactInfo(JOSCHA_BACH, "cognitive science / AI research"),
            ContactInfo(LAWRENCE_KRAUSS, "theoretical physicist with #MeToo problems", r"Lawrence Kraus[es]?|[jl]awkrauss|kruase"),
            ContactInfo(LINDA_STONE, f"ex-Microsoft, {MIT_MEDIA_LAB}"),
            ContactInfo(MARK_TRAMO, "professor of neurology at UCLA"),
            ContactInfo('Nancy Dahl', f"wife of {LAWRENCE_KRAUSS}"),
            ContactInfo(NEAL_KASSELL, "professor of neurosurgery at University of Virginia"),
            ContactInfo(NOAM_CHOMSKY, "professor of linguistics at MIT"),
            ContactInfo('Norman Finkelstein', "scholar, well known critic of Israel"),
            ContactInfo(PETER_ATTIA, "longevity medicine"),
            ContactInfo(ROBERT_TRIVERS, "evolutionary biology", r"tri[vy]ersr@gmail|Robert\s*Trivers?"),
            ContactInfo(ROGER_SCHANK, "Teachers College, Columbia University"),
            ContactInfo(SETH_LLOYD, "professor of mechanical engineering at MIT"),
            ContactInfo('Valeria Chomsky', f"wife of {NOAM_CHOMSKY}"),
            ContactInfo(YUKO_BARNABY, f"{MIT_MEDIA_LAB} Assistant to the Director", r"Y[ou]ko\s*Ba(m|rn)(aby)?"),
        ],
        patterns=[
            r"Andy\s*Lippman",  # Media Lab
            r"Arizona\s*State\s*University",
            r"Bard\s+((Early )?College|High School|Schools)",
            r"Brotherton",
            r"Carl\s*Sagan",
            r"Columbia(\s*(Business\s*School|University))?",
            r"Dan(iel|ny) Kahneman",
            r"(Francis\s*)?Crick",
            r"J(ames|im)\s*Watson",
            r"(Lord\s*)?Martin\s*Rees",
            r"Massachusetts\s*Institute\s*of\s*Technology",
            r"Mayo\s*Clinic",
            r"Media\s*Lab",
            r"(Marvin\s*)?Minsky",
            r"MIT(\s*Media\s*Lab)?",
            r"Norman\s*Finkelstein",
            r"Oxford(?! Analytica)",
            r"Praluent",
            r"Princeton(\s*University)?",
            r"Regeneron",
            r"(Richard\s*)?Dawkins",
            r"Rockefeller\s*University",
            r"(Sandy\s*)?Pentland",  # Media Lab
            r"Sanofi",
            r"Stanford(\s*University)?(\s*Hospital)?",
            r"(Ste(ph|v)en\s*)?Hawking",
            r"(Steven?\s*)?Pinker",
            r"Texas\s*A&M",
            r"Tulane",
            r"UCLA",
        ],
    ),
    HighlightedNames(
        label='Africa',
        style='light_pink4',
        contacts=[
            ContactInfo('Abdoulaye Wade', "former president of Senegal, father of Karim Wade"),
            ContactInfo('Ivan Glasenberg', "South African former CEO of Glencore, one of the world's largest commodity trading and mining companies"),
            ContactInfo('Karim Wade', 'son of the president of Senegal, facing arrest for corruption, email handle is "Afri zp"'),
            ContactInfo('Miles Alexander', "Operations Manager Michaelhouse Balgowan KwaZulu-Natal South Africa"),
            ContactInfo('Macky Sall', "prime minister of Senegal, defeated Abdoulaye Wade")
        ],
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
        contacts=[
            ContactInfo(ANDRES_SERRANO, "'Piss Christ' artist"),
            ContactInfo('Barry Josephson', "American film producer, editor FamilySecurityMatters.org"),
            ContactInfo(BILL_SIEGEL, "documentary film producer and director"),
            ContactInfo(DAVID_BLAINE, "famous magician"),
            ContactInfo('David Brenner', "American comedian and actor"),
            ContactInfo('Richard Merkin', "painter, illustrator and arts educator"),
            ContactInfo(STEVEN_PFEIFFER, "Associate Director at Independent Filmmaker Project (IFP)"),
            ContactInfo('Steven Gaydos', "American screenwriter and journalist")
        ],
        patterns=[
            r"(Art )?Spiegelman",
            r"Artspace",
            r"Ayn\s*Rand",
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
            r"Sotheby's",
            r"Woody( Allen)?",
            r"Zach Braff",
        ],
    ),
    HighlightedNames(
        label=BILL_GATES,
        style='turquoise4',
        category=TECH_BRO,
        contacts=[
            ContactInfo(BILL_GATES, "ex-Microsoft, Gates Foundation, bgC3"),
            ContactInfo(
                name=BORIS_NIKOLIC,
                info=f"biotech VC partner of {BILL_GATES}, Epstein estate executor",
                emailer_pattern=r"(boris )?nikolic?",
            )
        ],
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
        label=CRYPTO,
        style='orange1 bold',
        contacts=[
            ContactInfo(
                name=ADAM_BACK,
                info=f"co-founder of {BLOCKSTREAM}, bitcoin dev, long time Tether defender",
                emailer_pattern=r"Adam\s*Back?",
            ),
            ContactInfo(
                name=AMIR_TAAKI,
                info=f"bitcoin bro, partner of {DONALD_NORMAN} (and {BROCK_PIERCE}?)",
                emailer_pattern=r"Amir\s*Taaki|genjix",
            ),
            ContactInfo(
                name=ANTHONY_SCARAMUCCI,
                info="Skybridge Capital, FTX investor",
                emailer_pattern=r"mooch|(Anthony ('The Mooch' )?)?Scaramucci",
            ),
            ContactInfo(AUSTIN_HILL, f"{BLOCKSTREAM} co-founder with {ADAM_BACK}, Brudder Ventures"),
            ContactInfo(BROCK_PIERCE, "Bannon business partner, Tether co-founder, friend of Yair Netanyahu, sex crime history"),
            ContactInfo(BRYAN_BISHOP, "executive at LedgerX, Polymath fund"),
            ContactInfo(DONALD_NORMAN, f"co-founder of early British crypto exchange Intersango with {AMIR_TAAKI}"),
            ContactInfo(JEFFREY_WERNICK, "former COO of Parler, involved in numerous crypto companies like Bitforex"),
            ContactInfo(
                name=JEREMY_RUBIN,
                info="developer/researcher",
                emailer_pattern=r"Jeremy\s*Rubin",
            ),
            ContactInfo(
                name=JOI_ITO,
                info=f"former head of {MIT_MEDIA_LAB} and MIT Digital Currency Initiative",
                emailer_pattern=r"ji@media.mit.?edu|(joichi|joi)( Ito)?",
            ),
            ContactInfo(
                name=LORENZO_DE_MEDICI,
                info="Medici Bank, possibly Medici heir?",
                emailer_pattern=r"Prince\s*Lorenzo|Lorenzo\s*de\s*Medici",
            ),
            ContactInfo(MADARS_VIRZA, f"ZCash lead dev, {MIT_MEDIA_LAB}")
        ],
        patterns=[
            r"Alphabit",
            r"((Andy|Adam)\s*)Back",
            r"Balaji",
            r"Barry Silbert",
            r"Bart\s*Stephens",  # co-founder, Blockchain Capital
            r"Bioptix",  # Now RIOT Blockchain
            r"bitcoin(\s*Foundation)?",
            r"Bit(Angels|Fury)",
            r"block ?chain(\s*capital)?",
            r"Blockstream",
            r"Bradley\s*Rotter",
            r"Brian Forde",
            r"Brock(\s*Pierce)?",
            r"Brudder(\s*Ventures)?",
            r"Coinbase",
            r"coins?(\s*Center)?",
            r"Cory\s*Fields",  # bitcoin dev
            r"cr[iy]?pto\s*(coins?|currenc(y|ies)|PR\s*Lab)?",
            r"crypto(prlab)?",
            r"(Dan\s*)?Morehead",
            r"Digital\s*Currenc(ies|y)(\s*Initiative)?",
            r"e-?currency",
            r"Fred\s*Ehrsam",
            r"(Gavin )?Andress?en",  # bitcoin dev
            r"(Hester\s*)?Peirce",
            r"(Howard\s+)?Lutnic?k",
            r"ICO",
            r"(Jim\s*)Pallotta",  # Media lab advisory board
            r"Kraken",
            r"Kyara(\s*Investments?)?",  # crypto vehicle with Joi Ito
            r"Layer\s+(1|One)",
            r"LedgerX",
            r"Libra",
            r"Madars",
            r"Medici\s*Bank",
            r"Mi(chael|ke)\s*Novogratz",
            r"Noble\s*(Bank|Markets)",  # Crypto bank with Tether ties
            r"Pantera",
            r"(Patrick\s*)?Murck",
            r"Ribbit",
            r"(?-i:RIOT)",  # (?-i:) makes it case sensitive
            r"Ron\s*Rivest",
            r"(Ross\s*)?Ulbricht",
            r"Silk\s*Road",
            r"SpanCash",
            r"Tether",
            r"virtual\s*currenc(ies|y)",
            r"Wire\s*ca\n?rd",
            r"Wladimir( van der Laan)?",  # bitcoin dev
            r"ZCash",
            r"ZECC?",
            r"ZeroCoin",
            r"(zero\s+knowledge\s+|zk)pro(of|tocols?)",
        ],
    ),
    HighlightedNames(
        label=BUSINESS,
        style='spring_green4',
        contacts=[
            ContactInfo(
                name=ALIREZA_ITTIHADIEH,
                info="CEO Freestream Aircraft Limited",
                emailer_pattern=r"Alireza.[Il]ttihadieh",
            ),
            ContactInfo('AT&T Court Appearance Team', "AT&T"),
            ContactInfo(
                name=BARBRO_C_EHNBOM,
                info="Swedish pharmaceuticals, SALSS",
                emailer_pattern=r"behnbom@aol.com|(Barbro\s.*)?Ehnbom",
            ),
            ContactInfo(
                name=BARRY_J_COHEN,
                emailer_pattern=r"barry\s*((j.?|james)\s*)?cohen?",
            ),
            ContactInfo('David Mitchell', "Mitchell Holdings, New York real estate developer"),
            ContactInfo(
                name=GERALD_BARTON,
                info="Maryland property developer Landmark Land Company",
                emailer_pattern=r"Gerald.*Barton",
            ),
            ContactInfo(NICOLE_JUNKERMANN, f"ex-model, NJF Capital, German investor in Revolut, Winamax (online poker) and Carbyen ({EHUD_BARAK})"),
            ContactInfo(GORDON_GETTY, "heir to oil tycoon J. Paul Getty"),
            ContactInfo('Philip Kafka', f"president of Prince Concepts (and son of {TERRY_KAFKA}?)"),
            ContactInfo(
                name=ROBERT_LAWRENCE_KUHN,
                info="investment banker, China expert",
                emailer_pattern=r"Robert\s*(Lawrence)?\s*Kuhn",
            ),
            ContactInfo(
                name=TERRY_KAFKA,
                info="CEO of Impact Outdoor (highway billboards)",
                emailer_pattern=r"Terry Kafka?",
            ),
            ContactInfo(TOM_PRITZKER, "chairman of The Pritzker Organization and Hyatt Hotels")
        ],
        patterns=[
            r"Arthur Klein",
            r"(Barry\s*)?Honig",
            r"((Bill|David)\s*)?Koch(\s*(Bro(s|thers)|Industries))?",
            r"Gruterite",
            r"((John|Patricia)\s*)?Kluge",
            r"Marc Rich",
            r"(Mi(chael|ke)\s*)?Ovitz",
            r"(Steve\s+)?Wynn",
            r"(Les(lie)?\s+)?Wexner",
            r"Michael\s*Klein",
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
        contacts=[
            ContactInfo('Gino Yu', "professor / game designer in Hong Kong")
        ],
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
        contacts=[
            ContactInfo(CAROLYN_RANGEL, f"{DEEPAK_CHOPRA}'s assistant {'(???)'}"),
            ContactInfo(DEEPAK_CHOPRA, "woo woo")
        ],
    ),
    HighlightedNames(
        label='Democrat',
        style='sky_blue1',
        contacts=[
            ContactInfo(PAUL_PROSPERI, "friend of Bill Clinton")
        ],
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
        contacts=[
            ContactInfo(EVA_DUBIN, f"Epstein's ex-girlfriend now married to {GLENN_DUBIN}"),
            ContactInfo(GLENN_DUBIN, "Highbridge Capital Management, married to Epstein's ex-gf Eva"),
        ],
        patterns=[r"((Celina|Eva( Anderss?on)?|Glenn?) )?Dubin"],
    ),
    HighlightedNames(
        label='employee',
        style='medium_purple4',
        contacts=[
            ContactInfo('Alfredo Rodriguez', "Epstein's butler, stole the journal"),
            ContactInfo('Bella Klein', "Epstein's accountant"),
            ContactInfo('Bernard Kruger', "Epstein's doctor"),
            ContactInfo(
                name=EDUARDO_ROBLES,
                info="home builder at Creative Kingdom Dubai",
                emailer_pattern=r"Ed(uardo)?\s*Robles",
            ),
            ContactInfo(ERIC_ROTH, "jet decorator at International Jet"),
            ContactInfo(GWENDOLYN_BECK, "Epstein fund manager in the 90s"),
            ContactInfo('Ike Groff', f"brother of {LESLEY_GROFF}?"),
            ContactInfo(
                name=JANUSZ_BANASIAK,
                info="Epstein's house manager",
                emailer_pattern=r"Janu[is]z Banasiak",
            ),
            ContactInfo('John Allessi', "Epstein's houseman"),
            ContactInfo(
                name=JEAN_HUGUEN,
                info="interior design at Alberto Pinto Cabinet",
                emailer_pattern=r"Jean[\s.]Huguen",
            ),
            ContactInfo(
                name=JOJO_FONTANILLA,
                info="Filipino housekeeper",
                emailer_pattern=r"Jo.. Fontanilla",
            ),
            ContactInfo(
                name=LAWRANCE_VISOSKI,
                info="Epstein's pilot",
                emailer_pattern=r"La(rry|wrance) Visoski?|Lvjet",
            ),
            ContactInfo(
                name=LESLEY_GROFF,
                info="Epstein's assistant",
                emailer_pattern=r"Lesley\s*Gro(ff)?",
            ),
            ContactInfo('Linda Pinto', "interior design at Alberto Pinto Cabinet"),
            ContactInfo(
                name=LYN_FONTANILLA,
                info="Filipino housekeeper",
                emailer_pattern=r"L.nn? Fontanilla",
            ),
            ContactInfo(MERWIN_DELA_CRUZ, "housekeeper"),
            ContactInfo(
                name=NADIA_MARCINKO,
                info="Epstein's pilot",
                emailer_pattern=r"Na[dď]i?a\s+Marcinko(v[aá])?",
            ),
            ContactInfo('Sean J. Lancaster', "airplane reseller"),
            ContactInfo(STORY_COWLES, "Epstein's male assistant")
        ],
        patterns=[
            r"Adriana\s*Ross",
            r"Merwin",
            r"(Sarah\s*)?Kellen", r"Vickers",  # Married name is Metiers
        ],
    ),
    HighlightedNames(
        label='Epstein',
        style='blue1',
        contacts=[
            ContactInfo(
                name=JEFFREY_EPSTEIN,
                emailer_pattern=r"[djl]\s?ee[vy]acation[©@]?g?(mail.com)?|Epstine|\bJEE?\b|Jeff(rey)? (Edward )?E((sp|ps)tein?)?( VI Foundation)?|jeeproject@yahoo.com|J Jep|Jeffery Edwards|(?<!(ark L.|rd Jay|Edward) )Epstein",
            ),
            ContactInfo(
                name=MARK_EPSTEIN,
                info="brother of Jeffrey",
                emailer_pattern=r"Mark (L\. )?(Epstein|Lloyd)",
            )
        ],
        patterns=[
            r"JEGE(\s*Inc)?",
            r"LSJE?(,\s*LLC)?",  # Virgin Islands corporation
            r"Zorro(\s*Ranch)?",
        ],
    ),
    HighlightedNames(
        label=EPSTEIN_LAWYER,
        style='purple',
        contacts=[
            ContactInfo('Alan S Halperin', "partner at Paul, Weiss"),
            ContactInfo(
                name=ALAN_DERSHOWITZ,
                info=f"{HARVARD} Law School professor",
                emailer_pattern=r"(alan.{1,7})?dershowi(lz?|t?z)|AlanDersh",
            ),
            ContactInfo(ARDA_BESKARDES, "NYC immigration attorney allegedly involved in sex-trafficking operations"),
            ContactInfo(
                name=BENNET_MOSKOWITZ,
                info="represented the Epstein estate executors",
                emailer_pattern=r"Moskowitz.*Bennet|Bennet.*Moskowitz",
            ),
            ContactInfo(
                name=BRAD_KARP,
                info="head of the law firm Paul Weiss",
                emailer_pattern=r"Brad (S.? )?Karp|Karp, Brad",
            ),
            ContactInfo(
                name=CHRISTIAN_EVERDELL,
                info=f"{GHISLAINE_MAXWELL}'s lawyer ca. 2021, Cohen & Gresser",
                emailer_pattern=r"C(hristian\s*)?Everdell?",
            ),
            ContactInfo('Connie Zaguirre', f"office of {'Robert D. Critton Jr.'}"),
            ContactInfo(DAVID_SCHOEN, "criminal defense attorney after 2019 arrest"),
            ContactInfo(DEBBIE_FEIN, f"civil attorney Epstein v. Scott Rothstein, {BRAD_EDWARDS}, & L.M."),
            ContactInfo('Erika Kellerhals', "attorney in St. Thomas"),
            ContactInfo(FRED_HADDAD, "co-founder of Heck's in West Virginia"),
            ContactInfo(
                name=GERALD_LEFCOURT,
                info=f"friend of {ALAN_DERSHOWITZ}",
                emailer_pattern=r"Gerald\s*(B\.?\s*)?Lefcourt",
            ),
            ContactInfo('Howard Rubenstein', "Epstein's former spokesman"),
            ContactInfo(JACK_GOLDBERGER, "criminal defense attorney on 2008 case"),
            ContactInfo(
                name=JACKIE_PERCZEK,
                info="criminal defense attorney on 2008 case",
                emailer_pattern=r"jackie percze[kl]?",
            ),
            ContactInfo(JAY_LEFKOWITZ, "Kirkland & Ellis partner, criminal defense attorney on 2008 case"),
            ContactInfo(
                name=JESSICA_CADWELL,
                info=f"paralegal to {'Robert D. Critton Jr.'}",
                emailer_pattern=r"Jessica Cadwell?",
            ),
            ContactInfo(
                name=KEN_STARR,
                info="head of the Monica Lewinsky investigation against Bill Clinton",
                emailer_pattern=r"starr, ken|Ken(neth\s*(W.\s*)?)?\s+starr?|starr",
            ),
            ContactInfo(
                name=LILLY_SANCHEZ,
                info="criminal defense attorney",
                emailer_pattern=r"Lilly.*Sanchez",
            ),
            ContactInfo(
                name=MARTIN_WEINBERG,
                info="criminal defense attorney",
                emailer_pattern=r"martin.*?weinberg",
            ),
            ContactInfo(
                name=MICHAEL_MILLER,
                info="Steptoe LLP partner",
                emailer_pattern=r"Micha(el)? Miller|Miller, Micha(el)?",
            ),
            ContactInfo(
                name=REID_WEINGARTEN,
                info="Steptoe LLP partner",
                emailer_pattern=r"Weingarten, Rei[cdi]|Rei[cdi] Weingarten",
            ),
            ContactInfo(
                name='Robert D. Critton Jr.',
                info="criminal defense attorney",
                emailer_pattern=r"Robert D.? Critton,? Jr.?",
            ),
            ContactInfo('Robert Gold', "helped Epstein track down money belonging to Spanish families"),
            ContactInfo('Roy Black', "criminal defense attorney on 2008 case"),
            ContactInfo(
                name=SCOTT_J_LINK,
                info="criminal defense attorney",
                emailer_pattern=r"scott j. link?",
            ),
            ContactInfo(
                name=STACEY_RICHMAN,
                info="New York criminal defense attorney",
                emailer_pattern=r"srichmanlaw|Stacey\s*Richman",
            ),
            ContactInfo(
                name=TONJA_HADDAD_COLEMAN,
                info=f"civil attorney Epstein v. Scott Rothstein, {BRAD_EDWARDS}, & L.M.",
                emailer_pattern=r"To(nj|rl)a Haddad Coleman|haddadfm@aol.com",
            )
        ],
        patterns=[
            r"(Barry (E. )?)?Krischer",
            r"dersh",
            r"Kate Kelly",
            r"Kirkland\s*&\s*Ellis",
            r"(Leon\s*)?Jaworski",
            r"Michael J. Pike",
            r"Paul,?\s*Weiss",
            r"Steptoe(\s*& Johnson)?(\s*LLP)?",
            r"Sull(ivan)?\s*(&|and)?\s*Crom(well)?",
            r"Wein(berg|garten)",
        ],
    ),
    HighlightedNames(
        label=ESTATE_EXECUTOR,
        style='purple3 bold',
        category=EPSTEIN_LAWYER,
        contacts=[
            ContactInfo(
                name=DARREN_INDYKE,
                info="Epstein estate executor",
                emailer_pattern=r"darren$|Darren\s*(K\.?\s*)?[il]n[dq]_?yke?|dkiesq",
            ),
            ContactInfo(
                name=RICHARD_KAHN,
                info="Epstein estate executor",
                emailer_pattern=r"rich(ard)? kahn?",
            )
        ],
    ),
    HighlightedNames(
        label='Europe',
        style='light_sky_blue3',
        contacts=[
            ContactInfo(ANDRZEJ_DUDA, "former president of Poland"),
            ContactInfo('Caroline Lang', "daughter of Jack Lang"),
            ContactInfo(EDWARD_ROD_LARSEN, f"son of {TERJE_ROD_LARSEN}"),
            ContactInfo('Fabrice Aidan', f"diplomat who worked with {TERJE_ROD_LARSEN}"),
            ContactInfo('Jack Lang', "former French Minister of National Education"),
            ContactInfo(
                name=MIROSLAV_LAJCAK,
                info=f"Russia-friendly Slovakian politician, friend of {STEVE_BANNON}",
                emailer_pattern=r"Miro(slav)?(\s+Laj[cč][aá]k)?",
            ),
            ContactInfo(
                name=PETER_MANDELSON,
                info="UK politics",
                emailer_pattern=r"((Lord|Peter) )?Mandelson",
            ),
            ContactInfo(
                name=TERJE_ROD_LARSEN,
                info="Norwegian diplomat",
                emailer_pattern=r"Terje(( (R[øo]e?d[- ])?)?Lars[eo]n)?",
            ),
            ContactInfo(
                name=THORBJORN_JAGLAND,
                info="former prime minister of Norway, Nobel Peace Prize Committee",
                emailer_pattern=r"(Thor.{3,8})?Jag[il]and?",
            )
        ],
        patterns=[
            r"AfD",
            r"Alfa(\s*Bank)",
            r"(Angela )?Merk(el|le)",
            r"Austria",
            r"Belgi(an|um)",
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
            r"(Kamila\s*)?Bobinska",
            r"Kiev",
            r"Latvian?",
            r"Lithuanian?",
            r"Le\s*Pen",
            r"(?<!DOJ )London",
            r"Macron",
            r"Melusine",
            r"MI\s*5",
            r"Munich",
            r"NATO",
            r"(Nicholas\s*)?Sarkozy",
            r"Nigel(\s*Farage)?",
            r"(Northern\s*)?Ireland",
            r"Norw(ay|egian)",
            r"Oslo",
            r"Paris",
            r"Polish",
            r"pope",
            r"Portugal",
            r"Scotland",
            r"(Sebastian )?Kurz",
            r"Stockholm",
            r"Strasbourg",
            r"Strauss[- ]?Kahn",
            r"Swed(en|ish)(?![-\s]+American Life Scienc)",
            r"Swi(ss|tzerland)",
            r"(Tony\s)?Blair",
            r"United\s*Kingdom",
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
        contacts=[
            ContactInfo(
                name=AMANDA_ENS,
                info="Citigroup",
                emailer_pattern=r"ens, amanda?|Amanda.Ens",
            ),
            ContactInfo(BRAD_WECHSLER, f"head of {LEON_BLACK}'s personal investment vehicle according to FT"),
            ContactInfo(CECILIA_STEEN),
            ContactInfo(DANIEL_SABBA, f"{UBS} Investment Bank"),
            ContactInfo(
                name=DAVID_FISZEL,
                info="CIO Honeycomb Asset Management, Epstein invested in Spotify through him",
                emailer_pattern=r"David\s*Fis?zel",
            ),
            ContactInfo(JES_STALEY, "former CEO of Barclays"),
            ContactInfo(JIDE_ZEITLIN, f"former partner at {GOLDMAN_SACHS}, allegations of sexual misconduct"),
            ContactInfo('Laurie Cameron', "currency trading"),
            ContactInfo(
                name=LEON_BLACK,
                info="Apollo CEO who paid Epstein tens of millions for tax advice",
                emailer_pattern=r"Leon\s*Black?|(?<!Marc )Leon(?! (Botstein|Jaworski|Wieseltier))",
            ),
            ContactInfo(
                name=MARC_LEON,
                info="Luxury Properties Sari Morrocco",
                emailer_pattern=r"Marc[.\s]+(Kensington|Leon)|Kensington2",
            ),
            ContactInfo(
                name=MELANIE_SPINELLA,
                info=f"representative of {LEON_BLACK}",
                emailer_pattern=r"M?elanie Spine[Il]{2}a",
            ),
            ContactInfo(MORTIMER_ZUCKERMAN, "business partner of Epstein, newspaper publisher"),
            ContactInfo(NORMAN_D_RAU, "managing director at Morgan Stanley"),
            ContactInfo(
                name=PAUL_BARRETT,
                emailer_pattern=r"Paul Barre(d|tt)",
            ),
            ContactInfo(
                name=PAUL_MORRIS,
                info=f"{DEUTSCHE_BANK}",
                emailer_pattern=r"morris, paul|Paul Morris",
            ),
            ContactInfo('Skip Rimer', "Milken Institute (Michael Milken)"),
            ContactInfo('Steven Elkman', f"{DEUTSCHE_BANK}"),
            ContactInfo(TANCREDI_MARCHIOLO, "hedge fund manager"),
            ContactInfo('Vahe Stepanian', "Cetera Financial Group"),
            ContactInfo(VINIT_SAHNI, f"analyst at {DEUTSCHE_BANK} and {GOLDMAN_SACHS}")
        ],
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
            r"Cantor(\s*(Fitzgerald|Opportunities))?",
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
            r"Joon\s*Yun",
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
            r"Rockefeller(?! University)(\s*Foundation)?",
            r"SBNY",
            r"Serageldin",
            r"Signature\s*Bank",
            r"(Ste(phen|ve)\s*)?Schwart?z?man",
            r"Susquehanna",
            r"UBS",
            r"us.gio@jpmorgan.com",
            r"Wall\s*Street(?!\s*Jour)",
        ],
    ),
    HighlightedNames(
        label=FRIEND,
        style='tan',
        contacts=[
            ContactInfo(
                name=ANDREW_FARKAS,
                info="heir to the Alexander's department store fortune",
                emailer_pattern=r"Andrew\s*(L\.\s*)?Farkas|Farkas,\s*Andrew(\s*L\.?)?",
            ),
            ContactInfo(
                name=DANGENE_AND_JENNIE_ENTERPRISE,
                info="founders of the members-only CORE club",
                emailer_pattern=r"Dangene and Jennie Enterprise?",
            ),
            ContactInfo(
                name=DAVID_STERN,
                info=f"emailed Epstein from Moscow, knows chairman of {DEUTSCHE_BANK} (?)",
                emailer_pattern=r"David Stern?",
            ),
            ContactInfo(
                name=JONATHAN_FARKAS,
                info="heir to the Alexander's department store fortune",
                emailer_pattern=r"Jonathan Fark(a|u)(s|il)",
            ),
            ContactInfo('linkspirit', "Skype username of someone Epstein communicated with"),
            ContactInfo('Peter Thomas Roth', "student of Epstein at Dalton, skincare company founder"),
            ContactInfo(
                name=STEPHEN_HANSON,
                emailer_pattern=r"ste(phen|ve) hanson?|Shanson900",
            ),
            ContactInfo(TOM_BARRACK, "long time friend of Trump")
        ],
        patterns=[
            r"Jonanthan and Kimberly Farkus",
            r"Thomas\s*(J\.?\s*)?Barrack(\s*Jr)?",
        ],
    ),
    HighlightedNames(
        label='government',
        style='color(24) bold',
        contacts=[
            ContactInfo(
                name=ALISON_J_NATHAN,
                info="judge in New York's Southern District",
                emailer_pattern=r"Alison(\s*J\.?)?\s*Nathan|Nathan\s*NYSD\s*Chambers?",
            ),
            ContactInfo(
                name=ANN_MARIE_VILLAFANA,
                info="Southern District of Florida (SDFL) U.S. Attorney",
                emailer_pattern=r"Villafana, Ann Marie|(A(\.|nn) Marie )?Villafa(c|n|ri)a",
            ),
            ContactInfo(
                name=AUDREY_STRAUSS,
                info="USA Attorney",
                emailer_pattern=r"Audrey Strauss|Strauss, Audrey",
            ),
            ContactInfo(
                name=BUREAU_OF_PRISONS,
                info="American law enforcement",
                emailer_pattern=r"bop\.gov",
            ),
            ContactInfo(
                name=CHRISTOPHER_DILORIO,
                info="self described whistleblower",
                emailer_pattern=r"Chris\s*Di[lI]o[nr](io)?",
            ),
            ContactInfo(
                name=DANNY_FROST,
                info="Director of Communications at Manhattan D.A.",
                emailer_pattern=r"Frost, Danny|frostd@dany.nyc.gov|Danny\s*Frost",
            ),
            ContactInfo('DOJ Inspector General', "American law enforcement"),
            ContactInfo('DOJ London', "American law enforcement"),
            ContactInfo(FBI, "American law enforcement"),
            ContactInfo('Florence Hutner', "New York Office of Chief Medical Examiner"),
            ContactInfo('Justin Alfano', "American law enforcement"),
            ContactInfo('Manhattan DA', "American law enforcement"),
            ContactInfo('NY FBI', "American law enforcement"),
            ContactInfo(
                name=OFFICE_OF_THE_DEPUTY_ATTORNEY_GENERAL,
                info="American law enforcement",
                emailer_pattern=r"\bODAG\b",
            ),
            ContactInfo('Paula Speer', "court reporter"),
            ContactInfo('Police Code Enforcement', "Palm Beach buildings code enforcement"),
            ContactInfo(SDNY, "American law enforcement, Southern District of New York"),
            ContactInfo('USAHUB-USAJournal111', "American law enforcement"),
            ContactInfo(USANYS, "American law enforcement"),
            ContactInfo('USMS', "United States Marshal Service")
        ],
        patterns=[
            r"AG",
            r"(Alicia\s*)?Valle",
            r'Alice\s*Fisher|Fisher, Alice',
            r"AML",
            r"(Andrew\s*)?(McCabe|Natsios)",
            r"(Assistant\s+)?State\s*Attorney",
            r"Attorney General",
            r'Barbara\s*Burns',  # AUSA
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
            r"EDGAR (Filing|Search)",  # SEC database is EDGAR
            r"FCPA",
            r"FDIC",
            r"FDLE",
            r"Federal\s*Bureau\s*of\s*Investigation",
            r"FinCEN",
            r"(www\.)?FINRA(\.org)?",
            r"Florence Hutner",
            r"FOIA",
            r"FTC",
            r"Gary\s*Gensler",
            r"(General\s*)?P(a|e)traeus",
            r"Geoff\s*Ling",
            r"Homeland\s*Security",
            r"Interpol",
            r"IRS",
            r"(James\s*)?Comey",
            r"(Jennifer\s*Shasky\s*)?Calvery",
            r"((Judge|Mark)\s*)?(Carney|Filip)",
            r"(Judge\s*)?(Kenneth\s*)?(A\.?\s*)?Marra",
            r"(Justice|Treasury)\s*Dep(t|artment)",
            r"(Kirk )?Blouin",
            r"KYC",
            r"(Lann?a\s*)?Belohlavek",
            r"MDC"
            r"Metropolitan Detention Center",
            r"(Michael\s*)?Reiter",
            r"NIH",
            r"NPA",
            r"NS(A|C)",
            r"OCC",
            r"ODAG",
            r"OFAC",
            r"OGE",
            r"Office\s*of\s*Government\s*Ethics",
            r"PBPD",
            r"police",
            r"POTUS",
            r"(Preet\s*)?Bharara",
            r"Public\s*Corruption\s*Unit",
            r"SCOTUS",
            r"SD(FL|NY)",
            r"SEC(\.gov)?",
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
            USANYS,
            r"US\s*(AF|Army|Air\s*Force)",
            r"Walter\s*Reed(\s*Army\s*Institute\s*of\s*Research)?",
            r"(William\s*J\.?\s*)?Zloch",
            r"WRAIR",
        ],
    ),
    HighlightedNames(
        label=HARVARD,
        style='light_goldenrod3',
        contacts=[
            ContactInfo('Donald Rubin', "Professor of Statistics"),
            ContactInfo('Kelly Friendly', f"longtime aide and spokesperson of {LARRY_SUMMERS}"),
            ContactInfo(
                name=LARRY_SUMMERS,
                info="board of Digital Currency Group (DCG), Obama economic advisor",
                emailer_pattern=r"(La(wrence|rry).{1,5})?Summers?|^LH$|LHS|[Il]hsofficel?",
            ),
            ContactInfo('Leah Reis-Dennis', f"producer for {LISA_NEW}'s Poetry in America"),
            ContactInfo(
                name=LISA_NEW,
                info=f"professor of poetry, wife of {LARRY_SUMMERS}, AKA \"Elisa New\"",
                emailer_pattern=r"E?Lisa New?\b",
            ),
            ContactInfo('Lisa Randall', "theoretical physicist"),
            ContactInfo(
                name=MARTIN_NOWAK,
                info="professor of mathematics and biology",
                emailer_pattern=r"(Martin.*?)?No[vw]ak|Nowak, Martin",
            ),
            ContactInfo(MOSHE_HOFFMAN, "behavioral and evolutionary economics")
        ],
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
        contacts=[
            ContactInfo(
                name=ANIL_AMBANI,
                info="billionaire chairman of Reliance Group",
                emailer_pattern=r"Anil.Ambani",
            )
        ],
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
        contacts=[
            ContactInfo(
                name=EHUD_BARAK,
                info="former prime minister of Israel, Epstein business partner",
                emailer_pattern=r"(ehud|e?h)\s*barak|\behud",
            ),
            ContactInfo('Mitchell Bard', "director of the American-Israeli Cooperative Enterprise (AICE)"),
            ContactInfo(NILI_PRIELL_BARAK, f"wife of {EHUD_BARAK}")
        ],
        patterns=[
            r"AIPAC",
            r"Bibi",
            r"Carbyne",   # Co. invested in by barak + epstein
            r"(eh|(Ehud|Nili Priell)\s*)?barak",
            r"EB",
            r"Ehud\s*Barack",
            r"Hapoalim",
            r"Israeli?",
            r"Jerusalem",
            r"J\s*Street",
            r"Menachem\s*Begin",
            r"Mossad",
            r"Netanyahu",
            r"Reporty",  # Co. invested in by barak + epstein
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
        contacts=[
            ContactInfo('Alain Forget', "author of \"How To Get Out Of This World ALIVE\""),
            ContactInfo('Alex Yablon', "New York Magazine fact checker (?)"),
            ContactInfo(
                name=EDWARD_JAY_EPSTEIN,
                info="no relation, wrote books about spies",
                emailer_pattern=r"(?<!Jeffrey )Edward (Jay )?Epstein",
            ),
            ContactInfo(HENRY_HOLT, f"{MICHAEL_WOLFF}'s book publisher (company not a person)"),
            ContactInfo(
                name=JAMES_HILL,
                info="ABC News",
                emailer_pattern=r"hill, james e.|james.e.hill@abc.com",
            ),
            ContactInfo(JENNIFER_JACQUET, "Future Science magazine"),
            ContactInfo(JOHN_BROCKMAN, "literary agent and author specializing in scientific literature"),
            ContactInfo(
                name=LANDON_THOMAS,
                info="New York Times financial reporter",
                emailer_pattern=r"lando[nr] thomas( jr)?|thomas jr.?, lando[nr]",
            ),
            ContactInfo(
                name=MICHAEL_WOLFF,
                info="Author of \"Fire and Fury: Inside the Trump White House\"",
                emailer_pattern=r"Michael\s*Wol(f[ef]e?|i)|Wolff",
            ),
            ContactInfo(
                name='Newsmax',
                info="right wing American news outlet",
                emailer_pattern=r"Newsmax(\.com)?",
            ),
            ContactInfo(
                name=PAUL_KRASSNER,
                info="60s counterculture guy",
                emailer_pattern=r"Pa\s?ul Krassner",
            ),
            ContactInfo('Peter Aldhous', "Buzzfeed science reporter"),
            ContactInfo('Susan Edelman', "New York Post reporter"),
            ContactInfo('Tim Zagat', "Zagat restaurant guide CEO")
        ],
        patterns=[
            r"ABC(\s*News)?",
            r"Alexandra Wolfe|Wolfe, Alexandra",
            r"AlterNet",
            r"Arianna(\s*Huffington)?",
            r"(Arthur\s*)?Kretchmer",
            r'Associated\s*Press',
            r"Axios",
            r"BBC",
            r"(Bob|Robert)\s*(Costa|Woodward)",
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
            r"Hollywood\s*Reporter",
            r"Huff(ington)?(\s*Po(st)?)?",
            r"Ingram, David",
            r"James\s*Hill",
            r"(James\s*)?Patterson",
            r"Jesse Kornbluth",
            r"John\s*Connolly",
            r"Jonathan\s*Karl",
            r"Journal of Criminal Law and Criminology",
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
            r"(Thomson\s*)?Reuters",
            r"(Uma\s*)?Sanghvi",
            r"USA\s*Today",
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
        contacts=[
            ContactInfo('asmallworld@travel.asmallworld.net'),
            ContactInfo('digest-noreply@quora.com'),
            ContactInfo('editorialstaff@flipboard.com'),
            ContactInfo('How To Academy', is_junk=True),
            ContactInfo('Jokeland')
        ],
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
            r"el chapo",
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

        contacts=[
            ContactInfo(
                name=BOB_CROWE,
                info="partner at Nelson Mullins",
                emailer_pattern=r"[BR]ob Crowe",
            ),
            ContactInfo(
                name=GANBAT_CHULUUNKHUU,
                info="corrupt Mongolian politician who was later wanted by Interpol",
                emailer_pattern=r"Ganbat(@|\s*Ch(uluunkhuu)?)?",
            ),
            ContactInfo('Joshua Cooper Ramo', "co-CEO of Henry Kissinger Associates"),
            ContactInfo(KATHERINE_KEATING, "daughter of former Australian prime minister"),
            ContactInfo('Khaltmaagiin Battulga', "former president of Mongolia"),
            ContactInfo(
                name=MOHAMED_WAHEED_HASSAN,
                info="former president of the Maldives",
                emailer_pattern=r"Mohamed Waheed(\s+Hassan)?",
            ),
            ContactInfo(
                name=OLIVIER_COLOM,
                info="France",
                emailer_pattern=r"Colom, Olivier|Olivier Colom",
            ),
            ContactInfo('Paul Keating', "former prime minister of Australia"),
            ContactInfo(PUREVSUREN_LUNDEG, "Mongolian ambassador to the UN"),
            ContactInfo('Stanley Rosenberg', "former President of the Massachusetts Senate")
        ],
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
            r"Boston",
            r"Brooklyn",
            r"California",
            r"Canada",
            r"Cape Cod",
            r"Charlottesville",
            r"Colorado",
            r"Connecticut",
            r"Florida",
            r"Jersey\s*City",
            r"Los Angeles",
            r"Loudoun\s*County?",
            r"Martha's\s*Vineyard",
            r"Miami(?!\s?Herald)",
            r"Nantucket",
            r"New\s*(Jersey|Mexico)",
            r"(North|South)\s*Carolina",
            r"NY(C|\s*State)",
            r"Orange\s*County",
            r"Oregon",
            r"Palo Alto",
            r"Pennsylvania",
            r"Phoenix",
            r"Portland",
            r"San Francisco",
            r"Sant[ae]\s*Fe",
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
        contacts=[
            ContactInfo(
                name=ANAS_ALRASHEED,
                info=f"former information minister of Kuwait {'(???)'}",
                emailer_pattern=r"anas\s*al\s*rashee[cd]",
            ),
            ContactInfo(AZIZA_ALAHMADI, "Abu Dhabi Department of Culture & Tourism, assistant of Al Sabbagh"),
            ContactInfo(
                name=FAWZI_SIAM,
                info="sharia auditor in Qatar, friend of Sheikh Jabor Al-Thani",
                emailer_pattern=r"Fawzi.Siam?",
            ),
            ContactInfo(RAAFAT_ALSABBAGH, "Saudi royal advisor"),
            ContactInfo(
                name=SHAHER_ABDULHAK_BESHER,
                info="Yemeni billionaire",
                emailer_pattern=r"\bShaher(\s*Abdulhak\s*Besher)?\b",
            )
        ],
        patterns=[
            r"Abdulmalik Al-Makhlafi",
            r"Abdullah",
            r"Abu\s+Dhabi",
            r"Afghanistan",
            r"Al[-\s]?Qa[ei]da",
            r"Ahmadinejad",
            r"(Rakhat )?Aliyev",
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
            r"Hourani",
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
            r"Nazarbayev",
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
            r"Timur\s*Kulibayev",
            r"Tripoli",
            r"Tunisian?",
            r"Turk(ey|ish)?(?!s & Caicos)",
            r"UAE",
            r"((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        ],
    ),
    HighlightedNames(
        label='modeling',
        style='pale_violet_red1',
        contacts=[
            ContactInfo('Abi Schwinck', f"{JEAN_LUC_BRUNEL}'s MC2 Model Management {'(???)'}"),
            ContactInfo(DANIEL_SIAD),
            ContactInfo(
                name=FAITH_KATES,
                info="Next Models co-founder",
                emailer_pattern=r"faith kates?",
            ),
            ContactInfo('Gianni Serazzi', "fashion consultant?"),
            ContactInfo(
                name=HEATHER_MANN,
                info=f"South African former model, ex-girlfriend of {PRINCE_ANDREW} (?)",
                emailer_pattern=r"Heather Mann?",
            ),
            ContactInfo(
                name=JEAN_LUC_BRUNEL,
                info="MC2 Model Management founder, died by suicide in French jail",
                emailer_pattern=r"Jean[- ]Luc Brunel?|JeanLuc",
            ),
            ContactInfo(
                name=JEFF_FULLER,
                info=f"president of {JEAN_LUC_BRUNEL}'s MC2 Model Management USA",
                emailer_pattern=r"jeff@mc2mm.com|Jeff Fuller",
            ),
            ContactInfo('lorraine@mc2mm.com', f"{JEAN_LUC_BRUNEL}'s MC2 Model Management"),
            ContactInfo(
                name='pink@mc2mm.com',
                info=f"{JEAN_LUC_BRUNEL}'s MC2 Model Management",
                emailer_pattern=r"^Pink$|pink@mc2mm\.com",
            ),
            ContactInfo(
                name=MANUELA_MARTINEZ,
                info="Mega Partners (Brazilian agency)",
                emailer_pattern=r"Manuela (- Mega Partners|Martinez)",
            ),
            ContactInfo(
                name=MARIANA_IDZKOWSKA,
                emailer_pattern=r"Mariana [Il]d[źi]kowska?",
            ),
            ContactInfo('Michael Sanka', f"{JEAN_LUC_BRUNEL}'s MC2 Model Management {'(???)'}"),
            ContactInfo('Vladimir Yudashkin', "director of the 1 Mother Agency")
        ],
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
        contacts=[
            ContactInfo(AL_SECKEL, "Isabel Maxwell's husband, Mindshift conference, fell off a cliff"),
            ContactInfo('Barnaby Marsh', "co-founder of philanthropy services company Saint Partners"),
            ContactInfo(CHRISTINA_GALBRAITH, f"{JEFFREY_EPSTEIN} VI Foundation Media/PR, worked with {TYLER_SHEARS}"),
            ContactInfo(IAN_OSBORNE, f"{IAN_OSBORNE} & Partners reputation repairer hired in 2011"),
            ContactInfo(MATTHEW_HILTZIK, "crisis PR at Hiltzik Strategies"),
            ContactInfo(
                name=MICHAEL_SITRICK,
                info="crisis PR",
                emailer_pattern=r"(Mi(chael|ke).{0,5})?[CS]itrick",
            ),
            ContactInfo('Owen Blicksilver', "OBPR, Inc."),
            ContactInfo(
                name=PEGGY_SIEGAL,
                info="socialite, movie promoter",
                emailer_pattern=r"Peggy Siegal?",
            ),
            ContactInfo('R. Couri Hay'),
            ContactInfo(
                name=ROSS_GOW,
                info="Acuity Reputation Management",
                emailer_pattern=r"Ross(acuity)? Gow|(ross@)?acuity\s*reputation(\.com)?",
            ),
            ContactInfo(
                name=TYLER_SHEARS,
                info=f"reputation management, worked on with {CHRISTINA_GALBRAITH}",
                emailer_pattern=r"T[vy]ler\s*Shears",
            )
        ],
        patterns=[
            r"(Matt(hew)? )?Hiltzi[gk]",
            r"Philip\s*Barden",
            r"PR\s*Newswire",
            REPUTATION_MGMT,
            r"Reputation.com",
            r"(Robert L\. )?Dilenschneider",
        ],
    ),
    HighlightedNames(
        label='Republican',
        style='dark_red bold',
        contacts=[
            ContactInfo('Juleanna Glover', "CEO of D.C. public affairs advisory firm Ridgely|Walsh"),
            ContactInfo(RUDY_GIULIANI),
            ContactInfo(TULSI_GABBARD)
        ],
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
            r"Darrell\s*Issa",
            r"Devin\s*Nunes",
            r"(Don\s*)?McGa[hn]n",
            r"Erik Prince",
            r"Gary\s*Cohn",
            r"George\s*(H\.?\s*)?(W\.?\s*)?Bush",
            r"(George\s*)?Nader",
            r"GOP",
            r"((Chair|Jay|Joseph)\s*)?Clayton",  # SEC chair, now SDNY
            r"((Bill|William)\s*)?Hinman"
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
            r"(Steven?\s*)?Mnuchin",
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
            r"(Roy|Stephen)\s*Moore",
            r"Tea\s*Party",
            r"Wilbur\s*Ross",
        ],
    ),
    HighlightedNames(
        label='Rothschild',
        style='indian_red',
        contacts=[
            ContactInfo(
                name=ARIANE_DE_ROTHSCHILD,
                info="heiress",
                emailer_pattern=r"AdeR|((Ariane|Edmond) (de )?)?Rothsh?ch?ild|Ariane(?!\s+Dwyer)",
            ),
            ContactInfo(
                name=JOHNNY_EL_HACHEM,
                info="Edmond de Rothschild Private Equity",
                emailer_pattern=r"el hachem johnny|johnny el hachem",
            )
        ],
        patterns=['AdR'],
    ),
    HighlightedNames(
        label='Russia',
        style='red bold',
        contacts=[
            ContactInfo(
                name=ALEKSANDRA_KARPOVA,
                info=f"{CRYPTO_PR_LAB} co-founder",
                emailer_pattern=r"Aleksandra\s*Karpova",
            ),
            ContactInfo('Dasha Zhukova', "art collector, daughter of Alexander Zhukov"),
            ContactInfo(JULIA_SANTOS, "possibly a Russian in Paris that was recruiting girls from Ukraine for Epstein"),
            ContactInfo(
                name=KARYNA_SHULIAK,
                info="Epstein's final girlfriend to whom he tried to leave $50-100 million and the island",
                emailer_pattern=r"Karyna\s*Shuliak?",
            ),
            ContactInfo(
                name='Maria Prusakova',
                info=f"AKA Masha Prusso, former Olympic snowboarder, {CRYPTO_PR_LAB} co-founder, \"found ladies\" for Epstein",
                emailer_pattern=r"Ma(sha|riy?a)\s*(Prus(kova|so))",
            ),
            ContactInfo(MASHA_DROKOVA, "silicon valley VC, former Putin Youth member"),
            ContactInfo(
                name=RENATA_BOLOTOVA,
                info="former model, fund manager at New York State Insurance Fund, Рената Болотова",
                emailer_pattern=r"Renata Bolotova|Rena B|Renata Bo\w+|renbolotova",
            ),
            ContactInfo(
                name=SERGEY_BELYAKOV,
                info="graduate of Russia's FSB academy",
                emailer_pattern=r"Sergey\s*Belyako|Беляков\s*Сергей|Cepre(ct|il) [6BES][\w.]+|6(er|of)no\w+\s+[CE]\w+",
            ),
            ContactInfo(SVETLANA_POZHIDAEVA, f"Epstein's Russian assistant who was recommended for a visa by Sergei Belyakov (FSB) and {DAVID_BLAINE}")
        ],
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
            r'(Semion\s*)?Mogilevich',
            r"Moscow",
            r"Nic(k|holas)\s*Kovarsky",  # Friend of Belyakov
            r"(Natalia\s*)?Veselnitskaya",
            r"(Oleg\s*)?Deripaska",
            r"Oleksandr Vilkul",
            r"Onexim",  # Prokhorov investment vehicle
            r"Prokhorov",
            r"Rakishev",
            r"Rosneft",
            r"RT",
            r"Ruben\s*Vardanyan",
            r"St.?\s*?Petersburg",
            r'Svet',
            r"Russ?ian?",
            r"Sberbank",
            r"Soviet(\s*Union)?",
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
        contacts=[
            ContactInfo('Alisa Bekins', f"{PETER_THIEL}'s assistant"),
            ContactInfo(
                name=ANDREW_MCCORMACK,
                info=f"partner at {PETER_THIEL}'s {VALAR_VENTURES} {'(???)'}",
                emailer_pattern=r"Andrew\s*McCorm(ack?)?",
            ),
            ContactInfo('Auren Hoffman', "CEO of SafeGraph (firm that gathers location data from mobile devices) and LiveRamp"),
            ContactInfo(ELON_MUSK, "father of Mecha-Hitler"),
            ContactInfo(
                name=GOOGLE_PLUS,
                info="Google+",
                emailer_pattern=r"Google\+",
            ),
            ContactInfo(
                name='Ian O\'Donnell',
                info=f"Thiel's {VALAR_VENTURES}",
                emailer_pattern=r"Ian O'?Donnell",
            ),
            ContactInfo(
                name=JAMES_FITZGERALD,
                info=f"{PETER_THIEL}'s {VALAR_VENTURES} {QUESTION_MARKS}",
                emailer_pattern=r"James Fitz[g ]eral?d?",
            ),
            ContactInfo(
                name='LinkedIn',
                info="LinkedIn",
                emailer_pattern=r"Linked[Il]n(\s*Updates)?",
            ),
            ContactInfo(PETER_THIEL, "Paypal mafia member, founder of Palantir, Facebook investor"),
            ContactInfo(REID_HOFFMAN, "PayPal mafia member, founder of LinkedIn"),
            ContactInfo(
                name=STEVEN_SINOFSKY,
                info="a16z, ex-Microsoft, loves bitcoin",
                emailer_pattern=r"Steven Sinofsky?",
            ),
            ContactInfo(VALAR_VENTURES, f"{PETER_THIEL} affiliated fintech venture fund"),
            ContactInfo(
                name=VINCENZO_IOZZO,
                info="CEO of the identity-security company SlashID",
                emailer_pattern=r"Vincenzo [IL]ozzo",
            ),
            ContactInfo(ZUBAIR_KHAN, f"Tranchulas cybersecurity, {'InsightsPod'} founder, Islamabad / Dubai")
        ],
        patterns=[
            r"a16z|(?<!Gavin )Andree?ss?e?[eo]n(\s&Horowitz)?",
            r"AG?I",
            r"Artificial\s*(General\s*)?Intelligence",
            r"Ben\s*Horowitz",
            r"Chamath", r"Palihapitiya",
            r"cyber\s*security",
            r"Danny\s*Hillis",
            r"deep learning",
            r"Drew\s*Houston",
            r"Eliezer\s*Yudkowsky",
            r"Erick?\s*Sc?hmidt",
            r"Facebook",
            r"Greylock(\s*Partners)?",
            r"Instagram",
            r"(?<!(ustin|Moshe)\s)Hoffmand?",
            r"(Jeff\s*)?Bezos",
            r"Larry Page",
            r"LinkedIn",
            r"(Marc\s*)?(?<!Gavin )Andreess?en",
            r"(Mark\s*)?Zuckerberg",
            r"Masa(yoshi)?(\sSon)?",
            r"Neoteny",  # Joi Ito Japanese fund?
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
            r"Valar(\s*(Global\s*Fund|Ventures))?",
            r"Vision\s*Fund",
            r"Wearality(\s*Corporation)?",
            r"WikiLeak(ed|s)",
        ],
    ),
    HighlightedNames(
        label='Trump',
        style='red3 bold',
        contacts=[
            ContactInfo('Bruce Moskowitz', "'Trump's health guy' according to Epstein"),
            ContactInfo(
                name=NICHOLAS_RIBIS,
                info=f"Hilton CEO, former president of {'Trump Organization'}",
                emailer_pattern=r"Nic(holas|k)[\s._]Ribi?s?|Ribbis",
            )
        ],
        patterns=[
            r"@?realDonaldTrump",
            r"(Alan\s*)?Weiss?elberg",
            r"Alex\s*Jones",
            r"(Brad(ley)?\s*)Parscale",
            r"\bDJ?T\b",
            r"Donald J. Tramp",
            r"(Donald\s+(J\.\s+)?)?Trump(ism|\s*(Org(anization)?|Properties)(\s*LLC)?)?",
            r"Don(ald| *Jr)(?! (B|Norman|Rubin))",
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
        contacts=[
            ContactInfo(CECILE_DE_JONGH, "Virgin Islands first lady 2007-2015"),
            ContactInfo(KENNETH_E_MAPP, "Virgin Islands Governor"),
            ContactInfo(STACEY_PLASKETT, "Virgin Islands non-voting member of Congress")
        ],
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
            r"San\s*Juan",
            r"S(ain)?t.?\s*Thomas",
            r"USVI",
            r"(?<!stein |vis-a-)VI(?!s-a-)",
            r"(The\s*)?Virgin\s*Is(al|la)nd?s(\s*Daily\s*News)?",  # Hard to make this work right
            r"(West\s*)?Palm\s*Beach(\s*County)?(?!\s*(Daily|Post))",
        ],
    ),
    HighlightedNames(
        label='victim',
        style=VICTIM_COLOR,
        contacts=[
            ContactInfo(
                name=PAULA,
                info="ex-girlfriend who works in opera now",
                emailer_pattern=r"^Paula( Heil Fisher)?$",
            )
        ],
        patterns=[
            r"child\s*pornography",
            r"(David\s*)?Bo[il]es(,?\s*Schiller( & Flexner)?)?",
            r"Ellaina\s*Astras?",
            r"(Gloria\s*)?Allred",
            r"(Jane|Tiffany)\s*Doe",
            r"Katie\s*Johnson",
            r"Minor\s*Victim",
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
        contacts=[
            ContactInfo(
                name=BRAD_EDWARDS,
                info=ROTHSTEIN_ROSENFELDT_ADLER,
                emailer_pattern=r"Brad(ley)?(\s*J(.?|ames))?\s*Edwards",
            ),
            ContactInfo(
                name=DOUGLAS_WIGDOR,
                info=f"lawsuit against {LEON_BLACK}, Wigdor LLP",
                emailer_pattern=r"Doug(las)?\s*(H\.?)?\s*Wigdor",
            ),
            ContactInfo('Grant J. Smith', ROTHSTEIN_ROSENFELDT_ADLER),
            ContactInfo(
                name=JEANNE_M_CHRISTENSEN,
                info=f"lawsuit against {LEON_BLACK}, Wigdor LLP",
                emailer_pattern=r"Jeanne\s*(M\.?)?\s*Christensen",
            ),
            ContactInfo(JACK_SCAROLA, "Searcy Denney Scarola Barnhart & Shipley"),
            ContactInfo(KEN_JENNE, ROTHSTEIN_ROSENFELDT_ADLER)
        ],
        patterns=[
            r"(Alan(\s*P.)?|MINTZ)\s*FRAADE",
            r"(J\.?\s*)?(Stan(ley)?\s*)?Pottinger",
            r"(Mi(chael|ke)\s*)?Avenatti",
            r"Paul\s*(G.\s*)?Cassell",
            r"Rothstein\s*Rosenfeldt\s*Adler",
            r"(Scott\s*)?Rothstein",
            r"Wigdor(Law)?",
        ],
    ),
    HighlightedNames(
        label=STEVE_BANNON,
        style='color(58)',
        category='Republican',
        contacts=[
            ContactInfo(
                name=SEAN_BANNON,
                info=f"{STEVE_BANNON}'s brother",
                emailer_pattern=r"sean bannon?",
            ),
            ContactInfo(
                name=STEVE_BANNON,
                info="Trump campaign manager, memecoin grifter",
                emailer_pattern=r"steve banno[nr]?",
            )
        ],
        patterns=[
            r"(American\s*)?Dharma",
            r"Biosphere",
        ],
    ),

    # Individuals
    HighlightedNames(
        contacts=[
            ContactInfo(STEVEN_HOFFENBERG, "Epstein's Towers Financial ponzi partner, prison for 18 years")
        ],
        style='dark_olive_green3',
        category=FINANCE,
        patterns=[r"(steven?\s*)?hoffenberg?w?"],
    ),
    HighlightedNames(
        label='Ghislaine',
        style='deep_pink3',
        category='Epstein',
        contacts=[
            ContactInfo(
                name=BOBBI_C_STERNHEIM,
                info=f"{GHISLAINE_MAXWELL} criminal defense attorney",
                emailer_pattern=r"Bobbi C\.? Sternheim",
            ),
            ContactInfo(
                name=GHISLAINE_MAXWELL,
                info="Epstein's girlfriend, daughter of the spy Robert Maxwell",
                emailer_pattern=r"g ?max(well)?|Ghislaine|Maxwell",
            )
        ],
        patterns=[
            r"gmax(1@ellmax.com)?",
            r"(The )?TerraMar Project",
            r"(Scott\s*)?Borgenson", # Ghislaine lawyer
        ],
    ),
    HighlightedNames(
        contacts=[
            ContactInfo(
                name=JABOR_Y,
                info="former Qatari prime minister Hamad bin Jassim AKA \"HBJ\"",
                emailer_pattern=r"[ji]abor\s*y?",
            )
        ],
        category=MIDEAST,
        style='spring_green1'
    ),
    HighlightedNames(
        contacts=[
            ContactInfo(
                name=KATHRYN_RUEMMLER,
                info="former Obama legal counsel",
                emailer_pattern=r"Kathr?yn? Ruemmler?",
            )
        ],
        style='magenta2',
        category=FRIEND
    ),
    HighlightedNames(
        contacts=[
            ContactInfo(MELANIE_WALKER, f"doctor, friend of {BILL_GATES}")
        ],
        style='pale_violet_red1',
        category=FRIEND
    ),
    HighlightedNames(
        contacts=[
            ContactInfo(
                name=PAULA,
                info="Epstein's ex-girlfriend who is now in the opera world",
                emailer_pattern=r"^Paula( Heil Fisher)?$",
            )
        ],
        label='paula',
        style='pink1',
        category=FRIEND
    ),
    HighlightedNames(
        contacts=[
            ContactInfo(
                name=PRINCE_ANDREW,
                info="British royal family",
                emailer_pattern=r"Prince Andrew|The Duke",
            )
        ],
        patterns=[r'\bPA\b'],
        style='dodger_blue1',
        category='Europe'
    ),
    HighlightedNames(
        contacts=[
            ContactInfo(
                name=SOON_YI_PREVIN,
                info="wife of Woody Allen",
                emailer_pattern=r"Soon[- ]Yi Previn?",
            )
        ],
        style='hot_pink',
        category=ARTS
    ),
    HighlightedNames(
        contacts=[
            ContactInfo(
                name='Sultan Ahmed Bin Sulayem',
                info="chairman of ports in Dubai, CEO of DP World",
                emailer_pattern=r"Sultan (Ahmed )?bin Sulaye?m?",
            )
        ],
        style='green1',
        category=MIDEAST
    ),

    # HighlightedText not HighlightedNames bc of word boundary issue
    HighlightedText(
        label='metoo',
        style=VICTIM_COLOR,
        patterns=[r"#metoo"]
    ),
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
        patterns=[r'^[>• ]{,4}(Date ?|From|Sent|To|C[cC]|Importance|Reply[- ]?To|Subject|Bee|B[cC]{2}|Attach(ed|ments)|Flag|Classification|[Il]nline-[Il]mages|((A|Debut du message transfer[&e]|De(stinataire)?|Envoye|Expe(cl|d)iteur|Objet|Q|Sujet) ?)):|^on behalf of'],
    ),
    HighlightedText(
        label='http_links',
        style=f'{ARCHIVE_LINK_COLOR} underline',
        patterns=[r"https?:[^\s]+"],
    ),
    HighlightedText(
        label='quoted_reply_line',
        style='dim',
        patterns=[
            REPLY_REGEX.pattern, r"^(> )?wrote:$",
            r"CONFIDENTIAL FOR ATTORNEY'S EYES ONLY(\nDO NOT COPY)?",
            r"PRIVILEGED ?- ?ATTORNEY WORK.*(\nCONFIDENTIAL - SUBJECT TO.*)?",
        ],
    ),
    HighlightedText(
        label='redacted',
        style='grey58',
        patterns=[fr"{REDACTED}|<?Privileged - Redacted>?"],
    ),
    HighlightedText(
        label='sent_from',
        style='light_cyan3 italic dim',
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
        pattern=r"^(> )?(Attach(ed|ments)|[Il]nline-[Il]mages): (?P<email_attachments>.*)",
    ),
    ManualHighlight(
        label='email_timestamp',
        style=TIMESTAMP_STYLE,
        pattern=r"^(> )?(Date|Sent): (?P<email_timestamp>.*)",
    ),
]

ALL_HIGHLIGHTS = HIGHLIGHTED_NAMES + HIGHLIGHTED_TEXTS
JUNK_HIGHLIGHTS: HighlightedNames = [hn for hn in HIGHLIGHTED_NAMES if hn.label == JUNK][0]
JUNK_EMAILERS = [contact.name for contact in JUNK_HIGHLIGHTS.contacts]


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
