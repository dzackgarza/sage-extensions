r"""#381: which of the two -- representatives or keys -- differs between processes?

The line-cusp key partition of `Otilde` at `T_Co` differs across processes: 444
distinct keys in one, 351 in another, and one run raised in the walk.  By the
theorem (`results/issue381-the-key-is-not-reproducible.md`) the partition is
determined, so either the representatives the cusp row admits vary, or the key
computed from a fixed representative varies.  This probe runs the same
computation in two child processes under different `PYTHONHASHSEED` values and
compares the two dumps line by line: span, then key.
"""

import importlib.util
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "tests")

CHILD = len(sys.argv) > 1


def partition():
    START = time.perf_counter()
    spec = importlib.util.spec_from_file_location(
        "rows", "tests/coble_gamma_co_2_incidence_rows.py"
    )
    rows = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rows)
    from sage_extensions.categories.orthogonal_quotients import _isotropic_line_image_key

    lattice = rows._lattice_by_name("Tco")
    subgroup = rows._row_subgroup(lattice, "Otilde")
    line_cusps = tuple(subgroup.cusps(1))
    quotient = subgroup.finite_character_quotient()
    entries = []
    for position, cusp in enumerate(line_cusps):
        line = cusp.representative()
        entries.append(
            {
                "position": position,
                "span": repr(rows._coordinates(line)),
                "key": repr(sorted(_isotropic_line_image_key(quotient, line))),
            }
        )
    print(
        f"[{time.perf_counter() - START:8.2f}s] {len(entries)} cusps",
        file=sys.stderr,
    )
    return entries


if CHILD:
    print(json.dumps(partition()))
    sys.exit(0)

dumps = {}
for seed in ("0", "1"):
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = seed
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, __file__, "child"],
        capture_output=True,
        text=True,
        env=environment,
    )
    print(f"[{time.perf_counter() - started:8.2f}s] seed {seed}: rc {completed.returncode}", flush=True)
    print(completed.stderr[-2000:], flush=True)
    dumps[seed] = json.loads(completed.stdout) if completed.returncode == 0 else None

if dumps["0"] is None or dumps["1"] is None:
    print("a child failed; nothing to compare")
    sys.exit(0)

left, right = dumps["0"], dumps["1"]
spans_differ = [i for i, (a, b) in enumerate(zip(left, right, strict=True)) if a["span"] != b["span"]]
keys_differ = [i for i, (a, b) in enumerate(zip(left, right, strict=True)) if a["key"] != b["key"]]
print(f"cusps: {len(left)} vs {len(right)}")
print(f"positions whose SPAN differs: {len(spans_differ)}; first {spans_differ[:3]}")
print(f"positions whose KEY differs:  {len(keys_differ)}; first {keys_differ[:3]}")
print(f"distinct keys: {len({entry['key'] for entry in left})} vs {len({entry['key'] for entry in right})}")
print("done")
