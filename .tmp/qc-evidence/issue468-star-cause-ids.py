r"""Compare two trees' failed test ids for the 16 files of the #407/#408 causes (#468).

    python3 .scratch/issue468-cause-ids.py <base-runs-dir> <repair-runs-dir> <flipped.txt>

Each runs directory holds one JUnit xml per file, written by
``pytest --junit-xml=.tmp/causes468/<slug>.xml <file>`` in that tree.  The
comparison is at test-id level: a count cannot tell a repaired id from a newly
broken one.
"""

import pathlib
import sys
import xml.etree.ElementTree as ET


def outcomes(runs):
    out = {}
    for xml in sorted(pathlib.Path(runs).glob("*.xml")):
        for case in ET.parse(xml).getroot().iter("testcase"):
            key = f"{case.get('classname')}::{case.get('name')}"
            out[key] = tuple(
                sorted(c.tag for c in case if c.tag in ("failure", "error")
            )
            )
    return out


base, repair = outcomes(sys.argv[1]), outcomes(sys.argv[2])
red_base = {k for k, v in base.items() if v}
red_repair = {k for k, v in repair.items() if v}
print(f"base   : {len(base)} ids, {len(red_base)} red")
print(f"repair : {len(repair)} ids, {len(red_repair)} red")
print(f"same id set: {set(base) == set(repair)}")
print(f"green on base, red on the repair: {sorted(red_repair - red_base)}")
print(f"red on base, green on the repair: {sorted(red_base - red_repair)}")
print(
    "same failure kind for every shared red id: "
    f"{all(base[k] == repair[k] for k in red_base & red_repair)}"
)
flipped = [
    line.strip().replace("/", ".")
    for line in pathlib.Path(sys.argv[3]).read_text().splitlines()
    if line.strip()
]
print()
print(f"the {len(flipped)} ids of the two namespace causes, as recorded:")
print(f"  collected in the repair: {sum(1 for i in flipped if i in repair)}/{len(flipped)}")
print(f"  green in the repair    : {sum(1 for i in flipped if repair.get(i) == ())}")
print(f"  green on base          : {sum(1 for i in flipped if base.get(i) == ())}")
