r"""The cyclic module $\mathbb Z_2/(6)$ over the $2$-adic integers.

$3$ is a unit of $\mathbb Z_2$, so $\mathbb Z_2/(6) = \mathbb Z_2/(2) \cong \mathbb F_2$:
a torsion module of projective dimension one, with
$\operatorname{Tor}_1(\mathbb F_2, \mathbb F_2) = \mathbb F_2$ and
$\operatorname{Ext}^1(\mathbb F_2, \mathbb Z_2) = \mathbb Z_2/2$ (Weibel,
*An Introduction to Homological Algebra*, 3.1 and 4.1).
"""

from sage_extensions.all import *  # noqa: F401,F403


def two_adic_mod_6():
    R = Zp(2)
    return R, Modules(R)(R.quotient_ring(R.ideal(6)))


def test_z2_mod_6_is_z2_mod_2_a_torsion_module_of_projective_dimension_one() -> None:
    R, M = two_adic_mod_6()
    assert M.cardinality() == 2
    assert M.is_torsion()
    assert M.annihilator() == R.ideal(2)
    assert M.projective_dimension() == 1


def test_in_z2_mod_6_the_generator_is_nonzero_killed_by_2_and_tor1_has_two_elements() -> None:
    R, M = two_adic_mod_6()
    g = M.module_generator(0)
    assert g != M.zero()
    assert 6 * g == M.zero()
    assert 2 * g == M.zero()
    assert 3 * g == g
    assert M.tor(M, 1).cardinality() == 2


def test_z2_mod_6_has_a_length_one_resolution_and_ext1_into_z2_of_order_two() -> None:
    R, M = two_adic_mod_6()
    resolution = M.free_resolution(2)
    assert resolution.length() == 1
    assert resolution.is_exact()
    assert M.ext(R.regular_module(), 1).cardinality() == 2
    assert M.ext(R.regular_module(), 0).is_zero()
