r"""#381: the Otilde row at T_Co with its cap, and the transporter route it exercises."""

import importlib.util
import sys
import time

sys.path.insert(0, "tests")
START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}")


spec = importlib.util.spec_from_file_location("rows", "tests/coble_gamma_co_2_incidence_rows.py")
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)

lattice = rows._lattice_by_name("Tco")
log(f"lattice: rank {lattice.module_rank()}, signature {lattice.signature()}")
subgroup = rows._row_subgroup(lattice, "Otilde")
log(f"subgroup built: {subgroup}")
outcome = rows.run_row(lattice, subgroup, "Otilde", 600, "auto")
log(f"outcome: {outcome.report()}")
quotient = subgroup.finite_character_quotient()
log(f"registered transports: {len(quotient._transported_isotropic_objects)}")
log("done")
