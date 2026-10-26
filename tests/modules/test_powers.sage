r"""Tensor, symmetric, exterior and divided powers of abelian groups.

For $M$ free of rank $n$: $T^d M$ has rank $n^d$, $\operatorname{Sym}^d M$ and
$\Gamma^d M$ rank $\binom{n+d-1}{d}$, $\Lambda^d M$ rank $\binom nd$ (Bourbaki,
*Algebra* III, §6, §7 and IV, §5).  For $M = \mathbb Z/2$ with generator $x$,
$\Gamma^n M = \mathbb Z\gamma_n(x) / \big(2^k\binom nk \gamma_n(x)\big)_{1 \le k \le n}$,
so $\Gamma^2 = \mathbb Z/4$, $\Gamma^3 = \mathbb Z/2$, $\Gamma^4 = \mathbb Z/8$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_ranks_of_the_powers_of_z2() -> None:
    """T^2 = 4, Sym^2 = 3, Lambda^2 = 1, Lambda^3 = 0, Gamma^3 = 4. Source: Bourbaki, Algebra III §6-7."""
    M = ZZ**2
    assert M.tensor_power(2).module_rank() == 4
    assert M.tensor_power(3).module_rank() == 8
    assert M.symmetric_power(2).module_rank() == 3
    assert M.exterior_power(2).module_rank() == 1
    assert M.exterior_power(3).module_rank() == 0
    assert M.divided_power_module(3).module_rank() == 4


def test_power_modules_retain_the_source_and_degree_that_define_them() -> None:
    M = ZZ**2

    tensor_square = M.tensor_power(2)
    symmetric_cube = M.symmetric_power(3)
    divided_square = M.divided_square()

    assert tensor_square.power_source() is M
    assert tensor_square.power_degree() == 2
    assert symmetric_cube.power_source() is M
    assert symmetric_cube.power_degree() == 3
    assert divided_square.power_source() is M
    assert divided_square.power_degree() == 2


def test_divided_powers_of_z_mod_2_differ_from_its_symmetric_powers() -> None:
    r"""$T^3 = \operatorname{Sym}^3 = \mathbb Z/2$ while $\Gamma^2 = \mathbb Z/4$, $\Gamma^3 = \mathbb Z/2$,
    $\Gamma^4 = \mathbb Z/8$ (orders $\gcd_k 2^k\binom nk$ = 4, 2, 8).

    Source: Roby, Lois polynômes et lois formelles en théorie des modules, III; Whitehead's
    $\Gamma(\mathbb Z/2) = \mathbb Z/4$ (Whitehead, A certain exact sequence, 1950); by hand.
    """
    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(2)))
    assert tuple(M.tensor_power(3).invariant_factors()) == (2,)
    assert tuple(M.symmetric_power(3).invariant_factors()) == (2,)
    assert tuple(M.divided_power_module(2).invariant_factors()) == (4,)
    assert tuple(M.divided_power_module(3).invariant_factors()) == (2,)
    assert tuple(M.divided_power_module(4).invariant_factors()) == (8,)


def test_polarization_after_inclusion_is_d_factorial_and_inclusion_after_polarization_symmetrizes() -> None:
    r"""$\Gamma^d M = (T^d M)^{S_d} \hookrightarrow T^d M$ and $T^d M \to \Gamma^d M$ compose to $d!$ on
    $\Gamma^d M$ and to $\sum_{\sigma \in S_d} \sigma$ on $T^d M$.

    Source: Bourbaki, Algebra IV §5 ex. (divided powers as symmetric tensors).
    """
    M = ZZ**2
    for d in (2, 3):
        divided = M.divided_power_module(d)
        tensor = M.tensor_power(d)
        inclusion = M.divided_power_invariant_inclusion(d)
        polarization = M.tensor_power_polarization(d)
        S = Groups.S(d)
        assert polarization * inclusion == S.cardinality() * divided.End().one()
        symmetrization = sum((M.tensor_power_permutation(d, sigma) for sigma in S), tensor.End().zero())
        assert inclusion * polarization == symmetrization


def test_symmetric_and_divided_squares_and_cubes_are_functors() -> None:
    r"""$\operatorname{Sym}^d$ and $\Gamma^d$ preserve composition of the shear $x \mapsto x + y$ and the
    scaling $\operatorname{diag}(2, 3)$; the shear induces isomorphisms and the scaling does not.

    Source: functoriality of Sym^d and Gamma^d (Bourbaki, Algebra III §6, IV §5).
    """
    M = ZZ**2
    x, y = M.module_generator(0), M.module_generator(1)
    shear = M.End()({0: x + y, 1: y})
    scale = M.End()({0: 2 * x, 1: 3 * y})
    for power in (
        lambda f: f.symmetric_power(2),
        lambda f: f.symmetric_power(3),
        lambda f: f.divided_power(2),
        lambda f: f.divided_power(3),
    ):
        assert power(scale * shear) == power(scale) * power(shear)
        assert power(M.End().one()) == power(M.End().one()).domain().End().one()
        assert power(shear).is_isomorphism()
        assert not power(scale).is_surjective()
