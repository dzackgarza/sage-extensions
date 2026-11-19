r"""#381: the row under cProfile, which counts the nested torsor calls natively."""

import cProfile
import importlib.util
import io
import pstats
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
profile = cProfile.Profile()
profile.enable()
outcome = rows.run_row(lattice, subgroup, "Otilde", 60, "auto")
profile.disable()
log(f"outcome: {outcome.report()}")
stream = io.StringIO()
pstats.Stats(profile, stream=stream).sort_stats("cumulative").print_stats(30)
text = stream.getvalue()
print(text)
for line in text.splitlines():
    if "integral_parameter_classes" in line or "_integral_parameter_cosets" in line or "integral_members" in line:
        log(f"  {line.strip()}")
log("done")
