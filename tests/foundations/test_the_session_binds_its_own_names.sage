r"""The session publishes the names its own source binds.

``sage_extensions.all`` is the session's definition, so a name is a session name
because a statement of the module puts it there: a star import of the area
package that declares it, an assignment, a definition, or the module's own
``_lazy_import`` re-export.  A name whose only route into the module is a
function of another module writing into the module's namespace gives the session
a name a reader of ``all.py`` cannot find, and gives that function the power to
change what the session publishes.  The six scalar rings ``ZZ``, ``QQ``, ``AA``,
``QQbar``, ``RDF`` and ``CDF`` were bound that way, and the research dialect was
installed the same way, reading the session's namespace to learn the vocabulary
its lowerings resolve.

The other two questions are the mathematics that installation must not trade
away: each scalar ring name denotes the ring it names, and the dialect's names
are the owned constructors.  ``TL01`` and ``TL03`` give a test the session's
names and nothing else, so the first question is asked through
``tests/foundations/conftest.py``'s ``names_the_session_does_not_bind``.

Source: Sage's ``import *`` binds ``__all__`` (Python Reference, "The import
statement"), and ``AA`` is the real closure of ``QQ`` in ``RR`` while ``QQbar``
is the algebraic closure of ``QQ`` (Lang, *Algebra*, XII §4).
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_every_session_name_is_bound_by_a_statement_of_the_module() -> None:
    r"""No public name of the session arrives from outside the module's own text.

    The residue is empty when every name the session publishes is the module's:
    an area's declaration reached the session through the star import that binds
    that area's ``__all__``, and everything else is a statement written in
    ``all.py``.
    """
    assert names_the_session_does_not_bind() == ()


def test_the_scalar_ring_names_denote_the_rings_they_name() -> None:
    r"""``AA`` holds the real root of ``2``, ``QQbar`` the root of ``-1``, and the rest answer as rings.

    ``sqrt 2`` in ``AA`` is a real number squaring to ``2``; ``QQbar`` contains
    ``i`` with ``i^2 = -1``, which has no square root in the ordered field
    ``RR``; ``RDF`` and ``CDF`` are the double fields, and ``QQ`` is the
    fraction field of ``ZZ``.  A scalar
    ring reachable from outside the module's text is a ring whose binding the
    module does not state, which is the defect above in the session's own
    vocabulary.
    """
    root_two = AA(2).sqrt()

    assert root_two**2 == 2
    assert root_two > 0
    assert QQbar(-1).sqrt() ** 2 == -1
    assert RDF(4).sqrt() ** 2 == 4
    assert CDF(2) + CDF(3) == CDF(5)
    assert Integer(2) in ZZ
    assert (QQ(2) ** -1) * QQ(2) == 1


def test_the_dialect_names_are_the_owned_constructors() -> None:
    r"""``Integer``, ``RealNumber``, ``matrix`` and ``factorial`` build owned objects.

    The dialect's names are what a lowered session script resolves, so they are
    the session's own objects: an integer literal is an element of ``ZZ``, a
    decimal-free rational is exact, and the matrix constructor builds a matrix
    over the ring its entries lie in, with the identity acting as one.
    """
    identity = matrix([[1, 0], [0, 1]])
    entries = matrix([[1, 2], [3, 4]])

    assert Integer("7") + Integer(1) == 8
    assert Integer("7") in ZZ
    assert RealNumber("1/3") * 3 == 1
    assert entries * identity == entries
    assert factorial(5) == 120
    assert {1..4}.cardinality() == 4
