# The divided-class key is not reproducible across processes at `T_Co`

The theorem that makes the key an answer, and the computation that refutes its
implementation, in that order.

## The theorem

Let `G = O(L)`, `chi` a finite character with `Gamma = ker chi`, and let `v` be a
primitive isotropic vector with divided class `c = [v/div(v)]` in `A_L`.  An
element of `Gamma` acts trivially on `A_L`, and the divided class of a primitive
vector is carried by an isometry to the divided class of its image -- the
equivariance the tree states in `_isotropic_line_image_key`'s own docstring
(`orthogonal_quotients.py:4483`).  Hence **the class pair `{c, -c}` is constant
on a `Gamma`-orbit of lines**, and the map

    line cusp |-> its class pair

is a function of the cusp, not of the representative chosen.  The partition of
the cusps by class pair is therefore determined by the lattice and the subgroup.

## The computation

`Otilde` at `T_Co`, the same tree, the same subgroup, three processes:

| probe | line cusps | distinct keys | keys naming more than one cusp |
| --- | ---: | ---: | ---: |
| `line-cusps.log` (`cbbe353`) | 527 | **444** | **24**, largest 15, 12, 12, 11, 11, 9, 3, 2 |
| `fibre-index.log` (`c0a9d38`) | 527 | **351** | **104**, all of size 2 |
| `key-stability.log` (`c0a9d38`) | -- | -- | the walk itself raised |

The third process did not even get a partition: `cusps(1)` raised

    AssertionError: the orbit walk's transversal element does not carry the start
    to the reached point

in the `point=` branch of `_iter_splitting_isometries_in_im_rho_from_image`
(`:2313`).

An order-of-construction explanation is ruled out: building the character image
before the cusps and after them, in one process with the cusp cache cleared
between the runs, both answer 527 cusps (`order2.log`, 149.84 s and 68.51 s).

## What that means

The **count** is stable in every run -- 527 line cusps, the number the double
cosets give -- and the **partition by key is not**.  By the theorem above the
partition is determined, so one of two things is wrong in the implementation:

* the key is not computing the orbit invariant its docstring names, or
* the 527 objects the cusp row admits are not one representative per orbit, so
  the key is being asked of lines from a varying transversal.

Either way the acceptance cannot stand on this read: the refusal's *trigger* is
not a property of the lattice.  `Otilde` refused in one run at a bucket of 2 and
`Otilde+` at a bucket of 4, and the ambiguity count itself moves between 24 and
104 -- so a run that returns and a run that refuses may be differing in the walk,
not in the mathematics.

This supersedes the reading in
`issue381-the-divided-class-read-raises-at-tco.md` and
`issue381-the-refusal-has-no-cheaper-route.md` of the ambiguity as a fixed
`24 of 444` structure: that was one process's partition, and another process
partitions the same 527 cusps into 351 keys with 104 ambiguous.

## What is not claimed

The mechanism is not identified -- the theorem says the partition is determined,
the computation says it varies, and the gap between them is the next thing to
find.  Nothing here says which of the two sides above is at fault.

No object is introduced: the divided class and its equivariance are the
library's, the orbit--coset correspondence is Dutour Sikiric--Hulek,
arXiv:2302.01679v2, Lemma 3.6, printed p. 22, and every count is a log's.
