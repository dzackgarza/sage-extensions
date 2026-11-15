r"""#528: the Otilde(T_Co) plane row's setup stages, each timed alone.

The row is

    NamedLattices.Tco.stable_orthogonal_group().isotropic_orbit_representatives(2)

and its setup -- everything before the first transported plane -- is a sum of
calls the #390 slice (``issue390-stage-slice.log``) charged as stages: the
lattice, its stable orthogonal group, the ambient ``O(L)`` plane row, the
plane's parabolic family, the completeness decision on that family, the
character quotient's index (which is ``image_order``), the ambient
discriminant images, and the walk's own setup (the coset action, the closure
and GAP's breadth-first walk, up to the first lift).  This probe answers **one
of those questions per run**: it builds only the inputs that stage takes, times
the stage alone, and stops.  It never runs the row.

Nothing in the library is changed; the instrumentation is installed in this
process only.

* ``libgap`` is replaced by a timing proxy in every loaded ``sage_extensions``
  module that holds a module-level reference to it, so the GAP primitives of a
  stage are timed individually (``FactorCosetAction``, ``IsomorphismPermGroup``,
  ``ClosureGroup``, ``Subgroup``, ``Image``, ``Order``, ``Index``,
  ``GeneratorsOfGroup``, ``Group``, ``Size``, ``DirectProduct`` ...).  The proxy
  forwards every attribute and every call to the real ``libgap``.
* The Python call sites a stage reaches are wrapped as sub-stages
  (``image_order``, ``subgroup_image_order``, ``_ambient_generators``,
  ``ambient_discriminant_images``, ``_sign_descent_rank``,
  ``_im_rho_engine_and_section``, ``_joint_discriminant_image_gap``,
  ``_kernel_sign_flip``, ``image``, ``parabolic_image_subgroup``), so a stage
  that is mostly one of them is named rather than inferred.  The cached ones
  are wrapped through their own descriptor's definition, so the cache stays in
  force and the run measures the call the row makes.
* The time of a stage is exclusive: the time inside its own call with the time
  of every sub-stage nested inside it subtracted.  The inputs it took are
  reported separately, as ``input:`` rows, and are **not** part of the stage's
  number.
* A sampler thread reads ``/proc/self/status`` and keeps the peak ``VmRSS`` of
  the stage the run is in.

Modes, one per run::

    stage=lattice          # NamedLattices.Tco
    stage=group            # lattice.stable_orthogonal_group()
    stage=ambient_row      # (supergroup).isotropic_orbit_representatives(2)
    stage=parabolic        # plane.parabolic_stabilizer_generators()
    stage=complete         # plane.is_parabolic_complete()
    stage=index            # quotient.index()   (interior: image_order)
    stage=disc_images      # quotient.ambient_discriminant_images()
    stage=walk             # quotient._iter_splitting_isometries_in_im_rho(family),
                           #   up to and including its first lift -- the row's
                           #   "walk setup", with the caches the walk itself
                           #   reads pre-warmed so the stage is the walk
    profile=<stage>        # the same stage under cProfile, with the top calls
                           #   by cumulative time, their caller chains, and the
                           #   construction/computation split below
    cap=<seconds>          # the stage's own cap (default 560: under the ten
                           #   minutes a run may take)

Each run prints, at the end, ``RESULT stage=<name> seconds=<x>`` (or
``RESULT stage=<name> undecided`` when the cap stopped it, or ``RESULT
stage=<name> raised``), which is the line a bisection script can read.

**The construction/computation split** (``profile=``).  An object's
construction should be nearly instant, so a constructor that computes is a
laziness defect of its owner.  The split is taken from the one ``cProfile`` of
the stage: every profiled entry's *own* time (``tottime``, which sums to the
stage's measured exclusive time without double counting) is charged to one of
three classes by the name of the function that holds it.

* ``construction``: the constructors and their placement -- ``__init__``,
  ``__classcall__``/``__classcall_private__``, ``_object_of`` and
  ``_object_from_category``, ``__call__`` of a parent's constructor,
  ``_module_subobject_spanning``/``_lattice_subobject_spanning``,
  ``_lattice_object``, ``_form_module_from_bilinear_computation``,
  ``_construct_form_module``, ``_form_module_categories``,
  ``_fresh_free_module_on``, ``_same_presentation_module``,
  ``_module_with_structure``, ``refine`` and the category joins,
  ``is_subcategory``/``meet``/``homset``/``Hom`` creation, and coercion
  registration.
* ``computation``: the mathematics the stage owes -- everything that runs
  through the ``libgap`` proxy (the GAP calls are the proxy's own ``call``
  frame, so their whole subtree is charged where it happens), and the named
  algorithms: orbit and stabilizer walks, orders, Smith and Hermite forms,
  linear algebra on the Gram matrix.
* ``other``: anything else, reported by name so nothing hides in it.

The three columns of the printed table are own time summed per class, the
share of the stage, and the count of distinct entries.  The biggest entries of
each class are printed under it, each as ``file:line function own cum calls``,
so a constructor that computes is named at its line.
"""

import cProfile
import io
import pstats
import signal
import sys
import threading
import time
import traceback

from sage.libs.gap.libgap import libgap as _real_libgap

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories import orthogonal_quotients as oq

START = time.monotonic()
CAP = 560.0
SAMPLE_SECONDS = 2.0

STAGES = (
    "lattice",
    "group",
    "ambient_row",
    "direct_plane",
    "parabolic",
    "complete",
    "index",
    "disc_images",
    "walk",
)

# ``input=direct`` makes the plane's stages (``parabolic``, ``complete``, ``walk``)
# take a primitive isotropic plane built from the lattice's own vectors instead of
# the port's first ambient class.  It exists because on a tree where the ambient
# row does not return inside a run's ten minutes, the port's plane is not
# available as an input at all, and a stage whose input cannot be built inside
# the budget is not measurable; the plane is an input, not the stage.
INPUT_MODE = "port"


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


STATE = {"stage": "start-up", "done": False}
ACCOUNT = {}
TOTAL = {}
COUNTS = {}
PARENTS = {}
STACKS = {}
STAGE_RSS = {}
LOADS = []
FRAMES = []
_LOCK = threading.Lock()


def enter(key):
    begin = _now()
    FRAMES.append([key, begin, 0.0])
    STATE["stage"] = key
    return begin


def leave():
    key, begin, children = FRAMES.pop()
    elapsed = _now() - begin
    ACCOUNT[key] = ACCOUNT.get(key, 0.0) + (elapsed - children)
    TOTAL[key] = TOTAL.get(key, 0.0) + elapsed
    COUNTS[key] = COUNTS.get(key, 0) + 1
    if FRAMES:
        FRAMES[-1][2] += elapsed
        PARENTS.setdefault(key, set()).add(FRAMES[-1][0])
        STATE["stage"] = FRAMES[-1][0]


class _Stage:
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

    def __call__(self, *args, **kwargs):
        return object.__getattribute__(self, "_real")(*args, **kwargs)

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


WRAPPED = set()


def wrap_call_sites():
    """Wrap the Python call sites a setup stage reaches as sub-stages."""
    targets = (
        (oq.OrthogonalCharacterQuotient, "image_order"),
        (oq.OrthogonalCharacterQuotient, "subgroup_image_order"),
        (oq.OrthogonalCharacterQuotient, "_ambient_generators"),
        (oq.OrthogonalCharacterQuotient, "ambient_discriminant_images"),
        (oq.OrthogonalCharacterQuotient, "_sign_descent_rank"),
        (oq.OrthogonalCharacterQuotient, "_im_rho_engine_and_section"),
        (oq.OrthogonalCharacterQuotient, "_joint_discriminant_image_gap"),
        (oq.OrthogonalCharacterQuotient, "_kernel_sign_flip"),
        (oq.OrthogonalCharacterQuotient, "image"),
        (oq.OrthogonalCharacterQuotient, "parabolic_image_subgroup"),
    )
    for klass, name in targets:
        for owner in klass.__mro__:
            if name in vars(owner):
                original = vars(owner)[name]

                def timed(
                    self, *args, __original=original, __name=name, **kwargs
                ):
                    function = __original.__get__(self, type(self))
                    with _Stage(__name):
                        return function(*args, **kwargs)

                setattr(owner, name, timed)
                break
        else:
            raise RuntimeError(f"no class of {klass!r} defines {name}")


def install():
    """Install the GAP proxy wherever a module holds a reference to it."""
    patched = []
    for name, module in list(sys.modules.items()):
        if not name.startswith("sage_extensions"):
            continue
        if getattr(module, "libgap", None) is _real_libgap:
            module.libgap = PROXY
            patched.append(name)
    log(f"the GAP proxy is installed on {len(patched)} sage_extensions modules")
    wrap_call_sites()


class _Inputs:
    """The stage's inputs, each built once and charged to an ``input:`` row."""

    def __init__(self):
        self._cache = {}

    def need(self, name, thunk):
        if name not in self._cache:
            begin = _now()
            log(f"building input: {name}")
            with _Stage(f"input: {name}"):
                self._cache[name] = thunk()
            log(f"input built: {name} in {_now() - begin:.1f} s")
        return self._cache[name]

    def lattice(self):
        return self.need("lattice construction", lambda: NamedLattices.Tco)

    def group(self):
        return self.need(
            "stable orthogonal group", lambda: self.lattice().stable_orthogonal_group()
        )

    def plane(self):
        if INPUT_MODE == "direct":
            # A primitive isotropic plane built from the lattice's own vectors,
            # without the port's ambient classification: the stage's input, not
            # the row's first plane.  The search is over the basis and its small
            # combinations and takes the first pair that is isotropic,
            # orthogonal and primitive -- so the stage is timed with a plane in
            # hand whatever the ambient row costs on the tree under test.
            return self.need("direct primitive isotropic plane", self._direct_plane)
        return self.need(
            "ambient O(L) plane row (its first plane)",
            lambda: tuple(self.group().supergroup().isotropic_orbit_representatives(2))[0],
        )

    def _direct_plane(self):
        """A primitive isotropic plane from the lattice's own vectors, by a bounded search.

        T_Co's basis is ``h`` of ``<2>``, the hyperbolic pair ``ep, fp`` of
        ``U(2)`` and the eight roots of ``E8(-2)``, so the hyperbolic basis
        vectors alone give no *plane*: ``ep`` and ``fp`` are isotropic but not
        orthogonal, and an ``E8(-2)`` vector has even norm.  An isotropic
        partner of ``ep`` therefore mixes the two: ``2h + a1 + a2`` has
        ``b(., ep) = 0`` and ``q = 4 - 4 = 0``.  The search below is that,
        bounded and stated: every integer combination of the roots with
        coefficients in ``-1..1`` plus ``a * h`` for ``a`` in ``-2..2``, kept
        when it is isotropic and orthogonal to the first isotropic vector
        found, and the plane is the first primitive span of two of them.
        """
        from itertools import product

        lattice = self.lattice()
        ring = lattice.base_ring()
        zero = ring.zero()
        basis = tuple(lattice.module_generators())
        isotropic = [
            vector
            for vector in basis
            if lattice.b(vector, vector) == zero and vector != lattice.zero()
        ]
        if not isotropic:
            raise RuntimeError(f"no isotropic basis vector of {lattice}")
        anchor = isotropic[0]
        hyperbolic = basis[0]
        roots = basis[3:]
        for coefficients in product((-1, 0, 1), repeat=len(roots)):
            for multiple in (-2, -1, 1, 2):
                candidate = multiple * hyperbolic
                for coefficient, root in zip(coefficients, roots):
                    if coefficient:
                        candidate = candidate + coefficient * root
                if lattice.b(candidate, anchor) != zero:
                    continue
                if lattice.b(candidate, candidate) != zero:
                    continue
                try:
                    return lattice.primitive_isotropic_subobject(anchor, candidate)
                except AssertionError:
                    continue
        raise RuntimeError(
            f"no primitive isotropic plane found with {anchor!r} over the bounded search"
        )

    def family(self):
        return self.need(
            "parabolic family", lambda: tuple(self.plane().parabolic_stabilizer_generators())
        )

    def quotient(self):
        return self.need(
            "character quotient", lambda: self.group().finite_character_quotient()
        )


def stage_thunk(stage, inputs):
    """Build the stage's inputs and return the callable that is the stage alone."""
    if stage == "lattice":
        return lambda: NamedLattices.Tco
    if stage == "direct_plane":
        inputs.lattice()
        return inputs._direct_plane
    if stage == "group":
        inputs.lattice()
        return lambda: inputs.lattice().stable_orthogonal_group()
    if stage == "ambient_row":
        inputs.group()
        return lambda: inputs.group().supergroup().isotropic_orbit_representatives(2)
    if stage == "parabolic":
        inputs.plane()
        return lambda: inputs.plane().parabolic_stabilizer_generators()
    if stage == "complete":
        inputs.plane()
        return lambda: inputs.plane().is_parabolic_complete()
    if stage == "index":
        inputs.quotient()
        return lambda: inputs.quotient().index()
    if stage == "disc_images":
        inputs.quotient()
        return lambda: inputs.quotient().ambient_discriminant_images()
    if stage == "walk":
        inputs.family()
        quotient = inputs.quotient()
        # The caches the walk itself reads, warmed before the stage starts, so
        # the number this run reports is the walk and not its prerequisites.
        # ``image_order`` is deliberately not among them: the walk does not
        # read it.
        for name in (
            "_sign_descent_rank",
            "_im_rho_engine_and_section",
            "ambient_discriminant_images",
        ):
            begin = _now()
            log(f"pre-warming {name}")
            with _Stage(f"input: pre-warm {name}"):
                getattr(quotient, name)()
            log(f"pre-warmed {name} in {_now() - begin:.1f} s")

        def walk_to_first_lift():
            iterator = quotient._iter_splitting_isometries_in_im_rho(inputs.family())
            return next(iterator)

        return walk_to_first_lift
    raise SystemExit(f"unknown stage {stage!r}; one of {STAGES}")


def _load1():
    try:
        with open("/proc/loadavg") as handle:
            return float(handle.read().split()[0])
    except OSError:
        return float("nan")


def sample():
    # No lock here: a list append is atomic, and taking a lock on this thread
    # under ``cProfile`` (which profiles every thread) charged its wait to the
    # stage, which is not the stage's time.
    while not STATE["done"]:
        stage = STATE["stage"]
        rss = _status_mib("VmRSS:")
        STAGE_RSS[stage] = max(STAGE_RSS.get(stage, 0.0), rss)
        LOADS.append((_now() - START, _load1(), stage))
        time.sleep(SAMPLE_SECONDS)


def stack_sample(stop):
    """Sample the main thread's stack: which call a stage is inside, and for how long.

    Used in ``profile=`` mode only.  ``cProfile`` records calls that *return*,
    so a stage the run's cap stops leaves the call that never returned out of
    its table; this sampler names it, and the frequency of a leaf frame is the
    share of the stage's time that frame holds.
    """
    ident = threading.main_thread().ident
    while not stop.is_set():
        frame = sys._current_frames().get(ident)
        stack = []
        while frame is not None and len(stack) < 14:
            stack.append(
                f"{frame.f_code.co_filename.rsplit('/', 1)[-1]}:{frame.f_lineno} "
                f"{frame.f_code.co_name}"
            )
            frame = frame.f_back
        STACKS.setdefault(STATE["stage"], []).append(tuple(stack))
        stop.wait(0.5)


def progress():
    """One line every thirty seconds naming the stage the run is in.

    A run the launcher's own timeout kills prints no report, so this line is
    what says where it was: a stage whose input is the ambient row cannot be
    measured on a tree where that input does not return, and the log has to
    show that it was the input, not the stage, that was still running.
    """
    while not STATE["done"]:
        time.sleep(30.0)
        if STATE["done"]:
            break
        log(
            f"progress stage={STATE['stage']!r} rss={_status_mib('VmRSS:'):.0f} MiB "
            f"load={_load1():.2f}"
        )


class Undecided(Exception):
    """The stage did not return inside the run's cap."""


def _alarm(signum, frame):
    raise Undecided


def report_inputs():
    log("")
    log("=== everything else this run timed, outside the stage ===")
    log(f"  {'row':<52}{'calls':>7}{'seconds':>10}")
    total = 0.0
    for key in TOTAL:
        if key == STATE.get("target") or key == CALIBRATION_KEY:
            continue
        log(f"  {key:<52}{COUNTS.get(key, 0):>7}{TOTAL[key]:>10.1f}")
        if key.startswith("input:"):
            total += TOTAL[key]
    log(f"  {'inputs proper (the rows above marked input:), total':<52}{'':>7}{total:>10.1f}")
    return total


def report_stage(stage, seconds, outcome):
    log("")
    log("=== the stage alone ===")
    log(f"  {'stage':<52}{'calls':>7}{'seconds':>10}{'peak MiB':>10}")
    log(
        f"  {stage:<52}{COUNTS.get(stage, 0):>7}{seconds:>10.1f}"
        f"{STAGE_RSS.get(stage, float('nan')):>10.0f}"
    )
    children = [
        (TOTAL[key], key)
        for key in TOTAL
        if stage in PARENTS.get(key, ())
    ]
    log("=== inside it (each sub-stage's own total, children included) ===")
    named = 0.0
    for value, key in sorted(children, reverse=True):
        named += value
        log(f"  {key:<52}{COUNTS.get(key, 0):>7}{value:>10.3f}")
    log(f"  {'not inside a named sub-stage':<52}{'':>7}{seconds - named:>10.3f}")
    deeper = [
        (TOTAL[key], key)
        for key in TOTAL
        if key != stage and stage not in PARENTS.get(key, ()) and not key.startswith("input:")
    ]
    if deeper:
        log("=== below them ===")
        for value, key in sorted(deeper, reverse=True):
            log(f"  {key:<52}{COUNTS.get(key, 0):>7}{value:>10.3f}")
    if outcome is not None:
        text = repr(outcome)
        log(f"the stage returned {text[:160]}")


def run_stage(stage, thunk, profiler=None, sampling_stacks=False):
    STATE["target"] = stage
    signal.signal(signal.SIGALRM, _alarm)
    stop = threading.Event()
    if sampling_stacks:
        threading.Thread(target=stack_sample, args=(stop,), daemon=True).start()
    # The sampler's own stage label is the target's, from here on.
    STATE["stage"] = stage
    before = gap_snapshot()
    begin = _now()
    outcome = None
    decided = True
    if profiler is not None:
        profiler.enable()
    try:
        signal.setitimer(signal.ITIMER_REAL, CAP)
        with _Stage(stage):
            outcome = thunk()
    except Undecided:
        decided = False
        log(f"the stage did not return inside its {CAP:.0f} s cap")
    except Exception:
        decided = False
        log("the stage raised:")
        traceback.print_exc()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        seconds = _now() - begin
        if profiler is not None:
            profiler.disable()
        stop.set()
    after = gap_snapshot()
    log("")
    log("=== GAP primitives, by time in this stage ===")
    for spent, calls, name in gap_delta(before, after):
        log(f"  {name:<40}{calls:>6} calls{spent:>12.3f} s")
    report_stage(stage, seconds, outcome if decided else None)
    return seconds, decided, outcome


def report_stacks(stage):
    stacks = STACKS.get(stage, [])
    if not stacks:
        return
    counts = {}
    for stack in stacks:
        leaf = stack[0] if stack else "?"
        counts[leaf] = counts.get(leaf, 0) + 1
    log("")
    log(f"=== the main thread's stack, {len(stacks)} samples at 0.5 s ===")
    log("  leaf frame (where the stage was) and the samples it holds:")
    for leaf, count in sorted(counts.items(), key=lambda item: -item[1])[:12]:
        log(f"    {count:>5}  {leaf}")
    log("  the last sample's whole stack, innermost first:")
    for depth, frame in enumerate(stacks[-1]):
        log(f"    {depth:>2}. {frame}")


CONSTRUCTION_NAMES = frozenset({
    "__init__",
    "__classcall__",
    "__classcall_private__",
    "_object_of",
    "_object_from_category",
    "_object_from_engine",
    "_spanning",
    "_lattice_subobject_spanning",
    "_lattice_subobject_on_basis",
    "_module_subobject_spanning",
    "_module_subobject_constructor_data",
    "_lattice_object",
    "_lattice_on_gram",
    "_form_module",
    "_form_module_from_bilinear_computation",
    "_construct_form_module",
    "_form_module_categories",
    "_fresh_free_module_on",
    "_same_presentation_module",
    "_module_with_structure",
    "refine",
    "_final_category_operations",
    "_refine",
    "owned_category_join",
    "_owned_category_join",
    "category_join",
    "join",
    "meet",
    "is_subcategory",
    "_is_subcategory",
    "Hom",
    "homset",
    "hom",
    "Mor",
    "_construct",
    "_construct_object",
    "_element_constructor_",
    "_coerce_map_from_",
    "register_coercion",
    "register_conversion",
    "_register_pair",
    "_gram_axiom_categories",
    "_form_of_gram",
    "tensor",
    "_module_generating_set",
    "matrix_space",
    "_gram_axioms",
    "_placement",
    "validate_form_placement",
    "_with_category",
})

CONSTRUCTION_PREFIXES = (
    "_lattice_subobject",
    "_module_subobject",
    "_form_module",
    "_fresh_free_module",
    "_gram_axiom",
    "refine",
    "_refine",
)

COMPUTATION_NAMES = frozenset({
    "call",  # the libgap proxy's own frame: a GAP call and its whole subtree
    "image_order",
    "subgroup_image_order",
    "ambient_discriminant_images",
    "_im_rho_engine_and_section",
    "_sign_descent_rank",
    "_joint_discriminant_image_gap",
    "parabolic_stabilizer_generators",
    "is_parabolic_complete",
    "parabolic_completeness_decision",
    "exact_isotropic_stabilizer_generators",
    "splitting_isometries",
    "splitting_isometries_from_line_class",
    "transport_isotropic_object",
    "integral_kernel_group_generators",
    "kernel_generators",
    "rational_lifts",
    "discriminant_representation",
    "lll",
    "qfisom",
    "qfauto",
    "b",
    "orbit_representatives",
    "_orbit_walk",
    "orbits",
    "orbits_presented_by",
    "stabilizer",
    "setwise_stabilizer",
    "pointwise_stabilizer",
    "group_generators",
    "schreier_generators",
    "order",
    "cardinality",
    "smith_form",
    "hermite_form",
    "echelon_form",
    "isometry",
    "isometry_to",
    "isotropic_orbit_representatives",
    "isotropic_equivalence_witness",
    "_isotropic_orbit_representatives",
    "_isotropic_equivalence_witness",
    "_hyperbolic_completion",
    "_planes_through_line",
    "_isotropic_plane_orbit_representatives",
    "primitive_marking_classes",
    "eichler_transvection",
    "reflection",
    "preimage_morphism",
    "solve",
    "image",
    "_from_engine",
    "_to_engine",
})

COMPUTATION_PREFIXES = (
    "_orbit",
    "_iter_orbit",
    "orbit_",
    "_stabilizer",
    "stabilizer_",
    "discriminant_",
    "_discriminant_",
    "isotropic_",
    "_isotropic_",
    "smith_",
    "hermite_",
    "_act",
    "act_",
    "_gap",
    "gap_",
    "libgap",
)


def classify(filename, lineno, name):
    """Charge one profiled entry to construction, computation or other."""
    short = filename.rsplit("/", 1)[-1]
    if "/sage/" in filename or short in ("libgap.py", "gap.py", "sage_object.py"):
        # GAP's own calls and Sage's own core: the mathematics, unless the
        # name says it is a Sage parent's constructor.
        if name in ("__init__", "__classcall__", "__classcall_private__"):
            return "construction"
        if name in COMPUTATION_NAMES or name.startswith(COMPUTATION_PREFIXES):
            return "computation"
        return "other"
    if name in CONSTRUCTION_NAMES or name.startswith(CONSTRUCTION_PREFIXES):
        return "construction"
    if name in COMPUTATION_NAMES or name.startswith(COMPUTATION_PREFIXES):
        return "computation"
    return "other"


def report_split(stage, stats, seconds):
    """Print the construction/computation split of one profiled stage."""
    entries = []
    for key, value in stats.stats.items():
        filename, lineno, name = key
        cc, nc, own, cum, _callers = value
        entries.append((own, cum, nc, filename, lineno, name))
    classes = {"construction": [], "computation": [], "other": []}
    for entry in entries:
        classes[classify(entry[3], entry[4], entry[5])].append(entry)
    log("")
    log("=== construction against computation, by own time ===")
    log(f"  {'class':<16}{'own s':>10}{'share':>9}{'cum s':>10}{'entries':>9}")
    for name in ("construction", "computation", "other"):
        own = sum(entry[0] for entry in classes[name])
        cum = sum(entry[1] for entry in classes[name])
        log(
            f"  {name:<16}{own:>10.2f}{100.0 * own / seconds if seconds else float('nan'):>8.1f}%"
            f"{cum:>10.2f}{len(classes[name]):>9}"
        )
    log(f"  {'stage (its own time)':<16}{seconds:>10.2f}")
    for name in ("construction", "computation", "other"):
        rows = sorted(classes[name], reverse=True)[:14]
        log("")
        log(f"=== {name}: the biggest entries, by own time ===")
        log(f"  {'file:line':<44}{'function':<34}{'own s':>9}{'cum s':>9}{'calls':>7}")
        for own, cum, nc, filename, lineno, function in rows:
            where = f"{filename.rsplit('/', 1)[-1]}:{lineno}"
            log(f"  {where:<44}{function[:33]:<34}{own:>9.3f}{cum:>9.3f}{nc:>7}")


CALIBRATION_KEY = "calibration (fixed workload, for the run's CPU share)"


def calibration():
    """A fixed workload, so a run can say how much of the VM it actually got.

    This VM is shared: another project's build on the same four cores did
    inflate the same stage by a factor of three between two runs of this probe
    (the ``group`` stage: 1.81 s at a load average of 1.0, 6.36 s at 11.6).  A
    wall-clock number without a calibration beside it is not comparable across
    runs, so every run times this loop -- Python integer arithmetic and one GAP
    call, both fixed -- and prints it.  The probe's idle value is in the log of
    the first run and every table quotes it.
    """
    with _Stage(CALIBRATION_KEY):
        total = 0
        for value in range(300000):
            total += value * value
        PROXY.Order(PROXY.SymmetricGroup(8))
    return total


def caller_chain(stats, key, depth=14):
    """Walk up from one profiled entry, taking at each step the heaviest caller."""
    chain = []
    seen = set()
    current = key
    while len(chain) < depth and current not in seen:
        seen.add(current)
        value = stats.stats.get(current)
        if not value or not value[4]:
            break
        caller, _counts = max(value[4].items(), key=lambda item: item[1][3])
        chain.append(f"{caller[2]} ({caller[0].rsplit('/', 1)[-1]}:{caller[1]})")
        current = caller
    return chain


def run_profile(stage, thunk):
    profiler = cProfile.Profile()
    seconds, decided, _outcome = run_stage(stage, thunk, profiler=profiler, sampling_stacks=True)
    report_stacks(stage)
    if not decided:
        log("the profiled run did not decide; its call table is the completed calls only")
    buffer = io.StringIO()
    stats = pstats.Stats(profiler, stream=buffer)
    stats.sort_stats("cumulative")
    stats.print_stats(28)
    log("")
    log("=== cProfile, top calls by cumulative time ===")
    for line in buffer.getvalue().splitlines():
        log(line.rstrip())
    log("")
    log("=== the top calls and where they were called from ===")
    rows = sorted(
        ((value[3], key, value) for key, value in stats.stats.items()), reverse=True
    )
    for cumulative, key, value in rows[:5]:
        cc, nc, own, cum, callers = value
        log(
            f"  {key[2]} ({key[0].rsplit('/', 1)[-1]}:{key[1]}) "
            f"cum={cum:.2f} s own={own:.2f} s calls={nc}"
        )
        for caller, (cc2, nc2, tt2, ct2) in sorted(
            callers.items(), key=lambda item: -item[1][3]
        )[:6]:
            log(
                f"      called from {caller[2]} "
                f"({caller[0].rsplit('/', 1)[-1]}:{caller[1]}) "
                f"x{nc2} cum={ct2:.2f} s"
            )
        log("      the chain from the stage itself:")
        for frame in caller_chain(stats, key, depth=14):
            log(f"        <- {frame}")
    report_split(stage, stats, seconds)
    return seconds, decided


def main(argv):
    global CAP
    stage = None
    profile = False
    for argument in argv:
        if argument.startswith("cap="):
            CAP = float(argument.split("=", 1)[1])
        elif argument.startswith("stage="):
            stage = argument.split("=", 1)[1]
        elif argument.startswith("input="):
            global INPUT_MODE
            INPUT_MODE = argument.split("=", 1)[1]
        elif argument.startswith("profile="):
            stage = argument.split("=", 1)[1]
            profile = True
    if stage not in STAGES:
        raise SystemExit(f"give stage=<one of {STAGES}> or profile=<one of them>")
    log(f"probe: T_Co's plane row setup, stage {stage!r} alone (#528)")
    log(f"cap {CAP:.0f} s, python {sys.version.split()[0]}")
    install()
    threading.Thread(target=sample, daemon=True).start()
    threading.Thread(target=progress, daemon=True).start()
    calibration()
    log(f"calibration (fixed workload, for the run's CPU share): {TOTAL[CALIBRATION_KEY]:.3f} s")
    inputs = _Inputs()
    thunk = stage_thunk(stage, inputs)
    inputs_total = sum(v for k, v in ACCOUNT.items() if k.startswith("input:"))
    log(f"inputs built in {inputs_total:.1f} s; calling the stage alone")
    if profile:
        seconds, decided = run_profile(stage, thunk)
    else:
        seconds, decided, _outcome = run_stage(stage, thunk)
    STATE["done"] = True
    inputs_total = report_inputs()
    loads = [(t, value) for t, value, _stage in LOADS if value == value]
    if loads:
        peak = max(value for _t, value in loads)
        log("")
        log(
            f"the VM's 1-minute load average while this run went on: "
            f"first {loads[0][1]:.2f}, peak {peak:.2f}, last {loads[-1][1]:.2f} "
            f"({len(loads)} samples of /proc/loadavg)"
        )
    log("")
    log(f"peak VmRSS (python, sampled) {max(STAGE_RSS.values(), default=float('nan')):.0f} MiB")
    verdict = f"{seconds:.2f}" if decided else "undecided"
    log(f"RESULT stage={stage} seconds={verdict} inputs={inputs_total:.2f} "
        f"calib={TOTAL[CALIBRATION_KEY]:.3f} "
        f"load_peak={max((value for _t, value, _s in LOADS if value == value), default=float('nan')):.2f}"
        + (" profiled" if profile else ""))
    log("PROBE DONE")
    return 0 if decided else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
