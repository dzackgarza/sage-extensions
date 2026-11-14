r"""Time ``import sage_extensions.all`` after ``sage.all``, as the suite gate does.

    /sage/.venv/bin/python -u .scratch/issue468-import-time.py [runs]

The ceiling is ``STAR_IMPORT_CEILING`` = 3.0 s (sage_extensions.testing.suite_budget).
Each measurement is a fresh process, so no measurement warms the next.
"""

import subprocess
import sys
import time

if len(sys.argv) > 1 and sys.argv[1] == "child":
    import sage.all  # noqa: F401  (Sage's own load is outside the measured workload)

    start = time.perf_counter()
    import sage_extensions.all  # noqa: F401

    print(f"{time.perf_counter() - start:.3f}")
    raise SystemExit(0)

runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
times = []
for _ in range(runs):
    done = subprocess.run(
        [sys.executable, __file__, "child"], capture_output=True, text=True, check=True
    )
    times.append(float(done.stdout.strip()))
print(f"star import, {runs} fresh processes: {', '.join(f'{t:.3f}' for t in times)} s")
print(f"max {max(times):.3f} s against the 3.0 s ceiling")
