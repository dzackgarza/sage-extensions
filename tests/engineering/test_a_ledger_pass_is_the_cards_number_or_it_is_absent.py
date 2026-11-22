r"""A line's ``PASS`` is a run's state, not a comparison: the card decides the row.

The acceptance aggregate of #319 (``--coverage``) reports a required row decided
when the ledger holds a ``PASS`` for it.  The ledger is a file on disk -- one line
per attempt, appended by whatever run measured the row, at whatever revision, and
read later by a process that did not measure it -- so the label on a line cannot be
what decides the row.  What decides it is the number the line says the call
returned, set against the number the row's card states, read by the row's tag at
the moment the aggregate runs.

Three ledgers decide that here, each written by the test rather than read from an
evening's run:

* a line labelled ``PASS`` whose returned value is one more than the card's is not
  a decision: the aggregate names the row absent and exits 1, even though the line
  is otherwise exactly the shape a passing attempt has;
* a line whose own recorded ``expected`` is not the card's is absent too -- a ledger
  that agrees with a number its card does not state establishes nothing, whether the
  disagreement is a stale reading of the card or a hand-written line;
* a line whose returned value *is* the card's is decided, so the rule refuses
  nothing that agrees with the card it is compared against.

The card's number is read here by the row's own tag, through the same reader the
module measures against (``card_row_value``, bound by this directory's
``conftest.py``), so no expected value is typed in this file.
"""


def _ledger_line(expected, returned, state="PASS"):
    r"""One attempt at ``otilde-plus-t-en``'s line row, at the shape the module appends."""
    return {
        "row": "otilde-plus-t-en:lines",
        "card": "otilde-plus-t-en",
        "quantity": "lines",
        "degree": None,
        "lattice": "029J: U + U(2) + E8(-2)",
        "group": "Otilde+(T_En)",
        "expected": expected,
        "returned": returned,
        "detail": None,
        "state": state,
        "elapsed": 93.6,
        "revision": "9e36bc4",
        "measured_at": "2026-11-21T00:00:00Z",
    }


def _card_value() -> int:
    r"""The card's own line count for ``Otilde+(T_En)``, read by tag."""
    return card_row_value("otilde-plus-t-en", "lines")


def test_a_pass_line_that_returns_another_number_is_absent(tmp_path) -> None:
    r"""A line's label is not its value: one off the card's number is not a decision."""
    stated = _card_value()
    ledger = ledger_holding(tmp_path, [_ledger_line(stated, stated + 1)])
    status, output, _rows = runs_the_module(
        "--coverage", ledger, "--tags", "otilde-plus-t-en", "--rows", "lines"
    )
    assert status == 1, (status, output)
    assert [line for line in output if "ABSENT otilde-plus-t-en:lines" in line], output


def test_a_pass_line_measured_against_another_number_is_absent(tmp_path) -> None:
    r"""A self-consistent line that is not the card's number establishes nothing."""
    stated = _card_value()
    ledger = ledger_holding(tmp_path, [_ledger_line(stated + 1, stated + 1)])
    status, output, _rows = runs_the_module(
        "--coverage", ledger, "--tags", "otilde-plus-t-en", "--rows", "lines"
    )
    assert status == 1, (status, output)
    assert [line for line in output if "ABSENT otilde-plus-t-en:lines" in line], output


def test_a_pass_line_that_returns_the_cards_number_is_decided(tmp_path) -> None:
    r"""The card's own number is a decision, so the rule is not a refusal of every line."""
    stated = _card_value()
    ledger = ledger_holding(tmp_path, [_ledger_line(stated, stated)])
    status, output, _rows = runs_the_module(
        "--coverage", ledger, "--tags", "otilde-plus-t-en", "--rows", "lines"
    )
    assert status == 0, (status, output)
