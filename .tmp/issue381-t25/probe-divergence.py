r"""#381: the first divergence between the two seeded processes, and its kind.

Two processes under different `PYTHONHASHSEED` partition `Otilde`'s 527 line
cusps of `T_Co` differently, and their anchor is the same line with opposite
generators.  This probe dumps every cusp -- position, span, divided-class key --
in both processes and finds the first position where the two lists differ, then
asks whether the two dumps are the same set of objects (an order difference) or
not (different objects).
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
    quotient = subgroup.finite_character_quotient()
    entries = []
    for cusp in subgroup.cusps(1):
        line = cusp.representative()
        entries.append(
            [
                repr(rows._coordinates(line)),
                repr(sorted(_isotropic_line_image_key(quotient, line))),
            ]
        )
    return entries


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
    print(f"cusps: {len(left)} and {len(right)}")
    first = next(
        (index for index, (a, b) in enumerate(zip(left, right, strict=False)) if a != b),
        None,
    )
    print(f"first differing position: {first}")
    if first is not None:
        print(f"  seed 0: span {left[first][0][:90]} key {left[first][1][:70]}")
        print(f"  seed 1: span {right[first][0][:90]} key {right[first][1][:70]}")
        same_everywhere_before = left[:first] == right[:first]
        print(f"  prefixes equal: {same_everywhere_before}")
    left_spans = [entry[0] for entry in left]
    right_spans = [entry[0] for entry in right]
    print(f"span sets equal: {set(left_spans) == set(right_spans)}")
    print(f"  spans only in seed 0: {len(set(left_spans) - set(right_spans))}")
    print(f"  spans only in seed 1: {len(set(right_spans) - set(left_spans))}")
    left_keys = [entry[1] for entry in left]
    right_keys = [entry[1] for entry in right]
    print(f"key multisets equal: {sorted(left_keys) == sorted(right_keys)}")
print("done")
