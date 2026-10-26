r"""The integral cohomology of a cyclic group, from its periodic resolution.

For $G = C_n = \langle t \rangle$ the trivial module $\mathbb Z$ has the periodic free
$\mathbb Z[G]$-resolution $\cdots \to \mathbb Z[G] \xrightarrow{N} \mathbb Z[G]
\xrightarrow{t - 1} \mathbb Z[G] \to \mathbb Z$, with $N = \sum_{g} g$.  Applying
$\operatorname{Hom}_{\mathbb Z[G]}(-, \mathbb Z)$ gives $\mathbb Z \xrightarrow{0} \mathbb Z
\xrightarrow{n} \mathbb Z \xrightarrow{0} \mathbb Z \to \cdots$, so $H^0(C_n, \mathbb Z) = \mathbb Z$,
$H^1(C_n, \mathbb Z) = 0$ and $H^2(C_n, \mathbb Z) = \mathbb Z/n$.  Values by hand from
the definitions.  Here $n = 3$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def periodic_cochains(order):
    r"""$\mathbb Z \xrightarrow{0} \mathbb Z \xrightarrow{n} \mathbb Z \xrightarrow{0} \mathbb Z$ in degrees $0$ to $3$."""
    c0, c1, c2, c3 = ZZ ^ 1, ZZ ^ 1, ZZ ^ 1, ZZ ^ 1
    d0 = c0.Mor(c1)({0: 0 * c1.module_generator(0)})
    d1 = c1.Mor(c2)({0: order * c2.module_generator(0)})
    d2 = c2.Mor(c3)({0: 0 * c3.module_generator(0)})
    return CochainComplexes(ZZ)({0: c0, 1: c1, 2: c2, 3: c3}, {0: d0, 1: d1, 2: d2})


def test_h0_of_c3_with_integer_coefficients_is_z() -> None:
    r"""$H^0(C_3, \mathbb Z) = \mathbb Z^{C_3} = \mathbb Z$."""
    assert periodic_cochains(3).cohomology(0).module_rank() == 1


def test_h1_of_c3_with_integer_coefficients_vanishes() -> None:
    r"""$H^1(C_3, \mathbb Z) = \operatorname{Hom}(C_3, \mathbb Z) = 0$."""
    assert periodic_cochains(3).cohomology(1).is_zero()


def test_h2_of_c3_with_integer_coefficients_is_z3() -> None:
    r"""$H^2(C_3, \mathbb Z) = \mathbb Z/3$."""
    assert tuple(periodic_cochains(3).cohomology(2).invariant_factors()) == (3,)
