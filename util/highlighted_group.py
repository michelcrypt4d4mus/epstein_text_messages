import re
from dataclasses import dataclass, field

from util.constants import *
from util.env import is_debug, logger

REGEX_STYLE_PREFIX = 'regex'

UNSPLITTABLE_NAMES = [
    JEREMY_RUBIN,
]

NAMES_TO_NOT_HIGHLIGHT: list[str] = [name.lower() for name in [
    'Allen',
    'Amanda',
    'Andres',
    'Andrew',
    'Black',
    'Brad',
    'Daniel',
    'Darren',
    'David',
    'Etienne',
    'Jeff',
    'jeffrey',
    'John',
    'Jonathan',
    'Joseph',
    'Kahn',
    'Jr',
    'JR.',
    'Le',
    'Leon',
    'Marc',
    'Martin',
    'Melanie',
    'Michael',
    'Paul',
    'Pen',
    'Peter',
    'Reid',
    'Richard',
    'Robert',
    'Roger',
    'Rubin',
    'Scott',
    'Sean',
    'Stephen',
    'Steve',
    'Steven',
    'Stone',
    'Susan',
    'The',
    'Thomas',
    'Tom',
    'Victor',
    "Y",
    "Y.",
]]

emailer_pattern = lambda name: EMAILER_REGEXES[name].pattern if name in EMAILER_REGEXES else name
highlighter_style_name = lambda style_name: f"{REGEX_STYLE_PREFIX}.{style_name.replace(' ', '_')}"


@dataclass
class HighlightedGroup:
    label: str
    style: str
    pattern: str = ''
    emailers: list[str] = field(default_factory=list)
    is_multiline: bool = False
    regex: re.Pattern = field(init=False)


    def __post_init__(self):
        patterns = [self.emailer_pattern(e) for e in self.emailers] + ([self.pattern] if self.pattern else [])
        pattern = '|'.join(patterns)

        if self.label in ['bank']:
            logger.warning(f"'{self.label}' pattern:\n{pattern}")

        if self.is_multiline:
            self.regex = re.compile(fr"(?P<{self.label}>{pattern})", re.IGNORECASE | re.MULTILINE)
        else:
            self.regex = re.compile(fr"\b(?P<{self.label}>({pattern})s?)\b", re.IGNORECASE)

    # TODO: handle word boundary issue for names that end in symbols
    def emailer_pattern(self, name: str) -> str:
        if name in EMAILER_REGEXES:
            return EMAILER_REGEXES[name].pattern
        elif name in UNSPLITTABLE_NAMES or ' ' not in name:
            return name

        names = name.split()
        first_name = ' '.join(names[0:-1])
        last_name = names[-1]
        name_regex_parts = [n for n in [name, first_name, last_name] if n not in NAMES_TO_NOT_HIGHLIGHT]

        if len(names) > 2:
            logger.warning(f"'{name}' has {len(names)} names (first_name='{first_name}')")

        return '|'.join(name_regex_parts)


HIGHLIGHTED_GROUPS = [
    HighlightedGroup(
        label='bank',
        style='green',
        pattern='Apollo|Black(rock|stone)|DB|Deutsche Bank|Goldman( ?Sachs)|HSBC|(Janet\\s*)?Yellen|(Jide\\s*)?Zeitlin|(Jerome\\s*)?Powell|Jes\\s+Staley|Merrill\\s+Lynch|Morgan Stanley|j\\.?p\\.?\\s*morgan( Chase)?|Chase Bank|us.gio@jpmorgan.com|Marc\\s*Leon',
        emailers=[
            ALIREZA_ITTIHADIEH,
            AMANDA_ENS,
            DANIEL_SABBA,
            LEON_BLACK,
            PAUL_MORRIS,
            PAUL_BARRETT,
        ]
    ),
    HighlightedGroup(
        label='bitcoin',
        style='orange1 bold',
        pattern='bitcoin|block ?chain( capital)?|Brock|coins|cr[iy]?pto(currency)?|e-currency|(Howard\\s+)?Lutnick|(jeffrey\\s+)?wernick|Libra|SpanCash|Tether|(zero\\s+knowledge\\s+|zk)pro(of|tocols?)',
        emailers = [
            JEREMY_RUBIN,
            SCARAMUCCI,
        ],
    ),
    HighlightedGroup(
        label='bro',
        style='tan',
        emailers=[JONATHAN_FARKAS, TOM_BARRACK]
    ),
    HighlightedGroup(
        label='business',
        style='spring_green4',
        pattern='Marc Rich|(Steve\\s+)?Wynn|(Leslie\\s+)?Wexner',
        emailers=[
            BARBRO_EHNBOM,
            BORIS_NIKOLIC,
            NICHOLAS_RIBIS,
            ROBERT_LAWRENCE_KUHN,
            STEPHEN_HANSON,
            TERRY_KAFKA,
            TOM_PRITZKER,
        ]
    ),
    HighlightedGroup(
        label='china',
        style='bright_red',
        pattern='Beijing|CCP|Chin(a|ese)|Gino Yu|Guo|Kwok|Tai(pei|wan)|Peking|PRC|xi',
    ),
    HighlightedGroup(
        label='deepak_chopra',
        style='dark_goldenrod',
        pattern='(Deepak )?Chopra|Deepak|Carolyn Rangel',
    ),
    HighlightedGroup(
        label='democrats',
        style='sky_blue1',
        pattern='Biden|(Bill )?Clinton|Hillary|Democrat(ic)?|(John )?Kerry|Maxine\\s*Waters|(Barack )?Obama|(Nancy )?Pelosi|Ron\\s*Dellums',
    ),
    HighlightedGroup(
        label='dubin',
        style='medium_orchid1',
        pattern='((Celina|Eva( Anderss?on)?|Glenn) )?Dubin',
        emailers=[]
    ),
    HighlightedGroup(
        label='employee',
        style='deep_sky_blue4',
        emailers=[
            LAWRANCE_VISOSKI,
            LESLEY_GROFF,
            NADIA_MARCINKO,
        ]
    ),
    HighlightedGroup(
        label='entertainers',
        style='light_steel_blue3',
        pattern='Andres Serrano|Bill Siegel|Bobby slayton|David Blaine|Etienne Binant|Ramsey Elkholy|Steven Gaydos?|Woody( Allen)?',
    ),
    HighlightedGroup(
        label='europe',
        style='light_sky_blue3',
        pattern='Miro(slav)?|(Caroline|Jack)?\\s*Lang(, Caroline)?|Le\\s*Pen|Macron|(Angela )?Merk(el|le)|(Sebastian )?Kurz|(Vi(c|k)tor\\s+)?Orbah?n|Edward Rod Larsen|Ukrain(e|ian)|Zug|(Thor.{3,8})?Jag[il]and?',
        emailers=[
            MIROSLAV_LAJCAK,
            PETER_MANDELSON,
            TERJE_ROD_LARSEN,
        ]
    ),
    HighlightedGroup(
        label='harvard',
        style='deep_pink2',
        pattern='Harvard|MIT( Media Lab)?|Media Lab|(La(wrence|rry).{1,5})?Summers?|^LH$|LHS|Ihsofficel|Martin.*?Nowak|Nowak, Martin',
        emailers=[LISA_NEW]
    ),
    HighlightedGroup(
        label='india',
        style='bright_green',
        pattern='Ambani|Hardeep( puree)?|Indian?|Modi|mumbai|Zubair( Khan)?',
        emailers=[ANIL_AMBANI, VINIT_SAHNI]
    ),
    HighlightedGroup(
        label='israel',
        style='dodger_blue2',
        pattern='Bibi|(eh|(Ehud|Nili Priell) )?barak|Mossad|Netanyahu|Israeli?',
    ),
    HighlightedGroup(
        label='javanka',
        style='medium_violet_red',
        pattern='Ivanka( Trump)?|(Jared )?Kushner|Jared',
    ),
    HighlightedGroup(
        label='journalist',
        style='bright_yellow',
        pattern='Alex Yablon|Edward (Jay )?Epstein|lando[nr] thomas|thomas jr.?, lando[nr]|Paul Krassner|Wolff|Susan Edelman|[-\\w.]+@(bbc|independent|mailonline|mirror|thetimes)\\.co\\.uk',
        emailers=[MICHAEL_WOLFF]
    ),
    HighlightedGroup(
        label='lawyer',
        style='medium_purple2',
        pattern='(Erika )?Kellerhals|(Ken(neth W.)?\\s+)?Starr|Lefkowitz|Michael J. Pike|Paul Weiss|Weinberg|Weingarten|Roy Black',
        emailers=[
            ALAN_DERSHOWITZ,
            DARREN_INDYKE,
            BRAD_KARP,
            DAVID_STERN,
            DAVID_SCHOEN,
            JACK_GOLDBERGER,
            JAY_LEFKOWITZ,
            LILLY_SANCHEZ,
            MARTIN_WEINBERG,
            REID_WEINGARTEN,
            RICHARD_KAHN,
            SCOTT_J_LINK
        ]
    ),
    HighlightedGroup(
        label='lobbyist',
        style='light_coral',
        pattern='Purevsuren Lundeg|Rob Crowe|Stanley Rosenberg',
        emailers=[
            OLIVIER_COLOM,
        ]
    ),
    HighlightedGroup(
        label='middle_east',
        style='dark_sea_green4',
        pattern='Abdulmalik Al-Makhlafi|Abu\\s+Dhabi|Anas Alrasheed|Assad|Aziza Alahmadi|Dubai|Emir(ates)?|Erdogan|Gaddafi|HBJ|Imran Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\\s+bin\\s+Salman|Muslim|Pakistani?|Raafat\\s*Alsabbagh|Riya(dh|nd)|Saudi(\\s+Arabian?)?|Shaher( Abdulhak Besher)?|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)',
        emailers=[
            ANAS_ALRASHEED,
            AZIZA_ALAHMADI,
            MOHAMED_WAHEED_HASSAN,
        ]
    ),
    HighlightedGroup(
        label='modeling',
        style='pale_violet_red1',
        pattern=r'\w+@mc2mm.com',
        emailers=[
            DANIEL_SIAD,
            FAITH_KATES,
            JEAN_LUC_BRUNEL,
            MARIANA_IDZKOWSKA,
        ]
    ),
    HighlightedGroup(
        label='police',
        style='color(24)',
        pattern='Ann Marie Villafana|(James )?Comey|Kirk Blouin|((Bob|Robert) )?Mueller|Police Code Enforcement',
        emailers=[]
    ),
    HighlightedGroup(
        label='publicist',
        style='orange_red1',
        pattern='Henry Holt|Ian Osborne|Matthew Hiltzik|ross@acuityreputation.com|Citrick',
        emailers=[
            AL_SECKEL,
            CHRISTINA_GALBRAITH,
            MICHAEL_SITRICK,
            PEGGY_SIEGAL,
            TYLER_SHEARS,
        ]
    ),
    HighlightedGroup(
        label='republicans',
        style='dark_red',
        pattern='bolton|Broidy|(?!Merwin Dela )Cruz|kudlow|lewandowski|mattis|mnuchin|(Paul )?Manafort|Pompeo|Republican',
    ),
    HighlightedGroup(
        label='russia',
        style='red bold',
        pattern=r'GRU|FSB|Lavrov|Masha\s*Drokova|Moscow|(Oleg )?Deripaska|(Vladimir )?Putin|Russian?|Rybolo(olev|vlev)|Vladimir Yudashkin',
    ),
    HighlightedGroup(
        label='scholar',
        style='light_goldenrod2',
        pattern='((Noam|Valeria) )?Chomsky|David Grosof|Joscha|Bach|Moshe Hoffman|Peter Attia|Trivers',
        emailers=[
            DAVID_HAIG,
            JOSCHA_BACH,
            LAWRENCE_KRAUSS,
            ROBERT_TRIVERS,
            STEVEN_PFEIFFER,
        ]
    ),
    HighlightedGroup(
        label='south_america',
        style='yellow',
        pattern='Argentina|Bra[sz]il(ian)?|Bolsonar[aio]|Lula|(Nicolas )?Maduro|Venezuelan?s?',
    ),
    HighlightedGroup(
        label='tech_bro',
        style='cyan2',
        pattern='Elon|Musk|Masa(yoshi)?( Son)?|Najeev|(Peter )?Th(ie|ei)l|Softbank',
        emailers=[
            REID_HOFFMAN,
            STEVEN_SINOFSKY
        ]
    ),
    HighlightedGroup(
        label='trump',
        style='red3 bold',
        pattern='DJT|(Donald\\s+(J\\.\\s+)?)?Trump|Don(ald| Jr)(?! Rubin)|(Matt(hew)? )?Calamari|Roger\\s+Stone',
    ),
    HighlightedGroup(
        label='victim',
        style='orchid1',
        pattern='(Virginia\\s+((L\\.?|Roberts)\\s+)?)?Giuffre|Virginia\\s+Roberts',
    ),
    HighlightedGroup(
        label='virgin_islands',
        style='sea_green1',
        pattern='Cecile de Jongh|(Kenneth E\\. )?Mapp',
        emailers=[
            STACY_PLASKETT,
        ]
    ),
    HighlightedGroup(
        label='ariane_de_rothschild',
        style='indian_red',
        emailers=[ARIANE_DE_ROTHSCHILD]
    ),
    HighlightedGroup(
        label='bannon',
        style='color(58)',
        pattern='((Steve|Sean)\\s+)?Bannon',
    ),
    HighlightedGroup(
        label='bill_gates',
        style='turquoise4',
        pattern='BG|(Bill\\s+((and|or)\\s+Melinda\\s+)?)?Gates|Melinda(\\s+Gates)?',
    ),
    HighlightedGroup(
        label='ghislaine_maxwell',
        style='deep_pink3',
        pattern='Ghislaine|Maxwell|GMAX|gmax1@ellmax.com',
    ),
    HighlightedGroup(
        label='jabor_y',
        style='spring_green1',
        emailers=[JABOR_Y]
    ),
    HighlightedGroup(
        label='jeffrey_epstein',
        style='blue1',
        pattern='Mark (L. )?Epstein',
        emailers=[JEFFREY_EPSTEIN]
    ),
    HighlightedGroup(
        label='joi_ito',
        style='blue_violet',
        emailers=[JOI_ITO]
    ),
    HighlightedGroup(
        label='kathy_ruemmler',
        style='magenta2',
        emailers=[KATHY_RUEMMLER]
    ),
    HighlightedGroup(
        label='linda_stone',
        style='pink3',
        emailers=[LINDA_STONE]
    ),
    HighlightedGroup(
        label='melanie_spinella',
        style='magenta3',
        emailers=[MELANIE_SPINELLA]
    ),
    HighlightedGroup(
        label='melanie_walker',
        style='light_pink3',
        emailers=[MELANIE_WALKER]
    ),
    HighlightedGroup(
        label='paula',
        style='pink1',
        emailers=[PAULA]
    ),
    HighlightedGroup(
        label='prince_andrew',
        style='dodger_blue1',
        emailers=[PRINCE_ANDREW]
    ),
    HighlightedGroup(
        label='soon_yi',
        style='hot_pink',
        emailers=[SOON_YI]
    ),
    HighlightedGroup(
        label='sultan_bin_sulayem',
        style='green1',
        emailers=[SULTAN_BIN_SULAYEM]
    ),

    # Regexes for things other than names
    HighlightedGroup(
        label='header_field',
        style='plum4',
        pattern='^(Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):',
        is_multiline=True,
    ),
    HighlightedGroup(
        label='redacted',
        style='grey58',
        pattern=REDACTED,
        is_multiline=True,
    ),
    HighlightedGroup(
        label='sent_from',
        style='gray42 italic',
        pattern=SENT_FROM_REGEX.pattern,
        is_multiline=True,
    ),
    HighlightedGroup(
        label='snipped_signature',
        style='gray19',
        pattern=r'<\.\.\.(snipped|trimmed).*\.\.\.>',
        is_multiline=True,
    ),
    HighlightedGroup(
        label='timestamp_2',
        style='dark_cyan',
        pattern=r"\d{1,4}[-/]\d{1,2}[-/]\d{2,4} \d{1,2}:\d{2}:\d{2}( [AP]M)?",
        is_multiline=True,
    ),
    HighlightedGroup(
        label='unknown',
        style='cyan',
        pattern=r'\(unknown\)',
        is_multiline=True,
    ),
]


if is_debug:
    for hg in HIGHLIGHTED_GROUPS:
        print(hg)
        print("\n")
