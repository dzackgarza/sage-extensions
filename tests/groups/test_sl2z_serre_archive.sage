r"""Serre's amalgam $\mathrm{SL}_2(\mathbf{Z}) \cong C_4 *_{C_2} C_6$ (Serre, *Trees*, I.4.2)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sl2z_is_generated_by_elements_of_orders_four_and_six_amalgamated_over_minus_one() -> None:
    r"""$S = \begin{psmallmatrix}0&-1\\1&0\end{psmallmatrix}$ has order 4 and
    $ST = \begin{psmallmatrix}0&-1\\1&1\end{psmallmatrix}$ has order 6, with
    $S^2 = (ST)^3 = -1$; $\mathrm{SL}_2(\mathbf{Z})$ is infinite with
    abelianization $\mathbf{Z}/12$ (Serre, *Trees*, I.4.2).
    """
    group = Groups.SL(2, ZZ)
    s = group(matrix(ZZ, [[0, -1], [1, 0]]))
    t = group(matrix(ZZ, [[1, 1], [0, 1]]))
    minus_one = group(matrix(ZZ, [[-1, 0], [0, -1]]))

    assert s.order() == 4
    assert (s * t).order() == 6
    assert s**2 == minus_one
    assert (s * t) ** 3 == minus_one
    assert group.is_finite() is False
    assert Groups().abelianization()(group).cardinality() == 12
