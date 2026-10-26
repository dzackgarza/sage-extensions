r"""The integral cohomology of `PGL_2`, the complement of the quadric `ad - bc = 0` in `\mathbb{P}^3`.

Source: `PGL_2(\mathbb{C})` deformation retracts onto `PU(2) \cong SO(3) \cong
\mathbb{RP}^3`, whose integral cohomology is `\mathbb{Z}, 0, \mathbb{Z}/2, \mathbb{Z}`
in degrees 0 to 3 (Hatcher, *Algebraic Topology*, Example 3.8).
"""

from sage_extensions.all import *


def _pgl2():
    space = ProjectiveSpaces(QQ)(3)
    a, b, c, d = space.homogeneous_coordinate_generators()
    return space.distinguished_open(a * d - b * c)


def test_pgl2_has_integral_cohomology_z_0_z2_z_0() -> None:
    pgl2 = _pgl2()

    assert pgl2.integral_cohomology(0).module_rank() == 1
    assert pgl2.integral_cohomology(1).module_rank() == 0
    assert pgl2.integral_cohomology(2).cardinality() == 2
    assert pgl2.integral_cohomology(3).module_rank() == 1
    assert pgl2.integral_cohomology(4).module_rank() == 0


def test_rational_cohomology_of_pgl2_loses_the_two_torsion() -> None:
    r"""`H^2(PGL_2, \mathbb{Q}) = \mathbb{Z}/2 \otimes \mathbb{Q} = 0`, while
    `H^3(PGL_2, \mathbb{Q}) = \mathbb{Q}`."""
    pgl2 = _pgl2()

    assert pgl2.rational_cohomology(2).is_zero()
    assert pgl2.rational_cohomology(3).dimension() == 1
