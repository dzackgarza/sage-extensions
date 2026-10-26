r"""The exterior and divided power algebras are functors on modules."""

from sage_extensions.all import *  # noqa: F401,F403


def test_exterior_square_of_a_plane_endomorphism_is_multiplication_by_its_determinant() -> None:
    r"""For ``f : ZZ^2 -> ZZ^2`` with ``f(e1) = e1 + 3 e2``, ``f(e2) = 2 e1 + 4 e2``,
    ``Λ^2 f (e1 e2) = f(e1) f(e2) = (4 - 6) e1 e2 = det(f) e1 e2``."""
    module = Modules(ZZ).free_module(("e1", "e2"))
    e1, e2 = module.module_generator("e1"), module.module_generator("e2")
    f = module.Mor(module)({e1: e1 + 3 * e2, e2: 2 * e1 + 4 * e2})
    exterior_functor = Modules(ZZ).exterior_algebra()
    exterior = exterior_functor(module)
    top = exterior.algebra_generator("e1") * exterior.algebra_generator("e2")

    assert exterior_functor(f)(top) == -2 * top
    assert exterior_functor(f)(exterior.algebra_generator("e1")) == exterior.algebra_generator("e1") + 3 * exterior.algebra_generator("e2")


def test_divided_power_functor_sends_gamma_n_of_x_to_2_to_the_n_gamma_n_of_y() -> None:
    r"""For ``f : ZZ x -> ZZ y``, ``x ↦ 2y``: ``Γ(f)(γ_n(x)) = γ_n(2y) = 2^n γ_n(y)``,
    so ``γ_2(x) ↦ 4 γ_2(y)`` and ``γ_3(x) ↦ 8 γ_3(y)``."""
    source = Modules(ZZ).free_module(("x",))
    target = Modules(ZZ).free_module(("y",))
    f = source.Mor(target)({source.module_generator("x"): 2 * target.module_generator("y")})
    divided_functor = Modules(ZZ).divided_power_algebra()
    source_gamma, target_gamma = divided_functor(source), divided_functor(target)
    x = source_gamma.degree_one_generator("x")
    y = target_gamma.degree_one_generator("y")

    assert divided_functor(f)(source_gamma.divided_power(x, 2)) == 4 * target_gamma.divided_power(y, 2)
    assert divided_functor(f)(source_gamma.divided_power(x, 3)) == 8 * target_gamma.divided_power(y, 3)
