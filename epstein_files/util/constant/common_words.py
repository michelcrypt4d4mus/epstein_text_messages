from epstein_files.util.env import is_debug

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
    dont
    did
    didnt
    even
    find
    first
    for
    from
    get
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
    sent si signature smtp snipped
    te tel tenu tho though trimmed
    via vous voye
    was wasnt whether while wrote
""".strip().split()

COMMON_WORDS = {line.lower(): True for line in (MOST_COMMON_WORDS + OTHER_COMMON_WORDS)}
COMMON_WORDS_LIST = sorted([word for word in COMMON_WORDS.keys()])

UNSINGULARIZABLE_WORDS = """
    acosta aids alas always angeles anomalous anus apropos arabia ares asia asus atlanta australia ave avia
    bata betts bias bonus brookings
    california campus candia carlos caucus cbs cds chris clothes cms collins columbia conchita costa courteous curves cvs cyprus
    dallas data davis dementia denis dennis des dis drougas dubious
    emirates encyclopedia ens eps
    famous ferris focus folks forbes francis frivolous
    gas gaydos gmt gps
    halitosis has hillis his hivaids
    impetus innocuous india indonesia ios ips irs isis
    jános josephus
    las lens les lewis lhs lls los louis luis
    madars maldives maria mbs melania mets meyers moonves
    nafta nautilus nas nigeria notorious nous nucleus nunes
    olas outrageous
    pants parkes patricia pbs peres philadelphia physics pls plus potus prevus
    reis-dennis reuters rogers russia
    sach sadis saks santa ses sous stimulus syria
    texas this thus tous trans tremendous tries
    ups
    valeria versus via vicious victoria villafaria vinicius virginia vis vous
    was whoops wikipedia
    yemen yes yikes
    zakaria
""".strip().split()


if is_debug:
    word_str = '\n'.join(COMMON_WORDS_LIST)
    print(f"common words:\n\n{word_str}")
