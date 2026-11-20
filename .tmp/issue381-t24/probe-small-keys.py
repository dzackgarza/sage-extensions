r"""#381: the smallest lattice whose line-cusp key partition depends on the hash seed.

The defect is that two processes under different `PYTHONHASHSEED` partition the
line cusps of `Otilde` at `T_Co` differently.  A regression test wants the
smallest lattice that shows it, so this probe runs the same partition in two
seeded children for every lattice the driver names below `Tco`, and for `Tco`.
"""

import importlib.util
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "tests")

CHILD = len(sys.argv) > 1

LATTICES = ("6JRS", "U+U(2)+<-2>", "U+U(2)+<-4>", "U+U+<-4>", "Tco")


def partition(name):
    spec = importlib.util.spec_from_file_location(
        "rows", "tests/coble_gamma_co_2_incidence_rows.py"
    )
    rows = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rows)
    from sage_extensions.categories.orthogonal_quotients import _isotropic_line_image_key

    lattice = rows._lattice_by_name(name)
    subgroup = rows._row_subgroup(lattice, "Otilde")
    line_cusps = tuple(subgroup.cusps(1))
    quotient = subgroup.finite_character_quotient()
    counts = {}
    for cusp in line_cusps:
        key = _isotropic_line_image_key(quotient, cusp.representative())
        counts[repr(sorted(key))] = counts.get(repr(sorted(key)), 0) + 1
    return {"cusps": len(line_cusps), "keys": sorted(counts.values(), reverse=True)}


if CHILD:
    print(json.dumps(partition(sys.argv[1])))
    sys.exit(0)

for name in LATTICES:
    answers = {}
    for seed in ("0", "1"):
        environment = dict(os.environ)
        environment["PYTHONHASHSEED"] = seed
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, __file__, name],
            capture_output=True,
            text=True,
            env=environment,
        )
        answers[seed] = json.loads(completed.stdout) if completed.returncode == 0 else None
        print(
            f"[{time.perf_counter() - started:8.2f}s] {name} seed {seed}: rc {completed.returncode} "
            f"{answers[seed]}",
            flush=True,
        )
        if completed.returncode != 0:
            print(completed.stderr[-600:], flush=True)
    if answers["0"] is not None and answers["1"] is not None:
        print(f"{name}: partitions equal {answers['0'] == answers['1']}", flush=True)
print("done")
