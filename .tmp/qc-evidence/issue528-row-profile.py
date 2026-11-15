r"""#528: one cProfile of the ambient ``O(L)`` plane row alone, at one tree.

The row this issue is about is

    NamedLattices.Tco.stable_orthogonal_group().supergroup().isotropic_orbit_representatives(2)

and its setup was already split into stages, each timed alone, by
``issue390-stage-alone.py`` (``issue528-*-<stage>.log``).  This probe answers the
next question and only that one: **which function did the row's time or call
count move to between two trees**.  So it builds the two inputs the row takes
(the lattice and its stable orthogonal group) outside the profiled region, and
profiles the row itself and nothing else.

Why a table and not a printed top-N: two runs are compared function by
function, by own time and by call count, and a top-N list of one run cannot be
joined to a top-N list of another -- the entries below the cut are exactly the
ones a comparison is looking for.  Each run therefore writes every profiled
entry to a table

    # tree=<sha> seconds=<x> calib=<y> decided=<bool> rows=<n> calls=<n>
    <path inside the package>\t<lineno>\t<function>\t<own s>\t<cum s>\t<calls>

and ``issue528-row-profile-compare.py`` joins two of them on
``(path, function)`` -- not on the line number, which moves when a function is
edited -- and prints what grew in own time and what grew in call count.

Both rows return at both trees, so both tables are complete and their call
counts are comparable: the row is asked for the same orbit representatives of
the same lattice at both trees, and a truncated table would be marked
``decided=False`` in its header and is never compared as if whole.

The VM is shared, so every run times a fixed workload first and prints it with
the row's seconds (``calib=``): the same stage has been seen to move by a
factor of three with the VM's load alone (``issue390-stage-alone.py``'s
docstring).  The comparison quotes the raw seconds and the calibration beside
each other and does not divide one by the other.

Arguments (all optional)::

    cap=<seconds>    the row's own cap, default 560 (a run may take ten minutes)
    sha=<commit>     the tree's SHA, which names the table; the launcher reads it
                     on the host because the tree is bound without its ``.git``
    table=<path>     where to write the table; default
                     /repos/sage-extensions/.tmp/qc528/<sha>-row.tsv

The printed log is what the evidence file holds; the table is the raw record the
comparison reads.
"""

import cProfile
import os
import pstats
import signal
import sys
import time

from sage.libs.gap.libgap import libgap
from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()
CAP = 560.0
TABLE = None


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


def calibration():
    """A fixed workload: the run's CPU share, so two runs can be read together."""
    begin = now()
    total = 0
    for value in range(300000):
        total += value * value
    libgap.Order(libgap.SymmetricGroup(8))
    return now() - begin, total


class Undecided(Exception):
    """The row did not return inside the run's cap."""


def _alarm(signum, frame):
    raise Undecided


def package_path(filename):
    """The part of a file name that is stable across the two trees."""
    for marker in ("/sage_extensions/", "/sage/"):
        if marker in filename:
            return marker.strip("/").split("/", 1)[0] + "/" + filename.split(marker, 1)[1]
    return filename.rsplit("/", 1)[-1]


def main(argv):
    global CAP, TABLE
    tree_sha = "unknown"
    for argument in argv:
        if argument.startswith("cap="):
            CAP = float(argument.split("=", 1)[1])
        elif argument.startswith("table="):
            TABLE = argument.split("=", 1)[1]
        elif argument.startswith("sha="):
            # The launcher reads the tree's SHA on the host and passes it here:
            # the tree is bound into the image without its ``.git`` (a
            # worktree's ``.git`` is a file pointing into the main checkout,
            # which is not bound), so ``git rev-parse`` inside the container
            # cannot see it.  The launcher's own header prints the same SHA, so
            # the two can be checked against each other.
            tree_sha = argument.split("=", 1)[1]
    if TABLE is None:
        TABLE = f"/repos/sage-extensions/.tmp/qc528/{tree_sha[:8]}-row.tsv"

    seconds_calib, _ = calibration()
    say(f"calibration (fixed workload, for the run's CPU share): {seconds_calib:.3f} s")
    say(f"tree {tree_sha}, cap {CAP:.0f} s, python {sys.version.split()[0]}")

    begin = now()
    lattice = NamedLattices.Tco
    say(f"input: lattice {now() - begin:.2f} s: {lattice}")
    begin = now()
    group = lattice.stable_orthogonal_group()
    say(f"input: stable orthogonal group {now() - begin:.2f} s")
    supergroup = group.supergroup()
    say(f"input: its supergroup (the ambient O(L)) {supergroup}")

    profiler = cProfile.Profile()
    signal.signal(signal.SIGALRM, _alarm)
    decided = True
    begin = now()
    profiler.enable()
    try:
        signal.setitimer(signal.ITIMER_REAL, CAP)
        representatives = supergroup.isotropic_orbit_representatives(2)
    except Undecided:
        decided = False
        say(f"the row did not return inside its {CAP:.0f} s cap")
        representatives = None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        seconds = now() - begin
        profiler.disable()
    if decided:
        say(f"the row returned {len(tuple(representatives))} plane representatives "
            f"in {seconds:.1f} s")
    say(f"the profiled row: {seconds:.1f} s (calib {seconds_calib:.3f} s, decided {decided})")

    stats = pstats.Stats(profiler)
    rows = []
    calls = 0
    for key, value in stats.stats.items():
        filename, lineno, name = key
        cc, nc, own, cum, _callers = value
        rows.append((package_path(filename), lineno, name, own, cum, nc))
        calls += nc
    os.makedirs(os.path.dirname(TABLE), exist_ok=True)
    with open(TABLE, "w") as handle:
        handle.write(
            f"# tree={tree_sha} seconds={seconds:.3f} calib={seconds_calib:.3f} "
            f"decided={decided} rows={len(rows)} calls={calls}\n"
        )
        for row in rows:
            handle.write("\t".join([row[0], str(row[1]), row[2],
                                    f"{row[3]:.6f}", f"{row[4]:.6f}", str(row[5])]) + "\n")
    say(f"table: {TABLE} ({len(rows)} functions, {calls} calls)")

    # The printed summary: own time, which is what the comparison ranks on.
    say("")
    say("=== the row's biggest entries by own time ===")
    say(f"  {'file:line':<52}{'function':<32}{'own s':>9}{'cum s':>9}{'calls':>10}")
    for path, lineno, name, own, cum, nc in sorted(rows, key=lambda row: -row[3])[:25]:
        say(f"  {path + ':' + str(lineno):<52}{name[:31]:<32}{own:>9.3f}{cum:>9.3f}{nc:>10}")
    say("")
    say("=== the row's biggest entries by cumulative time ===")
    say(f"  {'file:line':<52}{'function':<32}{'own s':>9}{'cum s':>9}{'calls':>10}")
    for path, lineno, name, own, cum, nc in sorted(rows, key=lambda row: -row[4])[:15]:
        say(f"  {path + ':' + str(lineno):<52}{name[:31]:<32}{own:>9.3f}{cum:>9.3f}{nc:>10}")
    say("")
    say(f"RESULT row_seconds={seconds:.2f} decided={decided} calib={seconds_calib:.3f} "
        f"calls={calls} table={TABLE}")
    say("PROBE DONE")
    return 0 if decided else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
