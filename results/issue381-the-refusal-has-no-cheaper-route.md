# The refusal has no cheaper route: 83 cusps share classes, and a transporter is 355 s

`Otilde+`'s row refuses in the divided-class read because 24 of the 444 keys name
more than one line cusp (`issue381-the-divided-class-read-raises-at-tco.md`).
The refusal names the route that decides such an edge -- `tits_building_incidence`
with a transporter.  This note prices that route and says what the numbers leave
standing.

## The two measured prices

| datum | value | where |
| --- | ---: | --- |
| one matched cusp's transporter | **did not return in 355 s** | `issue381-the-transporter-is-a-coset.md` |
| the 13-edge `Gamma_{Co,2}` row of `T_Co` on the flag route | **1 685.31 s** | `issue381-kernel-incidence-rows.md` |
| line cusps / distinct keys / keys naming more than one | 527 / 444 / **24** | `line-cusps.log` |
| cusps that share their key with another | `527 - 444 = 83` | same |

The archive gives each line cusp of these rows `1 080` plane classes
(`issue381-kernel-incidence-rows.md`), so the 83 ambiguous cusps carry
`83 x 1 080 = 89 640` edge endpoints.  At the measured `355 s` a transporter:

* `89 640 x 355 s = 31.8 million s`, about **368 days**, against the driver's
  `10 800 s` cap -- and that is the floor, counting only edges whose line cusp is
  one of the 83 and assuming every one of them needs the question asked once.

At the flag route's own rate -- `1 685.31 s / 13 edges = 130 s` an edge -- the
row's `569 160` edges come to `74 million s`, about **2.3 years**.  Neither
number is a machine problem: no host makes a year into half an hour.

## Why no finer key of the same kind exists

The key is the `rho(Gamma)`-orbit of the line's divided class pair.  Two cusps
share a key exactly when some `g` in the subgroup's image carries one's class
pair to the other's while the cusps differ, i.e. when the class-pair map is not
injective on the double cosets `A \\ F / F_P` of Dutour Sikiric--Hulek,
arXiv:2302.01679v2, Lemma 3.6, printed p. 22.  The fibre of that map is a torsor
under `Stab_F(c_0) / F_P`, so **any invariant that is a function of the line's
discriminant class is constant on a fibre** and cannot separate the cusps in it.
A finer invariant has to read something that is not a function of the class: the
stabilizer's own image, or an actual isometry.

That is why the row refuses rather than guessing, and why the refusal is the
honest end of this route at `T_Co`.

## What this leaves for `#381`

The two kernel rows of `T_Co` are **blocked on the invariant, not on cost or on
the host**: the divided-class read is exact on 444 of the row's keys and refuses
on 24, and the route that decides those 24 is priced out by two orders of
magnitude.  The options are a design change -- carry the stabilizer's image so
the read can separate a fibre -- or accepting the refusal as the row's answer for
this lattice.

What is *not* claimed: that the 83 cusps' edges all need a question (some may be
decided by an exact span match, `line_vertex_candidates`' first branch), so the
`368 days` is an upper bound on that term and a floor on the transporter route;
and that `Otilde`'s row refuses too -- it was killed by the host before its
relation opened, twice, and that remains unmeasured.

No object is introduced: the key is the library's, the double cosets and the
fibre are Lemma 3.6's, and every figure above is a number the tree or a log
already carries.
