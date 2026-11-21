# The line row of card 6JRX under Otilde+(Lambda_2) passes 5974 MiB without a count

Filed 2026-11-21, the day the row was measured, against `main` `d386f12`.  State:
open.  This is the second instance of the defect filed for card `6JRY`
(`results/issue319-6jry-otilde-plus-line-row.md`): the same row of the sister
lattice, under the same kind of group, on a lattice two units smaller.

## The row

| | |
| --- | --- |
| card | `6JRX` of `dzackgarza/lattice-database`, row `integral.primitive_orbits.Otilde+` |
| lattice | $\Lambda_2 = U \oplus U \oplus E_8(-1) \oplus E_8(-1) \oplus \langle -2\rangle$, rank 21, signature $(2,19)$, determinant $-2$ (the card's own invariants) |
| group | $\widetilde O^+(\Lambda_2) = \ker \rho \cap O^+(\Lambda_2)$, the kernel of the discriminant character intersected with the spinor-norm-one subgroup -- the card's `Otilde+`, which it identifies with Scattone's $O^*(L) = O_-(L) \cap \widetilde O(L)$ (J. Scattone, *On the compactification of moduli spaces for algebraic K3 surfaces*, Mem. Amer. Math. Soc. 374 (1987), Section 3.6) |
| expected | one orbit of primitive isotropic lines -- the card's row, from J. Scattone, same work, Theorem 4.0.1 |
| call | `group.isotropic_orbit_representatives(1).cardinality()`, the public orbit call of #286 (`PredicateSubgroups.isotropic_orbit_representatives`) |
| outcome | no value: 5974 MiB of resident memory at 834 s and still rising, when the measurement was stopped |

## What separates this row from the ones beside it

The other three rows of the same card are not affected, and each was measured on
the same host:

| row | card's value | call | time |
| --- | ---: | ---: | ---: |
| `6JRX:O:planes` | 4 | 4 | 90.9 s |
| `6JRX:O+:lines` | 1 | 1 | 9.9 s |
| `6JRX:O+:planes` | 4 | 4 | 95.1 s |
| `6JRX:Otilde+:lines` | 1 | -- | no value |

So the whole orthogonal group and its spinor-norm-one subgroup decide their orbits
of lines and planes on this lattice, and the discriminant kernel's line row does
not: the row is a cost of $\widetilde O^+(\Lambda_2)$'s line orbit computation,
not of the lattice, the harness or the module.

## The record of the stop

All measurements: the adopted runtime (SageMath 11.0.beta5, Python 3.14), the
indefinite port as the image provides it at `/repos/sage-indefinite-port` (this run
did not record which revision that copy is at), `main` `d386f12`, one process,
4 CPUs and 15 GiB of memory on the host.  The command, with `<tree>` the checkout:

```
~/sage-image/run.sh -w /work -b <tree>:/work -b <tree>/.git:<tree>/.git -- /bin/sh -c '
  cd /work && PYTHONPATH=/work/src:/work \
  /sage/.venv/bin/python -u tests/enriques_polarization_rows_by_card.py --one 6JRX:Otilde+:lines'
```

`ps` on the child after 834 s: `100% CPU, 5974 MiB resident`, still rising; the
job was then stopped through the session's job control, so the row has no outcome
and no value.  The sister row on card `6JRY` reaches 6312 MiB in 90 s by the same
call (`results/issue319-6jry-otilde-plus-line-row.md`); there the growth is about
ten times faster in the same runtime, so the two rows share the route and differ
in rate.

## Closing condition

The row closes when `isotropic_orbit_representatives(1)` returns a count on
$\widetilde O^+(\Lambda_2)$ for card `6JRX` and the count equals the card's row, in
the acceptance module's own run.  The repair belongs to the owner of that call.
