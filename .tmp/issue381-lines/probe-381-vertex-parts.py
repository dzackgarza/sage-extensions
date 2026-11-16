"""Probe: the parts of one line vertex on the Coble lattice, without the row.

A line vertex of the incidence costs, on the route it is repaired from, one
finite-image key of the line and one witness question at the cusps the key
names; the route it is repaired out of costs one witness question at every cusp
of the line row.  This probe measures those two unit costs on T_Co at one plane
the O(T_Co) row chooses, and the row size they are multiplied by, so the row's
line side is a number rather than an inference.
"""
import os
import threading
import time

START = time.monotonic()


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


def per_call(label, count, work):
    work()
    began = time.monotonic()
    for _ in range(count):
        work()
    elapsed = (time.monotonic() - began) / count
    print(f"    {label:52s} {elapsed * 1000:9.3f} ms per call", flush=True)


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
domain = plane.inclusion().domain()
labels = tuple(domain.module_generating_set())
first = plane.inclusion()(domain.module_generator(labels[0]))
second = plane.inclusion()(domain.module_generator(labels[1]))
lines = (
    lattice.primitive_isotropic_subobject(first),
    lattice.primitive_isotropic_subobject(first + second),
)
stage("one plane and two of its lines: a generator and the sum")

key = lambda line: frozenset(
    quotient.isotropic_class_orbit(_isotropic_line_class_points(lattice, line))
)
per_call("one finite-image key of a line", 20, lambda: key(lines[0]))
per_call("one finite-image key of the other line", 20, lambda: key(lines[1]))
print(f"    the two lines carry the same key: {key(lines[0]) == key(lines[1])}", flush=True)

cusps = tuple(_arithmetic_cusp(subgroup, line) for line in lines)
per_call(
    "one witness question at a cusp the line is in",
    3,
    lambda: cusps[0].transporter_witness(lines[0]),
)
per_call(
    "one witness question at a cusp the line is not in",
    3,
    lambda: cusps[1].transporter_witness(lines[0]),
)
per_call(
    "one separation question at that other cusp",
    3,
    lambda: quotient.invariant_separates_isotropic_orbits(lines[0], cusps[1].representative()),
)
stage("the parts")
print(f"    peak rss {rss_mib():7.1f} MiB, elapsed {time.monotonic() - START:7.1f} s", flush=True)
