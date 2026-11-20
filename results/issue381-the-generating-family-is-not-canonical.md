# The source: `O(T_Co)`'s generating family is not the same family twice

The theorem that makes the difference a defect is the one already stated
(`issue381-the-key-is-not-reproducible.md`): a line cusp is a `Gamma`-orbit and
`Gamma = ker rho` acts trivially on `A_L`, so the cusp -- not its representative
-- decides the divided class, and the partition of the cusps by class is
determined by the lattice and the subgroup.  Two processes disagreeing is
therefore a defect, and this note names its seat.

## The first divergence

`probe-divergence.py` (`divergence.log`), both seeds, every cusp dumped as
(position, span, key):

```
cusps: 527 and 527
first differing position: 0
  seed 0: span ((0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0),) key ['[ f3 ]']
  seed 1: span ((0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0),) key ['[ f2 ]']
span sets equal: False
  spans only in seed 0: 480
  spans only in seed 1: 520
key multisets equal: False
```

The rows differ at the **first** cusp, and they share only `527 - 520 = 7`
spans.  So the two rows are not the same objects in a different order: they are
almost disjoint enumerations.  That rules out a reordering -- of a Python set, a
dict, or the frontier -- as the seat.

## The seat

Every line of the row is `splitting.transport_isotropic_object(representative)`
for a lift `splitting` spelled by the walk, and the walk's letters index
`ambient = tuple(O(L).group_generators())` (`_ambient_generators`).  That family
is computed, not canonical, and `probe-generators.py` (`generators.log`) dumps it
in both processes:

```
generator counts: 358 and 336
ordered families equal: False
```

**The family itself has 358 elements in one process and 336 in the other.**  With
a different family the letter indices differ, so the same coset is spelled by
different words, its lift is a different isometry, and every transported line
differs -- which is exactly the 480/520 split above.  (The probe's "families
equal as sets" line is not evidence: it compares `repr`s of morphisms, which
collide.)

The chain, each link measured except the last:

1. the ambient generating family's size differs between processes -- **358
   against 336**;
2. the numbered rows' spans differ almost everywhere -- **480 and 520 of 527
   exclusive**;
3. the key multisets differ -- **365 against 346 distinct keys**;
4. and the cusp row's dedup, whose fallback is a transporter search, then admits
   a different 527 objects in each process -- *inferred*, not measured.

## What this changes

The seat is **not** `__hash__` (one bucket, a cost) and **not** the frontier's
iteration order (the rows are disjoint, not reordered).  It is the generating
family that the walk spells in, and the cusp row inherits it.

That also explains two things the record already carried: "the anchor is not
reproduced by a second process", and the sign-ambiguous anchor `v` against `-v` --
both are the same non-canonical family showing through.

The two repairs this names are: make the ambient generating family canonical (a
sorted or otherwise fixed family, the same elements in the same order), or make
the walk's output independent of which generating family spells it -- the cusp,
after all, is an orbit, and the theorem says the orbit does not depend on the
word.  The first is the smaller change and the one whose witness is the family
dump above.

## What is not done

No repair: the lint that would carry the regression test is being repaired at its
owner this cycle, and the brief forbids repairing before the red test is
committed.  The test's exact text is at
`results/issue381-subprocess-partition-test.py`.

No object is introduced: the cusp, the span, the divided class, the lift and the
generating family are the library's, and every count above is a log's.
