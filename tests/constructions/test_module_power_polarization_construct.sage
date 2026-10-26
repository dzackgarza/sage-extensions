r"""Divided-power invariants and tensor polarization compose to factorial and symmetrization."""

from sage_extensions.all import *  # noqa: F401,F403


def test_degree_two_power_aliases_are_the_general_inclusion_and_polarization() -> None:
    module = ZZ.free_module(2)

    assert module.divided_square_invariant_inclusion() == module.divided_power_invariant_inclusion(2)
    assert module.tensor_square_polarization() == module.tensor_power_polarization(2)


def test_degree_two_polarization_and_inclusion_compose_to_factorial_and_symmetrizer() -> None:
    module = ZZ.free_module(2)
    divided = module.divided_power_module(2)
    tensor_square = module.tensor_power(2)
    inclusion = module.divided_power_invariant_inclusion(2)
    polarization = module.tensor_power_polarization(2)
    transposition = next(
        permutation
        for permutation in Groups.S(2)
        if permutation != Groups.S(2).one()
    )
    swap = module.tensor_power_permutation(2, transposition)

    assert polarization * inclusion == 2 * divided.End().one()
    assert inclusion * polarization == tensor_square.End().one() + swap
