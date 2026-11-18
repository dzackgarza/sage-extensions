r"""A subspace carries the initial topology along its inclusion.

The induced topology on a subset ``S`` of a space ``X`` is the one whose opens are the
preimages of the opens of ``X`` (Mathlib, ``TopologicalSpace.induced``: the coarsest
topology making the inclusion continuous).  For an injective inclusion a subset ``V`` of
``S`` is open exactly when ``V`` is ``f^{-1}(U)`` for some open ``U`` of ``X``; the largest
candidate is ``f(V)`` together with everything outside the image of ``S``, which no preimage
can see.

The specimen is the Sierpinski space ``X = {0, 1, 2}`` with opens ``{}, {2}, {1}, {1,2},
{0,1,2}`` and the subset ``{0, 1}`` included by ``0 |-> 0`` and ``1 |-> 1``.  The preimages of
those opens are ``{}, {}, {1}, {1}, {0,1}``, so the subspace's opens are ``{}, {1}, {0,1}``:
the whole subspace is open -- it is the preimage of ``X`` itself -- and ``{0}`` is not,
although ``{0, 1}`` is a subset of ``X``'s point set.
"""

from sage_extensions.all import *


def _the_sierpinski_space():
    r"""``{0, 1, 2}`` with the opens ``{}, {2}, {1}, {1,2}, {0,1,2}``."""
    return TopologicalSpaces()((0, 1, 2), ((), (2,), (1,), (1, 2), (0, 1, 2)))


def test_the_opens_of_a_subspace_are_the_preimages_of_the_opens_of_its_space() -> None:
    r"""The inclusion selects three of the four subsets, and the fourth is not open.

    The subspace is ``{0, 1}`` by the map ``0 |-> 0``, ``1 |-> 1``.  Its whole set is open
    because it is the preimage of the ambient space, ``{1}`` is open because it is the
    preimage of ``{1}``, and ``{0}`` is not open because no open set of the ambient space
    pulls back to it.
    """
    ambient = _the_sierpinski_space()
    subset = TopologicalSpaces()((0, 1), ((), (1,), (0, 1)))
    inclusion = TopologicalSpaces().Mor(subset, ambient)(
        lambda point: ambient(1) if point == subset(1) else ambient(0)
    )

    space, into = TopologicalSpaces().subspace(inclusion)

    assert space in TopologicalSpaces()
    assert into.domain() is space
    assert into.codomain() is ambient
    assert into(space(1)) == ambient(1)
    assert into(space(0)) == ambient(0)

    power = space.power_set()
    assert space.is_open_subset(power(()))
    assert space.is_open_subset(power((space(0), space(1))))
    assert space.is_open_subset(power((space(1),)))
    assert not space.is_open_subset(power((space(0),)))


def test_a_one_point_subspace_of_a_sierpinski_space_keeps_the_opens_its_image_has() -> None:
    r"""The point at the closed point is a subspace of one point, and it is open.

    A one-point space has two subsets, and the empty one is open in every topology.  The
    whole one is open here because it is the preimage of the ambient space; the inclusion
    is continuous, so nothing else is asked of it.
    """
    ambient = TopologicalSpaces()((0, 1), ((), (1,), (0, 1)))
    point = TopologicalSpaces().terminal_object()
    inclusion = TopologicalSpaces().Mor(point, ambient)(lambda p: ambient(0))

    space, into = TopologicalSpaces().subspace(inclusion)

    assert space.cardinality() == 1
    assert into(space(0)) == ambient(0)
    assert space.is_open_subset(space.power_set()(()))
    assert space.is_open_subset(space.power_set()((space(0),)))
