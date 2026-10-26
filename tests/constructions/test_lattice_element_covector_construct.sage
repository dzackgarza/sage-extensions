r"""A lattice vector maps to its algebraic covector under the correlation."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_basis_vector_to_covector_lies_in_the_linear_dual() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    covector = e.to_covector()

    assert covector.parent() is lattice.linear_dual()


def test_vector_to_covector_is_the_algebraic_correlation_value() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)

    assert e.to_covector() == lattice.algebraic_correlation_morphism()(e)
