r"""The aggregate comparison is a pass only when every required row has one.

The acceptance of #319 is 349 rows of published orbit counts, and a run reports the
rows it was given: eight agreeing plane rows out of 87 say nothing about the other
79.  The no-skip rule is decided here, on a ledger the test writes, so the
question is asked of the aggregate itself rather than of a family's report: a
required row whose ledger holds no attempt is named as absent and the comparison
exits 1, and the same selection whose one row is present exits 0.

The ledger is the durable record the runs append to -- one line per attempt, with
the card, the dimension, the value or the exception, the revision and the elapsed
time -- so writing it here is also the check that a line it holds is what the
aggregate reads.
"""


def _row_line(state, returned, detail=None):
    r"""One attempt's line, at the shape the module appends."""
    return {
        "row": "otilde-plus-t-en:lines",
        "card": "otilde-plus-t-en",
        "quantity": "lines",
        "degree": None,
        "lattice": "029J: U + U(2) + E8(-2)",
        "group": "Otilde+(T_En)",
        "expected": 528,
        "returned": returned,
        "detail": detail,
        "state": state,
        "elapsed": 93.6,
        "revision": "9e36bc4",
        "measured_at": "2026-11-21T00:00:00Z",
    }


def test_a_ledger_that_holds_the_rows_one_is_a_pass(tmp_path) -> None:
    r"""The selected row has a PASS in the ledger, so the aggregate agrees."""
    ledger = ledger_holding(tmp_path, [_row_line("PASS", 528)])
    status, output, _rows = runs_the_module(
        "--coverage", ledger, "--tags", "otilde-plus-t-en", "--rows", "lines"
    )
    assert status == 0, (status, output)


def test_a_row_the_ledger_does_not_hold_is_named_and_fails(tmp_path) -> None:
    r"""An empty ledger holds no attempt for the row: absent, named, and exit 1."""
    ledger = ledger_holding(tmp_path, [])
    status, output, _rows = runs_the_module(
        "--coverage", ledger, "--tags", "otilde-plus-t-en", "--rows", "lines"
    )
    assert status == 1, (status, output)
    assert [line for line in output if "ABSENT otilde-plus-t-en:lines" in line], output


def test_a_row_whose_latest_attempt_did_not_decide_is_absent(tmp_path) -> None:
    r"""A recorded exception is not an agreement, so the aggregate is not a pass.

    The line says what the call raised and holds no value; the aggregate reads the
    state, so a row that raised stays absent rather than counting as covered.
    """
    ledger = ledger_holding(
        tmp_path, [_row_line("BROKEN", None, "ArithmeticError: the plane row raised")]
    )
    status, output, _rows = runs_the_module(
        "--coverage", ledger, "--tags", "otilde-plus-t-en", "--rows", "lines"
    )
    assert status == 1, (status, output)
    assert [line for line in output if "the latest attempt is BROKEN" in line], output
