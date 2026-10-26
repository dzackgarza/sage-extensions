r"""The Legendre family retains its smooth and singular fibres and first cohomology."""

from sage_extensions.all import *  # noqa: F401,F403


def test_legendre_family_morphism_starts_at_the_family_scheme() -> None:
    family = LegendreMonodromyFamily()

    assert family.family_morphism().domain() is family.family_scheme()


def test_legendre_reference_and_singular_fibres_have_expected_smoothness() -> None:
    family = LegendreMonodromyFamily()

    assert family.smooth_reference_fiber().is_smooth()
    assert not family.singular_fiber().is_smooth()


def test_legendre_reference_fiber_has_rank_two_first_cohomology() -> None:
    family = LegendreMonodromyFamily()
    base_point = family.base_point()

    assert family.fiber_cohomology(base_point).module_rank() == cardinal(2)
    assert family.proper_base_change_hypotheses_hold(base_point)


def test_legendre_local_system_is_the_selected_higher_direct_image() -> None:
    family = LegendreMonodromyFamily()

    assert family.local_system() is family.higher_direct_image()
