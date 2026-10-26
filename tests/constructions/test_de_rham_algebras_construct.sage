r"""The de Rham algebra of the affine line retains its source and differential forms."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_de_rham_algebra_has_the_expected_differential() -> None:
    line = QQ.polynomial_ring("x")
    x = line.algebra_generator("x")
    de_rham = line.de_rham_algebra()
    differential = de_rham.differential()

    assert de_rham in DeRhamAlgebras(QQ)
    assert de_rham.de_rham_source_algebra() is line
    assert de_rham.kahler_differentials().module_rank() == 1
    assert differential(differential(de_rham(x))) == de_rham.zero()
    assert differential(de_rham(x**2)) == 2 * de_rham(x) * differential(de_rham(x))
