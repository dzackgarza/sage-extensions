r"""A scheme morphism presented by local maps is an arrow, so it hashes.

A map out of a glued scheme is a family of local maps on its charts that agree
through the chart changes (Stacks Project, Tag 01JA).  Two such maps are equal
when they are the same map of the underlying spaces, so equal arrows share one
source and one target, and the endpoints are what a hash reads -- the rule of
:class:`Sets`, and the fallback the library's own ``arrow_hash`` states for an
arrow with no finite probe.  The fold of two lines glued along ``D(x)`` is the
specimen: it retains its chart maps and refuses no hash.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _glued_pair():
    r"""Two copies of ``A^1_Q`` glued along ``D(x)`` by the identity of ``D(x)``."""
    ring = QQ.polynomial_ring("x")
    line = ring.affine_spectrum()
    punctured = line.distinguished_open(ring.algebra_generator("x"))
    identity = punctured.Mor(punctured).identity()
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)
    return line, Schemes(QQ).glue_affine_atlas((line, line), (gluing,))


def test_the_fold_of_a_glued_pair_of_lines_is_a_point_of_a_finite_ordered_set() -> None:
    r"""The fold onto the line is one morphism, and its two builds hash alike.

    The identity on each chart glues to the fold ``X -> A^1_Q`` of the doubled
    line (the two charts agree on the overlap by construction), and it restricts
    to the identity on each chart.  A finite ordered set of the fold is built.
    """
    line, doubled = _glued_pair()
    identity = line.Mor(line).identity()
    atlas = doubled.gluing_datum()
    fold = doubled.Mor(line)((identity, identity))
    rebuilt = doubled.Mor(line)((identity, identity))

    assert fold * atlas.chart_embedding(1) == identity
    assert hash(fold) == hash(rebuilt)
    assert FiniteOrderedSets()((fold,)).cardinality() == 1
    assert FiniteOrderedSets()((fold, rebuilt)).cardinality() == 1
