# The 63 KB a plane: which structure holds it, and what the kernel row can afford

sage-extensions#584 says that
`OrthogonalCharacterQuotient.register_isotropic_lift`
(`src/sage_extensions/categories/orthogonal_quotients.py:2533`, the write at
`:2551`) *retains 63.0 KB per plane that its caller never reads*, and that this
is what kills the 189720-plane kernel incidence row of #381 at the runner's
memory ceiling.  This note measures that retention structure by structure, and
the finding is that the number is real but the owner is not this operation:

| what a plane of the row costs | bytes a plane | read afterwards? |
| --- | ---: | --- |
| the plane subobject the row returns as its representative | 32.1 KB | yes -- it *is* the cusp |
| the registry entry `register_isotropic_lift` writes | 7.5 KB | yes -- the lift, at `predicate_subgroups.py:1010` |
| resident bytes beyond the live objects (allocator) | 23 KB | -- |
| **the row's measured per-plane resident cost** | **63 KB** | |

The parabolic family the record lists as the entry's third component is **one
object for the whole row**, not one per plane: `tuple(family) is family` is
`True` on this tree (the probe prints it), so the entry's second element costs
8 bytes of slot and nothing more, at every one of the 189720 planes.

Nothing here is repaired by dropping a retained object, because nothing the call
retains is unread.  What the measurement does decide is #381's capacity
question, and it decides it against the row: with `register_isotropic_lift`'s
whole retention gone -- the extreme of every repair this issue allows -- the
plane row still costs 65.5 KB a plane against 66.2 KB with it: **six hundred
bytes a plane, 0.12 GiB at 189720 planes, out of 11.6** -- and the walk's own
retention (#585, 350-400 KB a plane) is five times the whole plane row.
**#381 waits on #585, and no repair of this registry moves its number.**

## 1. The instrument, and what it can and cannot say

The probe on the adopted runtime (Sage 11.0.beta5, `~/sage-image/run.sh`, the
image rootfs) at `main` `ecfbea1`, on `T_Co = <2> + U(2) + E8(-2)` (D. Dolgachev
and S. Kondo, Izv. Math. 77:3 (2013), section 3, equation (3.6), printed p. 513)
and the kernel row `Otilde(T_Co) = ker rho`:

* `.tmp/issue584/probe-584-retention.py` runs the row's own plane row --
  `_plane_orbit_from_parabolic_stabilizer`: the slicing plane's certified
  parabolic, the finite image's coset walk, and one
  `register_isotropic_lift(transported, splitting, family)` per representative --
  and reads `VmRSS` after every plane;
* the same probe with `PROBE_MODE=noreg` makes the same plane and the same span
  key and does not register, so the two runs on the same specimens differ by
  exactly what the call retains.  `PROBE_MODE=noreg` is therefore the measurement
  of the strongest repair #584 permits ("not kept at all");
* with `PROBE_METER_EVERY` set, the same probe attributes bytes: a referents walk
  from each retained object against a `seen` set persisting across planes, so an
  object shared with the row (the lattice, the parents, the categories, the
  parabolic family, the identity) is counted once, at the plane that first
  reaches it.

The meter's `seen` set is itself memory -- one Python integer per object walked,
about 50 bytes -- so metering every plane would add tens of kilobytes a plane to
the slope being measured.  The headline slopes below are taken with the meter
**off**; the attributions are taken with it sampling every tenth plane.

A memory question has no stage record to read (`CONTRIBUTING.md` `ENV-03`
records wall time), so these are probes and not the run's own records; the run
that would have carried the record was killed (image run 44012568639, exit 137 at
8649 s, `results/issue381-kernel-row-runner-kill.md`).

## 2. The registry entry, measured

One plane, at the write site: the registry is a dict keyed by `_span_key(plane)`
whose value is `(lift, tuple(parabolic_generators))`.  Marginal bytes, from the
probe's attribution over the metered planes:

| component | bytes a plane |
| --- | ---: |
| the span key the entry is looked up by | 466 |
| the entry tuple itself | 64 |
| the isometry the split produced for this plane | 6945 |
| the parabolic family | 0 -- one tuple object for the row |

The isometry is the whole of it.  One element of `O(T_Co)` costs 8.7 KB B:
an 11x11 integral matrix is 968 B of it, and the rest is the arrow-category
machinery every `OwnedLatticeIsometryMor` carries -- measured on two products of
the ambient generating family, at a two-letter word and at a five-letter word,
which cost the same 8.7 KB B: the cost is the element, not the word.

## 3. Where the 63 KB a plane sits

| structure | bytes a plane | what it is |
| --- | ---: | --- |
| the plane subobject the row returns | 32,098 | `_preamble_selected_framing_source` 19,248, `_module_subobject_construction` 11,352, `_preamble_form_computation` 3,960, `_preamble_gram_tensor` 592 |
| the registered lift | 6,945 | an element of `O(T_Co)`; a two-letter and a five-letter product of the ambient generating family both cost this |
| the span key the registry is looked up by | 466 | `(id(lattice), hermite rows)` |
| the entry tuple | 64 | the `(lift, family)` shell |
| the parabolic family | 0 | one object for the row, not one per plane |
| **live objects a plane** | **39,573** | |
| **resident bytes a plane** | **63,095** | the 100-plane slice below; the difference is allocator |

The ratio of resident to live is 1.6, and it is the same ratio at every size, so
the allocator is a constant factor on this workload and not a second retention.
Two reader-facing consequences of the table: **the registry is 7,475 B of the
63 KB a plane (one eighth), and the row's own returned representative is 32 KB of
it (one half)**.  The record's 63.0 KB was measured as a resident-set slope and
is correct as such; what it is not is a 63 KB retention held by
`register_isotropic_lift`.

The 63 KB is distributed, and the largest part of it is not the registry: it is
the plane the row *returns*.  `_plane_orbit_from_parabolic_stabilizer` transports
a representative for every double coset and returns them; `cusps(2)` wraps each in
an `_arithmetic_cusp`, which retains it as the cusp's representative for the
subgroup's lifetime (`cusps` is a `cached_method`).  That is the row's answer --
189720 representatives, one per orbit -- and no repair of the registration can
remove it without removing the row's answer.

## 4. Everything the entry holds is read

| the entry's part | who reads it |
| --- | --- |
| the span key | `isotropic_lift_of`, `certified_parabolic_generators` -- one dict hit each |
| the lift | `tits_building_incidence` (`predicate_subgroups.py:1010`) at every plane, for `transport_covering`'s `move = lift * ~reference_lift` |
| the family | `certified_parabolic_generators` (`orthogonal_quotients.py:2717`), conjugating it by the plane's lift |

Dropping the lift is not a saving, it is a different computation: with
`isotropic_lift_of` answering `None`, the walk falls through to
`orthogonal_group.isotropic_equivalence_witness(ambient_plane, plane)` at every
plane -- the port's isometry search, measured at 355 s for one matched pair
(`results/issue381-kernel-incidence-rows.md`) against a row of 189720.

## 5. Ten, a hundred, a thousand planes

Two probes on the same specimens, one process a point; `PROBE_MODE=baseline`
registers as the row does, `PROBE_MODE=noreg` makes the same plane and the same
span key and does not register (the ceiling of every repair #584 allows).  RSS is
`VmRSS` read after every plane; the per-plane figure is the steady bands.

| planes | mode | wall | RSS after the first lift | RSS at the end | per-plane RSS |
| ---: | --- | ---: | ---: | ---: | ---: |
| 10 | baseline | 225.2 s | 1291.9 MiB | 1292.2 MiB | not resolvable (0.3 MiB over nine planes) |
| 100 | baseline | 214.2 s | 1232.1 MiB | 1238.0 MiB | 62.5-69.9 KB in bands, 63.1 KB overall |
| 1000 | baseline | 213.8 s | 1379.0 MiB | 1442.1 MiB | 66.3-68.3 KB in bands, 66.2 KB overall |
| 100 | noreg | 216.7 s | 1330.4 MiB | 1336.3 MiB | 62.1-64.8 KB in bands, 62.8 KB overall |
| 1000 | noreg | 229.9 s | 1274.5 MiB | 1336.9 MiB | 65.5-67.5 KB in bands, 65.5 KB overall |

The ten-plane point is not a coefficient: 0.3 MiB of growth over nine planes is
the sampler's own granularity, which is why the record's table carries the same
"too small to resolve" at ten planes.  The 100- and 1000-plane points are the
coefficient, and they agree.

## 6. The row at 189720 planes, and #585

`tits_building_incidence` runs four terms, and the slices price three of them:

| term | measured | at 189720 planes |
| --- | ---: | ---: |
| the interpreter, `T_Co`, `Otilde(T_Co)`, the slicing plane's certified parabolic | 421 MiB resident | 0.41 GiB |
| the finite image's coset walk, whose tables the split iterator holds | +871 MiB (421 -> 1292 MiB) | 0.85 GiB |
| the plane row: one returned representative and one registered lift a plane | 63.1 KB a plane at 100, 66.2 KB at 1000 | 11.4 to 12.0 GiB |
| the walk's own retention (#585) | 350-400 KB a plane | 66-76 GiB |
| the line row (527 cusps) | not measured to completion: still rising at 2.7 MiB/s when its command was cut at 559.5 s (`results/issue381-kernel-row-runner-kill.md`) | unmeasured |

At the measured coefficient the plane row alone is 12.7 to 13.3 GiB resident, which
is the record's 12.8 GiB at the same 63 KB a plane.

**With `register_isotropic_lift`'s retention gone** -- the strongest repair #584
allows, measured as `PROBE_MODE=noreg` -- the plane row costs 65.5 KB a plane
instead of 66.2, so 189720 of them are 11.6 GiB and the row stands at
1.3 + 11.6 = 12.9 GiB before the walk starts.  The fall is 0.12 GiB, and it is
inside the run-to-run wobble: the lifted isometry is *made* either way, and what
the registry changes is only whether its pages are held, so the allocator hands
the next plane's work the same blocks.  Against the runner's 16 GiB the plane
row would fit, with 3 GiB for the line row and the relation -- and nothing to
spare.

**That is not what the row pays.**  The walk's own retention, #585's unit, is
350-400 KB a plane -- 66 to 76 GiB -- five times the whole plane row, and it is
in the same process.  So the answer to the capacity question is:

> At 189720 planes the kernel incidence row is 1.3 GiB + 11.6 GiB + 63-72 GiB
> = **76 to 85 GiB**, and it does not fit a 16 GiB runner.  **#381 waits on #585
> as well as on this issue**, and #585 is the larger term by five: without it the
> row would fit, with it the row is four to five times the runner.

Even with #585 repaired to the "few kilobytes a plane" its own acceptance asks
for, the row would stand at about 1.3 + 11.6 + 0.7 = 13.6 GiB -- inside 16 GiB,
but with the line row, the relation's certificates (section 7, ~33 GiB at three
a plane) and the allocator still to come out of what is left.

## 7. The certificate coefficient

The record derives the certificate count -- three a plane through `retain_flag`,
569160 on `T_Co` -- and does not read their size, because the row has never
returned.  Two of a certificate's parts are measurable without the row: a
*carried* flag, which `transport_covering` makes at every plane
(`move.transport_isotropic_object(flag)`), and a fresh transporter, which is a
product in the ambient generating family.  Both made on `T_Co` from the row's own
objects, one meter across the three carries so that the first pays only what the
refined isotropic category costs to build once:

| carry | the flag it makes | the transporter it is carried by |
| ---: | ---: | ---: |
| 1 | 229,912 B | 0 B (a generator of the shared family) |
| 2 | 66,480 B | 8,663 B |
| 3 | 46,020 B | 6,496 B |

A carried flag is 46 KB and a fresh transporter 6.5 KB at steady state, so a
certificate that retains a flag and its two transporters is about 59 KB of its
own objects, and **three a plane is about 177 KB a plane, 33 GiB at 189720
planes**, beside the cusps it shares with the two cusp rows.

That is a derivation from measured parts, not a reading of a returned row: the
kernel row on `T_Co` has still never returned.  It is also the largest per-plane
term measured in this unit -- larger than the plane row (63 KB) and of the same
order as the walk's retention (350-400 KB) -- and it is a property of the
relation the call *returns*, so no repair of an auxiliary registry touches it.

## 8. What was repaired, and what was not

**No code change is landed, and the measurement is the reason.**  Every part of
the registry entry is read (section 4), so the two repairs #584 allows both come
to the same thing: return the record to the caller and let it drop it, or do not
keep it at all.  Either leaves `isotropic_lift_of` answering `None`, and the walk
then asks the port's isometry search at every plane -- 355 s for one matched pair
-- instead of reading a word the split already spelled.  That is not removing a
retention the caller does not read; it is removing a datum the caller does read,
and it changes what the row costs by four orders of magnitude in the other
direction.

What the measurement files instead, for the owner of each structure:

| finding | size a plane | at 189720 planes | where |
| --- | ---: | ---: | --- |
| the registered lift (an isometry of `O(T_Co)`) | 6,945 B | 1.3 GiB | the registry; read at `predicate_subgroups.py:1010` |
| the span key and the entry shell | 530 B | 0.1 GiB | the registry; read by the lookup |
| the returned representative, of which `_preamble_selected_framing_source` | 32,098 B (19,248 B) | 6.0 GiB (3.6 GiB) | the cusp row's answer; the subobject's own construction |
| one isometry of `O(T_Co)` whatever its word | 8.7 KB | -- | the arrow owner: `_isometry_inverse_computation` is the largest part of it |
| one edge certificate (a carried flag and two transporters) | ~59 KB | ~33 GiB at three a plane | the relation the call returns |

The honest summary of #584 is therefore three sentences.  The 63 KB a plane is
real and linear.  One eighth of it is the registry this issue names, one half is
the representative the row returns, and the rest is the allocator's constant
factor on both.  Removing the whole registry would take the row from 12.7 GiB to
12.9 GiB and would break the walk; what actually decides whether the row returns
is #585's 66-76 GiB, and then the 33 GiB the returned relation's certificates
would add.
