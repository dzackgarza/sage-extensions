# #371: `is_isotropic` and `isotropic_vector` in every rank

`T_Co.Aut().isotropic_orbit_representatives(2)` stopped at
`lattice_engines.py:496` (`qfsolve, dim >= 10 is not yet implemented`) because
isotropy was decided only by a witness search over the whole Gram matrix
(`results/issue360-coble-plane-row.md`).  This unit decides it by theorem where a
theorem applies, and builds the witness from a subspace of at most five
variables where the search cannot run.

## The decision rule

A nondegenerate form over `ZZ` or `QQ` of rank `n` is decided by three
statements, and a search runs only where none of them applies:

| case | answer | source |
| --- | --- | --- |
| definite (`signature_pair()` has one part zero) | **not isotropic** | a definite form is nonzero on every nonzero vector — that is what definiteness is |
| indefinite, `n >= 5` | **isotropic** | Meyer's theorem: an indefinite rational quadratic form in at least five variables represents zero (Serre, *A Course in Arithmetic*, Ch. IV, §3.2, Cor. 2, printed p. 43, as #371 cites it) |
| indefinite, `n <= 4` | `qfsolve`, witness or obstruction | Hasse–Minkowski: a rational form represents zero iff it does over `RR` and over every `QQ_p` (Serre, Ch. IV, §3.2, Thm. 8, printed p. 41) |

The threshold is sharp and the third row is not decoration: `⟨1, 1, -3⟩` (rank 3)
and `⟨1, -2⟩` (rank 2) are indefinite and anisotropic over `QQ`, so signature
alone decides nothing below rank five — the first is already a pinned row of
`tests/lattices/test_genus.sage`, and the second is pinned in the new test.

## The witness

`isotropic_vector()` on a nondegenerate lattice over `ZZ` or `QQ`:

* rank at most nine: PARI's `qfsolve` on the whole form, as before;
* rank at least ten: the form is diagonalized over `QQ`
  (`_congruence_diagonal_form`), the five diagonal directions carrying both
  signs span a subspace that Meyer's theorem makes isotropic, `qfsolve` runs
  there — five variables, inside its own bound — and the solution is carried back
  through the diagonalizing change of basis.  Over `ZZ` the rational solution is
  cleared of denominators and made primitive (`_raise_lattice_direction`), and
  the result is checked to have square zero: a disagreement between the
  diagonalization and the solver raises instead of returning a false witness.

The solver is Denis Simon's code — Sage's `quadratic_forms.qfsolve` module is
"Interface to the PARI/GP quadratic forms code of Denis Simon" — and its bound is
the implementation's, not the mathematics'.  The reference for answering rational
isotropy by Simon's method is Hecke's `src/QuadForm/Quad/Spaces.jl`,
`_isotropic_subspace`, which cites Simon, *Quadratic equations in dimensions 4, 5
and more* and whose sibling `_rational_witt_index` this repository already
follows.  The rank-five reduction itself is this module's; what makes it a
witness and not a search is the theorem.

## The test

`tests/lattices/test_the_isotropy_decisions_in_high_rank.sage` — **4 passed in
2.92 s** (`.tmp/qc-evidence/issue371-test.log`), through the public calls only:

```
U + E8(-1),  rank 10, signature (1, 9)   is_isotropic() True,  witness square 0, primitive
T_Co,        rank 11, signature (2, 9)   is_isotropic() True,  witness square 0, primitive
E8(-1) + E8(-1), rank 16, definite       is_isotropic() False, isotropic_vector() raises
<1, -2>,     rank 2,  indefinite         is_isotropic() False, isotropic_vector() raises
```

`test_lint` on the module: **1 file, 0 findings**.

## The `T_Co` plane call

`T_Co.Aut().isotropic_orbit_representatives(2)` and
`T_Co.Aut().tits_building_incidence()` both return, in one process
(`.tmp/qc-evidence/issue371-tco-plane-call.log`, peak 747 MiB, whole run
1495.3 s, the VM at load 5 with two foreign jobs of other chats running):

```
T_Co is_isotropic(): True                                     (setup, 9.7 s)
isotropic_orbit_representatives(2) = 1 orbit                1423.4 s
  representative ((2,0,0,0,-1,-1,-2,-2,-2,-2,-2), (0,1,0,0,0,0,0,0,0,0,0)), primitive
  divided classes of the representative: 2*[h] - [a1] + 2*[a8], [fp]
cusps(2) = 1                                                 0.0 s
isotropic_orbit_representatives(1) = 1                       0.0 s   (one line orbit, already cached)
cusps(1) = 1                                                 0.0 s
tits_building_incidence() = 1 edge                           62.2 s
  edge: line (0,1,0,0,0,0,0,0,0,0,0) -> plane <the representative above>
```

Against #360's page proofs: the plane row **1** is research #645's
`thm:coble-plane-stabilizer-image` item 5, the incidence is one line orbit to one
plane orbit (the page's "three line classes in every plane class" is a statement
about the 527 line classes and the 23715 plane classes, which `O(T_Co)` collapses
to one orbit each), and the line row **1** is the transitivity
`thm:plane-half-index` item 4 records.  Nothing mismatches.

The same call stopped twice before this unit, and the two stops were the same
defect at two sizes:

```
before:  9 min 6 s  lattice_engines.py:496  qfsolve, dim >= 10 is not yet implemented
                        (rank 11, the whole Gram)
second:  the incidence's witt_index on T_Co: the same refusal on a 9x9 Gram
```

The second stop is why the reduction is stated for rank five and above rather
than for rank ten and above: PARI's `qfsolve` answers a diagonal form of size
eleven (`issue371-qfsolve-bound.log`) and refuses that nine-variable form, so the
refusal is a property of the reduction path and not of the dimension alone, and
the dimension of the *call* is what has to be inside Simon's stated range.
After the change the same `witt_index` — `_rational_witt_index` on `T_Co`'s
rational space, which splits off two hyperbolic planes — runs its witnesses at
five variables and the incidence returns.

The plane row cost 972.7 s in the run before this change and 1423.4 s in this one,
on a differently loaded machine (the 972.7 s run had one foreign job, the
1423.4 s run two, at load 5); the two numbers are not a controlled comparison and
no cause is claimed for the difference.  Where the time goes is a separate
finding for #329/#335, not this unit's.

## Not verified here

The Serre pages (Ch. IV §3.2, Cor. 2 on p. 43; Thm. 8 on p. 41) are cited as
#371 states them and were not opened in this session; what is checked here is
that the rule they license agrees, on every specimen of the test, with the
search where the search runs at all, and with the pinned anisotropic rows of the
existing suite (`⟨1, 1, -3⟩`, `⟨1, -2⟩`).
