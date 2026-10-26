r"""Derivations of the affine plane form the represented module of vector fields."""

from sage_extensions.all import *  # noqa: F401,F403


def _plane_derivations():
    algebra = QQ.polynomial_ring(("x", "y"))
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    target = algebra.regular_module()
    derivations = algebra.derivations(target)
    partial_x = derivations({x: algebra.one(), y: algebra.zero()})
    x_partial_y = derivations({x: algebra.zero(), y: x})
    return algebra, x, y, target, derivations, partial_x, x_partial_y


def test_affine_plane_derivation_space_represents_leibniz_derivations() -> None:
    algebra, x, y, target, derivations, partial_x, _ = _plane_derivations()

    assert derivations in Modules(algebra)
    assert partial_x == derivations({"x": algebra.one(), "y": algebra.zero()})
    assert derivations.module_rank() == 2
    assert partial_x.domain() is algebra
    assert partial_x.codomain() is target
    identification = algebra.regular_module_isomorphism()
    assert identification(partial_x.generator_image("x")) == algebra.one()
    assert identification(partial_x(x * y)) == y
    assert partial_x.linear_endomorphism()(x * y) == y
    assert partial_x.restricted_codomain().regular_module_identification()(partial_x.as_morphism()(x * y)) == y
    assert partial_x.restricted_codomain().base_ring() is QQ


def test_affine_plane_derivations_have_the_expected_lie_and_cartan_operations() -> None:
    algebra, x, y, _, _, partial_x, x_partial_y = _plane_derivations()
    bracket = partial_x.lie_bracket(x_partial_y)
    de_rham = algebra.de_rham_algebra()
    dx = de_rham(algebra.kahler_differentials().differential_generator("x"))

    assert bracket.linear_endomorphism()(x) == algebra.zero()
    assert bracket.linear_endomorphism()(y) == algebra.one()
    assert partial_x.interior_product()(dx) == de_rham.one()
    assert partial_x.lie_derivative()(de_rham(x)) == de_rham.one()
    assert partial_x.lie_derivative()(dx) == de_rham.zero()

