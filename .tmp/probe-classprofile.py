r"""#381: where integral_parameter_classes spends its time now, at T_Co."""

import cProfile
import io
import pstats
import time

from sage_extensions.all import NamedLattices, Sterk, ZZ

START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


lattice = NamedLattices.Tco
enriques = NamedLattices.TEn
cusp = Sterk.selected_isotropic_vectors()["Sterk_5"]
coordinates = cusp.to_vector()
given = {label: int(coordinates(label)) for label in tuple(enriques.module_generating_set())}
coefficients = {"h": ZZ(given["e"])} if given["e"] else {}
for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
    if given[label]:
        coefficients[label] = ZZ(given[label])
line = lattice.primitive_isotropic_subobject(lattice.linear_combination(coefficients))
reduction = line.isotropic_reduction()
torsor = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())

start = time.perf_counter()
classes = torsor.integral_parameter_classes()
log(f"integral_parameter_classes: [{time.perf_counter() - start:.2f}s]")

profile = cProfile.Profile()
profile.enable()
torsor2 = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())
torsor2._integral_parameter_cosets()
profile.disable()
stream = io.StringIO()
pstats.Stats(profile, stream=stream).sort_stats("tottime").print_stats(14)
print(stream.getvalue())
log("done")
