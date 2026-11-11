# #254: `Aut`-orbits of a diagram's maximal elliptic and parabolic subdiagrams

**Result: `maximal_elliptic_subdiagram_orbits` and `maximal_parabolic_subdiagram_orbits`
exist on `CoxeterDiagrams`, for both values of `connected`; their orbits partition the
family the maximal query returns, each orbit is one `Aut`-orbit, `subdiagram_orbit_poset`
accepts them, and a vertex relabelling leaves the orbit counts unchanged.** Measured on the
adopted runtime with the indefinite port at `/work`, in a detached worktree of `main`.

## The gap

`CoxeterDiagrams` had `elliptic_subdiagram_orbits` — the orbits of the elliptic induced
subdiagrams — and `maximal_elliptic_subdiagrams`, and no orbit set of the maximal ones.
Maximality is a relation of a subdiagram to the ambient diagram: no predicate on a
subdiagram decides it, so the file's private G-set adapter `_subdiagram_g_set(predicate,
connected)` cannot express it as written.

## The methods

`src/sage_extensions/categories/coxeter_diagrams.py`:

* `maximal_elliptic_subdiagram_orbits(*, connected=False)` and
  `maximal_parabolic_subdiagram_orbits(*, connected=False)`: the family is
  `maximal_elliptic_subdiagrams(connected=…)` / `maximal_parabolic_subdiagrams(connected=…)`,
  and the orbit set is the same `FiniteGSets(self.Aut())(points, act)` construction the other
  subdiagram orbit queries use, on the ranks of that family's members.  `Aut` carries an
  inclusion of vertex sets to an inclusion, so it permutes a maximal family and the ranks are
  a stable set; the action asserts that stability rather than assuming it.
* `subdiagram_rank(vertices)`: the rank of an induced subdiagram in `induced_subdiagrams`'
  order, so an orbit point can be read back as a subdiagram without enumerating the \(2^n\).

## The slow steps, fixed at their owners

Building the orbit set used to require `induced_subdiagrams()` — every induced subdiagram,
with its graph object and construction data — and the parabolic maximal family required every
parabolic induced subdiagram.  On Sterk's cusp diagrams that is \(2^{12}\) to \(2^{14}\)
diagrams per query.  Rather than accept it, the owners are repaired, with the results
unchanged:

| owner | before | after |
| --- | --- | --- |
| `_subdiagram_g_set` admits on vertex positions, and ranks are computed (`_subdiagram_rank_of_positions`) instead of looked up | builds \(2^n\) diagrams to filter | no diagram construction |
| the same, on cusp 4.3.5 (12 vertices): building the elliptic orbit set | 16.99 s | 0.14 s |
| the same, parabolic orbits | 17.56 s | 0.19 s |
| `maximal_parabolic_subdiagrams(connected=True)` takes the elliptic query's vertex-set route | 107.16 s | 4.19 s |
| on cusp 4.3.6: `maximal_parabolic_subdiagrams(connected=True)` | 10.07 s | 0.71 s |
| `subdiagram_orbit_poset` recovers a rank's vertex set from the rank | \(2^n\) enumeration | no enumeration |
| both maximal families, cached per `connected` | recomputed per caller | paid once |

`elliptic_subdiagram_orbits`, `parabolic_subdiagram_orbits` and `subdiagram_orbits` keep the
same points, and `test_coxeter_subdiagrams.sage` — the existing module on this owner — passes
unchanged in the same run as the new one.

## The card rows

`tests/cards/refresh_lattice_database_enriques.py` gains `cusp_diagrams(ref, tag)`: card
`029J`'s `integral.cusp_chambers.<subgroup>` rows keep, per 0-cusp chamber, the walls as
vertices and the card's `diagram` bonds as the Coxeter entries (order `inf` on the card,
`null` in the digest).  The digest is **regenerated, not edited**:

```
python3 tests/cards/refresh_lattice_database_enriques.py --ref dbc9fc6add622459d60dba3dc62d3e4be6b903d7
wrote …/lattice-database-enriques.json at database ref dbc9fc6…: 87 group cards,
36 polarization-count degrees, 1 discriminant forms, 5 cusp chambers 5 cusp diagrams
```

The pin is the one `main` carried when this unit was rebased (`#285`'s evidence commit moved
it to `dbc9fc6`): `#312` reads the same card block for the wall counts, and this push leaves
that section and its pin alone.  Against `main` the digest's diff is the new section and its
`_provenance` line; `cusp_chambers`, and every other section, compare equal field for field.
An earlier revision of this branch was generated at `e8a7f88`, where that card stated Sterk's
fifth 0-cusp chamber as 13 walls; the rebase onto `dbc9fc6` made the whole digest one pin
again, and the fifth diagram now carries its 14 walls and 17 bonds.

## Red

At `2d104cab0d` (`main` before this unit), the test module with the digest in place:

```
$ pytest tests/lattices/test_the_maximal_subdiagram_orbits.sage … --no-time-gates
FFFFFFF                                                                  [100%]
E   AttributeError: 'CoxeterDiagrams.parent_class[_FiniteDigraphEngine].ObjectType' object
    has no attribute 'maximal_elliptic_subdiagram_orbits'.
    Did you mean: 'maximal_elliptic_subdiagrams'?
7 failed in 15.56s
```

## Green

On the pushed tree (`c32f8c1` plus this unit's three commits), with the port at `/work`:

```
$ pytest tests/lattices/test_the_maximal_subdiagram_orbits.sage \
         tests/lattices/test_coxeter_subdiagrams.sage \
         -q -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget \
         -p sage_extensions.testing.test_lint --no-time-gates --tb=short -rf -p no:cacheprovider
............                                                             [100%]
========================== test-call performance gate ==========================
tests/lattices/test_the_maximal_subdiagram_orbits.sage::test_the_orbits_partition_the_maximal_elliptic_subdiagrams: 75.00 s > 20 s
tests/lattices/test_the_maximal_subdiagram_orbits.sage::test_the_rank_of_a_subdiagram_is_its_rank_in_the_induced_enumeration: 69.05 s > 20 s
tests/lattices/test_the_maximal_subdiagram_orbits.sage::test_a_vertex_relabelling_leaves_the_orbit_counts_unchanged: 146.16 s > 20 s
12 passed in 1307.44s (0:21:47)
[peakrss] peak tree RSS      : 795 MiB
```

That run was taken while the shared VM carried other chats' jobs at a load average of about
fourteen on four cores; the same selection took 299.31 s an hour earlier on an idle VM.

Seven of the twelve are the new module and five are `test_coxeter_subdiagrams.sage`, the
existing module on this owner, which passes unchanged — the refactor keeps the points and the
order of the queries it re-routed.  An earlier run of the same two modules on the pre-rebase base
gave `12 passed in 370.11s`; the tree then differed by `#286`'s commits, by the two adapters
this unit drops afterwards, and by the fifth diagram's pin, none of which this module's
assertions depend on.

`just test-lint tests/lattices/test_the_maximal_subdiagram_orbits.sage` on the adopted
runtime: `1 files, 0 findings`, exit 0.

The first version of the relabelling fixture reversed the relabelled matrix's columns without
reversing its rows, so it compared `E_6` with a different diagram and failed (`|Aut|` 4
against 2) — the one failure of the run before the fixture was fixed, which the feature
commit's message records.

## The counts the run meets — recorded, not asserted

No lattice-database card states how many `Aut`-orbits a cusp diagram's maximal subdiagrams
fall into, so the test asserts the partition, the orbit identity and the order, never a
number.  What it meets, at digest pin `dbc9fc6`:

| specimen | vertices | \|Aut\| | elliptic, `connected=False` | elliptic, `connected=True` | parabolic, `connected=False` | parabolic, `connected=True` |
| --- | --- | --- | --- | --- | --- | --- |
| `E6` | 6 | 2 | 1 member / 1 orbit | 1 / 1 | 0 / 0 | 0 / 0 |
| cusp 4.3.5 | 12 | 4 | 44 / 15 | 20 / 6 | 36 / 13 | 12 / 6 |
| cusp 4.3.6 | 10 | 1 | 9 / 9 | 4 / 4 | 2 / 2 | 2 / 2 |
| cusp 4.3.7 | 12 | 2 | 34 / 18 | 8 / 4 | 31 / 17 | 7 / 5 |
| cusp 4.3.8 | 11 | 2 | 29 / 17 | 10 / 5 | 14 / 8 | 6 / 4 |
| cusp 4.3.9 | 14 | 8 | 132 / 24 | 16 / 3 | 154 / 28 | 24 / 8 |

`E6` is elliptic, so its parabolic family is empty: the test states that (`== 0`) instead of
skipping the row, and guards the parabolic partition on the cusp specimens being nonempty.

The five specimens are the card's diagrams, and the fifth is the 14-wall, 17-bond diagram the
card states at `dbc9fc6`.  `a36d86a` (`#312`) records that the library's computed chamber at
that cusp has 13 walls where the card states 14 — that discrepancy is `#312`'s, and this test
follows the card the digest carries.  The counts for that row were measured on the identical
row at the earlier pin `5c66bb3` (the walls and bonds of the two rows compare equal) and are
recorded here for that reason.

## What is not done here

* Consolidating `cusp_diagrams` into `#312`'s `cusp_chambers` section: this projection is a
  superset of that one's fields, and the two should be one section once `#312`'s reader is
  retired.  It is a separate section here because `#312`'s rows are that chat's, and the
  batch that assigned this unit says not to edit them.
* No count is asserted anywhere, because no card carries one; a card value for these orbit
  counts would let the table above become an assertion.
