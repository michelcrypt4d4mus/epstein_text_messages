import re
from dataclasses import dataclass, field

from rich.highlighter import RegexHighlighter

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import DEFAULT, REDACTED, TIMESTAMP_STYLE
from epstein_files.util.constant.urls import ARCHIVE_LINK_COLOR
from epstein_files.util.constants import EMAILER_ID_REGEXES, HEADER_ABBREVIATIONS, OSBORNE_LLP, REPLY_REGEX, SENT_FROM_REGEX, VIRGIN_ISLANDS
from epstein_files.util.data import extract_last_name, listify
from epstein_files.util.env import args, logger

ESTATE_EXECUTOR = 'Epstein estate executor'
REGEX_STYLE_PREFIX = 'regex'
NO_CATEGORY_LABELS = [BILL_GATES, STEVE_BANNON]
SIMPLE_NAME_REGEX = re.compile(r"^[-\w ]+$", re.IGNORECASE)


@dataclass(kw_only=True)
class HighlightedGroup:
    """
    Encapsulates info about people, places, and other strings we want to highlight with RegexHighlighter.
    Constructor must be called with either an 'emailers' arg or a 'pattern' arg (or both).

    Attributes:
        category (str): optional string to use as an override for self.label in some contexts
        emailers (dict[str, str | None]): optional names to construct regexes for (values are descriptions)
        is_multiline (bool): True if this pattern is only used by RegexHighlighter and this highlight group has no other info
        label (str): RegexHighlighter match group name, defaults to 1st 'emailers' key if only 1 emailer provided
        pattern (str): optional regex pattern identifying strings matching this group
        regex (re.Pattern): matches self.pattern + all first and last names (and pluralizations) in self.emailers
        style (str): Rich style to apply to text matching this group
        _capture_group_label (str): regex capture group variable name for matches of this HighlightedGroup's 'regex'
    """
    category: str = ''
    emailers: dict[str, str | None] = field(default_factory=dict)
    is_multiline: bool = False
    label: str = ''
    pattern: str = ''
    style: str
    # Computed fields
    regex: re.Pattern = field(init=False)
    _capture_group_label: str = field(init=False)

    def __post_init__(self):
        if not (self.emailers or self.pattern):
            raise ValueError(f"Must provide either 'emailers' or 'pattern' arg.")
        elif self.is_multiline and self.emailers:
            raise ValueError(f"'is_multiline' cannot be True when there are 'emailers'.")
        elif not self.label:
            if len(self.emailers) == 1:
                self.label = [k for k in self.emailers.keys()][0]
            else:
                raise ValueError(f"No label provided for {repr(self)}")

        pattern = '|'.join([self._emailer_pattern(e) for e in self.emailers] + listify(self.pattern))
        self._capture_group_label = self.label.lower().replace(' ', '_').replace('-', '_')
        self.theme_style_name = f"{REGEX_STYLE_PREFIX}.{self._capture_group_label}"
        match_group_var = fr"?P<{self._capture_group_label}>"

        if self.is_multiline:
            self.regex = re.compile(fr"({match_group_var}{pattern})", re.IGNORECASE | re.MULTILINE)
        else:
            self.regex = re.compile(fr"\b({match_group_var}({pattern})s?)\b", re.IGNORECASE)

    def get_info(self, name: str) -> str | None:
        """Label for people in this group with the additional info for 'name' if 'name' is in self.emailers."""
        info_pieces = [
            None if len(self.emailers) == 1 else (self.category or self.label.title()),
            self.emailers.get(name),
        ]

        info_pieces = [p for p in info_pieces if p is not None]
        return ', '.join(info_pieces) if info_pieces else None

    # TODO: handle word boundary issue for names that end in symbols
    def _emailer_pattern(self, name: str) -> str:
        """Pattern matching 'name'. Extends value in EMAILER_ID_REGEXES with last name if it exists."""
        last_name = extract_last_name(name)

        if name in EMAILER_ID_REGEXES:
            pattern = EMAILER_ID_REGEXES[name].pattern

            if SIMPLE_NAME_REGEX.match(last_name) and last_name.lower() not in NAMES_TO_NOT_HIGHLIGHT:
                pattern += fr"|{last_name}"  # Include regex for last name

            return pattern
        elif ' ' not in name:
            return name

        first_name = name.removesuffix(f" {last_name}")
        name_patterns = [name.replace(' ', r"\s+"), first_name.replace(' ', r"\s+"), last_name.replace(' ', r"\s+")]
        name_regex_parts = [n for n in name_patterns if n.lower() not in NAMES_TO_NOT_HIGHLIGHT]
        return '|'.join(name_regex_parts)


HIGHLIGHTED_GROUPS = [
    HighlightedGroup(
        label='africa',
        style='light_pink4',
        pattern=r'Econet(\s*Wireless)|Ghana(ian)?|(South\s*)?African?|(Strive\s*)?Masiyiwa|Ugandan?|Zimbabwe(an)?',
    ),
    HighlightedGroup(
        label='bitcoin',
        style='orange1 bold',
        pattern=r'Balaji|bitcoin|block ?chain( capital)?|Brock|coins?|cr[iy]?pto(currenc(y|ies))?|e-currency|(Gavin )?Andressen|(Howard\s+)?Lutnic?k|(jeffrey\s+)?wernick|Libra|Madars|(Patrick\s*)?Murck|(Ross\s*)?Ulbricht|Silk\s*Road|SpanCash|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)',
        emailers = {
            JEREMY_RUBIN: 'developer/researcher',
            SCARAMUCCI: 'Skybridge Capital, FTX investor',
        },
    ),
    HighlightedGroup(
        label='bro',
        style='tan',
        pattern=r"Andrew Farkas|Thomas\s*(J\.?\s*)?Barrack(\s*Jr)?",
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
        pattern=r'Gruterite|(John\s*)?Kluge|Marc Rich|(Mi(chael|ke)\s*)?Ovitz|(Steve\s+)?Wynn|(Leslie\s+)?Wexner|SALSS|Swedish[-\s]*American\s*Life\s*Science\s*Summit|Valhi|(Yves\s*)?Bouvier',
        emailers = {
            ALIREZA_ITTIHADIEH: 'CEO Freestream Aircraft Limited',
            BARBRO_EHNBOM: 'Swedish pharmaceuticals',
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
        label='cannabis',
        style='chartreuse2',
        pattern=r"CBD|cannabis|marijuana|THC|WEED(guide|maps)?[^s]?",
    ),
    HighlightedGroup(
        label='china',
        style='bright_red',
        pattern=r"Ali.?baba|Beijing|CCP|Chin(a|e?se)(?! Daily)|DPRK|Gino\s+Yu|Global Times|Guo|Hong|Huaw[ae]i|Kim\s*Jong\s*Un|Kong|Jack\s+Ma|Kwok|Ministry\sof\sState\sSecurity|Mongolian?|MSS|North\s*Korea|Peking|PRC|SCMP|Tai(pei|wan)|Xi(aomi)?|Jinping",
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
        pattern=r'(Al\s*)?Franken|((Bill|Hillart?y)\s*)?Clinton|((Chuck|Charles)\s*)?Schumer|(Diana\s*)?DeGette|DNC|Elena\s*Kagan|(Eliott?\s*)?Spitzer(, Eliot)?|George\s*Mitchell|(George\s*)?Soros|Hill?ary|Dem(ocrat(ic)?)?|(Jo(e|seph)\s*)?Biden|(John\s*)?Kerry|Lisa Monaco|(Matteo\s*)?Salvini|Maxine\s*Waters|(Barac?k )?Obama|(Nancy )?Pelosi|Ron\s*Dellums|Schumer|(Tim\s*)?Geithner|Vernon\s*Jordan',
    ),
    HighlightedGroup(
        label='Dubin family',
        style='medium_orchid1',
        pattern=r'((Celina|Eva( Anderss?on)?|Glenn) )?Dubin',
        emailers = {
            GLENN_DUBIN: "Highbridge Capital Management, married to Epstein's ex-gf Eva",
            EVA: "possibly Epstein's ex-girlfriend (?)",
        },
    ),
    HighlightedGroup(
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
        }
    ),
    HighlightedGroup(
        label='entertainer',
        style='light_steel_blue3',
        pattern=r'(Art )?Spiegelman|Bobby slayton|bono\s*mick|Errol(\s*Morris)?|Etienne Binant|(Frank\s)?Gehry|Jagger|(Jeffrey\s*)?Katzenberg|(Johnny\s*)?Depp|Kid Rock|Lena\s*Dunham|Madonna|Mark\s*Burnett|Ramsey Elkholy|Steven Gaydos?|Woody( Allen)?|Zach Braff',
        emailers={
            ANDRES_SERRANO: "'Piss Christ' artist",
            'Barry Josephson': 'American film producer and former music manager, editor FamilySecurityMatters.org',
            BILL_SIEGEL: 'documentary film producer and director',
            DAVID_BLAINE: 'famous magician',
            'Richard Merkin': 'painter, illustrator and arts educator',
            STEVEN_PFEIFFER: 'Associate Director at Independent Filmmaker Project (IFP)',
        },
    ),
    HighlightedGroup(
        label='estate_executor',
        style='purple3 bold',
        category='lawyer',
        emailers = {
            DARREN_INDYKE: ESTATE_EXECUTOR,
            RICHARD_KAHN: ESTATE_EXECUTOR,
        }
    ),
    HighlightedGroup(
        label='europe',
        style='light_sky_blue3',
        pattern=r'(Angela )?Merk(el|le)|Austria|(Benjamin\s*)?Harnwell|Berlin|Brexit(eers?)?|Brit(ain|ish)|Brussels|Cannes|(Caroline|Jack)?\s*Lang(, Caroline)?|Cypr(iot|us)|Davos|ECB|EU|Europe(an)?(\s*Union)?|Geneva|Germany?|Gree(ce|k)|Ital(ian|y)|Jacques|Le\s*Pen|London|Macron|Munich|(Natalia\s*)?Veselnitskaya|(Nicholas\s*)?Sarkozy|Nigel(\s*Farage)?|Oslo|Paris|Polish|(Sebastian )?Kurz|(Vi(c|k)tor\s+)?Orbah?n|Edward Rod Larsen|Strauss[- ]?Kahn|Swed(en|ish)(?![-\s]+America)|Switzerland|(Tony\s)?Blair|Ukrain(e|ian)|Vienna|(Vitaly\s*)?Churkin|Zug',
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
        style='medium_purple3',
        category='lawyer',
        pattern=r'(David\s*)?Boies|dersh|(Gloria\s*)?Allred|(Mi(chael|ke)\s*)?Avenatti',
        emailers = {
            ALAN_DERSHOWITZ: 'Harvard Law School professor and all around (in)famous American lawyer',
            KEN_STARR: 'head of the Monica Lewinsky investigation against Bill Clinton',
        }
    ),
    HighlightedGroup(
        label='finance',
        style='green',
        pattern=r'Apollo|Ari\s*Glass|(Bernie\s*)?Madoff|Black(rock|stone)|BofA|Boothbay(\sFund\sManagement)?|Chase\s*Bank|Credit\s*Suisse|DB|Deutsche\s*Bank|Fenner|FRBNY|Goldman(\s*Sachs)|HSBC|(Janet\s*)?Yellen|(Jerome\s*)?Powell(?!M\. Cabot)|(Jimmy\s*)?Cayne|JPMC?|j\.?p\.?\s*morgan(\.?com|\s*Chase)?|Madoff|Merrill(\s*Lynch)?|(Michael\s*)?(Cembalest|Milken)|MLPF&S|(money\s+)?launder(s?|ers?|ing)?(\s+money)?|Morgan Stanley|(Peter L. )?Scher|(Ray\s*)?Dalio|Schwartz?man|Serageldin|UBS|us.gio@jpmorgan.com',
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
        label=HARVARD.lower(),
        style='deep_pink2',
        pattern=r'Cambridge|(Derek\s*)?Bok|Elisa(\s*New)?|Harvard(\s*(Business|Law|University)(\s*School)?)?|(Jonathan\s*)?Zittrain|(Stephen\s*)?Kosslyn',
        emailers = {
            LARRY_SUMMERS: 'board of Digital Currency Group (DCG), Harvard president, Obama economic advisor',
            'Leah Reis-Dennis': 'producer for Lisa New\'s Poetry in America',
            LISA_NEW: f'professor of poetry, wife of {LARRY_SUMMERS}, AKA "Elisa New"',
            'Lisa Randall': 'theoretical physicist',
            MARTIN_NOWAK: 'professor of mathematics and biology',
            MOSHE_HOFFMAN: 'lecturer and research scholar in behavioral and evolutionary economics',
        }
    ),
    HighlightedGroup(
        label='india',
        style='bright_green',
        pattern=r'Anna\s*Hazare|(Arvind\s*)?Kejriwal|Hardeep( Pur[ei]e)?|Indian?|InsightsPod|Modi|Mumbai|Tranchulas',
        emailers = {
            ANIL_AMBANI: 'chairman of Reliance Group',
            VINIT_SAHNI: None,
            ZUBAIR_KHAN: 'Tranchulas CEO, InsightsPod founder',
        }
    ),
    HighlightedGroup(
        label='israel',
        style='dodger_blue2',
        pattern=r"AIPAC|Bibi|(eh|(Ehud|Nili Priell) )?barak|Ehud\s*Barack|Israeli?|Jerusalem|J\s*Street|Mossad|Netanyahu|(Sheldon\s*)?Adelson|Tel\s*Aviv|Yitzhak|Rabin|YIVO|zionist",
        emailers={
            EHUD_BARAK: 'former primer minister',
            'Mitchell Bard': 'director of the American-Israeli Cooperative Enterprise (AICE)',
            'Nili Priell Barak': f'wife of {EHUD_BARAK}',
        }
    ),
    HighlightedGroup(
        label='japan',
        style='color(168)',
        pattern=r'BOJ|(Bank\s+of\s+)?Japan(ese)?|jpy?(?! Morgan)|SG|Singapore|Toky[op]',
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
        pattern=r'Palm\s*Beach\s*(Daily\s*News|Post)|ABC|Alex\s*Yablon|(Andrew\s*)?Marra|Arianna(\s*Huffington)?|(Arthur\s*)?Kretchmer|BBC|Bloomberg|Breitbart|Charlie\s*Rose|China\s*Daily|CNBC|CNN(politics?)?|Conchita|Sarnoff|(?<!Virgin[-\s]Islands[-\s])Daily\s*(Mail|News|Telegraph)|(David\s*)?Pecker|David\s*Brooks|Ed\s*Krassenstein|(Emily\s*)?Michot|Ezra\s*Klein|(George\s*)?Stephanopoulus|Globe\s*and\s*Mail|Graydon(\s*Carter)?|Huffington(\s*Post)?|Ingram, David|(James\s*)?Patterson|Jonathan\s*Karl|Julie\s*(K.?\s*)?Brown|(Katie\s*)?Couric|Keith\s*Larsen|Miami\s*Herald|(Michele\s*)?Dargan|(National\s*)?Enquirer|(The\s*)?N(ew\s*)?Y(ork\s*)?(P(ost)?|T(imes)?)|(The\s*)?New\s*Yorker|NYer|PERVERSION\s*OF\s*JUSTICE|Politico|(Sean\s*)?Hannity|Sulzberger|SunSentinel|Susan Edelman|(Uma\s*)?Sanghvi|(The\s*)?Wa(shington\s*)?Po(st)?|Viceland|Vick[iy]\s*Ward|Vox|WGBH|(The\s*)?Wall\s*Street\s*Journal|WSJ|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk',
        emailers = {
            EDWARD_EPSTEIN: 'no relation to Jeffrey',
            'James Hill': 'ABC',
            JENNIFER_JACQUET: 'Future Science',
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
        pattern=r'Argentin(a|ian)|Bolsonar[aio]|Bra[sz]il(ian)?|Bukele|Caracas|Castro|Colombian?|Cuban?|El\s*Salvador|((Enrique )?Pena )?Nieto|LatAm|Lula|Mexic(an|o)|(Nicolas\s+)?Maduro|Panama( Papers)?|Peru|Venezuelan?|Zambrano',
    ),
    HighlightedGroup(
        label='law enforcement',
        style='color(24) bold',
        pattern=r'ag|(Alicia\s*)?Valle|((Bob|Robert)\s*)?Mueller|(Byung\s)?Pak|CFTC|CIA|CVRA|Dep(artmen)?t\.?\s*of\s*(the\s*)?(Justice|Treasury)|DOJ|FBI|FCPA|FDIC|Federal\s*Bureau\s*of\s*Investigation|FinCEN|FINRA|FOIA|FTC|IRS|(James\s*)?Comey|(Jennifer\s*Shasky\s*)?Calvery|((Judge|Mark)\s*)?(Carney|Filip)|(Kirk )?Blouin|KYC|NIH|NS(A|C)|OCC|OFAC|(Lann?a\s*)?Belohlavek|(Michael\s*)?Reiter|OGE|Office\s*of\s*Government\s*Ethics|Police Code Enforcement|SCOTUS|SD(FL|NY)|Southern\s*District\s*of\s*(Florida|New\s*York)|SEC|Securities\s*and\s*Exchange\s*Commission|State\s*Dep(artmen)?t|Strzok|Supreme\s*Court|Treasury\s*(Dep(artmen)?t|Secretary)|TSA|USAID|(William\s*J\.?\s*)?Zloch',
        emailers = {
            ANN_MARIE_VILLAFANA: 'southern district of Florida U.S. Attorney',
            DANNY_FROST: 'Director of Communications at Manhattan DA',
        }
    ),
    HighlightedGroup(
        label='lawyer',
        style='purple',
        pattern=r'(Barry (E. )?)?Krischer|Kate Kelly|Kirkland\s*&\s*Ellis|(Leon\s*)?Jaworski|Michael J. Pike|Paul,?\s*Weiss|Steptoe|Wein(berg|garten)',
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
        label='victim lawyer',
        style='dark_magenta bold',
        pattern=r'(Alan(\s*P.)?|MINTZ)\s*FRAADE|Paul\s*(G.\s*)?Cassell|Rothstein\s*Rosenfeldt\s*Adler|(Scott\s*)?Rothstein',
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
        pattern=r"[-\s]9/11[\s.]|Abdulmalik Al-Makhlafi|Abdullah|Abu\s+Dhabi|Afghanistan|Al[-\s]?Qa[ei]da|Ahmadinejad|Arab|Aramco|Assad|Bahrain|Basiji?|Benghazi|Cairo|Dj[iu]bo?uti|Doha|Dubai|Egypt(ian)?|Emir(at(es?|i))?|Erdogan|Fashi|Gaddafi|(Hamid\s*)?Karzai|HBJ|Houthi|Imran\s+Khan|Iran(ian)?|Isi[ls]|Islam(abad|ic|ist)?|Istanbul|Kh?ashoggi|(Kairat\s*)?Kelimbetov|kasshohgi|Kaz(akh|ich)stan|Kazakh?|Kh[ao]menei|Khalid\s*Sheikh\s*Mohammed|KSA|Libyan?|Mahmoud|Marra[hk]e[cs]h|MB(N|S|Z)|Mohammed\s+bin\s+Salman|Morocco|Mubarak|Muslim|Nayaf|Pakistani?|Omar|Palestin(e|ian)|Persian?|Riya(dh|nd)|Saddam|Salman|Saudi(\s+Arabian?)?|Shariah?|SHC|sheikh|shia|(Sultan\s*)?Yacoub|Syrian?|(Tarek\s*)?El\s*Sayed|Tehran|Tunisian?|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
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
        pattern=r"Henry Holt|(Matt(hew)? )?Hiltzi[gk]",
        emailers = {
            AL_SECKEL: 'husband of Isabel Maxwell, Mindshift conference organizer who fell off a cliff',
            'Barnaby Marsh': 'co-founder of Saint Partners, a philanthropy services company',
            CHRISTINA_GALBRAITH: None,
            IAN_OSBORNE: f"{OSBORNE_LLP} reputation repairer possibly hired by Epstein ca. 2011-06",
            MICHAEL_SITRICK: None,
            PEGGY_SIEGAL: 'socialite',
            ROSS_GOW: 'Acuity Reputation Management',
            TYLER_SHEARS: None,
        }
    ),
    HighlightedGroup(
        label='republicans',
        style='bold dark_red',
        pattern=r'Alberto\sGonzale[sz]|(Alex\s*)?Acosta|(Bill\s*)?Barr|Bill\s*Shine|(Bob\s*)?Corker|(John\s*(R.?\s*)?)Bolton|Broidy|(Chris\s)?Christie|Devin\s*Nunes|(George\s*)?Nader|GOP|(Brett\s*)?Kavanaugh|Kissinger|Kobach|Kolfage|Kudlow|Lewandowski|(Marco\s)?Rubio|(Mark\s*)Meadows|Mattis|(?<!Merwin Dela )Cruz|(Michael\s)?Hayden|((General|Mike)\s*)?(Flynn|Pence)|(Mitt\s*)?Romney|Mnuchin|Nikki|Haley|(Paul\s+)?Manafort|(Peter\s)?Navarro|Pompeo|Reagan|Republican|(?<!Cynthia )(Richard\s*)?Nixon|Sasse|(Rex\s*)?Tillerson',
        emailers = {
            RUDY_GIULIANI: 'disbarred formed mayor of New York City',
            TULSI_GABBARD: None,
        },
    ),
    HighlightedGroup(
        label='Rothschild family',
        style='indian_red',
        emailers={
            ARIANE_DE_ROTHSCHILD: None,
            JOHNNY_EL_HACHEM: f'Works with {ARIANE_DE_ROTHSCHILD}',
        },
    ),
    HighlightedGroup(
        label='russia',
        style='red bold',
        pattern=r'Alfa\s*Bank|Anya\s*Rasulova|Chernobyl|Day\s+One\s+Ventures|(Dmitry\s)?(Kiselyov|(Lana\s*)?Pozhidaeva|Medvedev|Rybolo(o?l?ev|vlev))|Dmitry|FSB|GRU|KGB|Kislyak|Kremlin|Lavrov|Lukoil|Moscow|(Oleg\s*)?Deripaska|Oleksandr Vilkul|Rosneft|RT|St.?\s*?Petersburg|Russian?|Sberbank|Soviet(\s*Union)?|USSR|(Vladimir\s*)?(Putin|Yudashkin)|Xitrans',
        emailers = {
            MASHA_DROKOVA: 'silicon valley VC, former Putin Youth',
            RENATA_BOLOTOVA: 'former aspiring model, now fund manager at New York State Insurance Fund',
            SVETLANA_POZHIDAEVA: f'Epstein\'s Russian assistant who was recommended for a visa by Sergei Belyakov (FSB) and {DAVID_BLAINE}',
        }
    ),
    HighlightedGroup(
        label='scholar',
        style='light_goldenrod2',
        pattern=r'Alain Forget|Brotherton|Carl\s*Sagan|Columbia|David Grosof|J(ames|im)\s*Watson|(Lord\s*)?Martin\s*Rees|MIT(\s*Media\s*Lab)?|Media\s*Lab|Minsky|((Noam|Valeria)\s*)?Chomsky|Praluent|Regeneron|(Richard\s*)?Dawkins|Sanofi|Stanford|(Stephen\s*)?Hawking|(Steven?\s*)?Pinker|UCLA',
        emailers = {
            DAVID_HAIG: None,
            JOSCHA_BACH: 'cognitive science / AI research',
            'Daniel Kahneman': 'Nobel economic sciences laureate and cognitivie psychologist (?)',
            LAWRENCE_KRAUSS: 'theoretical physicist',
            LINDA_STONE: 'ex-Microsoft, MIT Media Lab',
            MARK_TRAMO: 'professor of neurology at UCLA',
            NEAL_KASSELL: None,
            PETER_ATTIA: 'longevity medicine',
            ROBERT_TRIVERS: 'evolutionary biology',
            ROGER_SCHANK: 'Teachers College, Columbia University',
        },
    ),
    HighlightedGroup(
        label='tech bro',
        style='bright_cyan',
        pattern=r"AG?I|Chamath|Palihapitiya|Drew\s*Houston|Eric\s*Schmidt|Greylock(\s*Partners)?|(?<!Moshe\s)Hoffmand?|LinkedIn|(Mark\s*)?Zuckerberg|Masa(yoshi)?(\sSon)?|Najeev|Nathan\s*Myhrvold|Palantir|(Peter\s)?Th(ie|ei)l|Pierre\s*Omidyar|Sergey\s*Brin|Silicon\s*Valley|Softbank|SpaceX|Tim\s*Ferriss?|WikiLeak(ed|s)",
        emailers = {
            'Auren Hoffman': 'CEO of SafeGraph (firm that gathers location data from mobile devices) and LiveRamp',
            ELON_MUSK: 'father of Mecha-Hitler',
            PETER_THIEL: 'Paypal mafia member, founder of Palantir, early Facebook investor, reactionary',
            REID_HOFFMAN: 'PayPal mafia member, founder of LinkedIn',
            STEVEN_SINOFSKY: 'ex-Microsoft',
        },
    ),
    HighlightedGroup(
        label='trump',
        style='red3 bold',
        pattern=r"@?realDonaldTrump|(Alan\s*)?Weiss?elberg|\bDJ?T\b|Donald J. Tramp|(Donald\s+(J\.\s+)?)?Trump(ism|\s*Properties)?|Don(ald| *Jr)(?! Rubin)|Ivana|(Madeleine\s*)?Westerhout|Mar[-\s]*a[-\s]*Lago|(Marla\s*)?Maples|(Matt(hew)? )?Calamari|\bMatt C\b|Melania|(Michael (J.? )?)?Boccio|Roger\s+Stone|rona|(The\s*)?Art\s*of\s*the\s*Deal",
        emailers = {
            'Bruce Moskowitz': "'Trump's health guy' according to Epstein",
        }
    ),
    HighlightedGroup(
        label='victim',
        style='orchid1',
        pattern=r'BVI|(Jane|Tiffany)\s*Doe|Katie\s*Johnson|(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts',
    ),
    HighlightedGroup(
        label=VIRGIN_ISLANDS,
        style='sea_green1',
        pattern=r'Bahamas|Dominican\s*Republic|(Great|Little)\s*St.?\s*James|Haiti(an)?|(John\s*)deJongh(\s*Jr\.?)|(Kenneth E\. )?Mapp|Palm\s*Beach(?!\s*Post)|PBI|S(ain)?t.?\s*Thomas|USVI|VI|(The\s*)?Virgin\s*Islands(\s*Daily\s*News)?',  # TODO: VI Daily News should be yellow but it's hard bc Daily News xists
        emailers = {
            CECILE_DE_JONGH: f'First lady of the Virgin Islands 2007-2015',
            STACEY_PLASKETT: 'non-voting member of Congress',
            KENNETH_E_MAPP: 'Governor',
        }
    ),

    # Individuals
    HighlightedGroup(
        label=BILL_GATES,
        style='turquoise4',
        pattern=r'BG|b?g?C3|(Bill\s*((and|or)\s*Melinda\s*)?)?Gates|Melinda(\s*Gates)?|Microsoft|MSFT',
        emailers = {
            BORIS_NIKOLIC: f'biotech VC partner of {BILL_GATES}, {ESTATE_EXECUTOR}',
        },
    ),
    HighlightedGroup(
        label=STEVE_BANNON,
        style='color(58)',
        pattern=r'((Steve|Sean)\s*)?Bannon?',
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

    # Highlight regexes for things other than names, only used by RegexHighlighter pattern matching
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
        style='bright_green',
        pattern=r"\+?(1?\(?\d{3}\)?[- ]\d{3}[- ]\d{4}|\d{2}[- ]\(?0?\)?\d{2}[- ]\d{4}[- ]\d{4})|[\d+]{10,12}",
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
        style=TIMESTAMP_STYLE,
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


class InterestingNamesHighlighter(RegexHighlighter):
    """rich.highlighter that finds and colors interesting keywords based on the above config."""
    base_style = f"{REGEX_STYLE_PREFIX}."
    highlights = [highlight_group.regex for highlight_group in HIGHLIGHTED_GROUPS]


def get_info_for_name(name: str) -> str | None:
    highlight_group = _get_highlight_group_for_name(name)

    if highlight_group:
        return highlight_group.get_info(name)


def get_style_for_name(name: str | None, default_style: str = DEFAULT, allow_bold: bool = True) -> str:
    highlight_group = _get_highlight_group_for_name(name or UNKNOWN)
    style = highlight_group.style if highlight_group else default_style
    return style if allow_bold else style.replace('bold', '').strip()


def _get_highlight_group_for_name(name: str) -> HighlightedGroup | None:
    for highlight_group in HIGHLIGHTED_GROUPS:
        if highlight_group.regex.search(name):
            return highlight_group


if args.deep_debug:
    for hg in HIGHLIGHTED_GROUPS:
        print(f"{hg.label}: {hg.regex.pattern}\n")
