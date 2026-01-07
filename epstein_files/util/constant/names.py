from epstein_files.util.constant.strings import QUESTION_MARKS, remove_question_marks

UNKNOWN = '(unknown)'

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
BRAD_EDWARDS = 'Brad Edwards'
BRAD_KARP = 'Brad Karp'
BRAD_WECHSLER = 'Brad Wechsler'
BORIS_NIKOLIC = 'Boris Nikolic'
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
DONALD_TRUMP = 'Donald Trump'
EDUARDO_ROBLES = 'Eduardo Robles'
EDWARD_JAY_EPSTEIN = 'Edward Jay Epstein'
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
MANUELA_MARTINEZ = 'Manuela Martinez'
MARC_LEON = 'Marc Leon'
MARIANA_IDZKOWSKA = 'Mariana Idźkowska'
MARK_EPSTEIN = 'Mark Epstein'
MARK_TRAMO = 'Mark Tramo'
MARTIN_NOWAK = 'Martin Nowak'
MARTIN_WEINBERG = "Martin Weinberg"
MASHA_DROKOVA = 'Masha Drokova'
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
SHAHER_ABDULHAK_BESHER = f'Shaher Abdulhak Besher {QUESTION_MARKS}'
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
VINIT_SAHNI = 'Vinit Sahni'
ZUBAIR_KHAN = 'Zubair Khan'

# No communications but name is in the files
BILL_GATES = 'Bill Gates'
DONALD_TRUMP = 'Donald Trump'
ELON_MUSK = 'Elon Musk'
HENRY_HOLT = 'Henry Holt'  # Actually a company?
IVANKA = 'Ivanka'
JAMES_PATTERSON = 'James Patterson'
JARED_KUSHNER = 'Jared Kushner'
JULIE_K_BROWN = 'Julie K. Brown'
KARIM_SADJADPOUR = 'KARIM SADJADPOUR'.title()
MICHAEL_J_BOCCIO = 'Michael J. Boccio'
NERIO_ALESSANDRI = 'Nerio Alessandri (Founder and Chairman of Technogym S.p.A. Italy)'
PAUL_G_CASSELL = 'Paul G. Cassell'
RUDY_GIULIANI = 'Rudy Giuliani'
TULSI_GABBARD = 'Tulsi Gabbard'
VIRGINIA_GIUFFRE = 'Virginia Giuffre'

# Organizations
BOFA = 'BofA'
BOFA_MERRILL = f'{BOFA} / Merrill Lynch'
CNN = 'CNN'
DEUTSCHE_BANK = 'Deutsche Bank'
ELECTRON_CAPITAL_PARTNERS = 'Electron Capital Partners'
EPSTEIN_FOUNDATION = 'Jeffrey Epstein VI Foundation'
GOLDMAN_SACHS = 'Goldman Sachs'
GOLDMAN_INVESTMENT_MGMT = f'{GOLDMAN_SACHS} Investment Management Division'
HARVARD = 'Harvard'
INSIGHTS_POD = f"InsightsPod"  # Zubair bots
NEXT_MANAGEMENT = 'Next Management LLC'
JP_MORGAN = 'JP Morgan'
OSBORNE_LLP = f"{IAN_OSBORNE} & Partners LLP"  # Ian Osborne's PR firm
TRUMP_ORG = 'Trump Organization'
UBS = 'UBS'

# First and last names that should be made part of a highlighting regex for emailers
NAMES_TO_NOT_HIGHLIGHT: list[str] = [name.lower() for name in [
    'Al', 'Alan', 'Alfredo', 'Allen', 'Alex', 'Alexander', 'Amanda', 'Andres', 'Andrew',
    'Bard', 'Barry', 'Bill', 'Black', 'Boris', 'Brad', 'Bruce',
    'Carolyn', 'Chris', 'Christina',
    'Dan', 'Daniel', 'Danny', 'Darren', 'Dave', 'David',
    'Ed', 'Edward', 'Edwards', 'Epstein', 'Eric', 'Erika', 'Etienne',
    'Faith', 'Fred', 'Friendly', 'Frost', 'Fuller',
    'George',
    'Heather', 'Henry', 'Hill', 'Hoffman',
    'Ian',
    'Jack', 'James', 'Jay', 'Jean', 'Jeff', 'Jeffrey', 'Jennifer', 'Jeremy', 'jessica', 'Joel', 'John', 'Jon', 'Jonathan', 'Joseph', 'Jr',
    'Kahn', 'Katherine', 'Kelly', 'Ken', 'Kevin',
    'Larry', 'Leon', 'Lesley', 'Linda', 'Link', 'Lisa',
    'Mann', 'Marc', 'Marie', 'Mark', 'Martin', 'Melanie', 'Michael', 'Mike', 'Miller', 'Mitchell', 'Miles', 'Morris', 'Moskowitz',
    'Nancy', 'Neal', 'New',
    'Paul', 'Paula', 'Pen', 'Peter', 'Philip', 'Prince',
    'Randall', 'Reid', 'Richard', 'Robert', 'Rodriguez', 'Roger', 'Rosenberg', 'Ross', 'Roth', 'Rubin',
    'Scott', 'Sean', 'Stanley', 'Stern', 'Stephen', 'Steve', 'Steven', 'Stone', 'Susan',
    'The', 'Thomas', 'Tim', 'Tom', 'Tyler',
    'Victor',
    'Wade',
    "Y",
]]

# Names to color white in the word counts
OTHER_NAMES = NAMES_TO_NOT_HIGHLIGHT + """
    aaron albert alberto alec alexandra alice anderson andre ann anna anne ariana arthur
    baldwin barack ben benjamin berger bert binant bob bonner boyden bradley brady branson bright bruno bryant burton
    chapman charles charlie christopher clint cohen colin collins conway
    danny davis dean debra deborah dennis diana diane diaz dickinson dixon dominique don dylan
    edmond elizabeth emily entwistle erik evelyn
    ferguson flachsbart francis franco frank frost
    gardner gary geoff geoffrey gilbert gloria goldberg gonzalez gould graham greene guarino gwyneth
    hancock harold harrison harry hay helen hill hirsch hofstadter horowitz hussein
    ian isaac isaacson
    james jamie jane janet jason jen jim joe johnson jones josh julie justin
    karl kate kathy kelly kim kruger kyle
    laurie lawrence leo leonard lenny leslie lieberman louis lynch lynn
    marcus marianne matt matthew melissa michele michelle moore moscowitz
    nancy nicole nussbaum
    owen
    paulson philippe
    rafael ray richard richardson rob robin ron rubin rudolph ryan
    sara sarah sean seligman serge sergey silverman sloman smith snowden sorkin steele stevie stewart
    ted theresa thompson tiffany timothy tony
    valeria
    walter warren weinstein weiss william
    zach zack
""".strip().split()


def constantize_name(name: str) -> str:
    if name == 'Andrzej Duda or entourage':
        return 'ANDRZEJ_DUDA'

    variable_name = remove_question_marks(name)
    variable_name = variable_name.removesuffix('.').removesuffix('Jr').replace('ź', 'z').replace('ø', 'o').strip()
    variable_name = variable_name.upper().replace('-', '_').replace(' ', '_').replace('.', '')

    if variable_name not in globals():
        #print(f"  ****ERROR**** {variable_name} is not a name variable!")
        return f"'{name}'"
    else:
        return variable_name
