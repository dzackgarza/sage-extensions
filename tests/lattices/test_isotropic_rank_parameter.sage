r"""The rank of an isotropic marking is an integer index independent of the coefficient ring."""

import pytest

from sage_extensions.all import *


def test_a_positive_definite_line_has_no_positive_rank_isotropic_marking():
    r"""For q(x)=2x squared, an isotropic vector is zero and is not primitive."""
    lattice = Lattices(ZZ)([[2]])
    for rank in (1, 2):
        assert lattice.Aut().isotropic_orbit_representatives(rank).cardinality() == cardinal(0)


def test_a_fractional_rank_does_not_define_an_isotropic_marking():
    lattice = Lattices(ZZ)([[2]])
    with pytest.raises(TypeError):
        lattice.Aut().isotropic_orbit_representatives(QQ(1) / QQ(2))
