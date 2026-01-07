from epstein_files.util.env import args

# Removed: look, make, no, see, think, up, use, want
# https://www.gonaturalenglish.com/1000-most-common-words-in-the-english-language/
MOST_COMMON_WORDS = """
    a about after all also am an and any are as at
    be because been being but by
    came can can't cannot cant come could couldnt
    day do doing dont did didnt
    even
    find first for from
    get getting got give go going
    had hadnt has hasnt have havent having he hed her here him his how
    i if in into is isnt it its ive
    just
    know
    like
    man many me more my
    new not now
    of on one only or other our out
    people pm
    re
    said say saying says she shed so some subject
    take than that the their them then there these they theyd theyll theyre theyve thing this those through time to too two
    very
    was way we well went were werent weve
      what whatever when whenever where wherever which whichever who whoever why
      will with without wont would wouldnt wouldve
    year you youd youll your youre youve
""".strip().split()

OTHER_COMMON_WORDS = """
    january february march april may june july august september october november december
    jan feb mar apr jun jul aug sep sept oct nov dec
    sunday monday tuesday wednesday thursday friday saturday
    sun mon tue tues wed thu thur thurs fri sat
    st nd rd th skrev

    addthis attachments ave
    bcc bst btn
    cc ce cel
    date de des div dont du
    each ecrit edt el email en envoye epstein et
    fa fax fb fw fwd
    herself himself
    id ii iii im iphone iPad BlackBerry
    je jeffrey jr
    kl
    las le les let
    mr mrs ms much
    ne nonus nor
    ou over
    pdt pst
    rss
    sent ses si signature smtp snipped somers
    te tel tenu tho though trimmed
    via vous voye
    was wasnt whether while wrote
""".strip().split()

COMMON_WORDS = {line.lower(): True for line in (MOST_COMMON_WORDS + OTHER_COMMON_WORDS)}
COMMON_WORDS_LIST = sorted([word for word in COMMON_WORDS.keys()])

UNSINGULARIZABLE_WORDS = """
    abbas academia acosta aids alas algeria alice always andres angeles anus apparatus apropos arabia ares asia asus atlanta australia austria avia
    bahamas bata beatles beta betts bias boies bonus brookings brussels
    california campus candia cannes carlos caucus cbs cds census chaos chorus chris christmas clothes cms collins columbia com comms conchita consensus costa csis curves cvs cyprus
    dallas data davis davos dawkins deborah dementia denis dennis des diabetes dis drougas
    emirates emphasis encyclopedia ens eps eta
    facs ferris focus folks forbes francis
    gas gaydos georgia gittes gloria gmt gps gravitas
    halitosis hamas harris has hiatus hillis his hivaids hopkins
    impetus india indonesia ios ips irs isis isosceles
    jacques jános jones josephus jules
    kansas
    las lens les lewis lhs lls los louis luis
    madars malaysia maldives marcus maria massachusetts mbs media melania meta mets meyers mlpf&s mongolia moonves multimedia
    nadia nafta natalie nautilus nas nigeria novartis nucleus nunes
    olas orleans
    pants paris parkes patricia pbs pennsylvania peres perhaps philadelphia physics pls plus potus pres prevus
    rees reis-dennis reuters rodgers rogers russia
    sachs sadis saks santa ses shia simmons slovakia sometimes soros stimulus surplus syria
    tennis texas this thus trans tries tunisia
    ups uterus
    valeria vegas versus via victoria villafaria vinicius virginia vis
    was whereas whoops wikipedia
    yemen yes yikes
    zakaria
""".strip().split()


# if args.deep_debug:
#     word_str = '\n'.join(COMMON_WORDS_LIST)
#     print(f"common words:\n\n{word_str}")
