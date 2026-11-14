r"""Transport of a primitive null plane in `2U` retains its parabolic structure.

A lattice isometry carries a primitive isotropic subobject to a primitive
isotropic subobject of its codomain.  At a split plane, the parabolic block
construction applies to that transported object itself, not merely to the
source plane.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_null_plane_transport_retains_its_split_parabolic() -> None:
    r"""Swap two hyperbolic planes and use the parabolic at the transported plane."""
    hyperbolic = Lattices(ZZ)("U")
    lattice = hyperbolic + hyperbolic
    basis = tuple(lattice.module_generators())
    plane = lattice.primitive_isotropic_subobject(basis[0], basis[2])
    labels = tuple(lattice.module_generating_set())
    images = (basis[2], basis[3], basis[0], basis[1])
    swap = lattice.Aut()(dict(zip(labels, images, strict=True)))

    transported = swap.transport_isotropic_object(plane)

    assert transported.is_parabolic_complete() is True
    assert all(
        transported.inclusion().is_in_image(swap(plane.inclusion()(point)))
        for point in plane.module_generators()
    )
    assert all(
        plane.inclusion().is_in_image((~swap)(transported.inclusion()(point)))
        for point in transported.module_generators()
    )
