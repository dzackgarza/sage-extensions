r"""The ring Mor family refines both multiplicative-additive operation spines."""

from sage_extensions.all import *


def test_framed_polynomial_ring_map_uses_owned_generator_images() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    translate = polynomials.Mor(polynomials)({"x": x + polynomials.one()})

    assert translate.domain() is polynomials
    assert translate.codomain() is polynomials
    assert translate(x) == x + polynomials.one()
    assert translate(x**2) == (x + polynomials.one()) ** 2
    assert translate(x).parent() is polynomials
