r"""Stable-group isotropic plane orbits on the rank-five Scattone shadow.

``L_1 = U + U + <-2>`` is the rank-five lattice with one orbit of primitive isotropic
planes.  The public operations must return this one orbit under the stable group and
under its positive-spinor intersection, not only under the full orthogonal group.

The failure this pins: evaluation of the discriminant stabilizer passes a raw engine
``GapElement`` into ``LatticeIsometryMor`` instead of converting it through the owned
row-action conversion.  Before repair, ``stable.isotropic_orbit_representatives(2)`` on
this specimen raises ``TypeError: cannot define a linear map ... from [ f1 ] -> [ f1 ]``.
That is a public-call defect of the owner, not a new mathematical statement about the line.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_stable_plane_orbit_of_l_1() -> None:
    r"""$L_1$: the stable group has one isotropic plane orbit, checked intrinsically."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    stable = lattice.stable_orthogonal_group()
    planes = stable.isotropic_orbit_representatives(2)

    assert planes.cardinality() == cardinal(1)
    for plane in planes:
        assert plane.module_rank() == cardinal(2)
        assert plane.is_primitive() is True


def test_stable_plus_has_the_same_l_1_plane_orbit() -> None:
    r"""The same card's $\widetilde{O}^+$ plane fibres of rank two must also be one orbit.

    Spinor and discriminant characters are joint here, so the route sees the complete
    joint image instead of deducing coverage from a sign only.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    stable_plus = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    planes = stable_plus.isotropic_orbit_representatives(2)

    assert planes.cardinality() == cardinal(1)
    for plane in planes:
        assert plane.module_rank() == cardinal(2)
        assert plane.is_primitive() is True
