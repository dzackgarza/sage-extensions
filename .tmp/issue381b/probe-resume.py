"""A kernel plane row in two processes: a segment up to a mark, then the tail from it.

`PROBE_PHASE=split` draws the row's planes and stops at `PROBE_MARK` of them,
writing the checkpoint and exiting.  `PROBE_PHASE=tail` reads it, rebuilds what
the tail reads, continues the walk, and runs the row's relation and contract.

The checkpoint is the row's *anchor* and, a plane, the two data that name it:

* the anchor is the source plane's **span**, as the rows of its Hermite form.
  The drawn representative is not reproduced by a second process -- two runs of
  the same draw here returned `((1,0,0,0,0),(0,0,0,1,0))` and
  `((0,1,0,0,0),(0,0,0,1,0))` -- so a split records the span it drew and both
  phases walk from the copy that span names (:func:`_subobject_of_span`).  The
  family at that copy is the family at the drawn plane, in the same order.
* a plane's span, and the **word** its lift was spelled by.  The word is the
  only per-plane datum a checkpoint can hold: the finite element the relation
  reads at every plane is an element of the discriminant factor's orthogonal
  group and does not pickle (`PicklingError` on its category's metaclass), so
  the tail spells the word to recover it (:meth:`_spelled_lift`), which is the
  cost a resumed plane pays and a drawn plane does not.

What this buys and what it does not is measured in
`results/issue381-the-kernel-row-checkpoint.md`.
"""

import os
import pickle
import sys
import time

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.isotropic_orbits as isotropic_orbits  # noqa: E402
import sage_extensions.categories.orthogonal_quotients as orthogonal_quotients  # noqa: E402

from coble_gamma_co_2_incidence_rows import (  # noqa: E402
    _lattice_by_name,
    _row_subgroup,
    chosen_route,
    row_contract,
    row_relation,
)

ROW = os.environ.get("PROBE_ROW", "Otilde")
PHASE = os.environ.get("PROBE_PHASE", "split")
MARK = int(os.environ.get("PROBE_MARK", "1000"))
LATTICE_NAME = os.environ.get("PROBE_LATTICE", "Tco")
CHECKPOINT = os.environ.get(
    "PROBE_CHECKPOINT", f"/repos/sage-extensions/.tmp/issue381b/checkpoint-{LATTICE_NAME}-{ROW}.pkl"
)
start = time.monotonic()
clock = lambda: time.monotonic() - start  # noqa: E731


def mark(what):
    rss = int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0]) / 1024
    print(f"[{clock():9.1f} s rss {rss:8.1f} MiB] {what}", flush=True)


lattice = _lattice_by_name(LATTICE_NAME)
subgroup = _row_subgroup(lattice, ROW)
quotient = subgroup.finite_character_quotient()
drawn = tuple(lattice.Aut().isotropic_orbit_representatives(2))[0]
source_span = isotropic_orbits._span_key(drawn)
# The anchor is the span: the copy it names is what both phases walk from.
source = isotropic_orbits._subobject_of_span(lattice, source_span)
family = tuple(source.parabolic_stabilizer_generators())
mark(f"{LATTICE_NAME}, the {ROW} row, source span {source_span[1]}, {len(family)} parabolic generators")


def rows_of(span):
    return span[1]


if PHASE == "split":
    held = []
    for plane in orthogonal_quotients._iter_transported_planes(quotient, source, family):
        span = isotropic_orbits._span_key(plane)
        retained = quotient.__dict__["_isotropic_lift_registry"][span][0]
        held.append((rows_of(span), tuple(retained.letters), retained.flip is not None))
        if len(held) % 10000 == 0:
            mark(f"the segment: {len(held)} planes held")
        if len(held) >= MARK:
            break
    with open(CHECKPOINT, "wb") as handle:
        pickle.dump(
            {"row": ROW, "lattice": LATTICE_NAME, "source": rows_of(source_span), "planes": held},
            handle,
        )
    mark(f"checkpoint written: {len(held)} planes, {os.path.getsize(CHECKPOINT)} bytes")
    raise SystemExit(0)

# ---- the tail ------------------------------------------------------------------
with open(CHECKPOINT, "rb") as handle:
    checkpoint = pickle.load(handle)
for key, wanted in (("row", ROW), ("lattice", LATTICE_NAME)):
    if checkpoint[key] != wanted:
        raise SystemExit(f"the checkpoint holds {key} {checkpoint[key]!r}, not {wanted!r}")
if checkpoint["source"] != rows_of(source_span):
    # The anchor is the checkpoint's, not this process's draw: a different draw
    # would make the walk's order another one and the skip below another skip.
    raise SystemExit(
        f"the checkpoint was taken from the source {checkpoint['source']} and this process drew "
        f"{rows_of(source_span)}: the walk is not the one the checkpoint's mark counts"
    )
held = checkpoint["planes"]
mark(f"checkpoint read: {len(held)} planes")

flip_element = None
if any(flipped for _rows, _letters, flipped in held):
    _j, sign_labels = quotient._sign_descent_rank()
    flip_element = quotient._kernel_sign_flip(sign_labels[0]) if sign_labels else None
registry = quotient.__dict__.setdefault("_isotropic_lift_registry", {})
restoring = time.monotonic()
spans = []
for rows, letters, flipped in held:
    span = (id(lattice), rows)
    spelling = orthogonal_quotients._LiftSpelling(tuple(letters), flip_element if flipped else None)
    registry[span] = (spelling, family, quotient.image(quotient._spelled_lift(spelling))["discriminant"])
    spans.append(span)
mark(f"the registry restored: {len(registry)} entries in {time.monotonic() - restoring:.1f} s")

started = time.monotonic()
cusps = [isotropic_orbits._arithmetic_cusp(subgroup, isotropic_orbits._subobject_of_span(lattice, span))
         for span in spans]
mark(f"the restored planes cusped: {len(cusps)} in {time.monotonic() - started:.1f} s")

held_rows = {rows for rows, _letters, _flipped in held}
seen = set()
for plane in orthogonal_quotients._iter_transported_planes(
    quotient, source, family, resume_after=len(held)
):
    rows = rows_of(isotropic_orbits._span_key(plane))
    if rows in held_rows or rows in seen:
        raise SystemExit(
            f"the tail's walk yielded the plane {rows}, which the checkpoint already holds: the "
            f"anchor did not reproduce the walk, so the mark {len(held)} counts another row's planes"
        )
    seen.add(rows)
    cusps.append(isotropic_orbits._arithmetic_cusp(subgroup, plane))
    if len(cusps) % 10000 == 0:
        mark(f"the tail: {len(cusps)} plane cusps")
mark(f"the walk continued: {len(cusps)} plane cusps in all")

from sage_extensions.categories.sets.finite_ordered_sets import (  # noqa: E402
    _distinct_finite_ordered_set,
)

subgroup.cusps.clear_cache()
# The rank is the cache's key: a seeding that omits it answers every rank with
# the plane row, and the line row the relation indexes against is then the
# planes' -- which the relation refuses by name rather than reading.
subgroup.cusps.set_cache(_distinct_finite_ordered_set(cusps), 2)
mark(f"the cusp row seeded: {subgroup.cusps(2).cardinality()} plane cusps")

lines = tuple(subgroup.cusps(1))
mark(f"the line row: {len(lines)} line cusps")
taken, reason = chosen_route(subgroup, "divided-class")
mark(f"the row's route: {taken}")
started = time.monotonic()
incidences = tuple(row_relation(subgroup, taken))
mark(f"the relation: {len(incidences)} edges in {time.monotonic() - started:.1f} s")
planes_row = tuple(subgroup.cusps(2))
outcome = row_contract(lattice, subgroup, ROW, lines, planes_row, incidences, taken)
mark(f"the verdict: {outcome.report()}")
