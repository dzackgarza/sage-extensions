r"""#381: where the T_Co kernel row sits at this head, by periodic stack dumps."""

import faulthandler
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

lattice = rows._lattice_by_name("Tco")
subgroup = rows._row_subgroup(lattice, "Otilde")
log("subgroup built")
faulthandler.dump_traceback_later(30, repeat=True)
outcome = rows.run_row(lattice, subgroup, "Otilde", 240, "auto")
faulthandler.cancel_dump_traceback_later()
log(f"outcome: {outcome.report()}")
log("done")
