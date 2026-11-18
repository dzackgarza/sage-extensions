"""Where the kernel incidence row's memory goes, phase by phase.

The driver's row does four things: the line row, the plane row, the covering
search, and the edge loop.  This runs the first two through the row's own
generators and the last two through the public call, printing resident bytes at
every boundary and every PROBE_EVERY planes, with a sampler thread that names
the frame the process is in.  The plane count is reported so that a coefficient
can be read off the curve.
"""

import os
import sys
import threading
import time
import traceback

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403

EVERY = int(os.environ.get("PROBE_EVERY", "10000"))
SAMPLE = float(os.environ.get("PROBE_SAMPLE", "20"))
start = time.monotonic()
clock = lambda: time.monotonic() - start  # noqa: E731


def rss_kib():
    return int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0])


def mark(what):
    print(f"[{clock():9.1f} s rss {rss_kib() / 1024:8.1f} MiB] {what}", flush=True)


def sampler():
    while True:
        time.sleep(SAMPLE)
        frames = sys._current_frames()
        where = []
        for thread in frames.values():
            stack = traceback.extract_stack(thread)
            if stack:
                frame = stack[-1]
                where.append(f"{os.path.basename(frame.filename)}:{frame.lineno} {frame.name}")
        print(f"[{clock():9.1f} s rss {rss_kib() / 1024:8.1f} MiB] {' | '.join(where[:3])}", flush=True)


mark("T_Co, Otilde(T_Co)")
lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
mark("the subgroup")
quotient = subgroup.finite_character_quotient()
mark("the character quotient")

line_start = time.monotonic()
mark(f"the line row: {int(subgroup.cusps(1).cardinality())} cusps in {time.monotonic() - line_start:.1f} s")

threading.Thread(target=sampler, daemon=True).start()

plane_start = time.monotonic()
walker = subgroup.cusps(2) if os.environ.get("PROBE_VIA_CALL") else None
mark("the plane row (the row the call reads)")
if walker is not None:
    mark(f"the plane row: {int(walker.cardinality())} cusps in {time.monotonic() - plane_start:.1f} s")
else:
    from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
    from sage_extensions.categories.orthogonal_quotients import (
        _yield_subgroup_isotropic_orbit_representatives,
    )

    row = []
    samples = []
    for position, representative in enumerate(_yield_subgroup_isotropic_orbit_representatives(subgroup, 2)):
        row.append(_arithmetic_cusp(subgroup, representative))
        del representative
        if position and position % EVERY == 0:
            samples.append((position, rss_kib()))
            print(
                f"[{clock():9.1f} s rss {rss_kib() / 1024:8.1f} MiB] plane {position}: "
                f"{1000 * (time.monotonic() - plane_start) / position:.2f} ms a plane so far",
                flush=True,
            )
    mark(f"the plane row: {len(row)} cusps in {time.monotonic() - plane_start:.1f} s")
    for (p0, r0), (p1, r1) in zip(samples, samples[1:]):
        print(f"  planes {p0}->{p1}: {(r1 - r0) / (p1 - p0):.1f} KiB a plane", flush=True)

mark("the incidence call")
call_start = time.monotonic()
incidences = tuple(subgroup.tits_building_incidence_by_divided_classes())
mark(f"the incidence call returned {len(incidences)} edges in {time.monotonic() - call_start:.1f} s")
