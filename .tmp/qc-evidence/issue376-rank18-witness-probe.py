"""#376: is the witness cheap one Witt cancellation down, at positive index 1?"""
import faulthandler
import sys
import time

from sage_extensions.all import *

faulthandler.dump_traceback_later(180, repeat=True)

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
    stamp(f"{label}: {str(value)[:120]}  [{(time.time() - begin):.1f} s]")
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
U = C("U")
e8_squared = C("E8") + C("E8")
d16_plus = C(_d16_plus_gram()).twist(-1)

complement_source = U + e8_squared
complement_target = U + d16_plus
stamp(f"complements: {complement_source.signature_pair()}, {complement_target.signature_pair()}")

timed("rank 18: is_isometric_to", lambda: complement_source.is_isometric_to(complement_target))
timed("rank 18: isometry_to", lambda: complement_source.isometry_to(complement_target))
stamp("done")
