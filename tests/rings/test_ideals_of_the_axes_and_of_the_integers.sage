r"""Ideal operations in the coordinate ring of the axes and in the integers.

On ``A = Q[x, y]/(xy)``: ``A/(x) = Q[y]`` is a domain, so ``(x)`` is prime and not
maximal, while ``A/(x, y) = Q`` makes ``(x, y)`` maximal; ``(x + y)`` is not prime, as
``x * y = 0`` lies in it while neither factor does.  ``(x) + (y) = (x, y)``;
``(x)(y) = (xy) = 0``; ``(x) \cap (y) = 0``; ``0 : (x) = (y)``, the annihilator of
``x``; ``rad (x^2) = (x)``; the minimal primes of ``0`` are ``(x)`` and ``(y)``; ``x + y``
and ``y`` are congruent modulo ``(x)``; and ``A/(x)`` has Krull dimension one.

In ``Z``: ``(4) + (6) = (2)``, ``(4)(6) = (24)``, ``(4) \cap (6) = (12)``,
``(4)^2 = (16)``, ``(12) : (4) = (3)``, ``(12) : (2)^infinity = (3)``,
``Z/(12)`` has 12 elements, ``5`` and ``17`` are congruent modulo ``12``, and
``(4) = (-4)``.  ``(12) = (4) \cap (3)`` is its primary decomposition.
"""

from sage_extensions.all import *  # noqa: F401,F403


def axes():
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    return plane.quotient_by_relations([x * y])


def test_primes_and_maximal_ideals_of_the_axes() -> None:
    ring = axes()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")

    assert ring.ideal(x).is_prime()
    assert not ring.ideal(x).is_maximal()
    assert ring.ideal(x, y).is_maximal()
    assert not ring.ideal(x + y).is_prime()
    assert ring.ideal(x).quotient_ring().krull_dimension() == 1


def test_membership_congruence_and_annihilators_on_the_axes() -> None:
    ring = axes()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    line = ring.ideal(x)

    assert x**3 in line
    assert y not in line
    assert line.contains_ambient_element(x * x)
    assert line.congruent(x + y, y)
    assert not line.congruent(x + y, x)
    assert ring.ideal(ring.zero()).colon(line) == ring.ideal(y)


def test_sums_and_products_on_the_axes() -> None:
    ring = axes()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")

    assert ring.ideal(x).sum(ring.ideal(y)) == ring.ideal(x, y)
    assert ring.ideal(x).product(ring.ideal(y)) == ring.ideal(ring.zero())


def test_the_radical_of_x_squared_on_the_axes() -> None:
    ring = axes()
    x = ring.algebra_generator("x")

    assert ring.ideal(x**2).radical() == ring.ideal(x)


def test_the_associated_primes_of_zero_on_the_axes_are_the_two_lines() -> None:
    ring = axes()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    primes = ring.ideal(ring.zero()).associated_primes()

    assert ring.ideal(x) in primes
    assert ring.ideal(y) in primes


def test_ideal_arithmetic_in_the_integers() -> None:
    assert ZZ.ideal(ZZ(4)) == ZZ.ideal(ZZ(-4))
    assert ZZ.ideal(ZZ(12)).colon(ZZ.ideal(ZZ(4))) == ZZ.ideal(ZZ(3))
    assert ZZ.ideal(ZZ(12)).ideal_saturation(ZZ.ideal(ZZ(2))) == ZZ.ideal(ZZ(3))
    assert ZZ.ideal(ZZ(12)).congruent(ZZ(5), ZZ(17))
    assert not ZZ.ideal(ZZ(12)).congruent(ZZ(5), ZZ(11))


def test_sums_products_and_powers_of_integer_ideals() -> None:
    four = ZZ.ideal(ZZ(4))
    six = ZZ.ideal(ZZ(6))

    assert four.sum(six) == ZZ.ideal(ZZ(2))
    assert four.product(six) == ZZ.ideal(ZZ(24))
    assert four.power(2) == ZZ.ideal(ZZ(16))


def test_twelve_is_the_intersection_of_the_primary_ideals_four_and_three() -> None:
    components = ZZ.ideal(ZZ(12)).primary_decomposition()

    assert ZZ.ideal(ZZ(4)) in components
    assert ZZ.ideal(ZZ(3)) in components


def test_the_two_lines_of_the_axes_meet_in_zero() -> None:
    ring = axes()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")

    assert ring.ideal(x).intersection(ring.ideal(y)) == ring.ideal(ring.zero())


def test_the_residue_ring_of_twelve_has_twelve_elements() -> None:
    assert ZZ.ideal(ZZ(12)).residue_cardinality() == 12


def test_four_and_six_intersect_in_twelve() -> None:
    assert ZZ.ideal(ZZ(4)).intersection(ZZ.ideal(ZZ(6))) == ZZ.ideal(ZZ(12))


def test_subobject_join_and_meet_retain_the_commutative_ideal_structure() -> None:
    r"""For (4),(6) in Z, their join is (2) and meet is (12).

    Their defining module-subobject inclusions retain the actual regular
    module Z as codomain; both computed results remain ideals and hence
    support subsequent ideal multiplication and containment.
    """
    four, six = ZZ.ideal(ZZ(4)), ZZ.ideal(ZZ(6))
    join, meet = four.sum(six), four.intersection(six)

    for result in (join, meet):
        assert result in CommutativeIdeals(ZZ)
        assert result in ModuleSubobjects(ZZ)
        assert result.inclusion().codomain() is ZZ.regular_module()
        assert result.inclusion().is_injective()
        assert all(result.contains_ambient_element(generator) for generator in result.ideal_generators())
    assert join == ZZ.ideal(ZZ(2))
    assert meet == ZZ.ideal(ZZ(12))
    assert join.product(ZZ.ideal(ZZ(3))) == ZZ.ideal(ZZ(6))
    assert meet.sum(join) == join


def test_polynomial_ideal_subobject_operations_preserve_maps_and_ideal_arithmetic() -> None:
    r"""The join of (x),(y) in Q[x,y] is (x,y); their intersection is (xy)."""
    ring = QQ["x,y"]
    x, y = ring.algebra_generators()
    left, right = ring.ideal(x), ring.ideal(y)
    join = left.sum(right)
    meet = left.intersection(right)

    assert join == ring.ideal(x, y)
    assert meet == ring.ideal(x * y)
    for ideal in (join, meet):
        assert ideal in CommutativeIdeals(ring)
        assert ideal.inclusion().codomain() is ring.regular_module()
        assert all(ideal.contains_ambient_element(generator) for generator in ideal.ideal_generators())
    assert meet.product(join) == ring.ideal(x * x * y, x * y * y)


def test_localized_ideal_subobject_join_and_meet_retain_local_source_data() -> None:
    r"""The ideals (9), (6) of Z_(3) have sum (3) and intersection (9)."""
    ring = ZZ.localize_at_prime(3)
    left, right = ring.ideal(ring(9)), ring.ideal(ring(6))
    join, meet = left.sum(right), left.intersection(right)

    assert join == ring.ideal(ring(3))
    assert meet == ring.ideal(ring(9))
    assert join in CommutativeIdeals(ring) and meet in CommutativeIdeals(ring)
    assert join.inclusion().codomain() is ring.regular_module()
    assert meet.inclusion().codomain() is ring.regular_module()
    assert meet.contains_ambient_element(ring(18))
    assert not meet.contains_ambient_element(ring(3))
