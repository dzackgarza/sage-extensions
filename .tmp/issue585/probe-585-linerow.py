r"""Probe: is the T_Co line cusp row affordable, so the edges can be compared on it?

The kernel incidence's line vertices are the row ``cusps(1)``.  The class route
needs that row (it is what the finite image indexes), and so does the edge-set
comparison.  This probe builds the row alone, on ``Otilde(T_Co)``, and prints
which stage it is in.
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
        time.sleep(10.0)
        print(f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB", flush=True)


threading.Thread(target=sample, daemon=True).start()

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.orthogonal_quotients import _isotropic_line_image_key

MARK = time.monotonic()


def stage(label):
    global MARK
    now = time.monotonic()
    print(f"    {now - MARK:9.2f} s  {label}  rss {rss_mib():8.1f} MiB", flush=True)
    MARK = now


lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
stage("Otilde(T_Co)")
quotient = subgroup.finite_character_quotient()
stage("its character quotient")

lines = subgroup.cusps(1)
stage(f"the line cusp row")
print(f"[probe] the line row: {lines.cardinality()} cusps  rss {rss_mib():.1f} MiB", flush=True)

keys = {}
for cusp in tuple(lines):
    key = _isotropic_line_image_key(quotient, cusp.representative())
    keys.setdefault(key, 0)
    keys[key] += 1
stage("the row's keys")
sizes = sorted(keys.values())
print(f"[probe] RESULT cusps={lines.cardinality()} keys={len(keys)} bucket sizes={sizes}"
      f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB", flush=True)
