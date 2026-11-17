r"""Probe: how many cache decorators `src/` has, and how many key on an address.

An `id(...)`-keyed registry is sound only while the object at that address cannot
die, because the registry does not retain its key.  The count is the size of the
repair "hold the values weakly all the way down": each of them has to hold its
key objects, or be keyed on the objects themselves, before any of them may be
made weak.
"""

import pathlib
import re

DECORATOR = re.compile(r"@(cached_function|weak_cached_function|cached_method|cached_method_no_args)\b")


def main():
    total = 0
    keyed_by_id = 0
    sites = []
    for path in sorted(pathlib.Path("src").rglob("*.py")):
        lines = path.read_text().splitlines()
        for number, line in enumerate(lines):
            match = DECORATOR.search(line)
            if not match:
                continue
            total += 1
            block = "\n".join(lines[number : number + 12]).split("\ndef ")[0]
            if re.search(r"id\(", block):
                keyed_by_id += 1
                sites.append(f"{path}:{number + 1}")
    print(f"[probe] cache decorators under src/: {total}")
    print(f"[probe] of them keyed by id(...): {keyed_by_id}")
    for site in sites:
        print(f"  [id-keyed] {site}")


main()
