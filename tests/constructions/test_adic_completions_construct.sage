r"""The 3-adic completion of Z is the inverse limit of Z/3^n with its canonical maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _completion():
    return ZZ.adic_completion(ZZ.ideal(3))


def test_three_adic_completion_remembers_source_ideal_and_completion_map() -> None:
    completion = _completion()
    completion_map = completion.completion_map()

    assert completion in AdicCompletions()
    assert completion.completion_source() is ZZ
    assert completion.ideal_of_definition() == completion.ideal(completion(3))
    assert completion.extended_ideal() == completion.ideal(completion(3))
    assert completion_map.domain() is ZZ
    assert completion_map.codomain() is completion
    assert completion_map(ZZ(5)).is_unit()
    assert not completion_map(ZZ(3)).is_unit()
    assert completion.algebra_structure_morphism()(ZZ(5)) == completion_map(ZZ(5))
    assert completion.completion_map_kernel() == ZZ.ideal(0)
    assert completion.is_completion_map_injective()
    assert completion.is_adically_separated()
    assert completion.is_flat_over_source()


def test_three_adic_truncations_are_z_mod_three_to_the_n() -> None:
    completion = _completion()
    truncation_two = completion.adic_truncation(2)
    truncation_three = completion.adic_truncation(3)
    projection_two = completion.adic_projection(2)
    transition = completion.adic_transition_map(3, 2)

    assert truncation_two.cardinality() == cardinal(9)
    assert truncation_three.cardinality() == cardinal(27)
    assert completion.adic_artin_truncation(2) == truncation_two
    assert projection_two.domain() is completion
    assert projection_two.codomain() is truncation_two
    assert projection_two(completion(4)) == truncation_two(4)
    assert transition.domain() is truncation_three
    assert transition.codomain() is truncation_two
    assert transition(truncation_three(4)) == truncation_two(4)


def test_three_adic_residue_maps_reduce_modulo_three() -> None:
    completion = _completion()
    residue = completion.residue_map()
    source_residue = completion.source_residue_map()

    assert residue(completion(5)) == residue.codomain()(2)
    assert source_residue(ZZ(5)) == source_residue.codomain()(2)


def test_identity_of_z_induces_identity_on_three_adic_completion() -> None:
    completion = _completion()
    induced = completion.induced_map(ZZ.Mor(ZZ).identity(), completion)

    assert induced.domain() is completion
    assert induced.codomain() is completion
    assert induced(completion(5)) == completion(5)

