r"""#528: what the Otilde(T_Co) plane row is in after its transvections stop.

`a6cac20d79` ran the row once under a ten-minute cap and left one fact: it made
5652 `eichler_transvection`s by 150 s and none after, while `to_vector` climbed
from 189201 to 468060 by 575 s and the row had not returned.  The stage it
sits in is the one #528's body calls unattributed.  This probe attributes it:

  * a sampler thread reads the main thread's stack once a second
    (``sys._current_frames``) and tallies the leaf frame, counting only frames
    inside the package, so the tally names a function of this library rather
    than a site-packages leaf;
  * ``to_vector`` -- the crossing the ten-minute run saw climb -- is shadowed
    once per defining class and counted per *call site*
    (``co_filename``, ``co_name``, the call's own line), which names the
    function whose reads climb without guessing from a tally;
  * when the leaf signature repeats across samples (the run has entered one
    long function), two ``cProfile`` windows of ``WINDOW`` seconds are opened
    from inside the shadowed ``to_vector`` -- which runs in the main thread, the
    only thread a profiler can be switched on in -- separated by ``GAP``
    seconds, and each window's call counts are printed.  Two windows are what
    answers the question the brief asks: whether the crossings per element
    processed *rise* with the elements already processed (a scan, a cache whose
    keys do not separate, a membership test on a list) or are constant per
    element.  A rising ratio between the windows is a scan; an equal ratio is a
    constant.

The row itself is the issue's call, unchanged:
``NamedLattices.Tco.stable_orthogonal_group().isotropic_orbit_representatives(2)``.
A signal cannot interrupt it -- an ``AlarmInterrupt`` inside
``libgap.FactorCosetAction`` is cysignals' exception, not a probe's -- so the
cap is the launcher's and the probe only reports what it reached.
"""

import cProfile
import faulthandler
import gc
import io
import pstats
import sys
import threading
import time
import traceback

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories.modules.framed import framed_free_modules as ffm

START = time.monotonic()
SAMPLE_SECONDS = 20.0
INTERVAL = 10.0
WINDOW = 40.0
GAP = 80.0
# The two windows are scheduled by elapsed time, not by the sampler: the stage
# the row enters after its transvections stop holds the GIL inside GAP for
# minutes at a stretch, so a sampler-driven trigger may never fire.
SCHEDULE = ()
PACKAGE = "sage_extensions"

CALLS = {}
CALLERS = {}
SECONDS = {}
LEAVES = {}
TRACES = {}
COUNTING = True

_state = {
    "leaf": None,
    "streak": 0,
    "stage_started": None,
    "next_window": None,
    "profiler": None,
    "window_ends": None,
    "windows_done": 0,
    "counts_at": {},      # name -> to_vector total at the start of the last window
    "scheduled": 0,       # how many SCHEDULE entries have fired
}
_lock = threading.Lock()
DIAGNOSTICS = {}
_INTERVAL = {"at": None, "sites": {}, "diagnostics": {}, "to_vector": 0}


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


# --------------------------------------------------------------------------
# to_vector, counted per call site


def shadow_to_vector():
    """Count every ``to_vector`` call, by the site that made it."""
    done = []

    def visit(owner, prefix):
        for key, value in vars(owner).items():
            if not isinstance(value, type):
                continue
            if "to_vector" in vars(value):
                original = vars(value)["to_vector"]
                if not getattr(original, "_probe528_slice", False):
                    def counted(self, *args, __original=original, **kwargs):
                        return _crossing(__original, self, args, kwargs)

                    counted._probe528_slice = True
                    counted._probe528_original = original
                    setattr(value, "to_vector", counted)
                    done.append(f"{prefix}{key}")
            visit(value, f"{prefix}{key}.")

    visit(ffm, "framed_free_modules.")
    return done


def _crossing(original, self, args, kwargs):
    """The shadowed crossing: count it, and open a profiling window if due."""
    if COUNTING:
        frame = sys._getframe(2)
        code = frame.f_code
        site = (code.co_filename.rsplit("/", 1)[-1], code.co_name, frame.f_lineno)
        CALLERS[site] = CALLERS.get(site, 0) + 1
        CALLS["to_vector"] = CALLS.get("to_vector", 0) + 1
    _maybe_profile()
    interval_report()
    arm_window()
    begin = now()
    try:
        return original(self, *args, **kwargs)
    finally:
        if COUNTING:
            key = f"to_vector@{type(self).__name__}"
            SECONDS[key] = SECONDS.get(key, 0.0) + (now() - begin)


def _maybe_profile():
    """Start or stop a profiling window; called from the main thread only."""
    moment = now()
    profiler = _state["profiler"]
    if profiler is None:
        due = _state["next_window"]
        if _state["scheduled"] < len(SCHEDULE) and moment - START >= SCHEDULE[_state["scheduled"]]:
            due = moment
            _state["scheduled"] += 1
        if due is not None and moment >= due:
            profiler = cProfile.Profile()
            _state["profiler"] = profiler
            _state["window_ends"] = moment + WINDOW
            _state["counts_at"]["start"] = dict(CALLS)
            say(f"PROFILE window {_state['windows_done'] + 1} opens")
            profiler.enable()
        return
    if moment >= _state["window_ends"]:
        profiler.disable()
        _state["profiler"] = None
        _state["windows_done"] += 1
        stream = io.StringIO()
        pstats.Stats(profiler, stream=stream).sort_stats("tottime").print_stats(18)
        say(f"PROFILE window {_state['windows_done']} closes")
        say(stream.getvalue())
        stream = io.StringIO()
        pstats.Stats(profiler, stream=stream).sort_stats("ncalls").print_stats(12)
        say(stream.getvalue())
        _state["next_window"] = None


# --------------------------------------------------------------------------
# the per-element cost, in blocks, with the input each block was handed

ARM = (200.0, 330.0)
ARMED = set()
BLOCK = 50
GROWTH = {"calls": 0, "begin": None, "block": [], "size": 0}


def arm_window():
    """Ask for a profiling window at the next coordinate read after an armed moment.

    The stage the row enters after its transvections stop holds the GIL inside one
    GAP call for minutes, so a window scheduled by elapsed time can land inside it
    and never open.  Arming at a moment and opening at the next ``to_vector`` puts
    the window in the Python phase that follows, which is the walk.
    """
    if _state["profiler"] is not None or _state["next_window"] is not None:
        return
    for moment in ARM:
        if moment not in ARMED and now() - START >= moment:
            ARMED.add(moment)
            _state["next_window"] = now()
            say(f"  window armed at {moment:.0f} s, to open on the next coordinate read")
            return


def instrument_spanning():
    """Time every span construction the row makes, and the size of its input.

    ``_lattice_subobject_spanning`` is the construction `25eea761af` measured at
    3.93 ms a call early in this row and 126.82 ms a call after 2005 planes, twice
    per plane, and `0c57f3a` showed the construction itself is flat on a small
    lattice.  So what grows is either its input -- the basis it is handed, whose
    coordinates come from a word along the walk -- or something in the row's own
    state.  Both are printed with the block's time.
    """
    from sage_extensions.categories import lattices as lattices_module

    original = lattices_module._lattice_subobject_spanning
    if getattr(original, "_probe528_timed", False):
        return "already timed"

    def timed(module, basis, root_system_type_name=None):
        arm_window()
        begin = now()
        try:
            return original(module, basis, root_system_type_name)
        finally:
            spent = now() - begin
            GROWTH["calls"] += 1
            GROWTH["begin"] = spent if GROWTH["begin"] is None else GROWTH["begin"]
            try:
                size = max(
                    (
                        abs(int(entry))
                        for element in tuple(basis)
                        for entry in element.to_vector()
                    ),
                    default=0,
                )
            except (TypeError, ValueError):
                size = -1
            GROWTH["size"] = max(GROWTH["size"], size)
            GROWTH["block"].append((spent, size))
            if len(GROWTH["block"]) >= BLOCK:
                block = GROWTH["block"]
                GROWTH["block"] = []
                per_call = 1000.0 * sum(spent for spent, _size in block) / len(block)
                cache = getattr(original, "cache", None)
                retained = len(cache) if cache is not None else None
                say(
                    f"  SPAN block {GROWTH['calls'] // BLOCK:>4}: {per_call:8.2f} ms a call "
                    f"over {len(block)} calls; last basis coordinate size {block[-1][1]}, "
                    f"largest so far {GROWTH['size']}; cache {retained}; "
                    f"tracked objects {len(gc.get_objects())}; gc counts {gc.get_count()}"
                )

    timed._probe528_timed = True
    lattices_module._lattice_subobject_spanning = timed
    return "spanning"


# --------------------------------------------------------------------------
# what the main thread itself reports, since a sampler cannot see a held GIL


def wrap_diagnostics():
    """Count the calls that mark one element processed, for the interval ratios."""
    from sage_extensions.categories import lattice_morphisms as lattice_morphisms_module
    from sage_extensions.categories import isotropic_orbits as isotropic_orbits_module
    from sage_extensions.categories import orthogonal_quotients as quotients_module

    done = []

    def shadow(owner, name, label):
        for klass in owner.__mro__:
            if name in vars(klass):
                original = vars(klass)[name]
                if getattr(original, "_probe528_counted", False):
                    return
                def counted(*args, __original=original, **kwargs):
                    DIAGNOSTICS[label] = DIAGNOSTICS.get(label, 0) + 1
                    return __original(*args, **kwargs)
                counted._probe528_counted = True
                setattr(klass, name, counted)
                done.append(label)
                return

    shadow(lattice_morphisms_module.LatticeIsometryMethods, "transport_isotropic_object", "transport")
    shadow(quotients_module.OrthogonalCharacterQuotient, "register_isotropic_lift", "register")
    shadow(quotients_module.OrthogonalCharacterQuotient, "_registered_isotropic_split", "registry_scan")
    shadow(quotients_module.OrthogonalCharacterQuotient, "isotropic_lift_of", "lift_lookup")
    shadow(quotients_module.OrthogonalCharacterQuotient, "certified_parabolic_generators", "certified_parabolic")
    original_same = isotropic_orbits_module._same_subobject
    if not getattr(original_same, "_probe528_counted", False):
        def same_subobject(left, right):
            DIAGNOSTICS["same_subobject"] = DIAGNOSTICS.get("same_subobject", 0) + 1
            return original_same(left, right)
        same_subobject._probe528_counted = True
        isotropic_orbits_module._same_subobject = same_subobject
        # `orthogonal_quotients` imported it by name, so shadow it there too.
        if hasattr(quotients_module, "_same_subobject"):
            quotients_module._same_subobject = same_subobject
        done.append("same_subobject")
    return done


def interval_report():
    """Write what the last interval did, from the main thread that did it."""
    moment = now()
    if _INTERVAL["at"] is None:
        _INTERVAL["at"] = moment
        _INTERVAL["sites"] = dict(CALLERS)
        _INTERVAL["diagnostics"] = dict(DIAGNOSTICS)
        _INTERVAL["to_vector"] = CALLS.get("to_vector", 0)
        return
    if moment - _INTERVAL["at"] < INTERVAL:
        return
    sites = {
        site: count - _INTERVAL["sites"].get(site, 0)
        for site, count in CALLERS.items()
    }
    diagnostics = {
        name: count - _INTERVAL["diagnostics"].get(name, 0)
        for name, count in DIAGNOSTICS.items()
    }
    crossed = CALLS.get("to_vector", 0) - _INTERVAL["to_vector"]
    say(
        f"  window {crossed:>7} to_vector over {moment - _INTERVAL['at']:5.1f} s"
        + "".join(
            f" {name}={count}" for name, count in sorted(diagnostics.items()) if count
        )
    )
    for site, count in sorted(sites.items(), key=lambda item: -item[1])[:4]:
        if count:
            say(f"     site {count:>7}  {site[0]}:{site[2]}:{site[1]}")
    _INTERVAL["at"] = moment
    _INTERVAL["sites"] = dict(CALLERS)
    _INTERVAL["diagnostics"] = dict(DIAGNOSTICS)
    _INTERVAL["to_vector"] = CALLS.get("to_vector", 0)


# --------------------------------------------------------------------------
# the sampler


def leaf_of(frame):
    """The deepest frame inside the package, with the chain below it.

    A frame is named ``file:function`` and its chain keeps the line, because a
    function's own line moves inside its loop while the function it is in is
    the thing a reader needs to see.
    """
    chain = []
    while frame is not None:
        code = frame.f_code
        if PACKAGE in code.co_filename:
            name = code.co_filename.rsplit("/", 1)[-1]
            chain.append((f"{name}:{code.co_name}", f"{name}:{frame.f_lineno}:{code.co_name}"))
        frame = frame.f_back
    return chain


def sample(main_identifier):
    frame = sys._current_frames().get(main_identifier)
    if frame is None:
        return None, ()
    chain = leaf_of(frame)
    if not chain:
        LEAVES["<outside the package>"] = LEAVES.get("<outside the package>", 0) + 1
        return "<outside the package>", ()
    leaf = chain[0][0]
    LEAVES[leaf] = LEAVES.get(leaf, 0) + 1
    trace = " <- ".join(name for _key, name in chain[:7])
    TRACES[trace] = TRACES.get(trace, 0) + 1
    return leaf, tuple(name for _key, name in chain[:7])


def sampler(main_identifier):
    previous = None
    last_report = now()
    first_of_run = {}
    while not _state.get("stop"):
        time.sleep(1.0)
        leaf, chain = sample(main_identifier)
        if leaf is None:
            continue
        if leaf == previous:
            _state["streak"] += 1
        else:
            _state["streak"] = 0
            previous = leaf
            first_of_run = {"leaf": leaf, "chain": chain, "at": now() - START,
                            "to_vector": CALLS.get("to_vector", 0)}
        if (
            _state["stage_started"] is None
            and _state["streak"] >= 8
            and CALLS.get("to_vector", 0) > first_of_run.get("to_vector", 0) + 200
        ):
            _state["stage_started"] = now()
            _state["next_window"] = now() + 30.0
            say(f"STAGE leaf {leaf} for {_state['streak'] + 1} consecutive samples")
            say(f"  chain: {chain}")
            say(f"  to_vector at stage start {CALLS.get('to_vector', 0)}")
        if now() - last_report >= 15.0:
            last_report = now()
            top = sorted(LEAVES.items(), key=lambda item: -item[1])[:3]
            sites = sorted(CALLERS.items(), key=lambda item: -item[1])[:5]
            say(
                f"  sampled {sum(LEAVES.values())} times; leaf now {leaf}; "
                f"to_vector={CALLS.get('to_vector', 0)}"
            )
            for name, count in top:
                say(f"     leaf {count:>4}  {name}")
            for site, count in sites:
                say(f"     site {count:>7}  {site[0]}:{site[2]}:{site[1]}")


def report(prefix=""):
    say(f"{prefix}=== leaf tally over {sum(LEAVES.values())} samples ===")
    for name, count in sorted(LEAVES.items(), key=lambda item: -item[1])[:12]:
        say(f"  {count:>5}  {name}")
    say(f"{prefix}=== the stacks sampled, as chains ===")
    for name, count in sorted(TRACES.items(), key=lambda item: -item[1])[:8]:
        say(f"  {count:>5}  {name}")
    say(f"{prefix}=== the counted elements ===")
    for name, count in sorted(DIAGNOSTICS.items(), key=lambda item: -item[1]):
        say(f"  {name:<24}{count:>10}")
    say(f"{prefix}=== to_vector call sites, {CALLS.get('to_vector', 0)} calls ===")
    for site, count in sorted(CALLERS.items(), key=lambda item: -item[1])[:15]:
        say(f"  {count:>7}  {site[0]}:{site[2]}:{site[1]}")
    say(f"{prefix}=== to_vector by the class of the parent ===")
    for name, spent in sorted(SECONDS.items(), key=lambda item: -item[1])[:8]:
        say(f"  {name:<52}{SECONDS[name]:>10.3f} s")


def main():
    global COUNTING
    cap = 540.0
    for argument in sys.argv[1:]:
        if argument.startswith("cap="):
            cap = float(argument.split("=", 1)[1])
    shadowed = shadow_to_vector()
    say("shadowed to_vector at:", ", ".join(shadowed) if shadowed else "nothing")
    say("timed:", instrument_spanning())
    counted = wrap_diagnostics()
    say("counted:", ", ".join(counted) if counted else "nothing")
    lattice = NamedLattices.Tco
    group = lattice.stable_orthogonal_group()
    say(f"lattice {lattice}; subgroup {group}")
    main_identifier = threading.main_thread().ident
    # A sampler thread needs the GIL, and the stages below spend minutes inside
    # single C calls (PARI's and GAP's) that hold it.  faulthandler's watchdog is
    # a C thread and dumps every thread's Python stack without taking the GIL,
    # so the log carries a stack through exactly the stretches the sampler
    # cannot see.
    faulthandler.enable()
    faulthandler.dump_traceback_later(SAMPLE_SECONDS, repeat=True)
    # The samplers read the main thread's stack; a wrapper around the crossing
    # opens the profiling windows, so nothing else touches the profiler.
    count_sampler = threading.Thread(target=sampler, args=(main_identifier,), daemon=True)
    count_sampler.start()
    begin = now()
    decided = True
    planes = None
    try:
        planes = tuple(group.isotropic_orbit_representatives(2))
    except Exception as error:  # noqa: BLE001 - the row's own failure is the datum
        decided = False
        say(f"the row raised {type(error).__name__}: {error}")
        traceback.print_exc()
    finally:
        _state["stop"] = True
        COUNTING = False
        spent = now() - begin
    if _state["profiler"] is not None:
        _state["profiler"].disable()
        _state["profiler"] = None
    say("")
    say(f"the Otilde row: {spent:.1f} s, decided {decided}, cap {cap:.0f} s")
    if planes is not None:
        say(f"planes: {len(planes)}")
    report()
    say(
        f"RESULT otilde_seconds={spent:.1f} decided={decided} "
        f"stage_started={_state['stage_started'] is not None} "
        f"windows={_state['windows_done']} to_vector={CALLS.get('to_vector', 0)} "
        f"samples={sum(LEAVES.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
