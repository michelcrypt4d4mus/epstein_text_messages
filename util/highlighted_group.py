import re
from dataclasses import dataclass, field

from inflection import titleize
from rich.text import Text

from util.constants import *
from util.env import is_debug, logger

ESTATE_EXECUTOR = 'Epstein estate executor'
REGEX_STYLE_PREFIX = 'regex'
NO_CATEGORY_LABELS = [BILL_GATES, STEVE_BANNON]

# Keyed by the 'label' property
PEOPLE_INFO = {
    AL_SECKEL: 'husband of Isabel Maxwell, Mind State organizer, fell off a cliff',
    AZIZA_ALAHMADI: 'Abu Dhabi Department of Culture & Tourism',
    BARBRO_EHNBOM: 'Swedish pharmaceuticals',
    BILL_SIEGEL: 'documentary film producer and director',
    BORIS_NIKOLIC: f'Biotech VC, {ESTATE_EXECUTOR}',
    DANIEL_SABBA: 'UBS Investment Bank',
    DARREN_INDYKE: ESTATE_EXECUTOR,
    EHUD_BARAK: 'former primer minister',
    GLENN_DUBIN: "Highbridge Capital Management, married to Epstein's ex-gf Eva",
    GWENDOLYN_BECK: 'fund manager',
    JEAN_HUGUEN: 'interior design at Alberto Pinto Cabinet',
    'Linda Pinto': 'interior design at Alberto Pinto Cabinet',
    JEAN_LUC_BRUNEL: 'died by suicide in French prison',
    JES_STALEY: 'former CEO of Barclays',
    JIDE_ZEITLIN: 'former partner at Goldman Sachs, allegations of sexual misconduct',
    KATHERINE_KEATING: 'Daughter of former Australian PM',
    KENNETH_E_MAPP: 'Governor',
    LANDON_THOMAS: 'New York Times',
    LAWRANCE_VISOSKI: 'Pilot',
    JOSCHA_BACH: 'cognitive science / AI research',
    LEON_BLACK: 'Apollo CEO',
    LESLEY_GROFF: 'Assistant (?)',
    LISA_NEW: 'poetry',
    MARK_EPSTEIN: 'brother',
    'Nili Priell Barak': f'wife of {EHUD_BARAK}',
    MASHA_DROKOVA: 'silicon valley VC',
    MIROSLAV_LAJCAK: 'Russia friendly Slovak',
    MOHAMED_WAHEED_HASSAN: 'former president of the Maldives',
    NADIA_MARCINKO: 'Pilot',
    NICHOLAS_RIBIS: 'Hilton CEO',
    PAUL_KRASSNER: '60s guy',
    PUREVSUREN_LUNDEG: 'Mongolian ambassador to the UN',
    RICHARD_KAHN: ESTATE_EXECUTOR,
    ROBERT_TRIVERS: 'evolutionary biology',
    TERRY_KAFKA: 'CEO of Impact Outdoor (highway billboards)',
    TOM_BARRACK: 'long time friend of Trump',
    TOM_PRITZKER: 'brother of J.B. Pritzker',
}

safe_style_name = lambda label: label.lower().replace(' ', '_').replace('-', '_')


@dataclass
class HighlightedGroup:
    style: str
    label: str = ''      # TODO: make it default to None?
    pattern: str = ''    # TODO: make it default to None?
    emailers: list[str] = field(default_factory=list)
    has_no_category: bool = False
    info: str | None = None
    is_multiline: bool = False
    regex: re.Pattern = field(init=False)
    style_name: str = field(init=False)
    style_suffix: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            if len(self.emailers) != 1:
                raise RuntimeError(f"No label provided for {repr(self)}")
            else:
                self.label = self.emailers[0]
                self.has_no_category = True

        self.style_suffix = safe_style_name(self.label)
        self.style_name = f"{REGEX_STYLE_PREFIX}.{self.style_suffix}"
        patterns = [self.emailer_pattern(e) for e in self.emailers] + ([self.pattern] if self.pattern else [])
        pattern = '|'.join(patterns)

        if self.is_multiline:
            self.regex = re.compile(fr"(?P<{self.style_suffix}>{pattern})", re.IGNORECASE | re.MULTILINE)
            self.has_no_category = True
        else:
            self.regex = re.compile(fr"\b(?P<{self.style_suffix}>({pattern})s?)\b", re.IGNORECASE)

    def get_info(self) -> str | None:
        if self.info:
            return self.info
        elif self.has_no_category:
            return None
        else:
            return titleize(self.label)

    def colored_label(self) -> Text:
        return Text(self.label.replace('_', ' '), style=self.style)

    # TODO: handle word boundary issue for names that end in symbols
    def emailer_pattern(self, name: str) -> str:
        logger.debug(f"emailer_pattern() called for '{name}'")

        if name in EMAILER_ID_REGEXES:
            return EMAILER_ID_REGEXES[name].pattern
        elif ' ' not in name:
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
        label='finance',
        style='green',
        pattern=r'Apollo|Black(rock|stone)|DB|Deutsche\s*Bank|Goldman( ?Sachs)|HSBC|(Janet\s*)?Yellen|(Jerome\s*)?Powell|Jes\s+Staley|Merrill\s+Lynch|Morgan Stanley|j\.?p\.?\s*morgan( Chase)?|Chase Bank|us.gio@jpmorgan.com',
        emailers=[
            ALIREZA_ITTIHADIEH,
            AMANDA_ENS,
            DANIEL_SABBA,
            JIDE_ZEITLIN,
            LEON_BLACK,
            MARC_LEON,
            'Mortimer Zuckerman',  # Business partner
            PAUL_BARRETT,
            PAUL_MORRIS,
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
        pattern=r'Biden|((Bill|Hillary)\s*)?Clinton|DNC|(George\s*)?Soros|Hill?ary|Democrat(ic)?|(John\s*)?Kerry|Maxine\s*Waters|(Barac?k )?Obama|(Nancy )?Pelosi|Ron\s*Dellums',
    ),
    HighlightedGroup(
        label='dubin family',
        style='medium_orchid1',
        pattern='((Celina|Eva( Anderss?on)?|Glenn) )?Dubin',
        emailers=[EVA],
    ),
    HighlightedGroup(
        label='employee',
        style='deep_sky_blue4',
        emailers=[
            GWENDOLYN_BECK,
            LAWRANCE_VISOSKI,
            LESLEY_GROFF,
            JEAN_HUGUEN,
            'Linda Pinto',
            NADIA_MARCINKO,
        ]
    ),
    HighlightedGroup(
        label='entertainer',
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
        pattern=r'Alex Yablon|Ingram, David|Susan Edelman|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk',
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
        pattern=r'(Erika\s+)?Kellerhals|Michael J. Pike|Paul\sWeiss|Roy Black|Wein(berg|garten)',
        emailers=[
            BENNET_MOSKOWITZ,
            DARREN_INDYKE,
            BRAD_KARP,
            DAVID_STERN,
            DAVID_SCHOEN,
            DEBBIE_FEIN,
            FRED_HADDAD,
            JACK_GOLDBERGER,
            JACKIE_PERCZEK,
            JAY_LEFKOWITZ,
            JESSICA_CADWELL,
            LILLY_SANCHEZ,
            MARTIN_WEINBERG,
            REID_WEINGARTEN,
            RICHARD_KAHN,
            SCOTT_J_LINK,
            TONJA_HADDAD_COLEMAN,
        ]
    ),
    HighlightedGroup(
        label='famous_lawyer',
        info='lawyer',
        style='medium_purple3',
        emailers=[
            ALAN_DERSHOWITZ,
            KEN_STARR,
        ]
    ),
    HighlightedGroup(
        label='lobbyist',
        style='light_coral',
        pattern='Rob Crowe|Stanley Rosenberg',
        emailers=[
            KATHERINE_KEATING,
            MOHAMED_WAHEED_HASSAN,
            OLIVIER_COLOM,
            PUREVSUREN_LUNDEG,
        ]
    ),
    HighlightedGroup(
        label='mideast',
        style='dark_sea_green4',
        pattern=r"Abdulmalik Al-Makhlafi|Abu\s+Dhabi|Assad|Bahrain|Dubai|Emir(at(es?|i))?|Erdogan|Gaddafi|HBJ|Imran\s+Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|kasshohgi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Pakistani?|Riya(dh|nd)|Saudi(\s+Arabian?)?|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        emailers=[
            ANAS_ALRASHEED,
            AZIZA_ALAHMADI,
            RAAFAT_ALSABBAGH,
            SHAHER_ABDULHAK_BESHER,
        ]
    ),
    HighlightedGroup(
        label='modeling',
        style='pale_violet_red1',
        pattern=r'\w+@mc2mm.com',
        emailers=[
            DANIEL_SIAD,
            FAITH_KATES,
            'Gianni Serazzi',  # fashion consultant?
            JEAN_LUC_BRUNEL,
            MARIANA_IDZKOWSKA,
        ]
    ),
    HighlightedGroup(
        label='law enforcement',
        style='color(24) bold',
        pattern='FBI|(James )?Comey|(Kirk )?Blouin|((Bob|Robert) )?Mueller|Police Code Enforcement|Strzok',
        emailers=[
            ANN_MARIE_VILLAFANA,
        ]
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
        pattern=r'(Alex )?Acosta|Bolton|Broidy|GOP|(?<!Merwin Dela )Cruz|Kobach|Kolfage|Kudlow|Lewandowski|(Marco )?Rubio|Mattis|Mnuchin|(Paul\s+)?Manafort|(Peter )?Navarro|Pompeo|Republican',
        emailers = [
            RUDY_GIULIANI,
            TULSI_GABBARD,
        ]
    ),
    HighlightedGroup(
        label='russia',
        style='red bold',
        pattern=r'FSB|GRU|Lavrov|Moscow|(Oleg )?Deripaska|(Vladimir )?Putin|Russian?|Rybolo(olev|vlev)|Vladimir Yudashkin',
        emailers = [
            MASHA_DROKOVA,
        ]
    ),
    HighlightedGroup(
        label='scholar',
        style='light_goldenrod2',
        pattern='Alain Forget|David Grosof|Moshe Hoffman|((Noam|Valeria) )?Chomsky|Peter Attia',
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
        label='south america',
        style='yellow',
        pattern=r'Argentin(a|ian)|Bolsonar[aio]|Bra[sz]il(ian)?|Bukele|Cuban?|El\s*Salvador|Lula|(Nicolas\s+)?Maduro|Venezuelan?',
    ),
    HighlightedGroup(
        label='tech bro',
        style='cyan2',
        pattern='Masa(yoshi)?( Son)?|Najeev|Palantir|(Peter )?Th(ie|ei)l|Softbank',
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
        label='virgin islands',
        style='sea_green1',
        pattern=r'Bahamas|Cecile de Jongh|(Kenneth E\. )?Mapp|Virgin\s*Islands',
        emailers=[
            STACEY_PLASKETT,
        ]
    ),

    # Individuals
    HighlightedGroup(
        label=STEVE_BANNON,
        info='War Room',
        style='color(58)',
        pattern=r'((Steve|Sean)\s+)?Bannon?',
    ),
    HighlightedGroup(
        label=BILL_GATES,
        style='turquoise4',
        pattern=r'BG|(Bill\s+((and|or)\s+Melinda\s+)?)?Gates|Melinda(\s+Gates)?',
        has_no_category=True,
    ),
    HighlightedGroup(
        emailers=[STEVEN_HOFFENBERG],
        info=HEADER_ABBREVIATIONS['Hoffenberg'],
        pattern=r'(steven?\s*)?hoffenberg?w?',
        style='gold3'
    ),
    HighlightedGroup(emailers=[ARIANE_DE_ROTHSCHILD], style='indian_red', info='Rothschild family'),
    HighlightedGroup(emailers=[GHISLAINE_MAXWELL], pattern='gmax(1@ellmax.com)?', style='deep_pink3'),
    HighlightedGroup(emailers=[JABOR_Y], info=HEADER_ABBREVIATIONS['Jabor'], style='spring_green1'),
    HighlightedGroup(emailers=[JEFFREY_EPSTEIN], pattern='Mark (L. )?Epstein', style='blue1'),
    HighlightedGroup(emailers=[JOI_ITO], info='MIT Media Lab', style='blue_violet'),
    HighlightedGroup(emailers=[KATHY_RUEMMLER], info='former Obama legal counsel', style='magenta2'),
    HighlightedGroup(emailers=[LINDA_STONE], style='pink3'),
    HighlightedGroup(emailers=[MELANIE_SPINELLA], style='magenta3'),
    HighlightedGroup(emailers=[MELANIE_WALKER], info='Doctor', style='pale_violet_red1'),
    HighlightedGroup(emailers=[PAULA], style='pink1'),
    HighlightedGroup(emailers=[PRINCE_ANDREW], style='dodger_blue1'),
    HighlightedGroup(emailers=[SOON_YI], info="Woody Allen's wife", style='hot_pink'),
    HighlightedGroup(emailers=[SULTAN_BIN_SULAYEM], info='CEO of DP World, chairman of the ports in Dubai', style='green1'),

    # Highlight regexes for things other than names
    HighlightedGroup(
        label='header_field',
        style='plum4',
        pattern='^(Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):',
        is_multiline=True,
    ),
    HighlightedGroup(
        label='quoted_reply_line',
        style='dim',
        pattern=REPLY_REGEX.pattern,
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

COLOR_KEYS = [h.colored_label() for h in HIGHLIGHTED_GROUPS if not h.is_multiline]


def get_info_for_name(name: str) -> str | None:
    highlight_group = get_highlight_group_for_name(name)

    if not highlight_group:
        return None

    info = highlight_group.get_info()

    if info and name in PEOPLE_INFO:
        info += f", {PEOPLE_INFO[name]}"

    return info


def get_highlight_group_for_name(name: str) -> HighlightedGroup | None:
    for highlight_group in HIGHLIGHTED_GROUPS:
        if highlight_group.regex.search(name):
            return highlight_group


def get_style_for_name(name: str, default: str = DEFAULT, allow_bold: bool = True) -> str:
    highlight_group = get_highlight_group_for_name(name)
    style = highlight_group.style if highlight_group else default
    return style if allow_bold else style.replace('bold', '').strip()


if is_debug:
    for hg in HIGHLIGHTED_GROUPS:
        print(hg)
        print("\n")
