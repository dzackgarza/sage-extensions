r"""A derived family is computed on its first request, cached, and reused.

The Schreier family of a pointed finite orbit is derived data: it is read off the
``G``-set's action and the section of its orbit, and two requests that name the
same point name the same datum.  Recomputation is not free -- the family is one
composite per orbit point and letter, and its sections are realized on the way --
so the library computes it once and answers every later request from the cache.
The datum a cached method returns is the one it returned before, which is what
the tests here ask: not a value equal to the last one, but that one.
"""

from sage_extensions.all import *


def _transpositions():
    r"""The three transpositions of S(3), which conjugation permutes transitively."""
    group = Groups.S(3)
    return group((1, 2)), group((1, 3)), group((2, 3))


def _conjugation_action(element, point):
    r"""S(3) acting on its three transpositions by conjugation."""
    return element * point * ~element


def test_the_family_of_a_point_is_one_datum_per_point() -> None:
    r"""Two requests for the family of a point are one computation.

    The orbit of ``(1 2)`` under conjugation is all three transpositions, so the
    family is six composites over the two selected letters.  Both the morphism
    and the letters-and-transversals pair it is read from are asked twice, and
    each pair of requests must be the same object: a second request answered by
    computing again is the same value twice over, not one datum.
    """
    group = Groups.S(3)
    point = _transpositions()[0]
    g_set = FiniteGSets(group).from_finite_orbits((point,), _conjugation_action)

    assert g_set.orbit_schreier_morphism(point) is g_set.orbit_schreier_morphism(point)
    assert g_set.orbit_schreier_factors(point) is g_set.orbit_schreier_factors(point)


def test_the_family_of_a_coset_space_is_one_datum() -> None:
    r"""``S(3)/<(1 2)>``: the family and its trimmed form are each computed once.

    The coset space's family has six members over the two selected letters, and
    its trimmed form drops the trivial images.  Asking for either twice, and
    asking for the full family with its default written out, must answer with the
    datum already computed: the trim is a different request, so it is a different
    datum, and it too is computed once.
    """
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    cosets = group.left_cosets(subgroup)

    assert cosets.schreier_generating_morphism() is cosets.schreier_generating_morphism()
    assert cosets.schreier_generating_morphism(
        drop_trivial=True
    ) is cosets.schreier_generating_morphism(drop_trivial=True)
    assert cosets.schreier_generating_morphism() is cosets.schreier_generating_morphism(
        drop_trivial=False
    )
