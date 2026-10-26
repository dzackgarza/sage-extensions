r"""Finite products and coproducts of sets and of modules."""

from sage_extensions.all import *  # noqa: F401,F403


def test_binary_set_product_coproduct_and_diagonal_are_functorial() -> None:
    x = Sets.Δ[1]
    y = Sets.Δ[2]
    z = Sets.Δ[3]
    product = Sets().product_functor()
    coproduct = Sets().coproduct_functor()
    diagonal = Sets().diagonal_functor()

    pair = product.domain()(x, y)
    product_xy = product(pair)
    coproduct_xy = coproduct(pair)
    assert product_xy.cardinality() == 6
    assert coproduct_xy.cardinality() == 5

    fx = Sets().Mor(x, y)(lambda value: y(int(value) + 1))
    fy = Sets().Mor(y, z)(lambda value: z(int(value) + 1))
    target_pair = product.domain()(y, z)
    pair_map = product.domain().Mor(pair, target_pair)(fx, fy)
    carried = product(pair_map)
    element = product_xy((x(0), y(1)))
    assert carried(element)[0] == y(1)
    assert carried(element)[1] == z(2)

    carried_sum = coproduct(pair_map)
    assert carried_sum(coproduct_xy.injection(0)(x(1))).summand_element() == y(2)

    diagonal_map = diagonal(fx)
    assert diagonal_map.first() is fx
    assert diagonal_map.second() is fx


def test_finite_product_and_coproduct_of_modules_coincide() -> None:
    r"""``Z x Z = Z + Z``: the canonical map from the coproduct to the product is an isomorphism.

    The canonical map has components ``delta_ij``; for modules it is invertible
    on finite families.  The product of ``2`` and ``3`` acts componentwise,
    with cokernel ``Z/2 + Z/3``.
    """
    left = Modules(ZZ)(ZZ**1)
    right = Modules(ZZ)(ZZ**1)
    (x,) = left.basis()
    (y,) = right.basis()
    product = Modules(ZZ).product((left, right))
    coproduct = Modules(ZZ).coproduct((left, right))
    p0, p1 = product.left_projection(), product.right_projection()
    zero_left_right = left.Mor(right)({x: right.zero()})
    zero_right_left = right.Mor(left)({y: left.zero()})

    comparison = coproduct.from_summands(
        product.to_product(left.Mor(left).identity(), zero_left_right),
        product.to_product(zero_right_left, right.Mor(right).identity()),
    )
    assert comparison.is_isomorphism()
    assert product.is_isomorphic_to(coproduct)

    twice = left.Mor(left)({x: 2 * x})
    thrice = right.Mor(right)({y: 3 * y})
    product_map = product.to_product(twice * p0, thrice * p1)
    element = comparison(coproduct.left_inclusion()(x) + coproduct.right_inclusion()(y))
    assert p0(product_map(element)) == 2 * x
    assert p1(product_map(element)) == 3 * y
    assert product_map.cokernel().cardinality() == 6


def test_biproduct_identities_for_two_countable_free_modules() -> None:
    r"""On ``Z^(N) + Z^(N)``: ``p_i i_j = delta_ij``, checked on basis vectors of index 5 and 7."""
    free = Sets().free_module_adjunction(ZZ).left_adjoint()
    left = free(NN)
    right = free(NN)
    direct_sum = left + right
    e5 = left.basis()[NN(5)]
    f7 = right.basis()[NN(7)]
    i0, i1 = direct_sum.left_inclusion(), direct_sum.right_inclusion()
    p0, p1 = direct_sum.left_projection(), direct_sum.right_projection()

    assert p0(i0(e5)) == e5
    assert p1(i1(f7)) == f7
    assert p0(i1(f7)) == left.zero()
    assert p1(i0(e5)) == right.zero()
    assert i0(p0(i0(e5) + i1(f7))) + i1(p1(i0(e5) + i1(f7))) == i0(e5) + i1(f7)
