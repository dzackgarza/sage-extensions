r"""#381: the two kernel rows on the rank-five specimen, with their endpoint digest."""

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

lattice = rows._lattice_by_name("U+U(2)+<-2>")
log(f"lattice: rank {lattice.module_rank()}, signature {lattice.signature()}")
for label in ("Otilde", "Otilde+"):
    subgroup = rows._row_subgroup(lattice, label)
    outcome = rows.run_row(lattice, subgroup, label, 900, "auto")
    log(f"{label}: {outcome.report()}")
log("done")
