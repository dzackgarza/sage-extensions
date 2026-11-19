# The no-split answer is askable, and the test names no string

The previous round gave the answer a `reason` but left it unaskable from a
session test: `orthogonal_quotients`'s `__all__` reaches nothing, because that
module is not one of those `all.py` star-imports (`all.py:35-60`), so publishing
four names meant adding four names to the session preamble for one assertion.
Two accessors on the quotient do the same work without touching the preamble:

* `is_no_split(datum)` -- whether a line-splitting datum is this call's answer
  that nothing splits;
* `no_split_reasons()` -- the witnesses a no-split answer can name, in the
  module's order.

A test then reads both sides from the library and compares library values, which
is what the test lint asks for (`tests/lattices/
test_a_line_row_says_which_proof_stopped_the_split.sage`): on `U + U(2) + <-2>`
one ambient line orbit answers with the no-split value whose witness is among the
library's three, the other answers with a class-point family, and the witnesses
are distinct.

Measured: **1 passed in 14.92 s**, the call 9.99 s.

## No red, and why

Before the previous round's change the answer was a bare `"NOSPLIT"`: the
information a test would assert on did not exist, so the only red available is an
`AttributeError` for the missing attribute -- which is exactly the red the
standing rule refuses.  The defect was a loss of information in a return value,
and the test that guards it is green from the round the information appears.  The
probe of that round (`results/issue286-the-no-split-answer-names-its-witness.md`,
`.scratch/w286-probes/probe-reason2.log`) is the evidence that the fixed answer
names a specific witness on that specimen; this round makes the same fact
assertable inside the gate.

## What stays owed

`NO_SPLIT` and its three witnesses are still module constants of
`orthogonal_quotients` and not session names, deliberately: nothing outside that
module needs them now that the quotient answers both questions, and the preamble
gains names by ownership, not by convenience.
