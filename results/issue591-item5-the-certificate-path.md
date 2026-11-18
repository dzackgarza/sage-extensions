# #591 item 5 — why the `generator_morphisms` run grew, and what the row costs now

The record this item is read against (`lattice-database` `exceeded.yaml`, the
`6JRR` entry):

```
6JRR arithmetic-group.otilde-t-co.generator_morphisms:
  hash: 835e87dc1e3a87479bc8a0df960b89c8b784d51c402ba78e88834ad5beb3b7e3
  seconds: 4782
  lost: true
  killed_by: memory
  peak_bytes: 14382555136
  limit_bytes: 1675943526
```

All measurements below are on this tree, in the pinned runtime
(`~/sage-image/rootfs`, Sage 11.0.beta5, `/sage/.venv/bin/python`), one request
at a time.

## 1. The split: construction is cheap, the computation is the whole finite image

`Lattices.stable_orthogonal_group()` is the preimage of the trivial subgroup of
`O(A_L)` under `rho_L`. Splitting its cost at the two owners:

| step | owner | measured on `T_Co` |
| --- | --- | --- |
| the lattice, its Gram, `_presents_the_coble_form` | `Lattices` | 0.04 s, +0 MiB |
| `stable_orthogonal_group()` (construction) | `PreimageSubgroups.__init__` | 0.16 s, +11 MiB |
| the certified family (56 isometries) | `Coble.kernel_generators` | 0.27 s, +16 MiB |
| `group_generators()` on the installed resolution | `PreimageSubgroups` | 0.38 s, +3 MiB, peak 288 MiB |

so the path the database certifies against costs **0.4 s and 288 MiB** end to
end, and the construction is not where anything grows.

The route the record took is the one `PreimageSubgroups.__init__` installs when
the codomain is finite: the Schreier family of `G -> G/f^-1(K)`, which has one
member per coset `f(G)K/K`. On `T_Co` the target is trivial, so that is one
member per element of `O(A_L)` — `46998591897600` of them. The **construction**
of the coset space is not the cost: `_TransversalCosets(O(A_L), 1)` builds in
0.08 s, since GAP's transversal is not materialized. The **computation** is a
breadth-first sweep over the finite image, and its memory is set by what it
retains per coset.

## 2. The smallest lattice that shows it

`U(2) + <-2>^r` has `A_L = (Z/2)^{r+2}` and takes the same route; the finite
image's order is the only thing that changes:

| `r` | rank | `|O(A_L)|` | letters in the free cover | `coset_space()` |
| --- | --- | --- | --- | --- |
| 4 | 6 | 1920 | 15 | 24.2 s, +90 MiB |
| 5 | 7 | 51840 | 15 | 265 s, still running, +451 MiB and rising |

`r = 4` is the smallest rung that shows the growth in a bounded run: 12.6 ms
and ~47 kB per coset. Object counts after that sweep: 28 816 elements of the
finite image, 28 801 GAP permutations and 28 825 `fqf` elements retained for
1 920 points — 15 per point, one per letter, in `_TransversalCosets`'s cache
keyed by the element's identity.

At that constant the record is arithmetic, not tuning: `4.7*10^13` cosets at
52 kB is `2.4*10^18` bytes, and the 14 382 555 136 bytes the run held before it
was killed are about `2.8*10^5` cosets — `6*10^-9` of the image. No per-coset
constant brings that route under the 1 675 943 526-byte floor; it needs a
factor of `10^12`.

## 3. The repair, at the owner of the retention

`_TransversalCosets._multiplier` was a `cached_method` keyed by
`(id(element), element)`. A sweep asks about a fresh product `s * t_p` at every
letter of every point, so the cache held one element of the finite image and its
engine permutation per letter of the orbit, beside the orbit's own points.

It is now read per request; the conversion is one engine call and the element is
asked about once. Measured on the smallest lattice that shows the growth:

```
r = 4 coset_space():   before 24.2 s, +90 MiB       after 7.8 s, +5 MiB
r = 5 at 240 s        before +407 MiB (at 250 s)    after +184 MiB
r = 5 to its cap      after: 520 s, peak 1 473 MiB, no family yet
```

So the repair lowers the retention; it does not make that rung's sweep finish, and
it does not change the verdict on `T_Co` — the route is avoided by the certified
family, not tuned.

No library answer changes, so this repair has no red test of its own; the red
that item 5 has is the certificate's dispatch, below.

## 4. The certificate path, on the database's own worker

`latticedb.sage_genus`, one request, the card's own `gram_tensor` and the
card's own field:

```
{"tag": "6JRR", "gram": <6JRR's gram_tensor>, "integral": true,
 "fields": ["arithmetic-group.otilde-t-co.generator_morphisms"],
 "arithmetic_groups": [{"slug": "otilde-t-co", "standard_name": "Otilde"}]}

worker exit 0 after 2.6 s
value: 56 matrices, first row [-15, 4, 4, 16, 0, -16, 8, -8, 8, 0, 0]
peak tree RSS 401 MiB (worker VmHWM 293 MiB), against the 1675943526-byte floor
```

The card's Gram matrix is the catalogue's entry for entry, so the certified
family is selected for the lattice the certifier builds, not only for the
catalogue object.

The red is
`tests/lattices/test_the_coble_lattice_certified_generators.sage` at `8be68e2`
(whose parent is `62743b1`): **2 failed, 2 passed in 14.96 s** — the lattice
built from the source's Gram tensor raises the rank-ten refusal at
`lattices.py:4594`. On this tree the same file is 4 passed, and the seven files
that consume the coset arithmetic are 31 passed in 22.5 s;
`tests/groups/test_transversal_positions_beyond_machine_int.sage` is stopped at
collection by its own lint on both trees, which is pre-existing.

## 5. The image run inputs for the full row

`certify.yml` in `dzackgarza/lattice-database`, dispatched with
`tags: 6JRR` (one job, one card):

* image `ghcr.io/dzackgarza/sage:develop`, provisioned by
  `.github/actions/sage`, which installs `research` and then
  `research/pyproject.toml`, whose requirement is
  `sage-extensions @ git+https://github.com/dzackgarza/sage-extensions` — the
  library is main at the run, so the run must follow this push;
* database revision: the `certify.yml` checkout of `main`;
* research revision: `$(git -C research rev-parse HEAD)` at the run;
* the request: tag `6JRR`, its `gram_tensor`, `integral: true`, fields
  `arithmetic-group.otilde-t-co.generator_morphisms` with the arithmetic group
  `{slug: otilde-t-co, standard_name: Otilde}`;
* the budget: the run's own floor, `limit_bytes: 1675943526`, on the
  `--workers 1 --phase fields` job.

The record releases with `just retry-computation` on that entry once the run has
certified the value, as the database's README describes; a changed Gram tensor
changes the input hash and the entry no longer applies.
