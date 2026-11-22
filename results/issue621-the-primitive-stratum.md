# #621 — card 0128's `#h` row reads the primitive stratum, and lost it in a rewrite

Commit: (this commit, `main`).

The card is right. `#h` in Table 4 is the number of `O(M(1/2))`-orbits of *primitive*
vectors of degree `2d`, and the acceptance row compared it with the number of
`O(M(1/2))`-orbits of *all* vectors of that square. On the square-8 shell the call
returns three classes where the card states two: two primitive classes of square 8,
and the class of `2w` with `q(w) = 2`, which is not a primitive vector and so not a
numerical polarization in the source's sense. No card value is touched and no
certificate is refuted.

The reading was repaired once already. `69469e7` (*fix: The Table 4 degree row asks
for the primitive vectors the card counts*, 2026-11-19) made exactly this change, with
exactly this diagnosis and this count of thirteen affected degrees; `5befdf9` (*test:
every Enriques and K3 orbit row is compared with the card that states it*,
2026-11-21) rewrote the module and dropped the argument, and issue #621 was filed the
next day reporting the three degrees the earlier run reached. This round restores the
argument, states the source's condition where a rewrite reads it, and records that the
guard the earlier round named does not test the module at all.

## The source's definition, with its numbered statements

D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces ---
computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2.

* **The object.** Section 2, the paragraph introducing (3): a numerical polarization
  of degree `2d` is a class `h` of `M(1/2) = U + E8(-1)` with `h^2 = 2d > 0`, and
  "For what follows we can and will assume that this vector is primitive." The
  stabilizer is `O(M(1/2), h) = {g in O(M(1/2)) | g(h) = h}`, and (3) defines
  `Γ_h = π_N^{-1}(π_M(O(M,h)))`.
* **The group.** Section 1: for a given degree "one has to expect many primitive
  vectors `h` which are not equivalent modulo the action of the isometry group of
  the Néron-Severi lattice `M(1/2) := U + E8(-1)`"; Theorem 3.5's proof takes
  `H = {Σ α_i g_i | α_i ≥ 0}` as "our chosen fundamental domain of the group
  `O(U + E8(-1))`", which is the full isometry group. The counts measured with it
  agree with the card at all 36 degrees.
* **The count.** Section 3.4, the paragraph introducing Table 4: "Table 4 gives the
  following information for each degree `2d = 2, ..., 72` and corresponding genus
  `g = 2, ..., 37`: the first line shows the number `#h` of orbits of primitive
  vectors in a given degree." Section 3.2 states the aim: "to enumerate the number
  of inequivalent polarizations in a given degree (for small values of `d`)", and
  Theorem 3.3 with Table 3 lists the representative vectors of norm at most 30 in
  the fundamental domain.
* **No ampleness condition is part of the count.** Section 1 says that the root and
  `(-4)`-hyperplanes are removed from the *variety* so that `h` represents an ample
  class, that not removing them gives quasi-polarizations, and that the paper is
  concerned with the orthogonal varieties `M_{En,h}`. The count is over classes of
  vectors, not over chambers: a polarization's orbit is its vector's orbit.

So `#h(2d) = #{ O(M(1/2))-orbits of primitive h in M(1/2) with h^2 = 2d }`, with no
nef or chamber condition on `h`.

The card's lattice `M(1/2) = U + E8(-1)` is the Enriques lattice `E_10 = U ⊕ E_8 ≅
II_{1,9}` of the volume's definition of the Enriques lattice
(`@def:enriques-lattice`, `writing/lattice-theory/examples/k3-enriques-lattices.md`),
"even, unimodular, of signature (1,9), and ... the unique even unimodular lattice of
that signature up to isometry", which the volume also proves the canonical
complement `K_S^⊥` of the ten-point blowup to be
(`@prop:canonical-perp-is-e10`). Measured: the Gram matrix the acceptance module
builds from the source's (7) is isometric to the catalogue's `E10` (probe
`.tmp/p621-probe-b.log`), and both lattices answer the two strata identically.

## What the call enumerated

`O(W).vector_orbit_representatives(n)` returns one representative of each `O(W)`-orbit
of vectors of square `n`, and its own docstring says so: `content` "selects the
stratum `c * (primitive of square n/c^2)`" and "Every isometry preserves content, so
the strata do not interact." For an indefinite lattice the method unions those
strata over the contents `c` whose square divides `n`. The row called it with
`content=None`.

## The three classes at 2d = 8

Measured on card 0128's lattice at `be381be3` (probe `.tmp/p621-probe.log`; the
representatives themselves are not canonical and differ between runs, so the
classes are named by their invariants):

| class | square | content | square of the primitive part |
| --- | --- | --- | --- |
| 1 | 8 | 1 | 8 |
| 2 | 8 | 1 | 8 |
| 3 | 8 | 2 | 2 |

The strata by content are `{1: 2, 2: 1}`, summing to the 3 the call returns; the
primitive stratum `vector_orbit_representatives(8, content=1)` returns exactly
classes 1 and 2, in 1.5 s against 3.5-5.1 s for the shell.

**Which two are one orbit: none, and which one fails the source's conditions: the
third.** Class 3 is `2w` with `q(w) = 2`. Its content is 2, and content is an
`O(W)`-invariant --- an isometry acts on the chosen basis by a unimodular matrix, so
the gcd of the coordinates is preserved --- hence no isometry carries it onto a
vector of content 1. Its failure of primitivity is the volume's condition: `Z -> L`,
`1 |-> 2w` has cokernel presented by the `10 x 1` matrix of its coordinates, whose
Smith form is `diag(2)`, so the cokernel is `Z^9 ⊕ Z/2` and carries torsion; the
subobject is therefore not a primitive one (the definition of a primitive embedding
in the volume, `@def:primitive-embedding`). Section 2's `h` is primitive, so class 3
is not a numerical polarization in the source's sense, and Table 4 does not count
it. Classes 1 and 2 are the source's two classes at this degree: the library's
decision that they are inequivalent is the marked-lattice computation of
`Lattices(ZZ).CosliceUnder([[8]])` (its `primitive_marking_classes`), and Table 4
with the paper's two other statements of the same list --- it agrees with
`[CDGK, Appendix]` and with `[GH, Corollary 5.6]`, as Section 3.4 says --- states 2.
The representatives printed in Table 3 are an image in the transcription available
here, so the two classes are matched by count and by those two citations, not by a
printed representative.

## Why only some degrees disagreed

Every vector of square `n` is `c * w` for one content `c` with `c^2 | n` and one
primitive `w`, and no isometry changes `c`. So

```
shell(n) = sum over c with c^2 | n of primitive(n / c^2),
```

and the row's number exceeded the card's exactly at the degrees where a stratum of
content `c > 1` is non-empty. Measured for all 36 degrees of Table 4 (probe
`.tmp/p621-probe.log`); the identity held at every one, and the primitive stratum
equalled the card's `#h` at every one:

| $2d$ | shell (the call before the repair) | primitive stratum | card `#h` | sum over contents | contents |
| --- | --- | --- | --- | --- | --- |
| 2 | 1 | 1 | 1 | 1 | `[1]` |
| 4 | 2 | 2 | 2 | 2 | `[1, 2]` |
| 6 | 2 | 2 | 2 | 2 | `[1]` |
| 8 ** | 3 | 2 | 2 | 3 | `[1, 2]` |
| 10 | 3 | 3 | 3 | 3 | `[1]` |
| 12 | 4 | 4 | 4 | 4 | `[1, 2]` |
| 14 | 3 | 3 | 3 | 3 | `[1]` |
| 16 ** | 6 | 4 | 4 | 6 | `[1, 2, 4]` |
| 18 ** | 5 | 4 | 4 | 5 | `[1, 3]` |
| 20 | 5 | 5 | 5 | 5 | `[1, 2]` |
| 22 | 5 | 5 | 5 | 5 | `[1]` |
| 24 ** | 8 | 6 | 6 | 8 | `[1, 2]` |
| 26 | 5 | 5 | 5 | 5 | `[1]` |
| 28 | 8 | 8 | 8 | 8 | `[1, 2]` |
| 30 | 7 | 7 | 7 | 7 | `[1]` |
| 32 ** | 9 | 6 | 6 | 9 | `[1, 2, 4]` |
| 34 | 8 | 8 | 8 | 8 | `[1]` |
| 36 ** | 10 | 8 | 8 | 10 | `[1, 2, 3, 6]` |
| 38 | 7 | 7 | 7 | 7 | `[1]` |
| 40 ** | 13 | 10 | 10 | 13 | `[1, 2]` |
| 42 | 10 | 10 | 10 | 10 | `[1]` |
| 44 | 10 | 10 | 10 | 10 | `[1, 2]` |
| 46 | 11 | 11 | 11 | 11 | `[1]` |
| 48 ** | 15 | 11 | 11 | 15 | `[1, 2, 4]` |
| 50 ** | 10 | 9 | 9 | 10 | `[1, 5]` |
| 52 | 14 | 14 | 14 | 14 | `[1, 2]` |
| 54 ** | 13 | 11 | 11 | 13 | `[1, 3]` |
| 56 ** | 15 | 12 | 12 | 15 | `[1, 2]` |
| 58 | 14 | 14 | 14 | 14 | `[1]` |
| 60 | 16 | 16 | 16 | 16 | `[1, 2]` |
| 62 | 13 | 13 | 13 | 13 | `[1]` |
| 64 ** | 21 | 15 | 15 | 21 | `[1, 2, 4, 8]` |
| 66 | 16 | 16 | 16 | 16 | `[1]` |
| 68 | 16 | 16 | 16 | 16 | `[1, 2]` |
| 70 | 18 | 18 | 18 | 18 | `[1]` |
| 72 ** | 23 | 16 | 16 | 23 | `[1, 2, 3, 6]` |

A degree marked `**` is one the shell count got wrong; there are thirteen of them, and
the issue reports the three the earlier run reached.

The three degrees the issue reports are the three smallest with such a stratum:
`8 = 2^2 * 2`, `16 = 2^2 * 4` (and `16 = 4^2 * 1`), `18 = 3^2 * 2`. The eight
degrees that passed in run 44958950940 are degrees where every `2d/c^2` with
`c > 1` is odd, and an even unimodular lattice has no vector of odd square, so those
strata are empty.

## The reading the rewrite lost

`69469e7` (2026-11-19) repaired exactly this row, with this diagnosis and this count
of thirteen degrees, and its body ends by naming the guard that was to keep it:

> the guard that keeps the reading is
> tests/lattices/test_the_enriques_polarization_degrees_by_card.py, landed in the
> previous commit, whose degree-8 test fails if the reading drops `content=1`.

`5befdf9` (2026-11-21) replaced the module. The new `_computed_table4_row` reads
`orthogonal.unimodular.Aut().vector_orbit_representatives(row.degree)` --- the shell
--- and every other reading in the module is what it was (`lines`, `planes`, `flags`
are `isotropic_orbit_representatives(1)`, `isotropic_orbit_representatives(2)` or
`isotropic_plane_orbits(representatives)`, and `isotropic_orbit_representatives(2,
flag=True)`); diffing the two versions of the file on the calls is how that was
checked, and this one argument is the only difference.

The named guard did not fire, and cannot: it imports only the session and calls
`NamedLattices.E10.Aut()` itself, so it asserts the mathematics of the row and never
touches the module. Measured at `be381be3`, where the row is red:

    tests/lattices/test_the_enriques_polarization_degrees_by_card.py   [GREEN]

    ============================= test session starts ==============================
    collected 3 items
    tests/lattices/test_the_enriques_polarization_degrees_by_card.py ...     [100%]
    5.01s call  test_the_degree_eight_row_counts_the_primitive_class_alone
    3.34s call  test_the_smallest_degree_row_is_the_cards_orbit_count
    0.04s call  test_the_named_lattice_is_the_cards_lattice
    ============================== 3 passed in 14.64s ==============================
    pytest exit: 0

(`-o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p
sage_extensions.testing.test_lint --no-time-gates --durations=0`, in the same
runtime, at `be381be3`, with the row red at the same commit.)

So the sentence above is false as written, and the false claim is why the argument
could be dropped in a rewrite of the file it was meant to protect. That is the
finding this round files; the correction is appended to
`results/issue319-card-verification.md` rather than written into its old text.

## The repair, at the call's owner

`tests/enriques_polarization_rows_by_card.py`, `_computed_table4_row`: the one place
the module asks for these classes now reads
`unimodular.Aut().vector_orbit_representatives(row.degree, content=1)`, with the
source's condition stated at the documentation of the row and of the module, where a
rewrite of the file meets it. The operation is unchanged and its answer was never
wrong: the orbits of the square shell are three at `2d = 8`, and they stay three.
Both Table 4 rows are read off the same classes, so `#Γ̄_h` --- the number of distinct
triples of line, plane and flag counts over them --- stops counting non-primitive
classes as well.

## The red and the green

Both runs are the module's own rows, each in a child process of its own, in the
pinned runtime (`~/sage-image/run.sh` over the rootfs, `PYTHONPATH` bound to this
worktree's `src` and to the pinned indefinite port).

    before (be381be3):  python3 tests/enriques_polarization_rows_by_card.py \
                            --degrees 8,16,18 --rows "#h"
    ROW 0128:#h:8   [FAIL]  expected 2  call 3   (5.9 s)
    ROW 0128:#h:16  [FAIL]  expected 4  call 6   (7.4 s)
    ROW 0128:#h:18  [FAIL]  expected 4  call 5   (5.9 s)
    0 of 3 rows agree with their cards          (exit 1)

    after:              python3 tests/enriques_polarization_rows_by_card.py \
                            --tags 0128 --rows "#h"
    ROW 0128:#h:2 ... 0128:#h:72    [PASS]   each one's count equal to its card's
    PASS: 36   FAIL: 0   MISSING: 0   UNDECIDED: 0   BROKEN: 0   NOT REACHED: 0
    36 of 36 rows agree with their cards          (exit 0)
    per-row call 3.9 - 5.2 s, each row in a child process of its own

The red is this row and not a new collected test, and the reason is structural, not a
choice: the defect is the argument of a call site, so no test that calls the
operation on the mathematics can be red (its answer is right, and the two counts
differ, which is what such a test asserts); the module that makes the call is a
non-collected acceptance module, and `test_lint` TL01 lets a collected test import
only the session, `pytest` and `__future__`, so no collected test can call it. The
row is the instrument that measures this defect --- it is red on `main` in run
44958950940 as the issue records, and red here at `be381be3` --- and the gate that
runs it is the image job `enriques-polarization-rows`.

What would guard it is a reading that cannot be written without the argument. The
library offers none: `vector_orbit_representatives(square)` is the shell and
`content=1` is the primitive stratum, and a second name for the one-argument call
would be a duplicate spelling of an operation the tree already presents. So the
module's docstring states the condition at the row it belongs to, and the row is the
check.

## Reproducing the two strata

    python3 - <<'PY'
    from sage_extensions.all import *
    L = NamedLattices.E10                      # M(1/2) = U + E8(-1), @def:enriques-lattice
    corner = lambda n, c=None: int(L.O().vector_orbit_representatives(n, content=c).cardinality())
    print(corner(8), corner(8, 1), corner(8, 2))     # 3 2 1
    print(corner(16), corner(16, 1), corner(16, 2))  # 6 4 2
    print(corner(18), corner(18, 1), corner(18, 3))  # 5 4 1
    PY

## What this does not do

* The `#Γ̄_h` rows of card 0128 are not decided here: they build `Γ_h` for each class
  and call the isotropic-orbit classifier on an arithmetic subgroup of `O(T_En)`,
  and that call did not return for any row in this environment (#319's own finding).
  The repair changes which classes they are read from, not whether they return.
* The 87 `gamma-h-N` rows are untouched; they do not read a square shell.
* Nothing dispatched the CI job: the workflow that runs these rows is stored at
  `results/issue319-enriques-polarization-rows.workflow.yml`, not under
  `.github/workflows/`, because the connected GitHub connection cannot create a
  workflow file. The runs above are local, and a run of the job is what would put the
  36 `#h` rows in CI's record.
* No card value was changed and no card certificate was refuted: the card was right,
  so there was nothing to refute.

## Where the volume stands

The volume states no `#h` row: `writing/` names card 0128's Table 4 nowhere, and the
objects this result uses are the Enriques lattice (`@def:enriques-lattice`, proved
the canonical complement `K_S^⊥` of the ten-point blowup at
`@prop:canonical-perp-is-e10`) and the volume's notion of a primitive subobject
(`@def:primitive-embedding`). The result therefore departs from no stated conjecture
or expectation: it confirms the count that the volume's moduli picture assumes when
it fixes a numerical polarization of degree `2d` and forms `F_{En,2d}`, and it fixes
which classes the library must count to match it.
