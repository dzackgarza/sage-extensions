r"""Algebras given by a multiplication on a module, and maps between them."""

from sage_extensions.all import *  # noqa: F401,F403


def test_x_to_zero_is_an_algebra_map_from_split_idempotents_to_dual_numbers() -> None:
    r"""``QQ[x]/(x^2 - x) -> QQ[x]/(x^2)``, ``x ↦ 0``, respects the relation
    (``0^2 - 0 = 0``), so it is an algebra map; the linear map ``1 ↦ 1``,
    ``x ↦ x`` is not, since ``x^2 = x`` in the source but ``x^2 = 0 ≠ x`` in
    the target."""
    polynomials = QQ["x"]
    t = polynomials.gen()
    split = Algebras(QQ)(polynomials.quotient(polynomials.ideal([t**2 - t])))
    dual = Algebras(QQ)(polynomials.quotient(polynomials.ideal([t**2])))
    x_split, x_dual = split(t), dual(t)
    projection = split.Mor(dual)({x_split: dual.zero()})

    assert projection(x_split) == dual.zero()
    assert projection(split.one() + 3 * x_split) == dual.one()
    assert projection(x_split * x_split) == projection(x_split) * projection(x_split)
    assert x_split * x_split == x_split
    assert x_dual * x_dual == dual.zero()
    assert x_dual != dual.zero()


def test_multiplication_a2_b_ba_a_is_not_associative() -> None:
    r"""On ``QQ<a, b>`` with ``a a = b``, ``b a = a``, ``a b = b b = 0``:
    ``(a a) a = b a = a`` while ``a (a a) = a b = 0``."""
    module = Modules(QQ).free_module(("a", "b"))
    a, b = module.module_generator("a"), module.module_generator("b")
    algebra = Algebras(QQ)(
        module,
        {("a", "a"): b, ("b", "a"): a, ("a", "b"): module.zero(), ("b", "b"): module.zero()},
    )
    a, b = algebra(a), algebra(b)

    assert b * a == a
    assert a * b == algebra.zero()
    assert (a * a) * a == a
    assert a * (a * a) == algebra.zero()


def test_a_skew_but_not_alternating_bracket_in_characteristic_two_is_not_lie() -> None:
    r"""Over ``GF(2)`` the product ``x x = x`` on the line is skew
    (``[x, x] + [x, x] = 2x = 0``) but not alternating (``[x, x] ≠ 0``), so it
    is not a Lie algebra: Lie algebras require ``[v, v] = 0``."""
    module = Modules(GF(2)).free_module(("x",))
    x = module.module_generator("x")
    algebra = Algebras(GF(2))(module, {("x", "x"): x})

    assert algebra(x) * algebra(x) + algebra(x) * algebra(x) == algebra.zero()
    assert algebra(x) * algebra(x) != algebra.zero()
    assert algebra not in LieAlgebras(GF(2))
