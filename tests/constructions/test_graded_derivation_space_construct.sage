r"""The partial derivatives of a polynomial ring are homogeneous graded derivations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_partial_x_is_a_degree_minus_one_graded_derivation() -> None:
    algebra = QQ.free_module(("x", "y")).symmetric_algebra()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    space = algebra.graded_derivations(shift=-1)
    partial_x = space({"x": algebra.one(), "y": algebra.zero()})
    partial_y = space({"x": algebra.zero(), "y": algebra.one()})

    assert partial_x.algebra() is algebra
    assert partial_x.target() is algebra
    assert partial_x.degree_shift() == -1
    assert partial_x.degree_preservation_decision() is True
    assert partial_x.graded_leibniz_decision() is True
    assert partial_x.linearity_decision() is True
    assert partial_x.check_on_generators() is True
    assert partial_x(x * y) == y
    assert partial_x.as_morphism()(x * y) == y
    assert partial_x.underlying_linear_morphism()(x * y) == y
    assert partial_x.graded_commutator(partial_y)(x * y) == algebra.zero()

