# The kernel row's checkpoint: what is on disk, what a resume can hold, and what a resumed plane costs

The item asked for `Otilde+`'s last 9720 planes to be run from the state the
interrupted chat left at 13:57.  That state is a **stub**: it holds two planes of
the rank-5 specimen `U + U(2) + <-2>`, not the 180000-plane `T_Co` row, and the
keys it holds name a second process's lattice.  The protocol it belonged to was
broken in three more ways, which are named and repaired below.  What is
delivered is a run that stops at the last complete mark, writes what a tail can
actually adopt, and exits, verified end to end on the one specimen small enough
to run twice in a minute -- together with the measurement that says what a
resumed `T_Co` plane would cost, which is what forbids the fifth full row.

## 1. The checkpoint on disk is a stub

| | |
| --- | --- |
| file | `.tmp/issue381b/checkpoint-Otilde.pkl` |
| size | 135 bytes |
| contents | `{'row': 'Otilde', 'planes': [2 entries]}` |
| spans held | rank **5** rows -- `((0,1,0,0,0),(0,0,0,1,0))`, `((0,1,0,0,0),(0,0,1,0,0))` |
| key form | `(id(lattice), rows)` -- a dead process's address, `123719119012432` |

It was written by a two-plane split of the small specimen's `Otilde` row
(`resume-split-small.log`, 13:57:03, "checkpoint written: 1 planes, 90 bytes"),
and the tail run at 13:58:23 read it and stopped there: its log's last line is
"checkpoint read: 2 planes" and it has no launcher-exit line, because the chat
that owned it was cut.  Nothing on disk is `Otilde+`'s state: the 4220-MiB,
68-minute split that reached 180000 planes wrote no checkpoint, and this file is
80 minutes older than the row it was supposed to resume.

So "run the remaining 9720 planes from it" had no state to run from, and the
spans it does hold cannot be used as they stand: `_subobject_of_span` refuses a
span whose first entry is another lattice's id, by name.

## 2. Three things that would have stopped a tail even with 180000 planes

1. **The span key is not a key across processes.**  `_span_key` returns
   `(id(lattice), hermite_rows)` (`categories/isotropic_orbits.py`), so a
   checkpointed span names a coordinate set in one process and an address in the
   next.  A tail must re-anchor the rows to the lattice it built.
2. **The finite element the relation reads at every plane does not pickle.**
   `tits_building_incidence_by_divided_classes` reads
   `registered_isotropic_discriminant_of_span(span)` at each of the row's planes
   and spells an integral lift at one plane per covering position, and no other
   registry datum.  A per-plane entry of `(span rows, that element)` is the
   smallest thing a tail could want -- and it cannot be written: pickling the
   element serializes its category's metaclass and raises
   `_pickle.PicklingError: __reduce__ must return a string or tuple, not
   NoneType` (`anchor2-small.log`).  The only per-plane datum a checkpoint can
   hold is therefore the **word**, and reading the element back from a word is
   spelling the lift.
3. **A cusp row seeded without its rank poisons every rank.**  The previous
   driver seeded the plane row with `subgroup.cusps.set_cache(row)`; with no
   arguments the cached method answers *every* call with that value, so the
   relation's `self.cusps(1)` returned the two plane cusps and the relation
   refused: "the line of the covering flag ... lies in 2 line cusps"
   (`resume-tail-small2.log`).  The seeding is `set_cache(row, 2)`.

## 3. The anchor is not reproduced by a second process, so a resume pins it

The plane split is a walk from `isotropic_orbit_representatives(2)[0]`.  That
draw is not stable:

| run | source span | parabolic generators |
| --- | --- | --- |
| `probe-anchor.py`, run 1 | `((1,0,0,0,0),(0,0,0,1,0))` | 27 |
| `probe-anchor.py`, run 2 | `((0,1,0,0,0),(0,0,0,1,0))` | 27 |
| the 13:57 split's draw | `((0,1,0,0,0),(0,0,0,1,0))` | **30** |

The family itself *is* a function of the plane: at a copy rebuilt from a span it
is 27 generators, in the same order, as at the drawn plane, twice
(`anchor2-small.log`).  What is not a function of anything is which plane is
drawn.  `resume_after=k` therefore skips `k` steps of *the walk from the anchor
it was given*, which is the same walk only if the anchor is the same -- so a
checkpoint records the source **span**, and both phases walk from
`_subobject_of_span` of it.  The delivered driver refuses to run a tail whose
draw differs from the checkpoint's span, and refuses to accept a tail plane that
the checkpoint already holds (the misalignment a wrong anchor produces).

## 4. The delivered protocol, and its run

`.tmp/issue381b/probe-resume.py`, two processes, `PROBE_PHASE=split` then
`tail`:

* `split` pins the anchor by span, walks to `PROBE_MARK` planes, writes
  `{row, lattice, source rows, [(rows, letters, flip)]}`, exits;
* `tail` re-anchors the rows to its own lattice, spells each word to restore the
  registry entry, reads the prefix's cusps back from their spans, continues the
  walk at the mark, seeds the row by rank, and runs the relation and the
  contract.

On `U + U(2) + <-2>`, `Otilde`, `PROBE_MARK=1`
(`resume-split-small3.log`, `resume-tail-small3.log`):

* split: 1 plane, **136-byte** checkpoint, exit at 10.4 s, 494 MiB;
* tail, a fresh process: checkpoint read, 1 registry entry restored, 1 restored
  plane cusped, walk continued to **2 plane cusps**, **3 line cusps**,
  **4 edges in 2.5 s**, verdict **decided: 4 edges over 3 line cusps and 2 plane
  cusps**, endpoint digest `04c17f79b45ca82a…`, 521 MiB peak.

That is the row's own value: the single-pass driver on this tree returns the
same counts and the same endpoint digest (`small-singlepass.log`), and the
digest is the one the 09:47 single pass recorded.

Repeated on the head this lands on (`933efc6` + this change, whose ten
intervening commits touch the split, the relation and the registry the row is
built from -- `rebased-split.log`, `rebased-tail.log`, `rebased-singlepass.log`):
split 1 plane, 136-byte checkpoint, 494 MiB; tail 2 plane cusps, 3 line cusps,
4 edges in 2.7 s, **decided 4 edges over 3 line cusps and 2 plane cusps**,
digest `04c17f79b45ca82a…`, 521 MiB; single pass both rows, the same counts and
the same digest.  The cusp *representatives* differ between the two processes
even here -- the tail drew line cusp `((2,0,0,-1,0))` where the single pass drew
`((0,0,0,1,0))` -- and the digest, being over the edge's endpoint positions, does
not.  A digest over spans would not be reproducible, and this row's is not one.

## 5. What a resumed `T_Co` plane would cost, and why no row was started

Restoring a plane costs spelling its word -- 110 ms a plane, the recorded cost
of `_iter_splitting_isometries_in_im_rho`'s spelling and the row's dominant
per-plane term.  A tail from 180000 planes pays it 180000 times: **~5.5 h**,
before the 9720 planes it actually wants, and the registry it rebuilds is the
same 1.67-3.4 GiB that killed the row at 4127 MiB.  So this checkpoint cannot
make a 5% tail: a restored plane pays what a drawn plane pays, and the peak
returns.  Two repairs would change that, and neither is in this change:

* a **storable form for the finite element** at its owner, so the tail restores
  the element without the isometry (the relation spells a lift at exactly one
  plane per covering position, so the words are otherwise unread);
* the **fused walk** (`3a2b659`'s lane): one pass that registers, cusps and
  decides a plane's edges before the next, with the cusp spans and the edges on
  disk at each mark.

`T_Co`'s row was **not** started, and the memory lease was neither taken nor
written: `.scratch/memory-lease` holds `stage-1-coble-14je 4.0`, whose process is
live, and `MemAvailable` was 4761 MiB -- 665 MiB against the row's measured 4220
MiB peak.  Waiting is the answer; every run today stayed under 1 GiB (521 MiB the
largest) and needed no claim.

## 6. What was run, and what was not

Run, all on this tree (`db26628` + the split's resume parameter), port
`991b88b0`, the adopted runtime:

* `probe-anchor.py` twice (4-6 s a run, 285 MiB): the two draws above;
* `probe-anchor2.py` (16 s, 563 MiB): the family at a span's copy, and the
  pickle failure of the finite element;
* `probe-rowcounts.py` twice (24 s and 66 s, 420 MiB): 3 line and 2 plane cusps
  both times, with every representative different -- so a digest over spans is
  **not** reproducible across processes, and only the counts and the
  position-indexed endpoint digest are;
* the driver single-pass on both rows (26 s, 507 MiB): 4 edges over 3 line and 2
  plane cusps each, digest `47249bbc…` -- the same counts as the 09:47 run,
  whose spans and digest differ for the reason above;
* the two-phase row above, and the same three runs again on the head this lands
  on (`933efc6`), which return the same counts and digest.

Not run: either kernel row at 189720 planes, and `T_Co` at all.  No
`AttributeError`-for-a-missing-fix red exists for the resume parameter, and none
was manufactured: the parameter is new, and what is asserted instead is the
two-phase run's own counts and digest.
