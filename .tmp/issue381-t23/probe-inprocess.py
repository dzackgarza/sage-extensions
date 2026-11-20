r"""#381: is the key partition unstable inside one process too?

A lint-compliant test may not import anything but the session (TL01), so it
cannot spawn subprocesses; if the partition is stable within a process, no test
in the suite can express the defect.  This probe computes the partition twice in
one process -- clearing the cusp cache and building the character image between
the runs -- and compares the partitions, not merely their counts.
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
subgroup = rows._row_subgroup(lattice, "Otilde")


def partition(note):
    started = time.perf_counter()
    line_cusps = tuple(subgroup.cusps(1))
    quotient = subgroup.finite_character_quotient()
    buckets = {}
    for cusp in line_cusps:
        key = _isotropic_line_image_key(quotient, cusp.representative())
        buckets[key] = buckets.get(key, 0) + 1
    sizes = sorted(buckets.values(), reverse=True)
    log(
        f"{note}: {len(line_cusps)} cusps, {len(buckets)} keys, "
        f"multi {sum(1 for size in sizes if size > 1)}, largest {sizes[:6]} "
        f"({time.perf_counter() - started:.2f} s)"
    )
    return buckets, {repr(rows._coordinates(cusp.representative())) for cusp in line_cusps}


first_buckets, first_spans = partition("run 1")

subgroup.cusps.clear_cache()
quotient = subgroup.finite_character_quotient()
quotient._im_rho_engine_and_section()
log("cache cleared, character image built")

second_buckets, second_spans = partition("run 2")

log(f"partitions equal: {first_buckets == second_buckets}")
log(f"span sets equal: {first_spans == second_spans}")
log("done")
