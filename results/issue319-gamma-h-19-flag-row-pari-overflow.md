# The `gamma-h-19:flags` row stops in PARI's machine-integer range

## What the row did

The bounded batch of #319 at `52657751a1644f7a2759e80994eb46479e000089`, run
through `tests/enriques_polarization_rows_by_card.py --one <row> --cap 240`, one
process per row:

| row | card | expected | returned | state | wall |
|---|---|---:|---:|---|---:|
| `0128:#Gamma_h:28` | 0128 Table 4 | 6 | 6 | PASS | 18.7 s |
| `0128:#Gamma_h:30` | 0128 Table 4 | 5 | 5 | PASS | 15.6 s |
| `gamma-h-19:flags` | gamma-h-19 Table 1 | 162 | — | BROKEN | 163.3 s |

Raw line of the third row:

```
@@ROW@@ {"id": "gamma-h-19:flags", "card": "gamma-h-19", "group": "Gamma_h,19",
 "quantity": "flags", "degree": null, "expected": 162, "lattice": "029J: U + U(2) + E8(-2)",
 "state": "BROKEN", "detail": "PariError: overflow in t_INT-->long assignment",
 "elapsed": 163.3}
```

The row is `group.isotropic_orbit_representatives(2, flag=True)` on the group
card `gamma-h-19` names, `Gamma_h,19`, on the Enriques period lattice
$N = U \oplus U(2) \oplus E_8(-2)$. Card `gamma-h-19` states 162 flag orbits
(Table 1, case 19, $\overline{\{2,7\}}$; `#I_12 = 162`), so the row did not
disagree with its card: it raised before returning a number.

## It is intermittent

The same call at the same revision returned `162` in 171.5 s on an immediate
rerun, and in six further runs of the same row in fresh processes (168.9 s,
171.1 s, 171.4 s, 170.2 s, 175.3 s, 261.9 s). So the stop is one outcome of a
run-dependent path, not a property of the card or of the lattice; it was
observed once in eight runs. The row therefore stays open: a row that returns
162 six times has not shown it always returns.

## The mechanism

The flag row's split of each ambient representative calls
`OrthogonalCharacterQuotient.exact_isotropic_stabilizer_generators`, whose
closure loop asks for an ambient isometry between two objects
(`isotropic_equivalence_witness`), which reaches
`sage_extensions.categories.lattice_morphisms._definite_isometry_matrix` and
from there `QuadraticForm.is_globally_equivalent_to`, that is PARI's `qfisom`.
The exception's own frames in the failing run name no other site.

PARI's `qfisom`/`qfauto` take machine integers, so an integral Gram whose
entries leave the 63-bit range cannot be handed to them at all. Measured
directly in the pinned image on the 1x1 Gram `[[n]]`:

```
32 bits  qflllgram ok Mat(1)   qfauto ok [2, [Mat(-1)]]   qfisom ok Mat(1)
63 bits  qflllgram ok Mat(1)   qfauto precision too low in qfminim
                               qfisom precision too low in qfminim
64 bits  qflllgram ok Mat(1)   qfauto overflow in t_INT-->long assignment
                               qfisom overflow in t_INT-->long assignment
84 bits  qflllgram ok Mat(1)   qfauto overflow in t_INT-->long assignment
                               qfisom overflow in t_INT-->long assignment
```

The library's own decision has the same window. On $A_3$ scaled by $c$, asked
for through the public call `Lattices(ZZ)(gram).Isom(target).an_element()`
between the lattice and the same lattice in the basis $(b_1 + b_2, b_2, b_3)$:

```
2^0:  entries up to  2 bits -> decided
2^10: entries up to 12 bits -> decided
2^30: entries up to 32 bits -> PariError: overflow in qfisom [lattice too large]
2^59: entries up to 61 bits -> PariError: precision too low in qfminim
2^60: entries up to 62 bits -> PariError: precision too low in qfminim
2^61: entries up to 63 bits -> PariError: overflow in t_INT-->long assignment
2^62: entries up to 64 bits -> PariError: overflow in t_INT-->long assignment
2^70: entries up to 72 bits -> PariError: overflow in t_INT-->long assignment
```

Scaling an integral lattice by a positive integer preserves its isometries
exactly: $W^{\mathsf T}(cG)W = cG'$ holds iff $W^{\mathsf T}GW = G'$. So every
row above is a lattice pair the library has to decide, and from $2^{30}$ on it
raises instead.

**What is measured and what is inferred.** The row's exception is raised at
this function and nowhere else (the frames of the failing run name
`_definite_isometry_matrix`, `is_globally_equivalent_to` and `qfisom`, with no
other frame between), and the message is one this function alone can produce.
The two facts are not the same: none of the six clean reruns reached a Gram of
that size — with the search instrumented, a clean run of the row enters
`_definite_isometry_matrix` four times, on rank-8 Grams whose largest entry is
6 bits — so the input the failing run handed it was not captured. That the
row's failure is this window entered from a long transport word is therefore an
inference from the raising site, not a measurement, and capturing the failing
run's Gram is what would settle it. The defect below is measured
independently of that inference: it is a public call that raises today.

## The smallest public reproduction

`tests/lattices/test_a_scaled_lattice_isometry_is_decided.sage` — one test,
0.57 s, red on this revision:

```
tests/lattices/test_a_scaled_lattice_isometry_is_decided.sage: in test_an_integral_lattice_scaled_by_a_large_integer_keeps_its_isometries
src/sage_extensions/categories/lattice_morphisms.py:3406: in _definite_isometry_matrix
    transformation = reduced_target_form.is_globally_equivalent_to(reduced_source_form, return_matrix=True)
sage/quadratic_forms/quadratic_form__equivalence_testing.py:109: in is_globally_equivalent_to
    mat = other.__pari__().qfisom(self)
E   cypari2.handle_error.PariError: overflow in t_INT-->long assignment
1 failed in 6.58s
```

It is the acceptance row's message, on a call that takes under a second.

## Where the defect is owned, and what a repair has to decide

At `_definite_isometry_matrix`: it hands both Gram matrices to PARI unreduced in
size, unlike `_definite_automorphisms`, which divides the scalar content out
first for exactly this reason ("Remove the scalar content before PARI converts
entries to machine integers").

The gcd of a Gram matrix's entries is invariant under an integral change of
basis — every entry of $U^{\mathsf T}MU$ is an integer combination of entries of
$M$, and $M = (U^{-1})^{\mathsf T}(U^{\mathsf T}MU)U^{-1}$ with $U^{-1}$
integral, so the two gcds divide each other — so two isometric forms have equal
content, and dividing both by their common content $c$ leaves the solution set
of $W^{\mathsf T}GW = G'$ unchanged. That covers the three messages above. A
pair whose forms have different contents is not isometric at all.

Not done in this round: the repair. The row was checked, the defect is filed,
and the fix is the next unit of work at that owner. Main carries the red test
from this round until that fix lands; the test is the first half of the pair.

## The issue to file

The connected GitHub repository reads issues and pushes commits but cannot
create an issue, so the body is here and `results/issue319-gamma-h-19-flag-row-pari-overflow.md`
is its file. Filing it:

```
gh issue create --repo dzackgarza/sage-extensions \
  --title 'The definite isometry search raises on a Gram matrix PARI cannot hold' \
  --body-file results/issue319-gamma-h-19-flag-row-pari-overflow.md
```

Title: **`_definite_isometry_matrix` raises `overflow in t_INT-->long assignment` on a Gram matrix PARI cannot hold**

Body:

> The definite isometry decision hands both Gram matrices to PARI's `qfisom`
> without reducing their size, so an integral lattice with a large minimal
> vector has no decided isometry. The Enriques flag row `gamma-h-19:flags` of
> #319 stops at that function with that message instead of returning its card's
> 162.
>
> Reproduction at `main` (one test, 0.57 s, red):
> `tests/lattices/test_a_scaled_lattice_isometry_is_decided.sage`.
> The lattice is $A_3$ scaled by $2^{61}$, the target the same lattice in the
> basis $(b_1+b_2, b_2, b_3)$; the transition matrix is unimodular, so the two
> are isometric and the call must decide it. It raises
> `PariError: overflow in t_INT-->long assignment` from
> `lattice_morphisms.py:3406` (`QuadraticForm.is_globally_equivalent_to`).
>
> The window, on the same pair: decided at 12-bit entries, `overflow in qfisom
> [lattice too large]` at 32 bits, `precision too low in qfminim` at 61–62 bits,
> `overflow in t_INT-->long assignment` from 63 bits. `qflllgram` is unaffected,
> and `_definite_automorphisms` already divides the scalar content out for this
> reason; `_definite_isometry_matrix` does not.
>
> Observed in the acceptance path: the row `gamma-h-19:flags` of #319
> (lattice `029J: U + U(2) + E8(-2)`, group `Gamma_h,19`, card 162) raised this
> error in 163.3 s at `5265775`, and returned 162 in six reruns at the same
> revision. Recorded in `results/issue319-rows-ledger.jsonl`.
>
> Repair at that owner: divide both Grams by their common content before the
> search and rescale the witness (the gcd of a Gram's entries is invariant under
> an integral change of basis, so isometric forms have equal content and the
> solution set is unchanged); a pair of unequal contents is not isometric.

## Extended measurement, 2026-11-23

Four further runs of the same row carried the instrumented search at the same
revision: `162` each, in 182.9, 187.8, 221.1 and 182.0 s, and each entered
`_definite_isometry_matrix` four times on rank-8 Grams whose largest entry is 6
bits. No run raised and no input was dumped. The row has now been run twelve
times at `5265775`: one `BROKEN` (the batch's 163.3 s) and eleven `PASS`.

The size at which the search would refuse was therefore never reached in a
decided run, which bounds the inference above rather than confirming it: the
failing run took a path these twelve runs did not, and only capturing that run's
Gram would show which input it was. The measured defect — the same function
refusing a public isometry call whose Gram is large — is unaffected by this.
