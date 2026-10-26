r"""The five functors out of ``Mod_R``, asked for on that category.

A functor is a method of its domain category, so ``Mod_R`` is where the
underlying set, the linear dual, and the three free-algebra constructions are
spelled.  Each is applied here to one specimen: the free ``ZZ``-module of rank
two, and the involution of it that exchanges the two basis vectors.
"""

from sage_extensions.all import *


def _plane_with_swap():
    r"""``ZZ^2`` and the involution exchanging its two basis vectors."""
    plane = ZZ.free_module(2)
    swap = Modules(ZZ).End(plane)(
        {0: plane.module_generator(1), 1: plane.module_generator(0)}
    )
    return plane, swap


def test_the_symmetric_algebra_functor_is_asked_of_the_module_category() -> None:
    r"""``Sym_ZZ`` is commutative and ``Sym^2(ZZ^2)`` has rank three."""
    plane, swap = _plane_with_swap()
    symmetric = Modules(ZZ).symmetric_algebra()

    assert symmetric.codomain() == Algebras(Modules(ZZ).base_ring()).Associative().Unital().Commutative()
    algebra = symmetric(plane)
    assert algebra in Algebras(ZZ).Associative().Unital().Commutative()
    assert algebra.graded_piece(1).module_rank() == 2
    assert algebra.graded_piece(2).module_rank() == 3
    x, y = algebra.algebra_generator(0), algebra.algebra_generator(1)
    assert x * y == y * x

    image = symmetric(swap)
    assert image.domain() is algebra
    assert image.codomain() is algebra
    assert image(x) == y


def test_the_tensor_algebra_functor_is_asked_of_the_module_category() -> None:
    r"""``T_ZZ`` is noncommutative and ``T^2(ZZ^2)`` has rank four."""
    plane, swap = _plane_with_swap()
    tensor = Modules(ZZ).tensor_algebra()

    assert tensor.codomain() == Algebras(Modules(ZZ).base_ring())
    algebra = tensor(plane)
    assert algebra in Algebras(ZZ)
    assert algebra.graded_piece(1).module_rank() == 2
    assert algebra.graded_piece(2).module_rank() == 4
    x, y = algebra.algebra_generator(0), algebra.algebra_generator(1)
    assert x * y != y * x

    image = tensor(swap)
    assert image.domain() is algebra
    assert image.codomain() is algebra
    assert image(x) == y


def test_the_exterior_algebra_functor_is_asked_of_the_module_category() -> None:
    r"""``Lambda_ZZ`` is alternating and ``Lambda^2(ZZ^2)`` has rank one."""
    plane, swap = _plane_with_swap()
    exterior = Modules(ZZ).exterior_algebra()

    assert exterior.codomain() == AlternatingAlgebras(Modules(ZZ).base_ring())
    algebra = exterior(plane)
    assert algebra in AlternatingAlgebras(ZZ)
    assert algebra.graded_piece(1).module_rank() == 2
    assert algebra.graded_piece(2).module_rank() == 1
    x, y = algebra.algebra_generator(0), algebra.algebra_generator(1)
    assert x * x == algebra.zero()
    assert x * y == -(y * x)

    image = exterior(swap)
    assert image.domain() is algebra
    assert image.codomain() is algebra
    assert image(x) == y


def test_the_dual_of_the_shear_e0_to_e0_plus_e1_is_its_transpose() -> None:
    r"""For $f(e_0) = e_0 + e_1$, $f(e_1) = e_1$, the dual map $f^\vee(\varphi) = \varphi \circ f$ sends
    $e_0^* \mapsto e_0^*$ and $e_1^* \mapsto e_0^* + e_1^*$.

    Source: by hand (the matrix of the dual map is the transpose).
    """
    plane = ZZ**2
    shear = plane.End()({0: plane.module_generator(0) + plane.module_generator(1), 1: plane.module_generator(1)})
    dualize = Modules(ZZ).dualization()
    transpose = dualize(shear)
    dual = transpose.domain()
    assert dual.module_rank() == 2
    e0, e1 = dual.module_generator(0), dual.module_generator(1)
    assert transpose(e0) == e0
    assert transpose(e1) == e0 + e1


def test_the_unit_of_the_symmetric_and_tensor_algebra_adjunctions_is_the_degree_one_inclusion() -> None:
    r"""$\eta_M\colon M \to U\operatorname{Sym}(M)$ and $M \to U T(M)$ send $e_i$ to the generator $x_i$ of
    degree one, so they are injective and not surjective.

    Source: Lang, Algebra, XVI.7 and XVI.8 (universal properties of T(M) and S(M)).
    """
    plane = ZZ**2
    for adjunction in (Modules(ZZ).symmetric_algebra_adjunction(), Modules(ZZ).tensor_algebra_adjunction()):
        algebra = adjunction.left_adjoint()(plane)
        unit = adjunction.unit(plane)
        assert unit.is_injective()
        assert not unit.is_surjective()
        assert unit(plane.module_generator(0)) == algebra.algebra_generator(0)
        assert unit(plane.module_generator(1)) == algebra.algebra_generator(1)
