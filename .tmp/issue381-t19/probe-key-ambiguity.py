r"""#381: which lattices the gate can afford have an ambiguous line-cusp key?

The divided-class read raises when the key of a carried line names more than one
line cusp, and the key is `_isotropic_line_image_key` -- the `rho(Gamma)`-orbit of
the line's class pair, an invariant of the subgroup's orbits (Dutour
Sikiric--Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  At `T_Co` 24 of
444 keys name 2 to 15 cusps.  This probe asks whether any lattice the gate can
afford shows the same, which is what a red test of a finer invariant would need.
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

for name in ("6JRS", "U+U(2)+<-2>", "U+U(2)+<-4>", "U+U+<-4>"):
    lattice = rows._lattice_by_name(name)
    for label in ("Otilde", "Otilde+"):
        subgroup = rows._row_subgroup(lattice, label)
        line_cusps = tuple(subgroup.cusps(1))
        quotient = subgroup.finite_character_quotient()
        buckets = {}
        for cusp in line_cusps:
            key = _isotropic_line_image_key(quotient, cusp.representative())
            buckets.setdefault(key, []).append(cusp)
        sizes = sorted((len(bucket) for bucket in buckets.values()), reverse=True)
        log(
            f"{name} {label}: {len(line_cusps)} line cusps, {len(buckets)} keys, "
            f"multi-cusp keys {sum(1 for size in sizes if size > 1)}, largest {sizes[:5]}"
        )
log("done")
