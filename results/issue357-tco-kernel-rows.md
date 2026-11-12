# #357: the Otilde and Otilde+ line rows on T_Co, through the double-coset route

The lattice is `NamedLattices.Tco` = `<2> + (U + E8(-1))(2)`, Dolgachev--Kondō,
Izv. Math. 77:3 (2013), §3 eq. (3.6), printed p. 513.  The rows are the two
kernel rows of that lattice: `Otilde(T_Co) = ker rho` (the call
`Tco.stable_orthogonal_group().isotropic_orbit_representatives(1)`) and
`Otilde+(T_Co) = ker(rho, sn)` (the call
`Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)`),
the double-coset route of Dutour Sikirić--Hulek, arXiv:2302.01679v2, lemma 3.6,
p. 22.  All rows were run on the #357 worktree at `a5fa20dc63` with the port
bound at `991b88b0`.

## The hypotheses, checked on T_Co

For the representative of the one `O(T_Co)`-orbit of primitive isotropic vectors
(`.tmp/357a-instrument.log`, 2080.3 s total under load 20-35, the ambient stage
685.9 s): the representative is the computed vector of coordinates
`[0, 0, -1, 0, ..., 0]` (the negated `U(2)`-partner `fp`, so the own-label
lookup is empty), and each computed check holds:

| check | result | time |
| --- | --- | ---: |
| split-signature witness (the four checks) | True | 46.9 s |
| complement discriminant surjective | True | 29.3 s |
| divided class zero | False | — |
| `Otilde` line stabilizer image | `([f2], False)` | 1092.7 s |
| `Otilde+` line stabilizer image | `([f2], True)` | 224.2 s |

`T_Co` has rank 11 and no summand `U`, and no check failed: the #351
vector-itself construction (the Bezout partner, the plane, the kernel complement)
generalizes to `T_Co` as is, and no repair was needed.

## The two rows, through the public call

Both rows were run once in the background (`.tmp/357b-rows.log`, one process,
the second row reusing the first's ambient stage and gate):

| row | call | count | time |
| --- | --- | ---: | ---: |
| `Otilde(T_Co) = ker rho` | `Tco.stable_orthogonal_group().isotropic_orbit_representatives(1)` | **527** | 1934.1 s |
| `Otilde+(T_Co) = ker(rho, sn)` | `Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)` | **527** | 294.0 s |

The total was 2299.4 s, the peak tree RSS 1176 MiB under a 6144 MiB guard.  Every
representative is a primitive isotropic vector of divisor 2 with a nonzero
divided class (the first being `[fp]`, the last a class of
`-354*[h] + 32*[ep] + ...`), as the divided-class construction returns.

## The comparison with the page

The page-proof value of research `sec-cusp-lifting` is 527 line orbits with
index 1 over every class.  Both recorded counts are **527**, so both agree with
the page: the agreement is reported here and recorded in
`tests/lattices/test_the_coble_lattice_otilde_and_otilde_plus_line_rows.sage`,
and neither count is asserted from the page.  No mismatch arose, so nothing was
filed on research.

## The test

`tests/lattices/test_the_coble_lattice_otilde_and_otilde_plus_line_rows.sage`
records both counts (527 and 527) and compares each with the page-proof value in
its docstring; the assertions are the recorded computed counts, never the page.
The test's own run (`.tmp/357-test.log`): `1 passed` in <TEST_TIME>, the peak
tree RSS <TEST_RSS>.
