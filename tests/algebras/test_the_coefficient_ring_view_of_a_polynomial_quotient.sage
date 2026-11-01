r"""The coefficient-ring view of a polynomial quotient retains its presentation.

``A = R[x]/I`` states the polynomial cover as its base ring, so it cannot state
its own ``R``-algebra structure or the presentation of it.  Its view
``A.as_algebra_over(R)`` is the same ring over ``R`` — built on ``A`` and
retaining it — and ``R[x]/I`` is that view's presentation.  What the view
retains is what a map out of it is read against, and what makes the de Rham
algebra over ``R`` computable for the quotient at all.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    AlgebrasWithChosenFinitePresentation,
)

import pytest


def _dual_numbers():
    r"""``F_2[x]/(x^2)``, its polynomial cover and its ``F_2``-algebra view."""
    polynomials = GF(2)["x"]
    quotient = polynomials.quotient_ring(polynomials.gen() ** 2)
    return polynomials, quotient, quotient.as_algebra_over(GF(2))


def test_the_view_is_the_same_ring_read_over_the_coefficient_ring() -> None:
    r"""The view states ``F_2`` as base, keeps the quotient, and converts both ways."""
    polynomials, quotient, view = _dual_numbers()
    x = polynomials.gen()

    assert view is not quotient
    assert view.native_ring() is quotient
    assert view.base_ring() is GF(2)
    assert quotient.base_ring() is polynomials

    # The same element, read on both sides: the view is a scalar structure on
    # the quotient's ring, not a second representation of it.
    class_of_x = quotient(x)
    assert view(class_of_x) == view(x)
    assert quotient(view(class_of_x)) == class_of_x
    assert view(class_of_x) * view(class_of_x) == view.zero()


def test_the_view_carries_the_presentation_of_the_quotient() -> None:
    r"""Generators, relations and the lift are the quotient's, read over ``F_2``."""
    polynomials, quotient, view = _dual_numbers()
    x = polynomials.gen()

    assert view in AlgebrasWithChosenFinitePresentation(GF(2))
    assert view.presentation_ring() is polynomials
    assert view.algebra_generating_set() == polynomials.algebra_generating_set()
    assert view.algebra_generator("x") == view(quotient(x))
    assert view.lift_to_presentation(view.algebra_generator("x")) == x
    assert view.lift_to_presentation(view(x**2)) == polynomials.zero()
    relations = view.relations()
    assert tuple(relations.value(index) for index in relations.index_set()) == (x**2,)


def test_a_generator_assignment_is_read_against_the_retained_relations() -> None:
    r"""``x |-> 0`` descends; ``x |-> 1`` is refuted by ``x^2 = 0``."""
    _polynomials, _quotient, view = _dual_numbers()
    collapse = view.Mor(view)(
        {label: view.zero() for label in view.algebra_generating_set()}
    )

    assert collapse.is_multiplicative() is True
    assert collapse.preserves_unit() is True
    assert collapse(view.one()) == view.one()
    assert collapse(view.algebra_generator("x")) == view.zero()

    broken = view.Mor(view)(
        {label: view.one() for label in view.algebra_generating_set()}
    )
    with pytest.raises(ValueError):
        broken.validate_presentation_relations()


def test_the_de_rham_algebra_of_the_quotient_is_taken_over_the_coefficient_ring() -> None:
    r"""``DR_{F_2}(A)`` is built on the view, and in characteristic ``2`` ``x dx`` survives."""
    polynomials, quotient, view = _dual_numbers()
    x = polynomials.gen()
    de_rham = quotient.de_rham_algebra()

    assert de_rham.base_ring() is GF(2)
    assert de_rham.coefficient_algebra() is view
    assert de_rham.de_rham_source_algebra() is view

    X = de_rham(view(quotient(x)))
    dX = de_rham.d(X)
    assert dX != de_rham.zero()
    # d(x^2) = 2x dx = 0 imposes no relation on x dx when 2 = 0.
    assert de_rham.d(X * X) == de_rham.zero()
    assert X * dX != de_rham.zero()
