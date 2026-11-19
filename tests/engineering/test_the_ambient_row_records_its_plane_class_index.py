r"""The incidence driver records the plane class index at the ambient row.

``#286`` asks for `[Stab_{O(q)}(J) : rho(Stab_{O(L)}(P))]` over every liftable
`J = [P/2]`, for every row, and the ambient `O(L)` row is a row.  The index is
read from the plane's own parabolic, which every row has, so the driver's run
of the `O` row must record it.  `U + U(2) + <-4>` is the smallest gate lattice
whose plane row returns in seconds; its ambient row has one plane cusp.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_ambient_row_of_a_run_records_the_plane_class_index():
    r"""A run of the `O` row decides and records the index at its plane class."""
    status, recorded = incidence_rows_plane_class_indices(
        ["--rows", "O", "--lattice", "U+U(2)+<-4>", "--plane-class-index", "8", "--cap", "600"]
    )
    assert status == int(0)
    assert [label for label, _pairs in recorded] == ["O"]
    (_label, pairs), = recorded
    assert pairs != ()
