import re
from dataclasses import dataclass, field

from inflection import titleize
from rich.highlighter import RegexHighlighter
from rich.text import Text

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import DEFAULT, OTHER_SITE_LINK_STYLE, PHONE_NUMBER_STYLE, REDACTED
from epstein_files.util.constant.urls import ARCHIVE_LINK_COLOR
from epstein_files.util.constants import EMAILER_ID_REGEXES, HEADER_ABBREVIATIONS, REPLY_REGEX, SENT_FROM_REGEX
from epstein_files.util.env import args, logger

ESTATE_EXECUTOR = 'Epstein estate executor'
REGEX_STYLE_PREFIX = 'regex'
NO_CATEGORY_LABELS = [BILL_GATES, STEVE_BANNON]
SIMPLE_NAME_REGEX = re.compile(r"^[-\w ]+$", re.IGNORECASE)


@dataclass
class HighlightedGroup:
    style: str
    label: str = ''
    pattern: str = ''
    emailers: dict[str, str | None] = field(default_factory=dict)
    has_no_category: bool = False
    info: str | None = None
    is_multiline: bool = False
    regex: re.Pattern = field(init=False)
    style_name: str = field(init=False)
    style_suffix: str = field(init=False)

    def __post_init__(self):
        if not self.label:
            if len(self.emailers) == 1:
                self.label = [k for k in self.emailers.keys()][0]
                self.has_no_category = True
            else:
                raise RuntimeError(f"No label provided for {repr(self)}")

        self.style_suffix = self.label.lower().replace(' ', '_').replace('-', '_')
        self.style_name = f"{REGEX_STYLE_PREFIX}.{self.style_suffix}"
        patterns = [self._emailer_pattern(e) for e in self.emailers] + ([self.pattern] if self.pattern else [])
        pattern = '|'.join(patterns)

        if self.is_multiline:
            self.regex = re.compile(fr"(?P<{self.style_suffix}>{pattern})", re.IGNORECASE | re.MULTILINE)
            self.has_no_category = True
        else:
            self.regex = re.compile(fr"\b(?P<{self.style_suffix}>({pattern})s?)\b", re.IGNORECASE)

    def colored_label(self) -> Text:
        return Text(self.label.replace('_', ' '), style=self.style)

    def get_info(self, name: str) -> str | None:
        info_pieces = []

        if not self.has_no_category:
            info_pieces.append(self.info or titleize(self.label))

        if self.emailers.get(name) is not None:
            info_pieces.append(self.emailers[name])

        if len(info_pieces) > 0:
            return ', '.join(info_pieces)

    # TODO: handle word boundary issue for names that end in symbols
    def _emailer_pattern(self, name: str) -> str:
        logger.debug(f"emailer_pattern() called for '{name}'")
        names = name.split()
        last_name = names[-1]

        if name in EMAILER_ID_REGEXES:
            pattern = EMAILER_ID_REGEXES[name].pattern

            if SIMPLE_NAME_REGEX.match(last_name) and last_name.lower() not in NAMES_TO_NOT_HIGHLIGHT:
                logger.debug(f"Adding last name '{last_name}' to existing pattern '{pattern}'")
                pattern += fr"|{last_name}"  # Include regex for last name

            return pattern
        elif ' ' not in name:
            return name

        first_name = ' '.join(names[0:-1])
        name_patterns = [name.replace(' ', r"\s+"), first_name, last_name]
        name_regex_parts = [n for n in name_patterns if n.lower() not in NAMES_TO_NOT_HIGHLIGHT]
        logger.debug(f"name_regex_parts for '{name}': {name_regex_parts}")

        if len(names) > 2:
            logger.debug(f"'{name}' has {len(names)} names (first_name='{first_name}')")

        return '|'.join(name_regex_parts)


HIGHLIGHTED_GROUPS = [
    HighlightedGroup(
        label='bitcoin',
        style='orange1 bold',
        pattern=r'Balaji|bitcoin|block ?chain( capital)?|Brock|coins?|cr[iy]?pto(currenc(y|ies))?|e-currency|(Gavin )?Andressen|(Howard\s+)?Lutnic?k|(jeffrey\s+)?wernick|Libra|Madars|(Patrick\s*)?Murck|SpanCash|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)',
        emailers = {
            JEREMY_RUBIN: 'developer/researcher',
            SCARAMUCCI: 'Skybridge Capital, FTX investor',
        },
    ),
    HighlightedGroup(
        label='bro',
        style='tan',
        pattern=r"Andrew Farkas",
        emailers = {
            JONATHAN_FARKAS: "heir to the Alexander's department store fortune",
            'Peter Thomas Roth': 'student of Epstein at Dalton, skincare company founder',
            STEPHEN_HANSON: None,
            TOM_BARRACK: 'long time friend of Trump',
        }
    ),
    HighlightedGroup(
        label='business',
        style='spring_green4',
        pattern=r'(John\s*)?Kluge|Marc Rich|(Mi(chael|ke)\s*)?Ovitz|(Steve\s+)?Wynn|(Leslie\s+)?Wexner|Valhi|(Yves\s*)?Bouvier',
        emailers = {
            ALIREZA_ITTIHADIEH: 'CEO Freestream Aircraft Limited',
            BARBRO_EHNBOM: 'Swedish pharmaceuticals',
            BORIS_NIKOLIC: f'Biotech VC, {ESTATE_EXECUTOR}, VC partner of Bill Gates',
            FRED_HADDAD: "co-founder of Heck's in West Virginia",
            GORDON_GETTY: 'heir of oil tycoon J. Paul Getty',
            NICHOLAS_RIBIS: 'Hilton CEO',
            'Philip Kafka': 'president of Prince Concepts (and son of Terry Kafka?)',
            ROBERT_LAWRENCE_KUHN: "investment banker, China expert",
            TERRY_KAFKA: 'CEO of Impact Outdoor (highway billboards)',
            TOM_PRITZKER: 'brother of J.B. Pritzker',
        }
    ),
    HighlightedGroup(
        label='china',
        style='bright_red',
        pattern=r"Beijing|CCP|Chin(a|e?se)|Gino\s+Yu|Global Times|Guo|Hong|Huaw[ae]i|Kong|Jack\s+Ma|Kwok|Ministry\sof\sState\sSecurity|Mongolian?|MSS|Peking|PRC|Tai(pei|wan)|Xi",
    ),
    HighlightedGroup(
        label='deepak_chopra',
        style='dark_sea_green4',
        emailers = {
            'Carolyn Rangel': 'assistant',
            DEEPAK_CHOPRA: 'woo woo',
        }
    ),
    HighlightedGroup(
        label='democrats',
        style='sky_blue1',
        pattern=r'(Al\s*)?Franken|Biden|((Bill|Hillart?y)\s*)?Clinton|DNC|George\s*Mitchell|(George\s*)?Soros|Hill?ary|Dem(ocrat(ic)?)?|(John\s*)?Kerry|Lisa Monaco|(Matteo\s*)?Salvini|Maxine\s*Waters|(Barac?k )?Obama|(Nancy )?Pelosi|Ron\s*Dellums|Schumer|Vernon\s*Jordan',
    ),
    HighlightedGroup(
        label='Dubin family',
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
        pattern='Merwin',
        emailers = {
            ERIC_ROTH: 'jet decorator',
            GWENDOLYN_BECK: 'Epstein fund manager in the 90s',
            JEAN_HUGUEN: 'interior design at Alberto Pinto Cabinet',
            LAWRANCE_VISOSKI: 'pilot',
            LESLEY_GROFF: 'assistant',
            'Linda Pinto': 'interior design at Alberto Pinto Cabinet',
            MERWIN_DELA_CRUZ: None,  # HOUSE_OVERSIGHT_032652 Groff says "Jojo and Merwin both requested off Nov. 25 and 26"
            NADIA_MARCINKO: 'pilot',
        }
    ),
    HighlightedGroup(
        label='entertainer',
        style='light_steel_blue3',
        pattern=r'(Art )?Spiegelman|Bobby slayton|Errol(\s*Morris)?|Etienne Binant|(Frank\s)?Gehry|Jagger|(Jeffrey\s*)?Katzenberg|(Johnny\s*)?Depp|Lena Dunham|Madonna|Mark\s*Burnett|Ramsey Elkholy|Steven Gaydos?|Woody( Allen)?|Zach Braff',
        emailers={
            'Andres Serrano': "'Piss Christ' artist",
            'Barry Josephson': 'American film producer and former music manager, editor FamilySecurityMatters.org',
            BILL_SIEGEL: 'documentary film producer and director',
            'David Blaine': 'magician',
            'Richard Merkin': 'painter, illustrator and arts educator',
        },
    ),
    HighlightedGroup(
        label='estate_executor',
        info='lawyer',
        style='purple3 bold',
        emailers = {
            DARREN_INDYKE: ESTATE_EXECUTOR,
            RICHARD_KAHN: ESTATE_EXECUTOR,
        }
    ),
    HighlightedGroup(
        label='europe',
        style='light_sky_blue3',
        pattern=r'(Angela )?Merk(el|le)|Austria|(Benjamin\s*)?Harnwell|Berlin|Brit(ain|ish)|Brussels|Cannes|(Caroline|Jack)?\s*Lang(, Caroline)?|Cypr(iot|us)|Davos|ECB|Europe(an)?|Geneva|Germany?|Gree(ce|k)|Ital(ian|y)|Jacques|Le\s*Pen|London|Macron|(Natalia\s*)?Veselnitskaya|Nigel(\s*Farage)?|Oslo|Paris|Polish|(Sebastian )?Kurz|(Vi(c|k)tor\s+)?Orbah?n|Edward Rod Larsen|Strauss[- ]?Kahn|(Tony\s)?Blair|Ukrain(e|ian)|Vienna|(Vitaly\s*)?Churkin|Zug',
        emailers = {
            ANDRZEJ_DUDA: 'former president of Poland',
            MIROSLAV_LAJCAK: 'Russia-friendly Slovakian politician, friend of Steve Bannon',
            PETER_MANDELSON: 'UK politics',
            TERJE_ROD_LARSEN: 'Norwegian diplomat',
            THORBJORN_JAGLAND: 'former prime minister of Norway and head of the Nobel Peace Prize Committee',
        }
    ),
    HighlightedGroup(
        label='famous_lawyer',
        info='lawyer',
        style='medium_purple3',
        pattern=r'dersh|Gloria\s*Allred',
        emailers = {
            ALAN_DERSHOWITZ: None,
            KEN_STARR: 'head of the Monica Lewinsky investigation against Bill Clinton',
        }
    ),
    HighlightedGroup(
        label='finance',
        style='green',
        pattern=r'Apollo|Black(rock|stone)|BofA|Chase Bank|DB|Deutsche\s*Bank|Fenner|FRBNY|Goldman(\s*Sachs)|HSBC|(Janet\s*)?Yellen|(Jerome\s*)?Powell|(Jimmy\s*)?Cayne|JPMC?|j\.?p\.?\s*morgan(\.?com|\s*Chase)?|Madoff|Merrill(\s*Lynch)?|(Michael\s*)?(Cembalest|Milken)|MLPF&S|(money\s+)?launder(s?|ers?|ing)?(\s+money)?|Morgan Stanley|(Peter L. )?Scher|(Ray\s*)?Dalio|Schwartz?man|Serageldin|UBS|us.gio@jpmorgan.com',
        emailers={
            AMANDA_ENS: 'Citigroup',
            DANIEL_SABBA: 'UBS Investment Bank',
            DAVID_FISZEL: 'CIO Honeycomb Asset Management',
            JES_STALEY: 'former CEO of Barclays',
            JIDE_ZEITLIN: 'former partner at Goldman Sachs, allegations of sexual misconduct',
            LEON_BLACK: 'Apollo CEO',
            MARC_LEON: 'Luxury Properties Sari Morrocco',
            MELANIE_SPINELLA: f'representative of {LEON_BLACK}',
            MORTIMER_ZUCKERMAN: 'business partner of Epstein',
            PAUL_BARRETT: None,
            PAUL_MORRIS: 'Deutsche Bank',
        }
    ),
    HighlightedGroup(
        label='harvard',
        style='deep_pink2',
        pattern=r'Cambridge|(Derek\s*)?Bok|Elisa(\s*New)?|Harvard|(Stephen\s*)?Kosslyn',
        emailers = {
            LARRY_SUMMERS: 'Obama economic advisor, board of Digital Currency Group (DCG)',
            'Leah Reis-Dennis': 'producer for Poetry in America',
            LISA_NEW: 'poetry',
            'Lisa Randall': 'theoretical physicist',
            MARTIN_NOWAK: None,
        }
    ),
    HighlightedGroup(
        label='india',
        style='bright_green',
        pattern='Hardeep( puree)?|Indian?|Modi|mumbai',
        emailers = {
            ANIL_AMBANI: 'chairman of Reliance Group',
            VINIT_SAHNI: None,
            ZUBAIR_KHAN: 'Tranchulas CEO',
        }
    ),
    HighlightedGroup(
        label='israel',
        style='dodger_blue2',
        pattern=r"Bibi|(eh|(Ehud|Nili Priell) )?barak|Israeli?|Jerusalem|Mossad|Netanyahu|(Sheldon\s*)?Adelson|Tel\s*Aviv|YIVO|zionist",
        emailers={
            EHUD_BARAK: 'former primer minister',
            'Mitchell Bard': 'director of the American-Israeli Cooperative Enterprise (AICE)',
            'Nili Priell Barak': f'wife of {EHUD_BARAK}',
        }
    ),
    HighlightedGroup(
        label='japan',
        style='color(168)',
        pattern='BOJ|japan(ese)?|jpy?(?! Morgan)|SG|Singapore'
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
        pattern=r'ABC|Alex Yablon|(Andrew\s*)?Marra|Arianna( Huffington)?|(Arthur\s*)?Kretchmer|BBC|Bloomberg|Breitbart|Charlie rose|CNN(politics?)?|Conchita|Sarnoff|(David\s*)?Pecker|(Emily )?Michot|(George\s*)?Stephanopoulus|Graydon(\s*Carter)?|(Sean\s*)?Hannity|Huffington|Ingram, David|Jonathan Karl|(Katie )?Couric|(Michele\s*)?Dargan|NYT(imes)?|Politico|Sulzberger|SunSentinel|Susan Edelman|(Uma\s*)?Sanghvi|Viceland|Vick[iy] Ward|WaPo|WGBH|WSJ|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk',
        emailers = {
            EDWARD_EPSTEIN: 'no relation to Jeffrey',
            'James Hill': 'ABC',
            JOHN_BROCKMAN: 'literary agent and author specializing in scientific literature',
            LANDON_THOMAS: 'New York Times',
            MICHAEL_WOLFF: "Author or 'Fire and Fury: Inside the Trump White House'",
            PAUL_KRASSNER: '60s guy',
            'Tim Zagat': 'Zagat restaurant guide CEO',
        }
    ),
    HighlightedGroup(
        label='latin america',
        style='yellow',
        pattern=r'Argentin(a|ian)|Bolsonar[aio]|Bra[sz]il(ian)?|Bukele|Castro|Colombian?|Cuban?|El\s*Salvador|((Enrique )?Pena )?Nieto|LatAm|Lula|Mexic(an|o)|(Nicolas\s+)?Maduro|Panama( Papers)?|Peru|Venezuelan?',
    ),
    HighlightedGroup(
        label='law enforcement',
        style='color(24) bold',
        pattern=r'ag|(Alicia\s*)?Valle|((Bob|Robert) )?Mueller|(Byung\s)?Pak|CFTC|CIA|CVRA|DOJ|FBI|FDIC|FinCEN|FINRA|FTC|IRS|(James\s*)?Comey|(Jennifer\s*Shasky\s*)?Calvery|(Kirk )?Blouin|NIH|NSA|OCC|(Lann?a\s*)?Belohlavek|(Michael\s*)?Reiter|Police Code Enforcement|SEC|Strzok|TSA|USAID|(William\s*J\.?\s*)?Zloch',
        emailers = {
            ANN_MARIE_VILLAFANA: 'southern district of Florida U.S. Attorney',
            DANNY_FROST: 'Director of Communications at Manhattan DA',
        }
    ),
    HighlightedGroup(
        label='lawyer',
        style='purple',
        pattern=r'Avenatti|(Barry (E. )?)?Krischer|(David\s*)?Boies|Kate Kelly|(Leon\s*)?Jaworski|Michael J. Pike|Paul,?\s*Weiss|Steptoe|Wein(berg|garten)',
        emailers = {
            ARDA_BESKARES: 'NYC immigration attorney allegedly involved in sex-trafficking operations',
            BENNET_MOSKOWITZ: None,
            BRAD_KARP: 'head of the law firm Paul Weiss',
            DAVID_STERN: None,
            DAVID_SCHOEN: None,
            DEBBIE_FEIN: None,
            'Erika Kellerhals': 'attorney in St. Thomas',
            GERALD_LEFCOURT: f'friend of {ALAN_DERSHOWITZ}',
            JACK_GOLDBERGER: None,
            JACKIE_PERCZEK: None,
            JAY_LEFKOWITZ: None,
            JESSICA_CADWELL: 'paralegal (?)',  # paralegal, see https://x.com/ImDrinknWyn/status/1993765348898927022
            LILLY_SANCHEZ:  'criminal defense attorney',
            MARTIN_WEINBERG: 'criminal defense attorney',
            MICHAEL_MILLER: 'Steptoe LLP partner',
            REID_WEINGARTEN: 'Steptoe LLP partner',
            'Roy Black': 'criminal defense attorney',
            SCOTT_J_LINK: None,
            TONJA_HADDAD_COLEMAN: 'maybe daughter of Fred Haddad?',
        }
    ),
    HighlightedGroup(
        label='lawyer for victims',
        style='dark_magenta bold',
        pattern=r'Paul\s*(G.\s*)?Cassell',
        emailers = {
            BRAD_EDWARDS: 'Rothstein Rosenfeldt Adler (Rothstein was a crook & partner of Roger Stone)',
            JACK_SCAROLA: 'Searcy Denney Scarola Barnhart & Shipley',
        }
    ),
    HighlightedGroup(
        label='lobbyist',
        style='light_coral',
        pattern=r'[BR]ob Crowe|Stanley Rosenberg',
        emailers = {
            'Joshua Cooper Ramo': 'co-CEO of Henry Kissinger Associates',
            KATHERINE_KEATING: 'Daughter of former Australian PM',
            MOHAMED_WAHEED_HASSAN: 'former president of the Maldives',
            OLIVIER_COLOM: 'France',
            PUREVSUREN_LUNDEG: 'Mongolian ambassador to the UN',
            'Stanley Rosenberg': 'former President of the Massachusetts Senate',
        }
    ),
    HighlightedGroup(
        label='mideast',
        style='dark_sea_green4',
        pattern=r"Abdulmalik Al-Makhlafi|Abdullah|Abu\s+Dhabi|Afghanistan|Al[-\s]?Qaeda|Ahmadinejad|Arab|Aramco|Assad|Bahrain|Basiji?|Benghazi|Dj[iu]bo?uti|Doha|Dubai|Egypt(ian)?|Emir(at(es?|i))?|Erdogan|Fashi|Gaddafi|HBJ|Houthi|Imran\s+Khan|Iran(ian)?|Isi[ls]|Islam(ic|ist)?|Istanbul|Kh?ashoggi|kasshohgi|Kaz(akh|ich)stan|Kazakh?|Kh[ao]menei|KSA|Libyan?|Mahmoud|Marra[hk]e[cs]h|MB(N|S|Z)|Mohammed\s+bin\s+Salman|Morocco|Mubarak|Muslim|Nayaf|Pakistani?|Omar|Palestin(e|ian)|Persian?|Riya(dh|nd)|Saddam|Salman|Saudi(\s+Arabian?)?|Shariah?|SHC|sheikh|shia|(Sultan\s*)?Yacoub|Syrian?|(Tarek\s*)?El\s*Sayed|Tehran|Tunisian?|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
        emailers = {
            ANAS_ALRASHEED: None,
            AZIZA_ALAHMADI: 'Abu Dhabi Department of Culture & Tourism',
            RAAFAT_ALSABBAGH: 'Saudi royal advisor',
            SHAHER_ABDULHAK_BESHER: 'Yemeni billionaire',
        }
    ),
    HighlightedGroup(
        label='modeling',
        style='pale_violet_red1',
        pattern=r'\w+@mc2mm.com',
        emailers = {
            'Abi Schwinck': 'MC2 Model Management (?)|(Nicole\s*)?Junkerman',
            DANIEL_SIAD: None,
            FAITH_KATES: 'Next Models co-founder',
            'Gianni Serazzi': 'fashion consultant?',
            JEAN_LUC_BRUNEL: 'MC2 Model Management founder, died by suicide in French jail',
            JEFF_FULLER: 'president of MC2 Model Management USA',
            MANUELA_MARTINEZ: 'Mega Partners (Brazilian agency)',
            MARIANA_IDZKOWSKA: None,
            'Michael Sanka': 'MC2 Model Management (?)',
        }
    ),
    HighlightedGroup(
        label='publicist',
        style='orange_red1',
        pattern=r"Henry Holt|Ian Osborne|(Matt(hew)? )?Hiltzi[gk]",
        emailers = {
            AL_SECKEL: 'husband of Isabel Maxwell and Mindshift conference organizer who fell off a cliff',
            CHRISTINA_GALBRAITH: None,
            MICHAEL_SITRICK: None,
            PEGGY_SIEGAL: 'socialite',
            ROSS_GOW: 'Acuity Reputation Management',
            TYLER_SHEARS: None,
        }
    ),
    HighlightedGroup(
        label='republicans',
        style='bold dark_red',
        pattern=r'Alberto\sGonzale[sz]|(Alex\s*)?Acosta|(Bill\s*)?Barr|Bill\s*Shine|(Bob\s*)?Corker|Bolton|Broidy|(Chris\s)?Christie|Devin\s*Nunes|(George\s*)?Nader|GOP|Kissinger|Kobach|Kolfage|Kudlow|Lewandowski|(Marco\s)?Rubio|(Mark\s*)Meadows|Mattis|(?<!Merwin Dela )Cruz|(Michael\s)?Hayden|((General|Mike)\s*)?(Flynn|Pence)|(Mitt\s*)?Romney|Mnuchin|Nikki|Haley|(Paul\s+)?Manafort|(Peter\s)?Navarro|Pompeo|Reagan|Republican|(Richard\s*)?Nixon|Sasse|(Rex\s*)?Tillerson',
        emailers = {
            RUDY_GIULIANI: 'disbarred formed mayor of New York City',
            TULSI_GABBARD: None,
        },
    ),
    HighlightedGroup(
        label='russia',
        style='red bold',
        pattern=r'Chernobyl|Day\s+One\s+Ventures|(Dmitry\s)?(Kiselyov|Medvedev|Rybolo(o?l?ev|vlev))|Dmitry|FSB|GRU|KGB|Kislyak|Kremlin|Lavrov|Lukoil|Moscow|(Oleg )?Deripaska|Oleksandr Vilkul|Rosneft|(Vladimir )?Putin|Russian?|Sberbank|Vladimir( Yudashkin)?|Xitrans',
        emailers = {
            MASHA_DROKOVA: 'silicon valley VC',
            RENATA_BOLOTOVA: 'former aspiring model, now fund manager at New York State Insurance Fund',
        }
    ),
    HighlightedGroup(
        label='scholar',
        style='light_goldenrod2',
        pattern=r'Alain Forget|Brotherton|Columbia|David Grosof|MIT(\s*Media\s*Lab)?|Media\s*Lab|Minsky|Moshe Hoffman|((Noam|Valeria) )?Chomsky|Praluent|Regeneron|(Richard\s*)?Dawkins|Sanofi|Stanford|(Stephen\s*)?Hawking|UCLA',
        emailers = {
            'Barnaby Marsh': None,
            DAVID_HAIG: None,
            JOSCHA_BACH: 'cognitive science / AI research',
            LAWRENCE_KRAUSS: 'theoretical physicist',
            LINDA_STONE: 'ex-Microsoft, MIT Media Lab',
            MARK_TRAMO: 'professor of neurology at UCLA',
            NEAL_KASSELL: None,
            PETER_ATTIA: 'longevity medicine',
            ROBERT_TRIVERS: 'evolutionary biology',
            ROGER_SCHANK: 'Teachers College, Columbia University',
            STEVEN_PFEIFFER: None,
        },
    ),
    HighlightedGroup(
        label='tech bro',
        style='bright_cyan',
        pattern=r"AG?I|Eric\sSchmidt|(Mark\s*)?Zuckerberg|Masa(yoshi)?(\sSon)?|Najeev|Palantir|(Peter\s)?Th(ie|ei)l|Sergey\s*Brin|Softbank|SpaceX",
        emailers = {
            ELON_MUSK: None,
            REID_HOFFMAN: 'PayPal mafia member, founder of LinkedIn',
            STEVEN_SINOFSKY: 'ex-Microsoft',
        },
    ),
    HighlightedGroup(
        label='trump',
        style='red3 bold',
        pattern=r"@?realDonaldTrump|\bDJ?T\b|(Donald\s+(J\.\s+)?)?Trump(ism)?|Don(ald| *Jr)(?! Rubin)|(Madeleine\s*)?Westerhout|Mar[-\s]*a[-\s]*Lago|(Marla\s*)?Maples|(Matt(hew)? )?Calamari|\bMatt C\b|Melania|Roger\s+Stone|rona|(Alan\s*)?Weiss?elberg",
        emailers = {
            'Bruce Moskowitz': "'Trump's health guy' according to Epstein",
        }
    ),
    HighlightedGroup(
        label='victim',
        style='orchid1',
        pattern=r'BVI|(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts',
    ),
    HighlightedGroup(
        label='virgin islands',
        style='sea_green1',
        pattern=r'Bahamas|Cecile de Jongh|Dominican\s*Republic|Haiti|(Kenneth E\. )?Mapp|S(ain)?t.?\s*Thomas|USVI|VI|Virgin\s*Islands',
        emailers = {
            STACEY_PLASKETT: 'non-voting member of Congress',
            KENNETH_E_MAPP: 'Governor',
        }
    ),

    # Individuals
    HighlightedGroup(
        label=BILL_GATES,
        style='turquoise4',
        pattern=r'BG|(Bill\s+((and|or)\s+Melinda\s+)?)?Gates|Melinda(\s+Gates)?',
        has_no_category=True,
    ),
    HighlightedGroup(
        label='Rothschild family',
        emailers={
            ARIANE_DE_ROTHSCHILD: None,
            JOHNNY_EL_HACHEM: f'Works with {ARIANE_DE_ROTHSCHILD}',
        },
        style='indian_red'
    ),
    HighlightedGroup(
        label=STEVE_BANNON,
        info='War Room',
        style='color(58)',
        pattern=r'((Steve|Sean)\s+)?Bannon?',
    ),
    HighlightedGroup(
        emailers={STEVEN_HOFFENBERG: HEADER_ABBREVIATIONS['Hoffenberg']},
        pattern=r'(steven?\s*)?hoffenberg?w?',
        style='gold3'
    ),
    HighlightedGroup(emailers={GHISLAINE_MAXWELL: None}, pattern='gmax(1@ellmax.com)?|TerraMar', style='deep_pink3'),
    HighlightedGroup(emailers={JABOR_Y: HEADER_ABBREVIATIONS['Jabor']}, style='spring_green1'),
    HighlightedGroup(emailers={JEFFREY_EPSTEIN: None}, pattern='JEGE|LSJ|Mark (L. )?Epstein', style='blue1'),
    HighlightedGroup(emailers={JOI_ITO: 'former head of MIT Media Lab'}, style='gold1'),
    HighlightedGroup(emailers={KATHRYN_RUEMMLER: 'former Obama legal counsel'}, style='magenta2'),
    HighlightedGroup(emailers={MELANIE_WALKER: 'doctor'}, style='pale_violet_red1'),
    HighlightedGroup(emailers={PAULA: 'maybe Epstein\'s niece?'}, style='pink1'),
    HighlightedGroup(emailers={PRINCE_ANDREW: 'British royal family'}, style='dodger_blue1'),
    HighlightedGroup(emailers={SOON_YI: "wife of Woody Allen"}, style='hot_pink'),
    HighlightedGroup(emailers={SULTAN_BIN_SULAYEM: 'CEO of DP World, chairman of ports in Dubai'}, style='green1'),

    # Highlight regexes for things other than names
    HighlightedGroup(
        label='header_field',
        style='plum4',
        pattern='^(Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):',
        is_multiline=True,
    ),
    HighlightedGroup(
        label='http_links',
        style=f'{ARCHIVE_LINK_COLOR} underline',
        pattern=r"https?:[^\s]+",
        is_multiline=True,
    ),
    HighlightedGroup(
        label='phone_number',
        style=PHONE_NUMBER_STYLE,
        pattern=r"\+?(1?\(?\d{3}\)?[- ]\d{3}[- ]\d{4}|\d{2}[- ]\(?0?\)?\d{2}[- ]\d{4}[- ]\d{4})",
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

COLOR_KEYS = [
    highlight_group.colored_label()
    for highlight_group in sorted(HIGHLIGHTED_GROUPS, key=lambda hg: hg.label)
    if not highlight_group.is_multiline
]


class InterestingNamesHighlighter(RegexHighlighter):
    """rich.highlighter that finds and colors interesting keywords based on the above config."""
    base_style = f"{REGEX_STYLE_PREFIX}."
    highlights = [highlight_group.regex for highlight_group in HIGHLIGHTED_GROUPS]


def get_info_for_name(name: str) -> str | None:
    highlight_group = _get_highlight_group_for_name(name)

    if highlight_group:
        return highlight_group.get_info(name)


def get_style_for_name(name: str | None, default: str = DEFAULT, allow_bold: bool = True) -> str:
    name = name or UNKNOWN
    highlight_group = _get_highlight_group_for_name(name)
    style = highlight_group.style if highlight_group else default
    return style if allow_bold else style.replace('bold', '').strip()


def _get_highlight_group_for_name(name: str) -> HighlightedGroup | None:
    for highlight_group in HIGHLIGHTED_GROUPS:
        if highlight_group.regex.search(name):
            return highlight_group


if args.deep_debug:
    for hg in HIGHLIGHTED_GROUPS:
        print(f"{hg.label}: {hg.regex.pattern}\n")
