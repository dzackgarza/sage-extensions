r"""Finite covering families as represented diagrams with chosen overlaps.

Two copies of the identity ``X -> X`` form a cover of ``X``.  Their overlap is
again ``X`` with identity legs, so this specimen exposes the members, the one
unordered pair of indices, its span, and the finite presentation functor without
requiring any topology-specific coverage condition.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _double_identity_cover():
    sets = Sets()
    points = sets(("a", "b"))
    identity = sets.Mor(points, points).identity()
    overlap = sets.span(identity, identity)
    covers = CoveringFamilies(sets)
    cover = covers.family(points, (identity, identity), {(0, 1): overlap})
    return covers, cover, points, identity, overlap


def test_covering_family_retains_target_members_indices_and_overlap() -> None:
    covers, cover, points, identity, overlap = _double_identity_cover()
    indices = cover.index_set()
    pairs = cover.pair_index_set()

    assert cover.coverage() is covers
    assert cover.covering_family_category() is covers
    assert cover.site_category() is Sets()
    assert cover.covered_object() is points
    assert cover.target() is points
    assert indices.cardinality() == cardinal(2)
    assert cover.members().cardinality() == cardinal(2)
    assert cover.member(indices[0]) == identity
    assert cover.member(indices[1]) == identity
    assert pairs.cardinality() == cardinal(1)
    assert cover.overlaps().cardinality() == cardinal(1)
    assert cover.overlap_span(indices[0], indices[1]) == overlap


def test_covering_family_presentation_is_the_diagram_over_the_site_category() -> None:
    covers, cover, _points, _identity, _overlap = _double_identity_cover()
    presentation = cover.presentation()

    assert presentation.codomain() is Sets()
    assert cover in covers.presentation_category()


def test_covering_family_morphisms_have_identity() -> None:
    covers, cover, _points, _identity, _overlap = _double_identity_cover()
    identity = covers.Mor(cover, cover).identity()

    assert identity.domain() is cover
    assert identity.codomain() is cover
    assert identity * identity == identity
