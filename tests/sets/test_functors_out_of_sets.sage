r"""The functors and adjunctions whose domain is Set, asked of Set.

Each row states the functor's domain and codomain, its action on a set map
rather than only on objects, and the construction's own content on a small
specimen.  Each adjunction states the endpoints of its unit and counit and
the value of one of them.
"""


from sage_extensions.all import *



def test_the_free_module_adjunction_has_a_unit_of_generators_and_an_evaluating_counit() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    assert adjunction.left_adjoint().domain() == Sets()
    assert adjunction.left_adjoint().codomain() == Modules(ZZ)
    assert adjunction.right_adjoint().domain() == Modules(ZZ)
    assert adjunction.right_adjoint().codomain() == Sets()

    labels = Sets.Δ[1]
    free = adjunction.left_adjoint()(labels)
    unit = adjunction.unit(labels)
    assert unit.domain() is labels
    assert unit.codomain() is adjunction.right_adjoint()(free)
    assert unit(labels(0)) == free.module_generator(labels(0))

    counit = adjunction.counit(free)
    assert counit.codomain() is free
    assert counit.domain() is adjunction.left_adjoint()(adjunction.right_adjoint()(free))
    element = free.module_generator(labels(0)) + free.module_generator(labels(1))
    assert counit(counit.domain().module_generator(element)) == element




def test_the_free_group_adjunction_has_a_unit_of_letters_and_a_multiplying_counit() -> None:
    adjunction = Sets().free_group_adjunction()
    assert adjunction.left_adjoint().domain() == Sets()
    assert adjunction.left_adjoint().codomain() == Groups()
    assert adjunction.right_adjoint().domain() == Groups()
    assert adjunction.right_adjoint().codomain() == Sets()

    letters = Sets.Δ[1]
    free = adjunction.left_adjoint()(letters)
    unit = adjunction.unit(letters)
    assert unit.domain() is letters
    assert unit.codomain() is adjunction.right_adjoint()(free)
    assert unit(letters(0)) == free.free_generator(letters(0))

    symmetric = Groups.S(3)
    counit = adjunction.counit(symmetric)
    assert counit.codomain() is symmetric
    assert counit.domain() is adjunction.left_adjoint()(adjunction.right_adjoint()(symmetric))
    transposition = next(
        element for element in symmetric.group_generators() if element.order() == 2
    )
    assert counit(counit.domain().free_generator(transposition)) == transposition




def test_the_power_set_functor_has_all_of_sets_for_its_domain() -> None:
    functor = FiniteSets().power_set_functor()
    assert functor is Sets().power_set_functor()
    assert functor.domain() == Sets()
    assert functor.codomain() == Sets()

    source = Sets.Δ[3]
    target = Sets.Δ[1]
    parity = Sets().Mor(source, target)(lambda value: target(int(value) % 2))
    subsets = functor(source)
    images = functor(target)
    carried = functor(parity)

    assert subsets.cardinality() == cardinal(16)
    assert carried.domain() is subsets
    assert carried.codomain() is images
    assert carried(subsets({0, 2})) == images({0})
    assert carried(subsets({0, 1, 2})) == images({0, 1})
