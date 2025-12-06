from epstein_files.util.env import deep_debug

# https://www.gonaturalenglish.com/1000-most-common-words-in-the-english-language/
MOST_COMMON_WORDS = """
    a
    about
    after
    all
    also
    am
    an
    and
    any
    are
    as
    at
    be
    because
    been
    but
    by
    came
    can
    can't
    come
    could
    couldnt
    day
    do
    doing
    dont
    did
    didnt
    even
    find
    first
    for
    from
    get
    getting
    got
    give
    go
    going
    had
    hadnt
    has
    hasnt
    have
    havent
    having
    he
    hed
    her
    here
    him
    his
    how
    i
    if
    in
    into
    is
    it
    its
    ive
    just
    know
    like
    look
    make
    man
    many
    me
    more
    my
    new
    no
    not
    now
    of
    on
    one
    only
    or
    other
    our
    out
    people
    pm
    re
    said
    say
    saying
    says
    see
    she
    shed
    so
    some
    subject
    take
    than
    that
    the
    their
    them
    then
    there
    these
    they
    theyll
    theyve
    thing
    think
    this
    those
    through
    time
    to
    too
    two
    up
    use
    very
    want
    was
    way
    we
    well
    went
    were
    what
    whatever
    when
    whenever
    where
    wherever
    which
    whichever
    who
    why
    will
    with
    without
    wont
    would
    wouldnt
    wouldve
    year
    you
    youd
    youll
    your
    youre
    youve
""".strip().split()

OTHER_COMMON_WORDS = """
    january february march april may june july august september october november december
    jan feb mar apr jun jul aug sep oct nov dec
    sunday monday tuesday wednesday thursday friday saturday
    sun mon tues wed thur thurs fri sat
    st nd rd th skrev

    addthis attachments
    bcc bst btn
    cc ce cel
    date de des div dont du
    each ecrit edt el email en envoye epstein et
    fa fax fb fwd
    herself himself
    id ii iii im iphone iPad BlackBerry
    je jeffrey jr
    kl
    las le les let
    mr mrs ms much
    ne nor
    ou over
    pdt pst
    rss
    sent si signature smtp snipped somers
    te tel tenu tho though trimmed
    via vous voye
    was wasnt whether while wrote
""".strip().split()

COMMON_WORDS = {line.lower(): True for line in (MOST_COMMON_WORDS + OTHER_COMMON_WORDS)}
COMMON_WORDS_LIST = sorted([word for word in COMMON_WORDS.keys()])

UNSINGULARIZABLE_WORDS = """
    acosta aids alas always andres angeles anomalous anus apropos arabia ares asia asus atlanta australia ave avia
    bata betts bias boies bonus brookings
    california campus candia carlos caucus cbs cds census chris clothes cms collins columbia comms conchita costa courteous csis curves cvs cyprus
    dallas dangerous data davis dementia denis dennis des dis drougas dubious
    emirates emphasis encyclopedia enormous ens eps
    fabulous famous ferris focus folks forbes francis frivolous
    gas gaydos gittes gmt gorgeous gps
    halitosis hamas has hiatus hillis his hivaids
    impetus innocuous india indonesia ios ips irs isis
    jános jones josephus
    las lens les lewis lhs lls los louis luis
    madars maldives maria mbs melania mets meyers miscellaneous mlpf&s momentous moonves
    nafta nautilus nas nigeria notorious nous nucleus numerous nunes
    olas outrageous
    pants paris parkes patricia pbs peres philadelphia physics pls plus potus pres prevus
    reis-dennis reuters rogers russia
    sachs sadis saks santa ses sometimes sous stimulus syria
    tennis texas this thus tous trans tremendous tries
    ups
    valeria versus via vicious victoria villafaria vinicius virginia vis vous
    was whereas whoops wikipedia
    yemen yes yikes
    zakaria
""".strip().split()


if deep_debug:
    word_str = '\n'.join(COMMON_WORDS_LIST)
    print(f"common words:\n\n{word_str}")
