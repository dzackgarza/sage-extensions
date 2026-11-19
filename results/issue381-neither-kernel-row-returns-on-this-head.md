# Neither kernel row returns on this head: `Otilde` refuses too

The question left open by `issue381-the-divided-class-read-raises-at-tco.md` was
whether `Otilde`'s relation read refuses at its first record as `Otilde+`'s did.
Third attempt, on a host that stayed quiet (`oom_kill` 149 before and after),
driver caps, the `6144 MiB` guard:

```
[   1793.1 s rss   3220.6 MiB] the split: 180000 planes registered
[Otilde] error: the row step raised ArithmeticError: the line of the covering
  flag ... lies in 2 line cusps ...
[   1978.5 s rss   3496.2 MiB] done: 189721 planes, 0 records
```

**It refuses**, at a bucket of `2` where `Otilde+` refused at a bucket of `4` --
the two rows' coverings differ (their `K = Gamma cap Pi` differ) and land in
different fibres of the same key.

## The pair of runs, side by side

| | `Otilde` | `Otilde+` |
| --- | ---: | ---: |
| split | 189 721 planes, 1 793.1 s, 3 220.6 MiB | 189 721 planes, 1 723.9 s, 3 204.8 MiB |
| peak | 3 514 MiB | 3 556 MiB |
| relation | **0 records**, refused at `2 line cusps` | **1 record**, refused at `4 line cusps` |
| total | 1 978.5 s | 1 908.4 s |

Both refuse at their first record.  The split half is unchanged from the row
that returned on `8c094f8` (189 721 planes, 2 126.9 s, 3 622 MiB); the relation
half is not.

## So `#381`'s returned row is stale, and this is a regression

> **Attribution corrected.** The refusal is not `9ae39a1`'s: it predates the
> returning row (`b6d7bd8`, 17 Nov) and `9ae39a1` relocated the hunk.  The change
> that makes the row refuse is downstream of the read.  See
> `issue381-the-refusal-code-predates-the-return.md`.


`issue381-the-plane-rows-per-plane-cost.md` §10 records `Otilde(T_Co)` deciding
`569 160` edges over `527` and `189 720` cusps in 2 119.1 s -- **on `8c094f8`**.
The relation read that now refuses is newer than that run: `9ae39a1`, *the
divided-class relation decides its planes as they are reached, and a plane's lift
is spent by its edges*, is a descendant of the evidence commit `3a4a210` that
recorded the return.  On the current head the same row, the same caps and the
same lattice produce **no relation at all**.

That is a regression of the route with a clear owner and a clear witness, and it
is worth saying what kind it is: not a wrong answer but a lost one.  The row now
refuses an edge it used to decide, and it refuses it *correctly* given its key --
the key is equivocal on `24` of `444` classes at `T_Co`
(`issue381-the-divided-class-read-raises-at-tco.md`) and injective on every
lattice a test can afford (`issue381-the-key-is-exact-only-where-a-test-cannot-look.md`).

## What that means for the issue

`#381`'s kernel rows at `T_Co` are decided by no route in the tree on this head:

* the divided-class read refuses at the first ambiguous key, for both rows;
* the transporter route that would decide it is priced at `355 s` a question
  against `89 640` edge endpoints -- about `368 days` at the floor
  (`issue381-the-refusal-has-no-cheaper-route.md`);
* a finer invariant has no red test, because the four affordable specimens all
  have injective keys.

So the honest state is: **one regression, measured; no test that can hold it; one
design decision outstanding** -- carry the stabilizer's image so a fibre can be
separated, or restore a route that decides these edges, or accept the refusal as
this lattice's answer and report `#381` as blocked there rather than as decided.

No object is introduced: the key, the double cosets and the fibre are Dutour
Sikiri\'c--Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22, and every figure
above is a number a log in this tree carries.
