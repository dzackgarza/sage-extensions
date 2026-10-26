r"""$L^p$ consists of classes of functions modulo equality almost everywhere."""

from sage_extensions.all import *  # noqa: F401,F403


def test_changing_a_function_at_one_point_does_not_change_its_class() -> None:
    r"""$\operatorname{sgn}(x)^2$ differs from $1$ only at $0$, a null set, so both have one class in $L^\infty$."""
    maps = Lp(oo, RR, RR)
    s(t) = sgn(t)^2
    g(u) = exp(-u^2)
    punctured_one = maps(s)
    one = maps.one()
    quotient = maps.quotient_by_null_functions()
    projection = quotient.quotient_projection()

    assert punctured_one(RR.zero()) != one(RR.zero())
    assert projection(punctured_one) == projection(one)
    assert projection(punctured_one - one) == quotient.zero()
    assert projection(2 * punctured_one + one) == 3 * projection(one)
    assert quotient(maps(g)) != quotient.zero()
