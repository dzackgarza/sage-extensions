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
    sage -python <this file> detail=basis # also split the sublattice
                                          # construction into its five steps
    sage -python <this file> coercion     # also census the coercion and action
                                          # containers of the ambient lattice,
                                          # its free module and its base ring
    sage -python <this file> profile      # also profile one early and one late
                                          # window of 40 calls and compare them
    sage -python <this file> smoke        # U + U(2) + <-2>, whose Otilde row
                                          # returns 2 planes: the check that
                                          # the split and the windows work
"""

import cProfile
import gc
import os
import pstats
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


def _load():
    """The machine's one-minute load and its core count: the row shares the VM."""
    try:
        with open("/proc/loadavg") as handle:
            load = float(handle.read().split()[0])
    except OSError:
        load = float("nan")
    return load, os.cpu_count()


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
LOADS = {}        # window -> (load average 1 min, cores)
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


# ------------------------- the sublattice construction, split (detail=basis)

# The call graph inside ``_lattice_subobject_spanning``, parent first.  The
# report subtracts a parent's children from it to get the parent's own time:
# ``_lattice_subobject_spanning`` is the whole construction,
# ``_lattice_object`` is one of its children and
# ``_form_module_from_bilinear_computation`` one of ``_lattice_object``'s, whose
# own children are the inclusion and the parent construction.
BASIS_LABELS = (
    "span construction",
    "ctor data",
    "fresh module",
    "gram tensor",
    "lattice object",
    "form module",
    "inclusion",
    "module with structure",
)
BASIS_CHILDREN = {
    "span construction": ("ctor data", "fresh module", "gram tensor", "lattice object"),
    "lattice object": ("form module",),
    "form module": ("inclusion", "module with structure"),
}
BASIS_INNER = ("span construction", "lattice object", "form module")

# What the coercion census reads on each parent: ``Parent._introspect_coerce``
# is the coercion model's own debugging view of those containers, and it hands
# back the live objects, so a length is a length now and not a copy.
COERCION_KEYS = (
    "_coerce_from_list",
    "_convert_from_list",
    "_action_list",
    "_coerce_from_hash",
    "_convert_from_hash",
    "_embedding",
)
COERCION_TARGETS = []
COERCION_ROWS = {}     # window -> {target: {key: length}}
REGISTRATIONS = {}     # window -> {target: {call: count}}
LAST_PLANE = []        # the most recently transported plane, for the census

FRAMES = []


class _Nest:
    """Open a construction frame; the innermost finished frame charges its time.

    A construction step calls another, so a call's own cost is its wall time
    with the time of every frame opened inside it subtracted -- the same
    accounting probe J used for the row's stages, here inside one step.
    """

    def __init__(self, label):
        self.label = label

    def __enter__(self):
        self.begin = _now()
        self.children = 0.0
        self.opened = 0
        FRAMES.append(self)
        return self

    def __exit__(self, *exception):
        elapsed = _now() - self.begin
        FRAMES.pop()
        if STATE.get("in_transport"):
            add(STATE["window"], self.label, elapsed)
            add(STATE["window"], self.label + " own", elapsed - self.children)
        if FRAMES:
            FRAMES[-1].opened += 1
            if STATE.get("in_transport"):
                FRAMES[-1].children += elapsed
        if (
            STATE.get("trace")
            and STATE.get("in_transport")
            and self.label.startswith(STATE["trace"][0])
            and STATE["trace"][1] < 8
        ):
            STATE["trace"][1] += 1
            log(
                f"    trace {self.label}: {1000 * elapsed:.2f} ms, "
                f"{self.opened} child frame(s), {1000 * self.children:.2f} ms in them, "
                f"caller {STATE['trace'][2]}"
            )
        return False


def needs_transport_flag():
    return any(
        STATE.get(key)
        for key in ("detail_image", "detail_span", "detail_basis", "profile")
    )


def wrap_function(namespace, name, label):
    """Wrap a module-level function, recording only calls made in the transport."""
    original = getattr(namespace, name)

    def timed(*args, __original=original, __label=label, **kwargs):
        # Outside the transport this function is the library's own, untouched:
        # the row's setup calls ``tensor`` and the constructors constantly, and
        # a frame per call there would change the tree it is measuring.
        if not STATE.get("in_transport"):
            return __original(*args, **kwargs)
        if STATE.get("trace"):
            caller = sys._getframe(1).f_code.co_name
            STATE["trace"][2] = caller
        with _Nest(__label):
            return __original(*args, **kwargs)

    setattr(namespace, name, timed)
    STATE["patched"].append(
        f"{label}: {name} in {getattr(namespace, '__name__', '?')} (function)"
    )


def wrap_method_gated(instance, name, label):
    """Wrap a plain method on the class ``instance`` resolves it on."""
    klass = (
        next(k for k in instance.__mro__ if name in vars(k))
        if isinstance(instance, type)
        else _resolving_class(instance, name)
    )
    original = vars(klass)[name]

    def timed(self, *args, __original=original, __label=label, **kwargs):
        function = (
            __original.__get__(self, type(self)) if hasattr(__original, "__get__") else __original
        )
        if not STATE.get("in_transport"):
            return function(*args, **kwargs)
        with _Nest(__label):
            return function(*args, **kwargs)

    setattr(klass, name, timed)
    STATE["patched"].append(
        f"{label}: {name} on {klass.__module__}.{klass.__qualname__} ({type(original).__name__})"
    )


def install_constructor_split(lattice, ring):
    """Split ``_lattice_subobject_spanning`` into the steps it takes."""
    import sage_extensions.categories.lattices as lattice_module
    import sage_extensions.categories.modules.framed.formed.form_modules as form_modules

    wrap_function(lattice_module, "_span_basis_elements", "span basis")
    wrap_function(lattice_module, "_lattice_subobject_spanning", "span construction")
    wrap_function(lattice_module, "_module_subobject_constructor_data", "ctor data")
    wrap_function(lattice_module, "tensor", "gram tensor")
    wrap_method_gated(ring, "_fresh_free_module_on", "fresh module")
    wrap_function(
        form_modules, "_form_module_from_bilinear_computation", "form module"
    )
    # ``_lattice_object`` is handed the source module, and it is that module's
    # own ``Emb`` and ``_module_with_structure`` that build the inclusion and
    # the parent: both are patched the first time it is reached.
    original_object = lattice_module._lattice_object

    def timed_lattice_object(*args, __original=original_object, **kwargs):
        if not STATE.get("in_transport"):
            return __original(*args, **kwargs)
        module = args[1] if len(args) > 1 else kwargs.get("module")
        if module is not None and not STATE.get("lattice_inner_wrapped"):
            STATE["lattice_inner_wrapped"] = True
            try:
                # ``source.Emb(module)`` is reached through the subobject
                # construction's own ``inclusion`` call, and that is where it
                # is timed: the class carrying ``Emb`` only exists once the
                # subobject has been built.
                from sage_extensions.categories.modules.pure.modules import (
                    ModuleSubobjectConstruction,
                )

                wrap_method_gated(ModuleSubobjectConstruction, "inclusion", "inclusion")
            except Exception as failure:  # pragma: no cover - reporting only
                log(f"  inclusion not wrapped: {failure!r}")
            try:
                wrap_method_gated(module, "_module_with_structure", "module with structure")
            except Exception as failure:  # pragma: no cover - reporting only
                log(f"  _module_with_structure not wrapped: {failure!r}")
        with _Nest("lattice object"):
            return __original(*args, **kwargs)

    lattice_module._lattice_object = timed_lattice_object
    STATE["patched"].append(
        "lattice object: _lattice_object in sage_extensions.categories.lattices (function)"
    )
    log("the sublattice construction is split; labels: " + ", ".join(BASIS_LABELS))


def install_coercion(lattice):
    """Census the coercion and action containers of the parents a plane touches."""
    free = lattice.unformed_module()
    ring = lattice.base_ring()
    COERCION_TARGETS.extend(
        (("ambient lattice", lattice), ("its free module", free), ("base ring", ring))
    )
    for label, parent in COERCION_TARGETS:
        try:
            containers = parent._introspect_coerce()
        except Exception as failure:  # pragma: no cover - reporting only
            log(f"  {label}: no coercion census ({failure!r})")
            continue
        log(
            f"  {label}: "
            + ", ".join(
                f"{key.lstrip('_')} {0 if containers[key] is None else len(containers[key])}"
                for key in COERCION_KEYS
            )
        )
    # Who *registers* a map on each of them: the registration calls are the
    # only way an entry appears, and ``self`` names the parent it appears on.
    for label, parent in COERCION_TARGETS:
        klass = type(parent)
        for name in ("register_coercion", "register_embedding", "register_action",
                     "register_conversion"):
            original = getattr(klass, name, None)
            if original is None:
                continue

            def timed_registration(self, *args, __label=label, __name=name,
                                   __original=original, **kwargs):
                outcome = __original(self, *args, **kwargs)
                if self is parent:
                    row = REGISTRATIONS.setdefault(STATE["window"], {}).setdefault(
                        __label, {}
                    )
                    row[__name] = row.get(__name, 0) + 1
                return outcome

            try:
                setattr(klass, name, timed_registration)
            except Exception as failure:  # pragma: no cover
                log(f"  {label}.{name} not counted: {failure!r}")
    log("coercion census targets: " + ", ".join(label for label, _ in COERCION_TARGETS))


def coercion_row():
    """The containers' lengths, and what the last plane's parent holds."""
    row = {}
    for label, parent in COERCION_TARGETS:
        try:
            containers = parent._introspect_coerce()
        except Exception:  # pragma: no cover
            continue
        row[label] = {
            key: (0 if containers[key] is None else len(containers[key]))
            for key in COERCION_KEYS
        }
    if LAST_PLANE:
        plane = LAST_PLANE[-1]
        try:
            containers = plane._introspect_coerce()
            row["the last plane"] = {
                key: (0 if containers[key] is None else len(containers[key]))
                for key in COERCION_KEYS
            }
        except Exception:  # pragma: no cover
            pass
    return row


# ------------------------------------- who calls the set comparison (profile mode)
#
# The profiler names ``FiniteOrderedSets.__eq__`` as the function whose time per
# call grows and ``subobject_on`` as its caller; the call site inside that
# function is what a repair has to change, so the comparison counts itself by
# the file and line of the frame that made the call.
EQ_CALLS = {}


def install_equality_probe():
    from sage_extensions.categories.sets.finite_ordered_sets import (
        FiniteOrderedSets,
    )

    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

    instance = finite_ordered_set((0, 1))
    candidates = [
        klass
        for klass in type(instance).__mro__
        if "__eq__" in vars(klass) and hasattr(vars(klass)["__eq__"], "__code__")
    ]
    library = [
        klass
        for klass in candidates
        if vars(klass)["__eq__"].__code__.co_filename.endswith("finite_ordered_sets.py")
    ]
    if not library:
        raise RuntimeError(
            "no Python class on "
            f"{type(instance).__mro__} defines the library's __eq__ (candidates: {candidates})"
        )
    klass = library[0]
    original = vars(klass)["__eq__"]

    def timed(self, other, __original=original):
        if STATE.get("in_transport"):
            frame = sys._getframe(1)
            site = f"{frame.f_code.co_filename.rsplit('/', 1)[-1]}:{frame.f_lineno} {frame.f_code.co_name}"
            row = EQ_CALLS.setdefault(STATE["window"], {})
            row[site] = row.get(site, 0) + 1
        return __original(self, other)

    setattr(klass, "__eq__", timed)
    STATE["patched"].append(
        f"equality: __eq__ on {klass.__module__}.{klass.__qualname__} (counting its call sites)"
    )
    log("the set comparison counts its own call sites, by file:line of the caller")


# ------------------------------------------------------------------ profiling

PROFILE_SPECS = (("early", 5, 25), ("late", 120, 160))
PROFILES = {}
PROFILE_CALLS = {}


def profile_hook(planes):
    """Start or stop a profiler at this plane's boundaries."""
    if not STATE.get("profile"):
        return
    running = STATE.get("_profiling")
    if running is not None and planes >= running[2]:
        label, profiler, _stop, start = running
        profiler.disable()
        PROFILES[label] = profiler
        PROFILE_CALLS[label] = planes - start
        STATE["_profiling"] = None
        log(f"profile {label} closed at plane {planes} ({PROFILE_CALLS[label]} calls)")
    for label, start, stop in PROFILE_SPECS:
        if planes == start and label not in PROFILES:
            profiler = cProfile.Profile()
            profiler.enable()
            STATE["_profiling"] = (label, profiler, stop, start)
            log(f"profile {label} opened at plane {planes}")
            break


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
    profile_hook(planes)

    if needs_transport_flag():
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
    if needs_transport_flag():
        STATE["in_transport"] = False
    if STATE.get("coercion"):
        if not LAST_PLANE:
            LAST_PLANE.append(moved)
        else:
            LAST_PLANE[0] = moved

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
    LOADS[window] = _load()
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
    if STATE.get("detail_basis"):
        for step in BASIS_LABELS:
            cell = row.get(step)
            own = row.get(step + " own")
            if not cell:
                continue
            log(
                f"        construction: {step:<24} n={cell[1]:>6} "
                f"{1000 * cell[0] / cell[1]:9.2f} ms"
                + (
                    f"  own {1000 * own[0] / own[1]:9.2f} ms"
                    if own and (step,) and own[1] == cell[1]
                    else ""
                )
            )
    log(
        f"    snapshot cost {spent:.1f} s; rss {_status_mib('VmRSS:'):.0f} MiB; "
        f"objects {sum(counts.values())} (previous "
        f"{sum(COUNTERS[window - 1].values()) if window - 1 in COUNTERS else 0}); "
        f"load {LOADS[window][0]:.2f} on {LOADS[window][1]} core(s)"
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
    if STATE.get("profile") and window in EQ_CALLS:
        top = sorted(EQ_CALLS[window].items(), key=lambda item: -item[1])[:3]
        log("    set comparisons from: " + ", ".join(f"{site} x{count}" for site, count in top))
    if STATE.get("coercion"):
        COERCION_ROWS[window] = coercion_row()
        log("    coercion census: " + " | ".join(
            f"{target}: " + " ".join(
                f"{key.lstrip('_')} {value}" for key, value in containers.items()
            )
            for target, containers in COERCION_ROWS[window].items()
        ))
        registered = REGISTRATIONS.get(window, {})
        if registered:
            log("    registrations on a tracked parent: " + " | ".join(
                f"{target}: " + " ".join(f"{call} {count}" for call, count in calls.items())
                for target, calls in registered.items()
            ))
        log(
            f"    live MonoDict objects: {counts.get('MonoDict', 0)}, "
            f"live parents of the plane's class: "
            f"{counts.get(type(LAST_PLANE[0]).__name__, 0) if LAST_PLANE else 0}"
        )
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

def format_key(key):
    """``function (file:line)`` for a profile key."""
    filename, lineno, name = key[:3]
    return f"{name} ({filename.rsplit('/', 1)[-1]}:{lineno})"


def caller_chain(profiler, key, depth=6):
    """The largest-cumulative caller of ``key``, then of that one, and so on.

    The probe's own wrappers are stepped over: they stand between the library
    functions and say nothing about the library's call graph.
    """
    stats = pstats.Stats(profiler).stats
    chain = []
    current = key
    for _ in range(depth):
        value = stats.get(current)
        if value is None or not value[4]:
            break
        candidates = [
            item for item in value[4].items()
            if "probe.py" not in item[0][0]
        ] or list(value[4].items())
        parent, counts = max(candidates, key=lambda item: item[1][3])
        chain.append((parent, counts, counts[1]))
        current = parent
    return chain


def dump_profile(profiler):
    """The profile's own cumulative view, into the log."""
    import io

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative").print_stats(18)
    for line in stream.getvalue().splitlines():
        if line.strip():
            log("    " + line)


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
    if STATE.get("detail_basis"):
        order = [
            window for window in sorted(WINDOWS)
            if WINDOWS[window].get("span construction")
        ]
        log("")
        log("=== the sublattice construction, mean ms per call, inclusive, by window ===")
        log(
            f"{'window':>6}{'planes':>14}"
            + "".join(f"{name[:13]:>14}" for name in BASIS_LABELS)
        )
        for window in order:
            row = WINDOWS[window]
            held = row.get("call (four steps + framing)", [0.0, 0])[1]
            high = STATE.get("_window_end", {}).get(window, held)
            cells = ""
            for name in BASIS_LABELS:
                cell = row.get(name)
                cells += f"{1000 * cell[0] / cell[1]:14.2f}" if cell else f"{'-':>14}"
            log(f"{window:>6}{f'[{high - held}, {high})':>14}{cells}")
        log("")
        log("=== the same, exclusive: a parent's time with its children subtracted ===")
        log(f"{'window':>6}{'planes':>14}" + "".join(f"{'excl ' + n[:8]:>14}" for n in BASIS_INNER))
        for window in order:
            row = WINDOWS[window]
            high = STATE.get("_window_end", {}).get(window, 0)
            held = row.get("call (four steps + framing)", [0.0, 0])[1]
            cells = ""
            for name in BASIS_INNER:
                cell = row.get(name + " own")
                cells += f"{1000 * cell[0] / cell[1]:14.2f}" if cell else f"{'-':>14}"
            log(f"{window:>6}{f'[{high - held}, {high})':>14}{cells}")
        if order:
            first, last = order[0], order[-1]
            log("")
            log("=== the construction, first window against last (inclusive) ===")
            for name in BASIS_LABELS:
                left = WINDOWS[first].get(name)
                right = WINDOWS[last].get(name)
                if not left or not right:
                    continue
                a = 1000 * left[0] / left[1]
                b = 1000 * right[0] / right[1]
                log(
                    f"  {name:<28} window {first}: {a:9.2f}  window {last}: {b:9.2f}  "
                    f"ratio {b / a if a else float('nan'):6.2f}  calls/plane "
                    f"{left[1] / max(WINDOWS[first].get('call (four steps + framing)', [0, 1])[1], 1):4.2f}"
                )

    if STATE.get("coercion"):
        log("")
        log("=== the coercion census, length by window ===")
        windows = sorted(COERCION_ROWS)
        for target in [label for label, _parent in COERCION_TARGETS] + ["the last plane"]:
            for key in COERCION_KEYS:
                cells = [
                    str(COERCION_ROWS[window].get(target, {}).get(key, "-"))
                    for window in windows
                ]
                if len(set(cells)) == 1:
                    continue
                log(f"  {target}.{key.lstrip('_')}: " + " ".join(cells))
        log("  (windows in order: " + " ".join(str(window) for window in windows) + ")")
        log("")
        log("=== registrations on a tracked parent, by window ===")
        for window in sorted(REGISTRATIONS):
            calls = REGISTRATIONS[window]
            log(
                f"  window {window}: " + " | ".join(
                    f"{target}: " + " ".join(f"{call} {count}" for call, count in counts.items())
                    for target, counts in calls.items()
                )
            )
        if not REGISTRATIONS:
            log("  none: no coercion, embedding, action or conversion was registered on "
                "the ambient lattice, its free module or the base ring during the row")
        log("")
        log("=== MonoDict objects by window ===")
        for window in sorted(COUNTERS):
            counts = COUNTERS[window]
            log(
                f"  window {window}: MonoDict {counts.get('MonoDict', 0)}, "
                f"MonoDictEraser {counts.get('MonoDictEraser', 0)}, "
                f"TripleDict {counts.get('TripleDict', 0)}, "
                f"parents of the plane's class "
                f"{counts.get(type(LAST_PLANE[0]).__name__, 0) if LAST_PLANE else 0}"
            )

    if EQ_CALLS:
        log("")
        log("=== the set comparison, calls by their call site, per window ===")
        for window in sorted(EQ_CALLS):
            total = sum(EQ_CALLS[window].values())
            log(
                f"  window {window}: {total} comparisons -- " + ", ".join(
                    f"{site} x{count}"
                    for site, count in sorted(EQ_CALLS[window].items(), key=lambda item: -item[1])
                )
            )

    if PROFILES:
        log("")
        log("=== two profiled windows of the same row ===")
        per_call = {}
        for label in ("early", "late"):
            if label not in PROFILES:
                log(f"  {label}: the row did not reach this window")
                continue
            stats = pstats.Stats(PROFILES[label])
            calls = max(PROFILE_CALLS.get(label, 1), 1)
            per_call[label] = {
                key: value[3] / calls for key, value in stats.stats.items()
            }
            log(
                f"  {label}: {PROFILE_CALLS.get(label)} calls, "
                f"{stats.total_tt:.2f} s of profiled self time"
            )
        if "early" in per_call and "late" in per_call:
            early, late = per_call["early"], per_call["late"]
            rows = sorted(
                ((late.get(key, 0.0), early.get(key, 0.0), key) for key in late),
                reverse=True,
            )
            log("")
            log("  mean ms of cumulative time per transport call, worst functions (late)")
            log(f"    {'function':<46}{'early':>10}{'late':>10}{'growth':>10}")
            for late_value, early_value, key in rows[:12]:
                log(
                    f"    {format_key(key):<46}{1000 * early_value:10.2f}"
                    f"{1000 * late_value:10.2f}{1000 * (late_value - early_value):10.2f}"
                )
            growth = sorted(
                (
                    (late.get(key, 0.0) - early.get(key, 0.0), late.get(key, 0.0),
                     early.get(key, 0.0), key)
                    for key in set(late) | set(early)
                ),
                reverse=True,
            )
            log("")
            log("  the same, ranked by growth")
            log(f"    {'function':<46}{'early':>10}{'late':>10}{'growth':>10}")
            for change, late_value, early_value, key in growth[:12]:
                log(
                    f"    {format_key(key):<46}{1000 * early_value:10.2f}"
                    f"{1000 * late_value:10.2f}{1000 * change:10.2f}"
                )
            log("")
            log("  the caller chain of the largest growth among the library's own functions:")
            library = [
                entry for entry in growth if "probe.py" not in entry[3][0]
            ] or growth
            for level, (key, values, calls_seen) in enumerate(
                caller_chain(PROFILES["late"], library[0][3])
            ):
                log(
                    "    " + "  " * level + f"{format_key(key)}  "
                    f"cumulative {1000 * values[3] / max(PROFILE_CALLS.get('late', 1), 1):.2f} ms per call, "
                    f"{calls_seen} call(s)"
                )
            for rank, entry in enumerate(library[1:4], start=2):
                log("")
                log(f"  the caller chain of the {rank}nd largest growth:")
                for level, (key, values, calls_seen) in enumerate(
                    caller_chain(PROFILES["late"], entry[3])
                ):
                    log(
                        "    " + "  " * level + f"{format_key(key)}  "
                        f"cumulative {1000 * values[3] / max(PROFILE_CALLS.get('late', 1), 1):.2f} ms per call, "
                        f"{calls_seen} call(s)"
                    )
            log("")
            log("  raw cumulative view, early window:")
            dump_profile(PROFILES["early"])
            log("  raw cumulative view, late window:")
            dump_profile(PROFILES["late"])

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
            STATE["detail_basis"] = chosen == "basis"
        if argument == "coercion":
            STATE["coercion"] = True
        if argument == "profile":
            STATE["profile"] = True
        if argument.startswith("trace="):
            STATE["trace"] = [argument.split("=", 1)[1], 0, "?"]
    smoke = bool(argv) and argv[0] == "smoke"

    import sage_extensions
    import hashlib
    from pathlib import Path

    log(
        "probe M: split the plane transport of the Otilde plane row (#390)"
        + (" -- smoke run on U + U(2) + <-2>" if smoke else "")
    )
    log(
        "modes: "
        + ", ".join(
            [
                name
                for key, name in (
                    ("detail_image", "detail=image"),
                    ("detail_span", "detail=span"),
                    ("detail_basis", "detail=basis"),
                    ("coercion", "coercion"),
                    ("profile", "profile"),
                )
                if STATE.get(key)
            ]
            or ["stage split only"]
        )
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

    if STATE.get("detail_basis"):
        install_constructor_split(lattice, lattice.base_ring())
    if STATE.get("coercion"):
        install_coercion(lattice)
    if STATE.get("profile"):
        install_equality_probe()
        log(
            "profiling windows: "
            + ", ".join(f"{label} calls [{start}, {stop})" for label, start, stop in PROFILE_SPECS)
        )
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
    running = STATE.get("_profiling")
    if running is not None:
        running[1].disable()
        PROFILES[running[0]] = running[1]
        PROFILE_CALLS[running[0]] = STATE["planes"] - running[3]
        STATE["_profiling"] = None
        log(f"profile {running[0]} closed by the row's end at plane {STATE['planes']}")
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
