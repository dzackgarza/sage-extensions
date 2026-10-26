r"""Archive reconciliation for cone and cocone categories.

The archived product/limit layer required cones and cocones to retain their
structure maps and to have genuine morphisms whose apex maps satisfy the
commuting triangles.  The live owner keeps that construction independently of
whether a universal limit/colimit has been selected.
"""

import pytest

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.functors import (
    DiscreteCategory,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets


def _one_object_diagram(target_category=Sets()):
    labels = finite_ordered_set(("j",))
    index = DiscreteCategory(labels)
    one = finite_ordered_set(("*",))
    return Cat().Mor(index, target_category).constant_functor(one), one


def test_cone_retains_projection_and_nonidentity_apex_maps() -> None:
    diagram, one = _one_object_diagram()
    points = finite_ordered_set(("a", "b"))
    leg = Sets().Mor(points, one)(lambda _point: "*")
    cones = (diagram).Cones()
    cone = cones.cone(points, lambda _obj: leg)
    hom = cones.Mor(cone, cone)
    swap = Sets().Mor(points, points)(lambda point: "b" if point == "a" else "a")

    assert cone.apex() is points
    assert cone.structure_morphism(diagram.domain()("j")) is leg
    assert cone.structure_morphisms()["j"] is leg
    assert hom(swap).apex_map() is swap
    assert hom(swap) * hom(swap) == hom.identity()


def test_cocone_retains_injection_and_composes_apex_maps() -> None:
    diagram, one = _one_object_diagram()
    points = finite_ordered_set(("a", "b"))
    leg = Sets().Mor(one, points)(lambda _point: "a")
    cocones = (diagram).Cocones()
    cocone = cocones.cocone(points, lambda _obj: leg)
    hom = cocones.Mor(cocone, cocone)
    collapse_map = Sets().Mor(points, points)(lambda _point: "a")
    collapse = hom(collapse_map)

    assert cocone.apex() is points
    assert cocone.costructure_morphism(diagram.domain()("j")) is leg
    assert cocone.costructure_morphisms()["j"] is leg
    assert hom.identity() * collapse == collapse
    assert collapse * collapse == collapse


def test_cone_apex_map_must_belong_to_the_target_category_even_for_empty_diagram() -> None:
    points = finite_ordered_set(("a", "b"))
    empty = finite_ordered_set(())
    injections = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())
    diagram = Cat().Mor(DiscreteCategory(empty), injections).constant_functor(points)
    cones = (diagram).Cones()
    cone = cones.cone(points, lambda _obj: injections.identity(points))
    hom = cones.Mor(cone, cone)
    swap = Sets().Mor(points, points)(lambda point: "b" if point == "a" else "a")
    collapse = Sets().Mor(points, points)(lambda _point: "a")

    assert hom(swap).apex_map() is swap
    with pytest.raises(ValueError):
        hom(collapse)
