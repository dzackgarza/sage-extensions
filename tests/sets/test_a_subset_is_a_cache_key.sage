r"""A subset is a key of the product interner, so it hashes, and its hash is decided once.

``SET-05`` interns finite products and coproducts by the hashes of their
factors, so a subset is a cache key: it hashes by its ambient set, refined by
the decided members when that set is finite and enumerated.  Deciding every
member of a finite ambient set is the whole of that hash, so the subset caches
it rather than repeating the decisions at every lookup.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_subset_hash_decides_each_member_once() -> None:
    r"""The hash of a subset of ``{a, b}`` decides ``a`` and ``b`` once.

    The subset is cut out of a finite enumerated ambient set by a predicate
    that records the points it is asked about.  Its hash asks about both
    points and then caches the answer: a second and a third hash of the same
    subset add no questions, though each hash is a lookup of the product the
    subset is a factor of.
    """
    points = FiniteOrderedSets()(("a", "b"))
    asked = []

    def is_selected(point):
        asked.append(point)
        return point == "a"

    subset = points.power_set().from_predicate(is_selected)
    before = tuple(asked)
    hash(subset)
    assert tuple(asked) != before
    settled = tuple(asked)
    hash(subset)
    hash(subset)
    assert tuple(asked) == settled
    assert hash(subset) == hash(subset)
