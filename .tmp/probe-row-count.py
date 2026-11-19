r"""#381: the Otilde row at T_Co at this head, and how many lines the walk visits."""

import importlib.util
import sys
import time

sys.path.insert(0, "tests")
START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


import sage_extensions.categories.isotropic_orbits as orbits

visited = {"lines": 0, "planes_calls": 0}
original = orbits._planes_through_line


def counting(lattice, line, completion):
    visited["planes_calls"] += 1
    result = original(lattice, line, completion)
    return result


orbits._planes_through_line = counting

spec = importlib.util.spec_from_file_location("rows", "tests/coble_gamma_co_2_incidence_rows.py")
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)

lattice = rows._lattice_by_name("Tco")
subgroup = rows._row_subgroup(lattice, "Otilde")
started = time.perf_counter()
outcome = rows.run_row(lattice, subgroup, "Otilde", 600, "auto")
log(f"outcome: {outcome.report()}  [{time.perf_counter() - started:.2f}s]")
log(f"lines visited (planes-through-a-line calls): {visited['planes_calls']}")
log("done")
