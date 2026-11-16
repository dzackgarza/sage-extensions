"""#570: the Otilde(T_Co) line row, and the coordinates of the named cusp.

The row is how the named specimen is found: the cusp at position 215 of 527 is the
one carrying the divided class of a plane's own line.  This probe builds the row,
prints every representative's lattice coordinates and divided class, and names the
positions that carry the plane's line's class, so the computation probe can rebuild
that line without paying for the row again.
"""
import os
import time

START = time.monotonic()


def rss_mib():
    for line in open(f"/proc/{os.getpid()}/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return float("nan")


LAST = [START]


def stage(label, detail=""):
    now = time.monotonic()
    print(f"[t={now - START:8.2f}s | {now - LAST[0]:8.2f}s] {label}{detail}  rss={rss_mib():.0f} MiB", flush=True)
    LAST[0] = now


from sage_extensions.all import *  # noqa: F401,F403


def coordinates(lattice, term):
    inclusion = term.inclusion()
    domain = inclusion.domain()
    vector = inclusion(domain.module_generator(next(iter(domain.module_generating_set()))))
    labels = tuple(lattice.module_generating_set())
    readings = {str(label): int(vector.to_vector()(label)) for label in labels}
    return {label: value for label, value in readings.items() if value}


lattice = NamedLattices.Tco
stage("lattice", f" {lattice} rank {lattice.module_rank()}")
subgroup = lattice.stable_orthogonal_group()
stage("Otilde(T_Co)")

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
plane_line_class = lattice.divided_discriminant_class(first)
stage("the plane and its line's divided class", f" {plane_line_class}")

representatives = tuple(subgroup.isotropic_orbit_representatives(1))
stage("the Otilde line row", f" {len(representatives)} representatives")

for position, representative in enumerate(representatives):
    print(f"ROW {position} {coordinates(lattice, representative)} "
          f"class={lattice.divided_discriminant_class(representative.inclusion()(representative.inclusion().domain().module_generator(next(iter(representative.inclusion().domain().module_generating_set())))))}",
          flush=True)
stage("printed the row")
print(f"the plane's line class is {plane_line_class}", flush=True)
print(f"total {time.monotonic() - START:.1f} s", flush=True)
