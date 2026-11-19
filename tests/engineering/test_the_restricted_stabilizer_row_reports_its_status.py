r"""The restricted-stabilizer row reports a status, and does not fail while building.

``tests/coble_restricted_stabilizer.py`` builds `Stab_{Gamma_{En,2}}(delta)` for
the `(-2)`-vector `delta` of `T_En` whose perpendicular is `T_Co`.  The subgroup
is built from the coinvariant extension of the Enriques involution, so **its own
lattice is the construction's**, not the catalogue's `T_En`: `delta` belongs to
the subgroup's lattice, and an equal-but-distinct copy of `T_En` is another
lattice, so a `delta` taken from the catalogue gives a vector of no lattice the
subgroup acts on.

The row is correct and long — the stabilizer's generators are the indefinite
port's marked-diagram decision, minutes to hours at rank 12
(`results/issue286-the-restricted-stabilizer-cost.md`) — so its answer inside a
short cap is `undecided`.  What it must not do is fail while constructing, and
the difference is exactly the status: the row reports one for every cap it is
given.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_restricted_stabilizer_row_reports_undecided_and_does_not_fail_building():
    r"""Inside a cap the row is undecided; a construction failure is not a status.

    Three seconds is far below the minutes the stabilizer's generators need, so
    `undecided` is the only correct answer the row can give — and reaching it
    means the subgroup's stabilizer was formed on a vector of the subgroup's own
    lattice rather than failing inside the lattice's family realisation.
    """
    status = restricted_stabilizer_outcome(3)
    assert status == int(1)
