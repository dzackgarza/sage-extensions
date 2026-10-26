"""Defining data and canonical routes for native ring constructions."""

from sage_extensions.categories.algebras.algebras import AlgebrasWithChosenFinitePresentation
from sage_extensions.categories.algebras.free_algebras import SymmetricAlgebras, TensorAlgebras
from sage_extensions.categories.rings.commutative_algebra import (
    AdicCompletions,
    FormalPowerSeriesRings,
    QuotientRings,
)
from sage_extensions.categories.rings.commutative_ideals import CommutativeIdeals
from sage_extensions.categories.rings.number_fields import _number_field_of
from sage_extensions.categories.rings.ring_foundation import (
    GF,
    OwnedRings,
    _owned_integers,
    _owned_rationals,
)


def test_rational_localization_and_finite_field() -> None:
    integers = _owned_integers()
    rationals = _owned_rationals()
    assert integers.fraction_field_localization() is rationals
    assert integers.fraction_field() is rationals
    assert GF(4) is GF(4)
    assert GF(4) in OwnedRings().Division()


def test_free_algebras_keep_their_constructing_categories() -> None:
    rationals = _owned_rationals()
    polynomial = rationals.polynomial_ring("t")
    assert polynomial is rationals.polynomial_ring("t")
    assert polynomial.ambient_category() is SymmetricAlgebras(rationals)
    generating = rationals.free_module(("a", "b"))
    tensor = generating.tensor_algebra()
    assert tensor is generating.tensor_algebra()
    assert tensor.ambient_category() is TensorAlgebras(rationals)


def test_number_field_and_maximal_quotient_are_one_field() -> None:
    rationals = _owned_rationals()
    polynomial = rationals.polynomial_ring("t")
    t = polynomial.algebra_generator("t")
    f = t * t + polynomial(1)
    field = _number_field_of(f)
    ideal = CommutativeIdeals(polynomial).Maximal()(f)
    assert polynomial.quotient_ring(ideal) is field
    a = field.algebra_generator("t")
    assert a * a == field(-1)
    assert a.norm() == rationals(1)
    assert a.trace() == rationals(0)
    minimal_polynomial_ring = rationals.polynomial_ring("x")
    x = minimal_polynomial_ring.algebra_generator("x")
    assert a.minpoly() == x * x + minimal_polynomial_ring(1)
    multiplication = a.multiplication_morphism()
    algebra = field.as_algebra()
    assert multiplication.domain() is algebra
    assert multiplication.codomain() is algebra
    assert field.as_algebra() is algebra
    assert field.embeddings(field).cardinality() == 2
    order = field.ring_of_integers()
    assert order is field.ring_of_integers()
    assert len(tuple(order.integral_basis())) == 2


def test_presentations_retain_their_data_and_category() -> None:
    rationals = _owned_rationals()
    polynomial = rationals.polynomial_ring("p")
    p = polynomial.algebra_generator("p")
    relation = p * p
    quotient = polynomial.quotient_by_relations((relation,))
    assert quotient is polynomial.quotient_by_relations((relation,))
    assert quotient is polynomial.quotient_by_relations((relation + polynomial(0),))
    assert quotient.ambient_category() is AlgebrasWithChosenFinitePresentation(rationals)
    assert quotient.presentation_ring() is polynomial


def test_dual_numbers_retain_their_quotient() -> None:
    rationals = _owned_rationals()
    dual = rationals.dual_numbers("epsilon")
    assert dual is rationals.dual_numbers("epsilon")
    assert dual.ambient_category() is QuotientRings()
    assert dual.quotient_source() is rationals.polynomial_ring("epsilon")
    epsilon = dual.algebra_generator("epsilon")
    assert epsilon * epsilon == dual.zero()


def test_power_series_retain_their_completion() -> None:
    rationals = _owned_rationals()
    series = FormalPowerSeriesRings(rationals)("s", default_prec=5)
    assert series is FormalPowerSeriesRings(rationals)("s", default_prec=5)
    assert series.ambient_category() is AdicCompletions()
    assert series.completion_source() is rationals.polynomial_ring("s")
    s = series.formal_parameter("s")
    assert s.coefficient(1) == rationals(1)
