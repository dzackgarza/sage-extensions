"""Probe: which part of the line-cusp scan is the cost.

`matching_cusps` asks each cusp of a row two questions: whether the term is in
the cusp's universe, and whether the cusp has a transporter for it.  This probe
times the two separately on the Coble lattice, and the scan of a short prefix
of the row, so that the row's per-flag cost is a sum of measured parts.
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
line = lattice.primitive_isotropic_subobject(first)
stage("one plane and one of its lines")

reps = tuple(subgroup.isotropic_orbit_representatives(1))
stage(f"the Otilde line row: {len(reps)} lines")
cusps = tuple(subgroup.cusps(1))
stage(f"{len(cusps)} line cusps")

universe = cusps[0].universe()
per_call("cusp.universe()", 5, lambda: cusps[0].universe())
per_call("one universe membership", 5, lambda: line in universe)
per_call("one universe membership, another cusp", 5, lambda: line in cusps[1].universe())
per_call("one transporter witness", 3, lambda: cusps[0].transporter_witness(line))

prefix = 20
began = time.monotonic()
for cusp in cusps[:prefix]:
    if line not in cusp.universe():
        continue
    cusp.transporter_witness(line)
print(
    f"    the scan's two questions over {prefix} cusps: "
    f"{(time.monotonic() - began) / prefix * 1000:9.3f} ms per cusp",
    flush=True,
)
stage("the parts")
