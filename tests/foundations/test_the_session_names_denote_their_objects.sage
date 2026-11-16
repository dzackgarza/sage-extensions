r"""A session name denotes its object, in every position it is written.

``ZZ``, ``QQ``, ``AA``, ``QQbar``, ``RDF`` and ``CDF`` are session names because
``sage_extensions.rings`` declares them, and each denotes the one owned ring of
its name.  The preamble's categories are what separates the two objects a session
could publish under one of these spellings: the host's integer ring is not in
``Rings()``, ``PrincipalIdealDomains()`` or ``Fields()``, because those
categories hold preamble rings, so a name that resolved to the host's ring would
answer ``False`` to every membership below while still adding, multiplying and
inverting.  The algebra is asserted beside the membership for that reason: the
membership says whose object the name denotes, the algebra says what it is.

The dialect's own names follow the same rule.  ``Integer`` builds an element of
``ZZ``, ``RealNumber`` an element of ``RR``, ``matrix`` a matrix over the ring
its entries lie in, ``factorial`` an element of ``ZZ``, and the brace range is a
set — the research lowerings are installed and the names they emit resolve.

The third test reads a name in the position where the question is sharpest: an
index.  ``Sets.Δ[aleph0]`` is the set of cardinality ``aleph0``, because
``aleph0`` is a name the session supplies.  The research dialect reads
``R = A[x]`` as a generator declaration whenever the file binds ``x`` nowhere,
and a file that star-imports the session binds the session's names without
contributing an identifier to that scan; so this is the position where a session
name is most likely to be taken for a new one, and where taking it for a new one
would rebuild ``aleph0`` as a generator of the set construction.

Source: ``AA`` is the real closure of ``QQ`` inside ``RR`` and ``QQbar`` the
algebraic closure of ``QQ`` (Lang, *Algebra*, XII §4).
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_every_scalar_ring_name_denotes_the_owned_ring_of_that_name() -> None:
    r"""Each scalar name is the preamble's ring of that name, with the algebra that names it.

    ``ZZ`` is a principal ideal domain, the five fields are fields, and
    ``AA(2).sqrt()`` is the positive real root of ``2``; ``QQbar`` holds the root
    of ``-1``, which the ordered field ``RR`` lacks; ``RDF`` and ``CDF`` are the
    double fields, and ``QQ`` inverts its own elements.
    """
    assert ZZ in PrincipalIdealDomains()
    assert QQ in Fields()
    assert AA in Fields()
    assert QQbar in Fields()
    assert RDF in Fields()
    assert CDF in Fields()

    root_two = AA(2).sqrt()
    assert root_two**2 == 2
    assert root_two > 0
    assert QQbar(-1).sqrt() ** 2 == -1
    assert RDF(4).sqrt() ** 2 == 4
    assert CDF(2) + CDF(3) == CDF(5)
    assert Integer(2) in ZZ
    assert QQ(2) ** -1 * QQ(2) == 1


def test_the_dialect_names_build_owned_elements() -> None:
    r"""``Integer``, ``RealNumber``, ``matrix``, ``factorial`` and ``{1..4}`` build session objects.

    An integer literal is an element of ``ZZ``, a written fraction is exact, the
    matrix constructor builds a matrix over the ring its entries lie in with the
    identity acting on it, and the brace range is a four-element set.
    """
    identity = matrix([[1, 0], [0, 1]])
    entries = matrix([[1, 2], [3, 4]])
    four = {1..4}

    assert Integer("7") in ZZ
    assert Integer("7") + 1 == 8
    assert RealNumber("1/3") * 3 == 1
    assert entries * identity == entries
    assert entries[0, 1] == 2
    assert factorial(5) == 120
    assert four.cardinality() == 4
    assert 3 in four


def test_a_session_name_in_an_index_is_the_object_it_names() -> None:
    r"""``Sets.Δ[aleph0]`` is the set of cardinality ``aleph0``.

    The index is a session name, so the set is countable rather than carrying a
    fresh indeterminate called ``aleph0``, and its own cardinality says so.
    """
    countable = Sets.Δ[aleph0]

    assert countable.cardinality() == aleph0
    assert countable.power_set().cardinality() > aleph0
