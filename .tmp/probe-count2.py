r"""#381: how many nested parameter enumerations the row runs, counted on the torsor's own class."""

import importlib.util
import sys
import time

sys.path.insert(0, "tests")
START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


from sage_extensions.all import Lattices, ZZ

lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
labels = tuple(lattice.module_generating_set())
line = lattice.primitive_isotropic_subobject(lattice.module_generator(labels[0]))
reduction = line.isotropic_reduction()
torsor = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())
owner = type(torsor)
log(f"torsor class: {owner}")
original = owner.integral_parameter_classes
counts = {"calls": 0, "seconds": 0.0}


def counting(self):
    counts["calls"] += 1
    start = time.perf_counter()
    value = original(self)
    counts["seconds"] += time.perf_counter() - start
    return value


owner.integral_parameter_classes = counting
log("wrapped")

spec = importlib.util.spec_from_file_location("rows", "tests/coble_gamma_co_2_incidence_rows.py")
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)

big = rows._lattice_by_name("Tco")
subgroup = rows._row_subgroup(big, "Otilde")
started = time.perf_counter()
outcome = rows.run_row(big, subgroup, "Otilde", 60, "auto")
log(f"outcome: {outcome.report()}  [{time.perf_counter() - started:.2f}s]")
log(f"integral_parameter_classes calls: {counts['calls']}, inside them {counts['seconds']:.2f}s")
log("done")
