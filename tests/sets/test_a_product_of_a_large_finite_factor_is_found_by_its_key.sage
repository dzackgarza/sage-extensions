r"""A product of a large finite factor is found by the key that factor holds.

`SET-05`: two presentations of one family are one construction.  The store that
keeps one product per equal family keys a family by its index set and by its
factors' hashes (``set_categories._finite_family_key``), and a finite ordered
set's hash is the hash of its point sequence, which is the data its equality
compares.  So one key names one family, and a lookup finds one product however
its family was presented.

The cost claims below are stated as the asks a reader makes, not as a clock: a
map records every position it is asked for, and a point records every ask for
its hash, so the enumeration's own account says whether something read the
points.  A finite ordered set is fixed by its points, so a construction that
read them holds their hash: placing a family of such sets reads that value and
runs no factor's map, however large the factor is (#547).  A set whose points a
construction builds on demand -- an image under a map -- decides the same value
when it is first asked, and not before.

Equality stays extensional.  Three sets of one point sequence are equal each to
each whatever route built them, one family is one product, and equal sets hash
equally; the key adds only that two equal sets hold one point sequence, so the
confirmation a lookup makes is an identity test rather than a walk of the
factors.
"""

from sage_extensions.all import *  # noqa: F401,F403

_SIZE = 4096
_POSITIONS = (0, 1, 2)


class _Point(int):
    r"""The integer it counts, recording every ask for its hash.

    It states which point it is and nothing else, so it is a point of a finite
    ordered set; ``asked`` collects the numbers whose hash was computed, which is
    how a reader sees whether something hashed the points of a set again.
    """

    def __new__(cls, number, asked):
        point = int.__new__(cls, int(number))
        point.asked = asked
        return point

    def __hash__(self):
        self.asked.append(int(self))
        return int.__hash__(self)


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


def _recorded_factor(size, asked, first=0):
    r"""The ordered points $\text{first},\dots,\text{first}+\text{size}-1$ through a supplied inverse.

    The index set is the ordinal on ``size`` points, the forward map is the point
    at a position and records every position it is asked for, and the inverse is
    the position whose point equals the candidate, answering ``None`` off the
    image.  This is the presentation a section, an image and a residue locus
    reach their points through.

    ``first`` names the point at position zero, so two tests that place a family
    of one size place two families: the store of finite products keeps one
    construction per equal family, and its answers outlive a test.
    """

    def point_at(index):
        asked.append(int(index))
        return ZZ(first + int(index))

    def position_of(value):
        for position in range(size):
            if ZZ(first + position) == value:
                return position
        return None

    return FiniteOrderedSets().from_indexed(
        Sets.Δ[size - 1], point_at, index_of=position_of
    )


def test_a_finite_ordered_set_of_given_points_holds_their_hash() -> None:
    r"""A set built from its points answers for its hash without hashing them again.

    The points are read once, in the construction; the hash is the hash of the
    sequence that construction selected, and a reader that asks for it -- the
    store of finite products asks every factor for its hash -- reads a value the
    set already holds.  Four thousand points is the factor size of the issue, and
    a hash that walked them would ask for every one of them here.
    """
    asked = []
    factor = FiniteOrderedSets()(
        tuple(_Point(number, asked) for number in range(_SIZE))
    )
    settled = tuple(asked)

    hash(factor)
    hash(factor)

    assert tuple(asked) == settled
    assert cardinal(factor.cardinality()) == cardinal(_SIZE)


def test_a_finite_ordered_set_presented_by_a_supplied_inverse_holds_its_hash() -> None:
    r"""A set built through an inverse holds the hash of the points it read there.

    The construction reads its points once, so that the set is its point
    sequence and not a question it answers later by running the map again; the
    first ask for the hash therefore asks the map for nothing.
    """
    asked = []
    factor = _recorded_factor(_SIZE, asked)

    assert tuple(asked) == tuple(range(_SIZE))

    settled = tuple(asked)
    hash(factor)

    assert tuple(asked) == settled
    assert cardinal(factor.cardinality()) == cardinal(_SIZE)


def test_a_product_with_a_fresh_equal_large_factor_reads_no_point_of_it() -> None:
    r"""The lookup of a family of large factors asks neither factor for a point.

    The second factor is built separately, from the same points, and its own
    construction reads them; placing its family then reads the key each factor
    holds and finds the product of the first, confirming that the two equal
    factors are one factor without walking either.
    """
    unit = Sets.Δ[0]
    factor = _recorded_factor(_SIZE, [], first=_SIZE)
    product = Sets().product((factor, unit))

    asked = []
    again = _recorded_factor(_SIZE, asked, first=_SIZE)
    settled = tuple(asked)

    assert Sets().product((again, unit)) is product
    assert tuple(asked) == settled
    assert product.factor(0) is factor
    assert product.factor(1) is unit
    assert cardinal(product.factor(0).cardinality()) == cardinal(_SIZE)


def test_a_large_factor_is_found_and_the_sets_that_find_it_are_equal() -> None:
    r"""One family, one product: a fresh equal factor of 4096 points finds it.

    The two factors are built separately from their points and are equal sets,
    so their hashes agree and the store answers the second family with the
    product of the first.  The product's own factor is the first factor, which
    is what "one family, one construction" says.
    """
    points = tuple(int(number) for number in range(2 * _SIZE, 3 * _SIZE))
    factor = FiniteOrderedSets()(points)
    unit = Sets.Δ[0]
    product = Sets().product((factor, unit))

    again = FiniteOrderedSets()(points)

    assert Sets().product((again, unit)) is product
    assert again == factor
    assert again is not factor
    assert hash(again) == hash(factor)
    assert product.factor(0) is factor
    assert product.factor(1) is unit
    assert cardinal(product.factor(0).cardinality()) == cardinal(_SIZE)


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
