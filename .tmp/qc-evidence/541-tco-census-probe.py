"""#541: the plane transport census on T_Co itself.

`4c29488782` priced one plane transport on `U + U` and its relatives because those
were the smallest lattices whose transport cost more than 5 ms; the row under
#541 transports T_Co's planes at about 14-18 ms a plane, so the census is taken
here on T_Co directly, by that probe's method:

A  the cost of one transport, cold (a fresh plane, so the span is built inside
   the timed region, which is the row's situation) and warm;
B  one cold transport under ``setprofile``: every site's own and inclusive time,
   every object constructed, and what each named constructor builds inside itself;
C  the same transport with no profiler, timing the module-level and engine sites
   at call time, so the census is not read through the profiler's own overhead.

The plane and the isometry are found from the lattice's own data and checked
against the form before use.
"""
import gc
import statistics
import sys
import time
import traceback

from sage_extensions.all import *

REPORT = []


def report(title, body):
    print(f"\n===== {title} =====", flush=True)
    for line in body:
        print(line, flush=True)


# ------------------------------------------------------------- the specimen
def generators(lattice):
    labels = tuple(lattice.module_generating_set())
    return labels, {label: lattice.module_generator(label) for label in labels}


def pairing_matrix(lattice):
    labels, points = generators(lattice)
    size = len(labels)
    return labels, points, [[int(lattice.b(points[labels[i]], points[labels[j]])) for j in range(size)] for i in range(size)]


def reflection_of(lattice, vector):
    r"""The reflection in ``vector``, as an isometry, checked against the Gram.

    ``s_v(x) = x - (2 b(x,v) / b(v,v)) v`` is an isometry of the form for any
    vector of nonzero norm, and it is integral exactly when every coefficient
    ``2 b(e_i,v) / b(v,v)`` is an integer.  The matrix is built in the
    generators' own coordinates and each image is checked against the form.
    """
    from fractions import Fraction

    labels, points, gram = pairing_matrix(lattice)
    size = len(labels)
    coordinates = [int(entry) for entry in vector.to_vector()]
    pairings = [sum(int(gram[i][j]) * coordinates[j] for j in range(size)) for i in range(size)]
    norm = sum(pairings[i] * coordinates[i] for i in range(size))
    assert norm != 0, "a reflection needs a vector of nonzero norm"
    rows = []
    for i in range(size):
        coefficient = Fraction(2 * pairings[i], norm)
        assert coefficient.denominator == 1, (
            f"the reflection in {vector} is not integral: 2 b(e_{i}, v) / b(v,v) = {coefficient}"
        )
        rows.append([(1 if i == k else 0) - int(coefficient) * coordinates[k] for k in range(size)])
    zero = ZZ(0) * points[labels[0]]
    images = {}
    for i in range(size):
        image = zero
        for k in range(size):
            if rows[i][k]:
                image = image + ZZ(rows[i][k]) * points[labels[k]]
        images[labels[i]] = image
    isometry = lattice.Isom(lattice)(lambda label: images[label])
    for left in labels:
        for right in labels:
            assert lattice.b(isometry(points[left]), isometry(points[right])) == lattice.b(
                points[left], points[right]
            ), "the reflection is not an isometry of this lattice"
    return isometry


def norm_four_vector(lattice):
    r"""A vector ``v`` with ``b(v,v) = 4`` and every ``b(e_i, v)`` even.

    Those are the two conditions the reflection above is integral for.  The
    hyperbolic block's ``ep + fp`` has norm ``4`` and pairs evenly with every
    generator; the generators are scanned first in case one already qualifies.
    """
    labels, points, gram = pairing_matrix(lattice)
    ordered = [points[label] for label in labels]

    def qualifies(vector):
        coordinates = [int(entry) for entry in vector.to_vector()]
        pairings = [sum(int(gram[i][j]) * coordinates[j] for j in range(len(labels))) for i in range(len(labels))]
        norm = sum(pairings[i] * coordinates[i] for i in range(len(labels)))
        return norm == 4 and all(pairing % 2 == 0 for pairing in pairings)

    for vector in list(ordered) + [ordered[1] + ordered[2]] + [ordered[i] + ordered[j] for i in range(3, len(ordered)) for j in range(i + 1, len(ordered))]:
        if qualifies(vector):
            return vector
    raise RuntimeError("no vector of norm four with even pairings found")


def isotropic_vectors(lattice):
    r"""Isotropic vectors of the lattice, from its blocks.

    `T_Co` is ``<2> + U(2) + E8(-2)`` on the generators ``h, ep, fp, a1..a8``:
    ``ep`` and ``fp`` are isotropic themselves, and since ``q(2h + x) = 4 + q(x)``
    for ``x`` in the negative definite ``E8(-2)`` block, a sum of two distant
    ``E8`` roots makes ``2h + x`` isotropic.  Every candidate is required to
    satisfy ``q(v) = 0`` before it is offered.
    """
    labels, points = generators(lattice)
    ordered = [points[label] for label in labels]
    candidates = list(ordered)
    head = ordered[0]
    for other in ordered[3:]:
        candidates.append(head + other)
        candidates.append(head - other)
    for i in range(3, len(ordered)):
        for j in range(i + 1, len(ordered)):
            candidates.append(ordered[i] + ordered[j])
            candidates.append(ZZ(2) * head + ordered[i] + ordered[j])
    isotropic = []
    for vector in candidates:
        if lattice.q(vector) == 0 and all(vector != seen for seen in isotropic):
            isotropic.append(vector)
    return isotropic


def plane_of(lattice):
    r"""A primitive isotropic plane of the lattice, from its own isotropic vectors.

    The constructor decides isotropy and primitivity, so every ordered pair of
    isotropic vectors with vanishing pairing is offered to it and the first
    plane it accepts is the specimen.
    """
    pool = isotropic_vectors(lattice)
    for left in pool:
        for right in pool:
            if left == right or lattice.b(left, right) != 0:
                continue
            try:
                plane = lattice.primitive_isotropic_subobject(left, right)
            except Exception:
                continue
            assert plane.module_rank() == cardinal(2)
            return plane
    raise RuntimeError(f"no primitive isotropic plane among {len(pool)} isotropic vectors")


# --------------------------------------------------------------- A: the cost
def timed(isometry, plane):
    from sage_extensions.categories.lattices import _lattice_subobject_spanning

    before = len(_lattice_subobject_spanning.cache)
    gc.disable()
    start = time.perf_counter()
    moved = isometry.transport_isotropic_object(plane)
    taken = time.perf_counter() - start
    gc.enable()
    assert moved.module_rank() == cardinal(2)
    return taken, len(_lattice_subobject_spanning.cache) - before


def cost(lattice, isometry, plane, repeats=20):
    timed(isometry, plane)
    cold = [timed(isometry, plane) for _ in range(3)]
    warm = [timed(isometry, plane)[0] for _ in range(repeats)]
    built = [taken for taken, spans in cold if spans]
    body = [
        "cold (a fresh span inside the timed region): "
        + " ".join(f"{1e3 * taken:.2f} ms f{spans}" for taken, spans in cold),
        f"warm median {1e3 * statistics.median(warm):.2f} ms over {repeats} transports",
    ]
    if built:
        body.append(
            f"cold median {1e3 * statistics.median(built):.2f} ms = "
            f"{1.0 / statistics.median(built):.1f} planes/s"
        )
    report(f"A. one plane transport on T_Co (rank {int(lattice.module_rank())})", body)
    return statistics.median(built) if built else statistics.median(warm)


# ------------------------------------------------------- B: the stack profile
class StackProfile:
    def __init__(self):
        self.stats = {}
        self.edges = {}
        self.frames = {}

    @staticmethod
    def key(frame):
        code = frame.f_code
        qualname = getattr(code, "co_qualname", code.co_name)
        return (code.co_filename.rsplit("/", 1)[-1], code.co_firstlineno, qualname)

    def event(self, frame, event, arg):
        if event == "call":
            entry = [self.key(frame), time.perf_counter(), 0.0]
            self.frames[id(frame)] = entry
            if self.stack:
                edge = self.edges.setdefault((self.stack[-1][0], entry[0]), [0])
                edge[0] += 1
            self.stack.append(entry)
        elif event == "return":
            entry = self.frames.pop(id(frame), None)
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

    stack = []

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


def children(profile, parent_key, limit=12):
    rows = []
    for (parent, child), counts in profile.edges.items():
        if parent != parent_key:
            continue
        stat = profile.stats.get(child, [0, 0.0, 0.0])
        rows.append((stat[2], counts[0], child))
    rows.sort(reverse=True)
    return rows[:limit]


CONSTRUCTOR_SUFFIXES = (".__init__", ".__new__", ".Of", ".__classcall__", "._element_constructor_")


def census(lattice, isometry, plane):
    timed(isometry, plane)  # warm the class and category machinery
    profile = StackProfile()
    from sage_extensions.categories.lattices import _lattice_subobject_spanning

    before = len(_lattice_subobject_spanning.cache)
    _, wall = profile.run(lambda: isometry.transport_isotropic_object(plane))
    misses = len(_lattice_subobject_spanning.cache) - before
    stats = profile.stats
    body = [
        f"one transport of one fresh plane: {1e3 * wall:.2f} ms under setprofile, "
        f"{sum(s[0] for s in stats.values())} calls, {misses} span constructions",
        "\n-- own time, top 25 (own ms | calls | incl ms | site)",
    ]
    ordered = sorted(((s[1], s[0], s[2], key) for key, s in stats.items()), reverse=True)
    for own, calls, incl, key in ordered[:25]:
        body.append(f"{1e3 * own:9.3f} | {calls:8d} | {1e3 * incl:9.3f} | {key[0]}:{key[1]} {key[2]}")
    body.append("\n-- constructors, by inclusive time (incl ms | calls | own ms | site)")
    constructed = [
        (s[2], s[0], s[1], key) for key, s in stats.items() if key[2].endswith(CONSTRUCTOR_SUFFIXES)
    ]
    constructed.sort(reverse=True)
    for incl, calls, own, key in constructed[:20]:
        body.append(f"{1e3 * incl:9.3f} | {calls:8d} | {1e3 * own:8.3f} | {key[0]}:{key[1]} {key[2]}")
    body.append("\n-- what the named sites build inside themselves")
    for wanted in ("transport_isotropic_object", "Of", "_minimal_inherited_homs", "owned_parent_class",
                   "_declaring_classes", "_final_category_operations", "_owned_join_as_tuple",
                   "_lattice_subobject_spanning", "_span_basis_elements", "_lattice_subobject_on_basis",
                   "subobject_on", "image", "cokernel"):
        for key in [k for k in stats if k[2] == wanted or k[2].endswith("." + wanted)]:
            stat = stats[key]
            if stat[2] < 2e-3:
                continue
            body.append(f"\n{key[0]}:{key[1]} {key[2]}  calls={stat[0]} own={1e3 * stat[1]:.3f} ms "
                        f"incl={1e3 * stat[2]:.3f} ms")
            for incl, edge_calls, child in children(profile, key):
                body.append(f"    {1e3 * incl:8.3f} ms incl | {edge_calls:7d} calls | {child[0]}:{child[1]} {child[2]}")
    report("B. one cold transport on T_Co, object by object", body)


# --------------------------------------------- C: wall time without a profiler
class Timers:
    def __init__(self):
        self.rows = {}
        self.stack = []
        self.active = False

    def wrap(self, owner, name, label=None):
        target = vars(owner).get(name) if isinstance(owner, type) else None
        if target is None:
            target = getattr(owner, name)
        if not callable(target) or hasattr(target, "f") or hasattr(target, "cache"):
            raise TypeError("a cached descriptor, not a plain callable")
        label = label or f"{getattr(owner, '__name__', owner)}.{name}"
        row = self.rows.setdefault(label, [0, 0.0, 0.0])

        def wrapper(*args, **kwargs):
            if not self.active:
                return target(*args, **kwargs)
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
    import sage_extensions.categories.modules.framed.framed_free_modules as framed_free_modules
    import sage_extensions.categories.sets.set_categories as set_categories
    import sage_extensions.categories.sets.finite_ordered_sets as finite_ordered_sets
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
        (mors, "_minimal_inherited_homs"),
        (mors._MorCategoryOf, "Of"),
        (mors.CategoricalMor, "__init__"),
        (module_morphisms, "_engine_image"),
        (module_morphisms.ModuleMorphismMethods, "image"),
        (module_morphisms.ModuleMorphismMethods, "cokernel"),
        (lattices, "_lattice_subobject_spanning"),
        (lattices, "_lattice_subobject_on_basis"),
        (lattices, "_span_basis_elements"),
        (lattices, "_module_subobject_constructor_data"),
        (lattices.Lattices.ParentMethods, "subobject_on"),
        (lattices.Lattices.ParentMethods, "b"),
        (Homset, "__init__"),
        (set_categories.NaturalNumberSets.ParentMethods, "__call__"),
        (lattices.Lattices.ParentMethods, "_repr_"),
        (framed_free_modules, "_finite_support_labels"),
        (framed_free_modules, "_known_finite_generator_family"),
        (finite_ordered_sets.FiniteOrderedSets, "from_indexed"),
    ]
    wrapped, failed = [], []
    for owner, name in sites:
        try:
            timers.wrap(owner, name)
            wrapped.append(name)
        except Exception as error:
            failed.append(f"{getattr(owner, '__name__', owner)}.{name}: {error}")
    return wrapped, failed


def attribution(lattice, isometry, plane, samples=5):
    timers = Timers()
    wrapped, failed = wrap_sites(timers)
    timers.active = True
    timed(isometry, plane)  # warm-up, discarded
    baseline = {label: list(row) for label, row in timers.rows.items()}
    totals = []
    for _ in range(samples):
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
        f"{len(wrapped)} sites wrapped; not wrapped: {'; '.join(failed) if failed else 'none'}",
        f"{samples} transports with the wrappers counting: median {1e3 * statistics.median(totals):.2f} ms",
        "\n-- own ms per plane, then inclusive ms per plane, then calls per plane",
    ]
    for label, (calls, own, incl) in sorted(counted.items(), key=lambda pair: -pair[1][1]):
        body.append(
            f"{1e3 * own / samples:8.3f} | {1e3 * incl / samples:8.3f} | {calls / samples:8.1f} | {label}"
        )
    report("C. the same transport without a profiler, site by site", body)


def main():
    lattice = NamedLattices.Tco
    labels, points = generators(lattice)
    body = [f"generators {labels}", "**the Gram of T_Co on its generators**"]
    _, _, gram = pairing_matrix(lattice)
    for row in gram:
        body.append("   " + " ".join(f"{entry:4d}" for entry in row))
    body.append("norms b(e,e): " + " ".join(f"{gram[i][i]}" for i in range(len(gram))))
    report("0. the specimen", body)
    plane = plane_of(lattice)
    isometry = reflection_of(lattice, norm_four_vector(lattice))
    report("1. the plane and the isometry", [f"plane {plane}", "the isometry is a reflection in a vector of norm four with even pairings"])
    cost(lattice, isometry, plane)
    census(lattice, isometry, plane)
    attribution(lattice, isometry, plane)
    print("\nPROBE DONE", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
