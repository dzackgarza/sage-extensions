r"""#381: the per-plane frame's own callees, at a cap that reaches it often enough."""

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
outcome = rows.run_row(lattice, subgroup, "Otilde", 120, "auto")
profile.disable()
log(f"outcome: {outcome.report()}")
stats = pstats.Stats(profile)
for frame in ("_iter_splitting_isometries_in_im_rho_from_image", "_im_rho_engine_and_section"):
    stream = io.StringIO()
    pstats.Stats(profile, stream=stream).sort_stats("cumulative").print_callees(frame)
    log(f"---- callees of {frame} ----")
    print(stream.getvalue())
log("done")
