r"""Theta series to an explicit precision, and exact covolume, of definite lattices.

``theta_series(N)`` has exponent ``b(x, x)``, so its coefficient of
\(q^{2m}\) is \(r(m) = \#\{x : x \cdot x = 2m\}\), the coefficient of \(q^m\)
in the convention \(q^{x \cdot x / 2}\).

Values: Serre, *A Course in Arithmetic*, VII.6.6 (\(\theta_{E_8} = E_4 =
1 + 240\sum\sigma_3(m)q^m\)); Conway--Sloane, *Sphere Packings, Lattices and
Groups*, 4.6.1 (\(A_2\): \(1 + 6q + 6q^3 + 6q^4 + 12q^7 + \dots\)) and 1.2.4
(\(\det\) of the Gram matrix is the squared covolume).
"""

from sage_extensions.all import *


def test_e8_theta_series_is_the_weight_four_eisenstein_series_modulo_q_11() -> None:
    r"""\(240\sigma_3(m)\) for \(m = 1, \dots, 5\) is 240, 2160, 6720, 17520, 30240."""
    lattice = Lattices(ZZ)("E8").twist(-1)
    theta = lattice.theta_series(11)

    assert theta.precision_absolute() == 11
    assert [theta[2 * m] for m in range(6)] == [1, 240, 2160, 6720, 17520, 30240]
    assert [theta[2 * m + 1] for m in range(5)] == [0, 0, 0, 0, 0]


def test_a2_theta_series_counts_the_norms_of_the_eisenstein_integers() -> None:
    lattice = Lattices(ZZ)([[2, 1], [1, 2]])
    theta = lattice.theta_series(15)

    assert theta.precision_absolute() == 15
    assert [theta[2 * m] for m in range(8)] == [1, 6, 0, 6, 6, 0, 0, 12]


def test_covolume_is_the_exact_square_root_of_the_gram_determinant() -> None:
    a2 = Lattices(ZZ)([[2, 1], [1, 2]])
    e8 = Lattices(ZZ)("E8").twist(-1)

    assert a2.covolume() ** 2 == 3
    assert a2.covolume() != QQ(173) / 100
    assert e8.covolume() == 1


def test_scaling_the_form_by_c_scales_the_covolume_by_c_to_the_half_rank() -> None:
    a2 = Lattices(ZZ)([[2, 1], [1, 2]])
    e8 = Lattices(ZZ)("E8").twist(-1)

    assert a2.twist(3).covolume() == a2.covolume() * 3
    assert a2.twist(2).covolume() ** 2 == a2.covolume() ** 2 * 4
    assert e8.twist(2).covolume() == 16
    assert e8.twist(2).covolume() != 2 ** 8
