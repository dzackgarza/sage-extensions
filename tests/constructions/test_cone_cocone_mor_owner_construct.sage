r"""Cone and cocone Mor objects retain the category that owns their arrows."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cone_mor_remembers_its_cone_category() -> None:
    index = DiscreteCategory(Sets.Δ[0])
    point = Sets.Δ[0]
    diagram = Cat().Mor(index, Sets()).constant_functor(point)
    cones = diagram.Cones()
    identity = Sets().Mor(point, point).identity()
    cone = cones.cone(point, lambda _obj: identity)

    assert cones.Mor(cone, cone).cone_category() is cones


def test_cocone_mor_remembers_its_cocone_category() -> None:
    index = DiscreteCategory(Sets.Δ[0])
    point = Sets.Δ[0]
    diagram = Cat().Mor(index, Sets()).constant_functor(point)
    cocones = diagram.Cocones()
    identity = Sets().Mor(point, point).identity()
    cocone = cocones.cocone(point, lambda _obj: identity)

    assert cocones.Mor(cocone, cocone).cocone_category() is cocones
