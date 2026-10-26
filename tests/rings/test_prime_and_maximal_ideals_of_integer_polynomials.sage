r"""Prime and maximal ideals of ``ZZ[x, y]``.

``ZZ`` is a Jacobson ring, so a maximal ideal of ``ZZ[x, y]`` contains a
prime ``p`` and its image in ``F_p[x, y]`` is maximal.  ``(3, x^2 + 1, y)``
has quotient ``F_3[x]/(x^2 + 1) = F_9`` because ``-1`` is not a square mod 3;
``(2, x^2 + 1, y)`` has quotient ``F_2[x]/((x + 1)^2)``, which is not reduced.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane():
    plane = ZZ["x, y"]
    return plane, plane.algebra_generator("x"), plane.algebra_generator("y")


def test_the_ideal_of_a_closed_point_over_two_is_maximal() -> None:
    plane, x, y = _plane()
    ideal = plane.ideal(plane(2), x, y)
    assert ideal.is_prime()
    assert ideal.is_maximal()


def test_the_origin_of_the_generic_fibre_is_prime_but_not_maximal() -> None:
    plane, x, y = _plane()
    ideal = plane.ideal(x, y)
    assert ideal.is_prime()
    assert not ideal.is_maximal()


def test_six_splits_the_closed_point_into_two() -> None:
    plane, x, y = _plane()
    ideal = plane.ideal(plane(6), x, y)
    assert not ideal.is_prime()
    assert not ideal.is_maximal()


def test_x_squared_plus_one_is_irreducible_mod_three_and_not_mod_two() -> None:
    plane, x, y = _plane()
    over_three = plane.ideal(plane(3), x**2 + 1, y)
    over_two = plane.ideal(plane(2), x**2 + 1, y)
    assert over_three.is_maximal()
    assert not over_two.is_prime()
    assert plane.quotient_by_relations([plane(3), x**2 + 1, y]) in Fields()
