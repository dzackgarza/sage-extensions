# The joint sign line row: what `None` answered and the datum that replaces it

`sage-extensions#596`.  The `SO~+` row of `T_Co`'s primitive isotropic line series
died at 9.2 GiB because `isotropic_line_stabilizer_image` answered `None` for the one
ambient line, and `None` sends the row down the exact integral stabilizer.  This note
records what `None` meant, the certificate that replaces it, and the eight rows
measured on the stored `6JRR` Gram tensor.

Measurements are on the adopted runtime (`~/sage-image/run.sh`, Sage 11.0.beta5,
`/sage/.venv/bin/python`) with this repository's tree at `/work` on `PYTHONPATH` and
`sage-indefinite-port` at its unpaused head `54d12c2e` at `/port`.  The processes run
under `~/sage-image/peakrss.py`; the probes are under the turn's `.scratch/issue596/`.

## 1. What `None` meant

`isotropic_line_stabilizer_image` has three answers, and the consumers
(`orthogonal_quotients._yield_subgroup_isotropic_orbit_representatives`,
`lattice_morphisms.LatticeIsometryGroups.split_orbit`) read all three apart:

| answer | meaning | consumer |
| --- | --- | --- |
| `"NOSPLIT"` | the ambient `O(L)`-orbit is one `Gamma`-orbit | yield the ambient representative |
| `(class_points, sign_flag)` | the datum the double-coset walk consumes | `splitting_isometries_from_line_class` |
| `None` | **not certified** | `exact_isotropic_stabilizer_generators` + `splitting_isometries` |

So `None` is not "the stabilizer image is the whole group" -- that is `"NOSPLIT"`, a
different value which the consumer handles on its own branch -- and the consumer does
not misread it.  For `SO~+ = ker(rho, det, sn)` on `T_Co` the `None` came from one
refusal, at the top of the discriminant branch: a joint determinant *and* spinor
quotient was not certified by the one kernel-sign witness the code had, because one
flip covers one sign coset and not a two-character image.  A second refusal of the same
shape stood in the zero-class branch (`len(sign_labels) > 1`).

## 2. The certificate

The split needs `chi(Stab_{O(L)}(x))`, and with `Gamma = ker chi` the orbit count is

    [chi(O(L)) : chi(Stab(x))] = [im rho : Stab_{im rho}({c, -c})] * 2^(j - j'),

where `j` is the dimension of the sign patterns `ker rho` realizes
(`_sign_descent_rank`) and `j'` the dimension of the patterns realized by
`Stab(x) cap ker rho`.  The discriminant factor is certified by Eichler's criterion or
by the split-signature and complement witnesses; the sign factor needs `j' = j`, and
the elements that exhibit it are cheap:

* the negation `-1`, which carries `v` to `-v` and so fixes the line as a set;
* the Levi part `1_plane + (-1)_complement` of the parabolic at the line
  (`_split_signature_witness`, Zemel arXiv:1902.08264v2, Proposition 1.10, p. 13);
* the integral reflections in the vectors orthogonal to `v`.

On `T_Co` the first two have patterns `(det, sn) = (-1, +1)` and `(-1, -1)`: the
negation is in `ker rho` (`A_L = (Z/2)^11`, so `-1` acts trivially) and in `O+`, while
the Levi witness has spinor norm `-1`.  They span `F_2^2 = j`, so `j' = j = 2` and no
sign coset is left to lift.  `line_stabilizer_sign_patterns` computes exactly this
family and the call refuses (`None`) unless the patterns span the sign space of
`ker rho`.

The family is finite on purpose.  The square-2 fibre of an indefinite lattice is
infinite, so `Lattices.vectors_of_square_and_divisibility(2, 1)` -- the enumeration the
older branches of this call used for their witnesses -- is not part of it: on
`U + U + <2>` that enumeration does not return (a probe was stopped at 907 MiB after
four minutes), while the negation and the Levi part already span the space on every
specimen measured here.  A lattice whose patterns the finite family does not present is
refused, which is the same answer the call gave before the repair.

## 3. The eight rows on `T_Co`

`Lattices(ZZ)(gram)` on `6JRR`'s stored `gram_tensor` -- rank 11, signature (2, 9),
`A_L = (Z/2)^11` -- one row at a time, in the driver's order, in one process:

| subgroup | how it is built | constant | seconds |  |
| --- | --- | ---: | ---: | --- |
| `O` | `L.Aut()` | 1 | 0.01 | the ambient row, 1 line in 39.42 s, reused |
| `SO` | `L.SO()` | 1 | 0.02 | |
| `O+` | `L.O_plus()` | 1 | 0.06 | |
| `SO+` | `O+ cap SO` | 1 | 3.00 | was 33.17 s through the exact route |
| `Otilde` | `L.stable_orthogonal_group()` | 527 | 93.10 | |
| `SOtilde` | `SOtilde cap SO` | 527 | 64.83 | |
| `Otilde+` | `SOtilde cap O+` | 527 | 74.05 | |
| `SOtilde+` | `SOtilde cap SO cap O+` | **527** | **72.15** | was not returned: >= 510 s, >= 9200 MiB |

The eight rows in one process: 307.2 s, peak 1019 MiB, the process's own `VmHWM`
1019 MiB -- against the database's 238.7 s and 1033 MiB for the seven that returned
on the certify image.  An earlier run of the same eight rows peaked at 879 MiB, so the
peak is a collector's, not a row's.  Nothing was capped and no row was sampled down.

## 4. What the exact route cost

The row that answered `None` took `exact_isotropic_stabilizer_generators` and
`splitting_isometries`: the first materializes a right transversal of the preimage of
the class-data stabilizer in a group of order `4.7e13`, the second enumerates double
cosets in the joint permutation model, and both retain a constructed transport per
split line.  On the certify image that was `>= 510 s` and `>= 9200 MiB`.  With the
certificate the row is one class-orbit walk and `527` lifts, the same work the three
`ker rho` rows do, and it costs 83.08 s inside a process that peaks at 879 MiB.

## 5. The refusals removed, and what replaced each

* the joint determinant-and-spinor refusal in the discriminant branch, and its twin in
  the zero-class branch (`len(sign_labels) > 1`), are the same refusal: one witness of
  one sign coset was all the code could certify.  Both are replaced by the pattern-rank
  test, which is exact for one factor and now covers two.
* `_joint_discriminant_image_gap` refused the joint sign case outright.  The group it
  computes is `pi_1(Q cap S) = (cap_i H_i) cap rho(K_0)`, which is contained in the meet
  `cap_i H_i` of the preimage targets, so a trivial meet of the targets is the whole
  answer and no sign kernel is needed for it.  Every `ker rho` row is this case; a
  nontrivial meet with two sign factors is still refused.
* `_iter_splitting_isometries_in_im_rho_from_image` searched for a kernel-sign element
  on every call, including the calls where the stabilizer presents every sign coset and
  there is nothing to lift.  It now searches only where a coset is left, so the three
  rows that present a sign coset -- `SOtilde`, `Otilde+` and `SOtilde+` -- do not scan
  the lattice's reflection candidates for an element they do not use.

## 6. The neighbours

Nothing else changed value.  Ten small indefinite lattices, four rows each -- the
ambient row, `Otilde`, `Otilde+` and `SOtilde+` -- on the parent `ba51bdf` and on the
repaired tree, give the same forty counts:

    ambient / Otilde / Otilde+ / SOtilde+
    U + U + <-2>        1 1 1 1        U + <-2>             1 1 1 1
    U + U + <2>         1 1 1 1        U + <2>              1 1 1 1
    U + U + <-18>       2 2 2 2        U + U + U            1 1 1 1
    U(2) + U(2) + <-2>  1 9 9 9        U + U + <-2> + <-2>  1 1 1 1
    U(2) + <-2>         1 2 2 2        U(2) + <2>           1 2 2 2

The five test files that consume the call -- the new one,
`test_line_stabilizer_image_requires_eichlers_hypothesis`,
`test_the_exact_discriminant_image_of_a_line_stabilizer`,
`test_isotropic_line_orbits_of_small_indefinite_lattices` and
`test_the_stable_line_orbit_row_comes_from_the_exact_finite_image` -- are 13 passed in
19.96 s on the repaired tree, with the test lint reporting no findings.
