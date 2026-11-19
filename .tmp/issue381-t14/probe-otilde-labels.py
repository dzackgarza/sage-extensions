r"""#381: Otilde's character labels and sign descent at T_Co, measured not inferred.

The two kernel rows differ in `_image_labels` -- `Otilde` cuts only `rho`,
`Otilde+` cuts `rho` and the real spinor norm -- and that is what decides whether
a sign sheet exists at all.  This probe reads the pair off the quotient instead
of inferring it from the subgroup's description.
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
log(f"lattice: rank {lattice.module_rank()}, signature {lattice.signature()}")
for label in ("Otilde", "Otilde+"):
    subgroup = rows._row_subgroup(lattice, label)
    quotient = subgroup.finite_character_quotient()
    log(f"{label}: index {quotient.index()}")
    log(f"{label}: _image_labels {list(quotient._image_labels)}")
    log(f"{label}: determinant_kernel {quotient.determinant_kernel}; spinor_kernel {quotient.spinor_kernel}")
    j, sign_labels = quotient._sign_descent_rank()
    log(f"{label}: _sign_descent_rank() j={j}, labels={list(sign_labels)}")
log("done")
