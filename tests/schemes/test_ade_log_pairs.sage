r"""ADE log pairs: the toric surface the ADE polygon's normal fan gives.

The polygons are those of Alexeev--Thompson, *ADE surfaces and their moduli*,
Table 1.
"""

from sage_extensions.all import *


def test_the_a1_polygon_is_a_triangle_whose_toric_surface_is_the_projective_plane() -> None:
    r"""The \(A_1\) polygon is the triangle on \((0,2),(0,0),(2,0)\); its inner normal fan has rays
    \(e_1, e_2, -e_1-e_2\), the fan of \(\mathbf P^2\), whose Picard group has rank \(1\).
    With \(\Delta\) the full toric boundary, \(K_X + \Delta = 0\), so the pair is log Calabi--Yau.

    Source: Alexeev--Thompson, *ADE surfaces and their moduli*, Table 1; Cox--Little--Schenck,
    *Toric Varieties*, Thm. 8.2.3 (\(K_X = -\sum_\rho D_\rho\)).
    """
    pair = LogPairs(QQ)("A", 1)

    assert pair.polygon().vertices().cardinality() == 3
    assert pair.log_scheme().is_projective_space()
    assert pair.log_scheme().torus_invariant_divisor_group().module_generating_set().cardinality() == 3
    assert pair.log_scheme().picard_group().rank() == 1
    assert pair.is_log_calabi_yau()


def test_the_d4_polygon_is_a_square_whose_toric_surface_is_the_quadric() -> None:
    r"""The \(D_4\) polygon is the square \([0,2]^2\), whose normal fan is that of
    \(\mathbf P^1\times\mathbf P^1 = \mathbf F_0\): four rays, four invariant divisors, Picard rank \(2\).

    Source: Alexeev--Thompson, *ADE surfaces and their moduli*, Table 1; Cox--Little--Schenck,
    *Toric Varieties*, Thm. 4.2.1 (Picard rank of a smooth complete toric surface is #rays - 2).
    """
    pair = LogPairs(QQ)("D", 4)

    assert pair.polygon().vertices().cardinality() == 4
    assert pair.log_scheme().is_hirzebruch_surface(0)
    assert not pair.log_scheme().is_projective_space()
    assert pair.log_scheme().torus_invariant_divisor_group().module_generating_set().cardinality() == 4
    assert pair.log_scheme().picard_group().rank() == 2
