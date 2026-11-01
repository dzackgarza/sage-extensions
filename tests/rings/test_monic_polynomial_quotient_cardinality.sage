r"""``k[t]/(f)`` has ``|k|^deg f`` elements when ``f`` is monic.

The division algorithm in one variable gives the basis ``1, t, ..., t^(d-1)`` of
``k[t]/(f)`` for monic ``f`` of degree ``d``, so the cardinal is the *coefficient
field's*, raised to the degree — not the polynomial ring's, which is infinite and
would make the answer uninformative.  The branch checks every hypothesis first:
one algebra generator, a coefficient ring that is a field with a decided
cardinality, a defining ideal with exactly one generator, and a monic generator of
positive degree (``f - t^d`` of degree below ``d``).  Anything else refuses at
this branch rather than guessing; another owner may still answer correctly, which
is why the refusal is asserted on the branch and not on ``cardinality()``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_dual_numbers_over_five_elements_have_twenty_five() -> None:
    r"""``FF_5[t]/(t^2)`` is two-dimensional over ``FF_5``, and ``t`` is nilpotent there."""
    polynomials = GF(5)["t"]
    t = polynomials.gen()
    quotient = polynomials.quotient_ring(polynomials.ideal(t**2))

    assert quotient.cardinality() == 25

    projection = quotient.quotient_map()
    image = projection(t)
    assert image != quotient.zero()
    assert projection(t**2) == quotient.zero()
    assert image * image == quotient.zero()


def test_a_cubic_quotient_over_five_elements_has_one_hundred_twenty_five() -> None:
    polynomials = GF(5)["t"]
    t = polynomials.gen()
    quotient = polynomials.quotient_ring(polynomials.ideal(t**3 + t + polynomials.one()))

    assert quotient.cardinality() == 125


def test_the_coefficient_field_supplies_the_base_of_the_power() -> None:
    r"""``FF_4[t]/(t^2)`` is ``4^2 = 16``, not ``2^2``: the cardinal is the field's."""
    polynomials = GF(4)["t"]
    t = polynomials.gen()
    quotient = polynomials.quotient_ring(polynomials.ideal(t**2))

    assert quotient.cardinality() == 16


def test_an_infinite_coefficient_field_gives_an_infinite_quotient() -> None:
    r"""``QQ[t]/(t^2)`` is countable, so the formula reads ``aleph_0^2 = aleph_0``."""
    polynomials = QQ["t"]
    t = polynomials.gen()
    quotient = polynomials.quotient_ring(polynomials.ideal(t**2))

    assert quotient.cardinality() == polynomials.cardinality()
    assert quotient.cardinality().is_finite() is False


def test_the_retained_generator_is_monic_because_the_ideal_normalizes_it() -> None:
    r"""``(2t^2)`` is retained as ``(t^2)``: over a field the branch sees a monic generator.

    So the non-monic presentation does not reach the branch as non-monic — the
    ideal normalizes by the unit leading coefficient — and 25 is the right answer
    for both.  The guard is still asserted where the hypotheses really fail: a
    ring with more than one generator, below.
    """
    polynomials = GF(5)["t"]
    t = polynomials.gen()
    quotient = polynomials.quotient_ring(polynomials.ideal(polynomials(2) * t**2))

    (generator,) = tuple(quotient.defining_ideal().ideal_generators())
    assert generator == t**2
    assert (generator - t ** int(generator.degree())).degree() < int(generator.degree())
    assert quotient._monic_quotient_cardinality() == 25


def test_the_branch_refuses_a_ring_with_more_than_one_generator() -> None:
    plane = QQ["x,y"]
    x = plane.gen(0)
    quotient = plane.quotient_ring(plane.ideal(x**2))

    assert quotient._monic_quotient_cardinality() is None
