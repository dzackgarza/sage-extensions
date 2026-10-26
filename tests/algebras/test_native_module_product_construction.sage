r"""The quadratic extension ``QQ[z]/(z^2 - 2) = QQ(sqrt 2)``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_qq_adjoin_sqrt_two_is_a_field_of_degree_two_with_inverse_of_1_plus_3z() -> None:
    r"""``z^2 - 2`` is irreducible over ``QQ`` (``sqrt 2`` is irrational), so
    ``QQ[z]/(z^2 - 2)`` is a field of dimension 2, and
    ``(1 + 3z)^{-1} = (3z - 1)/17`` since ``(1 + 3z)(3z - 1) = 9z^2 - 1 = 17``."""
    polynomials = QQ["z"]
    extension = polynomials.quotient(polynomials.ideal([polynomials.gen() ** 2 - 2]))
    z = extension(polynomials.gen())

    assert extension.module_rank() == 2
    assert extension.is_field()
    assert (1 + 3 * z) * (3 * z - 1) == 17
    assert (1 + 3 * z) ** -1 == (3 * z - 1) / 17
    assert z * z == 2
