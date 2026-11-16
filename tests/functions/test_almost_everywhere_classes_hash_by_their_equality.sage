r"""The a.e. classes of integrable maps hash by their quotient.

``L^1(RR)`` modulo equality almost everywhere is a quotient of a real vector
space: two integrable maps are equal there when they agree outside a null set,
and a representative may be changed on a null set without changing its class.
No datum of one representative is invariant under that, so the quotient is what
a hash reads, and a finite ordered set of the classes is a set, which is the
rule of :class:`Sets`.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_zero_class_is_a_point_of_a_finite_ordered_set() -> None:
    r"""The zero class of ``L^1(RR)`` is a point of a finite ordered set.

    The zero integrable map is null, so it represents the zero class.  Equality
    of two classes is the proposition that the representatives agree outside a
    null set, which this library keeps as a proposition rather than deciding: a
    set of two classes is refused because that decision is missing, and a set of
    the class itself is built, which needs its hash and not its equality.
    """
    classes = Lp(1, RR, RR).quotient_by_null_functions().underlying_set()
    zero = classes.zero()

    assert hash(zero) == hash(classes.zero())
    assert FiniteOrderedSets()((zero,)).cardinality() == 1
