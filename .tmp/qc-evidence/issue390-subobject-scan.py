r"""#390 probe S: which equality scans the subobjects built before.

Probe M put the plane transport's rise in one statement of
``_lattice_subobject_on_basis`` and named ``FiniteOrderedSets.__eq__``
(``finite_ordered_sets.py:578``) the function whose time per call grows,
called from ``subobject_on``.  Its input was ``T_Co``, whose row spends
1100-1550 s in setup before its first plane, so every answer cost half an
hour.  This probe asks the same question on a lattice of rank 5, and answers
it in minutes.

    L      = U + U + <-2>                 rank 5, signature (2, 3)
    v_k    = (1, e^2 - c d, c, d, e)       primitive isotropic, a *a + c*d = e^2
    base_k = L.primitive_isotropic_subobject(v_k)
    g_k    = one of 40 isometries, a length-three word in O(L)'s generators
    moved  = g_k.transport_isotropic_object(base_k)

``transport_isotropic_object`` is the library method the row calls, so its two
statements -- ``(self * obj.inclusion()).image()`` and
``self.codomain().primitive_isotropic_subobject(*basis)`` -- are the same two
statements, reached through the same ``subobject_on`` and
``_lattice_subobject_spanning``, on rank 5 instead of rank 11.  The base
changes from call to call because a fixed base does not accumulate: the
isotropic line orbit of this lattice holds about 120 planes under the
isometries its generators reach, so a walk over one base stops generating new
subobjects after a hundred calls.  Fresh primitive isotropic vectors do not
run out, and ``v_k`` above gives one per ``(c, d, e)``.

Per window of ``WINDOW`` calls the probe records

* the mean and median wall time of one transport, which is the rise being
  reproduced;
* the equality comparisons of the finite ordered sets, counted by the class
  whose ``__eq__`` answered, by the file:line of the frame that asked, with
  both the count per call and the mean microseconds each comparison cost --
  so a comparison that scans something accumulated shows up as a rising cost
  even where its count is flat;
* the number of live objects, the process RSS, the machine's load, and the
  number of entries in the lattice's ``_cache__primitive_isotropic_subobject``,
  which is the accumulation itself.

Only a class that defines ``__eq__`` in Python can be counted.  The probe
reports which instance brought each counted class in, and which classes were
reached but define their equality in C, so an absent row is a statement about
the class rather than a hole in the count.

    sage -python <this file>             # 1200 transports, windows of 100
    sage -python <this file> n=400       # fewer
    sage -python <this file> profile     # plus cProfile of two windows
"""

import cProfile
import gc
import io
import os
import pstats
import random
import sys
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()
N = 1200
WINDOW = 100
POOL = 40
SEED = 20261115

STATE = {"window": 0, "counting": False}
CALLS = {}          # window -> [seconds of one transport, ...]
COMPARISONS = {}    # window -> {(class, site, other): [count, seconds]}
SUBOBJECTS = []     # the transported subobjects, retained as the row retains them


def log(message=""):
    print(f"[{time.monotonic() - START:.1f}s] {message}", flush=True)


def _proc(field):
    try:
        with open("/proc/self/status") as handle:
            for line in handle:
                if line.startswith(field):
                    return int(line.split()[1]) / 1024.0
    except OSError:
        pass
    return float("nan")


def _spanning_cache():
    """The ``cached_function`` cache of ``_lattice_subobject_spanning``."""
    from sage_extensions.categories.lattices import _lattice_subobject_spanning

    for attribute in ("cache", "_cache"):
        table = getattr(_lattice_subobject_spanning, attribute, None)
        if isinstance(table, dict):
            return table
    return {}


def _load():
    with open("/proc/loadavg") as handle:
        return float(handle.read().split()[0])


# ------------------------------------------------------- the equality census

_WRAPPED = {}


def counted_class(instance):
    for candidate in type(instance).__mro__:
        raw = vars(candidate).get("__eq__")
        if raw is not None and hasattr(raw, "__code__"):
            return candidate
    return None


def wrap_equality(instance, label):
    """Count the comparisons that reach this instance's Python ``__eq__``."""
    klass = counted_class(instance)
    if klass is None:
        return (
            f"{label}: no Python __eq__ on {type(instance).__name__}; "
            "its comparisons are C-level and cannot be counted here"
        )
    if klass in _WRAPPED:
        return f"{label}: {klass.__qualname__} (the same implementation, already counted)"
    original = vars(klass)["__eq__"]

    def counted(self, other, __original=original, __class=klass):
        if not STATE["counting"]:
            return __original(self, other)
        frame = sys._getframe(1)
        site = (
            f"{frame.f_code.co_filename.rsplit('/', 1)[-1]}:{frame.f_lineno} "
            f"{frame.f_code.co_name}"
        )
        cell = COMPARISONS.setdefault(STATE["window"], {}).setdefault(
            (__class.__name__, site, type(other).__name__), [0, 0.0]
        )
        begin = time.perf_counter()
        try:
            return __original(self, other)
        finally:
            cell[0] += 1
            cell[1] += time.perf_counter() - begin

    setattr(klass, "__eq__", counted)
    _WRAPPED[klass] = original
    return f"{label}: {klass.__module__}.{klass.__qualname__}"


# ------------------------------------------------------------------ the input

def lattice_and_family():
    """The rank-5 lattice, its orthogonal group, and the isometries to move by."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    group = lattice.stable_orthogonal_group()
    generators = tuple(group.group_generators())
    rng = random.Random(SEED)
    pool = []
    for _ in range(POOL):
        isometry = group.one()
        for _ in range(3):
            isometry = generators[rng.randrange(len(generators))] * isometry
        pool.append(isometry)
    labels = tuple(lattice.module_generating_set())

    def isotropic(index):
        """A primitive isotropic vector: a = 1, b = e^2 - c d, a b + c d = e^2."""
        e = 1 + (index % 11)
        c = (index // 11) % 11
        d = (index // 121) % 11
        return lattice.linear_combination(
            {
                labels[0]: ZZ(1),
                labels[1]: ZZ(e * e - c * d),
                labels[2]: ZZ(c),
                labels[3]: ZZ(d),
                labels[4]: ZZ(e),
            }
        )

    return lattice, group, pool, isotropic


# ------------------------------------------------------------------- windows

def close_window(window, calls):
    values = sorted(calls)
    row = COMPARISONS.get(window, {})
    count = sum(cell[0] for cell in row.values())
    seconds = sum(cell[1] for cell in row.values())
    log("")
    log(f"--- window {window}: {len(values)} transports ---")
    log(
        f"    transport   mean {1000 * sum(values) / len(values):8.2f} ms"
        f"  median {1000 * values[len(values) // 2]:8.2f} ms"
        f"  max {1000 * values[-1]:8.2f} ms"
    )
    log(
        f"    comparisons {count:>7}  ({count / len(values):.1f} per call,"
        f" {1e6 * seconds / count if count else float('nan'):.1f} us each)"
    )
    for (name, site, other), (hits, spent) in sorted(
        row.items(), key=lambda item: -item[1][1]
    )[:5]:
        log(
            f"      {name}.__eq__  from {site:<46} other={other:<26}"
            f"{hits:>7} comparisons, {1e6 * spent / hits:8.1f} us each"
        )
    log(
        f"    live objects {len(gc.get_objects())}, rss {_proc('VmRSS:'):.0f} MiB,"
        f" load {_load():.2f} on {os.cpu_count()} cores"
    )


def main(argv):
    global N, WINDOW
    profile = "profile" in argv
    for argument in argv:
        if argument.startswith("n="):
            N = int(argument.split("=", 1)[1])
        if argument.startswith("window="):
            WINDOW = int(argument.split("=", 1)[1])

    log("probe S: which equality scans the subobjects built before (#390)")
    log(f"n={N}, window={WINDOW}, pool={POOL}, seed={SEED}, python {sys.version.split()[0]}")
    log(f"load {_load():.2f} on {os.cpu_count()} cores")

    lattice, group, pool, isotropic = lattice_and_family()
    log(f"lattice {lattice}, rank {lattice.module_rank()}, signature {lattice.signature()}")
    log(f"isometries to move by: {len(pool)} words of length three in O(L)'s generators")
    first_base = lattice.primitive_isotropic_subobject(isotropic(0))
    image = (pool[0] * first_base.inclusion()).image()
    log("equality counted on:")
    for instance, label in (
        (lattice, "lattice"),
        (lattice.module_generating_set(), "lattice framing"),
        (first_base, "subobject"),
        (first_base.module_generating_set(), "subobject framing"),
        (first_base.inclusion().domain(), "subobject domain"),
        (image, "image"),
        (image.module_generating_set(), "image framing"),
    ):
        log("  " + wrap_equality(instance, label))

    profilers = {}
    active = [None]  # one profiler at a time: cProfile owns a fixed tool slot
    profile_windows = []
    if profile:
        early_start = 1 + WINDOW
        late_start = max(early_start + 2 * WINDOW, N - 2 * WINDOW)
        profile_windows = [early_start, late_start]
        log(f"profiled windows begin at calls {profile_windows}, {WINDOW} calls each")
    calls, window_calls = [], []
    STATE["counting"] = True
    begin = time.monotonic()
    for index in range(1, N + 1):
        window = (index - 1) // WINDOW
        if window != STATE["window"]:
            CALLS[STATE["window"]] = window_calls
            close_window(STATE["window"], window_calls)
            STATE["window"] = window
            window_calls = []

        if profile and index in profile_windows:
            profiler = cProfile.Profile()
            profiler.enable()
            profilers[index] = profiler
            active[0] = index
        if profile and active[0] is not None and index == active[0] + WINDOW - 1:
            profilers[active[0]].disable()
            active[0] = None

        base = lattice.primitive_isotropic_subobject(isotropic(index))
        isometry = pool[index % len(pool)]

        clock = time.perf_counter()
        moved = isometry.transport_isotropic_object(base)
        spent = time.perf_counter() - clock

        SUBOBJECTS.append(moved)
        calls.append(spent)
        window_calls.append(spent)

        if index % 200 == 0:
            log(
                f"  {index} transports, mean {1000 * sum(calls) / len(calls):.2f} ms,"
                f" last {1000 * calls[-1]:.2f} ms, rss {_proc('VmRSS:'):.0f} MiB"
            )
    STATE["counting"] = False
    if window_calls:
        CALLS[STATE["window"]] = window_calls
        close_window(STATE["window"], window_calls)
    total = time.monotonic() - begin

    # ----------------------------------------------------------------- report
    log("")
    log(f"=== one transport, by window of {WINDOW} calls ===")
    log(
        f"{'window':>6}{'calls':>7}{'mean ms':>10}{'median':>9}"
        f"{'comparisons':>13}{'per call':>10}{'us each':>9}{'built':>8}"
    )
    windows = sorted(CALLS)
    for window in windows:
        values = sorted(CALLS[window])
        row = COMPARISONS.get(window, {})
        count = sum(cell[0] for cell in row.values())
        seconds = sum(cell[1] for cell in row.values())
        log(
            f"{window:>6}{len(values):>7}{1000 * sum(values) / len(values):10.2f}"
            f"{1000 * values[len(values) // 2]:9.2f}"
            f"{count:>13}{count / len(values):>10.1f}"
            f"{(1e6 * seconds / count if count else float('nan')):>9.1f}"
            f"{(window + 1) * WINDOW:>11}"
        )
    early = sum(CALLS[windows[0]]) / len(CALLS[windows[0]])
    late = sum(CALLS[windows[-1]]) / len(CALLS[windows[-1]])
    log(
        f"  window {windows[0]}: {1000 * early:.2f} ms per transport; window "
        f"{windows[-1]}: {1000 * late:.2f} ms; ratio {late / early:.2f} over "
        f"{(windows[-1] - windows[0]) * WINDOW} transports"
    )
    log(
        "  the timed call is the library's own transport_isotropic_object; its "
        "two statements were split on T_Co by probe M and that split is not "
        "repeated here"
    )

    log("")
    log("=== comparisons, count per call and microseconds each, by window ===")
    keys = sorted({key for row in COMPARISONS.values() for key in row})
    for key in keys:
        counts = [COMPARISONS.get(window, {}).get(key, [0, 0.0])[0] for window in windows]
        if not max(counts):
            continue
        log(f"  {key[0]}.__eq__   other={key[2]}")
        log(f"    called from {key[1]}")
        log("    per call : " + " ".join(f"{value / WINDOW:7.1f}" for value in counts))
        log(
            "    us each  : "
            + " ".join(
                f"{(lambda cell: 1e6 * cell[1] / cell[0] if cell[0] else float('nan'))(COMPARISONS.get(window, {}).get(key, [0, 0.0])):7.1f}"
                for window in windows
            )
        )
        first = next(value for value in counts if value)
        log(
            f"    window {windows[0]}: {counts[0]} comparisons ({counts[0] / WINDOW:.1f} per call);"
            f" window {windows[-1]}: {counts[-1]} ({counts[-1] / WINDOW:.1f} per call);"
            f" ratio {counts[-1] / first if first else float('nan'):.2f}"
        )
    log("  (windows " + " ".join(str(window) for window in windows) + ")")

    log("")
    log("=== the accumulation ===")
    cache = lattice.__dict__.get("_cache__primitive_isotropic_subobject", {})
    coordinates = {
        tuple(
            tuple(int(value) for value in
                  subobject.embedded_module_generators()[label].to_vector())
            for label in subobject.module_generating_set()
        )
        for subobject in SUBOBJECTS
    }
    log(f"  primitive_isotropic_subobject cache entries: {len(cache)}")
    # ``_lattice_subobject_spanning`` is a cached_function whose key holds the
    # span basis, a FiniteOrderedSets.  Its cache is what a lookup scans.
    spanning_cache = _spanning_cache()
    log(f"  _lattice_subobject_spanning cache entries: {len(spanning_cache)}")
    if spanning_cache:
        hashes = sorted({hash(key[1]) for key in spanning_cache})
        cardinalities = sorted({int(key[1].cardinality()) for key in spanning_cache})
        log(f"  distinct hash values among those keys: {len(hashes)} -> {hashes[:6]}")
        log(f"  distinct cardinalities of the cached bases: {cardinalities}")
        log(
            "  a dict lookup on these keys compares the stored keys one by one "
            "whenever their hashes agree, which is why the comparison count grows"
        )
    log(f"  distinct transported subobjects: {len(coordinates)}")
    log(f"  subobjects retained by the probe: {len(SUBOBJECTS)}")
    log(f"  {N} transports in {total:.1f} s, mean {1000 * total / N:.2f} ms")
    log(f"  peak VmHWM {_proc('VmHWM:'):.0f} MiB")

    if profilers:
        log("")
        log("=== two profiled windows ===")
        per_call = {}
        for index, profiler in sorted(profilers.items()):
            stats = pstats.Stats(profiler)
            per_call[index] = {
                key: value[3] / WINDOW for key, value in stats.stats.items()
            }
            log(f"  window at call {index}: {stats.total_tt:.2f} s self time over {WINDOW} calls")
        indices = sorted(per_call)
        if len(indices) > 1:
            early_stats, late_stats = per_call[indices[0]], per_call[indices[-1]]
            rows = sorted(
                (
                    (late_stats.get(key, 0.0) - early_stats.get(key, 0.0),
                     late_stats.get(key, 0.0), early_stats.get(key, 0.0), key)
                    for key in set(early_stats) | set(late_stats)
                ),
                reverse=True,
            )
            log("")
            log("  growth of cumulative time per call")
            log(f"    {'function':<58}{'early':>10}{'late':>10}{'growth':>10}")
            for change, late_value, early_value, key in rows[:14]:
                filename, lineno, name = key[:3]
                frame = f"{name} ({filename.rsplit('/', 1)[-1]}:{lineno})"
                log(f"    {frame:<58}{1000 * early_value:10.2f}{1000 * late_value:10.2f}{1000 * change:10.2f}")
            # Who calls the comparison: the profile keeps its callers, with
            # counts, so the chain from the transport to __eq__ is read rather
            # than inferred from the call-site counter.
            for index in sorted(profilers):
                stats = pstats.Stats(profilers[index]).stats
                targets = [
                    key for key in stats
                    if key[2] == "__eq__" and key[0].endswith("finite_ordered_sets.py")
                ]
                log("")
                log(f"  the callers of FiniteOrderedSets.__eq__, window at call {index}:")
                for key in targets:
                    value = stats[key]
                    log(f"    __eq__ at {key[0].rsplit('/', 1)[-1]}:{key[1]}: {value[1]} calls")
                    for caller, counts in sorted(value[4].items(), key=lambda item: -item[1][1]):
                        log(
                            f"      called by {caller[2]} "
                            f"({caller[0].rsplit('/', 1)[-1]}:{caller[1]}): "
                            f"{counts[1]} call(s)"
                        )
                        parent = stats.get(caller)
                        if parent:
                            for grandparent, grandcounts in sorted(
                                parent[4].items(), key=lambda item: -item[1][1]
                            )[:2]:
                                log(
                                    f"        itself called by {grandparent[2]} "
                                    f"({grandparent[0].rsplit('/', 1)[-1]}:{grandparent[1]}): "
                                    f"{grandcounts[1]} call(s)"
                                )
            for index in sorted(profilers):
                log("")
                log(f"  raw cumulative view, window at call {index}:")
                stream = io.StringIO()
                pstats.Stats(profilers[index], stream=stream).sort_stats("cumulative").print_stats(16)
                for line in stream.getvalue().splitlines():
                    if line.strip():
                        log("    " + line)
    log("PROBE S DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
