r"""Finite Coxeter diagrams and their structure-preserving morphisms.

A Coxeter diagram remembers the complete symmetric Coxeter matrix, not only
the drawn graph.  In particular an absent edge means Coxeter entry ``2``.
Thus a vertex map from two isolated vertices to an edge is a graph morphism,
but not a Coxeter-diagram morphism.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _two_isolated_mirrors():
    return CoxeterDiagrams().from_coxeter_matrix(((1, 2), (2, 1)))


def _a2_diagram():
    return CoxeterDiagrams().from_coxeter_matrix(((1, 3), (3, 1)))


def test_coxeter_diagram_retains_the_complete_symmetric_angle_matrix() -> None:
    diagram = _a2_diagram()

    assert diagram in CoxeterDiagrams()
    assert diagram in LabelledGraphs()
    assert diagram.cardinality() == cardinal(2)
    assert diagram.coxeter_entry(diagram(0), diagram(0)) == 1
    assert diagram.coxeter_entry(diagram(0), diagram(1)) == 3
    assert diagram.coxeter_entry(diagram(1), diagram(0)) == 3
    assert diagram.has_edge(diagram(0), diagram(1))


def test_coxeter_endpoint_mor_preserves_every_coxeter_entry_by_default() -> None:
    source = _two_isolated_mirrors()
    target = _a2_diagram()
    structured = source.Mor(target)
    graph_mor = source.Mor(target, category=Graphs())
    vertex_map = lambda vertex: target(int(vertex))

    assert structured is CoxeterDiagrams().Mor(source, target)
    assert graph_mor is Graphs().Mor(source, target)
    assert graph_mor(vertex_map)(source(1)) == target(1)
    with pytest.raises(ValueError):
        structured(vertex_map)


def test_coxeter_morphisms_have_identity_and_composition() -> None:
    diagram = _a2_diagram()
    identity = diagram.Mor(diagram).identity()

    assert identity(diagram(0)) == diagram(0)
    assert identity * identity == identity
