# #623: the public plane stabilizer's determinant-`-1` half at Sterk's five planes

**Result of this turn.** The five-plane computation the earlier turns could not run has
been run, in the pinned Sage image, against `main`'s own code. At every one of Sterk's
five plane types the public family `setwise_stabilizer(Pi).group_generators()` contains
integral isometries of determinant `-1`, their plane actions are integral unimodular
`2 x 2` matrices of determinant `-1`, and the `Gamma_{En,2}` cut leaves `1, 1, 2, 1, 2`
orbits of sizes `[8], [8], [2,6], [8], [2,6]`. The new acceptance file
`tests/lattices/test_the_plane_stabilizer_has_its_reversing_half.sage` runs all five
in 154.2 s of test time, 5 tests, 0 failures (the log is
`results/issue623-the-acceptance-row-run.log`; an earlier run of the same file took
155.6 s with the per-test times shifted by under a second).

**The rows were already green before the repair, and this file is not the repair's red
test.** The same probe was run at `19903dc` (the commit the repair `1b20f71` sits on) and
at `1b20f71`, and the numbers are identical at all five planes. So the five planes never
separated the two coset comparisons; what separates them is the finite `GL_2(ZZ/8)`
specimen of `tests/lattices/test_the_plane_projection_walks_its_right_cosets.sage`, which
is red at `b561bf1` and green at `1b20f71`. No red was manufactured here; the honest
content of this row is the acceptance that the repair must leave standing, plus the
determinant measurement the earlier rows never made.

## Measurement

Command, run in the host's extraction of `ghcr.io/dzackgarza/sage:develop`
(`SAGE_BIN=/sage/.venv/bin/sage`, Sage `11.0.beta5`) under PRoot, with the tree under test
bound at `/repo` and `sys.path[0] = /repo/src` so the session is the checked-out one and
not the image's own `/repos/sage-extensions` (`cf656f8c`):

```
./run.sh -b <clone>:/repo -b <probe>:/probe -w /repo -- /sage/.venv/bin/sage /probe/probe_main.py
```

`SESSION FROM /repo/src/sage_extensions/__init__.py`, `CLONE HEAD: 1b20f716...`.
One process per commit, families and planes built once.

| plane | type | family | lattice det `{+1:-1}` | plane actions | plane-action det `{+1:-1}` | cut orbit sizes | orbits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| first | `{2,4,5}` | 121 | 57 : 64 | 10 | 9 : 1 | `[8]` | 1 |
| second | `{4,5}` | 121 | 57 : 64 | 15 | 14 : 1 | `[8]` | 1 |
| third | `{3,5}` | 121 | 57 : 64 | 11 | 10 : 1 | `[2,6]` | 2 |
| fourth | `{3,4}` | 120 | 56 : 64 | 18 | 17 : 1 | `[8]` | 1 |
| fifth | `{5,5}` | 120 | 56 : 64 | 12 | 11 : 1 | `[2,6]` | 2 |

`levi_plane_action_index(trivial_on_quotient=True) = 1` at all five. The same table was
produced at `19903dc`, row for row.

Wrapper calls used in the probe and their times at `1b20f71`: family 3.5-3.8 s per plane,
plane actions 0.1 s, index < 0.1 s, cut orbits 7.4 / 45.6 / 21.4 / 42.3 / 12.9 s. Peak
RSS 545 MiB for the whole process.

## The acceptance file

`tests/lattices/test_the_plane_stabilizer_has_its_reversing_half.sage`, one test per
plane, each asserting three things on that plane:

1. the lattice determinants realized by the returned family are exactly `{1, -1}`
   (`g.determinant()` on the rank-12 lattice `T_En`);
2. every plane action has integral entries and determinant `+-1`, and `-1` occurs
   (`levi_plane_action_generators`, which writes the images of the plane's basis in that
   basis and asserts the coordinates integral);
3. the `Gamma_{En,2}`-cut orbits of the eight antipodal pairs have the sizes of Sterk's
   (4.3.17) types: `[8]`, `[8]`, `[2,6]`, `[8]`, `[2,6]`.

```
SESSION FROM /repo/src/sage_extensions/__init__.py
LOADED /repo/tests/lattices/test_the_plane_stabilizer_has_its_reversing_half.sage in 0.3s
PASS test_the_stabilizer_has_its_reversing_half_at_the_fifth_type (19.6s)
PASS test_the_stabilizer_has_its_reversing_half_at_the_first_type (11.6s)
PASS test_the_stabilizer_has_its_reversing_half_at_the_fourth_type (46.4s)
PASS test_the_stabilizer_has_its_reversing_half_at_the_second_type (51.0s)
PASS test_the_stabilizer_has_its_reversing_half_at_the_third_type (25.6s)
SUMMARY 5 tests, 0 failures
```

The runner loads the file through `sage.repl.load` and calls its `test_` functions; no
weakening, no per-test gate.

## What was not run

* The #616 file's own rows -- `_assert_the_defining_relation` (every generator of the
  family decided by `rho_{L^-} in H`) and `_assert_the_family_generates_the_parabolic`
  (radical index 1, plane-action index 1, quotient-image index 1, `is_parabolic_complete`)
  -- were not rerun this turn. The cut-orbit rows of that file are superseded here by
  item 3 above, on the same families.
* No CI job was added. The connection this session pushes through is a GitHub App without
  the `workflows` permission, so GitHub rejects any push that creates a file under
  `.github/workflows/` ("refusing to allow a GitHub App to create or update workflow ...
  without `workflows` permission"), and the same connection carries no Actions API to
  dispatch a run or read a run id. The run above is therefore the image run itself, made
  on the host's extraction of `ghcr.io/dzackgarza/sage:develop`, not a runner's; the job
  that would repeat it is the one this file leaves out.
