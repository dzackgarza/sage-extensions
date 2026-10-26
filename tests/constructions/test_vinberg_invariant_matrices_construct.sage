r"""Vinberg invariant matrices as projectively labelled symmetric graphs.

For two mirrors ``r,s``, the invariant is the projective point
``[4 b(r,s)^2 : q(r)q(s)]``.  It therefore depends only on the reflection
geometry, not on independently rescaling either root, and its affine ratio is
``4 cos(pi/m)^2`` for a finite Coxeter bond ``m``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a2_invariants():
    diagram = CoxeterDiagrams().from_coxeter_matrix(((1, 3), (3, 1)))
    return diagram.vinberg_invariant_matrix()


def test_vinberg_matrix_retains_its_projective_invariants_and_graph_data() -> None:
    invariants = _a2_invariants()
    left, right = invariants(0), invariants(1)
    projective_line = invariants.projective_line()

    assert invariants in VinbergInvariantMatrices()
    assert invariants in LabelledGraphs()
    assert invariants.cardinality() == cardinal(2)
    assert invariants.vertices().cardinality() == cardinal(2)
    assert invariants.index_set().cardinality() == cardinal(2)
    assert invariants.edges().cardinality() == cardinal(1)
    assert invariants.has_edge(left, right)
    assert invariants.is_parent_of(left)
    assert isinstance(left, invariants.ElementType)
    assert invariants.vinberg_invariant(left, right) in projective_line
    assert invariants.vinberg_ratio(left, right) == 1
    assert invariants.vinberg_ratio(left, right) in invariants.base_ring()
    assert invariants.edge_label(left, right) == invariants.vinberg_invariant(left, right)
    assert invariants.vertex_label(left) == invariants.vinberg_invariant(left, left)


def test_vinberg_matrix_recovers_the_a2_coxeter_data_and_type() -> None:
    invariants = _a2_invariants()
    diagram = invariants.coxeter_diagram()
    matrix = invariants.coxeter_matrix()

    assert diagram in CoxeterDiagrams()
    assert diagram.cardinality() == cardinal(2)
    assert diagram.coxeter_entry(diagram(0), diagram(1)) == 3
    assert invariants.coxeter_entry(invariants(0), invariants(1)) == 3
    assert Groups.Coxeter(matrix).order() == 6
    assert invariants.is_elliptic()
    assert not invariants.is_hyperbolic()
    assert not invariants.is_parabolic()
    assert not invariants.is_compact_hyperbolic()
    assert not invariants.is_paracompact_hyperbolic()
    assert invariants.is_crystallographic()
    assert invariants.is_simply_laced()
    assert invariants.is_symmetric()
    assert not invariants.is_directed()


def test_vinberg_submatrix_and_weighted_graph_preserve_the_selected_invariants() -> None:
    invariants = _a2_invariants()
    left, right = invariants(0), invariants(1)
    submatrix = invariants.submatrix((left,))
    weighted = invariants.weighted_graph()
    weighted_left, weighted_right = weighted(0), weighted(1)

    assert submatrix in VinbergInvariantMatrices()
    assert submatrix.cardinality() == cardinal(1)
    assert weighted in LabelledGraphs()
    assert weighted.cardinality() == cardinal(2)
    assert weighted.edges().cardinality() == cardinal(1)
    assert weighted.vertex_label(weighted_left) == invariants.vertex_label(left)
    assert weighted.edge_label(weighted_left, weighted_right) == invariants.edge_label(left, right)


def test_vinberg_matrix_morphisms_have_the_expected_identity() -> None:
    invariants = _a2_invariants()
    identity = invariants.Mor(invariants).identity()

    assert identity(invariants(0)) == invariants(0)
    assert identity(invariants(1)) == invariants(1)
    assert identity * identity == identity
