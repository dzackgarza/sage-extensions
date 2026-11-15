r"""#528: one `eichler_transvection(f, a)` of T_Co, split into the objects it builds.

`1a1fc046c0` split one `_lift_at` and left 20.7 ms a call in
`eichler_transvection`; `45aeada173` measured 80.994 s of the ambient row's
113.940 s `_lift_at` there.  This probe goes one level down.  It builds the call the lift locus makes
(`isotropic_lifts.py:396`): T_Co's **rational** lattice -- the ring is `QQ`
there, and the integral lattice's own transvection is four times cheaper, so
the specimen's ring is part of the measurement -- with `e` its isotropic
witness and `a` a member of `e^perp`.  It reports, per call:

  * the library's own `eichler_transvection(f, a)`, wall time;
  * the base tree's arrangement of that body re-run stage by stage
    (`src/sage_extensions/categories/lattices.py:8329` there), each stage's own
    time, with a check that the staged reproduction is the library's matrix
    exactly -- kept unchanged across trees so one file measures both;
  * the crossings the body makes, counted per stage: `_owned_engine_element`
    and `_engine_element` (`rings/ring_foundation.py:8025`, `:8038`), the ring's
    `_element_constructor_` (`ring_foundation.py:6647`);
  * the same formula arranged as the formula reads -- coordinates crossed once,
    the arithmetic in the engine, the matrix built in the engine -- which is
    the lower bound the formula itself sets;
  * a `cProfile` of the library calls, by self time and by call count.

The transvection is Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
Lemma 3.1, equation (4), printed p. 8:

    t(e, a): v |-> v - (a, v)e + (e, v)a - (1/2)(a, a)(e, v)e,

which is the formula `lattices.py:8380` states and the loop at `:8360` applies.
Its matrix in the lattice's basis costs O(rank^2) ring operations; everything
this probe finds above that is bookkeeping, and the stage table says where.

    mode=split (default)   the split, on 20 calls
    mode=row               the ambient O(L) plane row, capped, with the call
                           counts inside its `eichler_transvection`s
"""

import cProfile
import io
import pstats
import sys
import threading
import time

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories import lattices as lat_module
from sage_extensions.categories.rings import ring_foundation as rf
from sage_extensions.categories.modules.framed import framed_free_modules as ffm

START = time.monotonic()
COUNTS = {}
SECONDS = {}
COUNTING = True


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
    if getattr(original, "_probe528_wrapped", False):
        return True

    def counted(*args, **kwargs):
        if not COUNTING:
            return original(*args, **kwargs)
        begin = now()
        try:
            return original(*args, **kwargs)
        finally:
            COUNTS[name] = COUNTS.get(name, 0) + 1
            SECONDS[name] = SECONDS.get(name, 0.0) + (now() - begin)

    counted._probe528_wrapped = True
    setattr(target, name, counted)
    return True


WRAPPED = ()


def wrap_everywhere(module, name):
    """Wrap every class in ``module`` that defines ``name``, nested ones included."""
    done = []

    def visit(owner, prefix):
        for key, value in vars(owner).items():
            if not isinstance(value, type):
                continue
            if name in vars(value):
                if wrap(value, name):
                    done.append(f"{prefix}{key}")
            visit(value, f"{prefix}{key}.")

    visit(module, f"{module.__name__.rsplit('.', 1)[-1]}.")
    return done


def instrument():
    """Count the crossings the transvection's body makes, by name."""
    done = []
    # The body imports these from ring_foundation inside itself, so the module
    # attribute is what a call reads.
    for name in ("_owned_engine_element", "_engine_element", "_engine_ring"):
        if name in vars(rf):
            if wrap(rf, name):
                done.append(name)
    # `_engine_component_matrix` is imported into the lattices module at import.
    if wrap(lat_module, "_engine_component_matrix"):
        done.append("_engine_component_matrix")
    # The call under study, so a row reports how many it made and what they cost.
    if wrap(lat_module.Lattices.ParentMethods, "eichler_transvection"):
        done.append("eichler_transvection")
    if wrap(lat_module.Lattices.ParentMethods, "_eichler_transvection_column_matrix"):
        done.append("_eichler_transvection_column_matrix")
    # The ring's own constructors and the coordinate reader, wherever they live.
    for module, name in (
        (rf, "_element_constructor_"),
        (ffm, "to_vector"),
        (ffm, "_framing_lift"),
    ):
        for owner in wrap_everywhere(module, name):
            done.append(f"{name}@{owner}")
    return done


def specimen():
    """The rational form of T_Co, an isotropic `e`, and a member of `e^perp`.

    The lift locus calls ``_target_witt.rational_lattice().eichler_transvection``
    (`isotropic_lifts.py:396`), so the call this probe splits is over the
    fraction field `QQ`, not over `ZZ`: the integral lattice's own transvection
    costs a quarter of this one, and its ring is not the row's.
    """
    integral = NamedLattices.Tco
    labels = tuple(integral.module_generating_set())
    gram = [
        [int(integral.b(integral.module_generator(row), integral.module_generator(column)))
         for column in labels]
        for row in labels
    ]
    lattice = Lattices(QQ)(gram)
    lattice_labels = tuple(lattice.module_generating_set())
    isotropic = lattice.isotropic_vector()
    ring = lattice.base_ring()
    zero = ring.zero()
    orthogonal = lattice.module_generator(
        lattice_labels[0]
    ) + ring(3) * lattice.module_generator(lattice_labels[3])
    assert isotropic.q() == zero, f"the specimen's e is not isotropic: q(e) = {isotropic.q()}"
    assert isotropic.b(orthogonal) == zero, (
        f"the specimen's a is not in e^perp: b(e, a) = {isotropic.b(orthogonal)}"
    )
    assert lattice.module_rank() == integral.module_rank() == 11
    return lattice, lattice_labels, isotropic, orthogonal


def check(lattice, isotropic, orthogonal, transvection):
    """The transvection is an isometry fixing e, as equation (4) states."""
    labels = tuple(lattice.module_generating_set())
    basis = tuple(lattice.module_generator(label) for label in labels)
    images = tuple(transvection(vector) for vector in basis)
    assert transvection(isotropic) == isotropic, "the transvection moved e"
    for left in range(len(basis)):
        for right in range(len(basis)):
            assert lattice.b(images[left], images[right]) == lattice.b(basis[left], basis[right]), (
                f"the transvection did not preserve b(e_{left}, e_{right})"
            )
    return True


def split_stages(lattice, isotropic, orthogonal, iterations):
    """Re-run `_eichler_transvection_column_matrix` stage by stage, timed."""
    from sage.matrix.constructor import matrix

    ring = lattice.base_ring()
    zero = ring.zero()
    times = {}
    calls = {}
    stages = []

    def stage(name, function):
        begin = now()
        before = dict(COUNTS)
        value = function()
        times[name] = times.get(name, 0.0) + (now() - begin)
        for key in COUNTS:
            delta = COUNTS[key] - before.get(key, 0)
            if delta:
                calls.setdefault(name, {})
                calls[name][key] = calls[name].get(key, 0) + delta
        stages.append(name)
        return value

    assembled = None
    library_matrix = None
    for iteration in range(iterations):
        def guards():
            assert isotropic.parent() is lattice and orthogonal.parent() is lattice
            assert isotropic.q() == zero
            assert isotropic.b(orthogonal) == zero

        stage("1 the three guards (parent, q(e), b(e, a))", guards)
        fraction_field = stage("2 ring.fraction_field()", ring.fraction_field)
        half_norm = stage(
            "2 half_norm = q(a)/2 in the fraction field",
            lambda: fraction_field(orthogonal.q()) / fraction_field(ring(2)),
        )
        labels = stage(
            "3 labels = tuple(module_generating_set())",
            lambda: tuple(lattice.module_generating_set()),
        )
        engine = stage("4 engine = _engine_ring(ring)", lambda: rf._engine_ring(ring))
        isotropic_coordinates = stage(
            "5 e's coordinates, as written (to_vector per label)",
            lambda: tuple(rf._engine_element(ring, isotropic.to_vector()(label)) for label in labels),
        )
        orthogonal_coordinates = stage(
            "6 a's coordinates, as written (to_vector per label)",
            lambda: tuple(rf._engine_element(ring, orthogonal.to_vector()(label)) for label in labels),
        )
        one_isotropic_coordinates = stage(
            "5+6 the same two, one to_vector each (the datum read once)",
            lambda: tuple(
                tuple(rf._engine_element(ring, values(label)) for label in labels)
                for values in (isotropic.to_vector(), orthogonal.to_vector())
            ),
        )
        del one_isotropic_coordinates
        gram = stage(
            "7 gram = _engine_component_matrix(gram_tensor())",
            lambda: lat_module._engine_component_matrix(lattice.gram_tensor()),
        )
        pairings_with_isotropic = stage(
            "8 gram * e (one rank-by-one product)",
            lambda: gram * matrix(engine, len(labels), 1, isotropic_coordinates),
        )
        pairings_with_orthogonal = stage(
            "8 gram * a (one rank-by-one product)",
            lambda: gram * matrix(engine, len(labels), 1, orthogonal_coordinates),
        )

        def the_loop():
            columns = []
            for source_position, label in enumerate(labels):
                pairing_with_isotropic = rf._owned_engine_element(
                    ring, pairings_with_isotropic[source_position, 0]
                )
                pairing_with_orthogonal = rf._owned_engine_element(
                    ring, pairings_with_orthogonal[source_position, 0]
                )
                half_coefficient = half_norm * fraction_field(pairing_with_isotropic)
                assert half_coefficient in ring
                integral_half_coefficient = ring(half_coefficient)
                columns.append(
                    tuple(
                        (
                            (ring.one() if target_position == source_position else zero)
                            - pairing_with_orthogonal
                            * rf._owned_engine_element(ring, isotropic_coordinates[target_position])
                            + pairing_with_isotropic
                            * rf._owned_engine_element(ring, orthogonal_coordinates[target_position])
                            - integral_half_coefficient
                            * rf._owned_engine_element(ring, isotropic_coordinates[target_position])
                        )
                        for target_position in range(len(labels))
                    )
                )
            return columns

        columns = stage("9 the per-entry loop (rank^2 entries)", the_loop)

        def assembly():
            return matrix(
                engine,
                [
                    [
                        rf._engine_element(ring, columns[source_position][target_position])
                        for source_position in range(len(labels))
                    ]
                    for target_position in range(len(labels))
                ],
            )

        assembled = stage("10 the matrix assembly, entry by entry", assembly)
        if iteration == 0:
            library_matrix = lattice._eichler_transvection_column_matrix(
                isotropic, orthogonal
            )
            assert assembled == library_matrix, (
                "the staged reproduction is not the library's column matrix"
            )
        automorphisms = stage("11 lattice.Aut()", lattice.Aut)
        stage(
            "12 _isometry_from_column_matrix(matrix)",
            lambda: automorphisms._isometry_from_column_matrix(assembled),
        )

    per_call = {name: 1000.0 * times[name] / iterations for name in stages}
    return per_call, calls, times, iterations


def formula_only(lattice, isotropic, orthogonal, iterations):
    """The formula's arithmetic: coordinates crossed once, matrix built in the engine.

    Equation (4) of Gritsenko--Hulek--Sankaran, section 3.1, printed p. 8, read
    as the body at `lattices.py:8360` reads it, with the owned ring crossed once
    per coordinate and once for `q(a)`: nothing else in the body's work is the
    formula's.
    """
    from sage.matrix.constructor import matrix
    ring = lattice.base_ring()
    labels = tuple(lattice.module_generating_set())
    gram = lat_module._engine_component_matrix(lattice.gram_tensor())
    engine = rf._engine_ring(ring)
    begin = now()
    for _ in range(iterations):
        e_values = isotropic.to_vector()
        a_values = orthogonal.to_vector()
        e_coordinates = [rf._engine_element(ring, e_values(label)) for label in labels]
        a_coordinates = [rf._engine_element(ring, a_values(label)) for label in labels]
        half_norm = engine(rf._engine_element(ring, orthogonal.q())) / engine(2)
        pairings_e = [
            sum(gram[row, column] * e_coordinates[column] for column in range(len(labels)))
            for row in range(len(labels))
        ]
        pairings_a = [
            sum(gram[row, column] * a_coordinates[column] for column in range(len(labels)))
            for row in range(len(labels))
        ]
        entries = []
        for target_position in range(len(labels)):
            row = []
            for source_position in range(len(labels)):
                coefficient = (
                    (engine(1) if target_position == source_position else engine(0))
                    - pairings_a[source_position] * e_coordinates[target_position]
                    + pairings_e[source_position] * a_coordinates[target_position]
                    - half_norm * pairings_e[source_position] * e_coordinates[target_position]
                )
                row.append(coefficient)
            entries.append(row)
        transvection_matrix = matrix(engine, entries)
    spent = now() - begin
    assert transvection_matrix == lattice._eichler_transvection_column_matrix(
        isotropic, orthogonal
    ), "the formula-only arrangement is not the library's column matrix"
    return 1000.0 * spent / iterations


def profile_calls(lattice, isotropic, orthogonal, iterations, lines=22):
    """`cProfile` over `iterations` library calls: self time and call counts."""
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(iterations):
        lattice.eichler_transvection(isotropic, orthogonal)
    profiler.disable()
    stream = io.StringIO()
    statistics = pstats.Stats(profiler, stream=stream)
    statistics.sort_stats("tottime").print_stats(lines)
    by_self = stream.getvalue()
    stream = io.StringIO()
    statistics = pstats.Stats(profiler, stream=stream)
    statistics.sort_stats("ncalls").print_stats(lines)
    by_calls = stream.getvalue()
    return by_self, by_calls


def split(argv):
    global COUNTING
    iterations = 20
    for argument in argv:
        if argument.startswith("iterations="):
            iterations = int(argument.split("=", 1)[1])
    lattice, labels, isotropic, orthogonal = specimen()
    say(f"lattice {lattice} of rank {lattice.module_rank()}")
    say(f"e = {isotropic}, q(e) = {isotropic.q()}")
    say(f"a = {orthogonal}, b(e, a) = {isotropic.b(orthogonal)}")

    begin = now()
    transvection = lattice.eichler_transvection(isotropic, orthogonal)
    say(f"one library eichler_transvection: {1000.0 * (now() - begin):.3f} ms")
    say(f"checks (t(e) = e, 121 pairings preserved): {check(lattice, isotropic, orthogonal, transvection)}")

    begin = now()
    for _ in range(iterations):
        lattice.eichler_transvection(isotropic, orthogonal)
    library_ms = 1000.0 * (now() - begin) / iterations
    say(f"the library call, {iterations} times: {library_ms:.3f} ms a call")

    wrapped = instrument()
    say("instrumented:", ", ".join(wrapped) if wrapped else "nothing")
    counts_before = dict(COUNTS)
    seconds_before = dict(SECONDS)
    begin = now()
    for _ in range(iterations):
        lattice.eichler_transvection(isotropic, orthogonal)
    counted_ms = 1000.0 * (now() - begin) / iterations
    say(f"the same call counted, {iterations} times: {counted_ms:.3f} ms a call")
    say("")
    say("=== what one library call crosses ===")
    say(f"  {'call':<44}{'calls':>9}{'ms':>9}{'us/call':>10}")
    for name in sorted(COUNTS, key=lambda key: -SECONDS.get(key, 0.0)):
        delta = COUNTS[name] - counts_before.get(name, 0)
        spent = SECONDS[name] - seconds_before.get(name, 0.0)
        if delta <= 0:
            continue
        say(
            f"  {name:<44}{delta / iterations:>9.1f}"
            f"{1000.0 * spent / iterations:>9.3f}{1e6 * spent / delta:>10.1f}"
        )

    say("")
    say("=== the crossings, by stage (one call) ===")
    COUNTING = True
    _, stage_calls, _, _ = split_stages(lattice, isotropic, orthogonal, 1)
    for name in stage_calls:
        say(f"  {name}")
        for key in sorted(stage_calls[name], key=lambda k: -stage_calls[name][k]):
            say(f"      {key:<40}{stage_calls[name][key]:>8}")

    say("")
    say("")
    say("=== the base body's arrangement, stage by stage, per call (counters off) ===")
    say("    the stages below are `8316-8409` as the base tree wrote them, kept")
    say("    unchanged so one probe measures both trees; their matrix is checked")
    say("    equal to the library's, and the library no longer runs them.")
    COUNTING = False
    per_call, _, _, iterations = split_stages(lattice, isotropic, orthogonal, iterations)
    say(f"  {'stage':<56}{'ms/call':>10}")
    total = 0.0
    for name in per_call:
        total += per_call[name]
        say(f"  {name:<56}{per_call[name]:>10.3f}")
    say(f"  {'total':<56}{total:>10.3f}")

    say("")
    formula_ms = formula_only(lattice, isotropic, orthogonal, iterations)
    say(f"=== the formula's own arithmetic, engine throughout: {formula_ms:.3f} ms a call ===")
    say(
        f"    the library {library_ms:.3f} ms, the base arrangement {sum(per_call.values()):.3f} ms,"
        f" the formula {formula_ms:.3f} ms"
    )
    say(
        f"RESULT library_ms={library_ms:.3f} counted_ms={counted_ms:.3f} "
        f"staged_ms={sum(per_call.values()):.3f} formula_ms={formula_ms:.3f} "
        f"ratio={library_ms / formula_ms:.2f}"
    )

    say("")
    say("=== cProfile over the library calls ===")
    by_self, by_calls = profile_calls(lattice, isotropic, orthogonal, iterations)
    say(by_self)
    say(by_calls)
    return 0


def row(argv):
    """The ambient O(L) plane row, capped, counting its transvections."""
    import signal
    import traceback

    cap = 520.0
    bare = False
    for argument in argv:
        if argument.startswith("cap="):
            cap = float(argument.split("=", 1)[1])
        if argument == "bare":
            bare = True
    if bare:
        say("not instrumented: the row's own time")
    else:
        wrapped = instrument()
        say("instrumented:", ", ".join(wrapped))

    class Stop(Exception):
        pass

    def alarm(signum, frame):
        raise Stop

    lattice = NamedLattices.Tco
    say(f"lattice {lattice}")
    signal.signal(signal.SIGALRM, alarm)
    begin = now()
    decided = True
    planes = None
    try:
        signal.setitimer(signal.ITIMER_REAL, cap)
        planes = tuple(
            lattice.stable_orthogonal_group().supergroup().isotropic_orbit_representatives(2)
        )
    except Stop:
        decided = False
        say(f"the row did not return inside its {cap:.0f} s cap")
    except Exception:
        decided = False
        say("the row raised:")
        traceback.print_exc()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        spent = now() - begin
    say("")
    say(f"the ambient row: {spent:.1f} s, decided {decided}")
    if decided:
        say(f"planes: {len(planes)}")
    say(f"  {'call':<38}{'calls':>8}{'seconds':>10}{'us/call':>10}")
    for name in sorted(COUNTS, key=lambda key: -SECONDS.get(key, 0.0)):
        say(
            f"  {name:<38}{COUNTS[name]:>8}"
            f"{SECONDS[name]:>10.3f}{1e6 * SECONDS[name] / COUNTS[name]:>10.1f}"
        )
    say(
        f"RESULT row_seconds={spent:.1f} decided={decided} "
        + " ".join(f"{name}={COUNTS[name]}" for name in sorted(COUNTS))
    )
    return 0



def public_counts(argv):
    """The crossings a test can see: the public methods one transvection asks.

    A `pytest`-collected test may not read a private attribute (TL02), so the
    seam a red test can count is a public one: the two vectors' ``to_vector``
    and the owned ring's ``one``, ``zero`` and ``fraction_field``, shadowed on
    the instances the caller holds.  This mode prints those counts for the
    T_Co specimen and for a rank-3 control, at whatever tree it runs on.
    """
    def counts_for(lattice, isotropic, orthogonal):
        ring = lattice.base_ring()
        counts = {}
        restorations = []

        def shadow(owner, name, key):
            original = getattr(owner, name)

            def counted(*args, **kwargs):
                counts[key] = counts.get(key, 0) + 1
                return original(*args, **kwargs)

            setattr(owner, name, counted)
            restorations.append((owner, name, original))

        shadow(isotropic, "to_vector", "e.to_vector")
        shadow(orthogonal, "to_vector", "a.to_vector")
        for name in ("one", "zero", "fraction_field"):
            shadow(ring, name, f"ring.{name}")
        shadow(lattice, "gram_tensor", "gram_tensor")
        shadow(lattice, "module_generating_set", "module_generating_set")
        try:
            transvection = lattice.eichler_transvection(isotropic, orthogonal)
            moved = transvection(isotropic) == isotropic
        finally:
            for owner, name, original in restorations:
                setattr(owner, name, original)
        return counts, moved

    lattice, labels, isotropic, orthogonal = specimen()
    say(f"=== the T_Co specimen ({lattice.base_ring()}, rank {lattice.module_rank()}) ===")
    counts, moved = counts_for(lattice, isotropic, orthogonal)
    for key in sorted(counts):
        say(f"  {key:<24}{counts[key]:>8}")
    say(f"  the transvection fixes e: {moved}")
    say(f"COUNTS tco " + " ".join(f"{key}={counts[key]}" for key in sorted(counts)))

    control = Lattices(QQ)([[0, 1, 0], [1, 0, 0], [0, 0, 2]])
    control_labels = tuple(control.module_generating_set())
    control_e = control.module_generator(control_labels[0])
    control_a = control.module_generator(control_labels[2])
    assert control_e.q() == control.base_ring().zero()
    assert control_e.b(control_a) == control.base_ring().zero()
    say("")
    say(f"=== the rank-3 control ({control}) ===")
    counts, moved = counts_for(control, control_e, control_a)
    for key in sorted(counts):
        say(f"  {key:<24}{counts[key]:>8}")
    say(f"  the transvection fixes e: {moved}")
    say(f"COUNTS control " + " ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    return 0



def otilde(argv):
    """The Otilde(T_Co) plane row once, capped, with progress lines every 30 s.

    The issue's own reading is that this row spends its first plane's time in
    stages before any transvection: the ambient `O(L)` row, the parabolic
    family, `quotient.image_order`, the discriminant images and the walk.  The
    progress lines say how far one capped run got and what the instrumented
    crossings had reached when the cap closed.
    """
    cap = 520.0
    for argument in argv:
        if argument.startswith("cap="):
            cap = float(argument.split("=", 1)[1])
    wrapped = instrument()
    say("instrumented:", ", ".join(wrapped))
    begin = now()

    def tick():
        """Print what the row has reached, every 30 s, from a thread.

        A signal cannot carry this: an `AlarmInterrupt` raised inside
        `libgap.FactorCosetAction` is cysignals' exception, not this probe's.
        """
        while not finished.wait(30.0):
            say(
                f"  progress {now() - begin:6.1f} s: "
                + " ".join(
                    f"{name}={COUNTS[name]}"
                    for name in (
                        "eichler_transvection",
                        "to_vector",
                        "_engine_component_matrix",
                    )
                    if name in COUNTS
                )
            )

    lattice = NamedLattices.Tco
    say(f"lattice {lattice}")
    finished = threading.Event()
    watcher = threading.Thread(target=tick, daemon=True)
    watcher.start()
    decided = True
    planes = None
    try:
        planes = tuple(
            lattice.stable_orthogonal_group().isotropic_orbit_representatives(2)
        )
    except Exception as error:
        decided = False
        say(f"the row raised {type(error).__name__}: {error}"[:200])
    finally:
        finished.set()
        spent = now() - begin
    if spent >= cap:
        say(f"the row ran past its {cap:.0f} s cap")
    say("")
    say(f"the Otilde row: {spent:.1f} s, decided {decided}")
    if decided:
        say(f"planes: {len(planes)}")
    for name in sorted(COUNTS, key=lambda key: -SECONDS.get(key, 0.0)):
        say(f"  {name:<44}{COUNTS[name]:>10}{SECONDS[name]:>10.3f}")
    say(
        f"RESULT otilde_seconds={spent:.1f} decided={decided} "
        + " ".join(f"{name}={COUNTS[name]}" for name in sorted(COUNTS))
    )
    return 0


def main(argv):
    if argv and argv[0] == "row":
        return row(argv[1:])
    if argv and argv[0] == "otilde":
        return otilde(argv[1:])
    if argv and argv[0] == "counts":
        return public_counts(argv[1:])
    if argv and argv[0] == "split":
        argv = argv[1:]
    return split(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
