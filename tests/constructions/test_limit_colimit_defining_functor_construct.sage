r"""Selected limit and colimit categories expose their defining functors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_selected_limits_expose_the_canonical_limit_functor() -> None:
    shape = DiscreteCategory(Sets.Δ[1])
    sets = Sets()
    limits = sets.Limits(shape)

    assert limits.defining_functor() is sets.limit_functor(shape)


def test_selected_colimits_expose_the_canonical_colimit_functor() -> None:
    shape = DiscreteCategory(Sets.Δ[1])
    sets = Sets()
    colimits = sets.Colimits(shape)

    assert colimits.defining_functor() is sets.colimit_functor(shape)
