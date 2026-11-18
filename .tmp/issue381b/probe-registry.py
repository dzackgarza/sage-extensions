"""What a plane of a kernel plane row now leaves in the lift registry.

Draws the first ``PROBE_PLANES`` planes of ``Otilde(T_Co)``'s split exactly as the row does,
then measures what the registry retains: the resident set before and after the registry is
dropped, and the direct size of the words it keeps.  The same measurement on the parent --
the registry holding each plane's *product* -- is ``#599``'s 9.2 KiB an entry
(``attribution.log``), taken with the same drop and the same runtime.
"""

import gc
import os
import sys
import time

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.isotropic_orbits as isotropic_orbits  # noqa: E402

from coble_gamma_co_2_incidence_rows import (  # noqa: E402
    _lattice_by_name,
    _row_subgroup,
)

ROW = os.environ.get("PROBE_ROW", "Otilde")
PLANES = int(os.environ.get("PROBE_PLANES", "200"))
start = time.monotonic()
clock = lambda: time.monotonic() - start  # noqa: E731


def rss_mib():
    return int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0]) / 1024


def mark(what):
    print(f"[{clock():9.1f} s rss {rss_mib():8.1f} MiB] {what}", flush=True)


lattice = _lattice_by_name("Tco")
subgroup = _row_subgroup(lattice, ROW)
quotient = subgroup.finite_character_quotient()
mark(f"T_Co and the {ROW} row's subgroup")

from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp  # noqa: E402
from sage_extensions.categories.orthogonal_quotients import (  # noqa: E402
    _yield_subgroup_isotropic_orbit_representatives,
)

spans = []
draw_started = time.monotonic()
for position, plane in enumerate(
    _yield_subgroup_isotropic_orbit_representatives(subgroup, 2)
):
    spans.append(_arithmetic_cusp(subgroup, plane).span())
    if position + 1 >= PLANES:
        break
del plane
mark(f"the split: {len(spans)} planes drawn in {time.monotonic() - draw_started:.1f} s")

registry = quotient.__dict__.get("_isotropic_lift_registry", {})
mark(f"the registry holds {len(registry)} entries")

word_bytes = 0
image_entries = 0
for retained, family, image in registry.values():
    word_bytes += sys.getsizeof(retained)
    if isinstance(retained, tuple):
        for field in retained:
            word_bytes += sys.getsizeof(field)
    image_entries += 1
per_entry = word_bytes / max(1, len(registry))
print(
    f"  the words the registry keeps: {per_entry:.0f} B a plane "
    f"({word_bytes} B over {len(registry)} entries), beside {image_entries} finite elements",
    flush=True,
)

before = rss_mib()
gc.collect()
collected = rss_mib()
del registry
quotient.__dict__.pop("_isotropic_lift_registry", None)
for span in spans:
    del span
gc.collect()
after = rss_mib()
print(
    f"  resident before dropping the registry {before:.1f} MiB, after gc {collected:.1f} MiB, "
    f"after dropping it {after:.1f} MiB: {(before - after) * 1024 / max(1, PLANES):.0f} B a plane freed",
    flush=True,
)
mark("done")
