r"""Counting monomorphisms, epimorphisms and automorphisms of small objects."""

from sage_extensions.all import *  # noqa: F401,F403


def test_injections_surjections_and_bijections_between_finite_sets() -> None:
    r"""``|Inj(2, 4)| = 4 * 3 = 12``, ``|Surj(4, 2)| = 2^4 - 2 = 14``, ``|Aut(2)| = 2``.

    In ``Sets`` the monomorphisms are the injections and the epimorphisms the
    surjections; a constant map on a two-point set is neither.
    """
    two = Sets()((0, 1))
    four = Sets()((0, 1, 2, 3))
    constant = two.Mor(two)(lambda _point: two(0))
    swap = two.Mor(two)(lambda point: two(1 - point))

    assert two.Mor(four).cardinality() == 16
    assert Sets().Mono(two, four).cardinality() == 12
    assert Sets().Epi(four, two).cardinality() == 14
    assert Sets().Aut(two).cardinality() == 2
    assert constant not in Sets().Mono(two, two)
    assert constant not in Sets().Epi(two, two)
    assert swap in Sets().Aut(two)
    assert swap * swap == two.Mor(two).identity()


def test_endomorphisms_and_automorphisms_of_the_cyclic_group_of_order_three() -> None:
    r"""``End(C3) = Z/3`` has 3 elements; ``Aut(C3) = (Z/3)^x`` is cyclic of order 2."""
    c3 = Groups.C(3)

    assert c3.End().cardinality() == 3
    assert c3.Aut().cardinality() == 2
    assert c3.Aut().is_isomorphic_to(Groups.C(2))


def test_the_rank_one_lattice_has_automorphism_group_plus_minus_one() -> None:
    r"""``O(<2>) = {+-1}``, and every self-embedding of ``<2>`` is an isometry.

    An isometric embedding ``<2> -> <2>`` sends the generator to a vector of
    norm 2, which is ``+-e``, so it is surjective.
    """
    lattice = Lattices(ZZ)([[2]])
    (e,) = lattice.basis()
    minus_one = lattice.Mor(lattice)({e: -e})

    assert lattice.O().cardinality() == 2
    assert minus_one in lattice.O()
    assert lattice.Emb(lattice).cardinality() == 2
