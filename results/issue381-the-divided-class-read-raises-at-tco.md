# `Otilde+`'s row raised: the divided-class key is not complete at `T_Co`

The confirming run went out on a quiet host -- 8 683 MiB of `MemAvailable` -- and
came back with a refusal, not a verdict.  This note records the run, the
measurement that explains it, and what it does to the last note's claim.

## The run

```
PROBE=.tmp/issue381-t15/probe-row-otildeplus.py ...
--rows Otilde+ --lattice Tco --route divided-class --cap 10800 --budget 28800
```

`.tmp/issue381-t15/row-otildeplus.log`, one process, the `6144 MiB` guard:

```
[   1723.9 s rss   3204.8 MiB] the split: 180000 planes registered
[Otilde+] error: the row step raised ArithmeticError: the line of the covering
  flag ... carried to Rank-2 cusp ... lies in 4 line cusps of ... : the finite
  image does not separate this line's cusp from the others, and no edge is read
  from class data that names more than one vertex; tits_building_incidence
  decides it with a transporter
[   1908.4 s rss   3549.3 MiB] done: 189721 planes, 1 records
```

What the run *did* establish:

* the split finished: **189 721 planes**, the same number `Otilde`'s returned row
  registered, at **7.05 ms a plane** (`60 000` planes in 423 s) and **3 556 MiB**
  peak -- the length and cost the last two notes predicted;
* the relation built **one** record and then refused.

## Why: 24 of the 444 keys name more than one line cusp

The key the read uses is `_isotropic_line_image_key`, the `rho(Gamma)`-orbit of
the line's class pair -- an invariant of the subgroup's orbits
(D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).
`probe-line-cusps.py` (`line-cusps.log`) buckets both rows' line cusps by it:

| | `Otilde` | `Otilde+` |
| --- | ---: | ---: |
| line cusps | **527** | **527** |
| distinct keys | 444 | 444 |
| keys naming more than one cusp | **24** | **24** |
| largest buckets | 15, 12, 12, 11, 11, 9, 3, 2 | identical |

So the key is an invariant but not a *complete* one, and it is not complete for
either row: the same 24 classes of key name up to fifteen cusps each.  The read
refuses at the first covering flag whose carried line lands on one of them,
which is the honest behaviour the row documents, and it names the route that
decides such an edge instead -- the transporter.

## What this does to the last note

`issue381-the-two-kernel-rows-carry-one-relation.md` claimed the two rows carry
one relation.  **That is refuted at the edge read.**  What survives, and is now
measured on both rows, is the vertex half: `Otilde+` has `527` line cusps and
`189 720` plane cusps, the counts the archive carries.  What does not survive is
the step from "the vertices are the same" to "the relation is the same": the
relation is not read from the vertices alone, it is read from a key that does not
separate them.

## The provenance point, and why it is the larger finding

The `Otilde` row that returned (2 126.9 s, 569 160 records) ran on `8c094f8`,
and the read that raises here is newer than that run: `9ae39a1`, *the
divided-class relation decides its planes as they are reached, and a plane's lift
is spent by its edges*, is a descendant of the evidence commit `3a4a210` that
recorded the return.  So on the current head the route is untested for `Otilde`
too, and since the two rows' cusp sets and keys are the same, `Otilde`'s row is
expected to refuse at the same place.  That is a prediction, not a measurement:
it needs one run of `Otilde` on this head.

## What is not claimed

No code is changed and no test is written: the refusal is the library's stated
behaviour for an ambiguous key, not a wrong answer, so there is nothing red to
write.  Whether the ambiguity is repairable by a finer invariant, or whether the
row must take the transporter route at those 24 classes, is the next question and
is not answered here.

No object is introduced: the key is the library's, the orbit--coset correspondence
is Lemma 3.6's (printed p. 22), and every count above is a datum the library
printed.
