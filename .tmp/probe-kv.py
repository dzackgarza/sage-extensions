r"""#381: the reduction to lines of K_v, and what the library's line enumeration costs at rank ten."""

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

# the small specimen: K_v at U+U(2)+<-2>
small = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
labels = tuple(small.module_generating_set())
line = small.primitive_isotropic_subobject(small.module_generator(labels[0]))
quotient = line.isotropic_reduction().quotient_lattice()
log(f"small K_v: rank {quotient.module_rank()}, signature {quotient.signature()}, disc {quotient.discriminant()}")
signal.alarm(120)
try:
    representatives = quotient.Aut().isotropic_orbit_representatives(1)
    log(f"small K_v line orbits: {representatives.cardinality()}  [{time.perf_counter() - START:.2f}s]")
except Cap:
    log("small K_v line orbits: did not return inside 120 s")
finally:
    signal.alarm(0)

# the rank-eleven specimen
lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
enriques = NamedLattices.TEn
cusp = Sterk.selected_isotropic_vectors()["Sterk_5"]
coordinates = cusp.to_vector()
enriques_labels = tuple(enriques.module_generating_set())
given = {label: int(coordinates(label)) for label in enriques_labels}
coefficients = {"h": ZZ(given["e"])} if given["e"] else {}
for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
    if given[label]:
        coefficients[label] = ZZ(given[label])
vector = lattice.linear_combination(coefficients)
line = lattice.primitive_isotropic_subobject(vector)
quotient = line.isotropic_reduction().quotient_lattice()
log(f"T_Co K_v: rank {quotient.module_rank()}, signature {quotient.signature()}, disc {quotient.discriminant()}")
log(f"T_Co K_v even: {quotient.is_even()}")
signal.alarm(240)
try:
    representatives = quotient.Aut().isotropic_orbit_representatives(1)
    log(f"T_Co K_v line orbits: {representatives.cardinality()}  [{time.perf_counter() - START:.2f}s]")
except Cap:
    log("T_Co K_v line orbits: did not return inside 240 s")
finally:
    signal.alarm(0)
log("done")
