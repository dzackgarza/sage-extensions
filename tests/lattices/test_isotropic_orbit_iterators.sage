r"""Duplicate-free orbit iterators by Hermite normal form.

The primitive null lines of U are Ze and Zf. O(U) exchanges them and SO(U)={+-1}
fixes each: one O-orbit and two SO-orbits, both met at height one.
"""

from sage_extensions.all import *


def test_null_lines_of_u_under_o_and_so():
    ambient = Lattices(ZZ)("U")
    assert len(tuple(ambient.O().isotropic_orbit_iterator(1, height_bound=1))) == 1
    assert len(tuple(ambient.SO().isotropic_orbit_iterator(1, height_bound=1))) == 2
