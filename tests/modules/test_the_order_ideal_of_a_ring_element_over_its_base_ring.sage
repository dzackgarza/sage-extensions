r"""The order ideal of a ring element is an ideal of the ring's base ring.

A ring is a left module over its base ring, so an element of $\mathbf{Z}[x]$
carries two readings that both go by the name ``order_ideal``: the ring's
element class inherits ``Modules.ElementMethods.order_ideal`` from the module
structure $U(\mathbf{Z}[x])$ and ``FramedFreeModules.ElementMethods.order_ideal``
from the chosen basis of the monomials.  The order ideal itself is not a matter
of which level answers: it is
$O_M(v) = \{\varphi(v) : \varphi \in \operatorname{Hom}_R(M,R)\}$, an ideal of
the scalar ring $R$.  Reading $\mathbf{Z}[x]$ as a $\mathbf{Z}$-module, that is
an ideal of $\mathbf{Z}$ and not of $\mathbf{Z}[x]$ -- the linear functionals
take values in $\mathbf{Z}$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_order_ideal_of_an_integer_polynomial_is_the_ideal_of_its_coefficients() -> None:
    r"""$O_{\mathbf{Z}[x]}(2x+2) = (2)$: the values of the functionals at $2x+2$.

    $\mathbf{Z}[x]$ is free on the monomials over $\mathbf{Z}$, so a linear
    functional $\varphi$ is its family of values on them, and
    $\varphi(2x+2) = 2\varphi(1) + 2\varphi(x)$: every value is divisible by
    $2$.  The functional that is $1$ on $1$ and $0$ on every other monomial
    attains $2$, so the values generate exactly $(2)$.
    """
    line = ZZ["x"]
    x = line.algebra_generator("x")

    assert (2 * x + 2).order_ideal() == ZZ.ideal(2)


def test_the_order_ideal_of_a_rational_polynomial_is_the_unit_ideal() -> None:
    r"""$O_{\mathbf{Q}[x]}(x+1) = \mathbf{Q}$: the coefficients generate the field.

    Over $\mathbf{Q}$ the same functional that is $1$ on $1$ attains the
    coefficient $1$ of $x+1$, so the values generate the unit ideal of
    $\mathbf{Q}$ -- which is $\mathbf{Q}$ itself.
    """
    line = QQ["x"]
    x = line.algebra_generator("x")

    assert (x + 1).order_ideal() == QQ.ideal(1)
