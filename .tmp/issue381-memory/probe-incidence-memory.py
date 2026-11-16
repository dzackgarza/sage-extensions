"""Probe: the resident memory the Otilde(T_Co) incidence holds as it walks its planes.

The row walks 189720 planes (#390) and the kernel run was killed at 80 min before
it printed a row (image run 43964809482).  This probe measures which structure
holds the memory, by driving the row's own mechanism one stage at a time over a
few thousand planes of ``T_Co`` and sampling the process's resident set:

  stage A  the row's registered lifts: one primitive isotropic plane of ``T_Co``
           and one ambient isometry carrying the retained plane onto it, which is
           the record ``register_isotropic_lift`` keeps per plane of the row;
  stage B  the row's one covering, computed at the retained plane;
  stage C  that covering carried to every plane, which is what
           ``transport_covering`` does per plane, its carried flags retained in a
           list the way the incidence's ``sourced_flags`` retains them;
  stage D  the incidence itself, over a truncated plane row of the same planes,
           which adds the edge certificates to the same process.

Every plane here is a genuine primitive isotropic plane of ``T_Co`` and every
carrying isometry is a genuine isometry of ``T_Co`` (a word in the reflections of
the lattice in its ``E_8(-2)`` root basis), so the mechanism this measures is the
row's own; what the probe does not use is #390's eight-hour coset walk, which is
why the plane row is fed here instead of enumerated.  The stages are cumulative
and the sample lines carry the registry sizes, so a stage's own growth is the
difference between its samples.
"""
import os
import random
import signal
import threading
import time
import traceback

START = time.monotonic()
STATE = {"stage": "startup", "planes": 0, "frame": 0}


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def sizes():
    quotient = STATE.get("quotient")
    if quotient is None:
        return "registries -"
    def many(name):
        return len(quotient.__dict__.get(name, {}))
    return (
        f"lifts {many('_isotropic_lift_registry'):7d} "
        f"transports {many('_transported_isotropic_objects'):7d} "
        f"coverings {many('_isotropic_covering_registry'):4d} "
        f"bridges {many('_isotropic_root_bridges'):4d}"
    )


def sample():
    while True:
        print(
            f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB "
            f"stage={STATE['stage']} planes={STATE['planes']} frames={STATE['frame']} "
            f"{sizes()}",
            flush=True,
        )
        time.sleep(5)


threading.Thread(target=sample, daemon=True).start()

import sys

# Objects every retained datum of the row points into -- the lattice, the
# subgroup, the quotient, the shared certified family -- are counted once as the
# row's own and not again per plane.
SHARED = set()


def deep_size(obj, seen=None, depth=0):
    """The bytes ``obj`` retains, by walking its own attributes and containers.

    Shared parent and category objects are not counted: they belong to the row,
    not to the plane, and counting them per plane would report a cost the row
    does not pay per plane.
    """
    if seen is None:
        seen = set()
    if id(obj) in seen or id(obj) in SHARED or depth > 8:
        return 0
    seen.add(id(obj))
    total = sys.getsizeof(obj, 0)
    if isinstance(obj, dict):
        for key, value in obj.items():
            total += deep_size(key, seen, depth + 1) + deep_size(value, seen, depth + 1)
        return total
    if isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            total += deep_size(item, seen, depth + 1)
        return total
    attributes = getattr(obj, "__dict__", None)
    if attributes:
        for value in attributes.values():
            total += deep_size(value, seen, depth + 1)
    return total


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key
from sage_extensions.categories.orthogonal_quotients import (
    _plane_parabolic_incidence_flags,
)

mark = time.monotonic()


def stage(label):
    global mark
    now = time.monotonic()
    print(
        f"  {now - mark:8.2f} s  {label}  rss {rss_mib():7.1f} MiB  {sizes()}",
        flush=True,
    )
    mark = now


# Each stage is time-bounded rather than counted: the point is a resident-set
# slope per plane, and the number of planes that fit in a stage's budget is what
# the runtime allows.  A count would either overrun the ten-minute command or
# sample so few planes that the slope is noise.
A_SECONDS = float(os.environ.get("PROBE_A_SECONDS", "240"))
C_SECONDS = float(os.environ.get("PROBE_C_SECONDS", "60"))
D_SECONDS = float(os.environ.get("PROBE_D_SECONDS", "150"))

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
STATE["quotient"] = quotient
stage(
    f"Otilde(T_Co), index {quotient.index()}, "
    f"preserves conjugation {quotient.preserves_conjugation()}"
)

names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
source = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
retained_flag = IsotropicFlag(lattice, (source, names["ep"]))
retained_plane = retained_flag.top()
retained_plane.is_parabolic_complete()
family = tuple(retained_plane.parabolic_stabilizer_generators())
identity = subgroup.supergroup().one()
quotient.register_isotropic_lift(retained_plane, identity, family)
retained_span = _span_key(retained_plane)
stage(f"the retained plane, its parabolic ({len(family)} generators), its lift")

# --- stage A: the row's planes and their registered lifts -----------------------
STATE["stage"] = "A-lifts"
# The reflecting words of the E8(-2) root basis act on the planes of T_Co with
# only a few orbits, so they cannot feed a row of thousands of planes.  The
# ambient orthogonal group's own generating family does: a power of one generator
# and a short word in several are isometries of the lattice, distinct spans are
# kept, and each such isometry is the plane's registered lift -- what the row's
# double-coset walk registers per plane.
orthogonal_group = subgroup.supergroup()
ambient_generators = tuple(orthogonal_group.group_generators())
random.seed(381)
candidates = []
for generator in ambient_generators[:24]:
    lift = generator
    for _power in range(60):
        candidates.append(lift)
        lift = generator * lift
for _word in range(4000):
    lift = ambient_generators[random.randrange(len(ambient_generators))]
    for _step in range(random.randrange(0, 3)):
        lift = ambient_generators[random.randrange(len(ambient_generators))] * lift
    candidates.append(lift)
stage(f"A: {len(ambient_generators)} ambient generators, {len(candidates)} candidate isometries")

seen = {retained_span}
planes = []
lifts = []
a_started = time.monotonic()
for lift in candidates:
    if time.monotonic() - a_started > A_SECONDS:
        break
    target = lift.transport_isotropic_object(retained_plane)
    span = _span_key(target)
    if span in seen:
        continue
    seen.add(span)
    quotient.register_isotropic_lift(target, lift, family)
    planes.append(target)
    lifts.append(lift)
    if len(planes) <= 5 or len(planes) % 250 == 0:
        elapsed_a = time.monotonic() - a_started
        print(
            f"    A: {len(planes)} planes so far, {elapsed_a:.1f} s, "
            f"rss {rss_mib():7.1f} MiB {sizes()}",
            flush=True,
        )
STATE["planes"] = len(planes)
stage(f"A: {len(planes)} distinct planes of {len(candidates)} candidate isometries, one registered lift each")
SHARED.update({id(lattice), id(subgroup), id(quotient), id(family), id(retained_plane)})
plane_bytes = deep_size(planes[-1])
lift_bytes = deep_size(lifts[-1])
span_bytes = deep_size(_span_key(planes[-1]))
print(
    f"    A: one plane of the row retains {plane_bytes} B (its subobject), "
    f"{lift_bytes} B (its registered lift), {span_bytes} B (its span key): "
    f"{plane_bytes + lift_bytes + span_bytes} B a plane",
    flush=True,
)

# --- stage B: the row's one covering, at the retained plane --------------------
STATE["stage"] = "B-covering"
covering = _plane_parabolic_incidence_flags(subgroup, retained_plane, retained_flag)
quotient.register_isotropic_covering(retained_plane, 0, identity, covering)
stage(f"B: the row's one covering at the retained plane: {len(covering)} flags")

# --- stage C: the same covering carried to every plane -------------------------
STATE["stage"] = "C-carry"
SKIP_CARRY = os.environ.get("PROBE_SKIP_CARRY") == "1"
sourced_flags = []
reference = quotient.isotropic_covering_reference(0)
per_plane_ms = []
c_started = time.monotonic()
for position, lift in enumerate(() if SKIP_CARRY else lifts):
    if time.monotonic() - c_started > C_SECONDS and position > 5:
        break
    began = time.monotonic()
    assert quotient.isotropic_covering_of(planes[position], 0) is None
    carried = quotient.transport_covering(reference[1], reference[2], lift)
    sourced_flags.extend(carried)
    per_plane_ms.append((time.monotonic() - began) * 1000)
    STATE["planes"] = position + 1
    STATE["frame"] = len(sourced_flags)
    if (position + 1) % 100 == 0:
        recent = per_plane_ms[-200:]
        print(
            f"    C: {position + 1} planes carried, {len(sourced_flags)} flags held, "
            f"{sum(recent) / len(recent):8.2f} ms a plane, rss {rss_mib():7.1f} MiB {sizes()}",
            flush=True,
        )
if SKIP_CARRY:
    stage("C: skipped (PROBE_SKIP_CARRY=1)")
else:
    stage(
    f"C: {len(per_plane_ms)} planes carried, {len(sourced_flags)} flags held, "
    f"{sum(per_plane_ms) / len(per_plane_ms):.2f} ms a plane on average"
)

if SKIP_CARRY:
    carried_bytes, flag_bytes = 0, 0
else:
    carried_bytes = deep_size(sourced_flags[-1].terms()[0])
    flag_bytes = deep_size(sourced_flags[-1])
print(
    f"    C: one carried line retains {carried_bytes} B; one carried flag {flag_bytes} B; "
    f"the transports registry holds {len(quotient.__dict__.get('_transported_isotropic_objects', {}))} datums",
    flush=True,
)

# --- stage D: the incidence, over a truncated plane row of these planes -------
STATE["stage"] = "D-edges"
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

line_cusps = subgroup.cusps(1)
stage(f"D: the row's {len(line_cusps)} line cusps")

truncated = tuple(_arithmetic_cusp(subgroup, plane) for plane in planes)
STATE["planes"] = 0
STATE["frame"] = 0
real_cusps = type(subgroup).cusps


def counted(cusps):
    for position, cusp in enumerate(cusps):
        STATE["planes"] = position + 1
        yield cusp


def patched(self, rank=1):
    if rank == 1:
        return line_cusps
    return counted(truncated)


type(subgroup).cusps = patched
try:
    signal.signal(signal.SIGALRM, lambda signum, frame: (_ for _ in ()).throw(TimeoutError("one plane")))
    signal.setitimer(signal.ITIMER_REAL, D_SECONDS)
    began = time.monotonic()
    incidences = tuple(subgroup.tits_building_incidence())
    signal.setitimer(signal.ITIMER_REAL, 0)
    print(f"    D: the incidence returned {len(incidences)} edges in {time.monotonic() - began:.1f} s", flush=True)
except TimeoutError:
    print(f"    D: the incidence did not return inside {D_SECONDS} s", flush=True)
except Exception:
    traceback.print_exc()
finally:
    signal.setitimer(signal.ITIMER_REAL, 0)
    type(subgroup).cusps = real_cusps
stage(f"D: the incidence over {len(truncated)} planes")
print(f"final rss {rss_mib():.1f} MiB {sizes()}", flush=True)
