# Proposed issue: the known-family subgroup orbit call does not return (#294)

For the orchestrator to file. It is the blocking unit of the #294 batch: the card rows are
published and certified, and the *public call* that compares against them does not return.

## The missing result, observed

Producer `d462427`, held port `991b88b0`, harness `.scratch/sage-python-port` (binds the port
project at `/repos/sage-indefinite-port`; the image's bundled copy at the same path is a
different, stale revision and must not be used).

```python
u, e8 = Lattices(ZZ)("U"), Lattices(ZZ)("E8")
lattice = u + u + e8 + e8 + Lattices(ZZ)([[-2]])     # card 6JRX, Lambda_2, rank 21
lines = lattice.O_plus().isotropic_orbit_representatives(1)
```

* `lattice.Aut().isotropic_orbit_representatives(1)` — **returns**, `1` orbit, **115.06 s**
  (a valid run result; the card has no `O` line row, so it is not a card comparison).
* `lattice.O_plus().isotropic_orbit_representatives(1)` — **does not return**: killed at the
  900 s inner cap, peak tree RSS 3878 MiB (julia 3189 MiB). The card's row is
  `O+` → `constant: 1` (`6752696:lattices/6JRX.md`, §6 p. 94 with §1 p. 3), so this is the
  comparison #294 owes and it is unavailable.

`O_plus` is a predicate subgroup of the *same* object (`O_plus().supergroup() is
lattice.Aut()` is `True`) with `|O_plus : supergroup| = 2` and a 0.19 s construction. That
identity is stated as a fact about the objects; it is **not** offered as the cause of the
missing return, and no caching defect is claimed here.

## Where it is, from the run's own stack dumps

`faulthandler.dump_traceback_later(30, repeat=True)` in the producing process. The **last**
dump, i.e. where the process still was at 900 s:

```
predicate_subgroups.py:547            isotropic_orbit_representatives
orthogonal_quotients.py:1370          _subgroup_isotropic_orbit_representatives
lattice_morphisms.py:4088             isotropic_orbit_representatives
isotropic_orbits.py:955               _isotropic_orbit_representatives
marked_lattices.py:195                primitive_marking_classes
isotropic_induction.py:75/109         isotropic_vector_classes / _computed_...
recursive.py:1769                     primitive_vector_classes
eichler.py:995                        primitive_covering_vectors
eichler_criterion.py:353              covering_vector_representatives
eichler.py:805                        split_covering_vectors
eichler.py:514/555                    source_easy_generators / _computed_easy_generators
groups.py:5619                        group_generators
groups.py:1170 / objects.py:116       selected_resolution / realize
arrow_categories.py:2390              lambda: ... _core_automorphism_generators(self)
lattices.py:1850                      _core_automorphism_generators
lattice_morphisms.py:3795             _computed_group_generators
lattice_morphisms.py:3676             _engine_group
lattice_engines.py:1146               definite_isometry_group   (Julia bridge)
lorentzian_cells.py:4558/4698         _pinned_positive_eigen_directions / _source_integral_vector_allmeth_v2
```

So the wait is **not** `OrthogonalCharacterQuotient.splitting_isometries`; it is inside the
definite isometry group reached from the Eichler covering-vector route.

## The definite-lattice input, identified without running the enumeration

An aborting trace (patch `type(_oscar_lattices).definite_isometry_group` to print and
`SystemExit(0)` at its first call; no enumeration is run) gives the input and the owner call:

```
=== definite_isometry_group called
  gram shape: Type (0, 2) tensor in ((Integer Ring^8)*)^{⊗2}
  [[-2, 1, 0, 0, 0, 0, 0, 0],
   [ 1,-2, 1, 0, 0, 0, 0, 0],
   [ 0, 1,-2, 1, 0, 0, 0, 1],
   [ 0, 0, 1,-2, 1, 0, 0, 0],
   [ 0, 0, 0, 1,-2, 1, 0, 0],
   [ 0, 0, 0, 0, 1,-2, 1, 0],
   [ 0, 0, 0, 0, 0, 1,-2, 0],
   [ 0, 0, 1, 0, 0, 0, 0,-2]]
  <- groups.py:1170     generators = generating_set()
  <- arrow_categories.py:2390   lambda: ... _core_automorphism_generators(self)
  <- lattices.py:1850   return core_mor._computed_group_generators()
  <- lattice_morphisms.py:3795  generators = tuple(self._from_engine(...))
  <- lattice_morphisms.py:3676  order, generators = _oscar_lattices.definite_isometry_group(...)
```

That matrix is $-1\times$ the E8 Cartan matrix: rank 8, negative definite, determinant 1. So
the missing result reduces to: **the isometry group of $E_8(-1)$ is asked for through
`_oscar_lattices.definite_isometry_group`, and in this route it does not return.**

## Minimal public-call reproduction

```python
from sage_extensions.all import *
e8 = Lattices(ZZ)("E8")            # E8(-1): rank 8, negative definite, det 1
e8.orthogonal_group()              # asks the same adapter for the same Gram
```

to be run once with a bound; it is the smallest public call on the owner route above. The
full missing result is the `O_plus` line query in the first section, which is the one #294
needs.

Suggested title:

> `O_plus().isotropic_orbit_representatives(1)` does not return: the Eichler route asks for
> the isometry group of E8(−1) through the adapter and does not come back

Acceptance: on `Λ₂` from card `6JRX`, `O_plus().isotropic_orbit_representatives(1)` returns
inside a written budget and its cardinality is compared with the card's `O+` row, and the same
for `Otilde+` and for `Λ₄` (`6JRY`, `O` → planes 9, `O+` → constant 1 and planes 9).

## What is not claimed here

* No caching defect and no contention claim. The object identity and the two timings are
  facts; the reason the second route is slower is exactly what this issue asks to establish.
* The `O`-line count of 1 is a run result, not the card's `O+` row; one `O`-orbit is one
  `O+`-orbit only if some element outside `O+` lies in the orbit's stabilizer, and that is
  not assumed in signature (2,19).
* No T_Co result appears anywhere in this batch.

## Implementation design (owner: `orthogonal_quotients.py`, `_subgroup_isotropic_orbit_representatives`)

The seam is small, and this reading establishes it: `OrthogonalCharacterQuotient.splitting_isometries`
(`orthogonal_quotients.py:956`) uses the stabilizer **only through**
`self.image(generator)` for each generator, then does the double-coset computation in GAP. So
the operation only ever needs the finite subgroup `rho(Stab(x)) ≤ Q`; the integral stabilizer
is an implementation detail of how that image was obtained.

So the owner change is: compute `rho(Stab(x))` from the characters, then call the existing
double-coset machinery with that image (a new entry point that takes image keys rather than
generator images).

### The criterion, kept exact

For a finite-index `G ≤ O(L) =: G_0` and a point `x` of a `G_0`-set, with `Q = rho(G_0)`:

* `G` is transitive on `G_0.x` **iff** `G_0 = G·Stab_{G_0}(x)`;
* when `G = rho^{-1}(rho(G))` (the library's subgroups are exactly their character preimages),
  that is equivalent to `rho(Stab_{G_0}(x)) = Q`;
* otherwise the `G`-orbits inside `G_0.x` are the double cosets `rho(G) \\ Q / rho(Stab(x))`,
  which is what `splitting_isometries` already computes.

`Stab(x) ⊄ G` is **not** the criterion in general; it is the criterion only when
`[G_0 : G] = 2`, where the single nontrivial coset generates `Q ≅ Z/2`.

### The three characters, not one

1. **Discriminant factor, lines only, from the cited theorem.** Sterk 1991, Cor. 3.3 (p. 11),
   as research is stating it for `N = (H + H(2)) + P` with `P` even nondegenerate: primitive
   `v, w` of equal norm, equal divisibility `p`, and `v - w ∈ pN` lie in one
   discriminant-kernel orbit. Then a finite discriminant isometry fixing `c = [v/p]` lifts,
   and kernel transitivity corrects `g(v)` back to `v`, so the map from the integral line
   stabilizer onto the finite class stabilizer is **surjective**:
   `pi_1(rho(Stab(line))) = Stab_{O(A_L)}(c)`. The hypotheses are the theorem's, and they must
   be checked in code for the lattice at hand, not assumed: the decomposition of `N`, `P` even
   and nondegenerate, `v` primitive, and `div(v) = p`.
2. **Sign / spinor factor — separate, not implied by (1).** It is an index-two character and is
   decided by exhibiting an element of `Stab(x)` with the nontrivial value; a reflection in a
   vector `u ⊥ x` with `u·u = -2` has spinor class `[-2] ≠ 1`, so it witnesses the nontrivial
   value. A norm `-2` root reflection acts *trivially* on `A_L`, so it says nothing about (1)
   and must not be used there.
3. **Planes — separate, and not implied by the line lemma.** Nothing in Sterk's statement
   covers a rank-two isotropic subobject, so the plane rows keep the existing route until the
   corresponding statement is proved.

A witness that generates only part of `rho(Stab(x))` must not be promoted to the whole image;
the double-coset count would then be too large. The index-two case is safe precisely because
`Q ≅ Z/2` and one nontrivial value generates it.

### State

Not implemented, not tested, not pushed. Two things are missing and both are mathematical,
not cost: the hypothesis check for (1) on the cards' lattices (`Λ_k = U + U + E8(-1)^2 +
<-2k>` is *not* literally `(H + H(2)) + P`; whether it satisfies the theorem's hypotheses, or
which of its sublattices does, has to be established), and the correct image theorem for
planes. The index-two spinor branch alone is writable today and is *not* sufficient for the
`O+` plane rows.
