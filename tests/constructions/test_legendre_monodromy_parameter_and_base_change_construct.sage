r"""The Legendre family retains its parameter algebra and proper-base-change comparison."""

from sage_extensions.all import *  # noqa: F401,F403


def test_legendre_parameter_algebra_is_the_family_base_coordinate_algebra() -> None:
    family = LegendreMonodromyFamily()
    base = family.family_morphism().codomain()

    assert family.parameter_algebra() is base.coordinate_algebra()
    assert family.singular_parameter() in family.parameter_algebra()


def test_legendre_stalk_to_fiber_comparison_targets_reference_fiber_cohomology() -> None:
    family = LegendreMonodromyFamily()
    comparison = family.stalk_to_fiber_comparison()

    assert comparison.forward().codomain() is family.fiber_cohomology(
        family.base_point()
    )
