import re

EMAIL_CODE = """
    '022187': EmailConfig(author=None, recipients=[JEFFREY_EPSTEIN]),  # bad OCR causes issues
    '032436': EmailConfig(author=ALIREZA_ITTIHADIEH),    # Signature
    '032543': EmailConfig(author=ANAS_ALRASHEED),        # Later reply 033000 has quote
    '026064': EmailConfig(author=ARIANE_DE_ROTHSCHILD),
    '026069': EmailConfig(author=ARIANE_DE_ROTHSCHILD),
    '030741': EmailConfig(author=ARIANE_DE_ROTHSCHILD),
    '026018': EmailConfig(author=ARIANE_DE_ROTHSCHILD),
    '029504': EmailConfig(author=f'Audrey/Aubrey Raimbault {QUESTION_MARKS}'),  # (based on "GMI" in signature, a company registered by "aubrey raimbault")
    '033316': EmailConfig(author=AZIZA_ALAHMADI),        # "Regards, Aziza" at bottom
    '033328': EmailConfig(author=AZIZA_ALAHMADI),        # "Regards, Aziza" at bottom
    '026659': EmailConfig(author=BARBRO_C_EHNBOM),         # Reply
    '026745': EmailConfig(author=BARBRO_C_EHNBOM),         # Signature
    '026764': EmailConfig(author=BARRY_J_COHEN),
    '031227': EmailConfig(author=BENNET_MOSKOWITZ),
    '031442': EmailConfig(author=CHRISTINA_GALBRAITH),
    '019446': EmailConfig(author=CHRISTINA_GALBRAITH),   # Not 100% but from "Christina media/PR" which fits
    '026625': EmailConfig(author=DARREN_INDYKE, actual_text='Hysterical.'),
    '026624': EmailConfig(                          # weird format (signature on top)
        author=DARREN_INDYKE,
        recipients=[JEFFREY_EPSTEIN],
        timestamp=datetime.fromisoformat('2016-10-01 16:40:00')
    ),
    '031278': EmailConfig(                          # Quoted replies are in 019109
        author=DARREN_INDYKE,
        timestamp=datetime.fromisoformat('2016-08-17 11:26:00')
    ),
    '026290': EmailConfig(author=DAVID_SCHOEN),          # Signature
    '031339': EmailConfig(author=DAVID_SCHOEN),          # Signature
    '031492': EmailConfig(author=DAVID_SCHOEN),          # Signature
    '031560': EmailConfig(author=DAVID_SCHOEN),          # Signature
    '026287': EmailConfig(author=DAVID_SCHOEN),          # Signature
    '033419': EmailConfig(author=DAVID_SCHOEN),          # Signature
    '026245': EmailConfig(author=DIANE_ZIMAN, recipients=[JEFFREY_EPSTEIN]),  # TODO: Shouldn't need to be configured
    '031460': EmailConfig(author=EDWARD_JAY_EPSTEIN),
    '030578': EmailConfig(
        id='030578',
        duplicate_of_id='030414',
        duplicate_type='redacted',
        author=FAITH_KATES,
        attribution_explanation='Same as unredacted 030414, same legal signature',
    ),
    '030634': EmailConfig(author=FAITH_KATES),           # Same as unredacted 031135, same legal signature
    '026547': EmailConfig(author=GERALD_BARTON, recipients=[JEFFREY_EPSTEIN]),  # bad OCR
    '029969': EmailConfig(author=GWENDOLYN_BECK),        # Signature
    '031120': EmailConfig(author=GWENDOLYN_BECK),        # Signature
    '029968': EmailConfig(author=GWENDOLYN_BECK),        # Signature
    '029970': EmailConfig(author=GWENDOLYN_BECK),
    '029960': EmailConfig(author=GWENDOLYN_BECK),        # Reply
    '029959': EmailConfig(author=GWENDOLYN_BECK),        # "Longevity & Aging"
    '033360': EmailConfig(author=HENRY_HOLT),            # in signature. Henry Holt is a company not a person.
    '033384': EmailConfig(author=JACK_GOLDBERGER),       # Might be Paul Prosperi?
    '026024': EmailConfig(author=JEAN_HUGUEN),           # Signature
    '021823': EmailConfig(author=JEAN_LUC_BRUNEL),       # Reply
    '022949': EmailConfig(author=JEFFREY_EPSTEIN),
    '031624': EmailConfig(author=JEFFREY_EPSTEIN),
    '031996': EmailConfig(author=JEFFREY_EPSTEIN, recipients=[CHRISTINA_GALBRAITH]),  # bounced
    '028675': EmailConfig(author=JEFFREY_EPSTEIN, recipients=[LARRY_SUMMERS]),  # Bad OCR
    '025041': EmailConfig(author=JEFFREY_EPSTEIN, recipients=[LARRY_SUMMERS]),  # Bad OCR
    '029779': EmailConfig(author=JEFFREY_EPSTEIN, recipients=[LARRY_SUMMERS], is_fwded_article=True),  # Bad OCR, WaPo article
    '029692': EmailConfig(author=JEFFREY_EPSTEIN, recipients=[LARRY_SUMMERS], is_fwded_article=True),  # Bad OCR, WaPo article
    '018726': EmailConfig(
        author=JEFFREY_EPSTEIN,                        # Strange fragment only showing what was replied to
        timestamp=datetime.fromisoformat('2018-06-08 08:36:00'),
    ),
    '032283': EmailConfig(
        author=JEFFREY_EPSTEIN,                         # Strange fragment only showing what was replied to
        timestamp=datetime.fromisoformat('2016-09-14 08:04:00'),
    ),
    '026943': EmailConfig(
        author=JEFFREY_EPSTEIN,                         # Strange fragment only showing what was replied to
        timestamp=datetime.fromisoformat('2019-05-22 05:47:00'),
    ),
    '023208': EmailConfig(
        author=JEFFREY_EPSTEIN,                         # Same as 023291
        recipients=[BRAD_WECHSLER, MELANIE_SPINELLA]
    ),
    '032214': EmailConfig(                   # Quoted reply has signature
        author=JEFFREY_EPSTEIN,
        recipients=[MIROSLAV_LAJCAK],
        actual_text='Agreed',
    ),
    '029582': EmailConfig(author=JEFFREY_EPSTEIN, recipients=[RENATA_BOLOTOVA]),  # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '030997': EmailConfig(author=JEFFREY_EPSTEIN, actual_text='call back'),
    '028770': EmailConfig(author=JEFFREY_EPSTEIN, actual_text='call me now'),
    '031826': EmailConfig(author=JEFFREY_EPSTEIN, actual_text='I have'),
    '030768': EmailConfig(author=JEFFREY_EPSTEIN, actual_text='ok'),
    '022938': EmailConfig(author=JEFFREY_EPSTEIN, actual_text='what do you suggest?'),  # TODO: this email's header rewrite sucks
    '031791': EmailConfig(author=JESSICA_CADWELL),
    '028851': EmailConfig(
        author=JOI_ITO,
        recipients=[JEFFREY_EPSTEIN],
        timestamp=datetime.fromisoformat('2014-04-27 06:00:00'),
    ),
    '028849': EmailConfig(                                # Conversation with Joi Ito
        author=JOI_ITO,
        recipients=[JEFFREY_EPSTEIN],
        timestamp=datetime.fromisoformat('2014-04-27 06:30:00')
    ),
    '016692': EmailConfig(author=JOHN_PAGE),
    '016693': EmailConfig(author=JOHN_PAGE),
    '028507': EmailConfig(author=JONATHAN_FARKAS),
    '031732': EmailConfig(author=JONATHAN_FARKAS),
    '033484': EmailConfig(author=JONATHAN_FARKAS),
    '033282': EmailConfig(author=JONATHAN_FARKAS),
    '033582': EmailConfig(author=JONATHAN_FARKAS),         # Reply
    '032389': EmailConfig(author=JONATHAN_FARKAS),         # Reply
    '033581': EmailConfig(author=JONATHAN_FARKAS),         # Reply
    '033203': EmailConfig(author=JONATHAN_FARKAS),         # Reply
    '032052': EmailConfig(author=JONATHAN_FARKAS),         # Reply
    '033490': EmailConfig(author=JONATHAN_FARKAS),         # Signature
    '032531': EmailConfig(author=JONATHAN_FARKAS),         # Signature
    '026652': EmailConfig(author=KATHRYN_RUEMMLER),        # bad OCR
    '032224': EmailConfig(author=KATHRYN_RUEMMLER, recipients=[JEFFREY_EPSTEIN]),  # Reply
    '032386': EmailConfig(author=KATHRYN_RUEMMLER),        # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '032727': EmailConfig(author=KATHRYN_RUEMMLER),        # from "Kathy" about dems, sent from iPad (not 100% confirmed)
    '030478': EmailConfig(author=LANDON_THOMAS),
    '029013': EmailConfig(author=LARRY_SUMMERS, recipients=[JEFFREY_EPSTEIN]),
    '032206': EmailConfig(author=LAWRENCE_KRAUSS),         # More of a text convo?
    '032209': EmailConfig(author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN]),  # More of a text convo?
    '032208': EmailConfig(author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN]),  # More of a text convo?
    '029196': EmailConfig(author=LAWRENCE_KRAUSS, recipients=[JEFFREY_EPSTEIN], actual_text='Talk in 40?'),  # TODO: this email's header rewrite sucks
    '028789': EmailConfig(author=LAWRANCE_VISOSKI),
    '027046': EmailConfig(author=LAWRANCE_VISOSKI),
    '033370': EmailConfig(author=LAWRANCE_VISOSKI),        # Planes discussion signed larry
    '031129': EmailConfig(author=LAWRANCE_VISOSKI),        # Planes discussion signed larry
    '033495': EmailConfig(author=LAWRANCE_VISOSKI),        # Planes discussion signed larry
    '033154': EmailConfig(author=LAWRANCE_VISOSKI),
    '033488': EmailConfig(author=LAWRANCE_VISOSKI),
    '033593': EmailConfig(author=LAWRANCE_VISOSKI),        # Signature
    '033487': EmailConfig(author=LAWRANCE_VISOSKI, recipients=[JEFFREY_EPSTEIN]),
    '029977': EmailConfig( # Planes discussion signed larry
        author=LAWRANCE_VISOSKI,
        recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, LESLEY_GROFF, RICHARD_KAHN] + FLIGHT_IN_2012_PEOPLE,
    ),
    '033309': EmailConfig(author=LINDA_STONE),             # "Co-authored with iPhone autocorrect"
    '017581': EmailConfig(author='Lisa Randall'),
    '026609': EmailConfig(author='Mark Green'),            # Actually a fwd
    '030472': EmailConfig(author=MARTIN_WEINBERG),         # Maybe. in reply
    '030235': EmailConfig(author=MELANIE_WALKER),          # In fwd
    '032343': EmailConfig(author=MELANIE_WALKER),          # In later reply 032346
    '032212': EmailConfig(author=MIROSLAV_LAJCAK),
    '022193': EmailConfig(author=NADIA_MARCINKO),
    '021814': EmailConfig(author=NADIA_MARCINKO),
    '021808': EmailConfig(author=NADIA_MARCINKO),
    '022214': EmailConfig(author=NADIA_MARCINKO),          # Reply header
    '022190': EmailConfig(author=NADIA_MARCINKO),
    '021818': EmailConfig(author=NADIA_MARCINKO),
    '022197': EmailConfig(author=NADIA_MARCINKO),
    '021811': EmailConfig(author=NADIA_MARCINKO),          # Signature and email address in the message
    '026612': EmailConfig(author=NORMAN_D_RAU, actual_text=''),  # Fwded from "to" address
    '028487': EmailConfig(author=NORMAN_D_RAU),            # Fwded from "to" address
    '024923': EmailConfig(author=PAUL_KRASSNER, recipients=KRASSNER_024923_RECIPIENTS),
    '032457': EmailConfig(author=PAUL_KRASSNER),
    '029981': EmailConfig(author=PAULA),                   # Name in reply + opera reference (Fisher now works in opera)
    '030482': EmailConfig(author=PAULA),                   # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '033157': EmailConfig(author=PAUL_PROSPERI),           # Fwded from "to" address
    '033383': EmailConfig(author=PAUL_PROSPERI),           # Reply
    '033561': EmailConfig(author=PAUL_PROSPERI),           # Fwded mail sent to Prosperi. Might be Subotnick Stuart ?
    '031694': EmailConfig(author=PEGGY_SIEGAL),
    '032219': EmailConfig(author=PEGGY_SIEGAL),            # Signed "Peggy"
    '029020': EmailConfig(author=RENATA_BOLOTOVA),         # Signature
    '029605': EmailConfig(author=RENATA_BOLOTOVA),         # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '029606': EmailConfig(author=RENATA_BOLOTOVA),         # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '029604': EmailConfig(author=RENATA_BOLOTOVA),         # Continued in 239606 etc
    '033169': EmailConfig(author=ROBERT_TRIVERS, recipients=[JEFFREY_EPSTEIN]),  # Refs paper
    '033584': EmailConfig(author=ROBERT_TRIVERS, recipients=[JEFFREY_EPSTEIN]),  # Refs paper
    '026320': EmailConfig(author='Sean Bannon'),           # From protonmail, Bannon wrote 'just sent from my protonmail' in 027067
    '029003': EmailConfig(author=SOON_YI),                 # "Sent from Soon-Yi's iPhone"
    '029005': EmailConfig(author=SOON_YI),                 # "Sent from Soon-Yi's iPhone"
    '029007': EmailConfig(author=SOON_YI),                 # "Sent from Soon-Yi's iPhone"
    '029010': EmailConfig(author=SOON_YI),                 # "Sent from Soon-Yi's iPhone"
    '032296': EmailConfig(author=SOON_YI),                 # "Sent from Soon-Yi's iPhone"
    '019109': EmailConfig(                           # Actually a fwd by Charles Michael but Hofenberg email more intersting
        author=STEVEN_HOFFENBERG,
        recipients=['Players2'],
        timestamp=datetime.fromisoformat('2016-08-11 09:36:01')
    ),
    '026620': EmailConfig(  # "Respectfully, terry"
        author=TERRY_KAFKA,
        recipients=[JEFFREY_EPSTEIN, MARK_EPSTEIN, MICHAEL_BUCHHOLTZ] + IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS,
    ),
    '028482': EmailConfig(author=TERRY_KAFKA),             # Signature
    '029992': EmailConfig(author=TERRY_KAFKA),             # Quoted reply
    '029985': EmailConfig(author=TERRY_KAFKA),             # Quoted reply in 029992
    '020666': EmailConfig(author=TERRY_KAFKA),             # Ends with 'Terry'
    '026014': EmailConfig(
        author=ZUBAIR_KHAN,                              # truncated to only show the quoted reply
        recipients=[JEFFREY_EPSTEIN],
        timestamp=datetime.fromisoformat('2016-11-04 17:46:00'),
    ),
    '030626': EmailConfig(recipients=[ALAN_DERSHOWITZ, DARREN_INDYKE, KATHRYN_RUEMMLER, KEN_STARR, MARTIN_WEINBERG]),
    '028968': EmailConfig(recipients=[ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN]),
    '029835': EmailConfig(recipients=[ALAN_DERSHOWITZ, JACK_GOLDBERGER, JEFFREY_EPSTEIN]),
    '027063': EmailConfig(recipients=[ANTHONY_BARRETT]),
    '030764': EmailConfig(recipients=[ARIANE_DE_ROTHSCHILD]),   # Reply
    '026431': EmailConfig(recipients=[ARIANE_DE_ROTHSCHILD]),   # Reply
    '032876': EmailConfig(recipients=[CECILIA_STEEN]),
    '033583': EmailConfig(recipients=[DARREN_INDYKE, JACK_GOLDBERGER]),  # Bad OCR
    '033144': EmailConfig(recipients=[DARREN_INDYKE, RICHARD_KAHN]),
    '026466': EmailConfig(recipients=[DIANE_ZIMAN]),            # Quoted reply
    '031607': EmailConfig(recipients=[EDWARD_JAY_EPSTEIN]),
    '030525': EmailConfig(recipients=[FAITH_KATES]),            # Same as unredacted 030414, same legal signature
    '030575': EmailConfig(recipients=[FAITH_KATES]),            # Same Next Management LLC legal signature
    '030475': EmailConfig(recipients=[FAITH_KATES]),            # Same Next Management LLC legal signature
    '030999': EmailConfig(recipients=[JACK_GOLDBERGER, ROBERT_D_CRITTON]),
    '026426': EmailConfig(recipients=[JEAN_HUGUEN]),            # Reply
    '029975': EmailConfig(recipients=[JEAN_LUC_BRUNEL]),        # Same as another file
    '022202': EmailConfig(recipients=[JEAN_LUC_BRUNEL]),        # Follow up
    '031489': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # Bad OCR
    '032210': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # More of a text convo?
    '022344': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # Bad OCR
    '030347': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # Bad OCR
    '030367': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # Bad OCR
    '033274': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # this is a note sent to self
    '032780': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # Bad OCR
    '025233': EmailConfig(recipients=[JEFFREY_EPSTEIN]),        # Bad OCR
    '029324': EmailConfig(recipients=[JEFFREY_EPSTEIN, 'Jojo Fontanilla', 'Lyn Fontanilla']),
    '033575': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN]),
    '023067': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, DEBBIE_FEIN, TONJA_HADDAD_COLEMAN]),  # Bad OCR
    '033228': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, FRED_HADDAD]),  # Bad OCR
    '025790': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER]),  # Bad OCR
    '031384': EmailConfig(
        recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACK_GOLDBERGER, MARTIN_WEINBERG, SCOTT_J_LINK],
        actual_text='',
    ),
    '033512': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, JACKIE_PERCZEK, MARTIN_WEINBERG]),
    '032063': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, REID_WEINGARTEN]),
    '033486': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, RICHARD_KAHN]),  # Bad OCR
    '033156': EmailConfig(recipients=[JEFFREY_EPSTEIN, DARREN_INDYKE, RICHARD_KAHN]),  # Bad OCR
    '029154': EmailConfig(recipients=[JEFFREY_EPSTEIN, DAVID_HAIG]),        # Bad OCR
    '029498': EmailConfig(recipients=[JEFFREY_EPSTEIN, DAVID_HAIG, GORDON_GETTY, 'Norman Finkelstein']),  # Bad OCR
    '029889': EmailConfig(recipients=[JEFFREY_EPSTEIN, 'Connie Zaguirre', JACK_GOLDBERGER, ROBERT_D_CRITTON]),  # Bad OCR
    '028931': EmailConfig(recipients=[JEFFREY_EPSTEIN, LAWRENCE_KRAUSS]),   # Bad OCR
    '019407': EmailConfig(recipients=[JEFFREY_EPSTEIN, MICHAEL_SITRICK]),   # Bad OCR
    '019409': EmailConfig(recipients=[JEFFREY_EPSTEIN, MICHAEL_SITRICK]),   # Bad OCR
    '031980': EmailConfig(recipients=[JEFFREY_EPSTEIN, MICHAEL_SITRICK]),   # Bad OCR
    '029163': EmailConfig(recipients=[JEFFREY_EPSTEIN, ROBERT_TRIVERS]),    # Bad OCR
    '026228': EmailConfig(recipients=[JEFFREY_EPSTEIN, STEVEN_PFEIFFER]),   # Bad OCR
    '021794': EmailConfig(recipients=[JESSICA_CADWELL, ROBERT_D_CRITTON]),  # Bad OCR, same as 030299
    '030299': EmailConfig(recipients=[JESSICA_CADWELL, ROBERT_D_CRITTON]),  # Bad OCR
    '033456': EmailConfig(recipients=['Joel']),                    # Reply
    '033460': EmailConfig(recipients=['Joel']),                    # Reply
    '021090': EmailConfig(recipients=[JONATHAN_FARKAS], is_fwded_article=True),  # Reply to a message signed " jonathan" same as other Farkas emails
    '033073': EmailConfig(recipients=[KATHRYN_RUEMMLER]),          # to "Kathy" about dems, sent from iPad (not 100% confirmed)
    '032939': EmailConfig(recipients=[KATHRYN_RUEMMLER]),          # to "Kathy" about dems, sent from iPad (not 100% confirmed)
    '031428': EmailConfig(recipients=[KEN_STARR, LILLY_SANCHEZ, MARTIN_WEINBERG, REID_WEINGARTEN]),  # Bad OCR
    '031388': EmailConfig(recipients=[KEN_STARR, LILLY_SANCHEZ, MARTIN_WEINBERG, REID_WEINGARTEN]),  # Bad OCR
    '025329': EmailConfig(recipients=KRASSNER_MANSON_RECIPIENTS),
    '033568': EmailConfig(recipients=KRASSNER_033568_RECIPIENTS),
    '030522': EmailConfig(recipients=[LANDON_THOMAS], is_fwded_article=True),  # Vicky Ward article
    '031413': EmailConfig(recipients=[LANDON_THOMAS]),
    '033591': EmailConfig(recipients=[LAWRANCE_VISOSKI]),       # Reply signature
    '033466': EmailConfig(recipients=[LAWRANCE_VISOSKI]),       # Reply signature
    '028787': EmailConfig(recipients=[LAWRANCE_VISOSKI]),
    '027097': EmailConfig(recipients=[LAWRANCE_VISOSKI]),       # Reply signature
    '022250': EmailConfig(recipients=[LESLEY_GROFF]),           # Reply
    '032048': EmailConfig(recipients=[MARIANA_IDZKOWSKA]),      # Redacted here, visisble in 030242
    '030368': EmailConfig(recipients=[MELANIE_SPINELLA]),       # Actually a self fwd from jeffrey to jeffrey
    '030369': EmailConfig(recipients=[MELANIE_SPINELLA]),       # Actually a self fwd from jeffrey to jeffrey
    '030371': EmailConfig(recipients=[MELANIE_SPINELLA]),       # Actually a self fwd from jeffrey to jeffrey
    '023291': EmailConfig(recipients=[MELANIE_SPINELLA, BRAD_WECHSLER]),   # Same as 023291
    '022258': EmailConfig(recipients=[NADIA_MARCINKO]),         # Reply header
    '033097': EmailConfig(recipients=[PAUL_BARRETT, RICHARD_KAHN]),  # Bad OCR
    '030506': EmailConfig(recipients=[PAULA]),                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030507': EmailConfig(recipients=[PAULA]),                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030508': EmailConfig(recipients=[PAULA]),                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030509': EmailConfig(recipients=[PAULA]),                  # "Sent via BlackBerry from T-Mobile" only other person is confirmed "Paula"
    '030096': EmailConfig(recipients=[PETER_MANDELSON]),
    '032951': EmailConfig(recipients=[RAAFAT_ALSABBAGH, None]), # Redacted
    '029581': EmailConfig(recipients=[RENATA_BOLOTOVA]),        # Same signature style as 029020 ("--" followed by "Sincerely Renata Bolotova")
    '030384': EmailConfig(recipients=[RICHARD_KAHN, 'Alan Dlugash']),
    '019334': EmailConfig(recipients=[STEVE_BANNON]),
    '021106': EmailConfig(recipients=[STEVE_BANNON]),           # Reply
    '032475': EmailConfig(timestamp=datetime.fromisoformat('2017-02-15 13:31:25')),
    '030373': EmailConfig(timestamp=datetime.fromisoformat('2018-10-03 01:49:27')),
    '033050': EmailConfig(actual_text='schwartman'),
    '026298': EmailConfig(is_fwded_article=True),               # Written by someone else?
    '026755': EmailConfig(is_fwded_article=True),               # HuffPo
    '023627': EmailConfig(is_fwded_article=True),               # Wolff article about epstein
    '030528': EmailConfig(is_fwded_article=True),               # Vicky Ward article
    '018197': EmailConfig(is_fwded_article=True),               # Ray Takeyh article fwd
    '028648': EmailConfig(is_fwded_article=True),               # Ray Takeyh article fwd
    '028728': EmailConfig(is_fwded_article=True),               # WSJ forward to Larry Summers
    '027102': EmailConfig(is_fwded_article=True),               # WSJ forward to Larry Summers
    '028508': EmailConfig(is_fwded_article=True),               # nanosatellites article
    '013460': EmailConfig(is_fwded_article=True),               # Atlantic on Jim Yong Kim, Obama's World Bank Pick
    '028781': EmailConfig(is_fwded_article=True),               # Atlantic on Jim Yong Kim, Obama's World Bank Pick
    '019845': EmailConfig(is_fwded_article=True),               # Pro Publica article on Preet Bharara
    '029021': EmailConfig(is_fwded_article=True),               # article about bannon sent by Alain Forget
    '031688': EmailConfig(is_fwded_article=True),               # Bill Siegel fwd of email about hamas
    '026551': EmailConfig(is_fwded_article=True),               # Sultan bin Sulayem Ayatollah between the sheets
    '031768': EmailConfig(is_fwded_article=True),               # Sultan bin Sulayem 'Horseface'
    '031569': EmailConfig(is_fwded_article=True),               # Article by Kathryn Alexeeff fwded to Peter Thiel
""".strip()

ATTRIBUTION_REGEX = re.compile(r"^    '(\d{6})':.*# (.*)")
ATTRIBUTIONS = {}

for line in EMAIL_CODE.split('\n'):
    match = ATTRIBUTION_REGEX.match(line)

    if not match:
        continue

    ATTRIBUTIONS[match.group(1)] = match.group(2)


DESCRIPTIONS_CODE = """
    # books
    '015032': f'{BOOK} "60 Years of Investigative Satire: The Best of {PAUL_KRASSNER}"',
    '015675': f'{BOOK} "Are the Androids Dreaming Yet? Amazing Brain Human Communication, Creativity & Free Will" by James Tagg',
    '012899': f'{BOOK} "Engineering General Intelligence: A Path to Advanced AGI Via Embodied Learning and Cognitive Synergy" by Ben Goertzel',
    '012747': f'{BOOK} "Evilicious: Explaining Our Taste For Excessive Harm" by Marc D. Hauser',
    '019874': f'{BOOK} {FIRE_AND_FURY}',
    '032724': f'{BOOK} cover of {FIRE_AND_FURY}',
    '010912': f'{BOOK} "Free Growth and Other Surprises" by Gordon Getty (draft) 2018-10-18',
    '021247': f'{BOOK} "Invisible Forces And Powerful Beliefs: Gravity, Gods, And Minds" by The Chicago Social Brain Network 2010-10-04',
    '019477': f'{BOOK} "How America Lost Its Secrets: Edward Snowden, the Man, and the Theft" by {EDWARD_JAY_EPSTEIN}',
    '017088': f'{BOOK} "Taking the Stand: My Life in the Law" by {ALAN_DERSHOWITZ} (draft)',
    '023731': f'{BOOK} "Teaching Minds How Cognitive Science Can Save Our Schools" by {ROGER_SCHANK}',
    '013796': f'{BOOK} "The 4-Hour Workweek" by Tim Ferriss',
    '021145': f'{BOOK} "The Billionaire\'s Playboy Club" by {VIRGINIA_GIUFFRE} (draft?)',
    '013501': f'{BOOK} "The Nearness Of Grace: A Personal Science Of Spiritual Transformation" by Arnold J. Mandell ca. 2005-01-01',
    '018438': f'{BOOK} "The S&M Feminist" by Clarisse Thorn',
    '018232': f'{BOOK} "The Seventh Sense: Power, Fortune & Survival in the Age of Networks" by Joshua Cooper Ramo',
    '020153': f'{BOOK} "The Snowden Affair: A Spy Story In Six Parts" by {EDWARD_JAY_EPSTEIN}',
    '021120': f'{BOOK} chapter of "Siege: Trump Under Fire" by {MICHAEL_WOLFF}',
    '016221': DEEP_THINKING_HINT,
    '016804': DEEP_THINKING_HINT,
    '031533': f'few pages from a book about the Baylor University sexual assault scandal and Sam Ukwuachu',
    '011472': NIGHT_FLIGHT_HINT,
    '027849': NIGHT_FLIGHT_HINT,
    '010477': PATTERSON_BOOK_SCANS,
    '010486': PATTERSON_BOOK_SCANS,
    '021958': PATTERSON_BOOK_SCANS,
    '022058': PATTERSON_BOOK_SCANS,
    '022118': PATTERSON_BOOK_SCANS,
    '019111': PATTERSON_BOOK_SCANS,
    # articles
    '030199': f'article about allegations Trump raped a 13 year old girl {JANE_DOE_V_EPSTEIN_TRUMP} 2017-11-16',
    '031725': f"article about Gloria Allred and Trump allegations 2016-10-10",
    '031198': f"article about identify of Jane Doe in {JANE_DOE_V_EPSTEIN_TRUMP}",
    '012704': f"article about {JANE_DOE_V_USA} and {CVRA} 2011-04-21",
    '026648': f'article about {JASTA} lawsuit against Saudi Arabia by 9/11 victims (Russian propaganda?) 2017-05-13',
    '031776': f"article about Michael Avenatti by Andrew Strickler",
    '032159': f"article about microfinance and cell phones in Zimbabwe, Strive Masiyiwa (Econet Wireless)",
    '026584': f'article about tax implications of "disregarded entities" 2009-07-01',
    '024256': f'article by {JOI_ITO}: "Internet & Society: The Technologies and Politics of Control"',
    '027004': f'article by {JOSCHA_BACH}: "The Computational Structure of Mental Representation" 2013-02-26',
    '015501': f'article by {MOSHE_HOFFMAN}, Erez Yoeli, and Carlos David Navarrete: "Game Theory and Morality"',
    '030258': f'{ARTICLE_DRAFT} Mueller probe, almost same as 030248',
    '030248': f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258',
    '029165': f'{ARTICLE_DRAFT} Mueller probe, almost same as 030258',
    '033468': f'{ARTICLE_DRAFT} Rod Rosenstein ca. 2018-09-24',
    '030825': f'{ARTICLE_DRAFT} Syria',
    '030013': f'Aviation International News article 2012-07',
    '033253': f'{BBC} article about Rohingya in Myanmar by {ROBERT_LAWRENCE_KUHN}',
    '026887': f'{BBC} "New Tariffs - Trade War" by {ROBERT_LAWRENCE_KUHN}',
    '013275': f"{BLOOMBERG} article on notable 2013 obituaries 2013-12-26",
    '026543': f"{BLOOMBERG} BNA article about taxes",
    '014865': f"Boston Globe article about {ALAN_DERSHOWITZ}",
    '033231': f"Business Standard article about Trump's visit with India's Modi",
    '023572': f"{CHINA_DAILY_ARTICLE} China's Belt & Road Initiative by {ROBERT_LAWRENCE_KUHN}",
    '023571': f'{CHINA_DAILY_ARTICLE} terrorism, Macau, trade initiatives 2016-09-18',
    '023570': f'{CHINA_DAILY_ARTICLE} Belt & Road in Central/South America, Xi philosophy 2017-05-14',
    '025115': f'{CHINA_DAILY_ARTICLE} China and the US working together 2017-05-14',
    '026877': f'{CNN} "New Tariffs - Trade War" by {ROBERT_LAWRENCE_KUHN}',
    '026868': f'{CNN} "Quest Means Business New China Tariffs — Trade War" by {ROBERT_LAWRENCE_KUHN} 2018-09-18',
    '023707': f'{CNN} "Quest Means Business U.S. and China Agree to Pause Trade War" by {ROBERT_LAWRENCE_KUHN} 2018-12-03',
    '029176': f'{CNN} "U.S. China Tariffs - Trade War" by {ROBERT_LAWRENCE_KUHN}',
    '032638': f'{CNN} "Xi Jinping and the New Politburo Committee" by {ROBERT_LAWRENCE_KUHN}',
    '025292': f"{DAILY_MAIL_ARTICLE} Bill Clinton being named in a lawsuit",
    '019468': f"{DAILY_MAIL_ARTICLE} Epstein and Clinton",
    '022970': f"{DAILY_MAIL_ARTICLE} Epstein and Prince Andrew",
    '031186': f'{DAILY_MAIL_ARTICLE} rape of 13 year old accusations against Trump 2016-11-02',
    '013437': f"{DAILY_TELEGRAPH_ARTICLE} Epstein diary 2011-03-05",
    '023287': f"{DAILY_TELEGRAPH_ARTICLE} play based on the Oslo Accords 2017-09-15",
    '023567': f"Financial Times article about quantitative easing",
    '026761': f'Forbes article about {BARBRO_C_EHNBOM} "Swedish American Group Focuses On Cancer"',
    '031716': f'Fortune Magazine article by {TOM_BARRACK} 2016-10-22',
    '019233': f'Freedom House: "Breaking Down Democracy: Goals, Strategies, and Methods of Modern Authoritarians" 2017-06-02',
    '019444': f'Frontlines magazine article "Biologists Dig Deeper" ca. 2008-01-01',
    '023720': f'Future Science article: "Is Shame Necessary?" by {JENNIFER_JACQUET}',
    '027051': f"German language article about the 2013 Lifeball / AIDS Gala 2013-01",
    '021094': f"Globe and Mail article about Gerd Heinrich 2007-06-12",
    '013268': f"JetGala article about airplane interior designer {ERIC_ROTH}",
    '033480': f"{JOHN_BOLTON_PRESS_CLIPPING} 2018-04-06",
    '033481': f"{JOHN_BOLTON_PRESS_CLIPPING}",
    '029539': f"{LA_TIMES} Alan Trounson interview on California stem cell research and CIRM",
    '029865': f"{LA_TIMES} front page article about {DEEPAK_CHOPRA} and young Iranians 2016-11-05",
    '026598': f"{LA_TIMES} op-ed about why America needs a Ministry of Culture",
    '027024': f'{LA_TIMES} "Scientists Create Human Embryos to Make Stem Cells" 2013-05-15',
    '013403': f"Lexis Nexis result from The Evening Standard about Bernie Madoff 2009-12-24",
    '023102': f"Litigation Daily article about {REID_WEINGARTEN} 2015-09-04",
    '029340': f'MarketWatch article about estate taxes, particularly Epstein\'s favoured GRATs',
    '022707': MICHAEL_WOLFF_ARTICLE_HINT,
    '022727': MICHAEL_WOLFF_ARTICLE_HINT,
    '022746': MICHAEL_WOLFF_ARTICLE_HINT,
    '022844': MICHAEL_WOLFF_ARTICLE_HINT,
    '022863': MICHAEL_WOLFF_ARTICLE_HINT,
    '022894': MICHAEL_WOLFF_ARTICLE_HINT,
    '022952': MICHAEL_WOLFF_ARTICLE_HINT,
    '023627': MICHAEL_WOLFF_ARTICLE_HINT,
    '024229': MICHAEL_WOLFF_ARTICLE_HINT,
    '029416': f"{NATIONAL_ENQUIRER_FILING} 2017-05-25",
    '029405': f"{NATIONAL_ENQUIRER_FILING} 2017-05-25",
    '015462': f'Nautilus Education magazine (?) issue',
    '029925': f"New Yorker article about the placebo effect by Michael Specter 2011-12-04",
    '031972': f"{NYT_ARTICLE} #MeToo allegations against {LAWRENCE_KRAUSS} 2018-03-07",
    '032435': f'{NYT_ARTICLE} Chinese butlers',
    '029452': f"{NYT_ARTICLE} {PETER_THIEL}",
    '025328': f"{NYT_ARTICLE} radio host Bob Fass and Robert Durst",
    '033479': f"{NYT_ARTICLE} Rex Tillerson 2010-03-14",
    '028481': f'{NYT_ARTICLE} {STEVE_BANNON} 2018-03-09',
    '033181': f'{NYT_ARTICLE} Trump\'s tax avoidance 2016-10-31',
    '023097': f'{NYT_COLUMN} The Aristocrats by Frank Rich "The Greatest Dirty Joke Ever Told"',
    '033365': f'{NYT_COLUMN} trade war with China by Kevin Rudd',
    '019439': f"{NYT_COLUMN} the Clintons and money by Maureen Dowd 2013-08-17",
    '021093': f"page of unknown article about Epstein and Maxwell",
    '013435': f"{PALM_BEACH_DAILY_ARTICLE} Epstein's address book 2011-03-11",
    '013440': f"{PALM_BEACH_DAILY_ARTICLE} Epstein's gag order 2011-07-13",
    '029238': f"{PALM_BEACH_DAILY_ARTICLE} Epstein's plea deal",
    '021775': f'{PALM_BEACH_POST_ARTICLE} "He Was 50. And They Were Girls"',
    '022989': f"{PALM_BEACH_POST_ARTICLE} alleged rape of 13 year old by Trump",
    '022987': f"{PALM_BEACH_POST_ARTICLE} just a headline on Trump and Epstein",
    '015028': f"{PALM_BEACH_POST_ARTICLE} reopening Epstein's criminal case",
    '022990': f"{PALM_BEACH_POST_ARTICLE} Trump and Epstein",
    '031753': f'{PAUL_KRASSNER} essay for Playboy in the 1980s 1985-01-01',
    '023638': f'{PAUL_KRASSNER} magazine interview',
    '024374': f'{PAUL_KRASSNER} "Remembering Cavalier Magazine"',
    '030187': f'{PAUL_KRASSNER} "Remembering Lenny Bruce While We\'re Thinking About Trump" (draft?)',
    '019088': f'{PAUL_KRASSNER} "Are Rape Jokes Funny? (draft) 2012-07-28',
    '012740': f"{PEGGY_SIEGAL} article about Venice Film Festival ca. 2011-09-06",
    '013442': f"{PEGGY_SIEGAL} draft about Oscars ca. 2011-02-27",
    '012700': f"{PEGGY_SIEGAL} film events diary 2011-02-27",
    '012690': f"{PEGGY_SIEGAL} film events diary early draft of 012700 2011-02-27",
    '013450': f"{PEGGY_SIEGAL} Oscar Diary in Avenue Magazine 2011-02-27",
    '010715': f"{PEGGY_SIEGAL} Oscar Diary April 2012-02-27",
    '019864': f"{PEGGY_SIEGAL} Oscar Diary April 2017-02-27",
    '019849': f"{PEGGY_SIEGAL} Oscar Diary April 2017-02-27",
    '033323': f'{ROBERT_TRIVERS} and Nathan H. Lents "Does Trump Fit the Evolutionary Role of Narcissistic Sociopath?" (draft) 2018-12-07',
    '025143': f'{ROBERT_TRIVERS} essay "Africa, Parasites, Intelligence" ca. 2018-06-25',
    '016996': f'SciencExpress article "Quantitative Analysis of Culture Using Millions of Digitized Books" by Jean-Baptiste Michel',
    '025104': f"SCMP article about China and globalisation",
    '030030': f'{SHIMON_POST_ARTICLE} 2011-03-29',
    '025610': f'{SHIMON_POST_ARTICLE} 2011-04-03',
    '023458': f'{SHIMON_POST_ARTICLE} 2011-04-17',
    '023487': f'{SHIMON_POST_ARTICLE} 2011-04-18',
    '030531': f'{SHIMON_POST_ARTICLE} 2011-04-20',
    '024958': f'{SHIMON_POST_ARTICLE} 2011-05-08',
    '030060': f'{SHIMON_POST_ARTICLE} 2011-05-13',
    '030531': f'{SHIMON_POST_ARTICLE} 2011-05-16',
    '031834': f'{SHIMON_POST_ARTICLE} 2011-05-16',
    '023517': f'{SHIMON_POST_ARTICLE} 2011-05-26',
    '030268': f'{SHIMON_POST_ARTICLE} 2011-05-29',
    '029628': f'{SHIMON_POST_ARTICLE} 2011-06-04',
    '018085': f'{SHIMON_POST_ARTICLE} 2011-06-07',
    '030156': f'{SHIMON_POST_ARTICLE} 2011-06-22',
    '031876': f'{SHIMON_POST_ARTICLE} 2011-06-14',
    '032171': f'{SHIMON_POST_ARTICLE} 2011-06-26',
    '029932': f'{SHIMON_POST_ARTICLE} 2011-07-03',
    '031913': f'{SHIMON_POST_ARTICLE} 2011-08-24',
    '024592': f'{SHIMON_POST_ARTICLE} 2011-08-25',
    '024997': f'{SHIMON_POST_ARTICLE} 2011-09-08',
    '031941': f'{SHIMON_POST_ARTICLE} 2011-11-17',
    '021092': f'{SINGLE_PAGE} Tatler article about {GHISLAINE_MAXWELL} shredding documents 2019-08-15',
    '031191': f"{SINGLE_PAGE} unknown article about Epstein and Trump's relationship in 1997",
    '030829': f'South Florida Sun Sentinel article about {BRAD_EDWARDS} and {JEFFREY_EPSTEIN}',
    '026520': f'Spanish language article about {SULTAN_BIN_SULAYEM} 2013-09-27',
    '030333': f'The Independent article about Prince Andrew, Epstein, and Epstein\'s butler who stole his address book',
    '031736': f'{TRANSLATION} Arabic article by Abdulnaser Salamah "Trump; Prince of Believers (Caliph)!" 2017-05-13',
    '025094': f'{TRANSLATION} Spanish article about Cuba 2015-11-08',
    '010754': f"U.S. News article about Yitzhak Rabin 2015-11-04",
    '031794': f"very short French magazine clipping",
    '014498': f"{VI_DAILY_NEWS_ARTICLE} 2016-12-13",
    '031171': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-06",
    '023048': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-27",
    '023046': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-27",
    '031170': f"{VI_DAILY_NEWS_ARTICLE} 2019-03-06",
    '016506': f"{VI_DAILY_NEWS_ARTICLE} 2019-02-28",
    '016507': f'{VI_DAILY_NEWS_ARTICLE} "Perversion of Justice" by {JULIE_K_BROWN} 2018-12-19',
    '019212': f'{WAPO} and Times Tribune articles about Bannon, Trump, and healthcare execs',
    '033379': f'{WAPO} "How Washington Pivoted From Finger-Wagging to Appeasement" about Viktor Orban 2018-05-25',
    '031415': f'{WAPO} "DOJ discipline office with limited reach to probe handling of controversial sex abuse case" 2019-02-06',
    '031396': f'{WAPO} "DOJ discipline office with limited reach to probe handling of controversial sex abuse case" 2019-02-06',
    '019206': f"WSJ article about Edward Snowden by {EDWARD_JAY_EPSTEIN} 2016-12-30",
    # court docs
    '017603': DAVID_SCHOEN_CVRA_LEXIS_SEARCH,
    '017635': DAVID_SCHOEN_CVRA_LEXIS_SEARCH,
    '016509': DAVID_SCHOEN_CVRA_LEXIS_SEARCH,
    '017714': DAVID_SCHOEN_CVRA_LEXIS_SEARCH,
    '021824': f"{EDWARDS_V_DERSHOWITZ} deposition of {PAUL_G_CASSELL}",
    '010757': f"{EDWARDS_V_DERSHOWITZ} plaintiff response to Dershowitz Motion to Determine Confidentiality of Court Records 2015-11-23",
    '010887': f"{EDWARDS_V_DERSHOWITZ} Dershowitz Motion for Clarification of Confidentiality Order 2016-01-29",
    '015590': f"{EDWARDS_V_DERSHOWITZ} Dershowitz Redacted Motion to Modify Confidentiality Order 2016-02-03",
    '015650': f"{EDWARDS_V_DERSHOWITZ} Giuffre Response to Dershowitz Motion for Clarification of Confidentiality Order 2016-02-08",
    '010566': f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Statement of Undisputed Facts 2010-11-04",
    '012707': f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Master Contact List - Privilege Log 2011-03-22",
    '012103': f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Telephone Interview with {VIRGINIA_GIUFFRE} 2011-05-17",
    '017488': f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Deposition of Scott Rothstein 2012-06-22",
    '029315': f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Plaintiff Motion for Summary Judgment by {JACK_SCAROLA} 2013-09-13",
    '013304': f"{EPSTEIN_V_ROTHSTEIN_AND_EDWARDS} Plaintiff Response to Epstein's Motion for Summary Judgment 2014-04-17",
    '019352': FBI_REPORT,
    '021434': FBI_REPORT,
    '018872': FBI_SEIZED_PROPERTY,
    '021569': FBI_SEIZED_PROPERTY,
    '022494': f'Foreign Corrupt Practices Act (FCPA) DOJ Resource Guide ca. 2013-01',
    '017792': f"{GIUFFRE_V_DERSHOWITZ} article about Dershowitz's appearance on Wolf Blitzer",
    '017767': f"{GIUFFRE_V_DERSHOWITZ} article about {ALAN_DERSHOWITZ} working with {JEFFREY_EPSTEIN}",
    '017796': f"{GIUFFRE_V_DERSHOWITZ} article about {ALAN_DERSHOWITZ}",
    '017935': f"{GIUFFRE_V_DERSHOWITZ} defamation complaint 2019-04-16",
    '017824': f"{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} article by {JULIE_K_BROWN}",
    '017818': f"{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} article about accusations against {ALAN_DERSHOWITZ} by {JULIE_K_BROWN} 2018-12-27",
    '017800': f'{GIUFFRE_V_DERSHOWITZ} {MIAMI_HERALD} "Perversion of Justice" by {JULIE_K_BROWN}',
    '022237': f"{GIUFFRE_V_DERSHOWITZ} partial court filing with fact checking questions?",
    '016197': f"{GIUFFRE_V_DERSHOWITZ} response to Florida Bar complaint by {ALAN_DERSHOWITZ} about David Boies from {PAUL_G_CASSELL}",
    '017771': f'{GIUFFRE_V_DERSHOWITZ} Vanity Fair article "The Talented Mr. Epstein" by Vicky Ward 2011-06-27',
    '014652': f"{GIUFFRE_V_MAXWELL} Complaint 2015-04-22",
    '014797': f"{GIUFFRE_V_MAXWELL} Declaration of Laura A. Menninger in Opposition to Plaintiff's Motion 2017-03-17",
    '014118': f"{GIUFFRE_V_EPSTEIN} Declaration in Support of Motion to Compel Production of Documents 2016-10-21",
    '015529': f"{GIUFFRE_V_MAXWELL} defamation complaint 2015-09-21",
    '019297': f'{GIUFFRE_V_MAXWELL} letter from {ALAN_DERSHOWITZ} lawyer Andrew G. Celli 2018-02-07',
    '011463': f"{GIUFFRE_V_MAXWELL} Maxwell Response to Plaintiff's Omnibus Motion in Limine 2017-03-17",
    '014788': f"{GIUFFRE_V_MAXWELL} Maxwell Response to Plaintiff's Omnibus Motion in Limine 2017-03-17",
    '011304': f"{GIUFFRE_V_MAXWELL} Oral Argument Transcript 2017-03-17",
    '013489': f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of {BRAD_EDWARDS} 2010-07-20',
    '025939': f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of Jane Doe describing being raped by Epstein 2016-06-20',
    '025937': f'{JANE_DOE_V_EPSTEIN_TRUMP} Affidavit of Tiffany Doe describing Jane Doe being raped by Epstein and Trump 2016-06-20',
    '029398': f'{JANE_DOE_V_EPSTEIN_TRUMP} article in Law.com',
    '026854': f"{JANE_DOE_V_EPSTEIN_TRUMP} Civil Docket",
    '026384': f"{JANE_DOE_V_EPSTEIN_TRUMP} Complaint for rape and sexual abuse 2016-06-20",
    '013463': f'{JANE_DOE_V_EPSTEIN_TRUMP} Deposition of Scott Rothstein filed by {BRAD_EDWARDS} 2010-03-23',
    '029257': f'{JANE_DOE_V_EPSTEIN_TRUMP} factual allegations and identity of plaintiff Katie Johnson 2016-04-26',
    '032321': f"{JANE_DOE_V_EPSTEIN_TRUMP} Notice of Initial Conference 2016-10-04",
    '010735': f"{JANE_DOE_V_USA} Dershowitz Reply in Support of Motion for Limited Intervention 2015-02-02",
    '014084': f"{JANE_DOE_V_USA} Jane Doe Response to Dershowitz's Motion for Limited Intervention 2015-03-24",
    '023361': f"{JASTA_SAUDI_LAWSUIT} legal text and court documents 2012-01-20",
    '017830': f"{JASTA_SAUDI_LAWSUIT} legal text and court documents",
    '017904': f"{JASTA_SAUDI_LAWSUIT} Westlaw search results 2019-01",
    '011908': f"{JEAN_LUC_BRUNEL} v. {JEFFREY_EPSTEIN} and Tyler McDonald d/b/a YI.org court filing",
    '014037': f"Journal of Criminal Law and Criminology article on {CVRA}",
    '010723': f"{KEN_STARR_LETTER} 2008-05-19",
    '025353': f"{KEN_STARR_LETTER} 2008-05-19",
    '019224': f"{KEN_STARR_LETTER} 2008-05-19",
    '025704': f"{KEN_STARR_LETTER} 2008-05-27",
    '019221': f"{KEN_STARR_LETTER} 2008-05-27",
    '010732': f"{KEN_STARR_LETTER} 2008-05-27",
    '012130': f"{KEN_STARR_LETTER} 2008-06-19",
    '012135': f"{KEN_STARR_LETTER} 2008-06-19",
    '020662': f"letter from {ALAN_DERSHOWITZ}'s British lawyers Mishcon de Reya to Daily Mail threatening libel suit",
    '010560': f"letter from Gloria Allred to {SCOTT_J_LINK} alleging abuse of a girl from Kansas 2019-06-19",
    '031447': f"letter from {MARTIN_WEINBERG} to Melanie Ann Pustay and Sean O'Neill re: an Epstein FOIA request",
    '026793': f"letter from {STEVEN_HOFFENBERG}'s lawyers at Mintz Fraade offering to take over Epstein's business and resolve his legal issues 2018-03-23",
    '016420': f"{NEW_YORK_V_EPSTEIN} New York Post Motion to Unseal Appellate Briefs 2019-01-11",
    '028540': f"SCOTUS decision in Budha Ismail Jam et al. v. INTERNATIONAL FINANCE CORP",
    '012197': f"SDFL Response to {JAY_LEFKOWITZ} on Epstein Plea Agreement Compliance",
    '022277': f"{TEXT_OF_US_LAW} National Labour Relations Board (NLRB)",
    # conferences
    '030769': f"2017 Independent Filmmaker Project (IFP) Gotham Awards invitation",
    '014951': f"2017 TED Talks program 2017-04-20",
    '023069': f'{BOFA_MERRILL} 2016 Future of Financials Conference',
    '014315': f'{BOFA_MERRILL} 2016 Future of Financials Conference',
    '026825': f"Deutsche Asset & Wealth Management featured speaker bios",
    '017526': f'Intellectual Jazz conference brochure f. {DAVID_BLAINE}',
    '023120': f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more (old draft)",
    '023121': f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more (old draft)",
    '023123': f"{LAWRENCE_KRAUSS} 'Strange Bedfellows' list of invitees f. Johnny Depp, Woody Allen, Obama, and more",
    '031359': f"{NOBEL_CHARITABLE_TRUST} Earth Environment Convention about ESG investing",
    '031354': f'{NOBEL_CHARITABLE_TRUST} "Thinking About the Environment and Technology" report 2011',
    '024179': f'president and first lady schedule at 67th U.N. General Assembly 2012-09-21',
    '029427': f"seems related to an IRL meeting about concerns China will attempt to absorb Mongolia",
    '024185': f'schedule of 67th U.N. General Assembly w/"Presidents Private Dinner - Jeffrey Epstine (sic)" 2012-09-21',
    '025797': f'someone\'s notes from Aspen Strategy Group ca. 2013-05-29',
    '017524': f"{SWEDISH_LIFE_SCIENCES_SUMMIT} 2012 program 2012-08-22",
    '026747': f"{SWEDISH_LIFE_SCIENCES_SUMMIT} 2017 program 2017-08-23",
    '026731': f"text of speech by Lord Martin Rees at first inaugural Carl Sagan Lecture at Cornell",
    '019300': f'{WOMEN_EMPOWERMENT} f. {KATHRYN_RUEMMLER} 2019-04-05',
    '022267': f'{WOMEN_EMPOWERMENT} founder essay about growing the seminar business',
    '022407': f'{WOMEN_EMPOWERMENT} seminar pitch deck',
    '017060': f'World Economic Forum (WEF) Annual Meeting 2011 List of Participants 2011-01-18',
    # press releases, reports, etc.
    '024631': f"Ackrell Capital Cannabis Investment Report 2018",
    '016111': f'{BOFA_MERRILL} "GEMs Paper #26 Saudi Arabia: beyond oil but not so fast" 2016-06-30',
    '010609': f'{BOFA_MERRILL} "Liquid Insight Trump\'s effect on MXN" 2016-09-22',
    '025978': f'{BOFA_MERRILL} "Understanding when risk parity risk Increases" 2016-08-09',
    '014404': f'{BOFA_MERRILL} Japan Investment Strategy Report 2016-11-18',
    '014410': f'{BOFA_MERRILL} Japan Investment Strategy Report 2016-11-18',
    '014424': f'{BOFA_MERRILL} "Japan Macro Watch" 2016-11-14',
    '014731': f'{BOFA_MERRILL} "Global Rates, FX & EM 2017 Year Ahead" 2016-11-16',
    '014432': f'{BOFA_MERRILL} "Global Cross Asset Strategy - Year Ahead The Trump inflection" 2016-11-30',
    '014460': f'{BOFA_MERRILL} "European Equity Strategy 2017" 2016-12-01',
    '014972': f'{BOFA_MERRILL} "Global Equity Volatility Insights" 2017-06-20',
    '014622': f'{BOFA_MERRILL} "Top 10 US Ideas Quarterly" 2017-01-03',
    '014721': f'{BOFA_MERRILL} "Cause and Effect Fade the Trump Risk Premium" 2017-02-13',
    '014887': f'{BOFA_MERRILL} "Internet / e-Commerce" 2017-04-06',
    '014873': f'{BOFA_MERRILL} "Hess Corp" 2017-04-11',
    '023575': f'{BOFA_MERRILL} "Global Equity Volatility Insights" 2017-06',
    '014518': f'{BOFA_WEALTH_MGMT} tax alert 2016-05-02',
    '029438': f'{BOFA_WEALTH_MGMT} tax report 2018-01-02',
    '024271': f"Blockchain Capital and Brock Pierce pitch deck ca. 2015-10-01",
    '024302': f"Carvana form 14A SEC filing proxy statement 2019-04-23",
    '029305': f"CCH Tax Briefing on end of Defense of Marriage Act 2013-06-27",
    '014697': CHALLENGES_OF_AI,
    '011284': CHALLENGES_OF_AI,
    '024817': f"Cowen's Collective View of CBD / Cannabis report",
    '026794': f'{DEUTSCHE_BANK} Global Public Affairs report: "Global Political and Regulatory Risk in 2015/2016"',
    '022361': f'{DEUTSCHE_BANK_TAX_TOPICS} 2013-05',
    '022325': f'{DEUTSCHE_BANK_TAX_TOPICS} 2013-12-20',
    '022330': f'{DEUTSCHE_BANK_TAX_TOPICS} table of contents 2013-12-20',
    '019440': f'{DEUTSCHE_BANK_TAX_TOPICS} 2014-01-29',
    '024202': f'Electron Capital Partners LLC "Global Utility White Paper" 2013-03-08',
    '022372': f'Ernst & Young 2016 election report',
    '025663': f'{GOLDMAN_SACHS} report "An Overview of the Current State of Cryptocurrencies and Blockchain" 2017-11',
    '014532': f'{GOLDMAN_REPORT} "Outlook - Half Full" 2017-01-01',
    '026909': f'{GOLDMAN_REPORT} "The Unsteady Undertow Commands the Seas (Temporarily)" 2018-10-14',
    '026944': f'{GOLDMAN_REPORT} "Risk of a US-Iran Military Conflict" 2019-05-23',
    '026679': f'Invesco report: "Global Sovereign Asset Management Study 2017"',
    '023096': f'{EPSTEIN_FOUNDATION} blog 2012-11-15',
    '029326': f'{EPSTEIN_FOUNDATION} {PRESS_RELEASE} 2013-02-15',
    '026565': f'{EPSTEIN_FOUNDATION} {PRESS_RELEASE}, maybe a draft of 029326 2013-02-15',
    '026572': f"{JP_MORGAN} Global Asset Allocation report 2012-11-09",
    '030848': f"{JP_MORGAN} Global Asset Allocation report 2013-03-28",
    '030840': f"{JP_MORGAN} Market Thoughts 2012-11",
    '022350': f"{JP_MORGAN} report on tax efficiency of Intentionally Defective Grantor Trusts (IDGT)",
    '025242': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-04-09",
    '030010': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-06-14",
    '030808': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-07-11",
    '025221': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-07-25",
    '025229': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-08-04",
    '030814': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2011-11-21",
    '024132': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2012-03-15",
    '025242': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2012-04-09",
    '024194': f"{JP_MORGAN_EYE_ON_THE_MARKET} 2012-10-22",
    '025296': f'Laffer Associates report predicting Trump win 2016-07',
    '025551': f'Morgan Stanley report about alternative asset managers 2018-01-30',
    '026759': f'{PRESS_RELEASE} by Ritz-Carlton club about damage from Hurricane Irma 2017-09-13',
    '033338': f"{PRESS_RELEASE} announcing Donald Trump & {NICHOLAS_RIBIS} ended their working relationship at Trump's casino 2000-06-07",
    '012048': f'{PRESS_RELEASE} "Rockefeller Partners with Gregory J. Fleming to Create Independent Financial Services Firm" and other articles',
    '020447': f'Promoting Constructive Vigilance: Report of the Working Group on Chinese Influence Activities in the U.S. (Hoover Group/Stanford 2018)',
    '025763': f'S&P Economic Research: "How Increasing Income Inequality Is Dampening U.S. Growth" 2014-08-05',
    '019856': f"Sadis Goldberg LLP report on SCOTUS ruling about insider trading",
    '026827': f'Scowcroft Group report on ISIS 2015-11-14',
    '033220': f"short economic report on defense spending under Trump by Joseph G. Carson",
    '026856': f'speech by former Australian PM Kevin Rudd "Xi Jinping, China And The Global Order" 2018-06-26',
    '023133': f'"The Search for Peace in the Arab-Israeli Conflict" edited by {TERJE_ROD_LARSEN}, Nur Laiq, Fabrice Aidan 2019-12-09',
    '024135': f'{UBS_CIO_REPORT} 2012-06-29',
    '025247': f'{UBS_CIO_REPORT} 2012-10-25',
    '025849': f'US Office of Government Information Services report: "Building a Bridge Between FOIA Requesters & Agencies"',
    '020824': f"USA Inc: A Basic Summary of America's Financial Statements compiled by Mary Meeker 2011-02-01",
    # letters
    '017789': f'{ALAN_DERSHOWITZ} letter to {HARVARD} Crimson complaining he was defamed',
    '019086': f"{DAVID_BLAINE_VISA_LETTER} from Russia 'Svet' ({SVETLANA_POZHIDAEVA}?), names Putin puppet regimes ca. 2015-05-27",  # Date is a guess based on other drafts
    '019474': f"{DAVID_BLAINE_VISA_LETTER} from Russia 'Svetlana' ({SVETLANA_POZHIDAEVA}?) 2015-05-29",
    '019476': f"{DAVID_BLAINE_VISA_LETTER} (probably {SVETLANA_POZHIDAEVA}?) 2015-06-01",
    '031278': f"heavily redacted email, quoted replies are from {STEVEN_HOFFENBERG} about James Patterson's book",  # Quoted replies are in 019109
    '031670': f"letter from General Mike Flynn's lawyers to senators Mark Warner & Richard Burr about subpoena",
    '026011': f"letter from Gennady Mashtalyar to Epstein about algorithmic trading ca. 2016-06-24",  # date is based on Brexit reference but he could be backtesting
    '029301': f"letter from {MICHAEL_J_BOCCIO}, former lawyer at the Trump Organization 2011-08-07",
    '022405': f"letter from {NOAM_CHOMSKY} attesting to Epstein's good character",
    '026248': f'letter from Trump lawyer Don McGahn to Devin Nunes (R-CA) about FISA courts and Trump',
    '026134': f'letter to someone named George about investment opportunities in the Ukraine banking sector',
    '029304': f"Trump recommendation letter for recently departed Trump Organization lawyer {MICHAEL_J_BOCCIO}",
    '028928': WEINBERG_ABC_LETTER,
    '028965': WEINBERG_ABC_LETTER,
    # private placement memoranda
    '026668': f"Boothbay Fund Management 2016-Q4 earnings report signed by Ari Glass",
    '024432': f"Michael Milken's Knowledge Universe Education (KUE) $1,000,000 corporate share placement notice (SEC filing?)",
    '024003': f"New Leaf Ventures private placement memorandum",
    # property
    '018804': f"appraisal of going concern for IGY American Yacht Harbor Marina in {VIRGIN_ISLANDS}",
    '018743': f"Las Vegas property listing",
    '016597': f'letter from Trump Properties LLC appealing some decision about Mar-a-Lago by {PALM_BEACH} authorities',
    '016602': f"{PALM_BEACH_CODE_ENFORCEMENT} 2008-04-17",
    '016616': f"{PALM_BEACH_CODE_ENFORCEMENT} 2008-07-17",
    '016554': f"{PALM_BEACH_CODE_ENFORCEMENT} 2008-07-17",
    '016574': f"{PALM_BEACH_CODE_ENFORCEMENT} 2008-07-17",
    '016695': f"{PALM_BEACH} property info (?)",
    '016697': f"{PALM_BEACH} property tax info (?) that mentions Trump",
    '016636': f"{PALM_BEACH_WATER_COMMITTEE} Meeting on January 29, 2009",
    '022417': f"Park Partners NYC letter to partners in real estate project with architectural plans",
    '027068': f"{THE_REAL_DEAL_ARTICLE} 2018-10-11",
    '029520': f'{THE_REAL_DEAL_ARTICLE} "Lost Paradise at the Palm House" 2019-06-17',
    '018727': f"{VIRGIN_ISLANDS} property deal pitch deck, building will be leased to the U.S. govt GSA ca. 2014-06-01",
    # TSV files
    '016599': f"{PALM_BEACH_TSV} consumption (water?)",
    '016600': f"{PALM_BEACH_TSV} consumption (water?)",
    '016601': f"{PALM_BEACH_TSV} consumption (water?)",
    '016694': f"{PALM_BEACH_TSV} consumption (water?)",
    '016552': f"{PALM_BEACH_TSV} info",
    '016698': f"{PALM_BEACH_TSV} info (broken?)",
    '016696': f"{PALM_BEACH_TSV} info (water quality?",
    # reputation management
    '026582': f"{REPUTATION_MGMT} Epstein's internet search results at start of reputation repair campaign, maybe from {OSBORNE_LLP}",
    '030573': f"{REPUTATION_MGMT} Epstein's unflattering Google search results, maybe screenshot by {AL_SECKEL} or {OSBORNE_LLP}",
    '026583': f"{REPUTATION_MGMT} Google search results for '{JEFFREY_EPSTEIN}' with analysis ({OSBORNE_LLP}?)",
    '029350': f"{REPUTATION_MGMT} Microsoft Bing search results for Epstein with sex offender at top, maybe from {TYLER_SHEARS}?",
    '030426': f'{REPUTATION_MGMT} {OSBORNE_LLP} reputation repair proposal (cites Michael Milken) 2011-06-14',
    '030875': f"{REPUTATION_MGMT} {SCREENSHOT} Epstein's Wikipedia page",
    # misc
    '031743': f'a few pages describing the internet as a "New Nation State" (Network State?)',
    '018703': f"{ANDRES_SERRANO} artist statement about Trump objects",
    '028281': f'art show flier for "The House Of The Nobleman" curated by Wolfe Von Lenkiewicz & Victoria Golembiovskaya',
    '023438': f"Brockman announcemeent of auction of 'Noise' by Daniel Kahneman, Olivier Sibony, and Cass Sunstein",
    '025147': f'Brockman hot list Frankfurt Book Fair (includes article about Silk Road/Ross Ulbricht) 2016-10-23',
    '031425': f'completely redacted email from {SCOTT_J_LINK}',
    '012718': f"{CVRA} congressional record ca. 2011-06-17",
    '018224': f"conversation with {LAWRENCE_KRAUSS}?",
    '023050': f"{DERSH_GIUFFRE_TWEET}",
    '017787': f"{DERSH_GIUFFRE_TWEET}",
    '033433': f"{DERSH_GIUFFRE_TWEET} / David Boies 2019-03-02",
    '033432': f"{DERSH_GIUFFRE_TWEET} / David Boies 2019-05-02",
    '029918': f"{DIANA_DEGETTES_CAMPAIGN} campaign bio ca. 2012-01-01",
    '031184': f"{DIANA_DEGETTES_CAMPAIGN} fundraiser invitation",
    '027009': f"{EHUD_BARAK} speech to AIPAC 2013-03-03",
    '025540': f"Epstein's rough draft of his side of the story?",
    '024117': f"FAQ about anti-money laundering (AML) and terrorist financing (CFT) laws in the U.S.",
    '027071': f"{FEMALE_HEALTH_COMPANY} brochure request donations for female condoms in Uganda",
    '027074': f"{FEMALE_HEALTH_COMPANY} pitch deck (USAID was a customer)",
    '022780': FLIGHT_LOGS,
    '022816': FLIGHT_LOGS,
    '026678': f"fragment of image metadata {QUESTION_MARKS} 2017-06-29",
    '022986': f"fragment of a screenshot {QUESTION_MARKS}",
    '026521': f"game theory paper by {MARTIN_NOWAK}, Erez Yoeli, and Moshe Hoffman",
    '032735': f"{GORDON_GETTY} on Trump ca. 2018-03-20",  # Dated based on concurrent emails from Getty
    '019396': f'{HARVARD} Economics 1545 Professor Kenneth Rogoff syllabus',
    '023416': HARVARD_POETRY,
    '023435': HARVARD_POETRY,
    '023450': HARVARD_POETRY,
    '023452': HARVARD_POETRY,
    '029517': HARVARD_POETRY,
    '029543': HARVARD_POETRY,
    '029589': HARVARD_POETRY,
    '029589': HARVARD_POETRY,
    '029603': HARVARD_POETRY,
    '029298': HARVARD_POETRY,
    '029592': HARVARD_POETRY,
    '029102': HBS_APPLICATION_NERIO,
    '029104': HBS_APPLICATION_NERIO,
    '022445': f"Inference: International Review of Science Feedback & Comments 2018-11",
    '028815': f"{INSIGHTS_POD} business plan 2016-08-20",
    '011170': f'{INSIGHTS_POD} collected tweets about #Brexit 2016-06-23',
    '032324': f"{INSIGHTS_POD} election social media trend analysis 2016-11-05",
    '032281': f"{INSIGHTS_POD} forecasting election for Trump ca. 2016-10-25",
    '028988': f"{INSIGHTS_POD} pitch deck 2016-08-20",
    '026627': f"{INSIGHTS_POD} report on the presidential debate",
    '030142': f"{JASTA} (Justice Against Sponsors of Terrorism Act) doc that's mostly empty, references suit against Saudi f. {KATHRYN_RUEMMLER} & {KEN_STARR} ca. 2016-09-01",
    '033478': f'meme of Kim Jong Un reading {FIRE_AND_FURY}',
    '032713': f'meme of Kim Jong Un reading {FIRE_AND_FURY}',
    '033177': f'meme of Trump with text "WOULD YOU TRUST THIS MAN WITH YOUR DAUGHTER?"',
    '025205': MERCURY_FILMS_PROFILES,
    '025210': MERCURY_FILMS_PROFILES,
    '029564': f"{OBAMA_JOKE} ca. 2013-07-26",
    '029353': f"{OBAMA_JOKE} ca. 2013-07-26",
    '029352': f"{OBAMA_JOKE} ca. 2013-07-26",
    '029351': f"{OBAMA_JOKE} ca. 2013-07-26",
    '029354': f"{OBAMA_JOKE} ca. 2013-07-26",
    '026851': f"Politifact lying politicians chart 2016-07-26",
    '022367': f"{RESUME_OF} Jack J Grynberg 2014-07",
    '029302': f"{RESUME_OF} {MICHAEL_J_BOCCIO}, former lawyer at the Trump Organization 2011-08-07",
    '015671': f"{RESUME_OF} Robin Solomon ca. 2015-06-02",  # She left Mount Sinai at some point in 2015
    '015672': f"{RESUME_OF} Robin Solomon ca. 2015-06-02",  # She left Mount Sinai at some point in 2015
    '019448': f"Haitian business investment proposal called Jacmel",
    '029328': f"Rafanelli Events promotional deck",
    '029155': f'response sent to the Gruterites ({GORDON_GETTY} fans) by {ROBERT_TRIVERS} ca. 2018-03-19',
    '023666': f"{ROBERT_LAWRENCE_KUHN} sizzle reel / television appearances",
    '022213': f"{SCREENSHOT} Facebook group called 'Shit Pilots Say' disparaging a 'global girl'",
    '033434': f"{SCREENSHOT} iPhone chat labeled 'Edwards' at the top",
    '029356': f'{SCREENSHOT} quote in book about {LARRY_SUMMERS} (zoomed in corner of 029355)',
    '029355': f'{SCREENSHOT} two pages of a book in which {LARRY_SUMMERS} is mentioned',
    '029623': f'short bio of Kathleen Harrington, Founding Partner, C/H Global Strategies',
    '026634': f"some short comments about an Apollo linked hedge fund 'DE Fund VIII'",
    '029357': f"some text about Israel's challenges going into 2015, feels like it was extracted from a book 2015-01",
    '024294': f"{STACEY_PLASKETT} campaign flier ca. 2016-10-01",
    '023644': f"transcription of an interview with MBS from Saudi 2016-04-25",
    '010617': TRUMP_DISCLOSURES,
    '016699': TRUMP_DISCLOSURES,
    '030884': f"{TWEET} by Ed Krassenstein",
    '031546': f"{TWEET}s by Donald Trump about Russian collusion 2018-01-06",
    '033236': f'{TWEET}s about Ivanka Trump in Arabic 2017-05-20',
    '029475': f'{VIRGIN_ISLANDS} Twin City Mobile Integrated Health Services (TCMIH) proposal/request for donation',
    '029448': f'weird short essay titled "President Obama and Self-Deception"',
""".strip()

LINE_REGEX = re.compile(r"'(\d+)':(.*),?")
COMMENTS = {}
DESCRIPTIONS: dict[str, str] = {}


comment_swap_next = False
next_id = 'xxxxxx'
next_comment: str = '# books'

for i, line in enumerate(DESCRIPTIONS_CODE.split('\n')):
    line = line.strip()

    if line == '# books':
        continue
    if line.startswith('#'):
        comment_swap_next = True
        next_comment = line
    else:
        match = LINE_REGEX.match(line)

        if not match:
            raise RuntimeError(f'No match for {line}')

        id = match.group(1)
        DESCRIPTIONS[id] = match.group(2)

        if comment_swap_next:
            COMMENTS[id] = next_comment
            comment_swap_next = False

import json
print(f"COMMENTS:\n\n{json.dumps(COMMENTS)}\n")
