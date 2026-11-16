r"""The arrow type of a fixed Mor is the one its declared graph states.

The arrow type is generated once per family and key, from the first Mor that
asks for it, so what the key holds decides every later Mor's arrows.  The key
has to hold the Mor classes the endpoints select for the family's declared
supercategories: a Mor's arrows are the arrows of its own graph, and two Mors
of one family whose endpoints select different classes are different theories.

Sage orders the parent classes of unrelated categories by the order the session
built them, so each row runs its script in a fresh process; both rows run the
same script, which builds its Mors in one order and then in the other.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_arrow_type_of_a_mor_is_the_same_when_the_de_rham_algebra_is_built_first() -> None:
    r"""A de Rham Mor then a divided-power Mor: each keeps its own arrow type.

    ``DifferentialGradedAlgebras(ZZ)`` is one family, and its declared graph
    holds the algebra Mor of each endpoint's category.  The de Rham algebra
    ``Lambda(Q[1], x_0)`` is a framed algebra, so its algebra Mor class is
    ``AlgebraMor``, the class that carries the generator-image construction;
    the divided-power algebra ``Gamma(Z[x])`` is not framed, so its class is
    ``UnitalMultiplicativeAlgebraMor``.  Two different classes of arrows are
    two different arrow types, whichever Mor was asked for first.

    The same session also builds the module Mor and the slice Mor of
    ``Gamma(Z[x])``, whose arrow theories are likewise distinct.
    """
    run = arrow_type_order_run(de_rham_first=True)

    assert run.returncode == 0, run.stderr


def test_the_arrow_type_of_a_mor_is_the_same_when_the_divided_power_algebra_is_built_first() -> None:
    r"""The divided-power Mor then the de Rham Mor: the same two arrow types.

    The same assertions as in the other order.  A key that omits the selected
    class gives both differential graded algebra Mors the type of whichever
    was built first, so the row fails in either order until the key holds the
    selection.
    """
    run = arrow_type_order_run(de_rham_first=False)

    assert run.returncode == 0, run.stderr
