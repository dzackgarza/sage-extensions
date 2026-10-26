r"""Integrality, characteristic and minimal polynomials, and conjugates in ``QQ(sqrt 5)``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_characteristic_polynomial_is_the_minimal_polynomial_raised_to_the_relative_degree() -> None:
    r"""For ``alpha`` in ``K``, ``charpoly_{K/QQ}(alpha) = minpoly(alpha)^[K : QQ(alpha)]``
    (Lang, *Algebra*, VI §5).  In ``QQ(sqrt 5)``: ``1`` has minimal polynomial
    ``x - 1`` and characteristic polynomial ``(x - 1)^2``, while ``sqrt 5`` has
    both equal to ``x^2 - 5``."""
    field = QuadraticField(5, "a")
    one = field.one()
    a = field.primitive_element()

    assert one.minimal_polynomial().degree() == 1
    assert one.characteristic_polynomial() == one.minimal_polynomial() ** 2
    assert a.characteristic_polynomial() == a.minimal_polynomial()
    assert a.minimal_polynomial().degree() == 2
    assert a.minimal_polynomial()(a) == field.zero()


def test_number_field_integrality_is_not_membership_in_the_selected_power_order() -> None:
    field = QuadraticField(5, "a")
    a = field.primitive_element()
    integral = (field.one() + a) / 2

    assert integral.is_integral()
    assert not (field.one() / 2).is_integral()


def test_the_conjugates_of_root_five_are_plus_and_minus_root_five() -> None:
    r"""``QQ(sqrt 5)/QQ`` is Galois, so it is its own normal closure; its two
    embeddings send ``sqrt 5`` to the two roots ``+-sqrt 5`` of ``x^2 - 5``."""
    field = QuadraticField(5, "a")
    closure = field.normal_closure()
    a = field.primitive_element()
    conjugates = a.conjugates(closure)
    image = field.embeddings(closure)

    assert closure.degree() == 2
    assert conjugates.cardinality() == 2
    roots = [value for value in conjugates]
    assert roots[0] == -roots[1]
    assert roots[0] ** 2 == 5 * closure.one()
    assert image.cardinality() == 2
