r"""#381: are the admissible parameter classes of one line's torsor closed under addition?"""

import random
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


def check(name, lattice, vector, sample):
    log(f"===== {name} =====")
    line = lattice.primitive_isotropic_subobject(vector)
    reduction = line.isotropic_reduction()
    identity = reduction.Isom(reduction).identity()
    torsor = reduction.rational_lifts(reduction, identity)
    start = time.perf_counter()
    classes = torsor.integral_parameter_classes()
    log(f"  classes: {classes.cardinality()}  [{time.perf_counter() - start:.2f}s]")
    elements = list(classes)
    log(f"  iterated {len(elements)}")
    one = elements[0]
    log(f"  element type: {type(one).__name__}; parent: {one.parent()}")
    zero = one.parent().zero()
    log(f"  zero in classes: {zero in classes}")
    signal.alarm(240)
    try:
        picked = random.Random(0).sample(elements, min(sample, len(elements)))
        failures = 0
        tested = 0
        start = time.perf_counter()
        for left in picked:
            for right in elements:
                tested += 1
                if (left + right) not in classes:
                    failures += 1
                    if failures < 3:
                        log(f"  FAILURE: {left} + {right} not admissible")
        log(f"  closure over {len(picked)} x {len(elements)} = {tested} sums: {failures} failures  [{time.perf_counter() - start:.2f}s]")
    except Cap:
        log("  closure check did not finish inside 240 s")
    finally:
        signal.alarm(0)


small = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
check("U+U(2)+<-2>", small, small.module_generator(tuple(small.module_generating_set())[0]), 8)

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
check("T_Co cusp 5", lattice, lattice.linear_combination(coefficients), 8)
log("done")
