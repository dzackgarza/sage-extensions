r"""The incidence row reports a broken contract apart from an undecided row.

``tests/coble_gamma_co_2_incidence_rows.py`` takes one row of the
Tits-building incidence of a subgroup of ``O(T_Co)`` -- the edges at the
subgroup's plane orbits -- under a per-row cap.  Two facts a row can report
are different in kind: a row that did not return inside its cap states
nothing about the mathematics, because the cap is the caller's budget, while
a row that returned an edge failing its check states that the library's
answer is wrong.  The driver reports the two apart, in words and in its exit
status, and both Coble acceptance drivers draw their row statuses from one
vocabulary.

The smallest input that breaks an edge's contract is one real edge whose
line does not lie in its plane: a primitive totally isotropic plane of
``T_Co`` spanned by two orthogonal isotropic vectors, and a primitive
isotropic line spanned by an isotropic vector outside that plane.  No larger
row is needed, because the contract is checked edge by edge.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_line_outside_its_plane_breaks_the_incidence_rows_contract():
    r"""The row's edge contract passes a line of the plane and rejects a line outside it."""
    lattice = NamedLattices.Tco
    isotropic = Coble.isotropic_vectors()
    plane = lattice.subobject_on((isotropic["w1"], isotropic["w3"]))
    inside = lattice.subobject_on((isotropic["w1"],))
    outside_name = next(
        name for name in isotropic
        if name not in ("w1", "w3")
        and not plane.inclusion().is_in_image(isotropic[name])
    )
    outside = lattice.subobject_on((isotropic[outside_name],))

    assert incidence_edge_containment(inside, plane) is None

    violation = incidence_edge_containment(outside, plane)
    assert violation, "an isotropic line outside the plane was accepted as an edge of it"


def test_a_broken_contract_is_reported_apart_from_an_undecided_row():
    r"""The undecided row and the broken contract are different reports and exit statuses."""
    undecided, contract_violation = incidence_row_reports()

    assert "undecided" in undecided.report
    assert "contract violation" in contract_violation.report
    assert undecided.report != contract_violation.report
    assert undecided.exit_status != contract_violation.exit_status
