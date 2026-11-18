# The Otilde+ kernel row's covering: two word problems in the character product

`#286` stage 1 is met except the incidence of the `Otilde+` row of `T_Co`.  Two
dispatched runs of `.github/workflows/coble-kernel-incidence-rows.yml`
(`rows=Otilde+`, `route=divided-class`, cap 7200 s) were killed at their cap
inside `libgap.GroupHomomorphismByImages` at
`orthogonal_quotients.py:754 _character_permutation_model`, called from
`_plane_parabolic_incidence_flags`.  This note measures where that call
spends, repairs the two operations that cannot return, and names what the next
image run needs.

There is no run log or artifact in this session: `gh` in the VM is not
authenticated and the project's GitHub connection exposes no Actions endpoint
(the job-log endpoint answers 403, as `results/issue381-kernel-row-runner-kill.md`
already records).  What follows is measured independently, on the adopted
runtime, in the tree under test.

## 1. Construction against computation, `T_Co`, both kernel quotients

`Otilde = ker rho` has one character factor (the discriminant group);
`Otilde+ = ker(rho, sn_RR)` has two (the same discriminant group and a sign).
Probe `.scratch/w286-otilde-plus/.tmp/probe-model.py`, log
`.scratch/w286-probes/model-probe.log`:

| quantity | `Otilde` | `Otilde+` |
| --- | ---: | ---: |
| subgroup built | 0.139 s | 0.045 s |
| `finite_character_quotient()` (construction) | 0.001 s | 0.004 s |
| image labels | `('discriminant',)` | `('discriminant', 'spinor')` |
| character product order | 46 998 591 897 600 | 93 997 183 795 200 |
| product `IsPermGroup` | false | false |
| generators handed to the model | 4 | 5 |
| `_character_permutation_factors()` | 0.015 s | 0.000 s |
| permutation target order / moved points | 4.7e13 / 2046 | 9.4e13 / 2048 |
| `_character_permutation_model()` | **0.067 s** | **no return in 90 s** |

So the construction is free and the model is what does not return -- but only
once the quotient has a second factor.  Two probes separate the cause.

*(a) The constructor.*  The same generators and images handed to
`GroupHomomorphismByImagesNC` return in **0.000 s** at order 9.4e13
(`model-probe3.log`).  What the verified constructor adds is a check of the
image family against the source's stabilizer chain, and the source is a GAP
*direct product* whose factor is a 4.7e13 matrix group: GAP can build a chain
for the factor, but not for the product.

*(b) The elementwise images, which NC does not repair.*

| operation at order 9.4e13 | wall |
| --- | ---: |
| `GeneratorsOfGroup(product)` | 0.000 s |
| `Image(projection_i, generator)` (all 5, both factors) | 0.000 s |
| `Image(factor model, component)` (all 10) | 0.004 s max |
| the whole image family of the model | 0.016 s |
| `Image(NC model, a product generator)` | 0.000 s |
| `Image(NC model, an arbitrary element of the product)` | **no return in 60 s** |
| `quotient._permutation_of_key(key)` (the factorwise route) | 0.003 s |

`Image` of an element of the product sifts it through the source's chain, so
it is the word problem the factorwise model exists to avoid; and
`Image(model, a subgroup)` sifts the subgroup's generators, which is the same
wall once per generator.  No choice of constructor removes this: the repair
has to stop sending elements of the product to the model.

## 2. What the row's own call costs

`_plane_parabolic_incidence_flags` at the base plane of `T_Co`, one covering,
the certified parabolic family built first (112 generators, 5.0 s)
(`model-probe4.log`, then `.tmp/probe-fixed.py` / `fixed-covering.log`):

| tree | `Otilde` | `Otilde+` |
| --- | ---: | ---: |
| parent `df8b249` | 12.9 s before the change (8.2 s, #585) | **no return in 60 s** |
| repaired | 12.9 s, 3 flags, 3 distinct line class pairs | **20.6 s, 3 flags, 3 distinct line class pairs** |

Three is the degree the row's own contract asserts on every plane cusp of both
kernel rows (`527 * 1080 = 189720 * 3 = 569160` edges), so the covering is the
size the incidence walk expects, and `Otilde`'s own covering is unchanged.

## 3. The repair

At both owners, with the proof in the source:

* `_character_permutation_model` uses `GroupHomomorphismByImagesNC`.  The image
  family is a composite of the factor projections, the factors'
  `IsomorphismPermGroup` isomorphisms and the embeddings of those images into
  the permutation product; a product of homomorphisms into pairwise-commuting
  subgroups is a homomorphism, and each factor model is injective, so it is a
  faithful homomorphism and needs no check.
* `_permutation_character_target` builds the condition subgroup factor by
  factor (the discriminant-preimage targets' images under the discriminant
  factor's own model, met in the permutation target).
* `adjust_witness_into_subgroup` takes the permutation target from
  `_character_permutation_factors` rather than from the model's range.
* `_plane_parabolic_incidence_flags` builds the parabolic's image, the meet
  with the condition subgroup and the right group inside the permutation
  target, from the certified family's own character keys, and checks each
  double-coset representative's word-section lift the same way.  The
  subgroup's index in `O(L)` is no longer asked on this path: the meet answers
  `chi(Pi)` at index one without it, and that index is a quotient of two
  orders of 4.7e13 (68 s, the only gap of `model-probe3.log` before the
  constructor).

The `test:` commit before the fix asks the repaired operation's question on
`T_Co` -- whether the finite image adjusts a witness that has no stabilizer to
adjust by -- and is killed at a 200 s wall on its parent tree
(`red-on-parent.log`) and passes in 8.58 s after the repair
(`green-286-rebased.log`, gate 20 s).

## 4. What the next image run needs

The covering was the row's first wall and is now ~21 s once per row.  The
remaining costs are the ones #390 and #584 measure, and the dispatch is:

| input | value | why |
| --- | --- | --- |
| `rows` | `Otilde,Otilde+` | the two kernel rows; the matrix gives each its own job and memory |
| `lattice` | `Tco` | the object of #286 |
| `route` | `divided-class` | the route the two killed runs took |
| `cap` | `14400` | the walk is 53-66 ms a plane (#585), i.e. 10 000-12 500 s over 189 720 planes; the 10 800 s default sits inside that range |
| `budget` | `28800` (default) | one row per job |
| commit | `12b57de` | this repair |

The runner needs the 16 GiB the hosted job has: the plane row's own retention
was 3494 MiB at 180 000 planes on the release tree (`6b8f7d2`) and the
relation adds ~0.4 GiB.  What the run must not be asked for is a row that
still asks an element of the character product for its image; nothing in the
covering or the walk now does.

## 5. Open, and not repaired here

* `Image` of an arbitrary element of the character product still costs the word
  problem, so `_character_permutation_model` is a name for the shared target
  group and not an elementwise map.  The docstring says so; no caller on a row
  uses it that way any more.
* `quotient.index()` costs ~68 s at its first call on `Otilde+` (a quotient of
  two orders of 4.7e13).  The covering no longer asks it; `PredicateSubgroups.index`
  still does.
* The divided-class walk's 53-66 ms a plane is the dual-action inversion #585
  names: two thirds of the row's 10 000 s.  It is the next repair, not this one.
* `test_adjust_witness_into_subgroup_matches_elementwise_search` fails on its
  own `StopIteration` setup at the parent tree as well; it is not this change's.
