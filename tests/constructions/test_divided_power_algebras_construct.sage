r"""The divided-power algebra is a graded commutative algebra containing every Gamma^n(M)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_divided_power_algebra_contains_the_second_divided_power() -> None:
    module = ZZ.free_module(2)
    algebra = module.divided_power_algebra()
    divided_square = module.divided_power_module(2)
    gamma2 = module.divided_power_element(2, module.module_generator(0))

    assert algebra in DividedPowerAlgebras(ZZ)
    assert algebra in GradedAlgebras(ZZ)
    assert algebra in Algebras(ZZ).Associative().Unital().Commutative()
    assert divided_square.ambient_power_algebra() is algebra
    assert gamma2 in algebra.graded_piece(2)
    assert isinstance(algebra.one(), algebra.ElementType)


def test_divided_power_algebra_morphisms_have_identity() -> None:
    algebra = ZZ.free_module(2).divided_power_algebra()
    identity = algebra.Mor(algebra).identity()

    assert identity(algebra.one()) == algebra.one()
    assert identity * identity == identity

