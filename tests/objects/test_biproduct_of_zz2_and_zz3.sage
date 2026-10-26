from sage_extensions.all import *


def factors():
    return ZZ ^ 2, ZZ ^ 3


def biproduct():
    return Modules(ZZ).biproduct(factors())


def test_the_biproduct_is_the_product() -> None:
    r"""In an additive category finite products and coproducts coincide."""
    assert biproduct() == Modules(ZZ).product(factors())


def test_the_biproduct_is_the_coproduct() -> None:
    assert biproduct() == Modules(ZZ).coproduct(factors())


def test_the_categories_of_the_biproduct() -> None:
    assert biproduct() in Modules(ZZ)
    assert biproduct() in FreeModules(ZZ)


def test_the_rank_is_the_sum_of_the_ranks() -> None:
    assert biproduct().module_rank() == 5


def test_the_projections_and_inclusions() -> None:
    r"""$p_1 i_1 = \mathrm{id}$, $p_2 i_1 = 0$, $i_1p_1 + i_2p_2 = \mathrm{id}$."""
    left, right = factors()
    both = biproduct()
    assert both.left_projection() * both.left_inclusion() == left.Mor(left).identity()
    assert both.right_projection() * both.left_inclusion() == left.Mor(right).zero()
    assert both.left_inclusion() * both.left_projection() + both.right_inclusion() * both.right_projection() == both.Mor(both).identity()


def test_the_biproduct_has_one_endomorphism_category() -> None:
    both = biproduct()
    endomorphisms = both.Mor(both)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert both.Mor(both) is endomorphisms
    assert identity * identity == identity
