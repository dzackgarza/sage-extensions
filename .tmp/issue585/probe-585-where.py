r"""Probe: the structure that holds the walk's per-plane retention, by entry count and size.

The traced slice (``probe-585-instrument.py``) leaves the retention outside the
quotient: the quotient's own containers are flat while the process grows 300 KB a
plane.  This slice accounts the same walk on the other two objects it calls --
the lattice, whose ``primitive_isotropic_subobject`` is a cached constructor, and
the ambient group -- printing at each sample the entry count and the shallow size
of every container each of them holds, the traced total, and the resident set.
``PROBE_CLEAR=1`` drops the lattice's constructor cache after every plane, which
is the same walk with that one structure emptied: the difference between the two
runs is what that structure retains.
"""

import gc
import os
import sys
import threading
import time
import tracemalloc

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "1000"))
CLEAR = os.environ.get("PROBE_CLEAR", "0") == "1"

SUBOBJECT_CACHE = "_cache__primitive_isotropic_subobject"


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


def shallow(value):
    total = sys.getsizeof(value, 0)
    if isinstance(value, dict):
        for key, item in value.items():
            total += sys.getsizeof(key, 0) + sys.getsizeof(item, 0)
    return total


def account(target, label):
    rows = []
    for name, value in list(vars(target).items()):
        if isinstance(value, (dict, list, set, frozenset, tuple)):
            rows.append((shallow(value), len(value), type(value).__name__, name))
    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)
    print(f"[where {label}] {type(target).__name__}: {len(rows)} containers, {total / 1024:9.1f} KiB shallow", flush=True)
    for size, entries, kind, name in rows[:6]:
        print(f"    {size / 1024:10.1f} KiB  {entries:9d}  {kind:9s} {name}", flush=True)
    return total


lattice = NamedLattices.Tco
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
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

print(f"[probe] PROBE_CLEAR={CLEAR}", flush=True)
print(
    f"[probe] the lattice's cached-method caches: "
    f"{sorted((name, len(vars(lattice)[name])) for name in vars(lattice) if name.startswith('_cache__'))}",
    flush=True,
)
for target, label in ((quotient, "quotient"), (lattice, "lattice"), (subgroup, "subgroup")):
    account(target, f"before the walk, {label}")
cache = vars(lattice)[SUBOBJECT_CACHE]
print(f"[probe] the lattice's subobject cache at the start: {len(cache)} entries, {shallow(cache) / 1024:.1f} KiB", flush=True)

tracemalloc.start(4)
start_entries = len(cache)
start_size = shallow(cache)
band = max(1, PLANES // 10)
mark = time.monotonic()
carries = []
keys = []
for position in range(1, PLANES):
    carry_start = time.monotonic()
    carried = quotient.transport_covering(lifts[0], covering, lifts[position])
    carry_done = time.monotonic()
    lines = [flag.terms()[0] for flag in carried]
    for line in lines:
        _isotropic_line_image_key(quotient, line)
    keys_done = time.monotonic()
    quotient.release_isotropic_transports(lines)
    carries.append(carry_done - carry_start)
    keys.append(keys_done - carry_done)
    if CLEAR:
        cache.clear()
    if position < 10 or (position + 1) % band == 0 or position + 1 == PLANES:
        now = time.monotonic()
        steps = 1 if position == 1 else min(band, position - 1)
        called = 1000 * sum(carries[-steps:]) / steps
        keyed = 1000 * sum(keys[-steps:]) / steps
        current = tracemalloc.get_traced_memory()[0] / 1024 / 1024
        print(
            f"  [plane {position + 1:6d}/{PLANES}] carry {called:8.3f} ms and keys {keyed:8.3f} ms a plane"
            f"  rss {rss_mib():8.1f} MiB  traced {current:8.1f} MiB"
            f"  subobjects {len(cache):7d} (+{len(cache) - start_entries:7d})"
            f" {shallow(cache) / 1024:9.1f} KiB (+{(shallow(cache) - start_size) / 1024:8.1f})",
            flush=True,
        )
        if (position + 1) % (10 * band) == 0:
            for target, label in ((quotient, "quotient"), (lattice, "lattice"), (subgroup, "subgroup")):
                account(target, f"plane {position + 1}, {label}")
        mark = now
stage(f"the carry over {len(carries)} planes")
print(
    f"[probe] RESULT phase=where planes={PLANES} clear={int(CLEAR)}"
    f" carry_ms={1000 * sum(carries) / max(1, len(carries)):.3f} keys_ms={1000 * sum(keys) / max(1, len(keys)):.3f}"
    f" subobjects={len(cache)} added={len(cache) - start_entries} wall={time.monotonic() - START:.1f} s"
    f" rss={rss_mib():.1f} MiB traced={tracemalloc.get_traced_memory()[0] / 1024 / 1024:.1f} MiB",
    flush=True,
)
