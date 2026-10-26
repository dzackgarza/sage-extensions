r"""The algebraic de Rham cohomology of the affine line is concentrated in degree zero."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_de_rham_cohomology_is_a_cohomology_algebra() -> None:
    line = QQ.polynomial_ring("x")
    cohomology = line.de_rham_algebra().cohomology_algebra()

    assert cohomology in CohomologyAlgebras(QQ)
    assert cohomology.graded_piece(0).module_rank() == 1
    assert cohomology.graded_piece(1).cardinality() == cardinal(1)
    assert isinstance(cohomology.one(), cohomology.ElementType)

