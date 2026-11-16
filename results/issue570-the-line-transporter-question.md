# The transporter question at a line cusp, and what the parabolic family's size is

## The question

`Otilde(T_Co)` line cusps: 527 representatives, each named by the divided class
`2[h] + [a3] - [a4] + 2[a8]` of a plane's own line at the one cusp the finite image
does not separate from it.  The question is `cusp.transporter_witness(line)`, the one
#381's incidence asks at every plane.

## Stage split at the named cusp, with the rows built

One cold process per column, adopted runtime (Sage 11.0.beta5), port `991b88b0`, the
Otilde line row (527 representatives, 184.89 s) built first so the caches the incidence
has are warm.

| stage | parent `acd1c18` (`.tmp/p570r2_before.log`) | this tree (`.tmp/p570r2_witness.log`) |
| --- | ---: | ---: |
| the line row, 527 representatives | 242.74 s | 184.89 s |
| the question, first ask | 36.65 s | 37.75 s |
| the question, asked again | 33.97 s, 35.10 s | **5.65 s, 5.65 s** |

The first ask on this tree pays the one ambient witness between the two rows' roots
and the cusp's first stabilizer family; a second object compared against the same
cusp pays neither.

The parts of a question, measured one stage at a time in a process that replayed the
cusp's recorded coordinates instead of building the row (`27.40 s` and `27.10 s` warm
there): `invariant_separates_isotropic_orbits` 47.60 s on its first call
and 0.01 s per cusp after (the `O(A_L)` chain, cached per quotient); the port's ambient
isometry search 15.39 s; `exact_isotropic_stabilizer_generators` 13.58 s, of which the
parabolic family is 8.23 s (and 7.69 s is the `Subgroup` of its 91 images);
`adjust_witness_into_subgroup` 5.50 s.

## What was repaired

* A row that transports an object by a known isometry retains that isometry
  (`register_isotropic_transport`, keyed by the transported span), so an isometry
  between two transported objects is the composite `g_right * b * ~g_left` of their
  words.  When the two chains have different roots, one ambient witness between the
  roots is computed and kept -- the roots are the rows' own representatives, so that
  search is per row, not per object.
* The exact stabilizer generators of a cusp's representative are retained per span
  (`exact_isotropic_stabilizer_family`): the family is a function of the span, and a
  row asks for the same cusp's stabilizer once per object compared against it.

The 5.65 s that remain are `adjust_witness_into_subgroup` -- the trivial-condition case
repaired in round 1, whose cost is the stabilizer image's own membership test and word
section at `|W| = 89181388800`.

## The parabolic family's size is not one number

`isotropic_stabilizer_generators` at the same line, one cold process each:

| probe | family | `O(K)` family | rational group | integral stabilizer |
| --- | ---: | ---: | ---: | ---: |
| `.tmp/p570r2_stages.log`, three calls in one process | 91, 91, 91 | 94, 94, 94 | -- | -- |
| `.tmp/p570r2_chain-1.log` (seed 1) | -- | **60** | 42 | 84 |
| `.tmp/p570r2_chain-777.log` (seed 777) | -- | **94** | 52 | 104 |
| `.tmp/p570r2_family-1.log` (seed 1) | 91 | 94 | 52 | 104 |
| `.tmp/p570r2_family-777.log` (seed 777) | 87 | 93 | 49 | 98 |
| `.tmp/p570r2_trace-1.log` (seed 1) | 91 | 93 | -- | -- |
| `.tmp/p570r2_trace-777.log` (seed 777) | 84 | 93 | -- | -- |

Round 1 measured 88, 92, 93 and 96 for the same line.  Every stage after `O(K)`
inherits the count, so the family a caller receives is not determined by the
mathematics.

The stages above `O(K)` are one datum: `K = u^perp/u` has the same Gram in every
run (`.tmp/p570r2_gram-1.log`, `.tmp/p570r2_gram-777.log`), the reduction of `K` is
the same diagonal form `diag(-2,-2,-2,-2,2,-2,-2,-2,-2)` with its isometry in both,
and the perfect complex on it reports the same three cells of 17, 9 and 129 rows,
cell stabilizer counts 36, 28, 23, five adjacencies, and 93 generators in both seeds
(`.tmp/p570r2_cells3-1.log`, `.tmp/p570r2_cells3-777.log`).

So the varying stage is `EichlerRecursion.orthogonal_group_generators(K)` itself: it
returns 60, 93 or 94 elements for one lattice in different processes, where the
perfect complex on its reduced form returns 93 in every run.  That function is the
paused port's (`sage_indefinite_port.indefinite.recursive`, through
`lorentzian_orthogonal_group_generators` and the groupoid cache), and
`sage_extensions.categories.isotropic_orbits._isotropic_stabilizer_generators`
delegates to it, so the repair at this repository's owner is the induction
implemented in-repo -- not done in this round, and not guessed at.
