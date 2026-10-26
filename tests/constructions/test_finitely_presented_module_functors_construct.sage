r"""Finitely presented modules expose their biproduct and cokernel functors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_biproduct_bifunctor_adds_ranks() -> None:
    modules = Modules(ZZ).FinitelyPresented()
    left = ZZ.free_module(1)
    right = ZZ.free_module(2)
    biproduct = modules.biproduct_bifunctor()
    pair = biproduct.domain()(left, right)

    assert biproduct.domain() is Cat().product((modules, modules))
    assert biproduct.codomain() is modules
    assert biproduct(pair).module_rank() == cardinal(3)


def test_cokernel_arrow_functor_of_multiplication_by_two_is_z_mod_two() -> None:
    modules = Modules(ZZ).FinitelyPresented()
    line = ZZ.free_module(1)
    doubling = line.Mor(line)({0: 2 * line.module_generator(0)})
    arrows = modules.ArrowCategory()
    cokernel = modules.cokernel_arrow_functor()
    quotient = cokernel(arrows(doubling))

    assert cokernel.domain() is arrows
    assert cokernel.codomain() is modules
    assert quotient.cardinality() == cardinal(2)
