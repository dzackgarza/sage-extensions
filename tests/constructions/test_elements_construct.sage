r"""Elements of every named object behave as their algebra says.

Ring axioms on the witnesses of every ring, arithmetic of principal ideal
domains, fields, number fields; elements of free modules and lattices; group
elements; and the elements every witness object exhibits.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_ring_axioms_on_the_witnesses_of_every_ring(ring) -> None:
    a = ring.an_element()
    one = ring.one()
    zero = ring.zero()

    assert a.parent() is ring
    assert a + zero == a
    assert a * one == a
    assert one * a == a
    assert a - a == zero
    assert -a + a == zero
    assert a * zero == zero
    assert (a + one) - one == a
    assert zero.is_zero()
    assert one.is_one()
    assert one.is_unit()
    assert not zero.is_unit()
    assert (a + one) * (a + one) == a * a + a * one + one * a + one
    assert ring(3) * ring(4) == ring(12)
    assert ring(7) - ring(7) == zero
    assert one.multiplicative_order() == 1
    assert (-one).multiplicative_order() == (1 if ring.characteristic() == 2 else 2)


def test_commutativity_and_binomial_expansion(commutative_ring) -> None:
    ring = commutative_ring
    a = ring.an_element()
    b = ring(5)
    assert a * b == b * a
    assert (a + b) ** 2 == a**2 + 2 * a * b + b**2
    assert (a + b) ** 3 == a**3 + 3 * a**2 * b + 3 * a * b**2 + b**3


def test_additive_orders_in_finite_rings(finite_ring) -> None:
    ring = finite_ring
    assert ring.one().additive_order() == ring.characteristic()
    assert ring.zero().additive_order() == 1
    assert ring.characteristic() * ring.one() == ring.zero()


def test_divisibility_in_principal_ideal_domains(pid) -> None:
    ring = pid
    twelve, eighteen, six = ring(12), ring(18), ring(6)
    gcd = twelve.gcd(eighteen)
    lcm = twelve.lcm(eighteen)

    assert six.divides(twelve)
    assert gcd.divides(six)
    assert six.divides(gcd)
    assert lcm.divides(ring(36))
    assert ring(36).divides(lcm)
    assert twelve.divides(lcm)
    assert ring(4).is_square()
    assert ring(4).sqrt() ** 2 == ring(4)
    quotient, remainder = ring(17).quo_rem(ring(5))
    assert quotient * ring(5) + remainder == ring(17)
    assert ring(5).factorial() == ring(120)


def test_valuations_and_prime_divisors_in_the_integers() -> None:
    assert ZZ(12).prime_divisors() == Set((2, 3))
    assert ZZ(12).valuation(2) == 2
    assert ZZ(12).valuation(3) == 1
    assert ZZ(12).valuation(5) == 0
    assert ZZ(0).is_zero()
    assert not ZZ(2).is_unit()
    assert ZZ(-1).is_unit()
    assert ZZ(7).is_prime()
    assert not ZZ(8).is_prime()
    assert ZZ(8).is_square() is False
    assert ZZ(2) in ZZ.ideal(6).radical()
    assert ZZ(6) in ZZ.ideal(12).radical()
    assert ZZ(3) not in ZZ.ideal(4).radical()


def test_field_arithmetic(field) -> None:
    three = field(3)
    four = field(4)
    if three == field.zero():
        return
    assert three.is_unit()
    assert three.inverse_of_unit() * three == field.one()
    assert (three / four) * four == three
    assert field.an_element() * field.one() == field.an_element()


def test_number_field_element_invariants(build) -> None:
    gaussian = build("QQ(i)")
    i = gaussian.primitive_element()
    assert i * i == -gaussian.one()
    assert i.norm() == QQ(1)
    assert i.trace() == QQ(0)
    assert (i + gaussian.one()).norm() == QQ(2)
    assert (i + gaussian.one()).trace() == QQ(2)
    assert i.minpoly().degree() == 2
    assert i in gaussian.ring_of_integers()
    assert (i / gaussian(2)) not in gaussian.ring_of_integers()
    assert (i + gaussian.one()).is_unit() is False
    assert gaussian(i + gaussian.one()).inverse_of_unit() * (i + gaussian.one()) == gaussian.one()
    real_quadratic = build("QQ(sqrt5)")
    root_five = real_quadratic.primitive_element()
    golden = (real_quadratic.one() + root_five) / real_quadratic(2)
    assert golden.norm() == QQ(-1)
    assert golden.trace() == QQ(1)
    assert golden in build("QQ(sqrt5)").ring_of_integers()
    assert golden.is_unit()


def test_elements_of_free_modules(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    v = module.an_element()
    e0, e1 = module.module_generator(0), module.module_generator(1)
    assert v.parent() is module
    assert v + module.zero() == v
    assert 2 * v == v + v
    assert ring(2) * v == v + v
    assert 0 * v == module.zero()
    assert v - v == module.zero()
    assert e0 + e1 == e1 + e0
    assert e0 != e1
    assert -(e0 + e1) == -e0 - e1
    assert module.linear_combination({0: ring(3), 1: ring(-1)}) == 3 * e0 - e1


def test_elements_of_lattices() -> None:
    a2 = Lattices(ZZ)("A2")
    e0, e1 = a2.module_generator(0), a2.module_generator(1)
    assert e0.is_root()
    assert (e0 + e1).is_root()
    assert not (2 * e0).is_root()
    assert e0.b(e0) == -2 or e0.b(e0) == 2
    assert e0.norm() == e0.b(e0)
    assert e0.q() * 2 == e0.b(e0)
    assert e0.div() == 1
    assert (2 * e0).div() == 2
    assert (e0 + e1).b(e0 - e1) == 0
    assert e0.divisibility_ideal() == ZZ.ideal(1)
    assert (3 * e0).divisibility_ideal() == ZZ.ideal(3)


def test_elements_of_groups() -> None:
    group = Groups.S(4)
    g = group.group_generators()[0]
    h = group.group_generators()[1]
    assert g * g.inverse() == group.one()
    assert (g * h).inverse() == h.inverse() * g.inverse()
    assert g ** g.order() == group.one()
    assert (h * g * h.inverse()).order() == g.order()
    assert group.one().order() == 1
    assert g.order() in (2, 3, 4)


def test_elements_of_finite_and_infinite_sets() -> None:
    three = Sets.Δ[2]
    assert three.an_element() in three
    assert three(1) in three
    assert three(1) != three(2)
    named = Set(("a", "b"))
    assert "a" in named
    assert named.an_element() in named
    assert NN.an_element() in NN
    assert NN(5) + NN(7) == NN(12)
    assert NN(3) in ZZ
    assert QQ(1) / QQ(2) not in ZZ
    assert ZZ.cardinality() == aleph0
