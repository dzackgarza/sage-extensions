"""#541: the plane transport census -- run through the pinned image.

CPython of the image, /probe.py this file, /repos/sage-extensions the tree under
test, /work the port checkout; the launcher is the one the log header names.
"""
"""#541: what one plane transport builds, on the smallest lattice that shows it.

Inside the pinned image (see .tmp/qc-evidence/ for the published copy):
  sage-image/run.sh -w /work -b <port>:/work -b <worktree>:/repos/sage-extensions \
      -b <this file>:/probe.py -- /bin/sh -c 'PYTHONPATH=... /sage/.venv/bin/python -u -s /probe.py'

A  per-plane cost on U+U (rank 4), U+U+<-2> (rank 5) and T_En (rank 12): each
   timed transport is of a fresh plane of a fresh, kept-alive, isometric copy of
   the lattice, so its span is uncached while the class and category machinery
   is warm -- the row's own situation.  The class-and-category construction a
   lattice pays once is measured separately.
B  one transport of one fresh plane under ``setprofile``: every function the
   transport enters, calls, own time and inclusive time, and for each
   constructor the children that make it compute when it is built.
C  the same transport with no profiler, timing the module-level functions whose
   call sites resolve their name at call time.
D  identity across calls: a join is a value of the category set, a Mor set of
   one endpoint pair is one object, a datum is computed once per parent.
"""
import gc
import statistics
import sys
import time
import traceback

from sage_extensions.all import *

PAIR = (1, 2)  # the second generator of the first U block, the first of the second


def report(title, body):
    print(f"\n===== {title} =====", flush=True)
    for line in body:
        print(line, flush=True)


# ---------------------------------------------------------------- specimens
def gram_rows(lattice):
    gram = lattice.gram_matrix()
    return [[int(gram[i, j]) for j in range(gram.ncols())] for i in range(gram.nrows())]


def specimens():
    """(name, a factory for a fresh isometric copy) -- one kept-alive copy each."""
    return [
        ("U+U", Lattices(ZZ)("U") + Lattices(ZZ)("U")),
        ("U+U+<-2>", Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])),
        ("TEn", NamedLattices.TEn),
    ]


def plane_of(lattice):
    labels = tuple(lattice.module_generating_set())
    return lattice.primitive_isotropic_subobject(
        *(lattice.module_generator(labels[index]) for index in PAIR)
    )


def reflection(lattice, block):
    """The integral reflection in ``e + f`` (``U``) or ``ep + fp`` (``U(2)``).

    ``e + f`` has norm two and its reflection is ``e -> -f``, ``f -> -e``;
    ``ep + fp`` has norm four and its reflection is ``ep -> -fp``, ``fp -> -ep``.
    Both are checked against every pair of generators before use.
    """
    labels = tuple(lattice.module_generating_set())
    images = {label: lattice.module_generator(label) for label in labels}
    first, second = labels[0], labels[1]
    if block == "U":
        images[first] = -lattice.module_generator(second)
        images[second] = -lattice.module_generator(first)
    else:
        third, fourth = labels[2], labels[3]
        images[third] = -lattice.module_generator(fourth)
        images[fourth] = -lattice.module_generator(third)
    isometry = lattice.Isom(lattice)(lambda label: images[label])
    for left in labels:
        for right in labels:
            assert lattice.b(
                isometry(lattice.module_generator(left)),
                isometry(lattice.module_generator(right)),
            ) == lattice.b(
                lattice.module_generator(left), lattice.module_generator(right)
            ), f"the reflection on {block} is not an isometry of {lattice}"
    return isometry


def span_cache():
    from sage_extensions.categories.lattices import _lattice_subobject_spanning

    return _lattice_subobject_spanning.cache


# ------------------------------------------------------------------ A: cost
def timed(isometry, plane):
    """One transport: wall time and the span constructions built inside it."""
    from sage_extensions.categories.lattices import _lattice_subobject_spanning

    before = len(_lattice_subobject_spanning.cache)
    gc.disable()
    start = time.perf_counter()
    moved = isometry.transport_isotropic_object(plane)
    taken = time.perf_counter() - start
    gc.enable()
    assert moved.module_rank() == cardinal(2)
    return taken, len(_lattice_subobject_spanning.cache) - before


def base_planes(lattice):
    """Planes to transport: the block pair, and -- where the blocks allow it -- the diagonal.

    ``span(e, ep)`` is isotropic because the blocks are orthogonal.  In a
    lattice with two ``U`` blocks the diagonal ``span(e + ep, f - fp)`` is too:
    both vectors are isotropic and they pair to ``1 - 1 = 0``.  Each is checked
    by the constructor, and one that is not a primitive isotropic plane is
    dropped.
    """
    labels = tuple(lattice.module_generating_set())
    vectors = [lattice.module_generator(labels[index]) for index in PAIR]
    diagonal = [
        lattice.module_generator(labels[0]) + vectors[1],
        lattice.module_generator(labels[1]) - lattice.module_generator(labels[3]),
    ]
    planes = []
    for pair in ((vectors[0], vectors[1]), tuple(diagonal)):
        try:
            planes.append(lattice.primitive_isotropic_subobject(*pair))
        except Exception:
            continue
    return planes


def per_plane_cost(name, reference, repeats=20):
    """Cold and warm per-plane cost on one lattice.

    Cold: the transport of a plane whose span this call has not built, so the
    span is built inside the timed region -- what the row pays for every plane
    it reaches.  Warm: the same transport repeated, which rebuilds everything
    but the cached span.
    """
    first = reflection(reference, "U")
    second = reflection(reference, "U(2)")
    transporter = second * first
    planes = base_planes(reference)
    timed(transporter, planes[0])  # warm-up, discarded
    cold = []
    for plane in planes:
        for isometry in (second, first, transporter):
            taken, spans = timed(isometry, plane)
            cold.append((taken, spans))
    warm = [timed(transporter, planes[0])[0] for _ in range(repeats)]
    built = [taken for taken, spans in cold if spans]
    body = (
        f"{name:10s} rank {int(reference.module_rank()):2d}: "
        f"cold {' '.join(f'{1e3 * taken:.2f}f{spans}' for taken, spans in cold)} ms  "
        f"(median {1e3 * statistics.median(built) if built else float('nan'):7.2f} over {len(built)} "
        f"with a fresh span) | warm median {1e3 * statistics.median(warm):6.2f} ms | "
        f"{1.0 / statistics.median(built) if built else 0:5.1f} cold, "
        f"{1.0 / statistics.median(warm):5.1f} warm planes/s"
    )
    return body, (statistics.median(built) if built else float("inf"))


def ladder():
    body, chosen = [], None
    for name, reference in specimens():
        try:
            line, median = per_plane_cost(name, reference)
            body.append(line)
            if median > 5.0 and chosen is None:
                chosen = name
        except Exception:
            body.append(f"{name:10s} FAILED\n" + traceback.format_exc())
    report("A. per-plane transport cost: cold (fresh plane) and warm (repeat)", body)
    return chosen


# ------------------------------------------------------- B: stack profile
class StackProfile:
    """Own time, call count and call-graph edges, from ``setprofile`` events."""

    def __init__(self):
        self.stats = {}
        self.edges = {}
        self.stack = []
        self.frames = {}

    @staticmethod
    def key(frame):
        code = frame.f_code
        qualname = getattr(code, "co_qualname", code.co_name)
        return (code.co_filename.rsplit("/", 1)[-1], code.co_firstlineno, qualname)

    def event(self, frame, event, arg):
        frame_id = id(frame)
        if event == "call":
            key = self.key(frame)
            entry = [key, time.perf_counter(), 0.0]
            self.frames[frame_id] = entry
            if self.stack:
                edge = self.edges.setdefault((self.stack[-1][0], key), [0])
                edge[0] += 1
            self.stack.append(entry)
        elif event == "return":
            entry = self.frames.pop(frame_id, None)
            if entry is None:
                return
            elapsed = time.perf_counter() - entry[1]
            stat = self.stats.setdefault(entry[0], [0, 0.0, 0.0])
            stat[0] += 1
            stat[1] += elapsed - entry[2]
            stat[2] += elapsed
            if self.stack and self.stack[-1] is entry:
                self.stack.pop()
            elif entry in self.stack:
                while self.stack and self.stack.pop() is not entry:
                    pass
            if self.stack:
                self.stack[-1][2] += elapsed

    def run(self, call):
        gc.collect()
        gc.disable()
        sys.setprofile(self.event)
        start = time.perf_counter()
        try:
            value = call()
        finally:
            sys.setprofile(None)
            wall = time.perf_counter() - start
            gc.enable()
        return value, wall


def children(profile, parent_key, limit=10):
    rows = []
    for (parent, child), counts in profile.edges.items():
        if parent != parent_key:
            continue
        stat = profile.stats.get(child, [0, 0.0, 0.0])
        rows.append((stat[2], counts[0], child))
    rows.sort(reverse=True)
    return rows[:limit]


def profile_one(name, reference):
    planes = base_planes(reference)
    first = reflection(reference, "U")
    second = reflection(reference, "U(2)")
    transporter = second * first
    # Warm the class and category machinery on a plane whose transported image
    # is not the one profiled, so the profiled transport builds its span.
    timed(transporter, planes[-1]) if len(planes) > 1 else None
    plane = planes[0]
    profile = StackProfile()
    before = len(span_cache())
    _, wall = profile.run(lambda: transporter.transport_isotropic_object(plane))
    misses = len(span_cache()) - before
    stats = profile.stats
    body = [
        f"{name} rank {int(reference.module_rank())}: one transport of one fresh plane, "
        f"{1e3 * wall:.2f} ms under setprofile, {sum(s[0] for s in stats.values())} calls, "
        f"{misses} span constructions"
    ]
    ordered = sorted(((s[1], s[0], s[2], key) for key, s in stats.items()), reverse=True)
    body.append("\n-- own time, top 40 (own ms | calls | incl ms | site)")
    for own, calls, incl, key in ordered[:40]:
        body.append(f"{1e3 * own:9.3f} | {calls:8d} | {1e3 * incl:9.3f} | {key[0]}:{key[1]} {key[2]}")
    body.append("\n-- every object constructed, by calls (calls | own ms | incl ms | site)")
    constructed = [
        (s[0], s[1], s[2], key)
        for key, s in stats.items()
        if key[2].endswith((".__init__", ".__new__", ".Of", ".__classcall__"))
    ]
    constructed.sort(reverse=True)
    for calls, own, incl, key in constructed[:30]:
        body.append(f"{calls:8d} | {1e3 * own:8.3f} | {1e3 * incl:9.3f} | {key[0]}:{key[1]} {key[2]}")
    body.append("\n-- what each named site builds inside itself")
    for wanted in ("transport_isotropic_object", "Of", "refine", "owned_category_join",
                   "_owned_join_as_tuple", "_declaring_classes", "_final_category_operations",
                   "primitive_isotropic_subobject", "subobject_on", "_lattice_subobject_spanning",
                   "_lattice_subobject_on_basis", "is_primitive", "cokernel", "image", "compose",
                   "_engine_gram", "_evaluate_gram", "b", "module_generating_set", "module_rank"):
        for key in [k for k in stats if k[2] == wanted or k[2].endswith("." + wanted)]:
            stat = stats[key]
            if stat[2] < 1e-3:
                continue
            body.append(
                f"\n{key[0]}:{key[1]} {key[2]}  calls={stat[0]} "
                f"own={1e3 * stat[1]:.3f} ms incl={1e3 * stat[2]:.3f} ms"
            )
            for incl, edge_calls, child in children(profile, key):
                body.append(f"    {1e3 * incl:8.3f} ms incl | {edge_calls:7d} calls | "
                            f"{child[0]}:{child[1]} {child[2]}")
    report(f"B. one transport of one plane on {name}, object by object", body)


# --------------------------------------------- C: wall time without a profiler
class Timers:
    """Own and inclusive wall time per wrapped site, with a switch."""

    def __init__(self):
        self.rows = {}
        self.stack = []
        self.active = False
        self.seen = {}

    def wrap(self, owner, name, label=None):
        target = vars(owner).get(name) if isinstance(owner, type) else None
        if target is None:
            target = getattr(owner, name)
        if not callable(target) or hasattr(target, "f") or hasattr(target, "cache"):
            raise TypeError(f"a cached descriptor, not a plain callable")
        label = label or f"{getattr(owner, '__name__', owner)}.{name}"
        row = self.rows.setdefault(label, [0, 0.0, 0.0])
        seen = self.seen.setdefault(label, set())

        def wrapper(*args, **kwargs):
            if not self.active:
                return target(*args, **kwargs)
            if args and isinstance(args[0], type):
                seen.add(id(args[0]))
            start = time.perf_counter()
            entry = [0.0]
            self.stack.append(entry)
            try:
                return target(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                self.stack.pop()
                row[0] += 1
                row[2] += elapsed
                row[1] += elapsed - entry[0]
                if self.stack:
                    self.stack[-1][0] += elapsed

        setattr(owner, name, wrapper)


def wrap_sites(timers):
    import sage_extensions.categories.abstract_categories.mor_categories as mors
    import sage_extensions.categories.lattices as lattices
    import sage_extensions.categories.modules.module_morphisms.module_morphisms as module_morphisms
    import sage_extensions.categories.sets.set_categories as set_categories
    import sage_extensions.owned_category as owned_category
    import sage_extensions.refine as refine
    from sage.categories.homset import Homset

    sites = [
        (refine, "_declaring_classes"),
        (refine, "_final_category_operations"),
        (refine, "_is_bookkeeping_or_hook"),
        (refine, "owned_parent_class"),
        (refine, "realize_owned_category"),
        (refine, "refine"),
        (owned_category, "_owned_join_as_tuple"),
        (owned_category, "owned_category_join"),
        (owned_category, "_owned_sort_uniq"),
        (owned_category, "_owned_flatten_categories"),
        (mors, "_minimal_inherited_homs"),
        (mors, "_carves_the_same_mor"),
        (mors._MorCategoryOf, "Of"),
        (mors._MorCategoryOf, "base_category"),
        (mors._MorCategoryOf, "_cached_between"),
        (mors.CategoricalMor, "__init__"),
        (module_morphisms, "_engine_image"),
        (module_morphisms.ModuleMorphismMethods, "image"),
        (module_morphisms.ModuleMorphismMethods, "cokernel"),
        (lattices, "_lattice_subobject_spanning"),
        (lattices, "_lattice_subobject_on_basis"),
        (lattices, "_span_basis_elements"),
        (lattices, "_module_subobject_constructor_data"),
        (lattices.Lattices.ParentMethods, "subobject_on"),
        (lattices.Lattices.ParentMethods, "_evaluate_gram"),
        (lattices.Lattices.ParentMethods, "b"),
        (Homset, "__init__"),
        (set_categories.NaturalNumberSets.ParentMethods, "__call__"),
        (set_categories.NaturalNumberSets.ParentMethods, "_element_constructor_"),
    ]
    wrapped, failed = [], []
    for owner, name in sites:
        try:
            timers.wrap(owner, name)
            wrapped.append(name)
        except Exception as error:
            failed.append(f"{getattr(owner, '__name__', owner)}.{name}: {error}")
    return wrapped, failed


def attribution(name, reference, samples=3):
    first = reflection(reference, "U")
    second = reflection(reference, "U(2)")
    transporter = second * first
    plane = plane_of(reference)
    timers = Timers()
    wrapped, failed = wrap_sites(timers)
    timers.active = True
    timed(transporter, plane)  # warm-up, not counted
    baseline = {label: list(row) for label, row in timers.rows.items()}
    totals = []
    for isometry in (second, first, transporter):
        gc.disable()
        start = time.perf_counter()
        isometry.transport_isotropic_object(plane)
        totals.append(time.perf_counter() - start)
        gc.enable()
    timers.active = False
    counted = {}
    for label, (calls, own, incl) in timers.rows.items():
        base = baseline.get(label, [0, 0.0, 0.0])
        counted[label] = (calls - base[0], own - base[1], incl - base[2])
    body = [
        f"{name} rank {int(reference.module_rank())}: {len(wrapped)} sites wrapped; "
        f"not wrapped: {'; '.join(failed) if failed else 'none'}",
        f"{samples} transports with the wrappers counting: "
        + " ".join(f"{1e3 * t:.2f}" for t in totals)
        + f" ms, median {1e3 * statistics.median(totals):.2f} ms",
        "",
        "per transport (calls | own ms | incl ms | site)",
    ]
    for label, (calls, own, incl) in sorted(counted.items(), key=lambda item: -item[1][2]):
        distinct = len(timers.seen.get(label, ()))
        body.append(f"  {calls / samples:8.1f} | {1e3 * own / samples:8.3f} | "
                    f"{1e3 * incl / samples:9.3f} | {distinct:3d} classes | {label}")
    report(f"C. wall time of one plane's construction, no profiler, on {name}", body)


# ------------------------------------------------- D: identity across calls
def identities():
    from sage.all import Category

    from sage_extensions.categories.isotropic_parabolics import (
        PrimitiveIsotropicSubobjects,
    )
    from sage_extensions.owned_category import owned_category_join
    from sage_extensions.refine import _declaring_classes

    body = []
    lattice = Lattices(ZZ)(gram_rows(specimens()[0][1]))
    labels = tuple(lattice.module_generating_set())
    plane = plane_of(lattice)
    other = lattice.primitive_isotropic_subobject(
        lattice.module_generator(labels[0]), lattice.module_generator(labels[2])
    )
    body.append(f"two distinct planes: {plane is not other}")
    body.append(f"their categories are one object: {plane.category() is other.category()}")
    body.append(f"their classes are one object: {type(plane) is type(other)}")
    target = PrimitiveIsotropicSubobjects(lattice.base_ring())
    args = (plane.category(), target)
    body.append(f"owned_category_join of that pair is itself twice: "
                f"{owned_category_join(args) is owned_category_join(args)}")
    body.append(f"Category.join of the same pair is itself twice: "
                f"{Category.join(args) is Category.join(args)}")
    body.append(f"_declaring_classes of one class is a fresh dict each call: "
                f"{_declaring_classes(type(plane)) is not _declaring_classes(type(plane))}")
    family = lattice.module_category().Mor
    inclusion = plane.inclusion()
    body.append(f"Mor(domain, codomain) is one object for one endpoint pair: "
                f"{family(inclusion.domain(), lattice) is family(inclusion.domain(), lattice)}")
    body.append(f"the plane's own Mor parent is one object for one plane: "
                f"{family(plane, plane) is family(plane, plane)}")
    # The cost of the one datum the census finds first: the declaring classes
    # of a class, which is a function of the class alone.
    for label, target in (("the plane's class", type(plane)),
                          ("the plane's category's class", type(plane.category())),
                          ("a lattice class", type(lattice))):
        gc.disable()
        start = time.perf_counter()
        walks = 0
        while time.perf_counter() - start < 0.05:
            _declaring_classes(target)
            walks += 1
        elapsed = time.perf_counter() - start
        gc.enable()
        names = sum(len(vars(klass)) for klass in target.__mro__)
        body.append(
            f"_declaring_classes({label}): {1e3 * elapsed / walks:.3f} ms a call, "
            f"{1e6 * elapsed / walks / names:.3f} ns a name, {names} names over "
            f"{len(target.__mro__)} classes"
        )
    report("D. identity across calls, and the cost of one declaring-classes walk", body)


if __name__ == "__main__":
    names = dict(specimens())
    chosen = "U+U"
    for section in (profile_one, attribution):
        try:
            section(chosen, names[chosen])
        except Exception:
            print(traceback.format_exc(), flush=True)
    try:
        measured = ladder()
        if measured is not None:
            chosen = measured
        print(f"\ndissecting {chosen}", flush=True)
    except Exception:
        print(traceback.format_exc(), flush=True)
    try:
        identities()
    except Exception:
        print(traceback.format_exc(), flush=True)
