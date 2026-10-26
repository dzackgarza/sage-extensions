r"""A chosen finite presentation controls completion and tensor-Hom operations.

For ``M=QQ[x]/(x^4)``, the selected one-generator presentation makes the
``x``-adic completion equal to ``M``.  Its truncation tower is
``M/x^n M``, with the canonical transition maps, and the same presentation
supplies the tensor-Hom adjunction.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _x4_module():
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = ring.free_module(1)
    presentation = line.End()({0: x**4 * line.module_generator(0)})
    return ring, x, presentation.cokernel()


def test_chosen_presentation_retains_its_presenting_arrow_and_tensor_hom_adjunction() -> None:
    ring, _x, module = _x4_module()
    category = ModulesWithChosenFinitePresentation(ring)
    presentation = module.presentation_object()
    adjunction = module.tensor_mor_adjunction()

    assert module in category
    assert presentation in Modules(ring).ArrowCategory()
    assert adjunction.left_adjoint().domain() is Modules(ring)
    assert adjunction.right_adjoint().codomain() is Modules(ring)
    assert isinstance(module.module_generator(0), module.ElementType)


def test_chosen_presentation_routes_selected_subobject_data_to_its_inclusion() -> None:
    ring, _x, module = _x4_module()
    images = {
        label: module.module_generator(label)
        for label in module.module_generating_set()
    }
    subobject = ModulesWithChosenFinitePresentation(ring)(
        module.presentation(),
        category=ModuleSubobjects(ring),
        subobject_ambient=module,
        subobject_generator_images=images,
    )
    inclusion = subobject.inclusion()

    assert subobject in ModuleSubobjects(ring)
    assert inclusion.domain() is subobject
    assert inclusion.codomain() is module
    assert all(
        inclusion(subobject.module_generator(label)) == module.module_generator(label)
        for label in subobject.module_generating_set()
    )


def test_x4_module_is_unchanged_by_x_adic_completion_and_projects_to_truncations() -> None:
    ring, x, module = _x4_module()
    ideal = ring.ideal(x)
    completed = module.adic_completion(ideal)
    completion = completed.base_ring()
    unit = module.completion_unit(completion)
    projection3 = module.adic_module_projection(completion, 3)
    truncation3 = module.adic_module_truncation(completion, 3)
    base_changed = module.base_change_to_completion(completion)
    generator = module.module_generator(0)

    assert unit.is_isomorphism()
    assert completed == base_changed
    assert projection3.codomain() is truncation3
    assert projection3(unit(x**3 * generator)) == truncation3.zero()
    assert projection3(unit(x**2 * generator)) != truncation3.zero()


def test_adic_truncation_transition_maps_form_the_expected_quotient_tower() -> None:
    ring, x, module = _x4_module()
    completion = module.adic_completion(ring.ideal(x)).base_ring()
    higher = module.adic_module_truncation(completion, 3)
    lower = module.adic_module_truncation(completion, 2)
    transition = module.adic_module_transition_map(completion, 3, 2)
    projection3 = module.adic_module_projection(completion, 3)
    projection2 = module.adic_module_projection(completion, 2)
    unit = module.completion_unit(completion)
    generator = module.module_generator(0)

    assert transition.domain() is higher
    assert transition.codomain() is lower
    assert transition * projection3 == projection2
    assert transition(projection3(unit(x**2 * generator))) == lower.zero()
