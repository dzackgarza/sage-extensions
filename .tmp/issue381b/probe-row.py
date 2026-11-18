"""One kernel incidence row of T_Co through the driver, with its stages and its resident set logged.

The driver is called as the run calls it (``main``, with the same flags), and two counters are
wrapped around the library's own steps so that the resident set is recorded every 10 000 planes
of the split and every 10 000 records of the relation.  Nothing else is changed and no source is
edited.
"""

import os
import sys
import time

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.isotropic_orbits as isotropic_orbits  # noqa: E402
import sage_extensions.categories.orthogonal_quotients as orthogonal_quotients  # noqa: E402

import coble_gamma_co_2_incidence_rows as driver  # noqa: E402

ROW = os.environ.get("PROBE_ROW", "Otilde")
EVERY = int(os.environ.get("PROBE_EVERY", "10000"))
start = time.monotonic()
clock = lambda: time.monotonic() - start  # noqa: E731


def rss_mib():
    return int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0]) / 1024


def mark(what):
    print(f"[{clock():9.1f} s rss {rss_mib():8.1f} MiB] {what}", flush=True)


planes = [0]
records = [0]
original_register = orthogonal_quotients.OrthogonalCharacterQuotient.register_isotropic_lift
original_init = isotropic_orbits.DividedClassCuspIncidence.__init__


def counting_register(self, plane, lift, generators, image):
    answer = original_register(self, plane, lift, generators, image)
    planes[0] += 1
    if planes[0] % EVERY == 0:
        mark(f"the split: {planes[0]} planes registered")
    return answer


def counting_init(self, subgroup, line_cusp, plane_cusp, divided_classes):
    original_init(self, subgroup, line_cusp, plane_cusp, divided_classes)
    records[0] += 1
    if records[0] % EVERY == 0:
        mark(f"the relation: {records[0]} records")


orthogonal_quotients.OrthogonalCharacterQuotient.register_isotropic_lift = counting_register
isotropic_orbits.DividedClassCuspIncidence.__init__ = counting_init

mark(f"{ROW}: the driver's own row")
outcome = driver.main(
    [
        "--rows", ROW,
        "--lattice", "Tco",
        "--route", os.environ.get("PROBE_ROUTE", "divided-class"),
        "--cap", os.environ.get("PROBE_CAP", "10800"),
        "--budget", os.environ.get("PROBE_BUDGET", "28800"),
    ]
)
mark(f"the driver returned {outcome!r}")
print(f"[{clock():9.1f} s rss {rss_mib():8.1f} MiB] done: {planes[0]} planes, {records[0]} records")
