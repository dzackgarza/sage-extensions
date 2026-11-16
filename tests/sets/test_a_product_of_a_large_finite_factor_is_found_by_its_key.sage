r"""A product of a large finite factor is found by the factor's key, which is its points.

`SET-05`: two presentations of one family are one construction.  The store that
keeps one product per equal family keys a family by its index set and by its
factors' hashes (``set_categories._finite_family_key``), and a factor's hash is
the hash of its point sequence.  A finite ordered set *is* its points, in order,
so its hash is a function of the set, two equal sets supply one key, and the
lookup finds one product however its family was presented.

The three claims are asserted together because they are one rule.  If equality
answered by data other than the points -- the enumeration a set was built from,
the universe a subset was cut out of -- then ``==`` would stop being transitive,
a set being equal to each of two sets that are unequal to each other, and two
equal families would be two products, which is what `SET-05` forbids.

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


def _enumerated(points):
    r"""The finite ordered set of ``points``, built through an enumeration of them.

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

    return FiniteOrderedSets().from_indexed(
        Sets.Δ[2], point_at, index_of=position_of
    )


def test_equality_of_finite_ordered_sets_is_transitive_whatever_route_built_them() -> None:
    r"""Three sets of one point sequence are equal each to each, from three constructions.

    The three are built from different data: a literal sequence of points, an
    enumeration of them, and the subset of the ordinal $[2]$ cut out by a
    predicate.  Each is the point sequence $0 < 1 < 2$, so each is equal to each
    of the others, and ``==`` is an equivalence relation rather than a comparison
    of presentations.
    """
    points = _points()
    literal = FiniteOrderedSets()(points)
    enumerated = _enumerated(points)
    subset = Sets.Δ[2].filtered(lambda point: True)

    assert tuple(literal) == points
    assert tuple(enumerated) == points
    assert tuple(subset) == points
    assert literal == enumerated
    assert enumerated == subset
    assert literal == subset
    assert hash(literal) == hash(enumerated) == hash(subset)
    assert cardinal(literal.cardinality()) == cardinal(subset.cardinality())


def test_equal_sets_give_one_product_whatever_route_built_them() -> None:
    r"""One family, one product: the family's factor is the point sequence it enumerates.

    The family below is presented three times, through the three sets above, and
    the three presentations are one family.  The store answers the second and the
    third with the product of the first, and that product's factor is the first
    factor: the construction that was found is the one that was built.
    """
    points = _points()
    literal = FiniteOrderedSets()(points)
    unit = Sets.Δ[0]
    product = Sets().product((literal, unit))

    assert Sets().product((_enumerated(points), unit)) is product
    assert Sets().product((FiniteOrderedSets()(points), unit)) is product
    assert product.factor(0) is literal
    assert product.factor(1) is unit


def test_a_product_with_a_fresh_equal_large_factor_is_one_construction() -> None:
    r"""A 4096-point factor built twice is one family, so one product, and one key.

    The two factors are built separately from their points and are equal sets, so
    their hashes agree and the store finds the product of the first from the
    family of the second.  The product's own factor is the first factor, and the
    factor's cardinality is the 4096 points it was built from.
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
