r"""#381: does a kernel row have a character quotient, and does it populate the lift registry?"""

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

for name in ("U+U(2)+<-2>", "U+U(2)+<-4>"):
    lattice = rows._lattice_by_name(name)
    log(f"lattice {name}: rank {lattice.module_rank()}, disc form {lattice.discriminant_group().cardinality()}")
    for label in ("Otilde", "Otilde+"):
        subgroup = rows._row_subgroup(lattice, label)
        log(f"  {label}: subgroup {subgroup}")
        try:
            quotient = subgroup.finite_character_quotient()
        except Exception as error:
            log(f"  {label}: no character quotient ({type(error).__name__})")
            continue
        log(f"  {label}: quotient {quotient} of index {quotient.index()}")
        outcome = rows.run_row(lattice, subgroup, label, 300, "auto")
        log(f"  {label}: row outcome {outcome.report()}")
        registry = quotient.__dict__.get("_isotropic_lift_registry", {})
        log(f"  {label}: registered spans {len(registry)}")
        families = {id(record[1]): record for record in registry.values()}
        log(f"  {label}: distinct source families {len(families)}")
log("done")
