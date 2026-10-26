from sage_extensions.all import *


def _simple_roots(lattice):
    return Sets().Mor(lattice.module_generating_set(), lattice)(lattice.module_generator)


def test_the_two_automorphisms_of_the_a2_diagram_are_two_distinct_isometries() -> None:
    r"""``Aut`` of the ``A2`` Dynkin diagram is ``ZZ/2``, the stabilizer of the simple roots.

    ``|O(A2)| / |W(A2)| = 12 / 6 = 2`` (Humphreys, *Reflection Groups and
    Coxeter Groups*, 2.10 and the table of 2.11).
    """
    lattice = Lattices(ZZ)("A2")
    simple_roots = lattice.module_generators()
    stabilizer = lattice.O().stabilizer(_simple_roots(lattice))
    assert stabilizer.cardinality() == 2

    identity, swap = stabilizer
    assert identity != swap
    for isometry in (identity, swap):
        assert isometry in lattice.O()
        for left in simple_roots:
            for right in simple_roots:
                assert isometry(left).b(isometry(right)) == left.b(right)


def test_the_triality_group_of_the_d4_diagram_acts_faithfully_on_the_simple_roots() -> None:
    r"""``Aut`` of the ``D4`` diagram is ``S_3``: six elements of ``O(D4)`` permuting the simple roots.

    ``|O(D4)| / |W(D4)| = 1152 / 192 = 6`` (Humphreys, 2.10-2.11).  The family
    of simple roots is injective, so each element determines its permutation of
    the roots, and distinct elements give distinct permutations.
    """
    lattice = Lattices(ZZ)("D4")
    roots = _simple_roots(lattice)
    stabilizer = lattice.O().stabilizer(roots)
    assert stabilizer.cardinality() == 6

    representation = lattice.O().index_action(roots).permutation_representation()
    assert representation.kernel().cardinality() == 1
    assert representation.image().cardinality() == 6
