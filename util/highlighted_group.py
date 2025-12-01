import re
from dataclasses import dataclass, field

from rich.text import Text

from util.constants import *
from util.env import is_debug, logger

REGEX_STYLE_PREFIX = 'regex'

UNSPLITTABLE_NAMES = [
    JEREMY_RUBIN,
]


@dataclass
class HighlightedGroup:
    style: str
    label: str = ''      # TODO: make it default to None?
    pattern: str = ''    # TODO: make it default to None?
    emailers: list[str] = field(default_factory=list)
    is_multiline: bool = False
    regex: re.Pattern = field(init=False)
    style_name: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            if len(self.emailers) != 1:
                raise RuntimeError(f"No label provided for {repr(self)}")
            else:
                self.label = self.emailers[0].lower().replace(' ', '_').replace('-', '_')

        self.style_name = f"{REGEX_STYLE_PREFIX}.{self.label.replace(' ', '_')}"
        patterns = [self.emailer_pattern(e) for e in self.emailers] + ([self.pattern] if self.pattern else [])
        pattern = '|'.join(patterns)
        logger.debug('')
        logger.debug(f"'{self.label}' pattern:\n{pattern}")

        if self.is_multiline:
            self.regex = re.compile(fr"(?P<{self.label}>{pattern})", re.IGNORECASE | re.MULTILINE)
        else:
            self.regex = re.compile(fr"\b(?P<{self.label}>({pattern})s?)\b", re.IGNORECASE)

    def colored_label(self) -> Text:
        return Text(self.label.replace('_', ' '), style=self.style)

    # TODO: handle word boundary issue for names that end in symbols
    def emailer_pattern(self, name: str) -> str:
        logger.debug(f"emailer_pattern() called for '{name}'")

        if name in EMAILER_ID_REGEXES:
            return EMAILER_ID_REGEXES[name].pattern
        elif name in UNSPLITTABLE_NAMES or ' ' not in name:
            return name

        names = name.split()
        first_name = ' '.join(names[0:-1])
        last_name = names[-1]
        name_patterns = [name.replace(' ', r"\s+"), first_name, last_name]
        name_regex_parts = [n for n in name_patterns if n.lower() not in NAMES_TO_NOT_HIGHLIGHT]
        logger.debug(f"name_regex_parts for '{name}': {name_regex_parts}")

        if len(names) > 2:
            logger.warning(f"'{name}' has {len(names)} names (first_name='{first_name}')")

        return '|'.join(name_regex_parts)


HIGHLIGHTED_GROUPS = [
    HighlightedGroup(
        label='bank',
        style='green',
        pattern=r'Apollo|Black(rock|stone)|DB|Deutsche Bank|Goldman( ?Sachs)|HSBC|(Janet\s*)?Yellen|(Jerome\s*)?Powell|Jes\s+Staley|Merrill\s+Lynch|Morgan Stanley|j\.?p\.?\s*morgan( Chase)?|Chase Bank|us.gio@jpmorgan.com|Marc\s*Leon',
        emailers=[
            ALIREZA_ITTIHADIEH,
            AMANDA_ENS,
            DANIEL_SABBA,
            JIDE_ZEITLIN,
            LEON_BLACK,
            PAUL_MORRIS,
            PAUL_BARRETT,
        ]
    ),
    HighlightedGroup(
        label='bitcoin',
        style='orange1 bold',
        pattern=r'bitcoin|block ?chain( capital)?|Brock|coins|cr[iy]?pto(currency)?|e-currency|(Howard\s+)?Lutnick|(jeffrey\s+)?wernick|Libra|SpanCash|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)',
        emailers = [
            JEREMY_RUBIN,
            SCARAMUCCI,
        ],
    ),
    HighlightedGroup(
        label='bro',
        style='tan',
        emailers=[
            JONATHAN_FARKAS,
            TOM_BARRACK,
        ]
    ),
    HighlightedGroup(
        label='business',
        style='spring_green4',
        pattern=r'Marc Rich|(Steve\s+)?Wynn|(Leslie\s+)?Wexner',
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
        pattern=r"Beijing|CCP|Chin(a|ese)|Gino\s+Yu|Global Times|Guo|Jack\s+Ma|Kwok|Tai(pei|wan)|Peking|PRC|xi",
    ),
    HighlightedGroup(
        label='deepak_chopra',
        style='dark_goldenrod',
        pattern='Carolyn Rangel',
        emailers = [
            DEEPAK_CHOPRA,
        ]
    ),
    HighlightedGroup(
        label='democrats',
        style='sky_blue1',
        pattern=r'Biden|((Bill|Hillary) )?Clinton|DNC|(George )?Soros|Hill?ary|Democrat(ic)?|(John )?Kerry|Maxine\s*Waters|(Barac?k )?Obama|(Nancy )?Pelosi|Ron\s*Dellums',
    ),
    HighlightedGroup(
        label='dubin',
        style='medium_orchid1',
        pattern='((Celina|Eva( Anderss?on)?|Glenn) )?Dubin',
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
        pattern=r'(Caroline|Jack)?\s*Lang(, Caroline)?|Le\s*Pen|Macron|(Angela )?Merk(el|le)|(Sebastian )?Kurz|(Vi(c|k)tor\s+)?Orbah?n|Edward Rod Larsen|Ukrain(e|ian)|Zug',
        emailers=[
            MIROSLAV_LAJCAK,
            PETER_MANDELSON,
            TERJE_ROD_LARSEN,
            THORBJORN_JAGLAND,
        ]
    ),
    HighlightedGroup(
        label='harvard',
        style='deep_pink2',
        pattern=r'Harvard|MIT(\s*Media\s*Lab)?|Media\s*Lab|Stanford',
        emailers=[
            LARRY_SUMMERS,
            LISA_NEW,
            MARTIN_NOWAK,
        ]
    ),
    HighlightedGroup(
        label='india',
        style='bright_green',
        pattern='Hardeep( puree)?|Indian?|Modi|mumbai|Zubair( Khan)?',
        emailers=[
            ANIL_AMBANI,
            VINIT_SAHNI,
        ]
    ),
    HighlightedGroup(
        label='israel',
        style='dodger_blue2',
        pattern='Bibi|(eh|(Ehud|Nili Priell) )?barak|Mossad|Netanyahu|Israeli?',
    ),
    HighlightedGroup(
        label='javanka',
        style='medium_violet_red',
        emailers=[
            IVANKA,
            JARED_KUSHNER,
        ]
    ),
    HighlightedGroup(
        label='journalist',
        style='bright_yellow',
        pattern=r'Alex Yablon|Susan Edelman|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk',
        emailers=[
            EDWARD_EPSTEIN,
            LANDON_THOMAS,
            MICHAEL_WOLFF,
            PAUL_KRASSNER,
        ]
    ),
    HighlightedGroup(
        label='lawyer',
        style='medium_purple2',
        pattern='(Erika )?Kellerhals|Michael J. Pike|Paul Weiss|Weinberg|Weingarten|Roy Black',
        emailers=[
            ALAN_DERSHOWITZ,
            DARREN_INDYKE,
            BRAD_KARP,
            DAVID_STERN,
            DAVID_SCHOEN,
            JACK_GOLDBERGER,
            JACKIE_PERCZEK,
            JAY_LEFKOWITZ,
            JESSICA_CADWELL,
            KEN_STARR,
            LILLY_SANCHEZ,
            MARTIN_WEINBERG,
            REID_WEINGARTEN,
            RICHARD_KAHN,
            SCOTT_J_LINK,
            TONJA_HADDAD_COLEMAN,
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
        label='mideast',
        style='dark_sea_green4',
        pattern=r"Abdulmalik Al-Makhlafi|Abu\s+Dhabi|Assad|Bahrain|Dubai|Emir(ates)?|Erdogan|Gaddafi|HBJ|Imran\s+Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|kasshohgi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Pakistani?|Riya(dh|nd)|Saudi(\s+Arabian?)?|Shaher( Abdulhak Besher)?|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        emailers=[
            ANAS_ALRASHEED,
            AZIZA_ALAHMADI,
            MOHAMED_WAHEED_HASSAN,
            RAAFAT_ALSABBAGH,
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
        pattern='(Ann Marie )?Villafana|FBI|(James )?Comey|(Kirk )?Blouin|((Bob|Robert) )?Mueller|Police Code Enforcement',
    ),
    HighlightedGroup(
        label='publicist',
        style='orange_red1',
        pattern='Henry Holt|Ian Osborne|Matthew Hiltzik|ross@acuityreputation.com',
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
        style='bold dark_red',
        pattern=r'(Alex )?Acosta|Bolton|Broidy|GOP|(?<!Merwin Dela )Cruz|Kobach|Kolfage|Kudlow|Lewandowski|(Marco )?Rubio|mattis|mnuchin|(Paul\s+)?Manafort|(Peter )?Navarro|Pompeo|Republican',
        emailers = [
            RUDY_GIULIANI,
            TULSI_GABBARD,
        ]
    ),
    HighlightedGroup(
        label='russia',
        style='red bold',
        pattern=r'GRU|FSB|Lavrov|Moscow|(Oleg )?Deripaska|(Vladimir )?Putin|Russian?|Rybolo(olev|vlev)|Vladimir Yudashkin',
        emailers = [
            MASHA_DROKOVA,
        ]
    ),
    HighlightedGroup(
        label='scholar',
        style='light_goldenrod2',
        pattern='((Noam|Valeria) )?Chomsky|David Grosof|Moshe Hoffman|Peter Attia',
        emailers=[
            DAVID_HAIG,
            JOSCHA_BACH,
            LAWRENCE_KRAUSS,
            ROBERT_TRIVERS,
            ROGER_SCHANK,
            STEVEN_PFEIFFER,
        ]
    ),
    HighlightedGroup(
        label='south_america',
        style='yellow',
        pattern=r'Argentina|Bra[sz]il(ian)?|Bolsonar[aio]|Bukele|Caracas|El\s*Salvador|Lula|(Nicolas )?Maduro|Venezuelan?',
    ),
    HighlightedGroup(
        label='tech_bro',
        style='cyan2',
        pattern='Masa(yoshi)?( Son)?|Najeev|(Peter )?Th(ie|ei)l|Softbank',
        emailers=[
            ELON_MUSK,
            REID_HOFFMAN,
            STEVEN_SINOFSKY,
        ]
    ),
    HighlightedGroup(
        label='trump',
        style='red3 bold',
        pattern=r"@?realDonaldTrump|DJT|(Donald\s+(J\.\s+)?)?Trump|Don(ald| Jr)(?! Rubin)|Mar[- ]*a[- ]*Lago|(Matt(hew)? )?Calamari|Roger\s+Stone",
    ),
    HighlightedGroup(
        label='victim',
        style='orchid1',
        pattern=r'(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts',
    ),
    HighlightedGroup(
        label='virgin_islands',
        style='sea_green1',
        pattern=r'Cecile de Jongh|(Kenneth E\. )?Mapp',
        emailers=[
            STACEY_PLASKETT,
        ]
    ),

    # Individuals
    HighlightedGroup(
        label='bannon',
        style='color(58)',
        pattern=r'((Steve|Sean)\s+)?Bannon?',
    ),
    HighlightedGroup(
        label='bill_gates',
        style='turquoise4',
        pattern=r'BG|(Bill\s+((and|or)\s+Melinda\s+)?)?Gates|Melinda(\s+Gates)?',
    ),
    HighlightedGroup(
        emailers=[GHISLAINE_MAXWELL],
        style='deep_pink3',
        pattern='gmax(1@ellmax.com)?',
    ),
    HighlightedGroup(
        emailers=[JEFFREY_EPSTEIN],
        style='blue1',
        pattern='Mark (L. )?Epstein',
    ),
    HighlightedGroup(emailers=[ARIANE_DE_ROTHSCHILD], style='indian_red'),
    HighlightedGroup(emailers=[JABOR_Y], style='spring_green1'),
    HighlightedGroup(emailers=[JOI_ITO], style='blue_violet'),
    HighlightedGroup(emailers=[KATHY_RUEMMLER], style='magenta2'),
    HighlightedGroup(emailers=[LINDA_STONE], style='pink3'),
    HighlightedGroup(emailers=[MELANIE_SPINELLA], style='magenta3'),
    HighlightedGroup(emailers=[MELANIE_WALKER], style='light_pink3'),
    HighlightedGroup(emailers=[PAULA], style='pink1'),
    HighlightedGroup(emailers=[PRINCE_ANDREW], style='dodger_blue1'),
    HighlightedGroup(emailers=[SOON_YI], style='hot_pink'),
    HighlightedGroup(emailers=[STEVEN_HOFFENBERG], pattern=r'(steven?\s*)?hoffenberg?w?', style='spring_green3 bold'),
    HighlightedGroup(emailers=[SULTAN_BIN_SULAYEM], style='green1'),

    # Highlight regexes for things other than names
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
        label='quoted_reply_line',
        style='dim',
        pattern=REPLY_REGEX.pattern,
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

COLOR_KEYS = [h.colored_label() for h in HIGHLIGHTED_GROUPS if not h.is_multiline]


if is_debug:
    for hg in HIGHLIGHTED_GROUPS:
        print(hg)
        print("\n")
