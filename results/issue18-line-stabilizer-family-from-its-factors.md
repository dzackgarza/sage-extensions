# The Enriques line stabilizer: what the provider now certifies, and what the acceptance still needs

The consumer result this unit is accepted by is the one in the issue body:
`INDUCTION.line_automorphism_generators(N, e1)` on
`N = U + U(2) + E8(-2)` returns the full line stabilizer's family on both
published representatives `I_1_1` (`Z e1`) and `I_1_2` (`Z e3`) **inside the
port's acceptance run**, and the port's case_3 line/plane/flag counts
(5/10/19) pass against it.  The reproducer is `.tmp/repro_marked_stabilizer.py`
and the acceptance call is the port's
`tests/acceptance/test_isotropic_orbits.sage::test_stabilizer_images_have_dutour_sikiric_hulek_indices[I_1_1]`.

## State, stated plainly

The provider side of that repair is complete and is now certified on the
smallest lattices.  The two remaining cost stages are both on the consumer's
own loop, and one of them is port source:

```
port isotropic_induction.py:304
    return tuple(lattice.integral_isometry(generator)
                 for generator in action.stabilizer().group_generators())
```

- `action.stabilizer().group_generators()` is this repository's
  `IntegralStructureAction.stabilizer()`: recorded at **25600 generators in
  1643.0 s** on `N` (1024 orbit points x 25 letters).
- the per-element `lattice.integral_isometry` conversion is recorded at
  **0.143 s each**, so about **3668 s** for the family, measured on the first
  2000 elements only; the total is the record's extrapolation, not a
  measurement of a completed family.

The repair the issue names converts `|letters| + |orbit|` maps (25 + 1024) and
composes them, which is about 150 s at the recorded rate.  That conversion
cannot be written in this repository: the loop is port source, and the port is
paused (`991b88b0`), so this repository cannot make the acceptance call return
by changing its own owners alone.  Nothing here claims otherwise.

## What is now certified here

`tests/lattices/test_the_line_stabilizer_family_is_rebuilt_from_its_factors.sage`
pins the law the consumer's repair rests on, at the parabolic subobject where
the factors, the orbit-lattice records and the middle transports are public:

    family element  =  ~t_(s.p) * middle_(p, s) * t_p

with `t_p: L -> L_p` the orbit point's transport and `s: L_p -> L_(s.p)` the
letter, so the whole family follows from `|letters| + |orbit|` converted maps,
and with the family asserted to be the *setwise* stabilizer (it acts on the line
by `+-1`, not by `+1` alone).

Measured on the adopted runtime (Sage 11.0.beta5, port `991b88b0`, guard
6144 MiB), at parent `bcad374`:

| specimen | letters | orbit | family | composites |
| --- | ---: | ---: | ---: | --- |
| `U + <-6>`, line `e1` | 3 | 6 | 18 | 18, equal element for element; line actions `+1` 12, `-1` 6 |
| `U + U(2)`, line `e1` | 7 | 4 | 28 (16 distinct) | 28; the 16 distinct are the parabolic subgroup's own family; line actions `+1` 12, `-1` 4 |
| `U + U(2)`, plane `<e1,e3>` | 4 | 6 | 24 | 24, each an isometry of `L` stabilizing `J` |
| `U(2) + U(2) + <-2>`, line | 8 | 2 | 16 | 16 |
| `U(4) + <-8>`, line `e1` | 3 | 2 | 6 | 6 |

Each row is the alignment the issue's measured stage needs; the two specimens
that carry a nontrivial lattice orbit *and* a nonidentity image epimorphism are
the ones that separate reading `L_p`'s own generators from reading the
transported source basis.

The suite: **3 passed in 3.36 s**, test-lint clean.

## Named image-run inputs (not run here)

Neither is started in this session; each is a full-size run and both belong to
an image, with the guard at 6144 MiB and a streaming `python3 -u peakrss.py`:

1. `.tmp/repro_marked_stabilizer.py` at the port's `991b88b0` and this
   repository's `main` -- the acceptance observation itself.  It records
   `INDUCTION returned ... gens in ...s` for `I_1_1` and `I_1_2` and then the
   port wrapper.  At the recorded stage costs it does not fit the port's 2400 s
   inner cap.
2. the port's
   `tests/acceptance/test_isotropic_orbits.sage::test_stabilizer_images_have_dutour_sikiric_hulek_indices[I_1_1]`,
   which is the same call with the index assertion on top.

The one change that makes either fit is the port's own loop: read
`stabilizer_schreier_factors()` with `orbit_lattice_records()` and
`middle_transport()`, convert those, and compose.  That is port source, and this
repository's contract for it is the certificate above.
