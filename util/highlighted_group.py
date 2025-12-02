import re
from dataclasses import dataclass, field

from inflection import titleize
from rich.text import Text

from util.constants import *
from util.env import is_debug, logger

ESTATE_EXECUTOR = 'Epstein estate executor'
REGEX_STYLE_PREFIX = 'regex'
NO_CATEGORY_LABELS = [BILL_GATES, STEVE_BANNON]

safe_style_name = lambda label: label.lower().replace(' ', '_').replace('-', '_')


@dataclass
class HighlightedGroup:
    style: str
    label: str = ''      # TODO: make it default to None?
    pattern: str = ''    # TODO: make it default to None?
    emailers: dict[str, str | None] = field(default_factory=dict)
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
                self.label = [k for k in self.emailers.keys()][0]
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
        pattern=r'Apollo|Black(rock|stone)|DB|Deutsche\s*Bank|Goldman( ?Sachs)|HSBC|(Janet\s*)?Yellen|(Jerome\s*)?Powell|Merrill\s+Lynch|Morgan Stanley|j\.?p\.?\s*morgan( Chase)?|Chase Bank|us.gio@jpmorgan.com',
        emailers={
            ALIREZA_ITTIHADIEH: 'CEO Freestream Aircraft Limited',
            AMANDA_ENS: None,
            DANIEL_SABBA: 'UBS Investment Bank',
            'David Fiszel': 'CIO Honeycomb Asset Management'
            JES_STALEY: 'former CEO of Barclays',
            JIDE_ZEITLIN: 'former partner at Goldman Sachs, allegations of sexual misconduct',
            LEON_BLACK: 'Apollo CEO',
            MARC_LEON: None,
            MELANIE_SPINELLA: f'representative of {LEON_BLACK}',
            MORTIMER_ZUCKERMAN: 'business partner of Epstein',
            PAUL_BARRETT: None,
            PAUL_MORRIS: None,
        }
    ),
    HighlightedGroup(
        label='bitcoin',
        style='orange1 bold',
        pattern=r'Balaji|bitcoin|block ?chain( capital)?|Brock|coins|cr[iy]?pto(currency)?|e-currency|(Howard\s+)?Lutnick|(jeffrey\s+)?wernick|Libra|SpanCash|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)',
        emailers = {
            JEREMY_RUBIN: 'developer/researcher',
            SCARAMUCCI: None,
        },
    ),
    HighlightedGroup(
        label='bro',
        style='tan',
        emailers = {
            JONATHAN_FARKAS: None,
            'Peter Thomas Roth': 'student of Epstein at Dalton, skincare company founder',
            TOM_BARRACK: 'long time friend of Trump',
        }
    ),
    HighlightedGroup(
        label='business',
        style='spring_green4',
        pattern=r'Marc Rich|(Steve\s+)?Wynn|(Leslie\s+)?Wexner',
        emailers = {
            BARBRO_EHNBOM: 'Swedish pharmaceuticals',
            BORIS_NIKOLIC: f'Biotech VC, {ESTATE_EXECUTOR}',
            NICHOLAS_RIBIS: 'Hilton CEO',
            ROBERT_LAWRENCE_KUHN: None,
            STEPHEN_HANSON: None,
            TERRY_KAFKA: 'CEO of Impact Outdoor (highway billboards)',
            TOM_PRITZKER: 'brother of J.B. Pritzker',
        }
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
        emailers = {
            DEEPAK_CHOPRA: None,
        }
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
        emailers = {
            GLENN_DUBIN: "Highbridge Capital Management, married to Epstein's ex-gf Eva",
            EVA: "possibly Epstein's ex-girlfriend (?)",
        },
    ),
    HighlightedGroup(
        label='employee',
        style='deep_sky_blue4',
        emailers = {
            ERIC_ROTH: 'jet decorator',
            GWENDOLYN_BECK: 'Epstein fund manager in the 90s',
            LAWRANCE_VISOSKI: 'Pilot',
            LESLEY_GROFF: 'Assistant (?)',
            JEAN_HUGUEN: 'interior design at Alberto Pinto Cabinet',
            'Linda Pinto': 'interior design at Alberto Pinto Cabinet',
            NADIA_MARCINKO: 'pilot',
        }
    ),
    HighlightedGroup(
        label='entertainer',
        style='light_steel_blue3',
        pattern='Bobby slayton|David Blaine|Etienne Binant|Ramsey Elkholy|Steven Gaydos?|Woody( Allen)?',
        emailers={
            'Andres Serrano': "'Piss Christ' artist",
            BILL_SIEGEL: 'documentary film producer and director',
        }
    ),
    HighlightedGroup(
        label='europe',
        style='light_sky_blue3',
        pattern=r'(Caroline|Jack)?\s*Lang(, Caroline)?|Le\s*Pen|Macron|(Angela )?Merk(el|le)|(Sebastian )?Kurz|(Vi(c|k)tor\s+)?Orbah?n|Edward Rod Larsen|Ukrain(e|ian)|Zug',
        emailers = {
            MIROSLAV_LAJCAK: 'Russia friendly Slovak',
            PETER_MANDELSON: 'UK politics',
            TERJE_ROD_LARSEN: 'Norwegian diplomat',
            THORBJORN_JAGLAND: None,
        }
    ),
    HighlightedGroup(
        label='harvard',
        style='deep_pink2',
        pattern=r'Harvard',
        emailers = {
            LARRY_SUMMERS: 'board member of Digital Currency Group (DCG), Obama economic advisor',
            LISA_NEW: 'poetry',
            MARTIN_NOWAK: None,
        }
    ),
    HighlightedGroup(
        label='india',
        style='bright_green',
        pattern='Hardeep( puree)?|Indian?|Modi|mumbai|Zubair( Khan)?',
        emailers = {
            ANIL_AMBANI: None,
            VINIT_SAHNI: None,
        }
    ),
    HighlightedGroup(
        label='israel',
        style='dodger_blue2',
        pattern='Bibi|(eh|(Ehud|Nili Priell) )?barak|Mossad|Netanyahu|Israeli?',
        emailers={
            EHUD_BARAK: 'former primer minister',
            'Nili Priell Barak': f'wife of {EHUD_BARAK}',
        }
    ),
    HighlightedGroup(
        label='javanka',
        style='medium_violet_red',
        emailers = {
            IVANKA: None,
            JARED_KUSHNER: None,
        }
    ),
    HighlightedGroup(
        label='journalist',
        style='bright_yellow',
        pattern=r'Alex Yablon|Ingram, David|Susan Edelman|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk',
        emailers = {
            EDWARD_EPSTEIN: None,
            LANDON_THOMAS: 'New York Times',
            MICHAEL_WOLFF: None,
            PAUL_KRASSNER: '60s guy',
            'Tim Zagat': 'Zagat restaurant guide CEO',
        }
    ),
    HighlightedGroup(
        label='lawyer',
        style='medium_purple2',
        pattern=r'(Erika\s+)?Kellerhals|Michael J. Pike|Paul,?\s*Weiss|Roy Black|Wein(berg|garten)',
        emailers = {
            BENNET_MOSKOWITZ: None,
            'Brad Edwards': None,
            BRAD_KARP: None,
            DARREN_INDYKE: ESTATE_EXECUTOR,
            DAVID_STERN: None,
            DAVID_SCHOEN: None,
            DEBBIE_FEIN: None,
            FRED_HADDAD: None,
            JACK_GOLDBERGER: None,
            JACKIE_PERCZEK: None,
            JAY_LEFKOWITZ: None,
            JESSICA_CADWELL: None,
            LILLY_SANCHEZ: None,
            MARTIN_WEINBERG: None,
            MICHAEL_MILLER: 'Steptoe',
            REID_WEINGARTEN: None,
            RICHARD_KAHN: ESTATE_EXECUTOR,
            SCOTT_J_LINK: None,
            TONJA_HADDAD_COLEMAN: None,
        }
    ),
    HighlightedGroup(
        label='famous_lawyer',
        info='lawyer',
        style='medium_purple3',
        emailers = {
            ALAN_DERSHOWITZ: None,
            KEN_STARR: None,
        }
    ),
    HighlightedGroup(
        label='lobbyist',
        style='light_coral',
        pattern=r'[BR]ob Crowe|Stanley Rosenberg',
        emailers = {
            'Joshua Cooper Ramo': 'co-CEO of Kissinger Associates',
            KATHERINE_KEATING: 'Daughter of former Australian PM',
            MOHAMED_WAHEED_HASSAN: 'former president of the Maldives',
            OLIVIER_COLOM: 'France',
            PUREVSUREN_LUNDEG: 'Mongolian ambassador to the UN',
        }
    ),
    HighlightedGroup(
        label='mideast',
        style='dark_sea_green4',
        pattern=r"Abdulmalik Al-Makhlafi|Abu\s+Dhabi|Assad|Bahrain|Dubai|Emir(at(es?|i))?|Erdogan|Gaddafi|HBJ|Imran\s+Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|kasshohgi|Kaz(akh|ich)stan|Kazakh?|KSA|Marra[hk]e[cs]h|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Pakistani?|Riya(dh|nd)|Saudi(\s+Arabian?)?|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        emailers = {
            ANAS_ALRASHEED: None,
            AZIZA_ALAHMADI: 'Abu Dhabi Department of Culture & Tourism',
            RAAFAT_ALSABBAGH: None,
            SHAHER_ABDULHAK_BESHER: None,
        }
    ),
    HighlightedGroup(
        label='modeling',
        style='pale_violet_red1',
        pattern=r'\w+@mc2mm.com',
        emailers = {
            DANIEL_SIAD: None,
            FAITH_KATES: None,
            'Gianni Serazzi': 'fashion consultant?',
            JEAN_LUC_BRUNEL: 'sordid backstory, died by suicide in French prison',
            MARIANA_IDZKOWSKA: None,
        }
    ),
    HighlightedGroup(
        label='law enforcement',
        style='color(24) bold',
        pattern='FBI|(James )?Comey|(Kirk )?Blouin|((Bob|Robert) )?Mueller|Police Code Enforcement|Strzok',
        emailers = {
            ANN_MARIE_VILLAFANA: None,
            DANNY_FROST: 'Director of Communications at Manhattan DA',
        }
    ),
    HighlightedGroup(
        label='publicist',
        style='orange_red1',
        pattern='Henry Holt|Ian Osborne|Matthew Hiltzik',
        emailers = {
            AL_SECKEL: 'husband of Isabel Maxwell, Mind State organizer, fell off a cliff',
            CHRISTINA_GALBRAITH: None,
            MICHAEL_SITRICK: None,
            PEGGY_SIEGAL: None,
            ROSS_GOW: 'Acuity Reputation Management',
            TYLER_SHEARS: None,
        }
    ),
    HighlightedGroup(
        label='republicans',
        style='bold dark_red',
        pattern=r'(Alex )?Acosta|Bolton|Broidy|GOP|(?<!Merwin Dela )Cruz|Kobach|Kolfage|Kudlow|Lewandowski|(Marco )?Rubio|Mattis|Mnuchin|(Paul\s+)?Manafort|(Peter )?Navarro|Pompeo|Republican',
        emailers = {
            RUDY_GIULIANI: None,
            TULSI_GABBARD: None,
        }
    ),
    HighlightedGroup(
        label='russia',
        style='red bold',
        pattern=r'FSB|GRU|Lavrov|Moscow|(Oleg )?Deripaska|(Vladimir )?Putin|Russian?|Rybolo(olev|vlev)|Vladimir Yudashkin',
        emailers = {
            MASHA_DROKOVA: 'silicon valley VC',
        }
    ),
    HighlightedGroup(
        label='scholar',
        style='light_goldenrod2',
        pattern=r'Alain Forget|David Grosof|MIT(\s*Media\s*Lab)?|Media\s*Lab|Moshe Hoffman|((Noam|Valeria) )?Chomsky|Peter Attia|Stanford',
        emailers = {
            'Barnaby Marsh': None,
            DAVID_HAIG: None,
            JOSCHA_BACH: 'cognitive science / AI research',
            LAWRENCE_KRAUSS: None,
            NEAL_KASSELL: None,
            'Richard Merkin': None,
            ROBERT_TRIVERS: 'evolutionary biology',
            ROGER_SCHANK: None,
            STEVEN_PFEIFFER: None,
        }
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
        emailers = {
            ELON_MUSK: None,
            REID_HOFFMAN: None,
            STEVEN_SINOFSKY: None,
        }
    ),
    HighlightedGroup(
        label='trump',
        style='red3 bold',
        pattern=r"@?realDonaldTrump|DJT|(Donald\s+(J\.\s+)?)?Trump|Don(ald| Jr)(?! Rubin)|Mar[- ]*a[- ]*Lago|(Matt(hew)? )?Calamari|\bMatt C\b|Melania|Roger\s+Stone",
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
        emailers = {
            STACEY_PLASKETT: None,
            KENNETH_E_MAPP: 'Governor',
        }
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
        emailers={STEVEN_HOFFENBERG: HEADER_ABBREVIATIONS['Hoffenberg']},
        pattern=r'(steven?\s*)?hoffenberg?w?',
        style='gold3'
    ),
    HighlightedGroup(emailers={JABOR_Y: HEADER_ABBREVIATIONS['Jabor']}, style='spring_green1'),
    HighlightedGroup(emailers={ARIANE_DE_ROTHSCHILD: 'Rothschild family'}, style='indian_red'),
    HighlightedGroup(emailers={GHISLAINE_MAXWELL: None}, pattern='gmax(1@ellmax.com)?', style='deep_pink3'),
    HighlightedGroup(emailers={JEFFREY_EPSTEIN: None}, pattern='Mark (L. )?Epstein', style='blue1'),
    HighlightedGroup(emailers={JOI_ITO: 'former head of MIT Media Lab'}, style='gold1'),
    HighlightedGroup(emailers={KATHY_RUEMMLER: 'former Obama legal counsel'}, style='magenta2'),
    HighlightedGroup(emailers={LINDA_STONE: None}, style='pink3'),
    HighlightedGroup(emailers={MELANIE_WALKER: 'Doctor'}, style='pale_violet_red1'),
    HighlightedGroup(emailers={PAULA: None}, style='pink1'),
    HighlightedGroup(emailers={PRINCE_ANDREW: None}, style='dodger_blue1'),
    HighlightedGroup(emailers={SOON_YI: "Woody Allen's wife"}, style='hot_pink'),
    HighlightedGroup(emailers={SULTAN_BIN_SULAYEM: 'CEO of DP World}, chairman of the ports in Dubai'}, style='green1'),

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
    info_pieces = [info] if info else []

    if highlight_group.emailers.get(name) is not None:
        info_pieces.append(highlight_group.emailers[name])

    return ', '.join(info_pieces)


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
