r"""Symmetric algebras retain the generating module and polynomial grading."""

from sage_extensions.all import *  # noqa: F401,F403


def test_symmetric_algebra_exposes_its_homogeneous_components() -> None:
    module = QQ.free_module(("x", "y"))
    symmetric = module.symmetric_algebra()
    x = symmetric.algebra_generator("x")
    y = symmetric.algebra_generator("y")
    element = symmetric.one() + x + y + x * y

    assert symmetric in SymmetricAlgebras(QQ)
    assert symmetric.generating_module() is module
    assert symmetric.from_component(1, module.module_generator("x")) == x
    assert symmetric.homogeneous_component(element, 1) == x + y
    assert symmetric.homogeneous_component(element, 2) == x * y
    assert element.homogeneous_component(2) == x * y
    assert element.homogeneous_components() == symmetric.homogeneous_components(element)


def test_univariate_symmetric_algebra_polynomial_defines_a_number_field() -> None:
    polynomial_ring = QQ.free_module(("x",)).symmetric_algebra()
    x = polynomial_ring.algebra_generator("x")
    field = (x**2 + polynomial_ring.one()).number_field("i")

    assert field.degree() == 2

