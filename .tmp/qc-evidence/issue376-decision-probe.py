"""#376: the individual steps of the indefinite decision, each timed, with a stack dump while one hangs."""
import faulthandler
import sys
import time

from sage_extensions.all import *

faulthandler.dump_traceback_later(90, repeat=True)

START = time.time()


def stamp(message):
    print(f"[{time.time() - START:8.1f}s] {message}")
    sys.stdout.flush()


def timed(label, thunk):
    print(f"[{time.time() - START:8.1f}s] --> {label}")
    sys.stdout.flush()
    begin = time.time()
    try:
        value = thunk()
    except Exception as error:  # noqa: BLE001 - report the shape of the failure
        stamp(f"{label}: {type(error).__name__}: {str(error)[:300]}")
        return None
    stamp(f"{label}: {str(value)[:200]}  [{(time.time() - begin):.1f} s]")
    return value


def _d16_plus_gram():
    def entry(i, j):
        if i == j:
            return 4 if i in (0, 15) else 2
        if {i, j} == {0, 1}:
            return -2
        if {i, j} == {0, 15}:
            return 1
        if 1 <= i <= 14 and 1 <= j <= 14 and abs(i - j) == 1:
            return -1
        return 0

    return [[entry(i, j) for j in range(16)] for i in range(16)]


C = Lattices(ZZ)
e8_squared = C("E8") + C("E8")
d16_plus = C(_d16_plus_gram()).twist(-1)
source = e8_squared.two_u_eichler_model().lattice()
target = d16_plus.two_u_eichler_model().lattice()
stamp("built source (2, 18) and target (2, 18)")
mor = source.Isom(target)
stamp("built the Mor")

timed("engine grams", lambda: tuple(gram.dimensions() for gram in mor._engine_grams()))
timed("equal engine grams", lambda: mor._engine_grams()[0] == mor._engine_grams()[1])
timed("domain.is_nondegenerate()", lambda: source.is_nondegenerate())
timed("domain.is_even()", lambda: source.is_even())
timed("domain.discriminant()", lambda: source.discriminant())
timed("discriminant_module().invariant_factors()", lambda: source.discriminant_module().invariant_factors())
timed("genus equality", lambda: source.genus() == target.genus())
timed("spinor_genus_count", lambda: source.genus().spinor_genus_count())
timed("mor.is_empty()", lambda: mor.is_empty())
timed("source.is_isometric_to(target)", lambda: source.is_isometric_to(target))
timed("source.isometry_to(target)", lambda: source.isometry_to(target))
stamp("done")
