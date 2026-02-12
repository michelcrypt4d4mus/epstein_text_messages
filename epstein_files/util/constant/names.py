from epstein_files.util.constant.strings import QUESTION_MARKS, remove_question_marks

Name = str | None

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
ALIREZA_ITTIHADIEH = 'Alireza Ittihadieh'
AMANDA_ENS = 'Amanda Ens'
ANDRES_SERRANO = 'Andres Serrano'
ANN_MARIE_VILLAFANA = 'Ann Marie Villafana'
ANAS_ALRASHEED = 'Anas Alrasheed'
ANTHONY_BARRETT = 'Anthony Barrett'
ARIANE_DE_ROTHSCHILD = 'Ariane de Rothschild'
AZIZA_ALAHMADI = 'Aziza Alahmadi'
BARBRO_C_EHNBOM = 'Barbro C. Ehnbom'
BARRY_J_COHEN = 'Barry J. Cohen'
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
FAITH_KATES = 'Faith Kates'
FRED_HADDAD = 'Fred Haddad'
GERALD_BARTON = 'Gerald Barton'
GERALD_LEFCOURT = 'Gerald Lefcourt'
GHISLAINE_MAXWELL = 'Ghislaine Maxwell'
GLENN_DUBIN = 'Glenn Dubin'
GORDON_GETTY = 'Gordon Getty'
GWENDOLYN_BECK = 'Gwendolyn Beck'         # https://www.lbc.co.uk/article/who-gwendolyn-beck-epstein-andrew-5HjdN66_2/
HEATHER_MANN = 'Heather Mann'
IAN_OSBORNE = 'Ian Osborne'
INTELLIGENCE_SQUARED = 'Intelligence Squared'
JABOR_Y = 'Jabor Y'                       # mysterious 'influential man in Qatar"
JACK_GOLDBERGER = 'Jack Goldberger'
JACK_SCAROLA = 'Jack Scarola'
JACKIE_PERCZEK = 'Jackie Perczek'
JAMES_HILL = 'James Hill'
JANUSZ_BANASIAK = 'Janusz Banasiak'
JAY_LEFKOWITZ = 'Jay Lefkowitz'
JEAN_HUGUEN = 'Jean Huguen'
JEAN_LUC_BRUNEL = 'Jean Luc Brunel'
JEFF_FULLER = 'Jeff Fuller'
JENNIFER_JACQUET = 'Jennifer Jacquet'
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
LYN_FONTANILLA = 'Lyn Fontanilla'
MANUELA_MARTINEZ = 'Manuela Martinez'
MARC_LEON = 'Marc Leon'
MARIANA_IDZKOWSKA = 'Mariana Idźkowska'
MARK_EPSTEIN = 'Mark Epstein'
MARK_TRAMO = 'Mark Tramo'
MARTIN_NOWAK = 'Martin Nowak'
MARTIN_WEINBERG = "Martin Weinberg"
MARIYA_PRUSAKOVA = 'Maria Prusakova'
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
PAULA = f"Paula Heil Fisher {QUESTION_MARKS}"  # the last email about opera lines up but if Fisher was supposedly w/Epstein at Bear Stearns the timeline is a bit weird for her to call him "Unc"
PEGGY_SIEGAL = 'Peggy Siegal'
PETER_ATTIA = 'Peter Attia'
PETER_MANDELSON = 'Peter Mandelson'
PETER_THIEL = 'Peter Thiel'
PRINCE_ANDREW = 'Prince Andrew'
PUREVSUREN_LUNDEG = 'Purevsuren Lundeg'
RAAFAT_ALSABBAGH = 'Raafat Alsabbagh'
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
ZUBAIR_KHAN = 'Zubair Khan'

UNKNOWN = '(unknown)'

# DOJ files emails
ADAM_BACK = 'Adam Back'
ALEKSANDRA_KARPOVA = 'Aleksandra Karpova'
ALISON_J_NATHAN = 'Alison J. Nathan'
AMIR_TAAKI = 'Amir Taaki'
ANDREW_FARKAS = 'Andrew Farkas'
ANDREW_MCCORMACK = 'Andrew McCormack'
AUDREY_STRAUSS = 'Audrey Strauss'
AUSTIN_HILL = 'Austin Hill'
BOBBI_C_STERNHEIM = 'Bobbi C. Sternheim'
BROCK_PIERCE = 'Brock Pierce'
CHRISTIAN_EVERDELL = 'Christian Everdell'
CHRISTOPHER_DILORIO = 'Christopher Dilorio'
DOUGLAS_WIGDOR = 'Douglas Wigdor'
ED_BOYLE = 'Ed Boyle'
ELON_MUSK = 'Elon Musk'
GANBAT_CHULUUNKHUU = 'Ganbat Chuluunkhuu'
HASSAN_JAMEEL = 'Hassan Jameel'
IAN_ODONNELL = "Ian O'Donnell"
JAMES_FITZGERALD = 'James Fitzgerald'
JULIA_SANTOS = 'Julia Santos'
KARYNA_SHULIAK = 'Karyna Shuliak'
LORENZO_DE_MEDICI = 'Lorenzo de Medici'
NICOLE_JUNKERMANN = 'Nicole Junkermann'
STACEY_RICHMAN = 'Stacey Richman'

# No communications but name is in the files
BILL_GATES = 'Bill Gates'
DONALD_TRUMP = 'Donald Trump'
HENRY_HOLT = 'Henry Holt'  # Actually a company?
IVANKA = 'Ivanka'
JAMES_PATTERSON = 'James Patterson'
JARED_KUSHNER = 'Jared Kushner'
JEANNE_M_CHRISTENSEN = 'Jeanne M. Christensen'
JEFFREY_WERNICK = 'Jeffrey Wernick'
JULIE_K_BROWN = 'Julie K. Brown'
KARIM_SADJADPOUR = 'KARIM SADJADPOUR'.title()
MICHAEL_J_BOCCIO = 'Michael J. Boccio'
NERIO_ALESSANDRI = 'Nerio Alessandri (Founder and Chairman of Technogym S.p.A. Italy)'
PAUL_G_CASSELL = 'Paul G. Cassell'
RUDY_GIULIANI = 'Rudy Giuliani'
SERGEY_BELYAKOV = 'Sergey Belyakov'
TULSI_GABBARD = 'Tulsi Gabbard'
VIRGINIA_GIUFFRE = 'Virginia Giuffre'

# Organizations
ATT_COURT_APPEARANCE_TEAM = 'AT&T Court Appearance Team'
BOFA = 'BofA'
BOFA_MERRILL = f'{BOFA} / Merrill Lynch'
BUREAU_OF_PRISONS = 'Bureau of Prisons'
CNN = 'CNN'
CRYPTO_PR_LAB = 'Crypto PR Lab'
DEUTSCHE_BANK = 'Deutsche Bank'
ELECTRON_CAPITAL_PARTNERS = 'Electron Capital Partners'
EPSTEIN_FOUNDATION = 'Jeffrey Epstein VI Foundation'
FBI = 'FBI'
GOLDMAN_SACHS = 'Goldman Sachs'
GOLDMAN_INVESTMENT_MGMT = f'{GOLDMAN_SACHS} Investment Management Division'
GOOGLE_PLUS = 'Google Plus'
HARVARD = 'Harvard'
INSIGHTS_POD = f"InsightsPod"  # Zubair bots
JP_MORGAN = 'JP Morgan'
KYARA_INVESTMENTS = 'Kyara Investments'
MIT_MEDIA_LAB = 'MIT Media Lab'
NEXT_MANAGEMENT = 'Next Management LLC'
OFFICE_OF_THE_DEPUTY_ATTORNEY_GENERAL = 'Office of the Deputy Attorney General'
OSBORNE_LLP = f"{IAN_OSBORNE} & Partners"  # Ian Osborne's PR firm
ROTHSTEIN_ROSENFELDT_ADLER = "Rothstein Rosenfeldt Adler (Rothstein was Roger Stone's partner)"  # and a crook
TRUMP_ORG = 'Trump Organization'
UBS = 'UBS'
USANYS = 'USANYS'
VALAR_VENTURES = 'Valar Ventures'

# First and last names that should be made part of a highlighting regex for emailers
NAMES_TO_NOT_HIGHLIGHT = """
    adam al alain alan alison alfredo allen alex alexander amanda andres andrew anthony audrey
    back bard barrett barry bennet bernard bill black bob boris brad brenner bruce
    cameron caroline carolyn chris christian christina cohen
    dan daniel danny darren dave david debbie donald douglas
    ed edward edwards enforcement enterprise enterprises entourage epstein eric erika etienne
    faith fisher forget fred friendly frost fuller
    gates gerald george gold gordon
    haddad hanson harry hay heather henry hill hoffman howard
    ian ivan
    jack james jay jean jeff jeffrey jennifer jeremy jessica joel john jon jonathan joseph jr
    kafka kahn karl kate katherine kelly ken kevin krassner
    larry larsen laurie lawrence leon lesley linda link lisa
    mann marc marie mark martin matthew melanie michael mike miller mitchell miles morris moskowitz
    nancy nathan neal new nicole norman
    owen
    paul paula pen peter philip pierce prince
    randall rangel reid richard robert rodriguez roger rosenberg ross roth roy rubenstein rubin
    scott sean skip smith stacey stanley stern stephen steve steven stone susan
    terry the thomas tim tom tony tyler
    victor
    wade waters
    y
""".strip().split()

# Names to color white in the word counts
OTHER_NAMES = NAMES_TO_NOT_HIGHLIGHT + """
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
    rafael ray richard richardson rob robert robin ron rubin rudolph ryan
    sara sarah seligman serge sergey silverman sloman smith snowden sorkin steele stevie stewart
    ted theresa thompson tiffany timothy
    valeria
    walter warren weinstein weiss william
    zach zack
""".strip().split()


def constantize_name(name: str) -> str:
    if name == 'Andrzej Duda or entourage':
        return 'ANDRZEJ_DUDA'
    elif name == MIROSLAV_LAJCAK:
        return 'MIROSLAV_LAJCAK'
    elif name == 'Paula Heil Fisher (???)':
        return 'PAULA'

    variable_name = remove_question_marks(name)
    variable_name = variable_name.removesuffix('.').removesuffix('Jr').replace('ź', 'z').replace('ø', 'o').strip()
    variable_name = variable_name.upper().replace('-', '_').replace(' ', '_').replace('.', '')

    if variable_name not in globals():
        #print(f"  ****ERROR**** {variable_name} is not a name variable!")
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


def reverse_first_and_last_names(name: Name) -> str:
    """If there's a comma in the name in the style 'Lastname, Firstname', reverse it and remove comma."""
    if name is None or '@' in name:
        return name.lower()

    if ', ' in name:
        names = name.split(', ')
        return f"{names[1]} {names[0]}"
    else:
        return name


def reversed_name(name: str) -> str:
    """'Jeffrey Epstein' becomes 'Epstein Jeffrey'."""
    if ' ' not in name:
        return name

    return f"{extract_last_name(name)}, {extract_first_name(name)}"
