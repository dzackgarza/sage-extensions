r"""#528: what one coordinate read of a `T_Co` vector costs, and what a span costs.

The walk that transports the `Otilde(T_Co)` plane row's representatives makes
**4.50** ``to_vector`` calls per coordinate read inside
``_span_basis_elements``, and **9** per span basis, in every one of the thirteen
15-second windows the stage probe sampled (`issue528-otilde-stage-slice-run1.log`,
363.8 s to 562.8 s) -- a constant per element, not a growing one.  Those nine
reads are the per-element cost the row pays ~135 times a second.
``FramedFreeModules.ElementMethods.to_vector`` states that it *is* the
coordinates of the element (``v.to_vector()(i)`` is the coefficient of ``e_i``),
and it produces them by ``parent()._framing_lift(self)``, which constructs an
element of the framing source per call; the two reads a span makes of one
vector -- ``_module_subobject_constructor_data`` and the Gram rows -- therefore
derive the same datum twice.

This probe measures, on `T_Co` itself:

  * one ``to_vector`` of a dense vector, and one of a two-term vector;
  * ``_span_basis_elements`` for a two-vector basis, and the same construction
    with ``to_vector`` retaining its element's coordinates -- the same code, with
    the datum carried instead of re-derived -- so the difference is the reads and
    nothing else;
  * the number of ``to_vector`` calls each arrangement makes, which is diagnosis,
    not a cost.

The repairs' candidate is a retained datum per element (the same contract
`1a1debc9bd` applied to a torsor's base point), so the second number is what
that repair buys on this object.
"""

import time
import traceback

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories.modules.framed import framed_free_modules as ffm

START = time.monotonic()
CALLS = {}


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:6.2f}s]", *parts, flush=True)


def count_reads(element_methods):
    """Shadow ``to_vector`` on a class, counting calls."""
    original = element_methods.to_vector

    def counted(self):
        CALLS["to_vector"] = CALLS.get("to_vector", 0) + 1
        return original(self)

    element_methods.to_vector = counted
    return original


def cached_reads(element_methods):
    """Shadow ``to_vector`` so that an element's coordinates are retained once."""
    original = getattr(element_methods, "to_vector")

    def retained(self):
        CALLS["to_vector"] = CALLS.get("to_vector", 0) + 1
        cache = self.__dict__.get("_probe528_coordinates")
        if cache is None:
            cache = original(self)
            self.__dict__["_probe528_coordinates"] = cache
        return cache

    element_methods.to_vector = retained
    return original


def span_of(lattice, basis):
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        _span_basis_elements,
    )

    return _span_basis_elements(lattice, basis)


def main():
    lattice = NamedLattices.Tco
    labels = tuple(lattice.module_generating_set())
    say(f"lattice {lattice}, rank {lattice.module_rank()}")
    dense = lattice.linear_combination({
        label: ZZ(3 + position)
        for position, label in enumerate(labels)
    })
    sparse = lattice.linear_combination({labels[0]: ZZ(2), labels[3]: ZZ(1)})
    for name, vector in (("dense", dense), ("two-term", sparse)):
        begin = now()
        for _ in range(200):
            vector.to_vector()
        say(f"one to_vector of the {name} vector: {1000.0 * (now() - begin) / 200:.3f} ms")

    # `_lattice_subobject_spanning` is a cached function keyed by the basis, so a
    # repeated basis is a dictionary lookup and measures nothing.  Every call
    # below therefore takes its own basis -- `dense + i*sparse` with `sparse`,
    # an independent pair per `i` -- and the two arrangements draw from disjoint
    # ranges so that neither runs on the other's cache.
    count = 40
    engine_class = ffm.FramedFreeModules.ElementMethods
    original = count_reads(engine_class)
    try:
        begin = now()
        for i in range(count):
            span_of(lattice, (dense + ZZ(i) * sparse, sparse))
        plain = 1000.0 * (now() - begin) / count
        plain_reads = CALLS.get("to_vector", 0) / count
    finally:
        engine_class.to_vector = original
    say(f"one cold span basis, {plain_reads:.1f} to_vector a call: {plain:.3f} ms")

    CALLS.clear()
    original = cached_reads(engine_class)
    try:
        begin = now()
        for i in range(count, 2 * count):
            span_of(lattice, (dense + ZZ(i) * sparse, sparse))
        retained = 1000.0 * (now() - begin) / count
        retained_reads = CALLS.get("to_vector", 0) / count
    finally:
        engine_class.to_vector = original
    say(f"one cold span basis with the coordinates retained: {retained:.3f} ms")
    say(
        f"RESULT dense_to_vector_ms=.. span_ms={plain:.3f} span_reads={plain_reads:.1f} "
        f"cached_span_ms={retained:.3f} cached_span_reads={retained_reads:.1f} "
        f"ratio={plain / retained:.2f}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        raise
