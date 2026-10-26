r"""The universal property of the exterior algebra."""

from sage_extensions.all import *  # noqa: F401,F403


def test_x_to_epsilon_extends_from_the_exterior_algebra_to_the_dual_numbers() -> None:
    r"""A linear map ``f : M -> A`` with ``f(m)^2 = 0`` extends uniquely to an
    algebra map ``Λ(M) -> A``.  For ``M = ZZ x`` and ``A = ZZ[ε]/(ε^2)``,
    ``x ↦ ε`` extends with ``x ∧ x ↦ 0`` and ``1 + 3x ↦ 1 + 3ε``."""
    polynomials = ZZ["e"]
    dual_numbers = polynomials.quotient(polynomials.ideal([polynomials.gen() ** 2]))
    epsilon = dual_numbers(polynomials.gen())
    line = Modules(ZZ).free_module(("x",))
    linear = line.Mor(dual_numbers)({line.module_generator("x"): epsilon})
    extension = linear.alternating_extension()
    exterior = line.exterior_algebra()
    x = exterior.algebra_generator("x")

    assert extension(x) == epsilon
    assert extension(x * x) == dual_numbers.zero()
    assert extension(exterior.one() + 3 * x) == 1 + 3 * epsilon
    assert extension(exterior.one() + 3 * x) != dual_numbers.one()
