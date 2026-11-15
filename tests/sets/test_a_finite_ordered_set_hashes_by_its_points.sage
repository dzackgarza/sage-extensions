r"""A finite ordered set hashes the data it compares: its points, in order (#531).

:meth:`FiniteOrderedSets.ParentMethods.__eq__` decides equality of two finite
ordered sets by their cardinality and then their points, in order, point by
point.  A hash must be a function of that same data: Python's data model states
the one required property, "objects which compare equal have the same hash
value" (Python 3.14 documentation, *Data model*, ``object.__hash__``), and a
hash that ignores what equality reads does not merely collide -- it puts every
set of one cardinality in one bucket, so every dictionary keyed by such a set
compares its stored keys one by one.

That is what #390 measured on the rank-5 lattice below: the span bases
``_lattice_subobject_spanning`` is keyed by are finite ordered sets of lattice
vectors, the cache reached 1197 entries on 5 hash values, and one lookup
compared 5415 stored keys of 51 us each in the last window of the run
(``.tmp/qc-evidence/issue390-subobject-scan.log``, 335226fc95).

The statement here is the contract and its quantitative form on span bases of
one rank: two equal sets hash equally, and distinct sets of one cardinality do
not share a hash.  Distinct contents give distinct hashes with the probability
of a collision in Python's 64-bit hash, which for ``N = 200`` sets is
``N(N-1)/2 * 2^-64`` about ``1e-15`` pairs: the assertion that all 200 values
are distinct is therefore not a flake but a statement about the hash reaching
the points, and it fails outright for a hash of the cardinality alone.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest

_COUNT = 200


def _small_lattice():
    r"""``U \oplus U \oplus \langle -2 \rangle``, of rank 5 and signature \((2,3)\)."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def _coordinates(vector):
    r"""The coordinates of a lattice vector in the generating set of its lattice."""
    return tuple(int(entry) for entry in vector.to_vector())


def _span_basis(lattice, index):
    r"""The ``index``-th rank-two span basis of ``lattice``, as a finite ordered set.

    ``index`` selects the pair ``(e_0 + (k+1)e_1 + k e_2, e_2 + (k+1)e_3 + k e_4)``
    of the lattice's generators, which is independent for every ``k``, so the
    set is a basis of the rank-two span it generates.  The bases are built
    through :class:`FiniteOrderedSets`, which is the class whose hash is at
    issue: its points are lattice vectors, the objects the cache of #390 keys
    on.
    """
    labels = tuple(lattice.module_generating_set())
    points = tuple(lattice.module_generator(label) for label in labels)
    left = points[0] + ZZ(index + 1) * points[1] + ZZ(index) * points[2]
    right = points[2] + ZZ(index + 1) * points[3] + ZZ(index) * points[4]
    assert cardinal(lattice.subobject_on((left, right)).module_rank()) == cardinal(2)
    return FiniteOrderedSets()((left, right))


def _span_bases(lattice, count):
    r"""``count`` distinct rank-two span bases of ``lattice``, as finite ordered sets."""
    return tuple(_span_basis(lattice, index) for index in range(count))


def test_equal_finite_ordered_sets_hash_equally() -> None:
    r"""Two separately built sets with the same points in the same order hash equally.

    This is the required property of the hash, and it is the half the defect does
    not break: the cardinality is one thing two equal sets share.  It is asserted
    so that the repair cannot trade it away -- a hash that reaches the points must
    still agree on sets that are equal, which is the property a cache key needs
    for a hit.
    """
    lattice = _small_lattice()
    labels = tuple(lattice.module_generating_set())
    points = tuple(lattice.module_generator(label) for label in labels)
    first = FiniteOrderedSets()((points[0], points[1]))
    second = FiniteOrderedSets()((points[0], points[1]))

    assert first == second
    assert first is not second
    assert hash(first) == hash(second)
    assert cardinal(first.cardinality()) == cardinal(2)


def test_distinct_span_bases_of_one_rank_do_not_share_a_hash() -> None:
    r"""Two hundred distinct rank-two span bases take two hundred distinct hashes.

    The sets are pairwise distinct as sets of vectors, which the test states by
    their coordinates, so a hash that reads the points separates them: with
    ``N = 200`` the number of colliding pairs a 64-bit hash is expected to
    produce is ``N(N-1)/2 * 2^-64``, about ``1e-15``, and the assertion is that
    the number of distinct values is ``N`` exactly.  A hash of the cardinality
    alone gives one value, which is the defect of #531 and the reason one cache
    lookup in #390's run compared every stored span basis in turn.
    """
    lattice = _small_lattice()
    bases = _span_bases(lattice, _COUNT)
    contents = {
        tuple(_coordinates(point) for point in basis) for basis in bases
    }
    hashes = tuple(hash(basis) for basis in bases)
    distinct_hashes = set(hashes)

    assert cardinal(sum(1 for _ in bases)) == cardinal(_COUNT)
    assert cardinal(sum(1 for _ in contents)) == cardinal(_COUNT)
    assert cardinal(sum(1 for _ in distinct_hashes)) == cardinal(_COUNT)
    assert cardinal(bases[0].cardinality()) == cardinal(bases[-1].cardinality())


def test_a_span_basis_finds_its_own_cache_entry_without_scanning_the_others() -> None:
    r"""A set equal to one already built reaches its entry, and a new one does not.

    The dictionary a cache keeps is the consumer of the two tests above: two
    equal finite ordered sets are one key, so a lookup reaches the stored entry,
    and a distinct set is another key.  Written with the sets themselves as
    keys, it is the statement #531 closes with -- the entry is found in constant
    time, not by comparing the stored keys one by one.
    """
    lattice = _small_lattice()
    bases = _span_bases(lattice, 32)
    table = {basis: position for position, basis in enumerate(bases)}
    rebuilt = tuple(
        FiniteOrderedSets()(tuple(basis)) for basis in bases
    )

    assert cardinal(sum(1 for _ in table)) == cardinal(32)
    assert all(table[basis] == position for position, basis in enumerate(rebuilt))
    assert hash(bases[0]) != hash(bases[1])


def test_a_finite_ordinal_hashes_by_its_points_like_the_set_they_form() -> None:
    r"""An ordinal hashes as the finite ordered set of the same points does.

    ``AugmentedSimplexCategory`` is the one category refining ``FiniteOrderedSets``
    (``set_categories.py``, ``super_categories``), so an ordinal is a finite
    ordered set and takes this hash with its points ``0, ..., n``.  Two ordinals
    are never distinct sets of one cardinality, so the second set here is
    another three points: the hash reads the points, and two sets of one
    cardinality are apart.
    """
    ordinal = Sets.Δ[2]
    same = FiniteOrderedSets()(tuple(ordinal))
    shifted = FiniteOrderedSets()(tuple(Sets.Δ[3])[1:])

    assert tuple(ordinal) == (0, 1, 2)
    assert ordinal == same
    assert ordinal != shifted
    assert ordinal.cardinality() == shifted.cardinality()
    assert hash(ordinal) == hash(same)
    assert hash(ordinal) != hash(shifted)


def test_a_set_with_an_unhashable_point_is_unhashable() -> None:
    r"""An equal pair of sets, one of whose points refuses a hash, has one hash: none.

    :class:`tuple` and :class:`frozenset` hash their contents and refuse a hash
    when a content does not hash; a finite ordered set is the same data.  A
    mutable Sage vector or matrix is unhashable and equals its immutable copy,
    so the two sets below are equal: a hash that fell back to something weaker
    than the points when a point refused a hash gives these two equal sets two
    values.  The points are built over Python integers, ``int(...)``, because
    the preparser makes a literal a library integer that Sage's constructors
    reject (``tests/forms/test_the_coble_anti_isometry.sage``).
    """
    mutable_vector = vector([int(1), int(2)])
    immutable_vector = vector([int(1), int(2)])
    immutable_vector.set_immutable()
    mutable_matrix = identity_matrix(int(2))
    immutable_matrix = identity_matrix(int(2))
    immutable_matrix.set_immutable()

    assert mutable_vector == immutable_vector
    assert mutable_matrix == immutable_matrix
    for mutable, immutable in (
        (mutable_vector, immutable_vector),
        (mutable_matrix, immutable_matrix),
    ):
        with pytest.raises(TypeError):
            hash(mutable)
        floating = FiniteOrderedSets()((mutable,))
        fixed = FiniteOrderedSets()((immutable,))
        relocated = FiniteOrderedSets()((immutable,))
        assert floating == fixed
        assert fixed == relocated
        assert hash(fixed) == hash(relocated)
        with pytest.raises(TypeError):
            hash(floating)
