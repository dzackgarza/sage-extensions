r"""#528: one `_lift_at` of `T_Co`, split into the objects that call builds.

`843bb5b000` narrowed the ambient plane row's per-class cost to one call: on
`T_Co` the locus' `_lift_at` costs about 105 ms a class (1536 classes, 162 s of
a 520 s window) where `a71272add9`'s matrix test spent 2.23 ms.  This probe
answers the next question and only that one: **inside one call, which object's
construction holds the time**.

The input is the issue's lattice, `NamedLattices.Tco`, at a primitive isotropic
line of it; the classes are the locus' own, recorded by wrapping `_lift_at`
(call 21 raises, so the run stops after twenty classes and not 1536).  Each
recorded class is then evaluated with the body of `isotropic_lifts.py:388-401`
reproduced stage by stage, and the reproduction is checked against the library's
own `_lift_at` on the first class.

Three layers, printed:

1. `stages` -- per class, the whole call split into `_parameter_at`,
   `_target_section`, the three pieces of `eichler_transvection` (`Aut()`, the
   column matrix, the isometry from it), `base_point`, the composition `*`, and
   the locus' test `integral_restriction`.  Mean milliseconds and the count.
2. `counts` -- calls per class of the constructors whose cost the split cannot
   separate on its own: the condition-set engine's ingress (`is_parent_of` and
   `__contains__`, the membership test that runs the predicate), its
   `_element_constructor_`, `is_in_image`, and `Parent.__classcall__` /
   `Category.__classcall__` (the category join a parent construction pays).
3. one cProfile of a single library `_lift_at`, its top entries by own time and
   every construction-site entry by own time, cumulative time and call count.

The VM is shared, so the run times a fixed workload first and prints it beside
the call's seconds (`calib=`), and the numbers below are quoted with it.

Two inputs, so the same split is taken on a specimen and on the row itself:

    mode=line   the primitive isotropic basis line `ep` of `T_Co` (rank 11), the
                twenty classes the locus tests there, and their split;
    mode=row    the issue's own row, `T_Co`'s ambient `O(L)` plane row, with
                `_lift_at` replaced by the split in place: the classes are the
                row's own, the twentieth raises, and the row's route is
                unchanged apart from being observed.

    sage -python <this file> [mode=line|row] [classes=20] [cap=520]
"""

import collections
import cProfile
import pstats
import signal
import sys
import time

from sage.libs.gap.libgap import libgap

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories import isotropic_lifts as il
from sage_extensions.categories.sets import set_categories

START = time.monotonic()
CLASSES = 20
CAP = 540.0


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


def calibration():
    """A fixed workload: the run's CPU share, printed beside every number."""
    begin = now()
    total = 0
    for value in range(300000):
        total += value * value
    libgap.Order(libgap.SymmetricGroup(8))
    return now() - begin, total


class StopProbe(Exception):
    """Enough classes recorded."""


class Undecided(Exception):
    """The run's wall cap."""


class Counters:
    """Own time and call counts of one wrapped method."""

    def __init__(self):
        self.calls = 0
        self.seconds = 0.0

    def wrap(self, owner, name):
        original = vars(owner)[name]
        record = self

        def wrapper(*args, **kwargs):
            begin = now()
            try:
                return original(*args, **kwargs)
            finally:
                record.calls += 1
                record.seconds += now() - begin

        wrapper.__name__ = getattr(original, "__name__", name)
        setattr(owner, name, wrapper)
        return wrapper


def record_classes(torsor, limit):
    """The coordinates the locus itself tests, at most ``limit`` of them.

    `_lift_at` is wrapped, not reimplemented: the coordinates are the ones the
    library passes to it, and the recording costs one library call a class
    (which is the cost being measured, so it is not the cost of the probe).
    """
    owner = il.IsotropicReductionLiftTorsors.ParentMethods
    original = vars(owner)["_lift_at"]
    recorded = []
    seconds = []

    def recording(self, coordinates):
        if len(recorded) >= limit:
            raise StopProbe
        begin = now()
        try:
            return original(self, coordinates)
        finally:
            seconds.append(now() - begin)
            recorded.append(tuple(int(entry) for entry in coordinates))

    setattr(owner, "_lift_at", recording)
    stopped = False
    begin = now()
    try:
        torsor._integral_parameter_cosets()
    except StopProbe:
        stopped = True
    finally:
        setattr(owner, "_lift_at", original)
    return recorded, seconds, now() - begin, stopped


STAGES = collections.defaultdict(list)


def split_one(torsor, coordinates, source, target, deep, test=True):
    """One `_lift_at` split stage by stage; the deep split adds the internals."""
    begin = now()
    parameter = torsor._parameter_at(coordinates)
    STAGES["_parameter_at"].append(now() - begin)

    begin = now()
    section = torsor._target_section(parameter)
    STAGES["_target_section"].append(now() - begin)

    begin = now()
    witt = torsor._target_witt
    isotropic = witt.isotropic_vector()
    rational = witt.rational_lattice()
    STAGES["witt accessors"].append(now() - begin)

    if deep:
        begin = now()
        automorphisms = rational.Aut()
        STAGES["Aut() (parent construction)"].append(now() - begin)
        begin = now()
        column = rational._eichler_transvection_column_matrix(isotropic, section)
        STAGES["column matrix"].append(now() - begin)
        begin = now()
        transvection = automorphisms._isometry_from_column_matrix(column)
        STAGES["isometry from column"].append(now() - begin)
    else:
        begin = now()
        transvection = rational.eichler_transvection(isotropic, section)
        STAGES["eichler_transvection (whole)"].append(now() - begin)

    if deep:
        begin = now()
        trivialization = torsor.trivialization()
        STAGES["base_point: trivialization()"].append(now() - begin)
        begin = now()
        group = torsor.acting_group()
        identity = group.one()
        STAGES["base_point: acting_group().one()"].append(now() - begin)
        begin = now()
        base = trivialization(identity)
        STAGES["base_point: ingress points(one * base)"].append(now() - begin)
    else:
        begin = now()
        base = torsor.base_point()
        STAGES["base_point (whole)"].append(now() - begin)

    begin = now()
    lift = transvection * base
    STAGES["composition *"].append(now() - begin)

    if test:
        begin = now()
        restriction = lift.integral_restriction(source, target)
        STAGES["integral_restriction (the test)"].append(now() - begin)
    else:
        restriction = None
    return lift, restriction


def totals():
    return {name: (len(values), 1000.0 * sum(values) / len(values))
            for name, values in STAGES.items()}


def package_path(filename):
    for marker in ("/sage_extensions/", "/sage/"):
        if marker in filename:
            return marker.strip("/").split("/", 1)[0] + "/" + filename.split(marker, 1)[1]
    return filename.rsplit("/", 1)[-1]


def profile_one(torsor, coordinates, source, target):
    """One library `_lift_at`, profiled: which entry holds its time."""
    profiler = cProfile.Profile()
    begin = now()
    profiler.enable()
    lift = torsor._lift_at(coordinates)
    profiler.disable()
    seconds = now() - begin
    restriction_begin = now()
    restriction = lift.integral_restriction(source, target)
    restriction_seconds = now() - restriction_begin
    stats = pstats.Stats(profiler)
    rows = []
    calls = 0
    for (filename, lineno, name), (_cc, nc, own, cum, _callers) in stats.stats.items():
        rows.append((package_path(filename), lineno, name, own, cum, nc))
        calls += nc
    return rows, calls, seconds, restriction_seconds, restriction is not None, stats


CONSTRUCTION_SITES = (
    "__classcall__", "__init__", "_element_constructor_", "__contains__",
    "is_parent_of", "_declaring_classes", "_final_category_operations",
    "_is_bookkeeping_or_hook", "join", "refine", "_model", "is_in_image",
    "solve", "factor_through_or_none", "_preimage_or_none",
)


CALLER_TARGETS = (
    "__classcall__", "_element_constructor_", "__contains__", "is_parent_of",
    "is_in_image", "_preimage_or_none", "solve", "base_point",
    "_eichler_transvection_column_matrix", "_isometry_from_column_matrix",
    "integral_restriction", "linear_combination", "_fraction_equality_status",
    "refine", "_declaring_classes", "_final_category_operations", "join",
)


def report_callers(stats, floor=0.002):
    """For each entry a construction can hide in, the sites that call it."""
    say("")
    say("=== the construction sites' callers (who asks for the construction, and what it costs) ===")
    for (filename, lineno, name), (_cc, nc, own, cum, callers) in sorted(
            stats.stats.items(), key=lambda item: -item[1][3]):
        if name not in CALLER_TARGETS or cum < floor:
            continue
        say(f"  {package_path(filename)}:{lineno} {name}: own {own:.3f} s, "
            f"cum {cum:.3f} s, {nc} calls")
        for (cfile, cline, cname), (ccc, cnc, ctt, cct) in sorted(
                callers.items(), key=lambda item: -item[1][3])[:4]:
            say(f"      <- {package_path(cfile)}:{cline} {cname}: own {ctt:.3f} s, "
                f"cum {cct:.3f} s, {cnc} calls")


def report_profile(rows, calls, seconds, restriction_seconds, restriction,
                   title="one library `_lift_at`"):
    say("")
    say(f"=== {title}, profiled: {seconds:.3f} s, {calls} calls; "
        f"its `integral_restriction` a further {restriction_seconds:.3f} s "
        f"(integral: {restriction}) ===")
    say(f"  {'file:line':<56}{'function':<34}{'own s':>9}{'cum s':>9}{'calls':>9}")
    for path, lineno, name, own, cum, nc in sorted(rows, key=lambda row: -row[3])[:20]:
        say(f"  {path + ':' + str(lineno):<56}{name[:33]:<34}{own:>9.3f}{cum:>9.3f}{nc:>9}")
    say("")
    say("=== construction sites inside the same call, by own time ===")
    say(f"  {'file:line':<56}{'function':<34}{'own s':>9}{'cum s':>9}{'calls':>9}")
    sites = [row for row in rows if row[2] in CONSTRUCTION_SITES]
    for path, lineno, name, own, cum, nc in sorted(sites, key=lambda row: -row[3])[:24]:
        say(f"  {path + ':' + str(lineno):<56}{name[:33]:<34}{own:>9.3f}{cum:>9.3f}{nc:>9}")
    say("")
    say("=== construction sites inside the same call, by call count ===")
    for path, lineno, name, own, cum, nc in sorted(sites, key=lambda row: -row[5])[:16]:
        say(f"  {path + ':' + str(lineno):<56}{name[:33]:<34}{own:>9.3f}{cum:>9.3f}{nc:>9}")


def run_row(classes, cap, counters):
    """The row the issue is about, with the split taken in place on its own calls.

    `_lift_at` is replaced by the split, so every class the row tests is a class
    this probe has measured, and the twentieth raises to stop the row.  The
    split returns the library's own lift (checked generator by generator in the
    line mode), so the row's route is unchanged apart from being observed.
    """
    begin = now()
    lattice = NamedLattices.Tco
    say(f"input: lattice {now() - begin:.2f} s: {lattice}")
    begin = now()
    group = lattice.stable_orthogonal_group()
    say(f"input: stable orthogonal group {now() - begin:.2f} s")
    supergroup = group.supergroup()
    say(f"input: its supergroup (the ambient O(L))")

    owner = il.IsotropicReductionLiftTorsors.ParentMethods
    original = vars(owner)["_lift_at"]
    state = {"count": 0, "torsors": [], "seconds": []}

    def splitting(self, coordinates):
        if state["count"] >= classes:
            raise StopProbe
        source = self.source_reduction().isotropic_embedding().codomain()
        target = self.target_reduction().isotropic_embedding().codomain()
        deep = state["count"] < 2
        begin = now()
        if state["count"] == 1:
            profiler = cProfile.Profile()
            profiler.enable()
            lift, _restriction = split_one(self, coordinates, source, target, deep, test=False)
            profiler.disable()
            state["profile"] = (profiler, now() - begin)
        else:
            lift, _restriction = split_one(self, coordinates, source, target, deep, test=False)
        state["seconds"].append(now() - begin)
        state["count"] += 1
        state.setdefault("first_torsor", self)
        if id(self) not in state["torsors"]:
            state["torsors"].append(id(self))
        if state["count"] % 5 == 0:
            say(f"  {state['count']} class(es) split; {len(state['torsors'])} torsor(s); "
                f"{1000.0 * sum(state['seconds']) / len(state['seconds']):.1f} ms a class")
        return lift

    setattr(owner, "_lift_at", splitting)
    decided = True
    begin = now()
    signal.setitimer(signal.ITIMER_REAL, cap)
    try:
        representatives = supergroup.isotropic_orbit_representatives(2)
    except StopProbe:
        representatives = None
        say(f"stopped after {state['count']} class(es), as the probe asks")
    except Undecided:
        decided = False
        say(f"the row reached {state['count']} class(es) inside its {cap:.0f} s cap")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        setattr(owner, "_lift_at", original)
    say(f"the row: {now() - begin:.1f} s, {state['count']} class(es) split, "
        f"{len(state['torsors'])} torsor(s), decided {decided}")
    first = state.get("first_torsor")
    if first is not None:
        one = first.base_point()
        two = first.base_point()
        say(f"two `base_point()` calls of the torsor the classes came from are "
            f"the same object: {one is two}; equal: {one == two}")
        profiler = cProfile.Profile()
        begin = now()
        profiler.enable()
        first.base_point()
        profiler.disable()
        seconds = now() - begin
        stats = pstats.Stats(profiler)
        rows = []
        calls = 0
        for (filename, lineno, name), (_cc, nc, own, cum, _callers) in stats.stats.items():
            rows.append((package_path(filename), lineno, name, own, cum, nc))
            calls += nc
        report_profile(rows, calls, seconds, 0.0, None,
                       title="one `base_point()` of that torsor")
        say("")
        say("=== the base point's ingress, its callers ===")
        report_callers(stats, floor=0.001)
    if state["seconds"]:
        say(f"  the split `_lift_at`: {len(state['seconds'])} calls, "
            f"{sum(state['seconds']):.3f} s, "
            f"{1000.0 * sum(state['seconds']) / len(state['seconds']):.1f} ms a call")
    if not state["count"]:
        say("no class reached: the split has no input on this route")
        return 2
    say("")
    say(f"  {'stage':<52}{'calls':>7}{'ms/call':>10}{'total s':>10}")
    for name, (calls, milliseconds) in sorted(totals().items(), key=lambda item: -item[1][1]):
        say(f"  {name:<52}{calls:>7}{milliseconds:>10.3f}{milliseconds * calls / 1000.0:>10.3f}")
    say("")
    say("the constructors, over the split classes:")
    for name, counter in counters.items():
        say(f"  {name:<56}{counter.calls:>7} calls{counter.seconds:>9.3f} s own"
            f"{1000.0 * counter.seconds / max(counter.calls, 1):>9.2f} ms a call")
    if "profile" in state:
        profiler, seconds = state["profile"]
        stats = pstats.Stats(profiler)
        rows = []
        calls = 0
        for (filename, lineno, name), (_cc, nc, own, cum, _callers) in stats.stats.items():
            rows.append((package_path(filename), lineno, name, own, cum, nc))
            calls += nc
        report_profile(rows, calls, seconds, 0.0, None)
        report_callers(stats)
    say("PROBE DONE")
    return 0


def main(argv):
    global CLASSES, CAP
    mode = "line"
    for argument in argv:
        if argument.startswith("classes="):
            CLASSES = int(argument.split("=", 1)[1])
        elif argument.startswith("cap="):
            CAP = float(argument.split("=", 1)[1])
        elif argument.startswith("mode="):
            mode = argument.split("=", 1)[1]

    seconds_calib, _ = calibration()
    say(f"calibration (fixed workload, for the run's CPU share): {seconds_calib:.3f} s")
    say(f"mode={mode} classes={CLASSES} cap={CAP:.0f} s")

    counts = collections.OrderedDict()
    for name in ("is_parent_of", "__contains__", "_element_constructor_"):
        counters = Counters()
        counters.wrap(set_categories._ConditionSetEngine, name)
        counts[f"_ConditionSetEngine.{name}"] = counters
    from sage_extensions.categories.modules.module_morphisms import module_morphisms

    for owner in (module_morphisms.ModuleMorphismMethods,
                  module_morphisms.ModuleEmbeddingMethods):
        if "is_in_image" in vars(owner):
            counters = Counters()
            counters.wrap(owner, "is_in_image")
            counts[f"{owner.__name__}.is_in_image"] = counters

    def alarm(signum, frame):
        raise Undecided

    signal.signal(signal.SIGALRM, alarm)

    if mode == "row":
        return run_row(CLASSES, CAP, counts)

    begin = now()
    lattice = NamedLattices.Tco
    say(f"input: lattice {now() - begin:.2f} s: {lattice}")

    labels = tuple(lattice.module_generating_set())
    vectors = {label: lattice.module_generator(label) for label in labels}
    say(f"basis: {labels}")
    say("norms of the basis vectors: " + ", ".join(
        f"{label}: {vectors[label].q()}" for label in labels))

    isotropic_label = next(label for label in labels if vectors[label].q() == lattice.base_ring().zero())
    vector = vectors[isotropic_label]
    say(f"a primitive isotropic basis vector: {isotropic_label}")

    begin = now()
    line = lattice.primitive_isotropic_subobject(vector)
    say(f"input: primitive isotropic line {now() - begin:.2f} s")

    begin = now()
    reduction = line.isotropic_reduction()
    say(f"input: its isotropic reduction {now() - begin:.2f} s "
        f"(quotient rank {reduction.quotient_lattice().module_rank()})")

    begin = now()
    torsor = reduction.rational_lifts(reduction, reduction.Aut().one())
    say(f"input: the rational lift torsor {now() - begin:.2f} s: {torsor}")

    source = torsor.source_reduction().isotropic_embedding().codomain()
    target = torsor.target_reduction().isotropic_embedding().codomain()
    say(f"the locus' test lattices: source {source}, target {target}")

    say("")
    say("=== the locus' own classes: recording them ===")
    signal.setitimer(signal.ITIMER_REAL, CAP)
    try:
        recorded, library_seconds, locus_seconds, stopped = record_classes(torsor, CLASSES)
    except Undecided:
        recorded, library_seconds, locus_seconds, stopped = [], [], 0.0, False
        say(f"the locus did not reach {CLASSES} classes inside its {CAP:.0f} s cap")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    say(f"recorded {len(recorded)} class(es) in {locus_seconds:.1f} s of locus "
        f"(stopped after the recording: {stopped})")
    if library_seconds:
        say(f"  the library's own `_lift_at`: {len(library_seconds)} calls, "
            f"{sum(library_seconds):.3f} s, {1000.0 * sum(library_seconds) / len(library_seconds):.1f} ms a call")
    if not recorded:
        say("no class recorded: the split has no input")
        return 2

    for name, counter in counts.items():
        counter.calls = 0
        counter.seconds = 0.0

    say("")
    say("=== the split, per class (the body of `_lift_at` stage by stage) ===")
    for index, coordinates in enumerate(recorded):
        split_one(torsor, coordinates, source, target, deep=(index == 0))

    # The reproduction must be the library's own lift, not a second statement
    # of it: the first class' images are compared generator by generator.
    coordinates = recorded[0]
    lift, _restriction = split_one(torsor, coordinates, source, target, deep=False)
    library_lift = torsor._lift_at(coordinates)
    domain = lift.domain()
    generator_labels = tuple(domain.module_generating_set())
    same = all(lift(domain.module_generator(label)) == library_lift(domain.module_generator(label))
               for label in generator_labels)
    say(f"the split reproduces the library's `_lift_at` on all "
        f"{len(generator_labels)} generators: {same}")
    if not same:
        say("RESULT split_agrees=False")
        return 2

    say("")
    say(f"  {'stage':<52}{'calls':>7}{'ms/call':>10}{'total s':>10}")
    for name, (calls, milliseconds) in sorted(totals().items(), key=lambda item: -item[1][1]):
        say(f"  {name:<52}{calls:>7}{milliseconds:>10.3f}{milliseconds * calls / 1000.0:>10.3f}")

    say("")
    say(f"the constructors' calls over the {len(recorded)} classes: "
        f"(counters were reset after the recording, so these are the split's)")
    for name, counter in counts.items():
        say(f"  {name:<56}{counter.calls:>7} calls{counter.seconds:>9.3f} s own"
            f"{1000.0 * counter.seconds / max(counter.calls, 1):>9.2f} ms a call")

    say("")
    say("counts reset; profiling one library `_lift_at` alone:")
    for name, counter in counts.items():
        counter.calls = 0
        counter.seconds = 0.0
    rows, calls, seconds, restriction_seconds, restriction, stats = profile_one(
        torsor, recorded[min(1, len(recorded) - 1)], source, target)
    report_profile(rows, calls, seconds, restriction_seconds, restriction)
    report_callers(stats)
    say("")
    say("=== the same constructors inside that one profiled call ===")
    for name, counter in counts.items():
        say(f"  {name:<56}{counter.calls:>7} calls{counter.seconds:>9.3f} s own"
            f"{1000.0 * counter.seconds / max(counter.calls, 1):>9.2f} ms a call")

    stages = totals()
    say("")
    say("RESULT classes={} lift_ms={} base_point_ms={} transvection_ms={} "
        "composition_ms={} test_ms={} calib={:.3f}".format(
            len(recorded),
            round(1000.0 * sum(library_seconds) / len(library_seconds), 1) if library_seconds else -1,
            round(stages.get("base_point (whole)", (0, 0.0))[1], 1),
            round(stages.get("eichler_transvection (whole)", (0, 0.0))[1], 1),
            round(stages.get("composition *", (0, 0.0))[1], 1),
            round(stages.get("integral_restriction (the test)", (0, 0.0))[1], 1),
            seconds_calib,
        ))
    say("PROBE DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
