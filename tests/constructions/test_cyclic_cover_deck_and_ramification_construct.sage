r"""A double cyclic cover exposes its branch, deck actions, ramification, and quotient map."""

from sage_extensions.all import *  # noqa: F401,F403


def test_double_cover_deck_and_ramification_data() -> None:
    line_ring = QQ["x"]
    x = line_ring.algebra_generator("x")
    cover = CyclicCovers(line_ring, 2)(x**4 - 1)
    group = CyclicCovers(line_ring, 2).constant_deck_group()
    generator = group.group_generators()[0]
    sigma = cover.constant_deck_transformation(generator)
    action = cover.constant_deck_action()
    group_scheme = cover.deck_group_scheme()
    group_scheme_action = cover.deck_group_scheme_action()
    ramification = cover.ramification_support_subscheme()
    branch = cover.branch_subscheme()
    to_branch = cover.ramification_to_branch_morphism()

    assert cover.branch_section() == x**4 - 1
    assert cover.deck_root_of_unity() == -1
    assert sigma.coordinate_algebra_morphism()(cover.cover_variable()) == -cover.cover_variable()
    assert action.acting_group() is group
    assert group_scheme_action.acting_group() is group_scheme
    assert ramification.dimension() == 0
    assert to_branch.domain() is ramification
    assert to_branch.codomain() is branch
    assert cover.quotient_morphism() == cover.structure_morphism()
    assert not cover.is_etale_cover()
