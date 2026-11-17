r"""Probe: name the walk's per-plane retainer on T_Co, by measurement.

The ``carry`` slice of ``results/issue381-kernel-row-runner-kill.md`` measures the
walk's own per-plane work at 350-400 KB a plane, flat in the plane count.  This
probe runs that same slice (same objects, same calls: one covering at the first
plane, ``transport_covering`` and the three line keys at each further plane) and
accounts for the retention four ways at every sample point:

* the resident set of the process;
* the resident set attributed to each phase of a plane -- the carry, the keys,
  the release -- accumulated over the planes between two samples;
* every dictionary, list, set and other attribute the quotient holds, by entry
  count and by size (``sys.getsizeof`` over the structure, bounded depth);
* Python's own traced allocations (``tracemalloc``), whose current total is
  printed at every sample and whose snapshot at the last sample is compared
  against the snapshot at plane 100 by traceback, naming the allocating line.

No cap, no sampling of the walk: every plane is walked and every phase measured.
"""

import os
import sys
import threading
import time
import tracemalloc

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "10"))
TRACE_DEPTH = int(os.environ.get("PROBE_TRACE_DEPTH", "6"))
ACCOUNT_DEPTH = int(os.environ.get("PROBE_ACCOUNT_DEPTH", "3"))
MAIN = threading.get_ident()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def sample():
    while True:
        time.sleep(10.0)
        print(f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB", flush=True)


threading.Thread(target=sample, daemon=True).start()

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import FlagType
from sage_extensions.categories.orthogonal_quotients import (
    _isotropic_line_image_key,
    _plane_parabolic_incidence_flags,
)

MARK = time.monotonic()


def stage(label):
    global MARK
    now = time.monotonic()
    print(f"    {now - MARK:9.2f} s  {label}  rss {rss_mib():8.1f} MiB", flush=True)
    MARK = now


def deep_size(value, depth=ACCOUNT_DEPTH, seen=None):
    """Size of a structure in bytes: its own object plus, to a bounded depth, what it holds."""
    if seen is None:
        seen = set()
    ident = id(value)
    if ident in seen:
        return 0
    seen.add(ident)
    total = sys.getsizeof(value, 0)
    if depth <= 0:
        return total
    if isinstance(value, dict):
        try:
            items = list(value.items())
        except Exception:
            return total
        for key, item in items:
            total += deep_size(key, depth - 1, seen) + deep_size(item, depth - 1, seen)
    elif isinstance(value, (list, tuple, set, frozenset)):
        try:
            items = list(value)
        except Exception:
            return total
        for item in items:
            total += deep_size(item, depth - 1, seen)
    return total


def account(quotient, label):
    """Every structure the quotient holds, by entry count and size, largest first."""
    rows = []
    for name, value in list(vars(quotient).items()):
        if isinstance(value, (dict, list, set, frozenset, tuple)):
            try:
                entries = len(value)
            except Exception:
                entries = -1
            rows.append((deep_size(value), entries, type(value).__name__, name))
    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)
    print(f"[account {label}] quotient holds {len(rows)} containers, {total / 1024:9.1f} KiB in all", flush=True)
    for size, entries, kind, name in rows[:12]:
        print(f"    {size / 1024:9.1f} KiB  {entries:8d}  {kind:9s} {name}", flush=True)
    return total


def traced():
    current, peak = tracemalloc.get_traced_memory()
    return current / 1024 / 1024, peak / 1024 / 1024


lattice = NamedLattices.Tco
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
print(f"[probe] the walk's per-plane work over {PLANES} planes of the row", flush=True)
stage("T_Co and the row's plane")

subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage("Otilde and its character quotient")

print(f"[probe] the plane is parabolic complete: {plane.is_parabolic_complete()}", flush=True)
family = tuple(plane.parabolic_stabilizer_generators())
quotient.register_isotropic_lift(plane, quotient.supergroup.one(), family)
stage(f"the plane's parabolic: {len(family)} generators")

splittings = quotient._iter_splitting_isometries_in_im_rho(family)
first_splitting = next(splittings)
stage("the split's first lift")
lifts = [first_splitting]
planes = [first_splitting.transport_isotropic_object(plane)]
quotient.register_isotropic_lift(planes[0], first_splitting, family)
for position in range(1, PLANES):
    splitting = next(splittings)
    lifts.append(splitting)
    planes.append(splitting.transport_isotropic_object(plane))
    quotient.register_isotropic_lift(planes[-1], splitting, family)
stage(f"{len(planes)} planes of the row, one registered lift each")

basis = tuple(plane.inclusion().domain().module_generating_set())
vectors = tuple(plane.inclusion()(plane.inclusion().domain().module_generator(label)) for label in basis)
ambient_flag = lattice.isotropic_flag(vectors[0], vectors[1], flag_type=FlagType((1, 2)))
transported_flag = first_splitting.transport_isotropic_object(ambient_flag)
covering = _plane_parabolic_incidence_flags(subgroup, planes[0], transported_flag)
print(f"[probe] the covering at the first plane: {covering if covering is None else len(covering)} flags", flush=True)
stage("the row's one covering, computed at the first plane")

account(quotient, "after the covering")
tracemalloc.start(TRACE_DEPTH)
snapshot_before = tracemalloc.take_snapshot()
print(f"[trace] started at plane 1, current {traced()[0]:8.1f} MiB traced", flush=True)

carries = []
keys = []
releases = []
phase_rss = {"carry": 0.0, "keys": 0.0, "release": 0.0}
band = max(1, PLANES // 10)
mark = time.monotonic()
rss_start = rss_mib()
snapshots = {1: snapshot_before}
for position in range(1, PLANES):
    before = rss_mib()
    carry_start = time.monotonic()
    carried = quotient.transport_covering(lifts[0], covering, lifts[position])
    carry_done = time.monotonic()
    lines = [flag.terms()[0] for flag in carried]
    carry_rss = rss_mib()
    for line in lines:
        _isotropic_line_image_key(quotient, line)
    keys_done = time.monotonic()
    keys_rss = rss_mib()
    quotient.release_isotropic_transports(lines)
    releases.append(time.monotonic() - keys_done)
    release_rss = rss_mib()
    carries.append(carry_done - carry_start)
    keys.append(keys_done - carry_done)
    phase_rss["carry"] += carry_rss - before
    phase_rss["keys"] += keys_rss - carry_rss
    phase_rss["release"] += release_rss - keys_rss
    if position < 10 or (position + 1) % band == 0 or position + 1 == PLANES:
        now = time.monotonic()
        steps = 1 if position == 1 else min(band, position - 1)
        carried_by = (release_rss - rss_start) * 1024 / max(1, position)
        print(
            f"  [carry plane {position + 1:6d}/{PLANES}] {now - mark:9.4f} s over {steps} steps"
            f"  carry {1000 * sum(carries[-steps:]) / steps:8.3f} ms and"
            f" {1000 * sum(keys[-steps:]) / steps:8.3f} ms of keys a plane"
            f"  rss {release_rss:8.1f} MiB  {carried_by:7.1f} KiB a plane since the covering"
            f"  transports {int(quotient.retained_isotropic_transport_count())}"
            f"  traced {traced()[0]:8.1f} MiB",
            flush=True,
        )
        print(
            f"      rss by phase since plane 1: carry {phase_rss['carry']:8.1f} MiB,"
            f" keys {phase_rss['keys']:8.1f} MiB, release {phase_rss['release']:8.1f} MiB",
            flush=True,
        )
        account(quotient, f"plane {position + 1}")
        mark = now
    if position + 1 in (100, PLANES) and position + 1 not in snapshots:
        snapshots[position + 1] = tracemalloc.take_snapshot()

stage(f"the carry over {len(carries)} planes")
if PLANES in snapshots and 100 in snapshots:
    print("[trace] the growth from plane 100 to the last plane, by allocating line", flush=True)
    for statistic in snapshots[PLANES].compare_to(snapshots[100], "lineno")[:15]:
        print(f"    {statistic}", flush=True)
    print("[trace] the same, by traceback", flush=True)
    for statistic in snapshots[PLANES].compare_to(snapshots[100], "traceback")[:6]:
        print(f"    {statistic.size_diff / 1024:10.1f} KiB  {statistic.count_diff:8d} allocs"
              f"  {statistic.traceback}", flush=True)
print(
    f"[probe] RESULT phase=carry planes={PLANES} carries={len(carries)}"
    f" carry_ms={1000 * sum(carries) / max(1, len(carries)):.3f}"
    f" keys_ms={1000 * sum(keys) / max(1, len(keys)):.3f}"
    f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB"
    f" traced={traced()[0]:.1f} MiB"
    f" phase_rss_carry={phase_rss['carry']:.1f} phase_rss_keys={phase_rss['keys']:.1f}"
    f" phase_rss_release={phase_rss['release']:.1f}",
    flush=True,
)
