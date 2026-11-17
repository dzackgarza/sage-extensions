# What the incidence driver's route switch was decided on

The measurements behind `tests/coble_gamma_co_2_incidence_rows.py --route`, on
`T_Co = ⟨2⟩ ⊕ U(2) ⊕ E8(−2)`, the row `Otilde(T_Co) = ker rho`, tree `5f6abb8`,
on the adopted runtime (`~/sage-image/run.sh`, Sage 11.0.beta5), each probe
under `peakrss.py`.  Every log's header names the tree, the port's commit and
the load.

| file | what it measures |
| --- | --- |
| `probe-plane-row.py`, `probe-plane-row.log` | the plane row (`cusps(2)`), 200 planes: 69 570 B and 5.98 ms a plane; and the certificate route's carriage, 40 planes: 249 016 B and 13.68 ms a plane, three flags a plane |
| `probe-class-route.py`, `probe-class-route.log` | the divided-class route's per-plane work, 199 planes: 1 427 B and 1.65 ms a plane |
| `probe-line-row.py`, `probe-line-row.log` | `cusps(1)` of the same subgroup: cut at its 1 500 s wall without returning |
| `probe-decision-cost.py` | the cost of the route decision itself (`subgroup_image_order`, `preserves_conjugation`), first and second call |
| `check-routes.py` | the route `auto` takes for each `T_Co` row: certificate for `O`, divided-class for `Otilde` |
| `verify.sh`, `verify.log` | the switch's verification: both routes on `U+U(2)+<-2>`, `auto` on `6JRS`, and the gate |
| `probe-class-check.py`, `probe-class-check.log` | every carried class pair of the class route against the class pair of the carried line, 119 planes |

The derived numbers are in the commit body of the switch and in
`results/issue-body-the-plane-rows-representatives-are-a-constructed-subobject.md`.

`verify.log`'s sixth section is titled "6JRS, auto (certificate, rho trivial)"
because the script's title was written before the run; the route line the
driver logged inside that section is the run's answer -- `divided-class` -- and
the title was corrected in `verify.sh` after it.
