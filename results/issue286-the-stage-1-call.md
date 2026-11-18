# #286 stage 1: one call on `T_Co`, and the known-answer comparisons

**Result.** On `T_Co` the call returns, under `O(T_Co)`, one primitive isotropic
line orbit, one primitive isotropic plane orbit and one incidence edge; under
`Õ(T_Co) = ker ρ` and under `Õ⁺(T_Co) = ker(ρ, sn_RR)` it returns 527 line
orbits each, the number of nonzero isotropic classes of `A_{T_Co}`, so the index
`[Stab_{O(q)}(v̄) : ρ(Stab_Γ(v))]` is 1 over every class.  The page-proof rows it
can be compared with agree.  The kernel *plane* rows — 189 720 orbits each — do
not finish on this host (§ "The kernel plane rows"); `#588`'s span row is
2.0 GiB and 1 179 s on a runner of its own.

Measured in the adopted runtime (Sage 11.0.beta5 / Python 3.14, image
`ghcr.io/dzackgarza/sage@sha256:59568577…`) on `main`
`3998bd87a5945db69e03da7dec5f915c6f5f094c`, with `sage-indefinite-port` bound at
`991b88b095a42a1e3679569ea42328c900c120f6` (`sage_indefinite_port.__file__ =
/port/src/sage_indefinite_port/__init__.py`).  Other chats' probes ran on the
same 4-CPU VM throughout (a 4.8 GiB `probe-row.py` among them); the wall times
are the rows' costs under that machine and not an idle-host plateau.

The call is `PredicateSubgroups.ParentMethods.isotropic_orbit_representatives`
(`group/predicate_subgroups.py:602`) → `_subgroup_isotropic_orbit_representatives`
(`orthogonal_quotients.py:4413`) → `_yield_subgroup_isotropic_orbit_representatives`
(`:4318`), with `cusps` (`:772`) and `tits_building_incidence` (`:810`) the same
row read as spans and as a line/plane relation.  The line splitting is the
character quotient's `isotropic_line_stabilizer_image` →
`splitting_isometries_from_line_class` (`orthogonal_quotients.py:1573`, `:1716`),
whose family runs over the line's finite class (Dutour Sikirić–Hulek,
arXiv:2302.01679v2, Lemma 3.6, printed p. 22) and whose cardinality is the index
`[Stab_{O(q)}(v̄) : ρ(Stab_Γ(v))]`.  No file under `src/` was changed.

## Item 1 — `T_Co` from the citation, and the source's own page

`T_Co = ⟨2⟩ ⊕ E(2)`, `E = E₈ ⊕ U`, `E₈` negative definite: D. Dolgachev and
S. Kondō, *Enriques surfaces and Borel–Weil–Bott type duality*, Izv. Math. 77:3
(2013), §3 eq. (3.6), printed p. 513.  The printed page (`izv13.pdf`, p. 5 of the
16-page file) states:

* `N = ⟨2⟩ ⊕ E(2) (3.6)`, of signature `(2, 9)` and `q_{N_X} = −q_M`, `A_M ≅ (Z/2)^11`;
* `Proposition 3.2. Let N = ⟨2⟩ ⊕ E(2). Then the moduli space M_Co …`;
* `Note that N = ⟨2⟩ ⊕ E(2) is isomorphic to the orthogonal complement of a
  (−2)-vector in U ⊕ E(2)` — the `δ` of item 2.

`E₈` is the negative definite one and the source's own signature gives it: `<2>`
carries the one positive square, and `E(2)` has signature `(1, 9)` only when `E`
is `U ⊕ E₈(−1)`.

Built from that formula and compared entry for entry with the catalogue's
`NamedLattices.Tco`:

```
ranks 11 11
gram mismatches 0 []
sig (2, 9) det -2048 even True
```

The catalogue's docstring already carries the same citation and the same sign
argument (`catalogue.py:204`), so the two agree and the citation stands.  The
test that builds the formula: `tests/lattices/test_the_coble_lattice_from_the_cited_formula.sage`,
**3 passed in 68.34 s** (entry-for-entry comparison 0.17 s; signature and
determinant 0.32 s; the 528 isotropic classes with 527 nonzero, 65.43 s).

## Item 2 — the group rows, built by their constructions

`δ = e − f` in the `U` summand of `T_En = U ⊕ U(2) ⊕ E₈(−2)`, and:

```
q(delta) -2
perp rank 11 det -2048 sig (2, 9) isometric to Tco: True wall=0.2s
```

| row | construction |
| --- | --- |
| `O(T_Co)` | `Tco.Aut()` |
| `Õ(T_Co) = ker ρ` | `Tco.stable_orthogonal_group()` |
| `Õ⁺(T_Co) = ker(ρ, sn_RR)` | `Tco.stable_orthogonal_group()` ∩ `Tco.O_plus()` |
| `R_Γ` | the image in `O(δ^⊥)` of `Stab_Γ(δ)`, by restricting the stabilizer's own generators (`lattices.py:12195`, `perpendicular_restriction`) |

The two `R_Γ` whose `Γ` is named directly, `Γ^K_En = O(T_En)` and
`Γ_En = Õ⁺(T_En)`, are
`tests/lattices/test_the_restricted_stabilizer_rows_on_tco.sage`, and their
computed indices in `O(T_Co)` are **1** and **93997183795200 = 2·|O(q)|**.
That test on this tree: **1 passed in 199.02 s**.  The stage costs of the same
construction are in `results/issue359-tco-restricted-stabilizers.md` (measured at
`7d785fc`, port `991b88b0`: 330 / 331 generators of `Stab_{O(T_En)}(δ)` in
352.3 s / 287.1 s, restriction 40.6 s, `|ρ(O(δ^⊥))| = 46998591897600`).  `R_{Γ_{En,2}} = Γ_{Co,2}`
is the discriminant preimage of the point stabilizer `P`
(`tests/lattices/test_the_coble_gamma_co_2_line_row_returns_generators.sage`).

`prop:gamma-co-images` (page proof) states `R_{Γ^K_En} = O(T_Co)` — index 1 — and
the computed index is 1, so the page's statement holds for the built group.  Its
other row, `R_{Γ_En} = Õ⁺(T_Co)`, has index `93997183795200`, also the page's.
No defect is filed.

## Item 3 — the call on `T_Co`, `O(T_Co)`

| call | value | wall |
| --- | --- | ---: |
| `Tco.Aut().isotropic_orbit_representatives(1)` | **1 orbit** | 213.0 s |
| `Tco.Aut().isotropic_orbit_representatives(2)` | **1 orbit**, a rank-2 primitive isotropic plane | 4.4 s |

Both page-proof-only rows this call reaches — `O(T_Co)` transitive on primitive
isotropic vectors (`thm:unpolarized-cusps` via `prop:tco-split-maximal`) and one
`O(B)`-orbit of planes with `K_P ≅ I_{0,7}` — agree with the computed values.
One ambient orbit over the 527 nonzero isotropic classes of `A_{T_Co}` is index
1 over every class.

### The incidence at `O(T_Co)`

`tests/coble_gamma_co_2_incidence_rows.py --rows O --lattice Tco`, the package's
own row runner:

```
[O] the row's calls returned in 170.6 s
[O] line cusp 0: ((0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0),)
[O] plane cusp 0: ((2, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2), (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0))
[O] edge 0: L0 < P0
[O] audited 1 distinct edges; ordered endpoint SHA-256: 99a357b646bc6d0d81ac188c8bfffcbf6ab8f8f72a5d262fe81624f6f9a9a66c
[O] decided: 1 edges over 1 line cusps and 1 plane cusps
```

One edge over one line cusp and one plane cusp, and the audit of that edge
runs.  Two repairs to the runner are what let it print: the summary's datums
line asked the ambient group for a character quotient it does not have, and the
edge audit asked the certificate for a reconstructed flag it does not have
(`CuspIncidence` holds the flag it was built with; `ArithmeticCuspIncidence` is
the one that rebuilds it).  Both are `fix:` commits on this turn.

## Item 4 — the known-answer comparisons, before the `T_Co` numbers

Card values are read by tag from `tests/cards/lattice-database-enriques.json`
(`card_line_orbit_row`, `card_plane_orbit_row`), never typed.

| lattice, group | call | computed | card | wall |
| --- | --- | ---: | ---: | ---: |
| `029J` (`T_En`), `O` | `L.Aut().isotropic_orbit_representatives(1)` | **2** | 2 | 10.3 s |
| `029J`, `O` | `L.Aut().isotropic_orbit_representatives(2)` | **2** | 2 | 0.0 s |
| `029J`, `Õ⁺` (`otilde-plus-t-en`) | `ker(ρ,sn).isotropic_orbit_representatives(1)` | **528** | 528 | 176.7 s |
| `029J`, `Γ_{En,2}` | `Γ_{En,2}.isotropic_orbit_representatives(1)` | **5** | 5 | 53.8 s |
| `029J`, `Γ_{En,2}` | `Γ_{En,2}.isotropic_plane_orbits(P₁,P₂)` | **9** | 9 | 47.3 s |
| `029J`, `Õ⁺` | `Õ⁺.isotropic_plane_orbits(P₁,P₂)` | **24242** | 24242 | 11.6 s |
| `6JRX`, `O` | `Λ₂.Aut().isotropic_orbit_representatives(2)` | **4** | 4 | 101.0 s |
| `6JRX`, `O⁺` | `Λ₂.Aut() ∩ O⁺`, rank 2 | **4** | 4 | 16.0 s |
| `6JRY`, `O` | `Λ₄.Aut().isotropic_orbit_representatives(2)` | **9** | 9 | 43.4 s |
| `6JRY`, `O⁺` | `Λ₄.Aut() ∩ O⁺`, rank 2 | **9** | 9 | 39.5 s |

Every computed value is the card's; no mismatch to file.  The T_En rows the
issue calls `otilde-plus-t-en` are read off card `029J`, whose `Otilde+` row
states them: the digest's `arithmetic_groups` holds 87 cards, all `gamma-h-*`,
and carries no `otilde-plus-t-en` entry, so that tag's row is `029J`'s field and
its citation, which is what the readers above return.

The two `029J` plane rows are compared through `isotropic_plane_orbits` — the
same subgroup's divided-class plane row — and not through
`isotropic_orbit_representatives(2)`: on `T_En` the ambient plane classification
the latter starts from is the stage that spends over 50 minutes before the
subgroup is reached (#286, comment of 2026-11-17), while the divided-class row
answers the same orbit set from Sterk's two integral representatives
(Proposition 4.6, p. 29).  The `029J` `O` plane row is the named-lattice branch
of `_isotropic_plane_orbit_representatives` (`isotropic_orbits.py:1739-1748`),
which returns Sterk's two planes directly.  The line rows above are the public
call itself.

## Item 5 — the `T_Co` kernel rows: the line rows return, the plane rows do not

| page row (evidence) | call | computed |
| --- | --- | --- |
| `Õ(T_Co)`, 527 line orbits, index 1 over every class (page proof, `sec-cusp-lifting`) | `Tco.stable_orthogonal_group().isotropic_orbit_representatives(1)` | **527 orbits**, 172.2 s; representatives `e_ep` and `2e_h + e_a1 + e_a2 + 2e_a3 + 2e_a4 + e_a5 + e_a8` |
| `Õ⁺(T_Co)`, 527 line orbits, index 1 over every class (same) | `…intersection(Tco.O_plus()).isotropic_orbit_representatives(1)` | **527 orbits**, 122.7 s |
| `K_P ≅ I_{0,7}`, one `O(B)`-orbit of planes (page proof) | `Tco.Aut().isotropic_orbit_representatives(2)` | **1 orbit** (item 3) |
| plane orbit sizes 1575, 270, 9450, 3780, 8640 (neither record nor proof) | — | not asserted, not a value |

### What does not return, with the owner

**The kernel plane rows.**  `Õ(T_Co)`'s and `Õ⁺(T_Co)`'s
`isotropic_orbit_representatives(2)` are the rows of 189 720 planes.  The split
they walk now streams: `_plane_orbit_from_parabolic_stabilizer`
(`orthogonal_quotients.py:3952`) hands the row to `_iter_transported_planes`
(`:4035`), which yields one transported plane per double coset and retains only
the lift registry's entry (`ec2529e`), so the row no longer builds its 13.47 GiB
of planes before the first cusp —
`results/issue381-the-kernel-plane-row-does-not-stream.md` measured that gather
at 74.4 KB a plane and 6 162 MiB at 783 s, and it is repaired on this tree.  What
remains is the walk's own cost: one discriminant-image coset word per plane,
8.97 h a row at the rates `results/issue381-plane-row-route.md` measured, which
is #390's BFS repair and not this call's structure.  Probed this turn:
`itertools.islice(row, 3)` on `Õ(T_Co)`'s plane row yielded **no plane in 400 s**
and was killed at its cap, which is the walk's shape — one coset word before the
first plane — and not a refusal.  Not run to completion this turn.

## Item 6 — the `O(T_Co)` generators

`NamedLattices.Tco.Aut().group_generators()` — `lattices.py:2801` →
`_core_automorphism_generators` → the port's `automorphism_group_generators` —
at port revision **`991b88b095a42a1e3679569ea42328c900c120f6`**:

```
[O(T_Co) group_generators] 359 wall=27.0s
```

It returns; the `4f0ee50c` crash does not reproduce at `991b88b0`.  The count is
the run's: the port's generator search is not deterministic (330, 331, 335, 343,
348 and now 359 and 326 observed across runs).

## Files

* `tests/coble_gamma_co_2_incidence_rows.py` — two repairs to the row runner:
  the datums line of the summary prints where the subgroup has a character
  quotient (`ca84280`), and the edge audit asks a certificate for its
  reconstructed flag only where it has one, `ArithmeticCuspIncidence` and not
  the ambient group's `CuspIncidence` (`e14f425`).  On `3998bd8` the second
  raised after the row had returned in 99.1 s: `AttributeError: 'CuspIncidence'
  object has no attribute 'release_flag'`.
* `tests/lattices/test_the_coble_lattice_otilde_and_otilde_plus_line_rows.sage`
  — each kernel line row's count is asserted equal to the number of nonzero
  isotropic classes of `A_{T_Co}` counted in the file, which is the index-1
  statement; no page number is typed.
* `results/issue286-the-stage-1-call.md` — this record.

## Summary of the run

| # | item | outcome |
| --- | --- | --- |
| 1 | `T_Co` from DK13 (3.6), p. 513 | built, agrees with the catalogue entry for entry, 3 tests pass |
| 2 | the group rows by their constructions, `R_{Γ^K_En} = O(T_Co)` | indices `1` and `2·|O(q)|`, the page's |
| 3 | the call on `T_Co` under `O(T_Co)`, with incidence | 1 line orbit, 1 plane orbit, 1 edge |
| 4 | the known-answer comparisons | all ten rows are the cards' |
| 5 | the kernel rows on `T_Co` | line rows **527** each; the plane rows **189 720 cusps** each (36.2 min at 3 476 MiB and 30.2 min at 3 554 MiB) |
| 6 | `O(T_Co)` generators | return, 359 in 27.0 s, port `991b88b0` |

### The index over each finite class

The splitting family of a line is
`quotient.splitting_isometries_from_line_class(*line_image)`
(`orthogonal_quotients.py:1716`), one element per double coset of the finite
class stabilizer, so its cardinality is
`[Stab_{O(q)}(v̄) : ρ(Stab_Γ(v))]`.  On `T_Co` the two kernel rows return 527
orbits, the number of nonzero isotropic classes of `A_{T_Co}` (computed as 528
isotropic classes, 527 of them nonzero, in item 1), and each index is a positive
integer whose sum over the classes is that count: every index is 1, which is the
page's "index 1 over every class".  The ambient row is one orbit over the same
527 classes, so its index is 1 as well.

## Reproducing a row

Inside the adopted image, with the port bound ahead of the image's own copy:

```
~/sage-image/run.sh -w /work -b <tree>:/work -b <port>:/port -- /bin/sh -c \
  'cd /work && PYTHONPATH=/port/src:/work/src:/work \
   /sage/.venv/bin/python -u -c "<the call above>"'
```

`T_Co`'s rows and the two incidence repairs are also reachable through
`tests/coble_gamma_co_2_incidence_rows.py --rows O --lattice Tco`, and the
kernel line rows through
`tests/lattices/test_the_coble_lattice_otilde_and_otilde_plus_line_rows.sage`.

## The kernel plane rows, measured on `7753092`

The two kernel plane rows are 189 720 planes each, and they were the last item
open on this call.  Two instruments exist for them and they are not the same
row: `subgroup.cusps(2)` keeps a **span** per cusp and builds the plane only when
a reader asks for `representative()`, and
`subgroup.isotropic_orbit_representatives(2)` keeps every constructed plane.
`#588`'s retention repair (`#592`, `#593`) is stated on the first: the span row
falls from 12.29 GiB to 2.0 GiB at that length.

The `Õ(T_Co)` row, on the cusp instrument and alone on the host, **returns**:

```
[Otilde cusps] built in 2171.0 s, peak 3476.4 MiB
[Otilde cusps] counted 189720 cusps in 0.0 s, peak 3476.4 MiB
[Otilde cusps] a cusp's representative: rank 2, primitive True
```

The same row for `Õ⁺(T_Co) = ker(ρ, sn_RR)` first ran beside another chat's row
and was killed at 3 330 MiB, exit 137, 2 124 s in; run alone on the host it
returned:

```
[Otilde+ cusps] built in 1812.8 s, peak 3554.3 MiB
[Otilde+ cusps] counted 189720 cusps in 0.0 s, peak 3554.3 MiB
[Otilde+ cusps] a cusp's representative: rank 2, primitive True
```

189 720 cusps in 30.2 minutes at 3 554 MiB — the same count as `Õ`, as it must
be, since both groups have trivial character image and the ambient plane orbit
is one class.

The `Õ` row's numbers: 189 720 cusps in 36.2 minutes at a 3 476 MiB peak, each cusp answering
`representative()` with a rank-two primitive isotropic plane of `T_Co` — the
count `#390` returned, now measured here on the cusp form of the same row, and
the index over the single `O(T_Co)`-class is 189 720.

Earlier attempts, each sampled every 30 s, show where the host's limit sits:

| row | peak | wall | outcome |
| --- | ---: | ---: | --- |
| `isotropic_orbit_representatives(2)` (the gathered row) | **9 538 MiB** | 1 365 s | exit 137, RSS still rising at ~1.2 GiB a minute |
| `cusps(2)` (the span row, `#588`'s instrument) | **3 190 MiB** | 2 081 s | exit 137, still building |

The span row is the smaller one and it too was killed, at 3 190 MiB, with the
host's available memory down to 3 GiB because other chats' jobs were running
beside it; the kill follows the host, not the row's own size, which is the
pattern `9dceec9` recorded.

The gathered row, alone on a quieter host, was **killed at 9 538 MiB peak,
exit 137, 1 365 s in**, with RSS still rising at about 1.2 GiB a minute and the
walk roughly two thirds done.  Its
arithmetic is 1.5 GiB of coset tables once, plus 189 720 planes at 68.4 KiB
each: about 13.9 GiB, which no host of this size will give it.

The two coefficients, measured on the same tree by drawing 400 planes from the
row and sampling RSS across them:

| the 400 planes | KiB a plane | what it says |
| --- | ---: | --- |
| held | **68.4** | the returned representative and the record that keeps it |
| dropped as they arrive, their spans kept | **26.3** | the identity registries keep the plane after the caller lets it go |

So the peak is not the walk and not the incidence: it is the per-plane
representative.  Of that 68.4 KiB, 42.1 KiB goes when the caller drops the
plane and **26.3 KiB does not** — the `@cached_method` keyed by the span by
value on the ambient lattice, `_lattice_subobject_spanning`, `_lattice_mor` and
`_lattice_on_gram`, the registries `#588` enumerated and `#594` has not yet
converted.  The remaining 42.1 KiB is the public call's own contract: it
returns a tuple of 189 720 constructed planes, and a tuple holds them.  The
second row's own datum is the two generators' strings, about 160 B a plane, so
it does not account for the 26.3 KiB.

So the item is a **cost item**, not a host accident: the row's peak is the
per-plane representative, 26.3 KiB of which survives the caller dropping the
plane.  That retained term is `#594`'s subject; the 42.1 KiB term is the
gathered return of the public call.
