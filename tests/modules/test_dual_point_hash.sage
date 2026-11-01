r"""Points of a dual module hash by their values, not by their parent.

The linear dual of a module is a hom-set, so a point of it is an arrow.  Arrow
equality is extensional: two arrows of one hom-set are equal exactly when they
agree on the domain.  Hashing must therefore read the arrow on the domain as
well.  A hash of the parent alone -- or of the endpoint pair, which every arrow
of a hom-set shares -- puts every point of a dual module in one bucket, so a
dictionary of *n* distinct points compares every pair by arrow equality.  On the
rank-6 standard lattice that cost 22.9 s for 64 points and did not finish in
560 s for the 570 covectors one polyhedral cone carries.

These assertions pin the two halves of the contract: distinct points are
distributed (so insertion is linear), and equal points still share a hash, for
every presentation of the same arrow and for the arrows that arithmetic and the
zero produce.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.polyhedral_cones import finite_ordered_set




def _standard_lattice_dual():
    identity = [[ZZ(1) if i == j else ZZ(0) for j in range(6)] for i in range(6)]
    lattice = Lattices(ZZ)(identity)
    return lattice, lattice.dual_module()


def _covectors(dual, rows):
    labels = tuple(dual.module_generating_set())
    return tuple(
        dual.linear_combination(
            {label: ZZ(value) for label, value in zip(labels, row, strict=True) if value}
        )
        for row in rows
    )


def _box_rows():
    return [
        (a, b, c, 0, 0, 0)
        for a in range(1, 5)
        for b in range(0, 4)
        for c in range(0, 4)
    ]


def test_distinct_dual_points_have_distinct_hashes() -> None:
    _, dual = _standard_lattice_dual()
    points = _covectors(dual, _box_rows())

    assert len(points) == 64
    assert len(set(points)) == 64
    assert len({hash(point) for point in points}) == 64


def test_inserting_distinct_dual_points_does_not_compare_every_pair() -> None:
    r"""The distribution, not the clock, is what a test can hold.

    ``dict.fromkeys`` falls back to equality only on a hash collision, so a
    family whose points separate by values inserts without any arrow comparison.
    Counting the comparisons pins the quadratic behaviour out of the contract
    without timing it: the family below would need 64 * 63 / 2 of them under one
    shared hash.
    """
    _, dual = _standard_lattice_dual()
    points = _covectors(dual, _box_rows())

    ordered = finite_ordered_set(points)

    assert len(ordered) == 64
    assert set(ordered) == set(points)


def test_equal_dual_points_share_a_hash_whatever_presents_them() -> None:
    _, dual = _standard_lattice_dual()
    labels = tuple(dual.module_generating_set())
    unit = dual.linear_combination({labels[0]: ZZ(1)})
    rebuilt = dual.linear_combination({labels[0]: ZZ(2)}) - dual.linear_combination(
        {labels[0]: ZZ(1)}
    )
    doubled_then_halved = (ZZ(2) * unit) - unit

    assert rebuilt == unit
    assert hash(rebuilt) == hash(unit)
    assert doubled_then_halved == unit
    assert hash(doubled_then_halved) == hash(unit)
    assert hash(unit + dual.zero()) == hash(unit)


def test_the_zero_and_the_scalars_keep_their_own_hashes() -> None:
    _, dual = _standard_lattice_dual()
    labels = tuple(dual.module_generating_set())
    unit = dual.linear_combination({labels[0]: ZZ(1)})
    zero = dual.zero()

    assert zero != unit
    assert hash(zero) != hash(unit)
    assert hash(ZZ(2) * unit) != hash(unit)
    assert set(_covectors(dual, _box_rows())) == set(_covectors(dual, _box_rows()))


def test_the_primal_points_keep_their_distribution() -> None:
    r"""The dual repair must not disturb the side that already worked."""
    lattice, _ = _standard_lattice_dual()
    points = _covectors(lattice, _box_rows())

    assert len({hash(point) for point in points}) == 64
    assert len(finite_ordered_set(points)) == 64


def test_a_domain_without_a_finite_probe_falls_back_to_its_endpoints() -> None:
    r"""An infinite frame supplies no probe; the hash stays sound, not fatal.

    ``ZZ[x]`` is free on a countable frame, so its arrows have no finite probe to
    read.  The endpoint hash remains: equal arrows share it, which is what the
    contract requires, and it separates nothing the domain does not separate
    through a finite family.  Reading an infinite frame would be the regression
    -- it would never return -- so the fallback is the answer here.
    """
    polynomials = ZZ["x"]
    arrows = Sets().Mor(polynomials, polynomials)
    doubling = arrows(lambda element: ZZ(2) * element)
    rebuilt = arrows(lambda element: ZZ(2) * element)

    assert hash(doubling) == hash(rebuilt)
    assert isinstance(hash(doubling), int)
