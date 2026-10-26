r"""The walking arrow exposes the finite ordinal positions and unique order arrow."""

from sage_extensions.all import *  # noqa: F401,F403


def test_walking_arrow_finite_ordinal_exposes_positions_and_mor_owner() -> None:
    walking_arrow = Sets().ArrowCategory().domain_category()
    zero = walking_arrow(0)
    one = walking_arrow(1)
    morphisms = walking_arrow.Mor(zero, one)
    arrow = morphisms.unique()

    assert zero.position() == 0
    assert one.position() == 1
    assert morphisms.ordinal_category() is walking_arrow
    assert arrow.domain() is zero
    assert arrow.codomain() is one
