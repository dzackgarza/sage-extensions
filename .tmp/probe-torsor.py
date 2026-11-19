r"""#381: what one line's lifting torsor costs at T_Co."""

import signal
import time

from sage_extensions.all import Lattices, NamedLattices, Sterk, ZZ

START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


class Cap(Exception):
    pass


def cap(signum, frame):
    raise Cap()


signal.signal(signal.SIGALRM, cap)


def specimen(name, lattice, vector):
    log(f"===== {name}: rank {lattice.module_rank()}, v div {vector.div()} =====")
    line = lattice.primitive_isotropic_subobject(vector)
    reduction = line.isotropic_reduction()
    identity = reduction.Isom(reduction).identity()
    torsor = reduction.rational_lifts(reduction, identity)
    signal.alarm(240)
    try:
        start = time.perf_counter()
        classes = torsor.integral_parameter_classes()
        log(f"  parameter classes: {classes.cardinality()}  [{time.perf_counter() - start:.2f}s]")
        start = time.perf_counter()
        members = torsor.integral_members()
        log(f"  integral members built  [{time.perf_counter() - start:.2f}s]")
    except Cap:
        log("  did not return inside 240 s")
    finally:
        signal.alarm(0)


small = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
specimen("U+U(2)+<-2>", small, small.module_generator(tuple(small.module_generating_set())[0]))

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
enriques = NamedLattices.TEn
cusp = Sterk.selected_isotropic_vectors()["Sterk_5"]
coordinates = cusp.to_vector()
given = {label: int(coordinates(label)) for label in tuple(enriques.module_generating_set())}
coefficients = {"h": ZZ(given["e"])} if given["e"] else {}
for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
    if given[label]:
        coefficients[label] = ZZ(given[label])
vector = lattice.linear_combination(coefficients)
specimen("T_Co cusp 5", lattice, vector)
log("done")
