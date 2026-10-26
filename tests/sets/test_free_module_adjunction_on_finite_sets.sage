r"""The free $\mathbb{Z}$-module on a set is left adjoint to the underlying set.

Write $F : \mathbf{Set} \to \mathbf{Mod}_{\mathbb{Z}}$ and $U$ for its right
adjoint.  The unit $\eta_S : S \to UF(S)$ sends a point to its basis vector,
so distinct points go to distinct vectors.  The counit
$\varepsilon_M : FU(M) \to M$ evaluates a formal combination.  The hom-set
bijection sends $g : S \to U(B)$ to $\hat g = \varepsilon_B \circ F(g)$,
which agrees with $g$ on basis vectors, and back to
$U(\hat g) \circ \eta_S = g$.  The triangle identities are
$\varepsilon_{F S} \circ F(\eta_S) = \mathrm{id}_{F S}$ and
$U(\varepsilon_B) \circ \eta_{U B} = \mathrm{id}_{U B}$.  Functoriality:
$F$ of the map $\{0, 1\} \to \{0\}$ sends $3 e_0 - e_1$ to $2 e$.  These
are the definitions of the free module and of an adjunction.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_unit_sends_the_two_points_to_the_two_basis_vectors() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    two = Sets.Δ[1]
    unit = adjunction.unit(two)

    assert unit.codomain() is adjunction.left_adjoint()(two)
    assert unit(two(0)) != unit(two(1))
    assert unit(two(0)) + unit(two(1)) != 2 * unit(two(0))


def test_the_transpose_of_a_map_to_a_rank_one_module_agrees_on_basis_vectors() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    two = Sets.Δ[1]
    point = Sets.Δ[0]
    line = adjunction.left_adjoint()(point)
    basis_vector = adjunction.unit(point)(point(0))
    values = Sets().Mor(two, adjunction.right_adjoint()(line))(
        lambda index: 2 * basis_vector if index == 0 else -basis_vector
    )
    transpose = adjunction.mor_set_isomorphism_inverse(values, line)
    unit = adjunction.unit(two)

    assert transpose(unit(two(0))) == 2 * basis_vector
    assert transpose(unit(two(1))) == -basis_vector
    assert transpose(3 * unit(two(0)) - unit(two(1))) == 7 * basis_vector


def test_transposing_twice_returns_the_original_map_of_sets() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    two = Sets.Δ[1]
    point = Sets.Δ[0]
    line = adjunction.left_adjoint()(point)
    basis_vector = adjunction.unit(point)(point(0))
    values = Sets().Mor(two, adjunction.right_adjoint()(line))(
        lambda index: 2 * basis_vector if index == 0 else -basis_vector
    )
    transpose = adjunction.mor_set_isomorphism_inverse(values, line)
    back = adjunction.mor_set_isomorphism_forward(transpose, two)

    assert back(two(0)) == values(two(0))
    assert back(two(1)) == values(two(1))


def test_the_first_triangle_identity_on_the_free_module_on_two_points() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    two = Sets.Δ[1]
    free = adjunction.left_adjoint()
    unit = adjunction.unit(two)
    composite = adjunction.counit(free(two)) * free(unit)
    vector = 3 * unit(two(0)) - unit(two(1))

    assert composite(vector) == vector


def test_the_second_triangle_identity_on_the_free_module_of_rank_one() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    point = Sets.Δ[0]
    underlying = adjunction.right_adjoint()
    line = adjunction.left_adjoint()(point)
    basis_vector = adjunction.unit(point)(point(0))
    composite = underlying(adjunction.counit(line)) * adjunction.unit(underlying(line))

    assert composite(2 * basis_vector) == 2 * basis_vector
    assert composite(-basis_vector) == -basis_vector


def test_the_free_module_functor_sums_coefficients_along_the_map_to_a_point() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    two = Sets.Δ[1]
    point = Sets.Δ[0]
    free = adjunction.left_adjoint()
    collapse = Sets().Mor(two, point)(lambda _index: point(0))
    unit = adjunction.unit(two)

    assert free(collapse)(3 * unit(two(0)) - unit(two(1))) == 2 * adjunction.unit(point)(point(0))
    assert adjunction.unit_transformation().domain().functor()(two) is two
