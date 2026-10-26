r"""Tensor and symmetric algebras on the torsion module Z/2 + Z/3."""

from sage_extensions.all import *  # noqa: F401,F403


def test_degree_two_of_the_tensor_and_symmetric_algebra_on_z2_plus_z3_has_order_six() -> None:
    r"""Mixed products vanish because Z/2 (x) Z/3 = 0, so T^2 = Sym^2 = Z/2 + Z/3.

    Derivation: (Z/m) (x) (Z/n) = Z/gcd(m, n); Sym^2(Z/m) = Z/m; Sym^2(A + B) =
    Sym^2 A + A (x) B + Sym^2 B.
    """
    module = Modules(ZZ).direct_sum_of_cyclics((2, 3))
    for algebra in (module.tensor_algebra(), module.symmetric_algebra()):
        a = algebra.algebra_generator(0)
        b = algebra.algebra_generator(1)
        assert a * b == algebra.zero()
        assert b * a == algebra.zero()
        assert a * a != algebra.zero()
        assert 2 * (a * a) == algebra.zero()
        assert b * b != algebra.zero()
        assert 3 * (b * b) == algebra.zero()
        assert algebra.graded_piece(2).cardinality() == 6


def test_zero_finite_torsion_module_enumerates_only_zero_without_smith_workspace() -> None:
    zero = Modules(ZZ).FinitelyPresented().Torsion().direct_sum_of_cyclics(())
    elements = zero.elements()
    assert elements.cardinality() == 1
    assert tuple(elements)[0] == zero.zero()


def test_rank_zero_discriminant_class_has_additive_order_one() -> None:
    lattice = Lattices(ZZ)(ZZ.free_module(0))
    discriminant = lattice.discriminant_group()
    element = tuple(discriminant.elements())[0]
    assert element.additive_order() == ZZ.one()


def test_nonzero_discriminant_class_keeps_presented_additive_order() -> None:
    lattice = Lattices(ZZ)("A1")
    discriminant = lattice.discriminant_group()
    orders = tuple(element.additive_order() for element in discriminant.elements())
    assert {int(order) for order in orders} == {1, 2}


def test_finite_free_integer_saturation_returns_primitive_closure() -> None:
    ambient = Modules(ZZ)(ZZ.free_module(2))
    e, f = ambient.module_generators()
    submodule = ambient.subobject_on((ambient.scalar_multiple(ZZ.one() + ZZ.one(), e), f))
    saturated = submodule.inclusion().saturation()
    assert saturated.is_primitive()
    assert saturated.module_rank() == ambient.module_rank()
