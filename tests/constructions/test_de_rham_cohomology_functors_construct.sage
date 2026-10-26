r"""The affine line has the standard algebraic de Rham cohomology."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_de_rham_cohomology_functors_have_the_expected_values() -> None:
    algebras = Algebras(QQ).Associative().Unital().Commutative()
    line = QQ.polynomial_ring("x")
    h0 = algebras.de_rham_cohomology(0)
    h1 = algebras.de_rham_cohomology(1)
    graded = algebras.de_rham_cohomology_algebra()

    assert h0(line).module_rank() == cardinal(1)
    assert h1(line).module_rank() == cardinal(0)
    assert graded(line) in CohomologyAlgebras(QQ)
