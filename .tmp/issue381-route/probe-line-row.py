r"""Probe: the kernel line row (`cusps(1)`) of Otilde(T_Co), measured on its own.

`tits_building_incidence` computes `self.cusps(1)` before it walks anything, so
the line row is the row's first phase and every earlier record of the row was
cut before it returned.  This probe calls it and samples VmRSS: the row's time,
its growth, and whether it returns at all inside the launcher's wall.
"""
import os
import time

START = time.monotonic()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


from sage_extensions.all import *  # noqa: F401,F403

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] T_Co and Otilde(T_Co)", flush=True)
line_cusps = subgroup.cusps(1)
print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] the line row returned: "
      f"{line_cusps.cardinality()} cusps", flush=True)
print(f"[RESULT] line_cusps={line_cusps.cardinality()}"
      f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB", flush=True)
