r"""A class of ``ZZ/(n)`` hashes as the class, not as the lift it was given (#531).

:meth:`QuotientRings.ElementMethods._richcmp_` decides equality of two classes by
membership of their difference in the defining ideal, so ``1`` and ``4`` are one
class of ``ZZ/(3)``.  The hash is the engine's representative of the class, which
the engine hashes as that class, so equal classes given different lifts hash
equally and distinct classes of one modulus hash apart.

The two statements are what a cache keyed by such classes needs: without a hash of
the class, every set of vectors over ``ZZ/(n)`` is unhashable, and the cache of
``_lattice_subobject_spanning`` cannot be keyed by a span basis over ``ZZ/(3)``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_classes_with_different_lifts_are_one_key() -> None:
    r"""``1`` and ``4`` are one class of ``ZZ/(3)``, and one dictionary key."""
    ring = GF(3)
    lifted = ring(1)
    relifted = ring(4)
    table = {lifted: cardinal(1), relifted: cardinal(2)}

    assert lifted == relifted
    assert hash(lifted) == hash(relifted)
    assert cardinal(sum(1 for _ in table)) == cardinal(1)
    assert table[relifted] == cardinal(2)


def test_distinct_classes_of_one_modulus_hash_apart() -> None:
    r"""The classes of ``1`` and of ``2`` in ``ZZ/(3)`` are different sets of lifts."""
    ring = GF(3)
    first = ring(1)
    second = ring(2)

    assert first != second
    assert hash(first) != hash(second)
    assert cardinal(sum(1 for _ in {first: cardinal(0), second: cardinal(1)})) == cardinal(2)
