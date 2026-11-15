r"""#528 (part of #390): what ``_lattice_subobject_spanning`` computes or scans.

The per-plane transport of the ``Otilde(T_Co)`` plane row was measured at
``25eea761af``: ``_lattice_subobject_spanning`` costs **3.93 ms** a call early
in the row and **126.82 ms** a call after 2005 planes, twice per plane.  A
construction that is flat at the start of a row and 32x later is the laziness
question this run answers, and it is answered on a **small** lattice on
purpose: the question is what the construction does, not how large the row is,
and a cheap lattice keeps the interior visible.  The specimens are the
three-summand ``U + U(2) + <-2>`` the #390 smoke runs use, and ``U + U``.

Everything is measured in this process; the library is not changed.

**One call, four steps.**  ``_lattice_subobject_spanning`` ->
``_lattice_subobject_on_basis`` runs, in order:

1. ``_module_subobject_constructor_data(module, basis)``: the labels of the
   span, the union of the supports of the basis vectors
   (``_finite_support_labels``), and a coordinate matrix of the support;
2. ``ring._fresh_free_module_on(labels)``: the framed free module the subobject
   is on;
3. the Gram values: ``module.b(left, right)`` over the ``rank^2`` pairs, into
   ``tensor(...)``;
4. ``_lattice_object(...)``: the placement --
   ``_form_module_from_bilinear_computation`` -> ``_form_module_categories`` ->
   ``_construct_form_module`` -> ``module._module_with_structure`` ->
   ``_fresh_free_module_on`` with the joined categories -- where the category
   join and ``refine`` happen.

Each of those is timed with its own clock, and the placement one level further
(``_form_module_from_bilinear_computation``, ``_form_module_categories``,
``_construct_form_module``, ``_module_with_structure``, ``_fresh_free_module_on``
again).  The steps are patched where they are looked up -- the modules'
attributes, or the class that defines them -- so the call measured is the
library's own.

**Whether a step grows.**  The construction is called ``calls`` times, the
same basis every time, and the first block of 100 calls is compared with the
last block of 100.  Beside the times, the populations a growth could be
scanning are printed at the first and the last call: the module's generating
set, the entries of the ``__classcall__`` caches of the classes the placement
goes through, and the live-object count.  A step whose time grows while every
population it could scan is flat has a cause other than population.

**Own time, not my clocks.**  ``cProfile`` runs over calls 20-40 and again over
calls ``calls/10`` .. ``calls/10 + 20``: the same question by own time, and the
two profiles are printed side by side, so the split above can be checked
against the profiler.

Modes::

    sage -python <this file>                 # U + U(2) + <-2>, 3000 calls
    sage -python <this file> calls=1200      # fewer calls
    sage -python <this file> specimen=UU     # U + U
"""

import cProfile
import pstats
import sys
import time

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories import _lattice as _lat
from sage_extensions.categories import lattices as lat
from sage_extensions.categories.modules.framed import framed_free_modules as ffm
from sage_extensions.categories.modules.framed.formed import form_modules as fm
from sage_extensions.categories.modules.pure import modules as pure

START = time.monotonic()
SPECIMENS = {
    "U2m2": lambda: Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]]),
    "UU": lambda: Lattices(ZZ)("U") + Lattices(ZZ)("U"),
}


def now():
    return time.monotonic()


def log(message=""):
    print(f"[{now() - START:7.1f}s] {message}", flush=True)


STEPS = {}
SERIES = {}


def charge(key, begin):
    spent = now() - begin
    STEPS[key] = STEPS.get(key, 0.0) + spent
    SERIES.setdefault(key, []).append(spent)


def patch_function(module, name, key):
    """Replace ``module.name`` (looked up at call time) by a timed forwarding call."""
    original = getattr(module, name)
    if getattr(original, "_probe_key", None) == key:
        return

    def timed(*args, **kwargs):
        begin = now()
        try:
            return original(*args, **kwargs)
        finally:
            charge(key, begin)

    timed._probe_key = key
    setattr(module, name, timed)


def patch_method(cls, name, key):
    """Replace ``cls.name`` by a timed forwarding method."""
    for owner in cls.__mro__:
        if name in vars(owner):
            original = vars(owner)[name]
            if getattr(original, "_probe_key", None) == key:
                return

            def timed(self, *args, __original=original, __key=key, **kwargs):
                begin = now()
                try:
                    return __original.__get__(self, type(self))(*args, **kwargs)
                finally:
                    charge(__key, begin)

            timed._probe_key = key
            setattr(owner, name, timed)
            return
    raise RuntimeError(f"no class of {cls!r} defines {name}")


def instrument():
    patch_function(lat, "_lattice_subobject_spanning", "spanning, the whole call")
    patch_function(lat, "_module_subobject_constructor_data", "1 constructor data")
    patch_function(lat, "_lattice_object", "4 placement")
    patch_function(_lat, "_lattice_object", "4 placement")
    patch_function(fm, "_form_module_from_bilinear_computation", "4a bilinear computation")
    patch_function(fm, "_form_module_categories", "4b categories")
    patch_function(fm, "_construct_form_module", "4c construct")
    patch_function(ffm, "_fresh_free_module_on", "nf fresh module (all calls)")
    patch_method(pure.Modules.ParentMethods, "_module_with_structure", "4d with structure")


def population(lattice):
    """The sizes a growing step could be scanning, read without building anything."""
    rows = [("the module's generating set", len(tuple(lattice.module_generating_set())))]
    for label, obj in (
        ("the lattice object's classcall cache", type(lattice)),
        ("the fresh module's classcall cache", type(lattice.unformed_module())),
    ):
        classcall = vars(obj).get("__classcall__")
        rows.append((label, len(classcall.cache) if hasattr(classcall, "cache") else -1))
    rows.append(("the label set Sets.Delta", len(Sets.Δ._elements) if hasattr(Sets.Δ, "_elements") else -1))
    return rows


def block(values, start, stop):
    part = values[start:stop]
    return (len(part), 1000.0 * sum(part) / len(part) if part else float("nan"))


def profile_block(calls, lattice, basis, low, high, make):
    made = []
    profiler = cProfile.Profile()
    for index in range(low, high):
        if index == low + 5:
            profiler.enable()
        made.append(make(index))
    profiler.disable()
    made.append  # the objects are retained so nothing is collected early
    return pstats.Stats(profiler), made


def top_own(stats, count=12):
    rows = []
    for key, value in stats.stats.items():
        rows.append((value[2], value[3], value[1], key))
    rows.sort(reverse=True)
    return rows[:count]


def main(argv):
    calls = 3000
    specimen = "U2m2"
    for argument in argv:
        if argument.startswith("calls="):
            calls = int(argument.split("=", 1)[1])
        elif argument.startswith("specimen="):
            specimen = argument.split("=", 1)[1]
    log(f"probe: what _lattice_subobject_spanning computes or scans ({specimen}, {calls} calls)")
    lattice = SPECIMENS[specimen]()
    log(f"lattice {lattice} of rank {lattice.module_rank()}")
    instrument()
    generators = tuple(lattice.module_generators())
    basis = (generators[0], generators[1])
    log(f"span basis of {len(basis)} vectors: {basis}")

    def span(index):
        """One cold construction: a distinct basis each call, so no cache answers it.

        ``_lattice_subobject_spanning`` is a ``cached_function``: the same basis
        twice is the same subobject and the second call is a dictionary lookup
        (measured: 1480 identical calls cost 0.04 s in total).  The plane row's
        calls are not repeats -- every plane has its own basis -- so the probe
        gives each call its own basis, ``g0 + i*g1`` with ``g2``, which is a
        distinct independent pair for every ``i``.
        """
        return lat._lattice_subobject_spanning(
            lattice, (generators[0] + index * generators[1], generators[2])
        )
    log("populations before the first call:")
    for name, value in population(lattice):
        log(f"  {name:<44}{value}")

    early, early_made = profile_block(calls, lattice, basis, 20, 40, span)
    late_at = calls // 10
    late, late_made = profile_block(calls, lattice, basis, late_at, late_at + 20, span)

    made = list(early_made) + list(late_made)
    begin = now()
    for index in range(max(calls - 60, 0)):
        made.append(span(index))
    wall = now() - begin
    log("")
    log(f"{len(made)} objects built; the plain loop of {max(calls - 60, 0)} calls took {wall:.1f} s")
    log("populations after the last call:")
    for name, value in population(lattice):
        log(f"  {name:<44}{value}")
    log("")
    log("=== the steps of one construction: first 100 calls against the last 100 ===")
    log(f"  {'step':<40}{'calls':>7}{'first ms':>10}{'last ms':>10}{'ratio':>8}{'total s':>10}")
    for key in sorted(STEPS, key=lambda name: -STEPS[name]):
        values = SERIES[key]
        _n1, first = block(values, 0, 100)
        _n2, last = block(values, len(values) - 100, len(values))
        log(
            f"  {key:<40}{len(values):>7}{first:>10.3f}{last:>10.3f}"
            f"{(last / first if first else float('nan')):>8.2f}{STEPS[key]:>10.2f}"
        )
    log("")
    log("=== own time, cProfile over calls 25-40 (early) ===")
    log(f"  {'file:line':<46}{'function':<32}{'own s':>9}{'cum s':>9}{'calls':>7}")
    for own, cum, nc, key in top_own(early):
        where = f"{key[0].rsplit('/', 1)[-1]}:{key[1]}"
        log(f"  {where:<46}{key[2][:31]:<32}{own:>9.4f}{cum:>9.4f}{nc:>7}")
    log("")
    log(f"=== own time, cProfile over calls {late_at + 5}-{late_at + 20} ===")
    log(f"  {'file:line':<46}{'function':<32}{'own s':>9}{'cum s':>9}{'calls':>7}")
    for own, cum, nc, key in top_own(late):
        where = f"{key[0].rsplit('/', 1)[-1]}:{key[1]}"
        log(f"  {where:<46}{key[2][:31]:<32}{own:>9.4f}{cum:>9.4f}{nc:>7}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
