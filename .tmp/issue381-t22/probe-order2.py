r"""#381: does the line walk fail when `im rho` is built before the cusps are asked?

The first attempt compared two "fresh" subgroups, but `_row_subgroup` answers with
a unique parent, so the second `cusps(1)` was a cache hit.  This probe clears the
cusp cache between the runs and forces the character image in between, so the
second run genuinely recomputes with `im rho` already built.
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

lattice = rows._lattice_by_name("Tco")
subgroup = rows._row_subgroup(lattice, "Otilde")


def attempt(note):
    started = time.perf_counter()
    try:
        cusps = tuple(subgroup.cusps(1))
        log(f"{note}: OK, {len(cusps)} line cusps in {time.perf_counter() - started:.2f} s")
    except Exception as error:  # noqa: BLE001 - the failure is the measurement
        log(f"{note}: RAISED {type(error).__name__}: {error}")


attempt("run 1, nothing built")

subgroup.cusps.clear_cache()
quotient = subgroup.finite_character_quotient()
engine, im_rho, _section, ambient = quotient._im_rho_engine_and_section()
log("character image built")

attempt("run 2, after the character image")
log("done")
