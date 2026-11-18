# The line stabilizer's generators are the two factors of its Levi split

The acceptance is `test_a_stabilizers_generators_generate_a_subgroup.sage`'s
second specimen: `O(T_{\mathrm{En}})`'s setwise stabilizer `S` of the primitive
isotropic line `\mathbf Z e_1`, `T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)`
(rank 12, signature (2,10)).  `S` is built in about a second;
`S.group_generators()` had returned nothing after 2400 s.

## The mechanism

`setwise_stabilizer` selects the stabilizer's generating family lazily
(`select_group_generators` -> `LatticeIsometryMor._marking_stabilizer_generators`
-> `LatticeIsometryCategory._marked_automorphism_generators`), and for an
indefinite lattice that method delegated every marking it did not construct
itself to the indefinite port.  For a rank-one primitive isotropic marking the
port's branch (`isotropic_induction.py:304`, bound revision `991b88b0`) is

```
tuple(lattice.integral_isometry(generator)
      for generator in action.stabilizer().group_generators())
```

i.e. it realizes the integral-structure action's **orbit Schreier family** and
converts every member from the rational group to an integral isometry.  On
`T_{\mathrm{En}}` that family is `|letters| * |orbit| = 26 * 1024 = 26 624`
members (measured: the action's finite representation has 1024 orbit points and
26 letters; building the action took 4.8 s and the representation 3.9 s), at
0.143 s a conversion -- about 3 800 s -- on top of realizing the rational family
(1 643 s at 25 600 generators, `results/issue18-line-stabilizer-family-from-its-factors.md`).
The family is not wrong: it generates the stabilizer.  It is the wrong
construction for this question, because the stabilizer's own construction
already presents it as two factors.

The consumer stop quoted in the item (`lattice_morphisms.py:4041`,
`preimage.group_generators()` inside `discriminant_point_stabilizer_image_generators`,
2 662 s at 2.51 GiB) is the same smell at another owner: that family is the
Schreier family of the orbit of a point of `A_L`, 2.3e7 members on `T_{Co}`
(`results/issue358-the-gamma-co-2-line-row.md`, section 5), and its
`drop_trivial` pass evaluates every member.  It is **not** repaired here.

## The repair

`src/sage_extensions/categories/lattices.py`:

| site | what it is |
| --- | --- |
| `_marked_automorphism_generators` (:2827) | the dispatch now asks `_isotropic_parabolic_generators` |
| `_isotropic_parabolic_generators` (:2873) | rank one -> the line family, rank two -> the plane block family |
| `_marked_primitive_isotropic_subobject` (:2887) | the prelude both constructions read |
| `_isotropic_line_stabilizer_generators` (:2956) | **the repair**: the two-factor family |

`\rho: P_I \to O(K_I)`, `g \mapsto g|_{I^\perp/I}` with `K_I = I^\perp/I`, is a
group morphism whose kernel is the pointwise part of the parabolic.
`IsotropicReductions` already states both factors: `levi_action()` selects a
section on its image (`_levi_section`, through the signed lift torsors), so
`levi_lift(gamma)` gives one integral lift of an isometry of `K_I`, and it
selects kernel generators (`_levi_kernel_generators`: the integral Eichler
transvection kernel `F^+(1) = K_{\mathbf Z}`, plus one reversing element when
that fibre is nonempty).  For `g` in `P_I`, `\rho(g)` is a word in the selected
generators of `O(K_I)`; the same word in their lifts is an element of `P_I` with
the same image, so `g` differs from it by an element of the kernel.  Hence

    P_I = < one lift per generator of O(K_I) > * < the kernel's generators >,

with no coset enumerated.  The construction answers `None` -- so the caller
keeps the port's route -- when the marking is not a rank-one primitive
isotropic arrow of an indefinite even lattice over `ZZ`, when
`\mathrm{rank}(K_I) = 0`, and when a generator of `O(K_I)` has no integral lift;
a proper image would make the two factors generate only a subgroup.

Structure cited at the owners read here: Zemel, arXiv:1902.08264v2,
Proposition 1.6 on printed p. 10 (the parabolic maps onto the Levi quotient with
the unipotent radical as its kernel); Gritsenko--Hulek--Sankaran,
arXiv:0810.1614, section 3.1, equations (4)--(5) for the Eichler transvections.

## Measured (`T_{\mathrm{En}}`, line `\mathbf Z e_1`, port `991b88b0`)

```
lattice, O(L), line, stabilizer built                 4.6 s (incl. the star import)
reduction built                                       0.9 s
K_I rank 10, unimodular False, splitting complement (e_f,)
O(K_I) generators                                     15 in 4.1 s
levi image contains the first four generators         (True, True, True, True)
lift of three generators                              0.0 s; the first stabilizes the line
levi kernel generators                                12 in 4.1 s
whole two-factor family                               27 in 13.4 s
every member stabilizes the line                      True
group.subgroup(family)                                0.0 s; supergroup() is group
```

The public call returns 26 generators in 13.1 s on a second run (the port's
ambient family is not deterministic, sage-extensions#289), each admitted by the
line's own predicate, and one of them negates the line -- so the family is the
setwise stabilizer, not the pointwise one.

## Red, then green

Command (`.scratch/i18/pytest.sh`, tree bound at `/repos/sage-extensions`, port
at `/work`):

```
timeout -s KILL 150 /sage/.venv/bin/python -m pytest -o addopts= \
  -p qc_sage_session -p sage_extensions.testing.suite_budget \
  -p sage_extensions.testing.test_lint --durations=0 \
  tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage
```

Red, on the parent tree with the test file's own lint no longer stopping
collection (`fix: the stabilizer acceptance file runs` in the same push):

```
.
Killed
pytest exit 137
```

one passing dot and the run killed at 150 s inside
`test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup`.

Green, same command with the repair and a 900 s bound (time gates ON), over the
file and the two others the repair touches -- the factor law and the rank-two
path through the same dispatch:

```
7 passed in 23.30s
13.76s call  tests/groups/...::test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup
5.59s call   tests/lattices/test_the_stabilizer_generators_carry_the_radical.sage::test_...
0.86s call   ...test_the_line_stabilizers_family_is_its_factors_composites
0.71s call   ...test_the_line_stabilizers_family_negates_the_line_somewhere
0.68s call   ...test_the_plane_stabilizers_composites_are_isometries_that_stabilize_the_plane
0.55s call   ...test_a_generated_groups_line_stabilizer_generates_a_subgroup
0.03s call   ...test_a_family_outside_the_group_is_refused
pytest exit 0
```

The 13.76 s call is under the 20 s test-call ceiling, so the acceptance passes
with the gate on.  `test_a_family_outside_the_group_is_refused` -- the file's
third test -- still refuses `G.subgroup((swap,))` for `G = <-1>` inside the
finite `O(U)`: that refusal is still the decision that the swap lies outside
`G`, and the repaired line path did not turn it into a retreat.

## What else the repair touches

`tests/lattices/test_the_line_stabilizer_family_is_rebuilt_from_its_factors.sage`
compared the factor composites with `parabolic_subgroup().group_generators()`
*as sets*.  That identity held because the library's line family *was* the
orbit's Schreier family; it is not what the composite law says.  The law is that
the lattice-level composite `\sim t_{s.p} \cdot \mathrm{middle} \cdot t_p`
equals the group-level word `\sim t_{s.p} \cdot s \cdot t_p` converted along
`L`, and that is what the test now asserts, on the same specimens and with the
same discriminating power: a composite, its being an isometry of `L` and its
admission by the parabolic are still asserted, and a `middle_transport` read on
the transported source basis is neither.

## What is not run, and what is not claimed

- `discriminant_point_stabilizer_image_generators` and the orbit Schreier
  family it selects from are untouched; the consumer's 2 662 s stop is there.
- No `T_{Co}` row was re-run.  Its line and kernel rows have never returned for
  reasons of their own (`results/issue358-...`, `results/issue381-...`), so
  there is no green row to regress and none claimed.
- `lattice-database#40`'s acceptance item was not run here.
- `tests/lattices/test_nondegenerate_marking_stabilizers.sage` does not run on
  `main` either: the file trips its own lint (TL11 `generators` at line 18,
  TL01 port import at line 63), so all four of its tests error at setup.  Run by
  hand, two of its specimens now raise the port's own
  `ValueError: ... does not mark a totally isotropic sublattice` -- a rank-one
  marking of a *non-isotropic* vector, refused by
  `marked_lattices._isotropic_sublattice` on the parent tree as well, since both
  versions of the prelude answer `None` there and hand the marking to the port.
  That file is stale against the port, not against this repair.
