r"""Centres of free associative algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_associative_algebra_on_two_generators_has_centre_qq() -> None:
    r"""``Z(QQ<x, y>) = QQ``: a noncommutative polynomial commuting with ``x`` and
    ``y`` is a polynomial in a single word, hence a scalar.  So scalars are
    central while ``x``, ``x^2``, ``xy + yx`` and ``x + y`` are not."""
    tensor = Modules(QQ).free_module(("x", "y")).tensor_algebra()
    x, y = tensor.algebra_generator("x"), tensor.algebra_generator("y")
    center = tensor.ring_center()

    assert x * y != y * x
    assert 3 * tensor.one() in center
    assert x not in center
    assert x * x not in center
    assert x * y + y * x not in center
    assert x + y not in center


def test_tensor_algebra_on_one_generator_is_commutative_hence_its_own_centre() -> None:
    r"""``T(QQ x) = QQ[x]`` is commutative, so every element is central."""
    tensor = Modules(QQ).free_module(("x",)).tensor_algebra()
    x = tensor.algebra_generator("x")
    center = tensor.ring_center()

    assert x in center
    assert x**3 + 2 * x in center
    assert tensor.is_commutative()
