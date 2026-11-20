r"""#381: is the ambient generating family of O(T_Co) the same in two processes?

The two seeded rows hold almost disjoint sets of line spans (480 and 520 of 527
exclusive), so the *transports* differ, not their order.  Every transport is a
lift spelled from the ambient generating family `ambient = tuple(O(L).group_generators())`
(`_ambient_generators`), and the walk's letters index that family.  If the family
differs between processes, every spelled lift differs and so does every
transported line.  This probe dumps the family itself in both processes.
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

    lattice = rows._lattice_by_name("Tco")
    family = tuple(lattice.Aut().group_generators())
    entries = [repr(rows._coordinates(g)) if False else repr(g) for g in family]
    return {"count": len(entries), "entries": entries}


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
    print(f"generator counts: {left['count']} and {right['count']}")
    print(f"ordered families equal: {left['entries'] == right['entries']}")
    print(f"families equal as sets: {set(left['entries']) == set(right['entries'])}")
    print(f"  first differing position: {next((i for i, (a, b) in enumerate(zip(left['entries'], right['entries'], strict=False)) if a != b), None)}")
    if left["count"] == right["count"]:
        print(f"  entries differing: {sum(1 for a, b in zip(left['entries'], right['entries'], strict=True) if a != b)}")
print("done")
