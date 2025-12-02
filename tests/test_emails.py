from epstein_files.documents.email import Email
from epstein_files.util.data import dict_sets_to_lists

EMAIL_AUTHOR_COUNTS = {
    "(unknown)": 112,
    "ACT for America": 0,
    "Abi Schwinck": 1,
    "Al Seckel": 7,
    "Alain Forget": 3,
    "Alan Dershowitz": 5,
    "Alan Rogers": 0,
    "Alan S Halperin": 1,
    "Alex Yablon": 1,
    "Alireza Ittihadieh": 8,
    "Allen West": 0,
    "Amanda Ens": 8,
    "Anas Alrasheed": 7,
    "Andres Serrano": 3,
    "Andrew Friendly": 0,
    "Anil Ambani": 2,
    "Ann Marie Villafana": 1,
    "Anne Boyles": 1,
    "Anthony Barrett": 0,
    "Ariane de Rothschild": 4,
    "Aziza Alahmadi": 2,
    "BS Stern": 0,
    "Barbro C. Ehnbom": 11,
    "Barnaby Marsh": 1,
    "Barry J. Cohen": 5,
    "Barry Josephson": 2,
    "Bennet Greenwald": 0,
    "Bennet Moskowitz": 2,
    "Bennett Schmidt": 0,
    "Bill Gates": 0,
    "Bill Siegel": 5,
    "Bob Crowe": 2,
    "Boris Nikolic": 29,
    "Brad Edwards": 1,
    "Brad Karp": 5,
    "Brad Wechsler": 0,
    "Bruce Moskowitz": 6,
    "Caroline Lang": 4,
    "Carolyn Rangel": 1,
    "Cecile de Jongh": 2,
    "Cecilia Steen": 1,
    "Charlotte Abrams": 0,
    "Cheryl Kleen": 0,
    "Christina Galbraith": 5,
    "Connie Zaguirre": 0,
    "Dan Fleuette": 0,
    "Dangene and Jennie Enterprise": 5,
    "Daniel Sabba": 3,
    "Daniel Siad": 2,
    "Danny Frost": 1,
    "Danny Goldberg": 0,
    "Darren Indyke": 49,
    "Dave Hope": 1,
    "David Blaine": 0,
    "David Fiszel": 2,
    "David Grosof": 1,
    "David Haig": 1,
    "David Mitchell": 1,
    "David Schoen": 11,
    "David Stern": 7,
    "Debbie Fein": 0,
    "Deepak Chopra": 18,
    "Diane Ziman": 1,
    "Donald Rubin": 1,
    "Ed Boyden": 0,
    "Eduardo Robles": 1,
    "Edward Epstein": 2,
    "Edward Rod Larsen": 2,
    "Ehud Barak": 13,
    "Eric Roth": 5,
    "Erika Kellerhals": 3,
    "Etienne Binant": 1,
    "Eva Dubin": 2,
    "Fabrice Aidan": 1,
    "Faith Kates": 17,
    "Forrest Miller": 0,
    "Francis Derby": 0,
    "Fred Haddad": 3,
    "Gary Gross": 0,
    "George Krassner": 0,
    "Gerald Barton": 2,
    "Ghislaine Maxwell": 15,
    "Gianni Serazzi": 2,
    "Gino Yu": 3,
    "Glenn Dubin": 3,
    "Gordon Getty": 0,
    "Grant J. Smith": 0,
    "Grant Seeger": 0,
    "Gwendolyn Beck": 6,
    "Harry Fisch": 1,
    "Heather Mann": 2,
    "Henry Holt": 1,
    "Henry Hortenstine": 0,
    "Herb Goodman": 0,
    "How To Academy": 3,
    "Ian Osborne": 2,
    "Intelligence Squared": 4,
    "Jabor Y": 3,
    "Jack Goldberger": 4,
    "Jack Lang": 3,
    "Jackie Perczek": 0,
    "James Ramsey": 0,
    "Janet Kafka": 0,
    "Januiz Banasiak": 0,
    "Jay Lefkowitz": 7,
    "Jean Huguen": 1,
    "Jean Luc Brunel": 3,
    "Jeff Fuller": 0,
    "Jeffrey Epstein": 704,
    "Jennifer Jacquet": 1,
    "Jeremy Rubin": 3,
    "Jes Staley": 2,
    "Jessica Cadwell": 7,
    "Jide Zeitlin": 3,
    "Joel": 0,
    "Joel Dunn": 0,
    "John Brockman": 3,
    "John Page": 2,
    "John Zouzelka": 0,
    "Johnny el Hachem": 1,
    "Joi Ito": 25,
    "Jojo Fontanilla": 0,
    "Jokeland": 2,
    "Jonathan Farkas": 24,
    "Joscha Bach": 3,
    "Joseph Vinciguerra": 0,
    "Joshua Cooper Ramo": 1,
    "Juleanna Glover": 1,
    "Katherine Keating": 2,
    "Kathryn Ruemmler": 82,
    "Kelly Friendly": 4,
    "Ken Jenne": 1,
    "Ken Starr": 5,
    "Kenneth E. Mapp": 0,
    "Kevin Bright": 0,
    "Kirk Blouin": 2,
    "Landon Thomas Jr": 72,
    "Larry Cohen": 0,
    "Larry Summers": 48,
    "Laurie Cameron": 1,
    "Lawrance Visoski": 42,
    "Lawrence Krauss": 36,
    "Leah Reis-Dennis": 1,
    "Leon Black": 1,
    "Lesley Groff": 24,
    "Lilly Sanchez": 4,
    "Linda Pinto": 1,
    "Linda Stone": 13,
    "Lisa Albert": 0,
    "Lisa New": 22,
    "Lisa Randall": 2,
    "Louella Rabuyo": 0,
    "Lvjet": 4,
    "Lyn Fontanilla": 0,
    "Manuela Martinez": 2,
    "Marc Leon": 2,
    "Marcie Brown": 0,
    "Mariana Idźkowska": 0,
    "Mark Albert": 0,
    "Mark Epstein": 5,
    "Mark Green": 1,
    "Mark Lloyd": 1,
    "Mark Tramo": 1,
    "Marshall Funk": 0,
    "Martin Nowak": 1,
    "Martin Weinberg": 21,
    "Masha Drokova": 2,
    "Matthew Hiltzik": 2,
    "Matthew Schafer": 0,
    "Melanie Spinella": 1,
    "Melanie Walker": 3,
    "Merwin Dela Cruz": 1,
    "Michael Buchholtz": 0,
    "Michael Horowitz": 0,
    "Michael J. Pike": 0,
    "Michael Miller": 4,
    "Michael Sanka": 1,
    "Michael Simmons": 0,
    "Michael Sitrick": 0,
    "Michael Wolff": 84,
    "Miroslav Lajčák": 1,
    "Mitchell Bard": 4,
    "Mohamed Waheed Hassan": 2,
    "Mortimer Zuckerman": 0,
    "Moshe Hoffman": 1,
    "Nadia Marcinko": 8,
    "Nancy Cain": 0,
    "Nancy Dahl": 0,
    "Nancy Portland": 0,
    "Nate McClain": 0,
    "Nate White": 0,
    "Neal Kassell": 2,
    "Neil Anderson": 0,
    "Nicholas Ribis": 53,
    "Nili Priell Barak": 0,
    "Noam Chomsky": 4,
    "Norman D. Rau": 2,
    "Norman Finkelstein": 0,
    "Oliver Goodenough": 0,
    "Olivier Colom": 1,
    "Owen Blicksilver": 0,
    "Paul Barrett": 4,
    "Paul Krassner": 29,
    "Paul Morris": 5,
    "Paul Prosperi": 3,
    "Paula": 2,
    "Peggy Siegal": 8,
    "Peter Aldhous": 0,
    "Peter Attia": 2,
    "Peter Green": 1,
    "Peter Mandelson": 4,
    "Peter Thiel": 1,
    "Peter Thomas Roth": 2,
    "Philip Kafka": 1,
    "Police Code Enforcement": 0,
    "Prince Andrew": 2,
    "Purevsuren Lundeg": 1,
    "R. Couri Hay": 1,
    "Raafat Alsabbagh": 0,
    "Rafael Bardaji": 0,
    "Ramsey Elkholy": 1,
    "Reid Hoffman": 1,
    "Reid Weingarten": 72,
    "Renata Bolotova": 1,
    "Richard Barnnet": 0,
    "Richard Joshi": 0,
    "Richard Kahn": 117,
    "Richard Merkin": 3,
    "Rita Hortenstine": 0,
    "Robert D. Critton Jr.": 0,
    "Robert Gold": 0,
    "Robert Lawrence Kuhn": 26,
    "Robert Trivers": 16,
    "Roger Schank": 0,
    "Ross Gow": 1,
    "Roy Black": 5,
    "Sam Harris": 0,
    "Sam/Walli Leff": 0,
    "Saved by Internet Explorer 11": 1,
    "Scott J. Link": 2,
    "Sean Bannon": 3,
    "Sean J. Lancaster": 1,
    "Sean T Lehane": 0,
    "Shaher Abdulhak Besher (?)": 2,
    "Skip Rimer": 1,
    "Soon-Yi Previn": 10,
    "Stanley Rosenberg": 3,
    "Stephanie": 4,
    "Stephen Alexander": 1,
    "Stephen Hanson": 5,
    "Stephen Rubin": 0,
    "Steve Bannon": 44,
    "Steven Elkman": 1,
    "Steven Gaydos": 0,
    "Steven Pfeiffer": 2,
    "Steven Sinofsky": 2,
    "Steven Victor MD": 1,
    "Sultan Ahmed Bin Sulayem": 15,
    "Susan Edelman": 0,
    "Taal Safdie": 0,
    "Terje Rød-Larsen": 2,
    "Terry Kafka": 8,
    "Thanu Boonyawatana": 0,
    "Thorbjørn Jagland": 6,
    "Tim Kane": 0,
    "Tim Zagat": 1,
    "Tom": 0,
    "Tom Barrack": 1,
    "Tom Pritzker": 6,
    "Tonja Haddad Coleman": 8,
    "Travis Pangburn": 0,
    "Tyler Shears": 6,
    "Uri Fouzailov": 0,
    "Vahe Stepanian": 0,
    "Val Sherman": 0,
    "Valeria Chomsky": 2,
    "Vincenzo Lozzo": 1,
    "Vinit Sahni": 3,
    "Vladimir Yudashkin": 1,
    "Warren Eisenstein": 0,
    "Zubair Khan": 9,
    "asmallworld@travel.asmallworld.net": 4,
    "david.brown@thetimes.co.uk": 0,
    "digest-noreply@quora.com": 5,
    "drsra": 1,
    "editorialstaff@flipboard.com": 13,
    "io-anne.pugh@bbc.co.uk": 0,
    "jeff@mc2mm.com": 0,
    "lorraine@mc2mm.com": 1,
    "martin.robinson@mailonline.co.uk": 0,
    "middle.east.update@hotmail.com": 1,
    "nick.alwav@bbc.co.uk": 0,
    "nick.sommerlad@mirror.co.uk": 0,
    "p.peachev@independent.co.uk": 0,
    "pink@mc2mm.com": 0,
    "us.gio@jpmorgan.com": 13
}

EMAIL_RECIPIENT_COUNTS = {
    "(unknown)": 80,
    "ACT for America": 1,
    "Abi Schwinck": 0,
    "Al Seckel": 0,
    "Alain Forget": 0,
    "Alan Dershowitz": 15,
    "Alan Rogers": 1,
    "Alan S Halperin": 0,
    "Alex Yablon": 0,
    "Alireza Ittihadieh": 2,
    "Allen West": 2,
    "Amanda Ens": 1,
    "Anas Alrasheed": 5,
    "Andres Serrano": 0,
    "Andrew Friendly": 1,
    "Anil Ambani": 1,
    "Ann Marie Villafana": 3,
    "Anne Boyles": 0,
    "Anthony Barrett": 1,
    "Ariane de Rothschild": 3,
    "Aziza Alahmadi": 0,
    "BS Stern": 1,
    "Barbro C. Ehnbom": 0,
    "Barnaby Marsh": 2,
    "Barry J. Cohen": 0,
    "Barry Josephson": 0,
    "Bennet Greenwald": 1,
    "Bennet Moskowitz": 2,
    "Bennett Schmidt": 1,
    "Bill Gates": 2,
    "Bill Siegel": 1,
    "Bob Crowe": 0,
    "Boris Nikolic": 17,
    "Brad Edwards": 0,
    "Brad Karp": 5,
    "Brad Wechsler": 1,
    "Bruce Moskowitz": 0,
    "Caroline Lang": 2,
    "Carolyn Rangel": 0,
    "Cecile de Jongh": 2,
    "Cecilia Steen": 0,
    "Charlotte Abrams": 1,
    "Cheryl Kleen": 1,
    "Christina Galbraith": 6,
    "Connie Zaguirre": 1,
    "Dan Fleuette": 1,
    "Dangene and Jennie Enterprise": 0,
    "Daniel Sabba": 0,
    "Daniel Siad": 2,
    "Danny Frost": 0,
    "Danny Goldberg": 2,
    "Darren Indyke": 56,
    "Dave Hope": 0,
    "David Blaine": 1,
    "David Fiszel": 0,
    "David Grosof": 6,
    "David Haig": 2,
    "David Mitchell": 0,
    "David Schoen": 3,
    "David Stern": 1,
    "Debbie Fein": 8,
    "Deepak Chopra": 1,
    "Diane Ziman": 1,
    "Donald Rubin": 0,
    "Ed Boyden": 1,
    "Eduardo Robles": 0,
    "Edward Epstein": 1,
    "Edward Rod Larsen": 0,
    "Ehud Barak": 3,
    "Eric Roth": 2,
    "Erika Kellerhals": 2,
    "Etienne Binant": 1,
    "Eva Dubin": 0,
    "Fabrice Aidan": 0,
    "Faith Kates": 5,
    "Forrest Miller": 1,
    "Francis Derby": 1,
    "Fred Haddad": 4,
    "Gary Gross": 1,
    "George Krassner": 2,
    "Gerald Barton": 1,
    "Ghislaine Maxwell": 8,
    "Gianni Serazzi": 1,
    "Gino Yu": 0,
    "Glenn Dubin": 1,
    "Gordon Getty": 2,
    "Grant J. Smith": 1,
    "Grant Seeger": 1,
    "Gwendolyn Beck": 0,
    "Harry Fisch": 1,
    "Heather Mann": 0,
    "Henry Holt": 0,
    "Henry Hortenstine": 1,
    "Herb Goodman": 1,
    "How To Academy": 0,
    "Ian Osborne": 0,
    "Intelligence Squared": 0,
    "Jabor Y": 7,
    "Jack Goldberger": 10,
    "Jack Lang": 3,
    "Jackie Perczek": 4,
    "James Ramsey": 1,
    "Janet Kafka": 1,
    "Januiz Banasiak": 1,
    "Jay Lefkowitz": 4,
    "Jean Huguen": 1,
    "Jean Luc Brunel": 9,
    "Jeff Fuller": 1,
    "Jeffrey Epstein": 1536,
    "Jennifer Jacquet": 0,
    "Jeremy Rubin": 0,
    "Jes Staley": 7,
    "Jessica Cadwell": 5,
    "Jide Zeitlin": 0,
    "Joel": 2,
    "Joel Dunn": 1,
    "John Brockman": 0,
    "John Page": 2,
    "John Zouzelka": 1,
    "Johnny el Hachem": 0,
    "Joi Ito": 11,
    "Jojo Fontanilla": 1,
    "Jokeland": 0,
    "Jonathan Farkas": 9,
    "Joscha Bach": 4,
    "Joseph Vinciguerra": 1,
    "Joshua Cooper Ramo": 1,
    "Juleanna Glover": 0,
    "Katherine Keating": 3,
    "Kathryn Ruemmler": 57,
    "Kelly Friendly": 0,
    "Ken Jenne": 0,
    "Ken Starr": 10,
    "Kenneth E. Mapp": 1,
    "Kevin Bright": 1,
    "Kirk Blouin": 0,
    "Landon Thomas Jr": 52,
    "Larry Cohen": 1,
    "Larry Summers": 42,
    "Laurie Cameron": 0,
    "Lawrance Visoski": 11,
    "Lawrence Krauss": 13,
    "Leah Reis-Dennis": 1,
    "Leon Black": 4,
    "Lesley Groff": 22,
    "Lilly Sanchez": 3,
    "Linda Pinto": 0,
    "Linda Stone": 2,
    "Lisa Albert": 1,
    "Lisa New": 14,
    "Lisa Randall": 0,
    "Louella Rabuyo": 1,
    "Lvjet": 0,
    "Lyn Fontanilla": 1,
    "Manuela Martinez": 0,
    "Marc Leon": 1,
    "Marcie Brown": 1,
    "Mariana Idźkowska": 2,
    "Mark Albert": 1,
    "Mark Epstein": 3,
    "Mark Green": 0,
    "Mark Lloyd": 0,
    "Mark Tramo": 0,
    "Marshall Funk": 1,
    "Martin Nowak": 1,
    "Martin Weinberg": 28,
    "Masha Drokova": 2,
    "Matthew Hiltzik": 1,
    "Matthew Schafer": 1,
    "Melanie Spinella": 14,
    "Melanie Walker": 2,
    "Merwin Dela Cruz": 0,
    "Michael Buchholtz": 2,
    "Michael Horowitz": 1,
    "Michael J. Pike": 2,
    "Michael Miller": 0,
    "Michael Sanka": 0,
    "Michael Simmons": 1,
    "Michael Sitrick": 4,
    "Michael Wolff": 69,
    "Miroslav Lajčák": 1,
    "Mitchell Bard": 0,
    "Mohamed Waheed Hassan": 2,
    "Mortimer Zuckerman": 3,
    "Moshe Hoffman": 1,
    "Nadia Marcinko": 1,
    "Nancy Cain": 3,
    "Nancy Dahl": 2,
    "Nancy Portland": 2,
    "Nate McClain": 1,
    "Nate White": 1,
    "Neal Kassell": 1,
    "Neil Anderson": 1,
    "Nicholas Ribis": 10,
    "Nili Priell Barak": 1,
    "Noam Chomsky": 2,
    "Norman D. Rau": 0,
    "Norman Finkelstein": 1,
    "Oliver Goodenough": 1,
    "Olivier Colom": 0,
    "Owen Blicksilver": 1,
    "Paul Barrett": 1,
    "Paul Krassner": 7,
    "Paul Morris": 1,
    "Paul Prosperi": 0,
    "Paula": 4,
    "Peggy Siegal": 18,
    "Peter Aldhous": 2,
    "Peter Attia": 0,
    "Peter Green": 0,
    "Peter Mandelson": 4,
    "Peter Thiel": 5,
    "Peter Thomas Roth": 0,
    "Philip Kafka": 3,
    "Police Code Enforcement": 2,
    "Prince Andrew": 2,
    "Purevsuren Lundeg": 0,
    "R. Couri Hay": 0,
    "Raafat Alsabbagh": 2,
    "Rafael Bardaji": 1,
    "Ramsey Elkholy": 0,
    "Reid Hoffman": 2,
    "Reid Weingarten": 34,
    "Renata Bolotova": 0,
    "Richard Barnnet": 1,
    "Richard Joshi": 1,
    "Richard Kahn": 30,
    "Richard Merkin": 1,
    "Rita Hortenstine": 1,
    "Robert D. Critton Jr.": 8,
    "Robert Gold": 1,
    "Robert Lawrence Kuhn": 2,
    "Robert Trivers": 3,
    "Roger Schank": 2,
    "Ross Gow": 0,
    "Roy Black": 4,
    "Sam Harris": 1,
    "Sam/Walli Leff": 1,
    "Saved by Internet Explorer 11": 0,
    "Scott J. Link": 1,
    "Sean Bannon": 1,
    "Sean J. Lancaster": 0,
    "Sean T Lehane": 1,
    "Shaher Abdulhak Besher (?)": 0,
    "Skip Rimer": 0,
    "Soon-Yi Previn": 3,
    "Stanley Rosenberg": 1,
    "Stephanie": 0,
    "Stephen Alexander": 0,
    "Stephen Hanson": 3,
    "Stephen Rubin": 1,
    "Steve Bannon": 31,
    "Steven Elkman": 0,
    "Steven Gaydos": 2,
    "Steven Pfeiffer": 2,
    "Steven Sinofsky": 1,
    "Steven Victor MD": 0,
    "Sultan Ahmed Bin Sulayem": 14,
    "Susan Edelman": 1,
    "Taal Safdie": 1,
    "Terje Rød-Larsen": 0,
    "Terry Kafka": 1,
    "Thanu Boonyawatana": 1,
    "Thorbjørn Jagland": 6,
    "Tim Kane": 1,
    "Tim Zagat": 1,
    "Tom": 2,
    "Tom Barrack": 2,
    "Tom Pritzker": 9,
    "Tonja Haddad Coleman": 6,
    "Travis Pangburn": 1,
    "Tyler Shears": 1,
    "Uri Fouzailov": 1,
    "Vahe Stepanian": 1,
    "Val Sherman": 1,
    "Valeria Chomsky": 1,
    "Vincenzo Lozzo": 0,
    "Vinit Sahni": 1,
    "Vladimir Yudashkin": 0,
    "Warren Eisenstein": 2,
    "Zubair Khan": 1,
    "asmallworld@travel.asmallworld.net": 0,
    "david.brown@thetimes.co.uk": 1,
    "digest-noreply@quora.com": 0,
    "drsra": 0,
    "editorialstaff@flipboard.com": 0,
    "io-anne.pugh@bbc.co.uk": 1,
    "jeff@mc2mm.com": 1,
    "lorraine@mc2mm.com": 0,
    "martin.robinson@mailonline.co.uk": 1,
    "middle.east.update@hotmail.com": 0,
    "nick.alwav@bbc.co.uk": 1,
    "nick.sommerlad@mirror.co.uk": 1,
    "p.peachev@independent.co.uk": 1,
    "pink@mc2mm.com": 2,
    "us.gio@jpmorgan.com": 0
}


DEVICE_SIGNATURE_TO_AUTHORS = {
    "Sent from AOL Mobile Mail": [
        "David Schoen"
    ],
    "Sent from President's iPad": [
        "Mohamed Waheed Hassan"
    ],
    "Sent from ProtonMail": [
        "Jeffrey Epstein",
        "Sean Bannon"
    ],
    "Sent from Soon-Yi's iPhone": [
        "Soon-Yi Previn"
    ],
    "Sent from Steve Hanson's Blackberry": [
        "Stephen Hanson"
    ],
    "Sent from Yahoo Mail for iPhone": [
        "Merwin Dela Cruz"
    ],
    "Sent from my BlackBerry - the most secure mobile device": [
        "Michael Miller"
    ],
    "Sent from my BlackBerry 10 smartphone.": [
        "Reid Weingarten",
        "Nicholas Ribis"
    ],
    "Sent from my BlackBerry® wireless device": [
        "Landon Thomas Jr",
        "Ross Gow"
    ],
    "Sent from my Iphone": [
        "Vincenzo Lozzo"
    ],
    "Sent from my Samsung JackTM, a Windows Mobile® smartphone from AT&T": [
        "Boris Nikolic"
    ],
    "Sent from my Verizon 4G LTE Droid": [
        "Darren Indyke"
    ],
    "Sent from my Verizon Wireless BlackBerry": [
        "Lisa Randall",
        "Alan Dershowitz"
    ],
    "Sent from my Verizon, Samsung Galaxy smartphone": [
        "Reid Weingarten"
    ],
    "Sent from my Windows 10 phone": [
        "(unknown)"
    ],
    "Sent from my Windows Phone": [
        "Boris Nikolic",
        "Gwendolyn Beck"
    ],
    "Sent from my iPad": [
        "Peggy Siegal",
        "Mark Lloyd",
        "Larry Summers",
        "Cecilia Steen",
        "Ehud Barak",
        "Stephen Hanson",
        "Richard Merkin",
        "Neal Kassell",
        "Kathryn Ruemmler",
        "Lawrance Visoski",
        "Glenn Dubin",
        "(unknown)",
        "Bruce Moskowitz",
        "Joi Ito"
    ],
    "Sent from my iPhone": [
        "Larry Summers",
        "Terry Kafka",
        "Jack Goldberger",
        "Gino Yu",
        "Martin Weinberg",
        "Jonathan Farkas",
        "Lawrance Visoski",
        "Terje Rød-Larsen",
        "Joi Ito",
        "Neal Kassell",
        "Faith Kates",
        "Darren Indyke",
        "(unknown)",
        "Sean Bannon",
        "Alan Dershowitz",
        "David Schoen",
        "Ghislaine Maxwell",
        "Erika Kellerhals",
        "Aziza Alahmadi",
        "Harry Fisch",
        "Tyler Shears",
        "Landon Thomas Jr",
        "Ehud Barak",
        "Eva Dubin",
        "Stanley Rosenberg",
        "Kathryn Ruemmler",
        "Jes Staley",
        "Richard Kahn",
        "Lisa New",
        "Lesley Groff",
        "Kelly Friendly",
        "Bob Crowe",
        "Tom Barrack",
        "Bruce Moskowitz",
        "Jeffrey Epstein",
        "Stephen Hanson",
        "Richard Merkin",
        "Lawrence Krauss",
        "Sultan Ahmed Bin Sulayem",
        "Robert Lawrence Kuhn",
        "Glenn Dubin",
        "Mohamed Waheed Hassan",
        "Johnny el Hachem",
        "Heather Mann",
        "Anas Alrasheed",
        "Matthew Hiltzik",
        "Ken Starr",
        "Nicholas Ribis"
    ],
    "Sent from my iPhone and misspellings courtesy of iPhone.": [
        "Cecile de Jongh"
    ],
    "Sent via BlackBerry by AT&T": [
        "Terry Kafka",
        "Steve Bannon",
        "Peggy Siegal",
        "(unknown)"
    ],
    "Sent via BlackBerry from T-Mobile": [
        "Paula"
    ],
    "Sent via tin can and string.": [
        "Mark Epstein"
    ],
    "Sorry for all the typos .Sent from my iPhone": [
        "Jeffrey Epstein"
    ]
}

AUTHORS_TO_DEVICE_SIGNATURES = {
    "(unknown)": [
        "Sent via BlackBerry by AT&T",
        "Sent from my Windows 10 phone",
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Alan Dershowitz": [
        "Sent from my iPhone",
        "Sent from my Verizon Wireless BlackBerry"
    ],
    "Anas Alrasheed": [
        "Sent from my iPhone"
    ],
    "Aziza Alahmadi": [
        "Sent from my iPhone"
    ],
    "Bob Crowe": [
        "Sent from my iPhone"
    ],
    "Boris Nikolic": [
        "Sent from my Samsung JackTM, a Windows Mobile® smartphone from AT&T",
        "Sent from my Windows Phone"
    ],
    "Bruce Moskowitz": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Cecile de Jongh": [
        "Sent from my iPhone and misspellings courtesy of iPhone."
    ],
    "Cecilia Steen": [
        "Sent from my iPad"
    ],
    "Darren Indyke": [
        "Sent from my iPhone",
        "Sent from my Verizon 4G LTE Droid"
    ],
    "David Schoen": [
        "Sent from my iPhone",
        "Sent from AOL Mobile Mail"
    ],
    "Ehud Barak": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Erika Kellerhals": [
        "Sent from my iPhone"
    ],
    "Eva Dubin": [
        "Sent from my iPhone"
    ],
    "Faith Kates": [
        "Sent from my iPhone"
    ],
    "Ghislaine Maxwell": [
        "Sent from my iPhone"
    ],
    "Gino Yu": [
        "Sent from my iPhone"
    ],
    "Glenn Dubin": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Gwendolyn Beck": [
        "Sent from my Windows Phone"
    ],
    "Harry Fisch": [
        "Sent from my iPhone"
    ],
    "Heather Mann": [
        "Sent from my iPhone"
    ],
    "Jack Goldberger": [
        "Sent from my iPhone"
    ],
    "Jeffrey Epstein": [
        "Sent from ProtonMail",
        "Sent from my iPhone",
        "Sorry for all the typos .Sent from my iPhone"
    ],
    "Jes Staley": [
        "Sent from my iPhone"
    ],
    "Johnny el Hachem": [
        "Sent from my iPhone"
    ],
    "Joi Ito": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Jonathan Farkas": [
        "Sent from my iPhone"
    ],
    "Kathryn Ruemmler": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Kelly Friendly": [
        "Sent from my iPhone"
    ],
    "Ken Starr": [
        "Sent from my iPhone"
    ],
    "Landon Thomas Jr": [
        "Sent from my iPhone",
        "Sent from my BlackBerry® wireless device"
    ],
    "Larry Summers": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Lawrance Visoski": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Lawrence Krauss": [
        "Sent from my iPhone"
    ],
    "Lesley Groff": [
        "Sent from my iPhone"
    ],
    "Lisa New": [
        "Sent from my iPhone"
    ],
    "Lisa Randall": [
        "Sent from my Verizon Wireless BlackBerry"
    ],
    "Mark Epstein": [
        "Sent via tin can and string."
    ],
    "Mark Lloyd": [
        "Sent from my iPad"
    ],
    "Martin Weinberg": [
        "Sent from my iPhone"
    ],
    "Matthew Hiltzik": [
        "Sent from my iPhone"
    ],
    "Merwin Dela Cruz": [
        "Sent from Yahoo Mail for iPhone"
    ],
    "Michael Miller": [
        "Sent from my BlackBerry - the most secure mobile device"
    ],
    "Mohamed Waheed Hassan": [
        "Sent from President's iPad",
        "Sent from my iPhone"
    ],
    "Neal Kassell": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Nicholas Ribis": [
        "Sent from my BlackBerry 10 smartphone.",
        "Sent from my iPhone"
    ],
    "Paula": [
        "Sent via BlackBerry from T-Mobile"
    ],
    "Peggy Siegal": [
        "Sent via BlackBerry by AT&T",
        "Sent from my iPad"
    ],
    "Reid Weingarten": [
        "Sent from my BlackBerry 10 smartphone.",
        "Sent from my Verizon, Samsung Galaxy smartphone"
    ],
    "Richard Kahn": [
        "Sent from my iPhone"
    ],
    "Richard Merkin": [
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Robert Lawrence Kuhn": [
        "Sent from my iPhone"
    ],
    "Ross Gow": [
        "Sent from my BlackBerry® wireless device"
    ],
    "Sean Bannon": [
        "Sent from ProtonMail",
        "Sent from my iPhone"
    ],
    "Soon-Yi Previn": [
        "Sent from Soon-Yi's iPhone"
    ],
    "Stanley Rosenberg": [
        "Sent from my iPhone"
    ],
    "Stephen Hanson": [
        "Sent from Steve Hanson's Blackberry",
        "Sent from my iPad",
        "Sent from my iPhone"
    ],
    "Steve Bannon": [
        "Sent via BlackBerry by AT&T"
    ],
    "Sultan Ahmed Bin Sulayem": [
        "Sent from my iPhone"
    ],
    "Terje Rød-Larsen": [
        "Sent from my iPhone"
    ],
    "Terry Kafka": [
        "Sent via BlackBerry by AT&T",
        "Sent from my iPhone"
    ],
    "Tom Barrack": [
        "Sent from my iPhone"
    ],
    "Tyler Shears": [
        "Sent from my iPhone"
    ],
    "Vincenzo Lozzo": [
        "Sent from my Iphone"
    ]
}

SIGNATURE_SUBSTITUTION_COUNTS = {
    "(unknown)": 2,
    "Danny Frost": 16,
    "Darren Indyke": 52,
    "David Ingram": 11,
    "Deepak Chopra": 21,
    "Jeffrey Epstein": 3363,
    "Jessica Cadwell": 43,
    "Lawrence Krauss": 82,
    "Martin Weinberg": 23,
    "Paul Barrett": 19,
    "Peter Mandelson": 10,
    "Richard Kahn": 122,
    "Susan Edelman": 18,
    "Terry Kafka": 10,
    "Tonja Haddad Coleman": 16
}


def test_email_counts(epstein_files):
    author_counts = {k: v for k, v in EMAIL_AUTHOR_COUNTS.items() if v > 0}
    assert author_counts == epstein_files.email_author_counts
    recipient_counts = {k: v for k, v in EMAIL_RECIPIENT_COUNTS.items() if v > 0}
    assert recipient_counts == epstein_files.email_recipient_counts


def test_signatures(epstein_files):
    assert AUTHORS_TO_DEVICE_SIGNATURES == dict_sets_to_lists(epstein_files.email_author_device_signatures)
    assert DEVICE_SIGNATURE_TO_AUTHORS == dict_sets_to_lists(epstein_files.email_sent_from_devices)
    assert SIGNATURE_SUBSTITUTION_COUNTS == Email.signature_substitution_counts
