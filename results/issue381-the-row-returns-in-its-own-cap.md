# The 600 s is a probe's cap: the row returns in its own, at 8.6 ms a plane

This note corrects the cost model two records carry
(`issue381-the-per-plane-half.md`, and the handover that followed it), and it
does so from a log already on `main`.  The model says the `Otilde` kernel row of
`T_Co` "does not return inside a 600 s cap", that 600 s is `235 s` of finite
image plus `2137` planes at `0.19 s`, and that this is "about 7 % over".  The
first clause is true of the *probe*, not of the row.

## The two caps are different numbers

| cap | value | where |
| --- | ---: | --- |
| the driver's per-row cap | **10 800 s** | `tests/coble_gamma_co_2_incidence_rows.py:926` (`--cap`), `:153` |
| the driver's whole-run budget | 28 800 s | `:928` (`--budget`) |
| the probe caps of the later rounds | 600 s (120 s in one, 480 s in another) | `.tmp/probe-prof-long.py`, `.tmp/probe-callees.py`, `.tmp/issue381-t13/probe-gap-attrib.py` |

Every "the row did not return" in the last three rounds is a probe's `600` passed
to `run_row`, i.e. a budget one eighteenth of the row's own.

## What the row does inside its own cap, measured

`Otilde` at `T_Co` returned once, on `main` `8c094f8`, one process, the driver's
own caps (`.tmp/issue381b/row-Otilde-window.log`, quoted in
`issue381-the-plane-rows-per-plane-cost.md` §10):

```
[Otilde] the row's calls returned in 2119.1 s
[Otilde] audited 569160 distinct edges; ordered endpoint SHA-256: 2fcd49b9…284c7
[Otilde] decided: 569160 edges over 527 line cusps and 189720 plane cusps
[   2126.9 s rss   3619.5 MiB] done: 189721 planes, 569160 records
```

and its split's marks give the per-plane rate directly, between two marks and so
free of when the split started:

| mark | wall | planes since the last mark |
| --- | ---: | ---: |
| 10 000 planes | 437.8 s | -- |
| 100 000 planes | 1199.1 s | 90 000 in 761.3 s |
| 180 000 planes | 1901.6 s | 80 000 in 702.5 s |

**8.6 ms a plane** across the whole split (170 000 planes in 1463.8 s), and
`189 720 × 8.6 ms = 1632 s` of planes against a 10 800 s cap.

## So what is the 2137 and the 0.19 s

They are the *same* 600 s window seen twice: the probe stops after 600 s and
`cProfile` reports how many lifts the row's two walks had yielded in it (`2137`,
one generator resume a lift) and what that window cost divided by them.  A rate
taken over a window that contains the row's fixed 235 s of finite image and its
ambient plane orbit is not a per-plane cost of the split, and multiplying it by
the row's 189 720 planes multiplies a startup by a length.

The window is also a **profiled** one, and the profile is a call-count
instrument: it reports `537 786 193 function calls (532 581 282 primitive
calls) in 601.859 seconds`, and at that density its own accounting is a large
part of what it measures.  A per-item cost taken from it is an upper bound on
the profiled run and no statement about the row, which is the number the cap is
compared against.

That is the **seventh correction** to this record's cost model, and the same
shape as the six before it: the number was read off the instrument in front of
the reader rather than off the quantity the claim is about.

## What follows for the deferred rewrite

The rewrite the handover defers -- carry the reached point by a key and act on
the key instead of on the GAP set -- would shorten a row that already returns
with 5.1× of its cap to spare.  It is not what stands between this issue and its
row.  Nothing here says the walk is cheap; it says the row's own instrument
already answers.

## The rank-five acceptance value is not the one the handover names

Re-run on `bb57ca7`, port `991b88b0`, the driver on `U + U(2) + <-2>`, both
kernel rows (`.tmp/issue381-t13/small-rows.log`):

```
[Otilde]  edge 0: L0 < P0   edge 1: L2 < P0   edge 2: L0 < P1   edge 3: L1 < P1
[Otilde]  the degree sequence: line cusps [1, 2] over 3, plane cusps [2] over 2
[Otilde]  audited 4 distinct edges; ordered endpoint SHA-256: 04c17f79…587dc2
[Otilde]  decided: 4 edges over 3 line cusps and 2 plane cusps        (70.15 s)
[Otilde+] decided: 4 edges over 3 line cusps and 2 plane cusps        (82.95 s)
```

The relation is the one the record holds -- 4 edges over 3 line and 2 plane
cusps, plane degree 2, line degrees 1 and 2 -- and the digest is **not**
`47249bbc…`, which the handover names as the acceptance value.  The two runs'
endpoint lists differ only by a relabelling of the cusps (`L1`/`L2` exchanged,
and the plane representatives are other planes of the same two cusps), which is
what a changed representative order does to an ordered digest.  A rewrite judged
against `47249bbc…` would therefore be failed by its instrument and not by its
mathematics; the value on this head is
`04c17f79b45ca82ac8fdb82e60dcf96f510b89d8c7c7d03748c27e67ff587dc2`, and the
invariant to judge is the relation, not the digest.

## The item that is actually open

`Otilde+`: killed twice, not by its own cost but by the host (`§11`, `§12` of
`issue381-the-plane-rows-per-plane-cost.md`).  It reached 180 000 of its 189 720
planes at 2 377.5 s and 3 579.7 MiB, and the killer fired with `MemAvailable` at
984 MiB while other tenants held the machine.  The record's own gate for
launching it is about 8 GiB of headroom against a 4.9 GiB claim; this VM had
5 160 MiB of `MemAvailable` at the time of this note, so the row was not
launched here and no count of `Otilde+` is reported.

## What is not claimed

Nothing here re-runs the row.  The 8.6 ms is the split's own rate on
`8c094f8`, and `_iter_splitting_isometries_in_im_rho_from_image`'s `point=None`
branch is byte-identical between `8c094f8` and `bb57ca7` (the only difference in
the function is the `right_orders` hoist in the `point=` branch), so the
per-lift body has not changed; whether the whole row's wall clock is unchanged
too is what a run on this head would say, and it is not run.

## What a window of the row is made of, measured on the row

A second probe prices every GAP call the domain module makes and stamps when each
first happens (`probe-gap-attrib.py`, row cap 420 s, `attrib2.log`).  The row is
`Otilde` at `T_Co` on `bb57ca7`:

| t | what | cost |
| ---: | --- | ---: |
| 0 → 107.1 s | the line row, the ambient plane orbit, the finite image | not GAP from this module |
| 107.1 s | `IsomorphismPermGroup(im rho)`, a group of size 46 998 591 897 600 with 349 generators | 1.02 s, once |
| 108.5 s | `FactorCosetAction(im rho_perm, right_perm)`, the subgroup of size 247 726 080 with 113 generators | **140.64 s, once** |
| 249.1 s | `Index`, `GeneratorsOfGroup`, `TrivialSubgroup` | 0.24 ms, 16 µs, 0.15 ms |
| 256.0 s | `ClosureGroup`, 11 calls; the generating subset and the coset walk | 0.03 s |
| 256.5 s | the split's first plane | -- |
| 423.9 s | **22 798 planes** | **7.35 ms a plane** |

Three things follow, and they close the question the last three rounds opened.

**The split's own rate is unchanged.** 7.35 ms a plane here against the returned
row's 8.6 ms on `8c094f8`: the per-plane half never regressed, and the two
instruments agree although one of them is the row running for real.

**The `FactorCosetAction` the walk's docstring says "does not return at the
Enriques size" does return** -- in 140.64 s, once per row.  What does not return
is doing it per plane, and the walk is the route that pays it once.  It is a
third of a 420 s window, and the row's cap is 10 800 s.

**The coset space is exactly the row's length.** 46 998 591 897 600 /
247 726 080 = **189 720**, so the walk's `degree` is the row's plane count and it
yields one lift per coset -- which is what the returned row registered
(189 721 planes, the extra one the source it seeds).

The window's arithmetic: `257 s` of setup + `189 720 × 7.35 ms = 1394 s` of
planes = `1651 s`, against the row's measured `2119 s` -- the relation's 569 160
records and the contract being the rest.  That is the whole of the "600 s" the
earlier rounds were reading as a deficit.

## A note on the two group orders the probe prints

`46 998 591 897 600` is `|O(A_{T_Co})|`, the card's `6JRR`; `247 726 080` is
`|rho(Stab_{O(T_Co)}(P))|`, the stabilizer image the record carries, and their
quotient is the index `189 720` the same record carries for the plane row.  The
probe did not compute the index from a count of planes: it read it from the two
groups, and it agrees.
