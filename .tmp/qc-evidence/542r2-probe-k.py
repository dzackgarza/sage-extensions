"""#542 round 2: a copy of the structure sheaf as a second representative."""
import copy
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        v = f()
        print(f"{label}: {v!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


ring = QQ["x"]
scheme = ring.affine_spectrum()
sheaf = scheme.structure_sheaf()
clone = copy.copy(sheaf)
show("clone is sheaf", lambda: clone is sheaf)
show("clone == sheaf", lambda: clone == sheaf)
classes = scheme.picard_group().underlying_set()
first = classes(sheaf)
show("second", lambda: classes(clone))
second = classes(clone)
show("reps distinct", lambda: first.representative() is second.representative())
show("hash first", lambda: hash(first))
show("hash second", lambda: hash(second))
show("ask(first == second)", lambda: ask(first == second))
