# The cusp hash is one bucket: `hash((class, id(subgroup), rank))`

The key partition of `Otilde`'s line cusps at `T_Co` differs between processes
(`issue381-the-key-is-not-reproducible.md`).  This note records the red test the
brief asked for, what it can and cannot witness, and the site the search reached.

## The test, and why it is green

`tests/lattices/test_the_line_cusp_partition_is_one_partition.sage` builds the
partition twice in one process -- clearing the cusp cache between the runs -- on
the public divided class of each cusp's representative, and asserts the two are
one partition.  On this head it **passes** (`1 passed in 223.84 s`, the call
218.76 s over the 20 s gate).

That is not the defect being absent: the same computation in **two** processes
under different `PYTHONHASHSEED` differs at every position
(`probe-hashseed.py`, `hashseed.log`):

| | seed 0 | seed 1 |
| --- | ---: | ---: |
| line cusps | 527 | 527 |
| positions whose **span** differs | \multicolumn{2}{c}{**527 of 527**} |
| distinct divided-class keys | 368 | 387 |

A test cannot express that: the test lint's `TL01` admits only the session import,
so a test file cannot spawn a subprocess, and in one process the walk is stable.
So the red witness is cross-process and lives in the probe, not in the suite --
stated here rather than worked around, and the committed test is kept because it
pins the in-process half.

## The site

    class _ArithmeticCuspEngine(SageObject):
        def __hash__(self) -> int:
            return hash(
                (_ArithmeticCuspEngine, id(self.subgroup()), int(self.module_rank()))
            )

`isotropic_orbits.py:942`.  Two things follow from that one line:

1. **Every cusp of a rank under one subgroup has the same hash.**  A `set` or
   `dict` of cusps is therefore a single bucket, and every membership test falls
   to `__eq__` (`:925`), whose fallback for unequal spans is
   `transporter_witness(other.representative())` -- the port isometry search the
   record already prices at 355 s.  A row that deduplicates cusps through a
   table pays that per comparison; the cusp row's docstring says as much and
   admits points "as they are produced" instead.
2. **The hash carries a process address**, `id(self.subgroup())`, so the value
   differs between processes.  Anything that orders by hash -- a `set`'s
   iteration, a `dict` built in hash order -- orders differently in each process.

Which of those two produces the 527-of-527 span difference is **not yet shown**:
a constant hash makes a set degenerate to insertion order, and insertion order
is the walk's, so the constant hash alone does not explain it.  The other
candidate is the walk's own frontier -- GAP's `Set(List(...))` and the order in
which the generating images are applied -- and the two are separated by a probe
that dumps the frontier at the first divergence, which is not run here.

## What is not done

No repair: the brief forbids repairing before the red test is committed, and the
red test cannot be committed because the suite cannot spawn the process that would
make it red.  What is committed is the in-process half plus this note, so the next
round starts from the site rather than from the symptom.

No object is introduced: the cusp, its span, its divided class and the transporter
are the library's, and the counts are the probe's.
