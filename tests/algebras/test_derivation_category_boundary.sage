r"""Derivations of the coordinate axes ``QQ[x, y]/(xy)``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_weight_derivation_of_the_axes_satisfies_leibniz_and_factors_through_omega() -> None:
    r"""``D(x) = x``, ``D(y) = -y`` is a derivation of ``A = QQ[x,y]/(xy)``
    (it respects the relation: ``D(xy) = xy - xy = 0``); it satisfies
    ``D(fg) = f D(g) + g D(f)``, ``D(x^2 y^3) = -x^2 y^3 = 0`` in ``A``, and
    factors through the universal derivation ``d : A -> Ω_A``."""
    plane = QQ["x,y"]
    axes = plane.quotient(plane.ideal([plane.gen(0) * plane.gen(1)]))
    x, y = axes(plane.gen(0)), axes(plane.gen(1))
    derivation = axes.derivations()({x: x, y: -y})

    assert derivation(x * y) == axes.zero()
    assert derivation(x**3) == 3 * x**3
    assert derivation(x**2 + y**2) == 2 * x**2 - 2 * y**2
    assert derivation((x + 1) * (y + 1)) == (x + 1) * derivation(y) + (y + 1) * derivation(x)
    assert (derivation + derivation)(x) == 2 * x

    omega = axes.kahler_differentials()
    classifier = omega.from_derivation(derivation)
    assert classifier(omega.universal_derivation()(x + y)) == x - y
