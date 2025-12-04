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
can
can't
come
could
date
day
do
did
even
find
first
for
from
get
got
give
go
had
has
have
he
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
see
sent
she
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
were
what
when
where
which
who
will
with
won't
would
year
you
your
""".strip().split()

OTHER_COMMON_WORDS = """
    january february march april may june july august september october november december
    jan feb mar apr jun jul aug sep oct nov dec
    nd th rd st
    addthis attachments
    bcc
    cc
    contenttransferencoding
    dont
    email epstein
    fwd
    im iphone iPad BlackBerry
    jeffrey
    jr
    mr mrs
    over
    rss
    snipped signature
    sunday monday tuesday wednesday thursday friday saturday
    sun mon tues wed thur thurs fri sat
    trimmed
    whether wrote
""".strip().split()

COMMON_WORDS = {line.lower(): True for line in (MOST_COMMON_WORDS + OTHER_COMMON_WORDS)}
COMMON_WORDS_LIST = sorted([word for word in COMMON_WORDS.keys()])

UNSINGULARIZABLE_WORDS = """
    aids alas angeles anomalous anus apropos ares asus
    betts bias bonus brookings
    cbs cds carlos caucus chris clothes cms collins courteous curves cvs cyprus
    denis des dis drougas dubious
    emirates ens
    ferris folks francis
    gas gaydos
    halitosis has hillis his hivaids
    impetus innocuous ios irs isis
    jános josephus
    las lens les lewis lhs lls los
    madars maldives mbs mets meyers moonves
    nautilus nas notorious nous nucleus nunes
    olas outrageous
    pants parkes pbs physics pls prevus
    reis-dennis reuters rogers
    saks ses sous
    texas this thus tous trans tremendous tries
    ups
    vicious vinicius vous
    was whoops
    yes
""".strip().split()


if is_debug:
    word_str = '\n'.join(COMMON_WORDS_LIST)
    print(f"common words:\n\n{word_str}")
