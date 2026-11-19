r"""#381: the Otilde+ line row of T_Co -- how many cusps, and how the keys collide.

`Otilde+`'s row raised at its first edge: the line of a covering flag lay in four
of its line cusps, so the divided-class key did not name one vertex.  The key is
`_isotropic_line_image_key`, the `rho(Gamma)`-orbit of the line's class pair --
an invariant of the subgroup's orbits (Dutour Sikiric--Hulek, Lemma 3.6, p. 22).
This probe counts the row's line cusps and buckets them by that key.
"""

import importlib.util
import sys
import time

sys.path.insert(0, "tests")
START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


spec = importlib.util.spec_from_file_location("rows", "tests/coble_gamma_co_2_incidence_rows.py")
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)

from sage_extensions.categories.orthogonal_quotients import _isotropic_line_image_key

lattice = rows._lattice_by_name("Tco")
log(f"lattice: rank {lattice.module_rank()}, signature {lattice.signature()}")

for label in ("Otilde", "Otilde+"):
    started = time.perf_counter()
    subgroup = rows._row_subgroup(lattice, label)
    line_cusps = tuple(subgroup.cusps(1))
    log(f"{label}: {len(line_cusps)} line cusps in {time.perf_counter() - started:.2f} s")
    quotient = subgroup.finite_character_quotient()
    log(f"{label}: image labels {list(quotient._image_labels)}")
    buckets = {}
    started = time.perf_counter()
    for cusp in line_cusps:
        key = _isotropic_line_image_key(quotient, cusp.representative())
        buckets.setdefault(key, []).append(cusp)
    sizes = sorted((len(bucket) for bucket in buckets.values()), reverse=True)
    log(
        f"{label}: {len(buckets)} distinct keys in {time.perf_counter() - started:.2f} s; "
        f"largest buckets {sizes[:8]}; {sum(1 for size in sizes if size > 1)} keys name more than one cusp"
    )
log("done")
