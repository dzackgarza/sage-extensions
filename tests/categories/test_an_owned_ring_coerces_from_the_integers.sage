r"""An owned ring states its coercion from the integers as a map.

Every unital ring receives the unique unital ring morphism $\mathbf{Z} \to R$,
$n \mapsto n\cdot 1$ (Stacks, Tag 00RM, for the unital ring structure; the map is
the prime ring's universal one), and it is how the coercion model meets an element
and a numeral in one parent: an operator reads its numeral through the ring's own
construction instead of the ring's element class stating an operator per numeral.
So the coercion is a map the ring states, not only a constructor it happens to
have: ``QQ.coerce_map_from(ZZ)`` is that map, and it sends $2$ to $2$.

The distinction matters at the implementation boundary.  A map is built in the
Homset of its domain and codomain, and Sage builds that Hom by asking whether
each endpoint is in the category the map is stated over -- a set.  An owned
parent therefore has to be a set at that boundary for its coercion maps to exist
at all, which the owned category of sets states: Sage's ``Sets()`` is a runtime
root edge of it, and every owned set parent is a Sage set parent through it.
The specimen is the smallest such map, and the one the failure was found on: a
numeral reaching a chart's function ring refused, because no map over an owned
parent could be built.
"""

from sage_extensions.all import *


def test_the_rational_field_states_its_map_from_the_integers() -> None:
    r"""$\mathbf{Z} \to \mathbf{Q}$, $n \mapsto n$, is a map: it sends $2$ to $2$ and $-3$ to $-3$."""
    coercion = QQ.coerce_map_from(ZZ)

    assert coercion.domain() is ZZ
    assert coercion.codomain() is QQ
    assert coercion(ZZ(2)) == QQ(2)
    assert coercion(ZZ(-3)) == -QQ(3)


def test_a_numeral_meets_an_owned_ring_element_in_one_parent() -> None:
    r"""The map is what makes $2 \cdot (1/3)$ and $1/3 + 2/3$ arithmetic in one ring, not a TypeError."""
    assert ZZ(2) * QQ(1) == QQ(2)
    assert QQ(1) / QQ(3) + QQ(2) / QQ(3) == QQ(1)
    assert QQ.coerce_map_from(ZZ)(ZZ(1)) + QQ(1) / QQ(2) == QQ(3) / QQ(2)
