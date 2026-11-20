r"""#381: is the divided-class key a function of the cusp, or of the process's state?

Two runs of the same measurement on this tree disagreed: 527 line cusps partitioned
into 444 keys with 24 ambiguous buckets in one probe, and into 351 keys with 104
ambiguous buckets in another.  The key is `_isotropic_line_image_key`, the
`rho(Gamma)`-orbit of the line's class pair (Dutour Sikiric--Hulek,
arXiv:2302.01679v2, Lemma 3.6, printed p. 22), and a key that is an invariant of
the subgroup's orbits cannot depend on what the process computed before it.  This
probe computes the partition twice in one process, before and after building
`im rho`, and compares.
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
quotient = subgroup.finite_character_quotient()

line_cusps = tuple(subgroup.cusps(1))
log(f"line cusps: {len(line_cusps)}")


def partition():
    buckets = {}
    for cusp in line_cusps:
        key = _isotropic_line_image_key(quotient, cusp.representative())
        buckets.setdefault(key, []).append(cusp)
    sizes = sorted((len(bucket) for bucket in buckets.values()), reverse=True)
    return buckets, sizes


buckets_before, sizes_before = partition()
log(
    f"before im rho: {len(buckets_before)} keys, "
    f"multi-cusp {sum(1 for size in sizes_before if size > 1)}, largest {sizes_before[:6]}"
)

engine, im_rho, _section, ambient = quotient._im_rho_engine_and_section()
log("im rho built")

buckets_after, sizes_after = partition()
log(
    f"after im rho:  {len(buckets_after)} keys, "
    f"multi-cusp {sum(1 for size in sizes_after if size > 1)}, largest {sizes_after[:6]}"
)

same_keys = set(buckets_before) == set(buckets_after)
log(f"the two key sets are equal: {same_keys}")
if same_keys:
    different = [key for key in buckets_before if len(buckets_before[key]) != len(buckets_after[key])]
    log(f"keys whose bucket size changed: {len(different)}")
log("done")
