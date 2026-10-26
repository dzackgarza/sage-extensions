r"""Cohomology algebra Mor objects preserve the graded algebra identity."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_cohomology_algebra_has_an_identity_morphism() -> None:
    cohomology = QQ.polynomial_ring("x").de_rham_algebra().cohomology_algebra()
    identity = cohomology.Mor(cohomology).identity()

    assert identity.domain() is cohomology
    assert identity.codomain() is cohomology
    assert identity(cohomology.one()) == cohomology.one()
    assert identity * identity == identity

