r"""Tensor products and direct sums of linear maps of free abelian groups.

For $f: V \to V$ and $g: W \to W$ the map $f \otimes g$ sends $v \otimes w$ to $f(v) \otimes g(w)$;
$\otimes$ is a bifunctor, so $(h \otimes k)(f \otimes g) = hf \otimes kg$ and
$\mathrm{id} \otimes \mathrm{id} = \mathrm{id}$, and for $\operatorname{rank} V = m$,
$\operatorname{rank} W = n$ one has $\det(f \otimes g) = (\det f)^n (\det g)^m$ (the Kronecker product
formula).  The direct sum $f \oplus g$ acts blockwise, with $\det(f \oplus g) = \det f \det g$.  Here
$f$ swaps the basis of $\mathbb Z^2$ ($\det f = -1$) and $g = 3$ on $\mathbb Z$, so
$\det(f \otimes g) = (-1)^1 3^2 = -9$ and $\det(f \oplus g) = -3$.  Values by hand.
"""

from sage_extensions.all import *  # noqa: F401,F403


def swap_and_triple():
    plane, line = ZZ ^ 2, ZZ ^ 1
    a, b = plane.module_generator(0), plane.module_generator(1)
    w = line.module_generator(0)
    return plane.End()({0: b, 1: a}), line.End()({0: 3 * w})


def test_the_tensor_product_of_maps_acts_on_pure_tensors() -> None:
    r"""$(f \otimes g)(a \otimes w) = b \otimes 3w = 3 (b \otimes w)$, and $\det(f \otimes g) = -9$."""
    f, g = swap_and_triple()
    plane, line = f.domain(), g.domain()
    a, b = plane.module_generator(0), plane.module_generator(1)
    w = line.module_generator(0)
    product = Modules(ZZ).tensor_product((plane, line))
    tensored = f.tensor_product_map(g)

    assert tensored.domain() == product
    assert tensored(product.pure_tensor(a, w)) == 3 * product.pure_tensor(b, w)
    assert tensored.determinant() == -9


def test_the_tensor_product_of_maps_is_a_bifunctor() -> None:
    r"""$(h \otimes g)(f \otimes g) = hf \otimes g^2$ for $h = \operatorname{diag}(2, 1)$, and
    $\mathrm{id} \otimes \mathrm{id} = \mathrm{id}$."""
    f, g = swap_and_triple()
    plane, line = f.domain(), g.domain()
    h = plane.End()({0: 2 * plane.module_generator(0), 1: plane.module_generator(1)})
    product = Modules(ZZ).tensor_product((plane, line))

    assert h.tensor_product_map(g) * f.tensor_product_map(g) == (h * f).tensor_product_map(g * g)
    assert plane.End().one().tensor_product_map(line.End().one()) == product.End().one()


def test_the_direct_sum_of_maps_acts_blockwise() -> None:
    r"""$(f \oplus g)(a, 0) = (b, 0)$, $(f \oplus g)(0, w) = (0, 3w)$, and $\det(f \oplus g) = -3$."""
    f, g = swap_and_triple()
    plane, line = f.domain(), g.domain()
    a, b = plane.module_generator(0), plane.module_generator(1)
    w = line.module_generator(0)
    total = Modules(ZZ).biproduct((plane, line))
    summed = f.biproduct_map(g)

    assert summed(total.injection(0)(a)) == total.injection(0)(b)
    assert summed(total.injection(1)(w)) == 3 * total.injection(1)(w)
    assert summed.determinant() == -3
