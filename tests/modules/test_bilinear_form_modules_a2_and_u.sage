r"""Values, twists, index gymnastics, isometries and base change of the forms $A_2$ and $U$.

$A_2 = (\mathbb Z^2, b)$ with Gram matrix $[[2, 1], [1, 2]]$ has determinant $3$; the
hyperbolic plane $U$ has Gram matrix $[[0, 1], [1, 0]]$ and is unimodular.  The twist
$A_2(3)$ has form $3b$ and determinant $3^2 \cdot 3 = 27$.  The correlation
$c: L \to \operatorname{Hom}(L, \mathbb Z)$, $v \mapsto b(v, -)$, has matrix the Gram matrix, so
its cokernel has order $\lvert\det\rvert = 3$.  The Weyl group of $A_2$ contains the swap
$e_0 \leftrightarrow e_1$, and $e_0 \mapsto e_1$, $e_1 \mapsto e_1 - e_0$ is an isometry of order
$6$ (the Coxeter element composed with $-1$); $e_0 \mapsto 2e_0$ is not an isometry.  Base
change along $\mathbb Z \to \mathbb Q$ keeps the Gram matrix, and along $\mathbb Z \to \mathbb F_3$
the determinant becomes $0$.  All values by hand.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def a2():
    module = ZZ ^ 2
    return FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[2, 1], [1, 2]]))


def test_the_values_of_the_a2_form() -> None:
    r"""$b(e_0, e_1) = 1$, $b(e_0, e_0) = 2$, $b(e_0 + e_1, e_0 + e_1) = 6$; $e_0 \perp e_0 - 2e_1$."""
    form = a2()
    e0, e1 = form.module_generator(0), form.module_generator(1)

    assert form.b(e0, e1) == 1
    assert e0.b(e1) == 1
    assert form.norm(e0) == 2
    assert form.norm(e0 + e1) == 6
    assert not e0.is_isotropic()
    assert e0.is_orthogonal_to(e0 - 2 * e1)
    assert not e0.is_orthogonal_to(e1)
    assert form.determinant() == 3
    assert form.gram_tensor() == tensor(ZZ, (), (2, 2), [[2, 1], [1, 2]])


def test_the_twist_by_three_triples_the_form() -> None:
    r"""$A_2(3)$ has $b(e_0, e_1) = 3$, $b(e_0, e_0) = 6$ and determinant $27$."""
    twisted = a2().twist(3)
    t0, t1 = twisted.module_generator(0), twisted.module_generator(1)

    assert twisted.b(t0, t1) == 3
    assert twisted.b(t0, t0) == 6
    assert twisted.determinant() == 27


def test_the_hyperbolic_plane_has_isotropic_basis_vectors_and_raises_by_swapping() -> None:
    r"""In $U$, $f_0^2 = 0$ and $f_0 \cdot f_1 = 1$; $U^{-1} = U$ so raising $(3, 7)$ gives $(7, 3)$."""
    module = ZZ ^ 2
    hyperbolic_plane = FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[0, 1], [1, 0]]))
    f0, f1 = hyperbolic_plane.module_generator(0), hyperbolic_plane.module_generator(1)

    assert f0.is_isotropic()
    assert not (f0 + f1).is_isotropic()
    assert hyperbolic_plane.determinant() == -1
    assert hyperbolic_plane.raise_index(tensor.covector(ZZ, [3, 7])) == tensor.vector(ZZ, [7, 3])
    assert hyperbolic_plane.lower_index(tensor.vector(ZZ, [3, 7])) == tensor.covector(ZZ, [7, 3])


def test_raising_an_index_of_a2_needs_the_rational_inverse_gram_matrix() -> None:
    r"""$G^{-1} = \frac13 [[2, -1], [-1, 2]]$, so raising the covector $(1, 0)$ gives $(2/3, -1/3)$."""
    raised = NondegenerateGenericFibreFormModules(ZZ)(a2()).raise_index_over_fraction_field(tensor.covector(ZZ, [1, 0]))

    assert raised == tensor.vector(QQ, [2 / 3, -1 / 3])


def test_the_correlation_of_a2_has_cokernel_of_order_three() -> None:
    r"""$\operatorname{coker}(A_2 \to A_2^\vee) \cong \mathbb Z/3$."""
    assert a2().correlation_morphism().cokernel().cardinality() == 3


def test_the_swap_and_the_order_six_rotation_are_isometries_of_a2() -> None:
    r"""$\sigma: e_0 \leftrightarrow e_1$ is an involution preserving $b$; $\rho: e_0 \mapsto e_1,
    e_1 \mapsto e_1 - e_0$ preserves $b$, $\rho^3 = -1$ and $\rho^6 = 1$."""
    form = a2()
    e0, e1 = form.module_generator(0), form.module_generator(1)
    isometries = FormModules(ZZ).Mor(form, form)
    swap = isometries({0: e1, 1: e0})
    rotation = isometries({0: e1, 1: e1 - e0})
    identity = isometries.identity()

    assert swap.preserves_form_exactly()
    assert swap(e0) == e1
    assert swap * swap == identity
    assert rotation.preserves_form_exactly()
    cube = rotation * rotation * rotation
    assert cube(e0) == -e0
    assert cube(e1) == -e1
    assert cube * cube == identity


def test_a_map_that_doubles_a_root_is_not_a_morphism_of_the_form() -> None:
    r"""$e_0 \mapsto 2e_0$, $e_1 \mapsto e_1$ sends $b(e_0, e_0) = 2$ to $8$, so it is no isometry."""
    form = a2()
    e0, e1 = form.module_generator(0), form.module_generator(1)

    with pytest.raises(ValueError):
        FormModules(ZZ).Mor(form, form)({0: 2 * e0, 1: e1})


def test_the_identity_is_a_morphism_into_the_twist_along_multiplication_by_three() -> None:
    r"""$(\mathrm{id}, 3): (L, b) \to (L, 3b)$ is a morphism of formed modules: $3 b(x, y) = (3b)(x, y)$."""
    form = a2()
    twisted = form.twist(3)
    values = form.value_module()
    tripling = values.Mor(values)({0: 3 * values.module_generator(0)})
    identity_map = Modules(ZZ).Mor(form, twisted)({0: twisted.module_generator(0), 1: twisted.module_generator(1)})
    morphism = FormModules(ZZ).Mor(form, twisted)((identity_map, tripling))

    assert morphism.preserves_form_exactly()
    assert morphism.value_morphism()(values.module_generator(0)) == 3 * values.module_generator(0)


def test_a2_over_the_rationals_keeps_its_determinant() -> None:
    r"""$\det(A_2 \otimes \mathbb Q) = 3$."""
    rational = a2().base_change(ZZ.Mor(QQ)(lambda n: QQ(n)))

    assert rational.determinant() == 3


def test_a2_over_the_rationals_is_nondegenerate() -> None:
    r"""$\det(A_2 \otimes \mathbb Q) = 3 \neq 0$."""
    assert a2().base_change(ZZ.Mor(QQ)(lambda n: QQ(n))).is_nondegenerate()


def test_a2_modulo_three_is_degenerate() -> None:
    r"""$\det A_2 = 3 \equiv 0$ in $\mathbb F_3$, so $A_2 \otimes \mathbb F_3$ is degenerate."""
    reduction = a2().base_change(ZZ.Mor(GF(3))(lambda n: GF(3)(n)))

    assert not reduction.is_nondegenerate()


def test_a2_represents_two_and_not_four() -> None:
    r"""The norms of $A_2$ are $2(a^2 + ab + b^2)$; $2 = b(e_0, e_0)$ and $4$ is not of this form
    since $a^2 + ab + b^2 = 2$ has no integer solution."""
    form = a2()

    assert form.represents(2)
    assert not form.represents(4)


def test_the_bilinear_form_of_a2_as_a_quadratic_form() -> None:
    r"""$b$ is even, so $q(v) = b(v, v)/2$ is integral: $q(e_0) = 1$, $q(e_0 + e_1) = 3$."""
    quadratic = a2().to_quadratic_module()
    e0, e1 = quadratic.module_generator(0), quadratic.module_generator(1)

    assert quadratic.q(e0) == 1
    assert quadratic.q(e0 + e1) == 3
