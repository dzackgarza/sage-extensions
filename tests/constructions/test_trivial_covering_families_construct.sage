r"""The trivial coverage consists of singleton identity covers.

For every object ``X`` of a site, the unique trivial cover is ``id_X:X->X``.
Its overlap data is vacuous and it is still an ordinary covering-family object,
so all of the represented cover structure remains available.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_trivial_coverage_builds_the_singleton_identity_cover() -> None:
    sets = Sets()
    points = sets(("a", "b"))
    coverage = TrivialCoveringFamilies(sets)
    cover = coverage.family(points)
    index = cover.index_set().an_element()
    identity = sets.Mor(points, points).identity()

    assert coverage in Cat()
    assert cover in coverage
    assert cover in CoveringFamilies(sets)
    assert cover.coverage() is coverage
    assert cover.covered_object() is points
    assert cover.index_set().cardinality() == cardinal(1)
    assert cover.members().cardinality() == cardinal(1)
    assert cover.member(index) == identity
    assert cover.pair_index_set().cardinality() == cardinal(0)
    assert cover.overlaps().cardinality() == cardinal(0)


def test_trivial_covering_family_morphisms_have_identity() -> None:
    sets = Sets()
    points = sets(("a", "b"))
    coverage = TrivialCoveringFamilies(sets)
    cover = coverage.family(points)
    identity = coverage.Mor(cover, cover).identity()

    assert identity.domain() is cover
    assert identity.codomain() is cover
    assert identity * identity == identity
