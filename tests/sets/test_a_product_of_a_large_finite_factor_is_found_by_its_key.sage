r"""A product of a large finite factor is found by the factor's key, not its points.

A finite ordered set whose points are given by an enumeration it owns may declare
the datum that names it (``FiniteOrderedSets.from_indexed``, ``key=``).  The set
that declares a key is compared with another set that declares one by their keys,
and two declarations of one key are one construction.  The store that keeps one
product per equal family (`SET-05`) keys a family by its factors' declared keys,
so finding the product reads no point of the factor, and the cost of the lookup
does not grow with the factor.

Every set below reaches its points through a map that records the positions asked
of it.  That is how a reader's sets reach theirs -- an image is enumerated by its
source through its map -- so the recording is the enumeration's own account of
what the construction asked the mathematics for.  The assertion is therefore that
the product is found again having asked the large factor's points for nothing.
"""

from sage_extensions.all import *  # noqa: F401,F403

_SIZE = 4096  # points of the large factor; the assertions count no point, only none


def _integers_below(record, *, size, key):
    r"""The finite ordered set $\{0,\dots,n-1\}$ for $n=$ ``size``, in that order.

    The points are reached through ``point``, which records every position asked
    of it, and ``position`` inverts it without reaching any point.  The order is
    the one of the ordinal $\Delta[n-1]$ indexing the enumeration.
    """
    indices = Sets.Δ[size - 1]

    def point(index):
        record.append(int(index))
        return ZZ(int(index))

    def position(value):
        number = ZZ(value)
        return number if indices.is_parent_of(number) is True else None

    return FiniteOrderedSets().from_indexed(indices, point, index_of=position, key=key)


def test_one_key_names_one_set_and_constructing_it_asks_no_point() -> None:
    r"""Two declarations of one key are one set, and the second reads no point.

    A declared key is the set's defining datum, so the store that holds one set per
    datum answers the second declaration with the first set: the enumeration the
    second caller supplied is not run at all.
    """
    record = []
    first = _integers_below(record, size=_SIZE, key=("integers below", _SIZE))
    assert tuple(record) == ()

    again = _integers_below(record, size=_SIZE, key=("integers below", _SIZE))

    assert again is first
    assert tuple(record) == ()
    assert again == first


def test_a_product_with_a_large_finite_factor_is_found_without_reading_the_factor() -> None:
    r"""The product of a family holding the large factor is found again reading no point.

    The factor is presented twice by its one key, so the two families are one
    family (`SET-05`) and the second product is the first construction.  Neither
    the second presentation of the factor nor the lookup walks the factor.
    """
    record = []
    factor = _integers_below(record, size=_SIZE, key=("integers below", _SIZE))
    point = Sets.Δ[0]
    product = Sets().product((factor, point))
    assert product.factor(0) is factor
    assert product.factor(1) is point

    record.clear()
    again = _integers_below(record, size=_SIZE, key=("integers below", _SIZE))

    assert Sets().product((again, point)) is product
    assert tuple(record) == ()


def test_a_product_of_a_new_large_factor_reads_no_point_of_it() -> None:
    r"""A large factor's points are not read to find the product it indexes.

    This factor is its own datum, so the product it indexes is a new construction;
    the store must place the family by the keys its factors declare, which is a
    datum of the factor, and not by hashing the factor's points.  The point is read
    from the enumeration's account: building the factor asks for all of them, and
    asking for the product afterwards asks for none.
    """
    record = []
    other_record = []
    first = _integers_below(record, size=_SIZE, key=("integers below", _SIZE))
    point = Sets.Δ[0]
    product = Sets().product((first, point))

    second = _integers_below(other_record, size=_SIZE + 1, key=("integers below", _SIZE + 1))
    other_record.clear()

    later = Sets().product((second, point))

    assert later is not product
    assert later.factor(0) is second
    assert tuple(other_record) == ()
    assert tuple(record) == ()
