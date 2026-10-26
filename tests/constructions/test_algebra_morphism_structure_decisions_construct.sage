r"""A unital algebra identity preserves multiplication and the unit."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_algebra_identity_retains_its_linear_and_tensor_square_maps() -> None:
    algebra = QQ.polynomial_ring("x")
    identity = algebra.Mor(algebra).identity()
    linear = identity.underlying_morphism()
    tensor_square = identity.tensor_square_morphism()

    assert identity.is_multiplicative() is True
    assert identity.preserves_unit() is True
    assert linear.domain() is algebra
    assert linear.codomain() is algebra
    assert tensor_square.domain() is algebra.multiplication_morphism().domain()
    assert tensor_square.codomain() is algebra.multiplication_morphism().domain()
