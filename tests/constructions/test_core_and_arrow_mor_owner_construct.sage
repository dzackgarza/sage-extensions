r"""Core and arrow Mor objects retain the categories that own their arrows."""

from sage_extensions.all import *  # noqa: F401,F403


def test_core_mor_remembers_the_core_category() -> None:
    two = Sets.Δ[1]
    swap = Sets().Mor(two, two)(lambda point: two(1 - int(point)))
    core = Sets().Core()
    morphisms = core.Mor(two, two)
    isomorphism = morphisms(swap, swap)

    assert morphisms.core_category() is core
    assert isomorphism.forward() == swap
    assert isomorphism.inverse() == swap


def test_arrow_mor_identity_at_is_the_identity_square() -> None:
    two = Sets.Δ[1]
    identity = Sets().Mor(two, two).identity()
    arrows = Sets().ArrowCategory()
    arrow = arrows(identity)
    morphisms = arrows.Mor(arrow, arrow)

    assert morphisms.identity_at(arrow) == morphisms.identity()
