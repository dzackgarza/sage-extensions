r"""Duals, biproducts, kernels and cokernels of modules over the integers."""

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(order):
    r"""``Z/order`` as ``Z / order Z``, with the class of ``1``."""
    line = Modules(ZZ)(ZZ**1)
    (e,) = line.basis()
    quotient = line / line.span((order * e,))
    return quotient, quotient.projection()(e)


def test_finite_free_dualization_is_contravariant_and_biduality_is_natural() -> None:
    r"""``f^*`` is the transpose of ``f``, ``(g f)^* = f^* g^*``, and ``eta`` is natural.

    For ``f(x) = u + 2v``, ``f(y) = 3u - v``: ``f^*(u^*) = x^* + 3 y^*`` and
    ``f^*(v^*) = 2 x^* - y^*``.
    """
    m = Modules(ZZ)(ZZ**2)
    n = Modules(ZZ)(ZZ**2)
    p = Modules(ZZ)(ZZ**2)
    x, y = m.basis()
    u, v = n.basis()
    r, s = p.basis()
    f = m.Mor(n)({x: u + 2 * v, y: 3 * u - v})
    g = n.Mor(p)({u: 2 * r + s, v: r - 4 * s})
    dual = Modules(ZZ).dualization()
    x_star, y_star = m.dual_basis()
    u_star, v_star = n.dual_basis()

    assert dual(f)(u_star) == x_star + 3 * y_star
    assert dual(f)(v_star) == 2 * x_star - y_star
    assert dual(g * f) == dual(f) * dual(g)
    assert dual(dual(f)) * dual.double_dual_morphism(m) == dual.double_dual_morphism(n) * f


def test_module_biproduct_is_both_product_and_coproduct() -> None:
    r"""``Z/4 + Z/2``: ``p_i i_j = delta_ij``, and summand maps induce the (co)product maps."""
    z4, a = cyclic(4)
    z2, b = cyclic(2)
    direct_sum = z4 + z2
    i0, i1 = direct_sum.left_inclusion(), direct_sum.right_inclusion()
    p0, p1 = direct_sum.left_projection(), direct_sum.right_projection()

    assert direct_sum.cardinality() == 8
    assert p0 * i0 == z4.Mor(z4).identity()
    assert p1 * i1 == z2.Mor(z2).identity()
    assert p1(i0(a)) == z2.zero()
    assert p0(i1(b)) == z4.zero()

    doubling = z2.Mor(z4)({b: 2 * a})
    coproduct_map = direct_sum.from_summands(z4.Mor(z4).identity(), doubling)
    assert coproduct_map(i0(a)) == a
    assert coproduct_map(i1(b)) == 2 * a
    assert coproduct_map(i0(a) + i1(b)) == 3 * a

    reduction = z4.Mor(z2)({a: b})
    product_map = direct_sum.to_product(z4.Mor(z4).identity(), reduction)
    assert p0(product_map(a)) == a
    assert p1(product_map(a)) == b
    assert product_map.kernel().cardinality() == 1


def test_kernel_and_cokernel_are_functorial_on_commutative_module_squares() -> None:
    r"""``ker(Z^2 -> Z)`` has rank 1; ``coker(2: Z -> Z) = Z/2``; ``coker(2: Z/4 -> Z/4) = Z/2``.

    Kernel and cokernel are functors on the arrow category: the square
    ``(diag(2, 3), 2)`` over the first projection induces multiplication by 3
    on its kernel ``Z y``, and multiplication by 3 on ``Z/4`` descends to the
    identity of ``Z/2``.
    """
    plane = Modules(ZZ)(ZZ**2)
    line = Modules(ZZ)(ZZ**1)
    x, y = plane.basis()
    (z,) = line.basis()
    projection = plane.Mor(line)({x: z, y: line.zero()})
    left = plane.Mor(plane)({x: 2 * x, y: 3 * y})
    right = line.Mor(line)({z: 2 * z})
    left_again = plane.Mor(plane)({x: 5 * x, y: 7 * y})
    right_again = line.Mor(line)({z: 5 * z})
    arrows = Modules(ZZ).ArrowCategory()
    kernel = arrows.kernel_functor()
    cokernel = arrows.cokernel_functor()

    arrow = arrows(projection)
    first_square = arrows.morphism(arrow, arrow, left, right)
    second_square = arrows.morphism(arrow, arrow, left_again, right_again)
    kernel_object = kernel(arrow)
    (k,) = kernel_object.basis()

    assert projection * left == right * projection
    assert kernel_object.module_rank() == 1
    assert kernel_object.inclusion()(k) in (y, -y)
    assert kernel(first_square)(k) == 3 * k
    assert kernel(arrows.compose(second_square, first_square)) == kernel(second_square) * kernel(first_square)
    assert kernel(arrows.compose(second_square, first_square))(k) == 21 * k

    twice = line.Mor(line)({z: 2 * z})
    twice_arrow = arrows(twice)
    assert cokernel(twice_arrow).cardinality() == 2
    tripling = line.Mor(line)({z: 3 * z})
    assert cokernel(arrows.morphism(twice_arrow, twice_arrow, tripling, tripling)) == (
        cokernel(twice_arrow).Mor(cokernel(twice_arrow)).identity()
    )

    z4, a = cyclic(4)
    torsion_twice = z4.Mor(z4)({a: 2 * a})
    torsion_tripling = z4.Mor(z4)({a: 3 * a})
    torsion_arrow = arrows(torsion_twice)
    torsion_cokernel = cokernel(torsion_arrow)
    assert torsion_cokernel.cardinality() == 2
    assert cokernel(arrows.morphism(torsion_arrow, torsion_arrow, torsion_tripling, torsion_tripling)) == (
        torsion_cokernel.Mor(torsion_cokernel).identity()
    )
