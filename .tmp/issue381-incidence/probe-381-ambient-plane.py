"""Probe: the ambient O(T_Co) plane row, its representative, and its parabolic."""
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
        time.sleep(5)


threading.Thread(target=sample, daemon=True).start()

from sage_extensions.all import *  # noqa: F401,F403

mark = time.monotonic()


def stage(label):
    global mark
    now = time.monotonic()
    print(f"    {now - mark:8.2f} s  {label}  rss {rss_mib():7.1f} MiB", flush=True)
    mark = now


lattice = NamedLattices.Tco
group = lattice.Aut()
stage("O(T_Co)")
labels = tuple(lattice.module_generating_set())
planes = tuple(group.isotropic_orbit_representatives(2))
stage(f"ambient plane row: {len(planes)} orbits")
for position, plane in enumerate(planes):
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    rows = [
        tuple(int(inclusion(domain.module_generator(label)).to_vector()(other)) for other in labels)
        for label in domain.module_generating_set()
    ]
    print(f"  plane {position}: {rows} gram {plane.gram_tensor().entries()}", flush=True)
plane = planes[0]
print(f"  parabolic complete: {plane.is_parabolic_complete()}", flush=True)
stage("is_parabolic_complete")
family = tuple(plane.parabolic_stabilizer_generators())
stage(f"parabolic generators {len(family)}")
print(f"  index of the parabolic image: {group.finite_character_quotient().index()}", flush=True)
stage("quotient index")
