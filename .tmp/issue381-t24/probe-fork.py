r"""#381: does the process change the anchor, the key set, or only the multiplicities?

Two seeds partition `Otilde`'s 527 line cusps of `T_Co` differently.  The
divergence has three possible seats, and they are separated by dumping, per
process, the anchor the walk starts from (the drawn ambient line), the set of
distinct keys, and the multiplicities.
"""

import importlib.util
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "tests")

CHILD = len(sys.argv) > 1


def dump():
    spec = importlib.util.spec_from_file_location(
        "rows", "tests/coble_gamma_co_2_incidence_rows.py"
    )
    rows = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rows)
    from sage_extensions.categories.orthogonal_quotients import _isotropic_line_image_key

    lattice = rows._lattice_by_name("Tco")
    subgroup = rows._row_subgroup(lattice, "Otilde")
    ambient = lattice.Aut()
    drawn = tuple(ambient.isotropic_orbit_representatives(1))[0]
    anchor = repr(rows._coordinates(drawn))
    quotient = subgroup.finite_character_quotient()
    counts = {}
    for cusp in subgroup.cusps(1):
        key = repr(sorted(_isotropic_line_image_key(quotient, cusp.representative())))
        counts[key] = counts.get(key, 0) + 1
    return {
        "anchor": anchor,
        "distinct": sorted(counts),
        "multiplicities": sorted(counts.values(), reverse=True),
    }


if CHILD:
    print(json.dumps(dump()))
    sys.exit(0)

answers = {}
for seed in ("0", "1"):
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = seed
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, __file__, "child"], capture_output=True, text=True, env=environment
    )
    print(f"[{time.perf_counter() - started:8.2f}s] seed {seed}: rc {completed.returncode}", flush=True)
    if completed.returncode != 0:
        print(completed.stderr[-800:], flush=True)
    answers[seed] = json.loads(completed.stdout) if completed.returncode == 0 else None

if answers["0"] and answers["1"]:
    left, right = answers["0"], answers["1"]
    print(f"anchor equal: {left['anchor'] == right['anchor']}")
    print(f"  seed 0 anchor {left['anchor'][:90]}")
    print(f"  seed 1 anchor {right['anchor'][:90]}")
    print(f"distinct key sets equal: {left['distinct'] == right['distinct']}")
    print(f"distinct counts: {len(left['distinct'])} vs {len(right['distinct'])}")
    print(f"multiplicities equal: {left['multiplicities'] == right['multiplicities']}")
print("done")
