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
has
have
having
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
went
were
what
when
where
which
who
why
will
with
without
wont
would
year
you
your
youre
""".strip().split()

OTHER_COMMON_WORDS = """
    january february march april may june july august september october november december
    jan feb mar apr jun jul aug sep oct nov dec
    sunday monday tuesday wednesday thursday friday saturday
    sun mon tues wed thur thurs fri sat
    nd th rd st skrev

    addthis attachments
    bcc
    cc
    contenttransferencoding
    date de des dont
    el email epstein et
    fwd
    id im iphone iPad BlackBerry
    jeffrey jr
    le les
    mr mrs ms much
    nor
    ou over
    rss
    sent snipped signature
    tenu trimmed
    via vous
    was wasnt whether while wrote
""".strip().split()

COMMON_WORDS = {line.lower(): True for line in (MOST_COMMON_WORDS + OTHER_COMMON_WORDS)}
COMMON_WORDS_LIST = sorted([word for word in COMMON_WORDS.keys()])

UNSINGULARIZABLE_WORDS = """
    aids alas always angeles anomalous anus apropos ares asus
    betts bias bonus brookings
    carlos caucus cbs cds ce cel chris clothes cms collins courteous curves cvs cyprus
    dallas denis des dis drougas dubious
    each emirates ens
    famous ferris folks francis
    gas gaydos
    halitosis has hillis his hivaids
    impetus innocuous ios irs isis
    jános josephus
    las lens les let lewis lhs lls los
    madars maldives mbs mets meyers moonves
    nautilus nas ne notorious nous nucleus nunes
    olas outrageous
    pants parkes pbs physics pls potus prevus
    reis-dennis reuters rogers
    saks sent ses sous
    tel texas this thus tous trans tremendous tries
    ups
    via vicious vinicius vis vous
    was whoops
    yes
""".strip().split()


if is_debug:
    word_str = '\n'.join(COMMON_WORDS_LIST)
    print(f"common words:\n\n{word_str}")
