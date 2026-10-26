r"""The canonical maps between the tensor, symmetric, exterior and divided power algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_comparison_maps_out_of_the_tensor_algebra_and_into_divided_powers() -> None:
    r"""For ``M = ZZ^2`` with basis ``x, y``: ``T(M) -> Sym(M)`` kills ``xy - yx``;
    ``T(M) -> Λ(M)`` kills ``x ⊗ x`` and ``xy + yx``; ``Sym(M) -> Γ(M)`` sends
    ``x^n`` to ``n! γ_n(x)``, so ``x^3 ↦ 6 γ_3(x)``; and ``x^2 = 2 γ_2(x)`` in
    ``Γ(M)`` while ``γ_2(x)`` is not divisible by 2 there (Roby's divided power
    relations ``γ_i γ_j = binom(i+j, i) γ_{i+j}``)."""
    module = Modules(ZZ).free_module(("x", "y"))
    tensor = module.tensor_algebra()
    symmetric = module.symmetric_algebra()
    exterior = module.exterior_algebra()
    divided = module.divided_power_algebra()
    x_t, y_t = tensor.algebra_generator("x"), tensor.algebra_generator("y")
    x_s, y_s = symmetric.algebra_generator("x"), symmetric.algebra_generator("y")

    to_symmetric = module.tensor_to_symmetric()
    assert to_symmetric(x_t * y_t) == x_s * y_s
    assert to_symmetric(x_t * y_t - y_t * x_t) == symmetric.zero()
    assert x_t * y_t != y_t * x_t

    to_exterior = module.tensor_to_alternating()
    assert to_exterior(x_t * x_t) == exterior.zero()
    assert to_exterior(x_t * y_t + y_t * x_t) == exterior.zero()
    assert to_exterior(x_t * y_t) != exterior.zero()

    x_d = divided.degree_one_generator("x")
    gamma_2 = divided.divided_power(x_d, 2)
    gamma_3 = divided.divided_power(x_d, 3)
    to_divided = module.symmetric_to_divided()
    assert to_divided(x_s**3) == 6 * gamma_3
    assert to_divided(x_s**2 * y_s) == 2 * gamma_2 * divided.degree_one_generator("y")
    assert x_d**2 == 2 * gamma_2
    assert gamma_2 * x_d == 3 * gamma_3
    assert gamma_2 != x_d**2


def test_symmetric_and_divided_power_algebras_agree_over_the_rationals() -> None:
    r"""Over ``QQ`` the map ``Sym(M) -> Γ(M)``, ``x^n ↦ n! γ_n(x)``, is an
    isomorphism, with inverse ``γ_n(x) ↦ x^n / n!``."""
    module = Modules(QQ).free_module(("x", "y"))
    symmetric = module.symmetric_algebra()
    divided = module.divided_power_algebra()
    forward = module.symmetric_to_divided()
    backward = module.divided_to_symmetric()
    x, y = symmetric.algebra_generator("x"), symmetric.algebra_generator("y")
    gamma_2_x = divided.divided_power(divided.degree_one_generator("x"), 2)

    assert backward(gamma_2_x) == x**2 / 2
    assert backward(forward(x**2 * y + 3 * y)) == x**2 * y + 3 * y
    assert forward(backward(gamma_2_x * divided.degree_one_generator("y"))) == gamma_2_x * divided.degree_one_generator("y")
