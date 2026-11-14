r"""The six translates of diag(1,2,3) ZZ^3 carry the actual quotient action."""

from sage_extensions.all import *


def test_axis_lattice_translates_and_their_induced_actions():
    r"""S3 permutes the axis indices and the central sign fixes each lattice."""
    rational = Lattices(QQ)(3)
    basis = tuple(rational.module_generators())
    e, f, w = basis
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(rational)
    selected = space.subobject_on((space(e), space(2 * f), space(3 * w)))
    bound = space.subobject_on(tuple(space(point) for point in basis))
    group_generators = tuple(rational.O()(images) for images in (
        (f, w, e), (f, e, w), (-e, -f, -w),
    ))
    group = rational.O().subgroup(group_generators)
    action = IntegralStructureAction(group, selected.inclusion()).with_stable_containing_bound(bound.inclusion())
    representation = action.finite_representation()
    quotient = action.finite_module()
    submodules = representation.orbit_submodules()
    invariant = action.invariant_module()
    residue_basis = tuple(action.finite_projection()(invariant.lift(space(point))) for point in basis)
    expected = tuple(quotient.subobject_on(tuple(
        coefficient * point for coefficient, point in zip(indices, residue_basis, strict=True)
    )) for indices in (
        (1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1),
    ))

    assert representation.g_set().cardinality() == cardinal(6)
    assert quotient.cardinality() == cardinal(216)
    assert all(submodule.cardinality() == cardinal(36) for submodule in submodules)
    assert all(any(submodule.is_contained_in(candidate) for candidate in expected) for submodule in submodules)
    assert all(any(candidate.is_contained_in(submodule) for submodule in submodules) for candidate in expected)
    assert submodules[0] is action.selected_submodule()
    points = tuple(representation.g_set())
    for position, point in enumerate(points):
        submodule = submodules[position]
        for generator in group_generators:
            image = action.quotient_automorphism(generator)
            target = int(representation.g_set().act(generator, point))
            assert all(submodules[target].inclusion().is_in_image(
                image(submodule.inclusion()(element))
            ) for element in submodule.module_generators())
