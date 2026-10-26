r"""Archived slice/coslice/subobject semantics on the current owned categories."""

from sage_extensions.all import (
    ZZ,
    Modules,
    Sets,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/abstract_categories/slice_categories.sage",
    "live_owner": "sage_extensions/categories/abstract_categories/arrow_categories.py",
    "disposition": "reconciled-live-owner",
}


def test_slice_retains_the_fixed_codomain_and_identity_edge() -> None:
    points = finite_ordered_set(("a", "b"))
    same_points = finite_ordered_set(("a", "b"))
    one = finite_ordered_set(("*",))

    assert points == same_points
    assert points is not same_points
    assert Sets().SliceOver(points).base_object() is points
    assert Sets().SliceOver(same_points).base_object() is same_points

    structure = Sets().Mor(points, one)(lambda _point: one[0])
    obj = Sets().SliceOver(one)(structure)
    swap = Sets().Mor(points, points)(
        lambda point: points[1] if point == points[0] else points[0]
    )
    hom = obj.category().Mor(obj, obj)
    square = hom(swap)

    assert obj.arrow() is structure
    assert square.left() is swap
    assert square.right() == Sets().Mor(one, one).identity()
    assert square * square == hom.identity()


def test_coslice_retains_the_fixed_domain_and_identity_edge() -> None:
    one = finite_ordered_set(("*",))
    points = finite_ordered_set(("a", "b"))
    costructure = Sets().Mor(one, points)(lambda _point: points[0])
    coslice = Sets().CosliceUnder(one)
    obj = coslice(costructure)
    collapse = Sets().Mor(points, points)(lambda _point: points[0])
    hom = coslice.Mor(obj, obj)
    square = hom(collapse)

    assert obj.arrow() is costructure
    assert square.left() == Sets().Mor(one, one).identity()
    assert square.right() is collapse
    assert square * square == square
    assert hom.identity() * square == square


def test_subobject_is_the_object_with_its_selected_monomorphism_into_the_fixed_base() -> None:
    module = ZZ.free_module(2)
    generator = module.module_generator(0)
    submodule = module.subobject_on((generator,))
    inclusion = submodule.inclusion()
    category = Modules(ZZ).Subobjects(module)

    assert submodule in category
    assert category.base_object() is module
    assert category.as_slice_object(submodule).arrow() is inclusion
    identity = category.Mor(submodule, submodule).identity()
    assert identity.factor_morphism() == Modules(ZZ).Mor(submodule, submodule).identity()
    assert submodule.inclusion() is inclusion


def test_superobjects_coverings_and_covered_objects_keep_distinct_arrow_classes() -> None:
    one = finite_ordered_set(("*",))
    points = finite_ordered_set(("a", "b"))
    inclusion = Sets().Mono(one, points)(lambda _point: points[0])
    quotient = Sets().Epi(points, one)(lambda _point: one[0])

    superobjects = Sets().Superobjects(one)
    covering_objects = Sets().CoveringObjects(one)
    covered_objects = Sets().CoveredObjects(points)

    superobject = superobjects(inclusion)
    covering = covering_objects(quotient)
    covered = covered_objects(quotient)

    assert superobject.arrow() is inclusion
    assert covering.arrow() is quotient
    assert covered.arrow() is quotient
    assert Sets().Superobjects(one) is superobjects
    assert Sets().CoveringObjects(one) is covering_objects
    assert Sets().CoveredObjects(points) is covered_objects

    raw_inclusion = Sets().CosliceUnder(one)(inclusion)
    raw_quotient_over_one = Sets().SliceOver(one)(quotient)
    raw_quotient_under_points = Sets().CosliceUnder(points)(quotient)
    assert raw_inclusion in superobjects
    assert raw_inclusion not in Sets().CoveredObjects(one)
    assert raw_quotient_over_one in covering_objects
    assert raw_quotient_under_points in covered_objects
    assert raw_quotient_under_points not in Sets().Superobjects(points)
