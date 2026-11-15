r"""A point supplied to `Torsors.from_trivialization` is the point the torsor returns.

`Torsors.from_trivialization` states the contract: the point that defines the trivialization, when
the caller already holds it, is retained rather than evaluated through the group identity a second
time, and `base_point` answers with that datum. The point is a datum of the torsor -- the group, the
trivialization and the selected point are all fixed at construction -- so what the caller supplied
is what every read returns.
"""

from sage_extensions.all import *


def _regular_torsor_trivialization(group):
    r"""A trivialization of the regular ``G``-set, and the point it is defined at.

    The regular set ``G`` acted on by left multiplication is a ``G``-torsor, and ``g |-> g x`` is
    a set isomorphism ``G -> G`` whose inverse carries ``y`` to the unique ``g`` with ``g x = y``.
    That pair is the trivialization, and ``x`` is its point: the image of the identity, which is
    what `Torsors.from_trivialization` retains.
    """
    elements = tuple(group)
    points = FiniteGSets(group)(elements, lambda g, x: g * x)
    chosen = points(elements[1])
    forward = Sets().Mor(group, points)(lambda g: points(g * elements[1]))
    backward = Sets().Mor(points, group)(
        lambda y: next(g for g in group if points(g * elements[1]) == y)
    )
    return group, points, Sets().Core().Mor(group, points)(forward, inverse=backward), chosen


def test_a_supplied_trivialization_point_is_returned_as_supplied() -> None:
    r"""``from_trivialization(T, base_point=p).base_point() is p``, for the ``p`` the caller holds.

    The identity assertion is the contract, not an equality of points: the object supplied is the
    object returned. The trivialization is still the one whose image of the identity is that point,
    so the datum supplied is the datum the torsor would otherwise have computed.
    """
    group, points, trivialization, chosen = _regular_torsor_trivialization(Groups.C(3))
    torsor = Torsors(group).from_trivialization(trivialization, base_point=chosen)

    assert trivialization(group.one()) == chosen
    assert torsor.base_point() is chosen
    assert torsor.base_point() is torsor.base_point()
