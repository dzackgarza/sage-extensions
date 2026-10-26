r"""Tensor and symmetric algebras of finitely presented abelian groups, and their adjunctions."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _cyclic(order):
    r"""``ZZ/n`` as the cokernel of multiplication by ``n`` on ``ZZ``."""
    line = Modules(ZZ).free_module(1)
    return (order * line.Mor(line).identity()).cokernel()


def _torsion_sum(*orders):
    r"""``⊕ ZZ/n_i`` as the cokernel of ``e_i -> n_i e_i`` on the free module on the indices ``i``."""
    order_of = dict(enumerate(orders))
    free = Modules(ZZ).free_module(tuple(order_of))
    return free.Mor(free)(
        {free.module_generator(i): n * free.module_generator(i) for i, n in order_of.items()}
    ).cokernel()


def _adjunction(flavor):
    match flavor:
        case "tensor":
            return Modules(ZZ).tensor_algebra_adjunction()
        case "symmetric":
            return Modules(ZZ).symmetric_algebra_adjunction()


def test_tensor_and_symmetric_algebras_of_z4_squared_are_killed_by_four() -> None:
    r"""For ``M = (ZZ/4)^2``, the relations ``4x = 4y = 0`` generate a two-sided
    ideal, so ``4xy = 4yx = 0`` in ``T(M)`` and ``Sym(M)``; ``T(M)`` is
    noncommutative (``xy ≠ yx``: ``M ⊗ M = (ZZ/4)^4``) and ``Sym(M)`` is commutative."""
    module = _torsion_sum(4, 4)
    tensor, symmetric = module.tensor_algebra(), module.symmetric_algebra()
    tx, ty = tensor.algebra_generator(0), tensor.algebra_generator(1)
    sx, sy = symmetric.algebra_generator(0), symmetric.algebra_generator(1)

    assert 4 * tx * ty == tensor.zero()
    assert 4 * ty * tx == tensor.zero()
    assert 2 * tx * ty != tensor.zero()
    assert tx * ty != ty * tx
    assert 4 * sx * sy == symmetric.zero()
    assert sx * sy == sy * sx
    assert tensor.graded_piece(2).invariant_factors().cardinality() == 4


def test_relation_2x_plus_4y_and_its_multiples_vanish_in_tensor_and_symmetric_algebras() -> None:
    r"""For ``M = ZZ^2/(2x + 4y)``: ``2x + 4y = 0`` in degree one, hence
    ``(2x + 4y)x = y(2x + 4y) = 0`` in ``T(M)`` and ``Sym(M)``; ``x + 2y`` has order 2."""
    free = Modules(ZZ).free_module(("x", "y"))
    relations = Modules(ZZ).free_module(("r",))
    module = relations.Mor(free)(
        {relations.module_generator("r"): 2 * free.module_generator("x") + 4 * free.module_generator("y")}
    ).cokernel()

    for algebra in (module.tensor_algebra(), module.symmetric_algebra()):
        x, y = algebra.algebra_generator("x"), algebra.algebra_generator("y")
        assert 2 * x + 4 * y == algebra.zero()
        assert (2 * x + 4 * y) * x == algebra.zero()
        assert y * (2 * x + 4 * y) == algebra.zero()
        assert x + 2 * y != algebra.zero()
        assert 2 * x != algebra.zero()


@pytest.mark.parametrize("flavor", ("tensor", "symmetric"))
def test_free_algebra_functors_preserve_composition_along_z8_to_z4_to_z2(flavor) -> None:
    r"""``F = T`` or ``Sym`` along the reductions ``ZZ/8 -> ZZ/4 -> ZZ/2``:
    ``F(f)(x^2 + 3x) = y^2 + 3y`` and ``F(g f) = F(g) F(f)``."""
    functor = _adjunction(flavor).left_adjoint()
    source, middle, target = _cyclic(8), _cyclic(4), _cyclic(2)
    first = source.Mor(middle)({source.module_generator(0): middle.module_generator(0)})
    second = middle.Mor(target)({middle.module_generator(0): target.module_generator(0)})
    x = functor(source).algebra_generator(0)
    y = functor(middle).algebra_generator(0)
    z = functor(target).algebra_generator(0)

    assert functor(first)(x * x + 3 * x) == y * y + 3 * y
    assert functor(second)(y) == z
    for probe in (x, x * x, x * x * x + x):
        assert functor(second * first)(probe) == (functor(second) * functor(first))(probe)
    assert functor(second * first)(3 * x) == z


def test_tensor_algebra_map_preserves_word_order() -> None:
    r"""``T(ZZ^2) -> T(ZZ^2)``, ``x ↦ a``, ``y ↦ b``, sends ``xy`` to ``ab ≠ ba``."""
    source = Modules(ZZ).free_module(("x", "y")).tensor_algebra()
    target = Modules(ZZ).free_module(("a", "b")).tensor_algebra()
    x, y = source.algebra_generator("x"), source.algebra_generator("y")
    a, b = target.algebra_generator("a"), target.algebra_generator("b")
    extension = source.Mor(target)({x: a, y: b})

    assert extension(x * y) == a * b
    assert extension(x * y) != b * a
    assert extension(y * x * x) == b * a * a


@pytest.mark.parametrize("flavor", ("tensor", "symmetric"))
def test_free_forgetful_bijection_triangle_and_naturality_on_torsion_modules(flavor) -> None:
    r"""For ``F ⊣ U`` with ``F = T`` or ``Sym``: the linear map ``ZZ/8 -> U(F(ZZ/4))``,
    ``1 ↦ 2g``, extends to ``F(ZZ/8) -> F(ZZ/4)`` with ``x^2 ↦ 4g^2 = 0``; the
    bijection round-trips; the triangle ``ε_{F M} ∘ F(η_M) = id`` holds; and the
    unit is natural along ``ZZ/8 -> ZZ/4``."""
    adjunction = _adjunction(flavor)
    free, underlying = adjunction.left_adjoint(), adjunction.right_adjoint()
    source, target_module = _cyclic(8), _cyclic(4)
    target_algebra = free(target_module)
    g = target_algebra.algebra_generator(0)
    target_underlying = underlying(target_algebra)
    generator = source.module_generator(0)
    linear = source.Mor(target_underlying)({generator: target_underlying(2 * g)})

    extension = adjunction.mor_set_isomorphism_inverse(linear, target_algebra)
    recovered = adjunction.mor_set_isomorphism_forward(extension, source)
    x = free(source).algebra_generator(0)
    assert extension(x) == 2 * g
    assert extension(x * x) == target_algebra.zero()
    assert recovered(3 * generator) == linear(3 * generator)

    triangle = adjunction.counit(free(source)) * free(adjunction.unit(source))
    for probe in (x, x * x, x * x * x + 5 * x):
        assert triangle(probe) == probe

    reduction = source.Mor(target_module)({generator: target_module.module_generator(0)})
    left, right = adjunction.unit_transformation().naturality_square(reduction)
    assert left(3 * generator) == right(3 * generator)


@pytest.mark.parametrize("flavor", ("tensor", "symmetric"))
def test_counit_naturality_and_right_triangle_on_dual_numbers_mod_four(flavor) -> None:
    r"""On ``A = (ZZ/4)[ε]/(ε^2)``: the counit is natural for ``ε ↦ -ε``, and
    ``U(ε_A) ∘ η_{U A} = id`` on ``1``, ``ε`` and ``1 + 2ε``."""
    adjunction = _adjunction(flavor)
    polynomials = ZZ["e"]
    e = polynomials.gen()
    algebra = Algebras(ZZ)(polynomials.quotient(polynomials.ideal([4, e**2])))
    epsilon = algebra(e)
    involution = algebra.Mor(algebra)({epsilon: -epsilon})

    assert involution(epsilon) != epsilon
    left, right = adjunction.counit_transformation().naturality_square(involution)
    free_underlying = left.domain()
    for probe in (free_underlying.one(), free_underlying.algebra_generator(adjunction.right_adjoint()(algebra)(epsilon))):
        assert left(probe) == right(probe)

    underlying = adjunction.right_adjoint()
    triangle = underlying(adjunction.counit(algebra)) * adjunction.unit(underlying(algebra))
    for element in (algebra.one(), epsilon, algebra.one() + 2 * epsilon):
        assert triangle(underlying(algebra)(element)) == underlying(algebra)(element)


@pytest.mark.parametrize("flavor", ("tensor", "symmetric"))
def test_iterated_free_algebra_on_z2_plus_z3_kills_mixed_products(flavor) -> None:
    r"""In ``F(U(F(M)))`` for ``M = ZZ/2 ⊕ ZZ/3``, the degree-one generators ``[x]``,
    ``[y]`` coming from ``x, y ∈ M ⊂ U(F(M))`` satisfy ``2[x] = 3[y] = 0`` and
    ``[x][y] = 0``, since ``ZZ/2 ⊗ ZZ/3 = 0``; ``[x]^2 ≠ 0`` and has order 2."""
    adjunction = _adjunction(flavor)
    free, underlying = adjunction.left_adjoint(), adjunction.right_adjoint()
    module = _torsion_sum(2, 3)
    first_underlying = underlying(free(module))
    unit = adjunction.unit(first_underlying)
    first = free(module)
    a = unit(first_underlying(first.algebra_generator(0)))
    b = unit(first_underlying(first.algebra_generator(1)))

    assert 2 * a == a.parent().zero()
    assert 3 * b == b.parent().zero()
    assert a != a.parent().zero()
    iterated = free(first_underlying)
    a, b = iterated(a), iterated(b)
    assert a * b == iterated.zero()
    assert a * a != iterated.zero()
    assert 2 * (a * a) == iterated.zero()
