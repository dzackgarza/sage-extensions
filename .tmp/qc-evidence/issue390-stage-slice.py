r"""#390 probe J: the Otilde(T_Co) plane row, sliced by stage.

Measures the wall time and the peak memory of each stage of

    lattice.stable_orthogonal_group().isotropic_orbit_representatives(2)

on ``T_Co`` -- the ``Otilde(T_Co) = ker rho`` plane row of #390 -- with the row
capped at 90 minutes.  The row is the public call; nothing in the library is
changed.  The instrumentation is installed in this process only:

* ``orthogonal_quotients.libgap`` is replaced by a timing proxy that forwards
  every attribute to the real ``libgap`` and records, per name, the call count
  and the wall time of the call itself.  The GAP primitives of the plane row
  are therefore timed individually: ``IsomorphismPermGroup``, ``Subgroup``,
  ``FactorCosetAction``, ``Index``, ``Order``, ``ClosureGroup``, the
  breadth-first walk passed to ``function_factory``, ``Orbits``.
* ``OrthogonalCharacterQuotient``'s plain methods (``image_order``,
  ``subgroup_image_order``, ``index``) and its cached ones
  (``ambient_discriminant_images``, ``_im_rho_engine_and_section``,
  ``_sign_descent_rank``) are wrapped; the cached ones are wrapped through
  their own descriptor, so the cache stays in force and the row measured here
  is the row the call runs.
* ``OrthogonalCharacterQuotient._iter_splitting_isometries_in_im_rho`` is
  wrapped: the time to its first yield -- the coset action, the closure and
  the walk, which all run before the first lift exists -- is separated from
  the time of each lift after it, and the GAP-side snapshot at the first yield
  gives the split inside that block.
* ``Lattices.ParentMethods.primitive_isotropic_subobject`` is wrapped before
  the row starts (a Sage parent caches its methods in ``_cached_methods``, so a
  patch installed later is bypassed) to split the transport into the plane's
  admission and the rest.  It does not split it: the row answers that method
  once, so the subobject the transport builds is not built there, and the
  transport's interior stays unsplit in this record -- the stage is named, its
  two halves are not.
* ``transport_isotropic_object`` is wrapped on the class of the first lift
  the walk produces (once, so no wrapper stacks on another) and
  ``OrthogonalCharacterQuotient.register_isotropic_lift`` on the quotient: the
  transport and the registration of the planes.  Every wrapped call's own
  duration is also kept in a series, so the report can say whether the cost
  per call grows as the row advances -- the progress lines alone would show a
  decaying rate without saying which stage decays.
* ``orthogonal_quotients.finite_ordered_set`` and
  ``lattice_morphisms._isotropic_orbit_representatives`` are wrapped for the
  row's own assembly (the deduplication of the returned planes) and for the
  ambient ``O(L)`` plane row that precedes it.

One unrelated defect of the tree has to be stepped over to reach the row at
all, and the probe states it rather than hiding it: ``g_sets.py``'s
``_named_stabilizer`` (bbb6608) builds ``libgap.Group(engine_generators,
libgap.Identity(engine_generators[0]))`` and raises ``IndexError`` when the
acting group's generating family is empty -- the trivial group, which this
lattice's generator computation does reach (probe L: ``Symmetric group on 1
points`` acting on ``{0}``).  The probe's shim catches that ``IndexError`` and
returns ``None``, which is the answer the hook already gives for every case it
does not handle, so the caller falls back to the route the tree had before
bbb6608 -- the route the row took at ``488f06fc40``.  Every firing is counted
and printed; no other exception is caught.  ``issue390-stage-slice-main-blocked.log``
is the same probe without the shim, which is where the crash is recorded.

A sampler thread reads ``/proc/self/status``: ``VmRSS`` every two seconds,
tagged with the stage the row is in, so each stage carries its own peak; and
one progress line every thirty seconds with the lifts produced, the planes
transported and the rate over the last interval, which is what makes the
walk's rate visible rather than inferred.

A stage's ``seconds`` are exclusive: the time inside its own calls with the
time of every accounted stage nested inside it subtracted, so the column sums
to the row and a stage that calls another is not counted twice.  ``residual``
is the row's wall time minus that sum -- the part the wrappers do not name --
so a stage they miss cannot hide.

    sage -python <this file>            # the Otilde row on T_Co
    sage -python <this file> cap=1200   # the same row truncated to 1200 s: the
                                        # prefix that splits the transport into
                                        # the plane's admission and the rest
    sage -python <this file> no-shim    # the same row without the shim: the
                                        # ``IndexError`` of bbb6608's stabilizer
                                        # hook, recorded as the block it is
    sage -python <this file> smoke      # the same instrumentation on
                                        # U + U(2) + <-2>, whose Otilde row
                                        # walks two cosets in tens of seconds:
                                        # the check that the slicing sees the
                                        # walk, the transport and the
                                        # registration, not a measurement
"""

import signal
import sys
import threading
import time
import traceback

from sage.libs.gap.libgap import libgap as _real_libgap

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories import lattice_morphisms as lm
from sage_extensions.categories import orthogonal_quotients as oq

START = time.monotonic()
ROW_CAP = 5400  # 90 minutes, the row's own cap on this VM
SAMPLE_SECONDS = 2.0
PROGRESS_SECONDS = 30.0

WALK_SETUP = "walk setup: coset action, closure, GAP breadth-first walk"
LIFT = "lift spelling: one tree product per coset"


def _now():
    return time.monotonic()


def log(message=""):
    print(f"[{_now() - START:.1f}s] {message}", flush=True)


def _status_mib(field):
    try:
        with open("/proc/self/status") as handle:
            for line in handle:
                if line.startswith(field):
                    return int(line.split()[1]) / 1024.0
    except OSError:
        pass
    return float("nan")


STATE = {
    "stage": "start-up",
    "lifts": 0,
    "planes": 0,
    "degree": 0,
    "shim": 0,
    "done": False,
    "walk_setup_gap": [],
    "lift_seconds": [],
    "walk_started": None,
    "walk_ended": None,
}
ACCOUNT = {}
COUNTS = {}
STAGE_RSS = {}
SAMPLES = []
FRAMES = []
_LOCK = threading.Lock()


def enter(key):
    """Open an accounted stage; the caller's own time pauses until :func:`leave`."""
    begin = _now()
    FRAMES.append([key, begin, 0.0])
    STATE["stage"] = key
    return begin


def leave():
    """Close the innermost stage and charge its exclusive time, children removed."""
    key, begin, children = FRAMES.pop()
    elapsed = _now() - begin
    ACCOUNT[key] = ACCOUNT.get(key, 0.0) + (elapsed - children)
    COUNTS[key] = COUNTS.get(key, 0) + 1
    if FRAMES:
        FRAMES[-1][2] += elapsed
        STATE["stage"] = FRAMES[-1][0]


class _Stage:
    """``with _Stage(key):`` -- an accounted stage, exception-safe."""

    def __init__(self, key):
        self.key = key

    def __enter__(self):
        self.begin = enter(self.key)
        return self

    def __exit__(self, *exception):
        leave()
        return False


class _TimedGap:
    """Forwards to the real ``libgap`` and times every callable it hands out."""

    def __init__(self, real):
        object.__setattr__(self, "_real", real)
        object.__setattr__(self, "_wrappers", {})
        object.__setattr__(self, "totals", {})
        object.__setattr__(self, "results", {})

    def __getattr__(self, name):
        value = getattr(object.__getattribute__(self, "_real"), name)
        if not callable(value):
            return value
        wrappers = object.__getattribute__(self, "_wrappers")
        if name not in wrappers:
            wrappers[name] = self._timed(name, value)
        return wrappers[name]

    def _timed(self, name, value):
        totals = object.__getattribute__(self, "totals")
        results = object.__getattribute__(self, "results")
        record = totals.setdefault(name, [0, 0.0])

        def call(*args, **kwargs):
            begin = _now()
            outcome = value(*args, **kwargs)
            record[1] += _now() - begin
            record[0] += 1
            results[name] = outcome
            return outcome

        return call


PROXY = _TimedGap(_real_libgap)


def gap_snapshot():
    return {name: (record[0], record[1]) for name, record in PROXY.totals.items()}


def gap_delta(before, after):
    rows = []
    for name, (calls, seconds) in after.items():
        previous = before.get(name, (0, 0.0))
        if calls != previous[0]:
            rows.append((seconds - previous[1], calls - previous[0], name))
    return sorted(rows, reverse=True)


def wrap_defined(obj, name, key, counter=None):
    """Wrap the method ``name`` on the class of ``obj`` (or on ``obj``) that defines it.

    ``counter`` names a ``STATE`` counter raised once per call, for the stages
    whose count is the row's own output (the transported planes).
    """
    mro = obj.__mro__ if isinstance(obj, type) else type(obj).__mro__
    for klass in mro:
        if name in vars(klass):
            original = vars(klass)[name]

            def timed(
                self, *args, __original=original, __key=key, __counter=counter, **kwargs
            ):
                function = __original.__get__(self, type(self))
                begin = _now()
                with _Stage(__key):
                    outcome = function(*args, **kwargs)
                SERIES.setdefault(__key, []).append(_now() - begin)
                if __counter is not None:
                    STATE[__counter] += 1
                return outcome

            setattr(klass, name, timed)
            return klass
    raise RuntimeError(f"no class of {obj!r} defines {name}")


WRAPPED = set()
SERIES = {}


def wrap_once(obj, name, key, counter=None):
    """Wrap ``name`` on the class of ``obj`` once, wherever that class is."""
    klass = obj if isinstance(obj, type) else type(obj)
    if (klass, name) in WRAPPED:
        return
    WRAPPED.add((klass, name))
    wrap_defined(obj, name, key, counter=counter)


def wrap_iterator():
    original = oq.OrthogonalCharacterQuotient.__dict__[
        "_iter_splitting_isometries_in_im_rho"
    ]

    def timed(self, stabilizer_generators):
        before = gap_snapshot()
        begin = enter(WALK_SETUP)
        generator = original(self, stabilizer_generators)
        first = True
        try:
            while True:
                tick = _now()
                if not first:
                    enter(LIFT)
                try:
                    value = next(generator)
                except StopIteration:
                    if not first:
                        leave()
                    break
                leave()
                spent = _now() - tick
                if first:
                    STATE["walk_started"] = begin - START
                    STATE["walk_setup_gap"] = gap_delta(before, gap_snapshot())
                    if "Index" in PROXY.results:
                        STATE["degree"] = int(PROXY.results["Index"])
                    first = False
                else:
                    STATE["lift_seconds"].append(spent)
                    SERIES.setdefault(LIFT, []).append(spent)
                STATE["lifts"] += 1
                wrap_once(
                    value, "transport_isotropic_object", "transport", counter="planes"
                )
                if STATE["walk_ended"] is None:
                    STATE["walk_ended"] = _now() - START
                yield value
        finally:
            if FRAMES and FRAMES[-1][0] in (WALK_SETUP, LIFT):
                leave()
            if first:
                STATE["walk_ended"] = _now() - START

    oq.OrthogonalCharacterQuotient._iter_splitting_isometries_in_im_rho = timed


def wrap_row_dispatch():
    original_planes = oq._plane_orbit_from_parabolic_stabilizer
    original_assembly = oq.finite_ordered_set
    original_ambient = lm._isotropic_orbit_representatives

    def plane_row(subgroup, representative):
        enter("plane row dispatch (parabolic stabilizer)")
        wrap_defined(representative, "is_parabolic_complete", "is_parabolic_complete")
        wrap_defined(
            representative, "parabolic_stabilizer_generators", "parabolic family"
        )
        return original_planes(subgroup, representative)

    def ambient_row(group, rank, *, flag=False):
        with _Stage("ambient O(L) plane row"):
            return original_ambient(group, rank, flag=flag)

    def assembly(elements):
        with _Stage("row assembly: deduplicate the returned planes"):
            return original_assembly(elements)

    oq._plane_orbit_from_parabolic_stabilizer = plane_row
    oq.finite_ordered_set = assembly
    lm._isotropic_orbit_representatives = ambient_row


def sample():
    while not STATE["done"]:
        stage = STATE["stage"]
        rss = _status_mib("VmRSS:")
        with _LOCK:
            STAGE_RSS[stage] = max(STAGE_RSS.get(stage, 0.0), rss)
            SAMPLES.append((_now() - START, STATE["lifts"], STATE["planes"], rss, stage))
        time.sleep(SAMPLE_SECONDS)


def progress():
    reported = 0.0
    last_lifts = 0
    while not STATE["done"]:
        time.sleep(PROGRESS_SECONDS)
        now = _now() - START
        lifts = STATE["lifts"]
        window = now - reported
        rate = (lifts - last_lifts) / window if window > 0 else float("nan")
        rate_text = f"{rate:.1f}/s" if rate == rate else "nan"
        log(
            f"progress stage={STATE['stage']!r} lifts={lifts} "
            f"planes={STATE['planes']} rate={rate_text} "
            f"rss={_status_mib('VmRSS:'):.0f} MiB"
        )
        reported, last_lifts = now, lifts


class RowUndecided(Exception):
    """The row did not return inside the probe's cap."""


def _alarm(signum, frame):
    raise RowUndecided


class _QuotientProbe:
    """Records the quotient's own data when the row makes one."""

    def __init__(self):
        self.quotient = None


PROBE = _QuotientProbe()


def wrap_quotient():
    original = oq._subgroup_isotropic_orbit_representatives

    def subgroup_row(subgroup, rank, *, flag=False):
        PROBE.quotient = subgroup.finite_character_quotient()
        STATE["stage"] = "character quotient data (group orders)"
        return original(subgroup, rank, flag=flag)

    import sage_extensions.categories.group.predicate_subgroups as ps

    ps._subgroup_isotropic_orbit_representatives = subgroup_row


def install_stabilizer_shim():
    """Step over bbb6608's ``IndexError`` on a trivial acting group; count it."""
    from sage_extensions.categories.group import g_sets

    original = g_sets.FiniteGSets.ParentMethods._named_stabilizer

    def named_stabilizer(self, point):
        try:
            return original(self, point)
        except IndexError:
            STATE["shim"] += 1
            if STATE["shim"] == 1:
                log(
                    "the stabilizer shim answered a trivial acting group: "
                    f"{self.acting_group()!r} on {self.point_set()!r}"
                )
            return None

    g_sets.FiniteGSets.ParentMethods._named_stabilizer = named_stabilizer


def install(with_shim=True):
    if with_shim:
        install_stabilizer_shim()
    # The plane's admission is a Sage parent method, and a parent caches a
    # method in ``_cached_methods`` the first time it is reached -- a patch
    # installed after that is bypassed, so this one goes in before the row.
    from sage_extensions.categories.lattices import Lattices as _Lattices

    wrap_defined(
        _Lattices.ParentMethods,
        "primitive_isotropic_subobject",
        "plane admission (primitive_isotropic_subobject)",
    )
    oq.libgap = PROXY
    wrap_iterator()
    wrap_row_dispatch()
    wrap_quotient()
    wrap_defined(
        oq.OrthogonalCharacterQuotient, "register_isotropic_lift", "registration"
    )
    for name in ("image_order", "subgroup_image_order", "index"):
        wrap_defined(oq.OrthogonalCharacterQuotient, name, f"quotient.{name}")
    for name in (
        "ambient_discriminant_images",
        "_im_rho_engine_and_section",
        "_sign_descent_rank",
    ):
        wrap_defined(oq.OrthogonalCharacterQuotient, name, f"quotient{name}")


def report(row_seconds, decided, outcome):
    log("")
    log("=== stage table ===")
    log(f"{'stage':<62}{'calls':>8}{'seconds':>12}{'share':>9}{'peak MiB':>10}")
    before_row = ACCOUNT.get("lattice construction", 0.0) + ACCOUNT.get(
        "stable orthogonal group", 0.0
    )
    total = sum(ACCOUNT.values()) - before_row
    for key in sorted(ACCOUNT, key=lambda name: -ACCOUNT[name]):
        share = 100.0 * ACCOUNT[key] / row_seconds if row_seconds else float("nan")
        log(
            f"{key:<62}{COUNTS.get(key, 0):>8}{ACCOUNT[key]:>12.1f}"
            f"{share:>8.1f}%{STAGE_RSS.get(key, float('nan')):>10.0f}"
        )
    residual = row_seconds - total
    log(
        f"{'residual (row time not inside an accounted stage)':<62}{'':>8}"
        f"{residual:>12.1f}{100.0 * residual / row_seconds if row_seconds else float('nan'):>8.1f}%"
    )
    log("")
    log("=== the walk's own setup, by GAP primitive ===")
    children = 0.0
    for seconds, calls, name in STATE["walk_setup_gap"]:
        children += seconds
        log(f"  {name:<34}{calls:>6} calls{seconds:>12.3f} s")
    setup = ACCOUNT.get(WALK_SETUP, 0.0)
    log(
        f"  {'the breadth-first walk itself (not proxied)':<34}{'':>6}       "
        f"{setup - children:>12.3f} s"
    )
    log(f"  {'walk setup, exclusive':<34}{'':>6}       {setup:>12.3f} s")
    log("")
    lifts = STATE["lift_seconds"]
    log(f"walk started at {STATE['walk_started']} s, ended at {STATE['walk_ended']} s")
    log("(the first point's spelling is inside the walk setup, not in the per-lift list)")
    log(f"cosets of the coset action (degree): {STATE['degree']}")
    log(f"lifts produced: {STATE['lifts']}, planes transported: {STATE['planes']}")
    if lifts:
        ordered = sorted(lifts)
        log(
            f"per-lift spelling: n={len(ordered)} total={sum(ordered):.1f} s "
            f"min={ordered[0] * 1000:.3f} ms median={ordered[len(ordered) // 2] * 1000:.3f} ms "
            f"mean={1000 * sum(ordered) / len(ordered):.3f} ms max={ordered[-1] * 1000:.3f} ms"
        )
    log("")
    log("=== per-call cost by quarter of the calls (is the cost growing?) ===")
    for key in sorted(SERIES, key=lambda name: -ACCOUNT.get(name, 0.0)):
        values = SERIES[key]
        if len(values) < 8:
            continue
        quarter = len(values) // 4
        means = [
            sum(values[index * quarter:(index + 1) * quarter]) / max(quarter, 1)
            for index in range(4)
        ]
        if len(values) % 4:
            tail = values[3 * quarter:]
            means[3] = sum(tail) / len(tail)
        log(
            f"  {key:<44} n={len(values):>7} quarters (ms): "
            + " ".join(f"{1000 * mean:9.2f}" for mean in means)
        )
    series = [(t, lifts) for t, lifts, _planes, _rss, _stage in SAMPLES]
    if len(series) >= 4:
        cuts = [len(series) // 4, len(series) // 2, 3 * len(series) // 4, len(series) - 1]
        points = [(series[0][0], series[0][1])]
        log("lift rate over the sampled window (lifts/s):")
        for cut in cuts:
            points.append(series[cut])
        for (t0, n0), (t1, n1) in zip(points, points[1:]):
            span = t1 - t0
            log(f"  {t0:8.0f} s -> {t1:8.0f} s: {n0} -> {n1} lifts, {(n1 - n0) / span if span else float('nan'):.2f}/s")
    peak = max((rss for _t, _l, _p, rss, _s in SAMPLES), default=float("nan"))
    log("")
    log(f"the stabilizer shim answered {STATE['shim']} trivial-group questions")
    log(f"row wall time: {row_seconds:.1f} s, decided: {decided}")
    log(f"peak VmRSS (python, sampled): {peak:.0f} MiB, VmHWM now {_status_mib('VmHWM:'):.0f} MiB")
    if outcome is not None:
        log(f"the row returned {outcome} planes")
    for key in sorted(STAGE_RSS, key=lambda name: -STAGE_RSS[name])[:6]:
        log(f"  peak in {key!r}: {STAGE_RSS[key]:.0f} MiB")


def main(argv):
    global ROW_CAP
    for argument in argv:
        if argument.startswith("cap="):
            ROW_CAP = int(argument.split("=", 1)[1])
    install(with_shim="no-shim" not in argv)
    log(
        "probe J: the Otilde row, sliced by stage (#390)"
        + (
            " -- smoke run on U + U(2) + <-2>, whose Otilde row walks two cosets: "
            "the check that the slicing sees the walk, the transport and the "
            "registration, not a measurement of anything"
            if argv and argv[0] == "smoke"
            else ""
        )
    )
    log(f"cap {ROW_CAP} s, python {sys.version.split()[0]}")

    with _Stage("lattice construction"):
        lattice = (
            Lattices(ZZ)("U")
            + Lattices(ZZ)([[0, 2], [2, 0]])
            + Lattices(ZZ)([[-2]])
            if argv and argv[0] == "smoke"
            else NamedLattices.Tco
        )
    log(f"lattice {lattice} of rank {lattice.module_rank()}")
    with _Stage("stable orthogonal group"):
        stable = lattice.stable_orthogonal_group()
    log("Otilde(T_Co) = lattice.stable_orthogonal_group()")

    threading.Thread(target=sample, daemon=True).start()
    threading.Thread(target=progress, daemon=True).start()
    signal.signal(signal.SIGALRM, _alarm)
    STATE["stage"] = "row: isotropic_orbit_representatives(2)"
    log("calling stable.isotropic_orbit_representatives(2)")
    begin = _now()
    decided = True
    planes = None
    try:
        signal.setitimer(signal.ITIMER_REAL, ROW_CAP)
        planes = tuple(stable.isotropic_orbit_representatives(2))
    except RowUndecided:
        decided = False
        log(f"the row did not return inside its {ROW_CAP} s cap")
    except Exception:
        decided = False
        log("the row raised:")
        traceback.print_exc()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        row_seconds = _now() - begin
    STATE["done"] = True
    count = None
    if planes is not None:
        count = len(planes)
        begin = _now()
        primitive = all(plane.is_primitive() is True for plane in planes[:20])
        log(f"the first 20 planes primitive: {primitive} in {_now() - begin:.1f} s")
    report(row_seconds, decided, count)
    log("PROBE J DONE")
    return 0 if decided else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
