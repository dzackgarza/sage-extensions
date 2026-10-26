r"""Annihilators and localization on the coordinate axes $\mathbb Q[x,y]/(xy)$.

$m/1 = 0$ in $S^{-1}M$ exactly when some $s \in S$ kills $m$, that is when
$\operatorname{Ann}(m)$ meets $S$ (Atiyah–Macdonald, *Introduction to
Commutative Algebra*, ch. 3).  With $y$ inverted, $x$ becomes zero because $y$
annihilates it, while $1$ does not, because no power of $y$ lies in $(xy)$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def coordinate_axes():
    R = QQ["x,y"]
    x, y = R.algebra_generator("x"), R.algebra_generator("y")
    M = Modules(R)(R.quotient_ring(R.ideal(x * y)))
    return R, x, y, M


def test_on_the_coordinate_axes_ann_x_is_y_and_ann_1_is_xy() -> None:
    """Source: by hand; x*f in (xy) iff y | f since QQ[x,y] is a UFD."""
    R, x, y, M = coordinate_axes()
    g = M.module_generator(0)
    assert M.annihilator_of(x * g) == R.ideal(y)
    assert M.annihilator_of(g) == R.ideal(x * y)
    assert M.annihilator() == R.ideal(x * y)


def test_inverting_y_on_the_coordinate_axes_kills_x() -> None:
    """y * x = 0 in the quotient, so x/1 = 0 after inverting y. Source: Atiyah–Macdonald ch. 3."""
    R, x, y, M = coordinate_axes()
    L = M.localize(y)
    assert L(x * M.module_generator(0)) == L.zero()


def test_inverting_y_on_the_coordinate_axes_keeps_1() -> None:
    """No power y^n lies in (xy), so 1/1 != 0 after inverting y. Source: Atiyah–Macdonald ch. 3."""
    R, x, y, M = coordinate_axes()
    L = M.localize(y)
    assert L(M.module_generator(0)) != L.zero()
    assert not L.is_zero()
