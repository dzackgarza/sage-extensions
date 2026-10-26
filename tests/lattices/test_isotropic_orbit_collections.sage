r"""Orbits of primitive isotropic lines of the hyperbolic plane ``U``.

The primitive isotropic lines of ``U`` are ``ZZ e`` and ``ZZ f``.  ``O(U) =
{+-1, +-swap}`` exchanges them; ``SO(U) = {+-1}`` fixes each.
"""

from sage_extensions.all import *


def test_O_U_acts_transitively_on_the_primitive_isotropic_lines_of_U() -> None:
    lattice = Lattices(ZZ)("U")

    assert lattice.O().isotropic_orbit_representatives(1).cardinality() == 1


def test_SO_U_has_two_orbits_on_the_primitive_isotropic_lines_of_U() -> None:
    lattice = Lattices(ZZ)("U")

    assert lattice.SO().isotropic_orbit_representatives(1).cardinality() == 2
