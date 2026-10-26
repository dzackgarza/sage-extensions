r"""Archive reconciliation for quadratic versus bilinear 2-adic symmetries.

For the discriminant form of the rank-one lattice ``<8>``, the underlying
group is ``ZZ/8``.  Every unit whose square is one modulo eight preserves the
bilinear pairing, while preserving the quadratic refinement cuts the group to
``{+1,-1}``.  Thus the bilinear and quadratic orthogonal groups have orders
four and two respectively.  This is the rank-one case recorded in the
Miranda--Morrison 2-adic form rules used by the archived suite.
"""

from sage_extensions.all import *


def test_rank_one_2adic_quadratic_refinement_cuts_the_orthogonal_group_in_half() -> None:
    lattice = Lattices(ZZ)([[ZZ(8)]])
    quadratic = lattice.discriminant_group()
    bilinear = quadratic.associated_bilinear_form()

    assert tuple(quadratic.invariants()) == (ZZ(8),)
    assert tuple(bilinear.invariants()) == (ZZ(8),)
    assert quadratic.brown_invariant() == 1
    assert quadratic.automorphism_group().order() == 2
    assert bilinear.automorphism_group().order() == 4
