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
    being
    but
    by
    came
    can
    can't
    cannot
    cant
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
    theyre
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
    werent
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
    jan feb mar apr jun jul aug sep sept oct nov dec
    sunday monday tuesday wednesday thursday friday saturday
    sun mon tue tues wed thu thur thurs fri sat
    st nd rd th skrev

    addthis attachments ave
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
    sent ses si signature smtp snipped somers
    te tel tenu tho though trimmed
    via vous voye
    was wasnt whether while wrote
""".strip().split()

COMMON_WORDS = {line.lower(): True for line in (MOST_COMMON_WORDS + OTHER_COMMON_WORDS)}
COMMON_WORDS_LIST = sorted([word for word in COMMON_WORDS.keys()])

UNSINGULARIZABLE_WORDS = """
    academia acosta aids alas algeria always andres angeles anus apparatus apropos arabia ares asia asus atlanta australia austria avia
    bahamas bata beatles betts bias boies bonus brookings
    california campus candia carlos caucus cbs cds census chaos chorus chris christmas clothes cms collins columbia com comms conchita costa csis curves cvs cyprus
    dallas data davis davos dementia denis dennis des dis drougas
    emirates emphasis encyclopedia  ens eps
    facs ferris focus folks forbes francis
    gas gaydos georgia gittes gloria gmt gps
    halitosis hamas harris has hiatus hillis his hivaids
    impetus india indonesia ios ips irs isis isosceles
    jacques jános jones josephus
    las lens les lewis lhs lls los louis luis
    madars malaysia maldives maria massachusetts mbs media melania mets meyers mlpf&s mongolia moonves multimedia
    nadia nafta nautilus nas nigeria novartis nucleus nunes
    olas orleans
    pants paris parkes patricia pbs pennsylvania peres perhaps philadelphia physics pls plus potus pres prevus
    rees reis-dennis reuters rodgers rogers russia
    sachs sadis saks santa ses shia simmons sometimes stimulus syria
    tennis texas this thus trans tries tunisia
    ups
    valeria vegas versus via victoria villafaria vinicius virginia vis
    was whereas whoops wikipedia
    yemen yes yikes
    zakaria
""".strip().split()


if deep_debug:
    word_str = '\n'.join(COMMON_WORDS_LIST)
    print(f"common words:\n\n{word_str}")
