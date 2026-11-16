"""Probe: what the one cusp question a keyed vertex still asks costs.

`matching_cusps` asks a cusp two questions of a term: whether the term is in the
cusp's universe, and whether the cusp carries it.  The index answers the second
at one cusp; the first is still asked of that cusp at every line.  This probe
times the universe question alone, on T_Co, at a cusp of the line row asked
about a line that is no representative of it -- which is what a flag's line is.
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
    print(f"    {label:52s} {(time.monotonic() - began) / count * 1000:9.3f} ms per call", flush=True)


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
one_line = lattice.primitive_isotropic_subobject(first)
other_line = lattice.primitive_isotropic_subobject(first + second)
cusp = _arithmetic_cusp(subgroup, one_line)
stage("a plane, two of its lines, and the cusp of the first")

per_call("cusp.universe()", 5, lambda: cusp.universe())
per_call("the cusp's own representative in its universe", 5, lambda: one_line in cusp.universe())
per_call("the plane's other line in that universe", 5, lambda: other_line in cusp.universe())
per_call("the other line's transporter question at the cusp", 3, lambda: cusp.transporter_witness(other_line))
stage("the parts")
print(f"    peak rss {rss_mib():7.1f} MiB, elapsed {time.monotonic() - START:7.1f} s", flush=True)
