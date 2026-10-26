r"""A span is an object, and it owns its pushout.

A span :math:`A\leftarrow C\to B` is an apex with one arrow to each of two
objects, so it is a cone over the discrete diagram on those two and needs no
shape vocabulary beyond the one the diagram layer already has.  Being an
object, it has an apex, two legs, a diagram, and a colimit it asks its
category for.
"""

from sage_extensions.all import *


def _two_element_span():
    r"""``2 <- 1 -> 3`` in sets, both legs picking the first element."""
    apex = Sets.Δ[0]
    left_foot = Sets.Δ[1]
    right_foot = Sets.Δ[2]
    left_leg = Sets().Mor(apex, left_foot)(lambda _value: left_foot(0))
    right_leg = Sets().Mor(apex, right_foot)(lambda _value: right_foot(0))
    return Sets().span(left_leg, right_leg), apex, left_leg, right_leg






def test_a_span_owns_its_pushout() -> None:
    r"""Two feet of two and three points glued along one point make four."""
    span, _apex, _left_leg, _right_leg = _two_element_span()

    glued = span.pushout()

    assert glued.cardinality() == cardinal(4)


