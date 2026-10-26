r"""Set exposes its ordered refinements, and Mor sets know when they are endomorphisms."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sets_ordered_refinements_are_the_owned_order_categories() -> None:
    sets = Sets()

    assert sets.PartiallyOrdered() is PartiallyOrderedSets()
    assert sets.TotallyOrdered() is TotallyOrderedSets()


def test_set_mor_knows_whether_its_endpoints_agree() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]

    assert Sets().Mor(two, two).is_endomorphism_set()
    assert not Sets().Mor(two, three).is_endomorphism_set()
