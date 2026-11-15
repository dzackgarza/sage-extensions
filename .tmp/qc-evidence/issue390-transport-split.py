r"""#390 probe M: split the plane transport and place the growth.

Measures, on one run of the public call

    NamedLattices.Tco.stable_orthogonal_group().isotropic_orbit_representatives(2)

-- the ``Otilde(T_Co)`` plane row of #390 -- the four steps of
``LatticeIsometry.transport_isotropic_object``'s subobject branch,

    product     self * obj.inclusion()
    image       (that product).image()
    basis       image.inclusion().domain() and the generators read from it
    admission   self.codomain().primitive_isotropic_subobject(*basis)

and, in fixed windows of transported planes, the object counts and cache
sizes that grow.  The row is the public call; no library code is changed and
the instrumentation is installed in this process only.

Why the split is installed where it is
--------------------------------------
The previous run (``issue390-stage-slice.log``) patched
``Lattices.ParentMethods.primitive_isotropic_subobject`` with a plain
function and the row answered that patch **once**.  The reason is Sage's
``CachedMethod.__get__``: on the first call it builds a
``CachedMethodCaller`` bound to the lattice and stores it as an attribute of
the instance (or in ``inst._cached_methods``), and from then on attribute
lookup finds the instance's own caller and never reaches the class
attribute at all.  This probe keeps the cache in force but not the
shortcut: each wrapper resolves the real caller through the descriptor,
then removes the instance-level entry, so the next call is timed again while
``inst.__dict__['_cache__<name>']`` -- the dict the caller holds -- is the
same one throughout.  The same wrapper is used for the other cached methods
of the four steps.  Where a step's method is a plain function (``image``,
``subobject_on``, ``is_primitive``, ``refine``) the wrapper is a plain one.

The transport itself is replaced by a function that reproduces the branch's
four steps with a clock around each; the flag branch is handed to the
original.  The reproduction is checked against the original on the first
three calls: both are run and the two planes' embedded generators are
compared, and any divergence is reported (a divergence would make every row
below a measurement of something else).

What each window records
------------------------
A window is ``WINDOW`` transported planes; the snapshot before the row is
window ``-1``, so window 0 is the first plane.  At a window's close the probe
writes

* the mean time per call of each of the four steps, of the whole transport
  call, and of the admission's own interior (``subobject_on``,
  ``is_primitive``, ``refine``) -- those three are recorded only when the
  call is inside the admission step, because the row calls them elsewhere
  too and those calls are not this measurement;
* ``gc.get_objects()`` counted by type name with the growth against the
  previous window (top rows), the process RSS, and the live-object total --
  the "what grows" half of the question;
* the sizes of the caches the four steps fill: every ``_cache__*`` dict on
  the lattice and on every live instance of the types the steps create (one
  pass over the live objects, in the same pass as the type counts), and the
  ``__classcall__.cache`` of each class those instances -- and the lattice
  and its category -- construct through, i.e. the
  ``UniqueRepresentation``/``CachedRepresentation`` tables that would retain
  or re-scan something as the row advances;
* the cyclic collector's own cost inside the window (count and seconds from
  ``gc.callbacks``), because a per-call cost that rises with the heap is
  charged to whichever call allocates the most, and that is not the step's
  algorithm.

The snapshot's own cost is written with it, so a reader can see the
measurement's footprint in the numbers around it, and the admission wrapper's
overhead is reported as the difference between the admission step and the
method it times.

    sage -python <this file>              # the Otilde row on T_Co, cap 2700 s
    sage -python <this file> cap=600      # the same row truncated
    sage -python <this file> window=N     # windows of N planes instead of 250
    sage -python <this file> detail=image # also split the image step: the
                                          # span constructor it calls, timed
                                          # apart from the rest of the step
    sage -python <this file> detail=span  # also split subobject_on itself into
                                          # its span basis and its subobject
                                          # construction
    sage -python <this file> smoke        # U + U(2) + <-2>, whose Otilde row
                                          # returns 2 planes: the check that
                                          # the split and the windows work
"""

import gc
import sys
import threading
import time
import traceback
from collections import Counter

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories import lattice_morphisms as lm

START = time.monotonic()
ROW_CAP = 2700
WINDOW = 250
SAMPLE_SECONDS = 5.0


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


# ---------------------------------------------------------------- the steps

STEPS = ("product", "image", "basis", "admission")
# The interior of two steps, timed from wrappers on the methods they call.
INNER_LABELS = (
    "admission.subobject_on",
    "admission.is_primitive",
    "admission.refine",
    "primitive_isotropic_subobject (method)",
    "image (whole)",
    "image.subobject_on",
    "span basis",
    "span construction",
)
STATE = {
    "planes": 0,
    "flag_branch": 0,
    "window": 0,
    "done": False,
    "verified": [],
    "verify_failures": 0,
    "patched": [],
}
WINDOWS = {}      # window -> {step: [seconds, calls]}
COUNTERS = {}     # window -> Counter of object types
CACHES = {}       # window -> {(owner, name): [owners, entries]}
CLASS_CACHES = {}  # window -> {class name: entries}
RSS = {}          # window -> VmRSS in MiB
GC_ROWS = {}      # window -> [collections, seconds]
_LOCK = threading.Lock()


def add(window, name, seconds):
    row = WINDOWS.setdefault(window, {})
    cell = row.setdefault(name, [0.0, 0])
    cell[0] += seconds
    cell[1] += 1


def add_in_transport(name, seconds):
    """Record a call of a helper the transport's steps reach."""
    if STATE.get("in_transport"):
        add(STATE["window"], name, seconds)


def add_nested(name, seconds):
    """Record a call made inside one of the transport's own steps, and only one.

    ``subobject_on``, ``is_primitive`` and ``refine`` are also called all over
    the row outside the transport; those calls are not this measurement.  A
    call made while the transport's ``image`` step runs is booked to
    ``image.<name>`` -- that step builds its image by the same span
    constructor -- and any other call is dropped.
    """
    if STATE.get("in_admission"):
        add(STATE["window"], name, seconds)
    elif STATE.get("detail_image") and STATE.get("in_image"):
        add(STATE["window"], "image." + name.split(".", 1)[1], seconds)


# --------------------------------------------------- cache-preserving wrap

def _resolving_class(obj, name):
    for klass in type(obj).__mro__:
        if name in vars(klass):
            return klass
    raise RuntimeError(f"no class of {type(obj)!r} defines {name}")


def _drop_instance_shortcut(instance, name):
    """Remove the bound caller Sage stored on the instance, keeping its cache.

    ``CachedMethod.__get__`` stores the caller as an attribute of the instance
    so that later lookups skip the descriptor; the cache itself lives in
    ``instance.__dict__['_cache__' + name]`` and is untouched here.
    """
    try:
        instance.__dict__.pop(name, None)
    except AttributeError:
        pass
    try:
        table = instance._cached_methods
    except AttributeError:
        return
    if isinstance(table, dict):
        table.pop(name, None)


def wrap_step(instance_or_class, name, label, *, cached=None, into_steps=None, flag=None):
    """Wrap ``name`` where ``instance_or_class`` resolves it; keep its cache.

    ``cached=None`` means "ask the descriptor": a ``CachedMethod`` is resolved
    through itself on every call and the instance shortcut is dropped, a plain
    function is called directly.
    """
    target = instance_or_class
    if isinstance(target, type):
        klass = next(k for k in target.__mro__ if name in vars(k))
    else:
        klass = _resolving_class(target, name)
    original = vars(klass)[name]
    is_cached = cached
    if is_cached is None:
        is_cached = type(original).__name__ in ("CachedMethod", "CachedMethodCaller")

    if is_cached:
        def timed(self, *args, __original=original, __label=label,
                  __name=name, __steps=into_steps, __flag=flag, **kwargs):
            caller = __original.__get__(self, type(self))
            _drop_instance_shortcut(self, __name)
            begin = _now()
            if __flag:
                STATE[__flag] = True
            try:
                outcome = caller(*args, **kwargs)
            finally:
                if __flag:
                    STATE[__flag] = False
            spent = _now() - begin
            if __steps is None:
                add_nested(__label, spent)
            else:
                add(STATE["window"], __steps, spent)
            return outcome
    else:
        def timed(self, *args, __original=original, __label=label,
                  __steps=into_steps, __flag=flag, **kwargs):
            function = __original.__get__(self, type(self)) if hasattr(
                __original, "__get__") else __original
            begin = _now()
            if __flag:
                STATE[__flag] = True
            try:
                outcome = function(*args, **kwargs)
            finally:
                if __flag:
                    STATE[__flag] = False
            spent = _now() - begin
            if __steps is None:
                add_nested(__label, spent)
            else:
                add(STATE["window"], __steps, spent)
            return outcome

    setattr(klass, name, timed)
    STATE["patched"].append(
        f"{label}: {name} on {klass.__module__}.{klass.__qualname__} "
        f"({'CachedMethod' if is_cached else type(original).__name__})"
    )
    return klass


# ------------------------------------------------------- the measured table

ORIGINAL_TRANSPORT = None


def _plane_generators(plane):
    """The generators of a subobject, as coordinate vectors in its ambient."""
    embedded = plane.embedded_module_generators()
    return tuple(
        tuple(int(coordinate) for coordinate in embedded[label].to_vector())
        for label in plane.module_generating_set()
    )


def instrumented_transport(self, obj):
    clock = time.perf_counter
    from sage_extensions.categories.modules.pure.modules import ModuleSubobjects

    if not (obj in ModuleSubobjects(self.codomain().base_ring())):
        STATE["flag_branch"] += 1
        return ORIGINAL_TRANSPORT(self, obj)

    planes = STATE["planes"]
    if planes % WINDOW == 0 and planes != STATE.get("_window_floor"):
        # A boundary is closed before its successor's first call, so every
        # number below belongs to exactly one window -- and the window is read
        # after the close, not before it.
        close_window(planes)
        STATE["_window_floor"] = planes
    window = STATE["window"]

    if STATE.get("detail_image") or STATE.get("detail_span"):
        STATE["in_transport"] = True
    mark = clock()
    product = self * obj.inclusion()
    after_product = clock()
    if STATE.get("detail_image") and not STATE.get("image_wrapped"):
        STATE["image_wrapped"] = True
        wrap_step(product, "image", "image (whole)", cached=True, flag="in_image")
        log("  inside the image step: image and subobject_on are timed from here")
    image = product.image()
    after_image = clock()
    domain = image.inclusion().domain()
    basis = tuple(
        image.inclusion()(domain.module_generator(label))
        for label in domain.module_generating_set()
    )
    after_basis = clock()
    STATE["in_admission"] = True
    try:
        moved = self.codomain().primitive_isotropic_subobject(*basis)
    finally:
        STATE["in_admission"] = False
    after_admission = clock()
    if STATE.get("detail_image") or STATE.get("detail_span"):
        STATE["in_transport"] = False

    if len(STATE["verified"]) < 3:
        reference = ORIGINAL_TRANSPORT(self, obj)
        same = _plane_generators(reference) == _plane_generators(moved)
        STATE["verified"].append(
            f"call {planes}: rank {moved.module_rank()} vs {reference.module_rank()}, "
            f"generators equal: {same}"
        )
        if not same:
            STATE["verify_failures"] += 1

    add(window, "product", after_product - mark)
    add(window, "image", after_image - after_product)
    add(window, "basis", after_basis - after_image)
    add(window, "admission", after_admission - after_basis)
    add(window, "call (four steps + framing)", after_admission - mark)
    STATE["planes"] = planes + 1

    if not STATE.get("resolved"):
        STATE["resolved"] = True
        log(
            "first transport resolved: codomain is the row's lattice: "
            f"{self.codomain() is STATE['lattice']}; product {type(product).__name__}, "
            f"image {type(image).__name__}, plane {type(moved).__name__}"
        )
        for label, value in (
            ("product", product),
            ("image", image),
            ("plane", moved),
        ):
            try:
                log(f"  {label} class: {type(value).__module__}.{type(value).__qualname__}")
                TRACKED_TYPES.append(type(value))
            except Exception:  # pragma: no cover - reporting only
                pass
        try:
            wrap_step(moved, "is_primitive", "admission.is_primitive")
        except Exception as failure:  # pragma: no cover - reporting only
            log(f"  is_primitive not wrapped: {failure!r}")
        for label, klass in discover_class_caches(
            moved, product, image, STATE["lattice"], STATE["lattice"].category()
        ):
            TRACKED_CLASS_CACHES.append((label, klass))
        if TRACKED_CLASS_CACHES:
            log(
                "  class-level tables followed: "
                + ", ".join(label for label, _klass in TRACKED_CLASS_CACHES)
            )
        else:
            log("  class-level tables followed: none of the reached classes has one")
    return moved


# -------------------------------------------------- what grows: the snapshot

TRACKED_TYPES = []
TRACKED_CLASS_CACHES = []
SNAPSHOT_COST = []


def _object_table(previous):
    """One pass over the live objects: type counts, and the caches by owner."""
    counts = Counter()
    caches = {}
    tracked = set(TRACKED_TYPES) | {type(STATE["lattice"])}
    for obj in gc.get_objects():
        name = type(obj).__name__
        counts[name] += 1
        if type(obj) in tracked:
            try:
                namespace = object.__getattribute__(obj, "__dict__")
            except Exception:
                continue
            for key, value in namespace.items():
                if not key.startswith("_cache__"):
                    continue
                try:
                    size = len(value)
                except TypeError:
                    size = 1
                cell = caches.setdefault((name, key), [0, 0])
                cell[0] += 1
                cell[1] += size
    growth = Counter({name: counts[name] - previous.get(name, 0) for name in counts})
    return counts, caches, growth


def _classcall_cache(klass):
    """The ``UniqueRepresentation`` table a class constructs through, if any."""
    for base in klass.__mro__:
        raw = vars(base).get("__classcall__")
        if raw is None:
            continue
        function = raw.__func__ if isinstance(raw, staticmethod) else raw
        table = getattr(function, "cache", None)
        if table is not None:
            return table
    return None


def discover_class_caches(*instances):
    """The class-level tables the instances' own classes construct through."""
    found = []
    labels = set()
    for instance in instances:
        families = [type(instance)]
        category = getattr(instance, "category", None)
        if category is not None:
            families.append(type(category))
        for family in families:
            klass = family
            table = _classcall_cache(klass)
            if table is None:
                continue
            label = f"{klass.__name__}.__classcall__.cache"
            if label in labels:
                continue
            labels.add(label)
            found.append((label, klass))
    return found


def _class_tables():
    rows = {}
    for label, klass in TRACKED_CLASS_CACHES:
        table = _classcall_cache(klass)
        if table is None:
            continue
        try:
            rows[label] = len(table)
        except TypeError:
            rows[label] = -1
    return rows


def close_window(planes):
    window = STATE["window"]
    begin = _now()
    counts, caches, growth = _object_table(COUNTERS.get(window - 1, Counter()))
    class_tables = _class_tables()
    spent = _now() - begin
    SNAPSHOT_COST.append((window, spent))
    COUNTERS[window] = counts
    CACHES[window] = caches
    CLASS_CACHES[window] = class_tables
    RSS[window] = _status_mib("VmRSS:")
    STATE.setdefault("_window_end", {})[window] = planes

    row = WINDOWS.setdefault(window, {})
    held = row.get("call (four steps + framing)", [0.0, 0])[1]
    log("")
    log(
        f"--- window {window}: planes [{planes - held}, {planes}) "
        f"mean ms per call ---"
    )
    for step in STEPS + ("call (four steps + framing)",):
        cell = row.get(step)
        if not cell:
            continue
        log(f"    {step:<34} n={cell[1]:>6}  {1000 * cell[0] / cell[1]:9.2f} ms")
    for step in INNER_LABELS:
        cell = row.get(step)
        if not cell:
            continue
        log(f"      in a step: {step:<22} n={cell[1]:>6}  {1000 * cell[0] / cell[1]:9.2f} ms")
    log(
        f"    snapshot cost {spent:.1f} s; rss {_status_mib('VmRSS:'):.0f} MiB; "
        f"objects {sum(counts.values())} (previous "
        f"{sum(COUNTERS[window - 1].values()) if window - 1 in COUNTERS else 0})"
    )
    if window - 1 in COUNTERS:
        top = Counter(
            {name: COUNTERS[window][name] - COUNTERS[window - 1].get(name, 0)
             for name in COUNTERS[window]}
        )
        log("    top growth by type: " + ", ".join(
            f"{name} +{count}" for name, count in top.most_common(6) if count > 0
        ))
        lost = Counter(
            {name: COUNTERS[window - 1][name] - COUNTERS[window].get(name, 0)
             for name in COUNTERS[window - 1]}
        )
        log("    top shrink by type: " + ", ".join(
            f"{name} -{count}" for name, count in lost.most_common(3) if count > 0
        ))
    for (owner, key), (owners, entries) in sorted(
        caches.items(), key=lambda pair: -pair[1][1]
    )[:6]:
        log(f"    cache {owner}.{key}: {owners} owner(s), {entries} entrie(s)")
    for label, size in sorted(class_tables.items(), key=lambda pair: -pair[1])[:6]:
        log(f"    class cache {label}: {size}")
    STATE["window"] = window + 1


# --------------------------------------------------------- collector cost

GC_TOTALS = {"collections": 0, "seconds": 0.0, "generation": []}
_GC_START = {}


def _gc_callback(phase, info):
    if phase == "start":
        _GC_START["t"] = _now()
        return
    begin = _GC_START.pop("t", None)
    if begin is None:
        return
    spent = _now() - begin
    GC_TOTALS["collections"] += 1
    GC_TOTALS["seconds"] += spent
    row = GC_ROWS.setdefault(STATE["window"], [0, 0.0])
    row[0] += 1
    row[1] += spent


# ------------------------------------------------------------------- report

class RowUndecided(Exception):
    pass


def _alarm(signum, frame):
    raise RowUndecided


def report(row_seconds, decided, count):
    if STATE["planes"] > STATE.get("_window_floor", 0):
        close_window(STATE["planes"])
        STATE["_window_floor"] = STATE["planes"]
    log("")
    log("=== patched ===")
    for line in STATE["patched"]:
        log("  " + line)
    log(f"flag branch calls: {STATE['flag_branch']}")
    log(
        "the interior labels count only calls made inside the transport's own "
        "steps; 'image.' ones inside its image step, the others inside its "
        "admission step unless they are the span rows, which cover both"
    )
    log("the instrumented branch against the original on the first calls:")
    for line in STATE["verified"]:
        log("  " + line)
    log(f"  divergences: {STATE['verify_failures']}")

    log("")
    log("=== mean ms per call, by window of %d planes ===" % WINDOW)
    columns = STEPS + INNER_LABELS + ("call (four steps + framing)",)
    short = {
        "product": "product",
        "image": "image",
        "basis": "basis",
        "admission": "admission",
        "admission.subobject_on": "subobj",
        "admission.is_primitive": "prim",
        "admission.refine": "refine",
        "primitive_isotropic_subobject (method)": "method",
        "image (whole)": "img all",
        "image.subobject_on": "img span",
        "span basis": "span def",
        "span construction": "span ctor",
        "call (four steps + framing)": "call",
    }
    log(f"{'window':>6}{'planes':>14}" + "".join(f"{short.get(c, c):>10}" for c in columns)
        + f"{'gc s':>9}{'rss':>8}")
    for window in sorted(WINDOWS):
        row = WINDOWS[window]
        if not row.get("call (four steps + framing)"):
            continue
        cells = ""
        for column in columns:
            cell = row.get(column)
            cells += f"{1000 * cell[0] / cell[1]:10.2f}" if cell else f"{'-':>10}"
        call = row["call (four steps + framing)"]
        high = STATE["_window_end"].get(window, call[1])
        low = high - call[1]
        gc_row = GC_ROWS.get(window, [0, 0.0])
        log(
            f"{window:>6}{f'[{low},{high})':>14}{cells}"
            f"{gc_row[1]:9.2f}{RSS.get(window, float('nan')):8.0f}"
        )
    log("")
    log("=== first window against last (mean ms per call) ===")
    windows = [
        window for window in sorted(WINDOWS)
        if WINDOWS[window].get("call (four steps + framing)")
    ]
    if len(windows) >= 2:
        first, last = windows[0], windows[-1]
        for step in STEPS + INNER_LABELS + ("call (four steps + framing)",):
            left = WINDOWS[first].get(step)
            right = WINDOWS[last].get(step)
            if not left or not right:
                continue
            a = 1000 * left[0] / left[1]
            b = 1000 * right[0] / right[1]
            log(
                f"  {step:<32} window {first}: {a:9.2f}  window {last}: {b:9.2f}  "
                f"ratio {b / a if a else float('nan'):6.2f}"
            )
    log("")
    log("=== the admission wrapper's own cost (step minus the method it times) ===")
    for window in sorted(WINDOWS):
        row = WINDOWS[window]
        outside = row.get("admission")
        inside = row.get("primitive_isotropic_subobject (method)")
        if not outside or not inside:
            continue
        log(
            f"  window {window}: admission {1000 * outside[0] / outside[1]:8.2f} ms, "
            f"method {1000 * inside[0] / inside[1]:8.2f} ms, "
            f"wrapper {1000 * (outside[0] - inside[0]) / outside[1]:6.2f} ms per call"
        )
    log("")
    log("=== the cyclic collector ===")
    log(
        f"  {GC_TOTALS['collections']} collections, {GC_TOTALS['seconds']:.1f} s "
        f"inside them, over {row_seconds:.1f} s of row"
    )
    for window in sorted(GC_ROWS):
        calls = WINDOWS.get(window, {}).get("call (four steps + framing)")
        transport = calls[0] if calls else 0.0
        if not calls or calls[1] < 10:
            log(
                f"  window {window}: {GC_ROWS[window][0]} collections "
                f"{GC_ROWS[window][1]:.1f} s (no window of calls to divide by)"
            )
            continue
        log(
            f"  window {window}: {GC_ROWS[window][0]} collections "
            f"{GC_ROWS[window][1]:.1f} s, transport {transport:.1f} s "
            f"({100.0 * GC_ROWS[window][1] / transport if transport else float('nan'):.1f}%)"
        )
    log("")
    log("=== cache tables, entries by window ===")
    keys = sorted({key for table in CACHES.values() for key in table})
    for key in keys:
        cells = []
        for window in sorted(CACHES):
            cell = CACHES[window].get(key)
            cells.append(f"{cell[1]}" if cell else "-")
        if len(set(cells)) == 1:
            continue
        log(f"  {key[0]}.{key[1]}: " + " ".join(cells))
    classes = sorted({label for table in CLASS_CACHES.values() for label in table})
    for label in classes:
        cells = [str(CLASS_CACHES[window].get(label, "-")) for window in sorted(CLASS_CACHES)]
        log(f"  {label}: " + " ".join(cells))
    log("")
    ordered = [COUNTERS[window] for window in sorted(COUNTERS)]
    if len(ordered) >= 2:
        log("=== object count by type, first snapshot against last ===")
        first, last = ordered[0], ordered[-1]
        growth = Counter({name: last[name] - first.get(name, 0) for name in last})
        for name, increase in growth.most_common(10):
            log(f"  {name:<44}{first.get(name, 0):>9} -> {last[name]:>9}  ({increase:+})")
        for name, drop in Counter(
            {name: first[name] - last.get(name, 0) for name in first}
        ).most_common(5):
            if drop > 0:
                log(f"  {name:<44}{first[name]:>9} -> {last.get(name, 0):>9}  (-{drop})")
    log("")
    log(f"transported planes: {STATE['planes']}, flag-branch calls: {STATE['flag_branch']}")
    log(f"row wall time: {row_seconds:.1f} s, decided: {decided}")
    if count is not None:
        log(f"the row returned {count} planes")
    log(f"peak VmHWM: {_status_mib('VmHWM:'):.0f} MiB")


def main(argv):
    global ROW_CAP, WINDOW
    for argument in argv:
        if argument.startswith("cap="):
            ROW_CAP = int(argument.split("=", 1)[1])
        if argument.startswith("window="):
            WINDOW = int(argument.split("=", 1)[1])
        if argument.startswith("detail="):
            chosen = argument.split("=", 1)[1]
            STATE["detail_image"] = chosen == "image"
            STATE["detail_span"] = chosen == "span"
    smoke = bool(argv) and argv[0] == "smoke"

    import sage_extensions
    import hashlib
    from pathlib import Path

    log(
        "probe M: split the plane transport of the Otilde plane row (#390)"
        + (" -- smoke run on U + U(2) + <-2>" if smoke else "")
    )
    log(f"cap {ROW_CAP} s, python {sys.version.split()[0]}")
    log(f"sage_extensions from {sage_extensions.__file__}")
    source = Path(sage_extensions.__file__).parent
    for name in (
        "categories/lattice_morphisms.py",
        "categories/lattices.py",
        "categories/orthogonal_quotients.py",
        "categories/isotropic_parabolics.py",
    ):
        digest = hashlib.sha256((source / name).read_bytes()).hexdigest()
        log(f"  source {name}: {digest[:16]}")

    lattice = (
        Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
        if smoke
        else NamedLattices.Tco
    )
    STATE["lattice"] = lattice
    log(f"lattice {lattice} of rank {lattice.module_rank()}")
    stable = lattice.stable_orthogonal_group()
    log("Otilde = lattice.stable_orthogonal_group()")

    global ORIGINAL_TRANSPORT
    klass = _resolving_class(stable.one(), "transport_isotropic_object")
    ORIGINAL_TRANSPORT = vars(klass)["transport_isotropic_object"]
    log(f"transport defined on {klass.__module__}.{klass.__qualname__}")
    resolved = _resolving_class(lattice, "primitive_isotropic_subobject")
    log(
        f"primitive_isotropic_subobject resolves on {resolved.__module__}.{resolved.__qualname__} "
        f"({type(vars(resolved)['primitive_isotropic_subobject']).__name__})"
    )
    wrap_step(lattice, "primitive_isotropic_subobject",
              "primitive_isotropic_subobject (method)", cached=True)
    for owner, name in ((lattice, "subobject_on"), (lattice, "stable_orthogonal_group")):
        if name == "subobject_on":
            wrap_step(owner, name, "admission." + name)
    # ``is_primitive`` and ``refine`` are reached from inside the admission;
    # both are patched on the first plane the transport produces.
    oq = __import__("sage_extensions.categories.orthogonal_quotients", fromlist=["x"])
    original_subgroup_row = oq._subgroup_isotropic_orbit_representatives

    def subgroup_row(*args, **kwargs):
        outcome = original_subgroup_row(*args, **kwargs)
        log(f"the subgroup row held {len(outcome)} planes before the public call wrapped it")
        return outcome

    oq._subgroup_isotropic_orbit_representatives = subgroup_row
    import sage_extensions.categories.group.predicate_subgroups as predicate_subgroups

    predicate_subgroups._subgroup_isotropic_orbit_representatives = subgroup_row
    import sage_extensions.categories.lattices as lattice_module

    if STATE.get("detail_span"):
        for helper, label in (
            ("_span_basis_elements", "span basis"),
            ("_lattice_subobject_spanning", "span construction"),
        ):
            original_helper = getattr(lattice_module, helper)

            def timed_helper(*args, __original=original_helper, __label=label, **kwargs):
                begin = _now()
                outcome = __original(*args, **kwargs)
                add_in_transport(__label, _now() - begin)
                return outcome

            setattr(lattice_module, helper, timed_helper)
            STATE["patched"].append(
                f"{label}: {helper} in sage_extensions.categories.lattices (function)"
            )

    original_refine = lattice_module.refine

    def timed_refine(*args, **kwargs):
        begin = _now()
        outcome = original_refine(*args, **kwargs)
        add_nested("admission.refine", _now() - begin)
        return outcome

    lattice_module.refine = timed_refine
    STATE["patched"].append(
        f"admission.refine: {getattr(original_refine, '__module__', '?')}.refine (function)"
    )
    setattr(klass, "transport_isotropic_object", instrumented_transport)
    STATE["patched"].append(
        f"transport: transport_isotropic_object on {klass.__module__}.{klass.__qualname__} "
        "(replaced by the clocked branch)"
    )

    gc.callbacks.append(_gc_callback)
    log(f"gc enabled: {gc.isenabled()}, thresholds {gc.get_threshold()}")
    # The baseline is window -1: the first window of transported planes is 0.
    STATE["window"] = -1
    close_window(0)
    STATE["_window_floor"] = 0

    signal_module = __import__("signal")
    signal_module.signal(signal_module.SIGALRM, _alarm)
    log("calling stable.isotropic_orbit_representatives(2)")
    begin = _now()
    decided = True
    planes = None
    try:
        signal_module.setitimer(signal_module.ITIMER_REAL, ROW_CAP)
        row_object = stable.isotropic_orbit_representatives(2)
        log(
            f"the call returned {type(row_object).__module__}."
            f"{type(row_object).__qualname__} holding {len(row_object)}"
        )
        planes = tuple(row_object)
        log(f"iterated to {len(planes)} planes")
    except RowUndecided:
        decided = False
        log(f"the row did not return inside its {ROW_CAP} s cap")
    except Exception:
        decided = False
        log("the row raised:")
        traceback.print_exc()
    finally:
        signal_module.setitimer(signal_module.ITIMER_REAL, 0)
        row_seconds = _now() - begin
    STATE["done"] = True
    count = None
    if planes is not None:
        count = len(planes)
        primitive = all(plane.is_primitive() is True for plane in planes[:20])
        log(f"the first 20 planes primitive: {primitive}")
    report(row_seconds, decided, count)
    log("PROBE M DONE")
    return 0 if decided else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
