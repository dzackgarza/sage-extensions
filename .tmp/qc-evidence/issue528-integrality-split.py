r"""#528: where one ``is_integral_on`` call's time goes, and which of its data are per call.

`0c68a6f4ca` traced the elevated per-class cost of the lift locus to
``integral_restriction`` -> ``is_integral_on`` (``lattice_morphisms.py:1483``)
-> ``factor_through_or_none`` -> ``_preimage_or_none`` ->
``_preimage_through_the_extension_framing`` -> the coordinate solve, and named
one datum as the suspect: the target's frame inside the extension framing,
which is a property of the target lattice.

This probe separates the possibilities instead of assuming one:

* **identity of the data.**  Whether ``ModulesOverIntegralDomains(ZZ)(L)``, its
  ``generic_fibre_map()``, and ``Modules(QQ).restriction_of_scalars(f)`` are the
  same objects on a second access.  A fresh object per access is a cache that
  cannot hit, whatever ``@cached_method`` says on the method.
* **cost of one call.**  ``integral_restriction`` and ``is_integral_on`` timed
  on the same isometry, several times, on the control ``U(2) + U(2) + <2>``.
* **the split.**  One ``cProfile`` of a batch of ``is_integral_on`` calls, by
  own and cumulative time, so whichever owner holds the time is named at its
  line.

Nothing is changed in the library and no wall time is asserted from: the numbers
are printed for the commit body that follows.

    sage -python <this file>
"""

import cProfile
import io
import pstats
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.lattice_morphisms import LatticeIsometryMethods
from sage_extensions.categories.modules.pure.modules import ModulesOverIntegralDomains

START = time.monotonic()
BATCH = 40


def say(*parts):
    print(f"[{time.monotonic() - START:7.1f}s]", *parts, flush=True)


def report(stats, title, top=18):
    rows = []
    for key, value in stats.stats.items():
        filename, lineno, name = key
        cc, nc, own, cum, _callers = value
        rows.append((filename.rsplit("/", 1)[-1], lineno, name, own, cum, nc))
    say("")
    say(f"=== {title}: by own time ===")
    say(f"  {'file:line':<46}{'function':<32}{'own s':>9}{'cum s':>9}{'calls':>9}")
    for filename, lineno, name, own, cum, nc in sorted(rows, key=lambda row: -row[3])[:top]:
        say(f"  {filename + ':' + str(lineno):<46}{name[:31]:<32}{own:>9.3f}{cum:>9.3f}{nc:>9}")
    say("")
    say(f"=== {title}: by cumulative time ===")
    for filename, lineno, name, own, cum, nc in sorted(rows, key=lambda row: -row[4])[:top]:
        say(f"  {filename + ':' + str(lineno):<46}{name[:31]:<32}{own:>9.3f}{cum:>9.3f}{nc:>9}")


def main():
    hyperbolic = Lattices(ZZ)([[0, 2], [2, 0]])
    lattice = hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    labels = tuple(lattice.module_generating_set())
    marked = lattice.module_generator(labels[0])
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    torsor = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())
    quotient = torsor.integral_parameter_quotient()
    inclusion = quotient.domain().inclusion()
    parameter = inclusion(quotient.preimage(quotient.codomain().zero())).underlying_element()
    lift = torsor.parameterization()(parameter)
    say(f"lattice {lattice}")
    say("the lift at the zero parameter, which is the base point")

    # 1. identity of the data
    first = ModulesOverIntegralDomains(ZZ)(lattice)
    second = ModulesOverIntegralDomains(ZZ)(lattice)
    say("")
    say("=== is each datum the same object on a second access? ===")
    say(f"  ModulesOverIntegralDomains(ZZ)(L) is the same module: {first is second}")
    say(f"  generic_fibre_map() is the same morphism: "
        f"{first.generic_fibre_map() is second.generic_fibre_map()}")
    restrict_one = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())
    restrict_two = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())
    say(f"  Modules(QQ).restriction_of_scalars(f) is the same category: {restrict_one is restrict_two}")
    target_embedding = first.generic_fibre_map()
    if hasattr(target_embedding, "_integral_extension_coordinate_span"):
        first_span = target_embedding._integral_extension_coordinate_span()
        second_span = target_embedding._integral_extension_coordinate_span()
        say(f"  the extension framing span is the same datum: {first_span is second_span}")

    # 2. the cost of one call, on this isometry
    for name, call in (
        ("integral_restriction(L, L)", lambda: lift.integral_restriction(lattice, lattice)),
        ("is_integral_on(L, L)", lambda: lift.is_integral_on(lattice, lattice)),
    ):
        call()
        begin = time.monotonic()
        for _ in range(BATCH):
            call()
        say("")
        say(f"  {name}: {(time.monotonic() - begin) / BATCH * 1000:.2f} ms a call over {BATCH} calls")

    # 3. the split
    for name, call in (
        ("integral_restriction", lambda: lift.integral_restriction(lattice, lattice)),
        ("is_integral_on", lambda: lift.is_integral_on(lattice, lattice)),
    ):
        profiler = cProfile.Profile()
        profiler.enable()
        for _ in range(BATCH):
            call()
        profiler.disable()
        report(pstats.Stats(profiler), f"{BATCH} calls of {name}")
    say("")
    say("PROBE DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
