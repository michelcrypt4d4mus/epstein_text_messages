import re
from typing import Sequence

from epstein_files.util.constant.strings import PALM_BEACH, QUESTION_MARKS, VIRGIN_ISLANDS
from epstein_files.util.helpers.string_helper import remove_question_marks

Name = str | None

# Unknown / None
UNKNOWN = '(unknown)'
UNKNOWN_GIRL = 'unknown girl'

# Texting Names
ANDRZEJ_DUDA = 'Andrzej Duda or entourage'
ANIL_AMBANI = "Anil Ambani"
ANTHONY_SCARAMUCCI = "Anthony Scaramucci"
ARDA_BESKARDES = 'Arda Beskardes'
EVA = 'Eva (Dubin?)'
JEFFREY_EPSTEIN = 'Jeffrey Epstein'
JOI_ITO = 'Joi Ito'
LARRY_SUMMERS = 'Larry Summers'
MELANIE_WALKER = 'Melanie Walker'
MIROSLAV_LAJCAK = 'Miroslav Lajčák'
STACEY_PLASKETT = 'Stacey Plaskett'
SOON_YI_PREVIN = 'Soon-Yi Previn'
STEVE_BANNON = 'Steve Bannon'
STEVEN_SINOFSKY = 'Steven Sinofsky'
TERJE_ROD_LARSEN = 'Terje Rød-Larsen'

# Email Names - no trailing periods! (messes up regexes)
AL_SECKEL = 'Al Seckel'
ALAN_DERSHOWITZ = 'Alan Dershowitz'
ALAN_DLUGASH = 'Alan Dlugash'
ALIREZA_ITTIHADIEH = 'Alireza Ittihadieh'
AMANDA_ENS = 'Amanda Ens'
ANASTASIYA_SIROOCHENKO = 'Anastasiya Siroochenko'
ANDRES_SERRANO = 'Andres Serrano'
ANN_MARIE_VILLAFANA = 'Ann Marie Villafana'
ANAS_ALRASHEED = 'Anas Alrasheed'
ANTHONY_BARRETT = 'Anthony Barrett'
ANYA_RASULOVA = 'Anya Rasulova'
ARIANE_DE_ROTHSCHILD = 'Ariane de Rothschild'
AZIZA_ALAHMADI = 'Aziza Alahmadi'
BARBRO_C_EHNBOM = 'Barbro C. Ehnbom'
BARRY_J_COHEN = 'Barry J. Cohen'
BEN_GOERTZEL = 'Ben Goertzel'
BENNET_MOSKOWITZ = 'Bennet Moskowitz'
BILL_SIEGEL = 'Bill Siegel'
BOB_CROWE = 'Bob Crowe'
BRAD_EDWARDS = 'Brad Edwards'
BRAD_KARP = 'Brad Karp'
BRAD_WECHSLER = 'Brad Wechsler'
BRYAN_BISHOP = 'Bryan Bishop'
BORIS_NIKOLIC = 'Boris Nikolic'
CAROLYN_RANGEL = 'Carolyn Rangel'
CECILE_DE_JONGH = 'Cecile de Jongh'
CECILIA_STEEN = 'Cecilia Steen'
CELINA_DUBIN = 'Celina Dubin'
CHRISTINA_GALBRAITH = 'Christina Galbraith'  # Works with Tyler Shears on reputation stuff
DANGENE_AND_JENNIE_ENTERPRISE = 'Dangene and Jennie Enterprise'
DANIEL_SABBA = 'Daniel Sabba'
DANIEL_SIAD = 'Daniel Siad'
DANNY_FROST = 'Danny Frost'
DARREN_INDYKE = 'Darren Indyke'
DAVID_BLAINE = 'David Blaine'
DAVID_FISZEL = 'David Fiszel'
DAVID_HAIG = 'David Haig'
DAVID_INGRAM = 'David Ingram'
DAVID_MITCHELL = 'David Mitchell'
DAVID_SCHOEN = 'David Schoen'
DAVID_STERN = 'David Stern'
DEBBIE_FEIN = 'Debbie Fein'
DEEPAK_CHOPRA = 'Deepak Chopra'
DIANE_ZIMAN = 'Diane Ziman'
DONALD_NORMAN = 'Donald Norman'
DONALD_TRUMP = 'Donald Trump'
EDUARDO_ROBLES = 'Eduardo Robles'
EDWARD_JAY_EPSTEIN = 'Edward Jay Epstein'
EDWARD_ROD_LARSEN = 'Edward Rod Larsen'
EHUD_BARAK = 'Ehud Barak'
ERIC_ROTH = 'Eric Roth'
ETIENNE_BINANT = 'Etienne Binant'
EVA_DUBIN = 'Eva Dubin'
FAITH_KATES = 'Faith Kates'
FRANCESCA_HALL = 'Francesca Hall'
FRED_HADDAD = 'Fred Haddad'
GERALD_BARTON = 'Gerald Barton'
GERALD_LEFCOURT = 'Gerald Lefcourt'
GHISLAINE_MAXWELL = 'Ghislaine Maxwell'
GINO_YU = 'Gino Yu'
GLENN_DUBIN = 'Glenn Dubin'
GORDON_GETTY = 'Gordon Getty'
GWENDOLYN_BECK = 'Gwendolyn Beck'         # https://www.lbc.co.uk/article/who-gwendolyn-beck-epstein-andrew-5HjdN66_2/
HAMAD_BIN_JASSIM = 'Hamad bin Jassim al-Thani'
HEATHER_MANN = 'Heather Mann'
IAN_OSBORNE = 'Ian Osborne'
INTELLIGENCE_SQUARED = 'Intelligence Squared'
JACK_GOLDBERGER = 'Jack Goldberger'
JACK_SCAROLA = 'Jack Scarola'
JACKIE_PERCZEK = 'Jackie Perczek'
JAMES_HILL = 'James Hill'
JANUSZ_BANASIAK = 'Janusz Banasiak'
JAY_LEFKOWITZ = 'Jay Lefkowitz'
JEAN_HUGUEN = 'Jean Huguen'
JEAN_LUC_BRUNEL = 'Jean Luc Brunel'
JEFF_FULLER = 'Jeff Fuller'
JENNIE_SAUNDERS = 'Jennie Saunders'
JENNIFER_JACQUET = 'Jennifer Jacquet'
JENNIFER_KALIN = 'Jennifer Kalin'
JEREMY_RUBIN = 'Jeremy Rubin'             # Bitcoin dev
JES_STALEY = 'Jes Staley'
JESSICA_CADWELL = 'Jessica Cadwell'       # Paralegal?
JIDE_ZEITLIN = 'Jide Zeitlin'
JOHN_BROCKMAN = "John Brockman"
JOHN_PAGE = 'John Page'
JOHNNY_EL_HACHEM = 'Johnny el Hachem'
JOJO_FONTANILLA = 'Jojo Fontanilla'
JONATHAN_FARKAS = 'Jonathan Farkas'
JOSCHA_BACH = 'Joscha Bach'
JP_MORGAN_USGIO = 'us.gio@jpmorgan.com'
KARIM_WADE = 'Karim Wade'
KATHERINE_KEATING = 'Katherine Keating'
KATHRYN_RUEMMLER = 'Kathryn Ruemmler'
KEN_JENNE = 'Ken Jenne'
KEN_STARR = 'Ken Starr'
KENNETH_E_MAPP = 'Kenneth E. Mapp'
LANDON_THOMAS = 'Landon Thomas Jr'
LAWRANCE_VISOSKI = 'Lawrance Visoski'
LAWRENCE_KRAUSS = 'Lawrence Krauss'
LEON_BLACK = 'Leon Black'
LESLEY_GROFF = 'Lesley Groff'
LILLY_SANCHEZ = 'Lilly Sanchez'
LINDA_STONE = 'Linda Stone'
LISA_NEW = 'Lisa New'
LISA_RANDALL = 'Lisa Randall'
LYN_FONTANILLA = 'Lyn Fontanilla'
MANUELA_MARTINEZ = 'Manuela Martinez'
MARC_LEON = 'Marc Leon'
MARIANA_IDZKOWSKA = 'Mariana Idźkowska'
MARK_EPSTEIN = 'Mark Epstein'
MARK_TRAMO = 'Mark Tramo'
MARTIN_NOWAK = 'Martin Nowak'
MARTIN_WEINBERG = "Martin Weinberg"
MARIA_PRUSAKOVA = 'Maria Prusakova'
MASAYOSHI_SON = 'Masayoshi Son'
MASHA_DROKOVA = 'Masha Drokova'
MATTHEW_HILTZIK = 'Matthew Hiltzik'
MELANIE_SPINELLA = 'Melanie Spinella'
MERWIN_DELA_CRUZ = 'Merwin Dela Cruz'
MICHAEL_BUCHHOLTZ = 'Michael Buchholtz'
MICHAEL_MILLER = 'Michael Miller'
MICHAEL_SITRICK = 'Michael Sitrick'
MICHAEL_WOLFF = "Michael Wolff"
MOHAMED_WAHEED_HASSAN = 'Mohamed Waheed Hassan'
MORTIMER_ZUCKERMAN = 'Mortimer Zuckerman'
MOSHE_HOFFMAN = 'Moshe Hoffman'
NADIA_MARCINKO = 'Nadia Marcinko'
NEAL_KASSELL = 'Neal Kassell'
NICHOLAS_RIBIS = 'Nicholas Ribis'
NILI_PRIELL_BARAK = 'Nili Priell Barak'
NOAM_CHOMSKY = 'Noam Chomsky'
NORMAN_D_RAU = 'Norman D. Rau'
OLIVIER_COLOM = 'Olivier Colom'
PAUL_BARRETT = 'Paul Barrett'
PAUL_KRASSNER = 'Paul Krassner'
PAUL_MORRIS = 'Paul Morris'
PAUL_PROSPERI = 'Paul Prosperi'
PAULA_HEIL_FISHER = f"Paula Heil Fisher"  # the last email about opera lines up but if Fisher was supposedly w/Epstein at Bear Stearns the timeline is a bit weird for her to call him "Unc"
PEGGY_SIEGAL = 'Peggy Siegal'
PETER_ATTIA = 'Peter Attia'
PETER_MANDELSON = 'Peter Mandelson'
PETER_THIEL = 'Peter Thiel'
PRINCE_ANDREW = 'Prince Andrew'
PUREVSUREN_LUNDEG = 'Purevsuren Lundeg'
RAAFAT_ALSABBAGH = 'Raafat Alsabbagh'
REINALDO_AVILA_DA_SILVA = 'Reinaldo Avila Da Silva'
REID_HOFFMAN = 'Reid Hoffman'
REID_WEINGARTEN = 'Reid Weingarten'
RENATA_BOLOTOVA = 'Renata Bolotova'
RICHARD_KAHN = 'Richard Kahn'
ROBERT_D_CRITTON_JR = 'Robert D. Critton Jr.'
ROBERT_LAWRENCE_KUHN = 'Robert Lawrence Kuhn'
ROBERT_TRIVERS = 'Robert Trivers'
ROGER_SCHANK = 'Roger Schank'
ROSS_GOW = 'Ross Gow'
SAMUEL_LEFF = 'Samuel Leff'
SCOTT_J_LINK = 'Scott J. Link'
SEAN_BANNON = 'Sean Bannon'
SHAHER_ABDULHAK_BESHER = f'Shaher Abdulhak Besher'
STANLEY_POTTINGER = 'Stanley Pottinger'
STEPHEN_HANSON = 'Stephen Hanson'
STEVEN_HOFFENBERG = 'Steven Hoffenberg'
STEVEN_PFEIFFER = 'Steven Pfeiffer'
SULTAN_BIN_SULAYEM = 'Sultan Ahmed Bin Sulayem'
SVETLANA_POZHIDAEVA = 'Svetlana Pozhidaeva'
TERRY_KAFKA = 'Terry Kafka'
THANU_BOONYAWATANA = 'Thanu Boonyawatana'
THORBJORN_JAGLAND = 'Thorbjørn Jagland'
TOM_BARRACK = 'Tom Barrack'
TOM_PRITZKER = 'Tom Pritzker'
TONJA_HADDAD_COLEMAN = 'Tonja Haddad Coleman'
TYLER_SHEARS = 'Tyler Shears'  # Reputation manager, like Al Seckel
VINCENZO_IOZZO = 'Vincenzo Iozzo'
VINIT_SAHNI = 'Vinit Sahni'
WOODY_ALLEN = 'Woody Allen'
ZUBAIR_KHAN = 'Zubair Khan'

# DOJ files emails
ADAM_BACK = 'Adam Back'
ALEKSANDRA_KARPOVA = 'Aleksandra Karpova'
ALISON_J_NATHAN = 'Alison J. Nathan'
AMIR_TAAKI = 'Amir Taaki'
ANDREW_FARKAS = 'Andrew Farkas'
ANDREW_MCCORMACK = 'Andrew McCormack'
ANNA_KASATKINA = 'Anna Kasatkina'
ANTOINE_VERGLAS = 'Antoine Verglas'
ARIANNA_SIMPSON = 'Arianna Simpson'
AUDREY_STRAUSS = 'Audrey Strauss'
AUSTIN_HILL = 'Austin Hill'
BARNABY_MARSH = 'Barnaby Marsh'
BELLA_KLEIN = 'Bella Klein'
BILL_RICHARDSON = 'Bill Richardson'
BOBBI_C_STERNHEIM = 'Bobbi C. Sternheim'
BOBBY_KOTICK = 'Bobby Kotick'
BROCK_PIERCE = 'Brock Pierce'
CHRIS_POOLE = 'Chris Poole'
CHRISTIAN_EVERDELL = 'Christian Everdell'
CHRISTOPHER_DILORIO = 'Christopher Dilorio'
DANIEL_SCHMACHTENBERGER = 'Daniel Schmachtenberger'
DAPHNE_WALLACE = 'Daphne Wallace'
DASHA_GRUPMAN = 'Dasha Grupman'
DAVID_L_NEUHAUSER = 'David L. Neuhauser'
DAVID_RODGERS = 'David Rodgers'
DOUGLAS_WIGDOR = 'Douglas Wigdor'
ED_BOYLE = 'Ed Boyle'
ELON_MUSK = 'Elon Musk'
EMAD_HANNA = 'Emad Hanna'
FILIPA_PEROVIC = 'Filipa Perovic'
FAWZI_SIAM = 'Fawzi Siam'
GANBAT_CHULUUNKHUU = 'Ganbat Chuluunkhuu'
GAVIN_ANDRESEN = 'Gavin Andresen'
GIANNI_SERAZZI = 'Gianni Serazzi'
GREG_WYLER = 'Greg Wyler'
HASSAN_JAMEEL = 'Hassan Jameel'
HENRY_JARECKI = 'Henry Jarecki'
HONGBO_ROBERT_BAO = 'Hongbo Robert Bao'
HOSAIN_RAHMAN = 'Hosain Rahman'
HOWARD_LUTNICK = 'Howard Lutnick'
IAN_ODONNELL = "Ian O'Donnell"
JAMES_CAYNE = 'James Cayne'
JAMES_FITZGERALD = 'James Fitzgerald'
JAMES_TAGG = 'James Tagg'
JASON_CALACANIS = 'Jason Calacanis'
JEM_BENDELL = 'Jem Bendell'
JESSICA_BANKS = 'Jessica Banks'
JOSHUA_FINK = 'Joshua Fink'
JULIA_SANTOS = 'Julia Santos'
KARYNA_SHULIAK = 'Karyna Shuliak'
KIMBAL_MUSK = 'Kimbal Musk'
KIRA_DIKHTYAR = 'Kira Dikhtyar'
LASMA_KUHTARSKA = 'Lasma Kuhtarska'
LAURA_A_MENNINGER = 'Laura A. Menninger'
LORENZO_DE_MEDICI = 'Lorenzo de Medici'
LUKE_D_THORBURN = 'Luke D. Thorburn'
MADARS_VIRZA = 'Madars Virza'
MARK_ZEFF = 'Mark Zeff'
MELANIE_PHILLIPS = 'Melanie Phillips'
MICHAEL_FOWLER = 'Michael Fowler'
NICOLE_JUNKERMANN = 'Nicole Junkermann'
OLGA_PONOMAR_BECKER = 'Olga Ponomar-Becker'
OLIVER_GOODENOUGH = 'Oliver Goodenough'
PAOLO_ZAMPOLLI = 'Paolo Zampolli'
PERKINS_COIE = 'Perkins Coie'
PERRY_LANG = 'Perry Lang'
PHILIP_ROSEDALE = 'Philip Rosedale'
RAMSEY_ELKHOLY = 'Ramsey Elkholy'
RASSECK_BOURGI = 'Rasseck Bourgi'
SANITA = 'Sanita'
SETH_LLOYD = 'Seth Lloyd'
STACEY_RICHMAN = 'Stacey Richman'
STEVEN_VICTOR_MD = 'Steven Victor MD'
STORY_COWLES = 'Story Cowles'
SUE = 'Sue'
TANCREDI_MARCHIOLO = 'Tancredi Marchiolo'
UMAR_DZHABRAILOV = 'Umar Dzhabrailov'
WHITFIELD_DIFFIE = 'Whitfield Diffie'
YUKO_BARNABY = 'Yuko Barnaby'
YULIA_DOROKHINA = 'Yulia Dorokhina'
YURI_MILNER = 'Yuri Milner'

# No communications but name is in the files
BEN_LAWSKY = 'Ben Lawsky'
BILL_GATES = 'Bill Gates'
CHAMATH_PALIHAPITIYA = 'Chamath Palihapitiya'
DONALD_TRUMP = 'Donald Trump'
GEORGE_VRADENBURG = 'George Vradenburg'
GLORIA_ALLRED = 'Gloria Allred'
HENRY_HOLT = 'Henry Holt'  # Actually a company?
IVANKA = 'Ivanka'
JAMES_PATTERSON = 'James Patterson'
JARED_KUSHNER = 'Jared Kushner'
JEANNE_M_CHRISTENSEN = 'Jeanne M. Christensen'
JEFFREY_WERNICK = 'Jeffrey Wernick'
JULIE_K_BROWN = 'Julie K. Brown'
KARIM_SADJADPOUR = 'KARIM SADJADPOUR'.title()
MICHAEL_J_BOCCIO = 'Michael J. Boccio'
MILES_GUO = 'Miles Guo'
NAOMI_CAMPBELL = 'Naomi Campbell'
NERIO_ALESSANDRI = 'Nerio Alessandri (Founder and Chairman of Technogym S.p.A. Italy)'
PAUL_G_CASSELL = 'Paul G. Cassell'
RUDY_GIULIANI = 'Rudy Giuliani'
SERGEY_BELYAKOV = 'Sergey Belyakov'
STEVE_WYNN = 'Steve Wynn'
TED_LEONSIS = 'Ted Leonsis'
TULSI_GABBARD = 'Tulsi Gabbard'
VIRGINIA_GIUFFRE = 'Virginia Giuffre'

# Organizations
ALL_IN_PODCAST = 'All-In Podcast'
ASIA_GATEWAY = 'Asia Gateway'
ATORUS = 'ATorus'
ATT_COURT_APPEARANCE_TEAM = 'AT&T Court Appearance Team'
BANQUE_HAVILLAND = 'Banque Havilland'
BEAR_STEARNS = 'Bear Stearns'
BLOCKCHAIN_CAPITAL = 'Blockchain Capital'
BLOCKSTREAM = 'Blockstream'
BOFA = 'BofA'
BOFA_MERRILL = f'{BOFA} / Merrill Lynch'
BUREAU_OF_PRISONS = 'Bureau of Prisons'
CANTOR = 'Cantor Fitzgerald'
CANTOR_URRAMOOR = 'Cantor Urramoor Asset Management'
CARBYNE = 'Carbyne'
CLIFFORD_CHANCE = 'Clifford Chance'
COINBASE = 'Coinbase'
CRYPTO_CURRENCY_PARTNERS_II = 'Crypto Currency Partners II'
CRYPTO_PR_LAB = 'Crypto PR Lab'
DEUTSCHE_BANK = 'Deutsche Bank'
DOJ = 'DOJ'
EDMOND_DE_ROTHSCHILD = 'Edmond de Rothschild'
ELECTRON_CAPITAL_PARTNERS = 'Electron Capital Partners'
EPSTEIN_FOUNDATION = 'Jeffrey Epstein VI Foundation'
EXPRESSCOIN = 'ExpressCoin'
FBI = 'FBI'
GOLDMAN_SACHS = 'Goldman Sachs'
GOOGLE_PLUS = 'Google Plus'
HEDOSOPHIA = 'Hedosophia'
INSIGHTS_POD = f"InsightsPod"  # Zubair bots
INTERNATIONAL_PEACE_INSTITUTE = 'International Peace Institute'
JP_MORGAN = 'JP Morgan'
KYARA_INVESTMENT = 'Kyara Investment'
LAWRENCE_KRAUSS_ASU_ORIGINS = f"{LAWRENCE_KRAUSS}'s ASU Origins Project"
MC2_MODEL_MGMT = 'MC2 Model Management'
MERCANTILE_GLOBAL_HOLDINGS = 'Mercantile Global Holdings'
MIT_MEDIA_LAB = 'MIT Media Lab'
MOUNT_SINAI = 'Mount Sinai'
NEXT_MANAGEMENT = 'Next Management LLC'
NOBEL_CHARITABLE_TRUST = 'Nobel Charitable Trust'
OFFICE_OF_THE_DEPUTY_ATTORNEY_GENERAL = 'Office of the Deputy Attorney General'
OSBORNE_LLP = f"{IAN_OSBORNE} & Partners"  # Ian Osborne's PR firm
PALM_BEACH_POLICE = f"{PALM_BEACH} Police"
ROTHSTEIN_ROSENFELDT_ADLER = "Rothstein Rosenfeldt Adler"  # and a crook
SDNY = 'SDNY'
SECURITIES_AND_EXCHANGE_COMMISSION = 'Securities & Exchange Commission'
SOUTHERN_TRUST_COMPANY = 'Southern Trust Company'
TRUMP_ORG = 'Trump Organization'
UBS = 'UBS'
USANYS = 'USANYS'
US_ORG = 'US Office of Government Information Services'
VALAR_GLOBAL_FUND = 'Valar Global Fund'
VALAR_VENTURES = 'Valar Ventures'

# Locations
LITTLE_SAINT_JAMES = 'Little Saint James'

# Publications
BBC = 'BBC'
BLOOMBERG = 'Bloomberg'
CHINA_DAILY = "China Daily"
CNN = 'CNN'
DAILY_MAIL = 'Daily Mail'
DAILY_TELEGRAPH = "Daily Telegraph"
LA_TIMES = 'LA Times'
LEXIS_NEXIS = 'Lexis Nexis'
MIAMI_HERALD = 'Miami Herald'
NYT = "New York Times"
PALM_BEACH_DAILY_NEWS = f'{PALM_BEACH} Daily News'
PALM_BEACH_POST = f'{PALM_BEACH} Post'
SHIMON_POST = 'The Shimon Post'
THE_REAL_DEAL = 'The Real Deal'
VI_DAILY_NEWS = f'{VIRGIN_ISLANDS} Daily News'
WAPO = 'WaPo'


# Names to color white in the word counts
OTHER_NAMES = """
    adam al alain alan alison alfredo allen alex alexander amanda andres andrew angela ann anthony ari asia audrey
    back bard barrett barry ben bennet bernard bill black bo bob boris boyle brad brenner bruce bryan
    cameron capital caroline carolyn chris christian christina christopher cohen collins
    dan daniel danny darren dave david debbie department doj donald douglas dylan
    ed edward edwards elisa enforcement enterprise enterprises entourage epstein eric erik erika etienne
    faith fisher fitzgerald forget frances frank francesca fred friendly frost fuller fund
    gates gateway general gerald george gilbert girl glass gloria gold gordon greg
    haddad hall hanson harry hassan hay heather henry hill ho hoffman howard
    ian inc inc. ivan
    jack james jay jean jeanne jeff jeffrey jennifer jeremy jessica jim joel john jon jonathan joseph jr julia justin
    kafka kahn karl kate katherine kathryn kelly ken kevin krassner
    lang larry larsen laurie lawrence len leon les lesley linda link lisa london love
    management manhattan mann marc maria marie mark martin matthew melanie michael mike miller mitchell miles morris moskowitz
    nancy nathan neal new nicholas nicole nick norman ny
    oleg owen
    paul paula pen perry peter philip pierce plus police prince
    randall rangel reid richard robert roberts rodriguez roger rosenberg ross roth roy rubenstein rubin
    santos scott sean sergey service services simpson skip smith son stacey stanley stein stern stephen steve steven stone story susan
    team terry the thomas tim tom tony trust tyler
    unknown
    ventures victor viktor virginia
    wade waters
    aaron albert alberto alec alexandra alice anderson andre ann anna anne ariana arthur
    baldwin barack barrett ben benjamin berger bert binant bob bonner boyden bradley brady branson bright bruno bryant burton
    chapman charles charlie christopher clint cohen colin collins conway
    davis dean debbie debra deborah dennis diana diane diaz dickinson dixon dominique don dylan
    edmond elizabeth emily entwistle erik evelyn
    ferguson flachsbart francis franco frank
    gardner gary geoff geoffrey gilbert gloria goldberg gonzalez gould graham greene guarino gwyneth
    hancock harold harrison helen hirsch hofstadter horowitz hussein
    isaac isaacson
    jamie jane janet jason jeffrey jen jim joe johnson jones josh julie justin
    kathy kim kruger kyle
    lawrence leo leonard lenny leslie lieberman louis lynch lynn
    marcus marianne matt matthew melissa michele michelle moore moscowitz
    nancy nussbaum
    paulson philippe
    rafael ray richard richardson rob robert robin ron ross rubin rudolph ryan
    sara sarah seligman serge sergey silverman sloman smith snowden sorkin stanley steele stevie stewart
    ted theresa thompson tiffany timothy
    valeria
    walter warren weinstein weiss william
    zach zack
""".strip().split()


def constantize_name(name: str) -> str:
    if name == ANDRZEJ_DUDA:
        return 'ANDRZEJ_DUDA'
    elif name == MIROSLAV_LAJCAK:
        return 'MIROSLAV_LAJCAK'
    elif name == 'Paula Heil Fisher (???)':
        return 'PAULA'

    variable_name = remove_question_marks(name)
    variable_name = variable_name.removesuffix('.').removesuffix('Jr').replace('ź', 'z').replace('ø', 'o').strip()
    variable_name = variable_name.upper().replace('-', '_').replace(' ', '_').replace('.', '')

    if variable_name not in globals():
        return f"'{name}'"
    else:
        return variable_name


def extract_first_name(name: str) -> str:
    if ' ' not in name:
        return name

    return name.removesuffix(f" {extract_last_name(name)}")


def extract_last_name(name: str) -> str:
    if ' ' not in name:
        return name

    first_last_names = remove_question_marks(name).strip().split()

    if first_last_names[-1].startswith('Jr') and len(first_last_names[-1]) <= 3:
        return ' '.join(first_last_names[-2:])
    else:
        return first_last_names[-1]


def reverse_first_and_last_names(name: Name) -> Name:
    """If there's a comma in the name in the style 'Lastname, Firstname', reverse it and remove comma."""
    if name is None:
        return None
    elif '@' in name:
        return name.lower()

    if ', ' in name:
        names = name.split(', ')
        return f"{names[1]} {names[0]}"
    else:
        return name


def sort_names(names: Sequence[Name]) -> list[Name]:
    return sorted(names, key=lambda name: name or UNKNOWN)
