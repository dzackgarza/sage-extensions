r"""Polynomial tensor products satisfy the coproduct universal property over the base ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_polynomial_lines_have_the_plane_as_their_coproduct() -> None:
    category = Algebras(QQ).Associative().Unital().Commutative()
    first = QQ.polynomial_ring("x")
    second = QQ.polynomial_ring("y")
    coproduct = category.coproduct((first, second))
    factors = coproduct.coproduct_factors()
    injections = coproduct.coproduct_injections()

    assert coproduct in CommutativeAlgebraCoproducts(QQ)
    assert factors[0] is first
    assert factors[1] is second
    assert coproduct.tensor_factors()[0] is first
    assert coproduct.tensor_factors()[1] is second
    assert injections[0] == coproduct.coproduct_injection(0)
    assert injections[1] == coproduct.coproduct_injection(1)
    assert coproduct.left_coproduct_map() == injections[0]
    assert coproduct.right_coproduct_map() == injections[1]
    assert isinstance(coproduct.one(), coproduct.ElementType)


def test_polynomial_coproduct_factorizes_every_cocone() -> None:
    category = Algebras(QQ).Associative().Unital().Commutative()
    first = QQ.polynomial_ring("x")
    second = QQ.polynomial_ring("y")
    coproduct = category.coproduct((first, second))
    target = QQ.polynomial_ring(("u", "v"))
    u = target.algebra_generator("u")
    v = target.algebra_generator("v")
    left = first.Mor(target)({"x": u})
    right = second.Mor(target)({"y": v})
    induced = coproduct.from_cocone(left, right)
    tensor_induced = coproduct.tensor_map(left, right)

    assert induced * coproduct.left_coproduct_map() == left
    assert induced * coproduct.right_coproduct_map() == right
    assert tensor_induced == induced

