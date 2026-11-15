r"""#528: does the ambient row's slowdown come from more lift tests, or dearer ones?

`204ffbb96e` corrected the integral lift locus (the Smith reading of the
section's coordinates) and, with it, replaced the per-class lift test: the old
test formed, per class, the transvection's matrix times the base point's
coordinate matrix (`eichler_transvection_matrix` and one matrix product, with
`base_images` computed once); the new one composes the owned isometries,
`eichler_transvection(f, s(a)) * base_point()`, and asks the composition for
its `integral_restriction`.  The row's ambient plane step is 54 s before that
commit and does not return in 300 s after it.

Two explanations carry different owners, so this probe separates them on the
commit's own control `U(2) + U(2) + <2>` (where #405 reproduced: 64 classes of
`P/mP` reported before the correction, 32 of them lifting):

* **more classes or more lifts**: the corrected locus covers different
  parameters, so the mathematics owes the work.  Measured as the number of
  classes tested, `prod_i gcd(step_i, m)`, and the order of the kernel;
* **dearer tests**: each class costs more.  Measured as the wall time of the
  locus divided by the classes tested, and by what the test calls: the
  transvection, the composition, `integral_restriction`, `is_integral_on`,
  `factor_through_or_none` and `solve`.

The probe calls the same public entry at both commits,
`IsotropicReductionLiftTorsors.integral_parameter_classes()`, and wraps the
calls by name, so one file runs unchanged on the base tree `a71272add9` and on
`204ffbb96e`; a call a tree does not have is reported as absent rather than
counted as zero.

    sage -python <this file>
"""

import time

from sage_extensions.all import *  # noqa: F401,F403

import importlib

from sage_extensions.categories import isotropic_lifts as il

START = time.monotonic()
COUNTS = {}
SECONDS = {}


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


def wrap(owner, name):
    """Wrap ``owner.name`` in place, counting and timing its calls."""
    target = owner
    if isinstance(owner, type):
        found = None
        for klass in owner.__mro__:
            if name in vars(klass):
                found = klass
                break
        if found is None:
            return False
        target = found
    if name not in vars(target):
        return False
    original = vars(target)[name]

    def counted(*args, **kwargs):
        begin = now()
        try:
            return original(*args, **kwargs)
        finally:
            COUNTS[name] = COUNTS.get(name, 0) + 1
            SECONDS[name] = SECONDS.get(name, 0.0) + (now() - begin)

    setattr(target, name, counted)
    return True


# The module each measured call lives in, by dotted path: a tree that moved one
# is reported rather than aborting the run.
MODULES = {
    "lattices": "sage_extensions.categories.lattices",
    "lattice_morphisms": "sage_extensions.categories.lattice_morphisms",
    "module_morphisms": "sage_extensions.categories.modules.module_morphisms.module_morphisms",
    "ring_foundation": "sage_extensions.categories.rings.ring_foundation",
}
CALLS = (
    # (module key, name, owner attribute or None for the module itself)
    ("lattices", "eichler_transvection", "Lattices.ParentMethods"),
    ("lattices", "eichler_transvection_matrix", "Lattices.ParentMethods"),
    ("lattice_morphisms", "is_integral_on", None),
    ("lattice_morphisms", "integral_restriction", None),
    ("module_morphisms", "_preimage_or_none", None),
    ("module_morphisms", "factor_through_or_none", None),
    ("ring_foundation", "_fraction_equality_status", None),
)


def resolve(module, path):
    """Walk a dotted attribute path (``"Lattices.ParentMethods"``) on a module."""
    target = module
    for part in path.split("."):
        target = getattr(target, part, None)
        if target is None:
            return None
    return target


def instrument():
    present = {}
    loaded = {}
    for key, path in MODULES.items():
        try:
            loaded[key] = importlib.import_module(path)
        except Exception as error:  # the tree moved the module: report it
            present[f"{key} (module)"] = f"absent: {error!r}"[:60]
    for key, name, owner_path in CALLS:
        module = loaded.get(key)
        if module is None:
            present[name] = False
            continue
        owner = module if owner_path is None else resolve(module, owner_path)
        present[name] = wrap(owner, name) if owner is not None else False
    torsor_class = il.IsotropicReductionLiftTorsors.ParentMethods
    for name in ("_lift_at", "parameterization", "base_point", "_target_section"):
        present[name] = wrap(torsor_class, name)
    return present


def control():
    """`U(2) + U(2) + <2>`, and the isotropic line its first basis vector spans."""
    hyperbolic = Lattices(ZZ)([[0, 2], [2, 0]])
    lattice = hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    generators = tuple(lattice.module_generators())
    vector = generators[0]
    assert lattice.b(vector, vector) == lattice.base_ring().zero(), (
        f"the control's first generator is not isotropic in {lattice}"
    )
    return lattice, lattice.primitive_isotropic_subobject(vector)


def row(argv):
    """The same instrumentation on T_Co's ambient plane row, capped.

    The row's route reaches the locus once per candidate the port tests, so the
    count of lift tests the row makes -- and their mean cost -- is what the
    locus charges the row.  Base returns; the later tree may not, so the count
    is printed whether the row returns or not.
    """
    import signal
    import traceback

    cap = 300.0
    for argument in argv:
        if argument.startswith("cap="):
            cap = float(argument.split("=", 1)[1])
    present = instrument()
    say("instrumented:", ", ".join(f"{k}={v}" for k, v in sorted(present.items())))
    lattice = NamedLattices.Tco
    say(f"lattice {lattice}")

    class Stop(Exception):
        pass

    def alarm(signum, frame):
        raise Stop

    signal.signal(signal.SIGALRM, alarm)
    begin = now()
    decided = True
    try:
        signal.setitimer(signal.ITIMER_REAL, cap)
        planes = tuple(
            lattice.stable_orthogonal_group().supergroup().isotropic_orbit_representatives(2)
        )
    except Stop:
        decided = False
        planes = None
        say(f"the row did not return inside its {cap:.0f} s cap")
    except Exception:
        decided = False
        planes = None
        say("the row raised:")
        traceback.print_exc()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        spent = now() - begin
    say("")
    say(f"the ambient row: {spent:.1f} s, decided {decided}")
    say(f"  {'call':<34}{'calls':>8}{'seconds':>10}")
    for name in sorted(COUNTS, key=lambda key: -SECONDS.get(key, 0.0)):
        say(f"  {name:<34}{COUNTS[name]:>8}{SECONDS[name]:>10.3f}")
    say(
        f"RESULT row_seconds={spent:.1f} decided={decided} "
        + " ".join(f"{name}={COUNTS[name]}" for name in sorted(COUNTS))
    )
    return 0 if decided else 2


def main(argv):
    if argv and argv[0] == "row":
        return row(argv[1:])
    present = instrument()
    say("instrumented:", ", ".join(f"{k}={v}" for k, v in sorted(present.items())))
    lattice, line = control()
    say(f"control {lattice} of rank {lattice.module_rank()}, line {line}")
    reduction = line.isotropic_reduction()
    torsor = reduction.rational_lifts(reduction, reduction.Aut().one())
    say("torsor built")
    quotient = torsor.integral_parameter_quotient()
    say(
        f"parameter lattice of rank {quotient.domain().module_rank()}, "
        f"period {torsor.integral_parameter_period()}"
    )
    before = dict(COUNTS)
    begin = now()
    classes = torsor.integral_parameter_classes()
    spent = now() - begin
    say(f"integral_parameter_classes(): {spent:.3f} s")
    second = now()
    torsor.integral_parameter_classes()
    cached = now() - second
    say(f"the same call again (cached): {cached:.3f} s")
    say("")
    say("=== the calls the locus made, by count and time ===")
    say(f"  {'call':<34}{'calls':>8}{'seconds':>10}")
    for name in sorted(COUNTS, key=lambda key: -SECONDS.get(key, 0.0)):
        delta = COUNTS[name] - before.get(name, 0)
        if delta <= 0:
            continue
        say(f"  {name:<34}{delta:>8}{SECONDS[name]:>10.3f}")
    say("")
    tests = COUNTS.get("integral_restriction", 0) - before.get("integral_restriction", 0)
    matrix_tests = COUNTS.get("eichler_transvection_matrix", 0) - before.get(
        "eichler_transvection_matrix", 0
    )
    counted = tests or matrix_tests
    say(
        f"RESULT locus_seconds={spent:.3f} tests={counted} "
        f"per_test_ms={(1000.0 * spent / counted) if counted else float('nan'):.3f} "
        f"transvections={COUNTS.get('eichler_transvection', 0)} "
        f"matrix_tests={matrix_tests} "
        f"integral_restrictions={tests} "
        f"is_integral_on={COUNTS.get('is_integral_on', 0)} "
        f"solves={COUNTS.get('solve', 0)} "
        f"fraction_equality={COUNTS.get('_fraction_equality_status', 0)}"
    )
    say(f"the locus is {classes!r}"[:180])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
