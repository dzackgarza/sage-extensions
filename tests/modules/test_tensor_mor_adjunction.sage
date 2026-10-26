r"""The tensor product of abelian groups and the tensor–Hom adjunction.

$M \otimes N$ represents bilinear maps, and $- \otimes P \dashv \operatorname{Hom}(P, -)$
(Lang, *Algebra*, XVI.1 and XVI.2).  $\mathbb Z/2 \otimes \mathbb Z/4 = \mathbb Z/\gcd(2,4) = \mathbb Z/2$.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(n):
    return Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(n)))


def test_z_mod_2_tensor_z_mod_4_is_z_mod_2_and_represents_bilinear_maps() -> None:
    r"""$e \otimes f$ generates $\mathbb Z/2 \otimes \mathbb Z/4 = \mathbb Z/2$ and has order $2$; the bilinear map
    $(e, f) \mapsto e$ into $\mathbb Z/2$ factors uniquely through it, while $(e, f) \mapsto f \in \mathbb Z/4$
    is not bilinear on $\mathbb Z/2 \times \mathbb Z/4$ because $2e = 0$ and $2f \ne 0$.

    Source: Lang, Algebra, XVI.1; by hand.
    """
    left, right = cyclic(2), cyclic(4)
    e, f = left.module_generator(0), right.module_generator(0)
    tensor = left.tensor_product(right)
    pure = tensor.pure_tensor(e, f)

    assert tuple(tensor.invariant_factors()) == (2,)
    assert pure != tensor.zero()
    assert pure.additive_order() == 2
    assert tensor.universal_bilinear_map()(e, f) == pure

    beta = BilinearMap(left, right, left, {(0, 0): e})
    assert beta(pure) == e
    competing = tensor.Mor(left)({0: e})
    assert beta == competing

    with pytest.raises(ValueError):
        BilinearMap(left, right, right, {(0, 0): f})


def test_tensor_with_z_mod_4_is_left_adjoint_to_hom_from_z_mod_4() -> None:
    r"""For $P = \mathbb Z/4$: the hom bijection $\operatorname{Hom}(M \otimes P, N) \cong
    \operatorname{Hom}(M, \operatorname{Hom}(P, N))$ round-trips and curries, unit and counit are natural,
    $- \otimes P$ is a functor, and both triangle identities hold.

    Source: Mac Lane, Categories for the Working Mathematician, IV.1 (adjunctions); Lang XVI.2.
    """
    P = cyclic(4)
    adjunction = P.tensor_mor_adjunction()
    tensor_by = adjunction.left_adjoint()
    hom_from = adjunction.right_adjoint()

    M = ZZ**2
    a, b = M.module_generator(0), M.module_generator(1)
    N = cyclic(4)
    n = N.module_generator(0)
    p = P.module_generator(0)

    beta = BilinearMap(M, P, N, {(0, 0): n, (1, 0): 2 * n})
    transpose = adjunction.mor_set_isomorphism_forward(beta, M)
    assert adjunction.mor_set_isomorphism_inverse(transpose, N) == beta
    assert transpose(a)(p) == n
    assert transpose(b)(p) == 2 * n
    assert transpose(b)(2 * p) == N.zero()

    W = ZZ**3
    c, d, g = W.module_generator(0), W.module_generator(1), W.module_generator(2)
    f = M.Mor(W)({0: c + d, 1: 2 * g})
    left, right = adjunction.unit_transformation().naturality_square(f)
    assert left == right

    two = cyclic(2)
    reduction = N.Mor(two)({0: two.module_generator(0)})
    left, right = adjunction.counit_transformation().naturality_square(reduction)
    assert left == right

    X = ZZ**1
    x = X.module_generator(0)
    h = W.Mor(X)({0: x, 1: 2 * x, 2: -x})
    assert tensor_by(h * f) == tensor_by(h) * tensor_by(f)
    assert hom_from(reduction) * hom_from(N.End().one()) == hom_from(reduction)

    assert adjunction.counit(tensor_by(M)) * tensor_by(adjunction.unit(M)) == tensor_by(M).End().one()
    assert hom_from(adjunction.counit(N)) * adjunction.unit(hom_from(N)) == hom_from(N).End().one()
