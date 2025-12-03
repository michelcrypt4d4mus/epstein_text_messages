from epstein_files.util.env import is_debug

# https://www.gonaturalenglish.com/1000-most-common-words-in-the-english-language/
WORDS_LIST = """
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

OTHER_WORDS = """
attachments
email
epstein
fwd
im
iphone iPad BlackBerry
january february march april may june july august september october november december
jan feb mar apr jun jul aug sep oct nov dec
jeffrey
mr
nd th rd st
snipped signature
sunday monday tuesday wednesday thursday friday saturday
sun mon tues wed thur thurs fri sat
trimmed
wrote
""".strip().split()

COMMON_WORDS = {line.lower(): True for line in (WORDS_LIST + OTHER_WORDS)}


if is_debug:
    word_str = '\n'.join(sorted([k for k in COMMON_WORDS.keys()]))
    print(f"common words:\n\n{word_str}")
