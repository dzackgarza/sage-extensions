r"""#381: does a row populate the lift registry, and how many planes does it hold?"""

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

lattice = rows._lattice_by_name("U+U(2)+<-2>")
log(f"lattice {lattice} of rank {lattice.module_rank()}")
subgroup = rows._row_subgroup(lattice, "O")
log(f"subgroup {subgroup}")
outcome = rows.run_row(lattice, subgroup, "O", 600, "auto")
log(f"row outcome: {outcome.report()}")
quotient = subgroup.finite_character_quotient()
registry = quotient.__dict__.get("_isotropic_lift_registry", {})
log(f"registered spans: {len(registry)}")
for span in list(registry)[:4]:
    record = registry[span]
    log(f"  entry of arity {len(record)}: retained {type(record[0]).__name__}, "
        f"family of {len(record[1])}, image {type(record[2]).__name__}")
log("done")
