r"""Exterior and divided power algebras are functors on modules."""

from sage_extensions.all import *  # noqa: F401,F403


def test_exterior_and_divided_power_functors_send_xy_to_2ab_under_x_to_2a_y_to_b() -> None:
    r"""For ``f : ZZ^2 -> ZZ^2``, ``x ↦ 2a``, ``y ↦ b``: ``Λ(f)`` and ``Γ(f)`` are
    algebra maps, so ``xy ↦ f(x) f(y) = 2ab``; on ``Λ^2`` this is
    multiplication by ``det f = 2``."""
    source = Modules(ZZ).free_module(("x", "y"))
    target = Modules(ZZ).free_module(("a", "b"))
    f = source.Mor(target)({
        source.module_generator("x"): 2 * target.module_generator("a"),
        source.module_generator("y"): target.module_generator("b"),
    })

    for functor in (Modules(ZZ).exterior_algebra(), Modules(ZZ).divided_power_algebra()):
        source_algebra, target_algebra = functor(source), functor(target)
        x, y = source_algebra.degree_one_generator("x"), source_algebra.degree_one_generator("y")
        a, b = target_algebra.degree_one_generator("a"), target_algebra.degree_one_generator("b")
        induced = functor(f)

        assert induced(x) == 2 * a
        assert induced(y) == b
        assert induced(x * y) == 2 * a * b
        assert induced(x * y) != a * b
