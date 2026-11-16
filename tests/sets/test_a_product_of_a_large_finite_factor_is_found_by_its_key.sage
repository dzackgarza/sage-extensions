r"""A product of a large finite factor is found by the factor's key, which is its points.

`SET-05`: two presentations of one family are one construction.  The store that
keeps one product per equal family keys a family by its index set and by its
factors' hashes (``set_categories._finite_family_key``), and a factor's hash is
the hash of its point sequence.  A finite ordered set *is* its points, in order,
so its hash is a function of the set, two equal sets supply one key, and the
lookup finds one product however its family was presented.

The three claims are asserted together because they are one rule.  If equality
answered by data other than the points -- a datum a construction declares for
itself, say -- then ``==`` would stop being transitive, a set being equal to each
of two sets that are unequal to each other, and two equal families would be two
products, which is what `SET-05` forbids.

These tests assert the rule and not a way of reading it: no assertion counts a
call, a point or a clock.  The factor of the last test is 4096 points, so a rule
that read a factor's points when placing a family would read a large set; the cost
of that reading is measured where it is repaired and not asserted here.
"""

from sage_extensions.all import *  # noqa: F401,F403

_SIZE = 4096
_POSITIONS = (0, 1, 2)


def _points():
    r"""The ordered points $0 < 1 < 2$."""
    return (ZZ(0), ZZ(1), ZZ(2))


def _enumeration(points):
    r"""The two directions of the enumeration of ``points`` by their positions.

    The index set is the ordinal on three points, the forward map is the point at
    a position, and the inverse is the first position whose point equals the
    candidate, which answers ``None`` off the image.
    """

    def point_at(index):
        return points[int(index)]

    def position_of(value):
        for position in _POSITIONS:
            if value is points[position] or value == points[position]:
                return position
        return None

    return point_at, position_of


def _enumerated(points):
    r"""The finite ordered set of ``points``, built through an enumeration of them."""
    point_at, position_of = _enumeration(points)
    return FiniteOrderedSets().from_indexed(
        Sets.Δ[2], point_at, index_of=position_of
    )


def _declaring(points, datum):
    r"""The same set, built declaring ``datum`` as the data that names it."""
    point_at, position_of = _enumeration(points)
    return FiniteOrderedSets().from_indexed(
        Sets.Δ[2], point_at, index_of=position_of, key=datum
    )


def test_equality_of_finite_ordered_sets_is_transitive_whatever_data_they_declare() -> None:
    r"""Three sets of one point sequence are one point sequence: each is equal to each.

    A set built declaring data of its own is still the points it enumerates, so it
    is equal to every set of those points and unequal to none of them.  Two sets
    that are both equal to a third are equal to each other: ``==`` is an
    equivalence relation, not a comparison against a presentation.
    """
    points = _points()
    enumerated = _enumerated(points)
    first = _declaring(points, ("the first datum",))
    second = _declaring(points, ("the second datum",))

    assert tuple(first) == points
    assert first == enumerated
    assert enumerated == second
    assert first == second
    assert hash(first) == hash(second) == hash(enumerated)
    assert cardinal(first.cardinality()) == cardinal(second.cardinality())


def test_equal_sets_give_one_product_whatever_data_they_declare() -> None:
    r"""One family, one product: the family's factor is the point sequence it enumerates.

    The family below is presented three times, through three sets of one point
    sequence, one of which declares data of its own.  The three presentations are
    one family, so the store answers two of them with the third's product.
    """
    points = _points()
    unit = Sets.Δ[0]
    product = Sets().product((_declaring(points, ("the first datum",)), unit))

    assert Sets().product((_enumerated(points), unit)) is product
    assert Sets().product((_declaring(points, ("the second datum",)), unit)) is product
    assert product.factor(0) == _enumerated(points)
    assert product.factor(1) is unit


def test_a_product_with_a_fresh_equal_large_factor_is_one_construction() -> None:
    r"""A 4096-point factor built twice is one family, so one product, and one key.

    The two factors are built separately from their points and are equal sets, so
    their hashes agree and the store finds the product of the first from the
    family of the second.  The product's own factor is the first factor: the
    construction that was found is the one that was built.
    """
    points = tuple(int(number) for number in range(_SIZE))
    factor = FiniteOrderedSets()(points)
    unit = Sets.Δ[0]
    product = Sets().product((factor, unit))

    again = FiniteOrderedSets()(points)

    assert again == factor
    assert again is not factor
    assert hash(again) == hash(factor)
    assert Sets().product((again, unit)) is product
    assert product.factor(0) is factor
    assert product.factor(1) is unit
    assert cardinal(product.factor(0).cardinality()) == cardinal(_SIZE)
