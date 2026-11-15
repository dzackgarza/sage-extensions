r"""#528: two profiles of the ambient plane row, compared function by function.

``issue528-row-profile.py`` writes one table per tree:

    # tree=<sha> seconds=<x> calib=<y> decided=<bool> rows=<n> calls=<n>
    <path inside the package>\t<lineno>\t<function>\t<own s>\t<cum s>\t<calls>

This script joins two of them on ``(path, function)`` -- never on the line
number, which moves when the function is edited -- and prints, for every
function, its own time and its call count at both trees, ranked twice: once by
the growth of own time, once by the growth of the call count.  Both are what
the slow-run triage asks for before a mechanism is named: a function whose
*time* grew at a constant call count is a dearer call; a function whose *count*
grew is more calls of the same price, and only the second one has a bisection
predicate (`git bisect run` on the count, which the load of a shared VM does
not move).

Usage::

    python3 issue528-row-profile-compare.py <base.tsv> <main.tsv>

Every printed section is evidence; nothing here decides anything.
"""

import sys

FLOOR = 0.02  # seconds of own time at either tree, below which a row is noise


def read(path):
    header = {}
    rows = {}
    with open(path) as handle:
        first = handle.readline()
        if not first.startswith("#"):
            raise SystemExit(f"{path}: no header line")
        for field in first[1:].split():
            if "=" in field:
                key, value = field.split("=", 1)
                header[key] = value
        for line in handle:
            if not line.strip():
                continue
            where, lineno, name, own, cum, calls = line.rstrip("\n").split("\t")
            key = (where, name)
            previous = rows.get(key, (0.0, 0.0, 0, set()))
            rows[key] = (
                previous[0] + float(own),
                previous[1] + float(cum),
                previous[2] + int(calls),
                previous[3] | {lineno},
            )
    return header, rows


def line_of(entry):
    return "/".join(sorted(entry[3], key=int))


def show(title, ordered, base, main):
    print("")
    print(title)
    print(
        f"  {'file:line':<50}{'function':<30}"
        f"{'base own':>9}{'main own':>9}{'delta':>9}"
        f"{'base calls':>11}{'main calls':>11}{'x calls':>9}"
    )
    for key, base_own, main_own, base_calls, main_calls in ordered:
        where, name = key
        lines = line_of(base.get(key, (0, 0, 0, set())) if key in base else main[key])
        ratio = (main_calls / base_calls) if base_calls else float("inf")
        print(
            f"  {(where + ':' + lines)[:49]:<50}{name[:29]:<30}"
            f"{base_own:>9.3f}{main_own:>9.3f}{main_own - base_own:>+9.3f}"
            f"{base_calls:>11}{main_calls:>11}{ratio:>9.2f}"
        )


def main(argv):
    if len(argv) != 2:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    base_header, base = read(argv[0])
    main_header, main = read(argv[1])
    for label, header in (("base", base_header), ("main", main_header)):
        print(
            f"{label}: tree {header.get('tree')} row {header.get('seconds')} s "
            f"calib {header.get('calib')} s decided {header.get('decided')} "
            f"{header.get('rows')} functions {header.get('calls')} calls"
        )
    if "False" in (base_header.get("decided"), main_header.get("decided")):
        print(
            "\nONE OF THE TABLES IS TRUNCATED (decided=False).  Its call counts are "
            "the calls that\ncompleted, not the row's, and are not comparable with the "
            "other tree's; only the\nper-call cost of an entry is readable, and the "
            "printed ranking says so below."
        )
    total_base = sum(value[0] for value in base.values())
    total_main = sum(value[0] for value in main.values())
    calls_base = sum(value[2] for value in base.values())
    calls_main = sum(value[2] for value in main.values())
    print(
        f"\nsum of own time over all functions: base {total_base:.1f} s, "
        f"main {total_main:.1f} s (the rows' own exclusive time)\n"
        f"sum of call counts:                base {calls_base}, main {calls_main} "
        f"({calls_main / calls_base:.2f}x)"
    )

    joined = []
    for key in set(base) | set(main):
        base_own, _, base_calls, _ = base.get(key, (0.0, 0.0, 0, set()))
        main_own, _, main_calls, _ = main.get(key, (0.0, 0.0, 0, set()))
        joined.append((key, base_own, main_own, base_calls, main_calls))

    grown_time = sorted(
        (
            entry
            for entry in joined
            if max(entry[1], entry[2]) >= FLOOR and entry[2] > entry[1]
        ),
        key=lambda entry: -(entry[2] - entry[1]),
    )
    grown_calls = sorted(
        (
            entry
            for entry in joined
            if entry[3] or entry[4]
            if entry[4] > entry[3]
        ),
        key=lambda entry: -(entry[4] - entry[3]),
    )
    # More calls at a raised price is one row's growth, so the count ranking
    # also says how much own time the extra calls hold.
    show(
        "=== own time that grew between the trees (functions whose own time is "
        f"up, floor {FLOOR} s) ===",
        grown_time[:40],
        base,
        main,
    )
    show(
        "=== call counts that grew between the trees (functions called more "
        "often) ===",
        grown_calls[:40],
        base,
        main,
    )
    only = sorted(
        (
            entry
            for entry in joined
            if (entry[3] == 0 or entry[4] == 0) and max(entry[1], entry[2]) >= FLOOR
        ),
        key=lambda entry: -max(entry[1], entry[2]),
    )
    if only:
        show(
            "=== present at one tree only, by own time (a rename or a new call) ===",
            only[:25],
            base,
            main,
        )
    print("")
    print(
        f"a function whose own time grew at an unchanged call count is a dearer "
        f"call; one whose\ncall count grew is more calls.  Entries under {FLOOR} s "
        f"at both trees are not ranked."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
