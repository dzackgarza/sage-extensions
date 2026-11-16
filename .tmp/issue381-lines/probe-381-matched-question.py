"""Probe: the one transporter question the keyed vertex still asks, at the cusp it names.

A keyed line vertex asks the cusp the finite image names one transporter
question, and that cusp's representative is not the line.  This probe builds the
`Otilde(T_Co)` line row, finds by divided class the cusp whose line is the same
line as one of a plane's, and times the question at it -- the question the
repair leaves, and the one the row's cost turns on.
"""
import os
import threading
import time

START = time.monotonic()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status", encoding="utf-8") as handle:
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

mark = time.monotonic()


def stage(label):
    global mark
    now = time.monotonic()
    print(f"    {now - mark:8.2f} s  {label}  rss {rss_mib():7.1f} MiB", flush=True)
    mark = now


lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
stage("Otilde")
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
domain = plane.inclusion().domain()
labels = tuple(domain.module_generating_set())
first = plane.inclusion()(domain.module_generator(labels[0]))
second = plane.inclusion()(domain.module_generator(labels[1]))
line = lattice.primitive_isotropic_subobject(first)
line_class = lattice.divided_discriminant_class(first)
stage("one plane and one of its lines")

representatives = tuple(subgroup.isotropic_orbit_representatives(1))
stage(f"the Otilde line row: {len(representatives)} lines")
cusp = None
for position, representative in enumerate(representatives):
    generator = representative.inclusion()(
        representative.inclusion().domain().module_generator(
            next(iter(representative.inclusion().domain().module_generating_set()))
        )
    )
    if lattice.divided_discriminant_class(generator) == line_class:
        cusp = _arithmetic_cusp(subgroup, representative)
        print(f"    the row's cusp of the plane's line is position {position}", flush=True)
        break
stage("the cusp of that divided class")
if cusp is None:
    raise SystemExit("no row representative carries the plane's line class")

began = time.monotonic()
witness = cusp.transporter_witness(line)
print(
    f"    the transporter question at that cusp: {time.monotonic() - began:8.3f} s, "
    f"carried {witness is not None}",
    flush=True,
)
stage("the question the repair leaves")
print(f"    peak rss {rss_mib():7.1f} MiB, elapsed {time.monotonic() - START:7.1f} s", flush=True)
