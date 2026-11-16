"""Probe: one plane's lines on the Coble lattice, searched for and keyed.

The incidence identifies each flag's line term with a cusp of the line row by
asking every cusp for a transporter.  This probe builds one plane of the Coble
lattice, takes two of its lines -- one of its generators and the sum of the two,
neither of which is a chosen representative of the row -- and measures, for
each: the witness scan over the whole line row, and the finite-image key of the
line against the key of every cusp of the row.  It also prints how many
distinct keys the row carries, which is what decides whether a keyed lookup can
answer without the search.
"""
import os
import threading
import time

START = time.monotonic()
CAP = float(os.environ.get("PROBE_CAP", "500"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def sample():
    while True:
        print(f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB", flush=True)
        time.sleep(10)


threading.Thread(target=sample, daemon=True).start()

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
from sage_extensions.categories.orthogonal_quotients import (
    _isotropic_line_class_points,
)

mark = time.monotonic()


def stage(label):
    global mark
    now = time.monotonic()
    print(f"    {now - mark:8.2f} s  {label}  rss {rss_mib():7.1f} MiB", flush=True)
    mark = now


lattice = NamedLattices.Tco
stage("lattice")
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage(f"Otilde and its quotient, index {quotient.index()}")
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
stage("one plane, from the O(T_Co) row's own representative")
domain = plane.inclusion().domain()
labels = tuple(domain.module_generating_set())
first = plane.inclusion()(domain.module_generator(labels[0]))
second = plane.inclusion()(domain.module_generator(labels[1]))
lines = (
    lattice.primitive_isotropic_subobject(first),
    lattice.primitive_isotropic_subobject(first + second),
)
stage("two lines of that plane: a generator and the sum of the two")


def key_of(term):
    return frozenset(
        quotient.isotropic_class_orbit(_isotropic_line_class_points(lattice, term))
    )


line_reps = tuple(subgroup.isotropic_orbit_representatives(1))
stage(f"the Otilde line row: {len(line_reps)} line(s)")
line_cusps = tuple(_arithmetic_cusp(subgroup, representative) for representative in line_reps)
stage(f"{len(line_cusps)} line cusps built")

key_mark = time.monotonic()
keys = [key_of(cusp.representative()) for cusp in line_cusps]
print(
    f"    one line key (class pair and its orbit): "
    f"{(time.monotonic() - key_mark) / len(keys) * 1000:9.3f} ms per call",
    flush=True,
)
print(f"    distinct keys over the row: {len(set(keys))} of {len(keys)}", flush=True)
stage("the row's keys")


def witness_scan(term):
    found = []
    began = time.monotonic()
    for cusp in line_cusps:
        if term not in cusp.universe():
            continue
        witness = cusp.transporter_witness(term)
        if witness is not None:
            found.append(cusp)
    return time.monotonic() - began, found


for position, line in enumerate(lines):
    scan_seconds, matched = witness_scan(line)
    print(
        f"  line {position}: the witness scan over {len(line_cusps)} cusps took "
        f"{scan_seconds:8.3f} s and found {len(matched)}",
        flush=True,
    )
    key_mark = time.monotonic()
    key = key_of(line)
    key_seconds = time.monotonic() - key_mark
    bucket = [cusp for cusp, cusp_key in zip(line_cusps, keys, strict=True) if cusp_key == key]
    print(
        f"  line {position}: its key took {key_seconds * 1000:9.3f} ms, names "
        f"{len(bucket)} cusp(s), and holds the scanned cusp "
        f"{any(cusp is matched[0] for cusp in bucket) if matched else 'no scan match'}",
        flush=True,
    )
stage("the two lines")
print(f"    peak rss {rss_mib():7.1f} MiB, elapsed {time.monotonic() - START:7.1f} s", flush=True)
