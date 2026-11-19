# The per-`J` index is one value per row, so the table needs no slicing

The plane rows of `#286` are asked for the index
`[Stab_{O(q)}(J) : rho(Stab_Gamma(P))]` over every liftable order-four isotropic
class `J = [P/2]` of `A_{T_Co}`, of which the page's `prop:coble-planecusp-finite`
counts `23715 = 527 * 270 / 6`.  Asked one class at a time, each index costs the
plane's certified parabolic, its 112 character keys, one subgroup meet and two
finite orders — 20-90 s a class on this VM — and 23715 of those is weeks.  It
does not have to be asked 23715 times.

## The value is constant over the row

Write `chi = (rho, sn_RR)` and `Pi_P` for the parabolic at `P`.  The subgroup is
a character preimage, `Gamma = chi^-1(S)`, so
`rho(Stab_Gamma(P)) = chi(Gamma) cap chi(Pi_P)`, and `chi(Gamma)` is **normal**
in `chi(O(L))` because `Gamma` is normal in `O(L)`.  For any `g` in `O(L)`,

```
chi(Gamma) cap chi(Pi_{gP}) = chi(Gamma) cap g chi(Pi_P) g^-1
                            = g (chi(Gamma) cap chi(Pi_P)) g^-1,
```

so its order is the same at every plane of the row.  `|Stab_{O(q)}(J)|` is the
same at every `J` as well, because the 23715 classes are one `O(q)`-orbit:
`|O(q)| / 23715 = 46998591897600 / 23715 = 1981808640`, which is the stabilizer
order `#360` reads at a `T_Co` plane.  The index is therefore one number per
row, with the class count as its multiplicity — not a table of 23715 entries.

## Measured, at two different classes

`Otilde(T_Co) = ker rho`, adopted runtime, load 8.2
(`.scratch/w286-probes/per-j.log`, `.scratch/w286-probes/per-j2.log`, probes
`.scratch/w286-probes/probe-per-j.py`, `probe-per-j2.py`):

| plane | `|Stab_{O(q)}(J)|` | `|rho(Stab_Gamma(P))|` | index | class |
| --- | ---: | ---: | ---: | --- |
| A (the base plane) | 1981808640 | 1 | 1981808640 | `J_A` |
| B (the transport by ambient generator 2) | 1981808640 | 1 | 1981808640 | `J_B != J_A` |
| B' (the transport by ambient generator 0) | 1981808640 | 1 | 1981808640 | `J_B' = J_A` |

The classes of planes A and B differ (`the classes differ: True`), so the
agreement is across classes and not inside one; the first probe's two planes
happened to lie in one class, which is why the second was run.  The same value
holds at both kernel rows (`.scratch/w286-probes/per-j.log`): `Otilde+` answers
1981808640 as well, since `chi(Gamma)` is trivial for both kernels and the
right-hand order is 1.

Two planes' indices cost **90.3 s** in one command (plane A 21.9 s, the search
for another class plus plane B's parabolic and index the rest).

## What this means for the run

The per-`J` obligation is met by one recorded value per row plus the class
count, which is what the driver now logs: the number of distinct classes it
recorded, the index at each, and `|O(q)| / |Stab(J)|` as the class count.  No
slicing and no image run are needed for it.  A class count that disagreed with
`23715` would be the finding, and it is recorded, not asserted.

What is *not* claimed here: that the index is the subgroup's orbit count over a
class for a kernel row.  It is not — `rho(Stab_Gamma(P))` is trivial there, so
the index is `|Stab(J)|` itself; the row's 189720 plane orbits come from
`|rho(O(L))| / |rho(Stab_{O(L)}(P))|`, a different quotient.  The page's
`23715 * 8` is the ambient group's decomposition, and its `8` is
`[Stab_{O(q)}(J) : rho(Stab_{O(L)}(P))]`, which `#360` measures directly.
