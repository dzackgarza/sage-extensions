r"""The exact real field states its map from the integers, and a numeral meets an exact real in one parent.

Every unital ring receives the unique unital ring morphism $\mathbf{Z} \to R$, $n \mapsto
n\cdot 1$ (Stacks, Tag 00RM), and it is the map by which the coercion model meets an
element and a numeral in one parent.  An owned parent that is a set only in the owned
category graph is not a set for that model -- membership in Sage's ``Sets()`` is a test on
the class of the category's parent class -- so no coercion map over one could be built at
all, and the exact real field answered ``ValueError`` for the map every ring has.

The specimen is the smallest form of the question: the map, its two endpoints, its values
on a positive and a negative integer, and the arithmetic it makes possible in one parent.
"""

from sage_extensions.all import *


def test_the_exact_real_field_states_its_map_from_the_integers() -> None:
    r"""$\mathbf{Z} \to \mathbf{R}$, $n \mapsto n$, is a map of the rings it is between, sending $2$ to $2$ and $-3$ to $-3$."""
    coercion = RR.coerce_map_from(ZZ)

    assert coercion.domain() is ZZ
    assert coercion.codomain() is RR
    assert coercion(ZZ(2)) == RR(2)
    assert coercion(ZZ(-3)) == -RR(3)


def test_the_rational_field_states_the_same_map() -> None:
    r"""$\mathbf{Z} \to \mathbf{Q}$ is the same map, and its values are the rationals the integers are."""
    coercion = QQ.coerce_map_from(ZZ)

    assert coercion.domain() is ZZ
    assert coercion(ZZ(2)) == QQ(2)
    assert coercion(ZZ(-3)) == -QQ(3)


def test_the_map_is_what_makes_a_numeral_and_an_exact_real_meet_in_one_parent() -> None:
    r"""$\frac{1}{2} + 1 = \frac{3}{2}$ in the exact reals, read through the map and through the ring's own arithmetic."""
    half = RR(1) / RR(2)

    assert RR.coerce_map_from(ZZ)(ZZ(1)) + half == RR(3) / RR(2)
    assert RR(QQ(1) / QQ(2)) == half
