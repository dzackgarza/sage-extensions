r"""An absent row, or a row that is not PASS, is never reported as agreement.

The acceptance module of #319 compares each row of a published family with its
lattice-database card, and its contract is that agreement is the only thing it can
report as a pass.  Two ways of breaking that contract are decided here: a selection
that matches none of the rows the module enumerates -- a mistyped card tag or a
degree the card does not state, which is how a matrix entry would silently compare
nothing -- and a row whose card states no such value, which must be reported
``MISSING`` and must fail the run.

Both are read from a child run of the module, together with the per-row record it
appends under ``.timings/``: the record is what a current raw outcome is retrieved
from, so the test reads the state and the revision out of it rather than out of the
printed report alone.
"""


def test_a_selection_that_matches_no_row_fails() -> None:
    r"""A card tag the digest does not carry selects nothing, and that is exit 2."""
    status, output, _rows = runs_the_module("--tags", "029X")
    assert status == 2, (status, output)


def test_a_row_that_does_not_decide_is_not_agreement() -> None:
    r"""A row whose call does not return inside its cap is ``UNDECIDED`` and red.

    The row is recorded with the state it reached and the revision it was run at,
    so the record -- not only the printed summary -- says that this row did not
    agree with a card, and the run's status says it too.
    """
    status, output, rows = runs_the_module("--one", "gamma-h-1:lines", "--cap", "1")
    assert status == 1, (status, output)
    assert [row["state"] for row in rows] == ["UNDECIDED"], rows
    assert rows[0]["revision"], rows
    assert rows[0]["card"] == "gamma-h-1", rows
