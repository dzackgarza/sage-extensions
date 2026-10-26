r"""Cartan calculus of polynomial vector fields on the affine plane over ``QQ``."""

from sage_extensions.all import *  # noqa: F401,F403


def _plane():
    algebra = QQ["x,y"]
    x, y = algebra.algebra_generator("x"), algebra.algebra_generator("y")
    vector_fields = algebra.vector_fields()
    d_dx = vector_fields({x: algebra.one(), y: algebra.zero()})
    x_d_dy = vector_fields({x: algebra.zero(), y: x})
    return algebra, x, y, d_dx, x_d_dy


def test_bracket_of_d_dx_and_x_d_dy_is_d_dy() -> None:
    r"""``[d/dx, x d/dy] = d/dy``: on ``f``, ``d/dx(x f_y) - x d/dy(f_x) = f_y``."""
    algebra, x, y, d_dx, x_d_dy = _plane()
    bracket = d_dx.lie_bracket(x_d_dy)

    assert bracket(x) == algebra.zero()
    assert bracket(y) == algebra.one()
    assert bracket(x * y**2) == 2 * x * y


def test_contraction_and_lie_derivative_along_d_dx() -> None:
    r"""For ``X = d/dx``: ``i_X`` lowers degree by one with ``i_X dx = 1``,
    ``i_X dy = 0``, ``i_X(dx dy) = dy``; and ``L_X x = 1``, ``L_X y = 0``,
    ``L_X dx = 0``.  Derivation: ``i_X`` is the graded derivation of degree -1
    with ``i_X(df) = X f``, and ``L_X = d i_X + i_X d``."""
    algebra, x, y, d_dx, _ = _plane()
    de_rham = algebra.de_rham_algebra()
    d = de_rham.differential()
    X, Y = de_rham(x), de_rham(y)
    dx, dy = d(X), d(Y)
    contraction = d_dx.interior_product()
    lie = d_dx.lie_derivative()

    assert contraction.degree_shift() == -1
    assert lie.degree_shift() == 0
    assert contraction(X) == de_rham.zero()
    assert contraction(dx) == de_rham.one()
    assert contraction(dy) == de_rham.zero()
    assert contraction(dx * dy) == dy
    assert lie(X) == de_rham.one()
    assert lie(Y) == de_rham.zero()
    assert lie(dx) == de_rham.zero()


def test_cartan_identities_hold_on_a_mixed_degree_form() -> None:
    r"""``[d, i_X] = L_X``, ``[d, L_X] = 0``, ``[L_X, i_Y] = i_[X,Y]`` and
    ``[L_X, L_Y] = L_[X,Y]`` (graded commutators) for ``X = d/dx``,
    ``Y = x d/dy``.  Derivation: both sides of each identity are graded
    derivations of the same degree that agree on ``x``, ``y``, ``dx`` and ``dy``."""
    algebra, x, y, d_dx, x_d_dy = _plane()
    bracket = d_dx.lie_bracket(x_d_dy)
    de_rham = algebra.de_rham_algebra()
    d = de_rham.differential()
    X, Y = de_rham(x), de_rham(y)
    form = X * d(Y) + d(X) * d(Y)

    i_x, i_y = d_dx.interior_product(), x_d_dy.interior_product()
    l_x, l_y = d_dx.lie_derivative(), x_d_dy.lie_derivative()

    assert d.graded_commutator(i_x)(form) == l_x(form)
    assert d.graded_commutator(l_x)(form) == de_rham.zero()
    assert l_x.graded_commutator(i_y)(form) == bracket.interior_product()(form)
    assert l_x.graded_commutator(l_y)(form) == bracket.lie_derivative()(form)
    assert l_x(form) != de_rham.zero()
