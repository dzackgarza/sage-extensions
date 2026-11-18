r"""The singular integral-affine space as the selection of a locus and an affine complement.

A singular integral-affine space is a real surface with an integral-affine structure off a
finite set of points, where the structure degenerates to a cone of angle larger than
``2 pi``: the local model at a singular point is the cone on a circle of length
``2 pi n`` (Alexeev--Engel, *Compactifications of moduli spaces of K3 surfaces with a
nonsymplectic involution*, arXiv:2208.10383v2, Definition 6.11, p. 30, for the
integral-affine structure, and Construction 6.16, pp. 31--32, for the cutting and regluing
along the moment polygon).  The object therefore carries four
data and no more: the space, the singular locus in it, the regular part's inclusion, and
the integral-affine manifold on that regular part.

The specimen below separates them.  The ambient space is the two-point Sierpinski space
``{s < r}``; its singular locus is the one-point space at ``s`` and its regular part is the
plane, carried into the space by the constant map at ``r``, whose preimages are ``{s, r}``
and the empty set -- both open.  The plane's integral-affine atlas is the one an earlier
test builds: one chart, the identity inclusion and the identity chart into the model.

The values of the atlas' maps at points of the manifold are not asserted, for the reason
that test states: a point of a real smooth manifold cannot be built in this tree.  What is
asserted is that the selection retains the exact four objects and no reconstruction of
them, and that a selection into a space that is not the ambient space is refused.
"""

from sage_extensions.all import *

import pytest


def _the_plane_and_its_affine_manifold():
    r"""The plane's one-chart integral-affine structure and the manifold it presents."""
    lattice = ZZ.free_module(2)
    plane = SmoothManifolds()(2, "R^2")
    model = RR.free_module(lattice.module_generating_set())
    atlas = IntegralAffineAtlases().on(
        plane,
        model,
        {plane: plane},
        {plane: Sets().Mor(plane, plane).identity()},
        {plane: Sets().Mor(plane, model)(lambda point: model(tuple(point.coordinates())))},
        {},
        {},
    )
    return plane, IntegralAffineManifolds().on(plane, atlas)


def test_the_singular_affine_space_retains_its_locus_selection() -> None:
    r"""The four selected data are the four the object answers, object for object.

    The ambient space is ``{s < r}`` with the opens ``{}, {r}, {s, r}``; the singular locus
    is the one-point space at ``s``; the regular part is the plane, mapped to ``r``; and the
    affine structure on it is the plane's own.  The space reports that curve, that regular
    part and that manifold, and its two locus accessors answer the two inclusions' domains
    and the affine manifold itself.
    """
    plane, manifold = _the_plane_and_its_affine_manifold()
    ambient = TopologicalSpaces()((0, 1), ((), (1,), (0, 1)))
    singular_point = TopologicalSpaces().terminal_object()
    singular_inclusion = TopologicalSpaces().Mor(singular_point, ambient)(
        lambda point: ambient(0)
    )
    regular_inclusion = TopologicalSpaces().Mor(plane, ambient)(lambda point: ambient(1))

    space = SingularIntegralAffineSpaces().on(
        ambient, singular_inclusion, regular_inclusion, manifold
    )

    assert space in SingularIntegralAffineSpaces()
    assert space.underlying_topological_space() is ambient
    assert space.singular_locus_inclusion() is singular_inclusion
    assert space.regular_locus_inclusion() is regular_inclusion
    assert space.regular_affine_manifold() is manifold
    assert space.singular_locus() is singular_point
    assert space.regular_locus() == (regular_inclusion, manifold)
    assert space.singular_locus_inclusion().codomain() is ambient
    assert space.regular_locus_inclusion().codomain() is ambient


def test_a_selection_into_another_space_is_refused() -> None:
    r"""A locus selected into a different space is refused, not re-homed.

    The regular part's map below is the plane's identity, whose codomain is the plane, not
    the ambient two-point space: an integral-affine structure is added to the part the
    space carries, so the object has no authority to move that part into another space
    (``OWN-15``).
    """
    plane, manifold = _the_plane_and_its_affine_manifold()
    ambient = TopologicalSpaces()((0, 1), ((), (1,), (0, 1)))
    singular_point = TopologicalSpaces().terminal_object()
    singular_inclusion = TopologicalSpaces().Mor(singular_point, ambient)(
        lambda point: ambient(0)
    )
    regular_inclusion = TopologicalSpaces().Mor(plane, ambient)(lambda point: ambient(1))
    elsewhere = Sets().Mor(plane, plane).identity()

    with pytest.raises(AssertionError):
        SingularIntegralAffineSpaces().on(
            ambient, elsewhere, regular_inclusion, manifold
        )
    with pytest.raises(AssertionError):
        SingularIntegralAffineSpaces().on(
            plane, singular_inclusion, regular_inclusion, manifold
        )
