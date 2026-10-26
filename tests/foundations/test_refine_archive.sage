r"""Real roots of rational polynomials, and the order of $H_4$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_archived_owned_polynomial_real_roots_keep_exact_multiplicities() -> None:
    polynomial_ring = QQ.polynomial_ring("x")
    x = polynomial_ring.algebra_generator("x")

    roots = (x**2 - 5).roots(ring=AA)
    assert tuple(roots) == (1, 1)
    assert tuple(root**2 for root in roots.index_set()) == (5, 5)
    assert roots.index_set()[0] < 0 < roots.index_set()[1]

    repeated = ((x - 1) ** 2 * (x - 2)).roots(ring=AA)
    assert tuple(repeated.index_set()) == (AA(1), AA(2))
    assert tuple(repeated) == (2, 1)
    assert (x**2 + 1).roots(ring=AA).cardinality() == 0


def test_the_noncrystallographic_coxeter_group_h4_has_order_14400() -> None:
    r"""$|W(H_4)| = 14400$, the symmetry group of the 600-cell.

    Source: Humphreys, *Reflection Groups and Coxeter Groups*, §2.11, Table 2.2.
    """
    assert Groups.Coxeter(["H", 4]).order() == 14400
