from sage_extensions.all import *


def line():
    return ZZ ^ 1


def by_cokernel():
    r"""$\operatorname{coker}(\mathbb Z \xrightarrow{6} \mathbb Z)$."""
    module = line()
    return module.Mor(module)({0: 6 * module.module_generator(0)}).cokernel()


def test_the_cokernel_and_the_quotient_agree() -> None:
    module = line()
    assert by_cokernel() == module / module.subobject_on([6 * module.module_generator(0)])


def test_the_quotient_of_the_regular_module_by_the_ideal() -> None:
    quotient = ZZ.regular_module() / ZZ.ideal(6)
    assert quotient in Modules(ZZ)
    assert quotient.cardinality() == 6
    assert quotient.annihilator() == ZZ.ideal(6)


def test_the_categories_of_zz6() -> None:
    module = by_cokernel()
    assert module in Modules(ZZ)
    assert module in FinitelyPresentedModules(ZZ)
    assert module in TorsionModules(ZZ)
    assert module not in FreeModules(ZZ)


def test_the_invariants_of_zz6() -> None:
    module = by_cokernel()
    generator = module.module_generator(0)
    assert module.cardinality() == 6
    assert module.module_generators().cardinality() == 1
    assert module.annihilator() == ZZ.ideal(6)
    assert module.is_torsion()
    assert not module.is_free()
    assert 6 * generator == module.zero()
    assert 2 * generator != module.zero()
    assert 3 * generator != module.zero()


def test_the_invariant_factors_of_zz6() -> None:
    factors = by_cokernel().invariant_factors()
    assert factors.cardinality() == 1
    assert 6 in factors


def test_zz6_dies_over_the_rationals() -> None:
    r"""$\mathbb Q\otimes\mathbb Z/6 = 0$."""
    assert by_cokernel().base_change(ZZ.Mor(QQ)(lambda n: QQ(n))).cardinality() == 1


def test_the_endomorphisms_and_automorphisms_of_zz6() -> None:
    r"""$\operatorname{End}(\mathbb Z/6) = \mathbb Z/6$ and $\operatorname{Aut}(\mathbb Z/6) = (\mathbb Z/6)^\times$ of order $\varphi(6) = 2$."""
    module = by_cokernel()
    assert module.End().cardinality() == 6
    assert module.Aut().order() == 2


def test_zz6_has_one_endomorphism_category() -> None:
    module = by_cokernel()
    endomorphisms = module.Mor(module)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert module.Mor(module) is endomorphisms
    assert identity * identity == identity
