r"""The incidence row reports a broken contract apart from an undecided row.

``tests/coble_gamma_co_2_incidence_rows.py`` takes one row of the
Tits-building incidence of a subgroup of ``O(T_Co)`` -- the edges at the
subgroup's plane orbits -- under a per-row cap, and reports what the row did.
Three things a row can do are different in kind, and a reader of the run tells
them apart by the status the driver reached and by the exit status that
carries it:

* the row did not return inside its cap.  The cap is the caller's budget, not
  a mathematical statement, so the row claims nothing about the mathematics --
  and a cap that is already spent leaves no time for the call at all;
* the row returned a relation over its vertices that breaks the row's
  contract.  That is a statement about the library's answer, and the driver
  reaches it from the relation it was handed, not from a status it was told;
* the row's call raised.  That is neither of the two: a refused or failing call
  says nothing about the budget and nothing about a returned relation.

The row's data are the lattice and the subgroup it is taken under, so no test
here names a defect of a particular lattice: the relations are relations of
those rows, and the counts are the rows' own counts.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_row_whose_cap_is_spent_is_undecided():
    r"""A row with no time left in its cap is undecided, and a row with time is decided.

    ``A2`` is a definite lattice: it carries no isotropic line and no isotropic
    plane, so its row has no vertex and no edge, and the row that is given time
    decides with the empty relation.  The same row under a cap of zero seconds
    has no time to make the call and is undecided -- the two outcomes differ in
    their status, in the exit status that carries it and in what they report.
    """
    lattice = Lattices(ZZ)("A2")
    spent = incidence_row_outcome(lattice, lattice.Aut(), "A2", 0)
    given = incidence_row_outcome(lattice, lattice.Aut(), "A2", 3600)

    assert spent.status is RowStatus.UNDECIDED
    assert given.status is RowStatus.DECIDED
    assert given.counts == (0, 0, 0)
    assert spent.status.exit_status != given.status.exit_status
    assert spent.report() != given.report()
    assert spent.detail


def test_a_row_whose_call_raised_is_not_an_undecided_row():
    r"""A row whose call raises reports an error, in its own status and exit status.

    ``SO(U(2))`` cuts a determinant kernel only, and its plane row refuses to
    close the stabilizer's index by the divided-class route, so the row's call
    raises: the row is neither undecided -- the caller's cap is not what stopped
    it -- nor decided, and the run must not exit with the status of a row that
    merely ran out of time.
    """
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    failed = incidence_row_outcome(lattice, lattice.SO(), "SO(U(2))", 3600)
    spent = incidence_row_outcome(lattice, lattice.SO(), "SO(U(2))", 0)

    assert failed.status is RowStatus.ERROR
    assert failed.status is not spent.status
    assert failed.status.exit_status != spent.status.exit_status
    assert failed.report() != spent.report()
    assert failed.detail


def test_a_relation_that_leaves_a_vertex_without_an_edge_is_a_contract_violation():
    r"""A row's relation that leaves its vertices unjoined breaks the row's contract.

    ``U + U`` has one isotropic line orbit and one isotropic plane orbit under
    ``O(U + U)``, so its row has a vertex of each kind and an edge between them.
    A relation over those vertices with no edge in it leaves both without an
    edge, which is the smallest relation that breaks the row's contract: the
    driver reports it as a contract violation of the row and not as an
    undecided row, and it returns no counts for it.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    subgroup = lattice.Aut()
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    assert lines
    assert planes

    unjoined = incidence_row_contract(lattice, subgroup, lines, planes, ())
    spent = incidence_row_outcome(lattice, subgroup, "O(U + U)", 0)

    assert unjoined.status is RowStatus.CONTRACT_VIOLATION
    assert unjoined.status is not spent.status
    assert unjoined.counts is None
    assert unjoined.status.exit_status != spent.status.exit_status
    assert unjoined.report() != spent.report()
    assert unjoined.detail
