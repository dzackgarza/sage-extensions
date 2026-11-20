# Only `T_Co` differs, the lint refuses the test, and the cusp row is not the same row twice

## The smallest lattice

`probe-small-keys.py` (`small-keys.log`) ran the same partition in two children
under `PYTHONHASHSEED` 0 and 1 for every lattice the driver names below `Tco`:

| lattice | cusps | partitions equal |
| --- | ---: | --- |
| `6JRS` | 1 | **True** |
| `U + U(2) + <-2>` | 3 | **True** |
| `U + U(2) + <-4>` | 4 | **True** |
| `U + U + <-4>` | 1 | **True** |
| `T_Co` | 527 | **False** (largest buckets `9,9,8,8,7,…` against `7,5,5,5,5,…`) |

`T_Co` is the smallest and the only lattice that shows it, so a regression test
has to run there.

## The test, and the lint that refuses it

The test is written: `results/issue381-subprocess-partition-test.py`, to be
installed at `tests/lattices/test_the_line_cusp_key_partition_across_processes.sage`.
It computes the partition in two children under different `PYTHONHASHSEED` and
asserts equality.

The test lint refuses it, and this is the exact refusal
(`1 error in 4.91s`):

```
tests/lattices/test_the_line_cusp_key_partition_across_processes.sage:17: TL01 import json: take every name from the session
tests/lattices/test_the_line_cusp_key_partition_across_processes.sage:18: TL01 import os: take every name from the session
tests/lattices/test_the_line_cusp_key_partition_across_processes.sage:19: TL01 import subprocess: take every name from the session
tests/lattices/test_the_line_cusp_key_partition_across_processes.sage:20: TL01 import sys: take every name from the session
tests/lattices/test_the_line_cusp_key_partition_across_processes.sage:60: TL10 len(): ask for a cardinality
```

The rule, at its owner:

* `src/sage_extensions/testing/test_lint.py:14` --
  `- ``TL01`` an explicit session import, or an import other than the session, ``pytest`` or ``__future__``;`
* `src/sage_extensions/testing/test_lint.py:59` --
  `ALLOWED_IMPORTS = frozenset({SESSION_MODULE, "pytest", "__future__"})`
* `src/sage_extensions/testing/test_lint.py:253`--`:254` --
  `if alias.name not in ALLOWED_IMPORTS:` / `flag(node, "TL01", f"import {alias.name}: take every name from the session")`
* `src/sage_extensions/testing/test_lint.py:31` and `:293` for `TL10` --
  `` ``TL10`` ``len``: a length assumes finiteness; ask for a cardinality; `` /
  `flag(node, "TL10", "len(): ask for a cardinality")`

No workaround is applied: the test is not installed under `tests/`, and the file
above is its exact text.

## The frontier dump: the anchor differs, and so does the row

`probe-fork.py` (`fork.log`), two seeds, dumping the anchor the walk starts from,
the distinct key set, and the multiplicities:

```
seed 0 anchor ((0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0),)
seed 1 anchor ((0,  1, 0, 0, 0, 0, 0, 0, 0, 0, 0),)
anchor equal: False
distinct key sets equal: False      (365 against 346 distinct keys)
multiplicities equal: False
```

Two things are established:

1. **The drawn anchor is sign-ambiguous**: the same line, `v` in one process and
   `-v` in the other.  That alone cannot change a key, because the key is built
   from the class *pair* `{c, -c}`, which a sign leaves alone.
2. **The two runs do not hold the same 527 objects.**  The distinct key sets
   differ -- 365 against 346 -- and the keys are orbit invariants, so the cusp
   row is not enumerating one representative per orbit in both runs.  The count is
   527 in each, which is the double-coset count, so the row is 527 objects that
   are *not* the 527 orbits.

That is where the nondeterminism sits: not in `__hash__` (which is one bucket and
would only affect cost), but in **which objects the cusp row holds** -- the anchor
is sign-ambiguous, and the row's equality, whose fallback is a transporter
search, is what decides whether two yielded representatives are one orbit.

## What is not done

No repair, and no finer dump: the next step is the per-cusp dump in both
processes, which says whether the two rows differ by swapped representatives of
the same orbits or by genuinely different objects.  The repair follows that, at
`_ArithmeticCuspEngine.__eq__` or at the walk's yield, once the seat is named.

No object is introduced: the anchor, the cusp, its span, its divided class and the
transporter are the library's.
