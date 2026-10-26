r"""The Hesse pencil retains its basepoint, good-locus restriction, and sample fibres."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hesse_selected_basepoint_is_a_base_locus_point() -> None:
    hesse = HesseBertiniFamily()

    assert hesse.basepoint() is hesse.base_locus_point()


def test_hesse_good_locus_restriction_map_has_the_expected_endpoints() -> None:
    hesse = HesseBertiniFamily()
    restricted = hesse.restriction_to_good_locus()
    inclusion = hesse.good_locus_restriction_map()

    assert inclusion.domain() is restricted
    assert inclusion.codomain() is hesse.family()


def test_hesse_selected_general_and_exceptional_members_distinguish_smoothness() -> None:
    hesse = HesseBertiniFamily()

    assert hesse.general_member().is_smooth()
    assert not hesse.exceptional_member().is_smooth()
