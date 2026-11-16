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

An edge's line lies in its plane for a reason of the form and not of the
clause that decides it, so the test that asks the edge clause about a line
outside a plane gives the reason: the plane is totally isotropic, so each of
its vectors pairs trivially with each of its generators, and the line's
generator pairs with one of them by a nonzero integer, which no vector of the
plane does.
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
    A relation over those vertices with no edge in it leaves the plane vertex
    without the edge its lines give it, and a plane cusp of a row always carries
    one; that is the smallest relation that breaks the row's contract, and the
    driver reports it as a contract violation of the row and not as an undecided
    row, returning no counts for it.
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


def test_a_line_that_pairs_nontrivially_with_the_plane_is_outside_it():
    r"""The edge clause passes a generator of the plane and rejects a line pairing with it.

    The plane is spanned by the isotropic vectors ``w1`` and ``w3``, which pair
    trivially with each other, so every vector of the plane pairs trivially with
    ``w1``.  ``w2`` is isotropic and pairs with ``w1`` by two, so no vector of
    the plane is its line: that is the reason the line is outside the plane, and
    it is read off the form, not off the predicate the clause evaluates.
    """
    lattice = NamedLattices.Tco
    isotropic = Coble.isotropic_vectors()
    plane = lattice.subobject_on((isotropic["w1"], isotropic["w3"]))
    inside = lattice.subobject_on((isotropic["w1"],))
    outside = lattice.subobject_on((isotropic["w2"],))

    assert lattice.b(isotropic["w1"], isotropic["w1"]) == ZZ(0)
    assert lattice.b(isotropic["w3"], isotropic["w3"]) == ZZ(0)
    assert lattice.b(isotropic["w1"], isotropic["w3"]) == ZZ(0)
    assert lattice.b(isotropic["w2"], isotropic["w1"]) == ZZ(2)

    assert incidence_edge_containment(lattice, inside, plane) is None
    assert incidence_edge_containment(lattice, outside, plane)


def test_a_row_of_a_lattice_with_no_isotropic_plane_decides_with_its_line_vertex():
    r"""A row whose lattice has no isotropic plane has no edge, and it is decided, not broken.

    ``U + <-2>`` has signature ``(1, 2)``, so it carries no totally isotropic
    plane -- a totally isotropic two-plane would force both indices of the form
    to be at least two -- and its building has line vertices only.  Its row
    therefore returns one line cusp, no plane cusp and no edge, and that is the
    row's complete answer: an edge is a line vertex's incidence with a plane
    vertex, and this row has no plane vertex to carry one, so the driver decides
    it rather than reporting a vertex as left without an edge.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    outcome = incidence_row_outcome(lattice, lattice.Aut(), "O(U + <-2>)", 3600)

    assert outcome.status is RowStatus.DECIDED
    assert outcome.counts == (0, 1, 0)
