r"""#404 probe: the kernel plane row step and ``check_row_count`` on ``U + U(2) + <-2>``.

The driver ``tests/coble_kernel_plane_rows.py`` is loaded as a module, not run
as a script, so the row step and the double-coset check it uses on ``T_Co``
run here on the gate lattice.  Nothing in the driver's own ``main`` is used:
its Coble lattice is replaced by the argument of ``run_row``.
"""

import importlib.util
import time

from sage_extensions.all import *  # noqa: F401,F403

DRIVER = "/repos/sage-extensions/tests/coble_kernel_plane_rows.py"

spec = importlib.util.spec_from_file_location("coble_kernel_plane_rows", DRIVER)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)

lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
print(f"lattice of rank {lattice.module_rank()}", flush=True)
stable = lattice.stable_orthogonal_group()
counts = {}
for label, subgroup in (
    ("Otilde", stable),
    ("Otilde+", stable.intersection(lattice.O_plus())),
):
    started = time.monotonic()
    count, decided = driver.run_row(lattice, subgroup, label, 1200)
    print(f"[{label}] run_row -> count={count} decided={decided}", flush=True)
    if not decided:
        raise SystemExit(f"[{label}] the row step did not decide")
    equal = driver.check_row_count(lattice, subgroup, label, count)
    print(f"[{label}] check_row_count -> {equal} in {time.monotonic() - started:.1f} s", flush=True)
    if not equal:
        raise SystemExit(f"[{label}] the row does not equal its double cosets")
    counts[label] = count
if counts["Otilde+"] < counts["Otilde"]:
    raise SystemExit("the Otilde+ row has fewer planes than the Otilde row")
print(f"rows: Otilde={counts['Otilde']} Otilde+={counts['Otilde+']}", flush=True)
print("PROBE404 OK", flush=True)
