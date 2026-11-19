r"""#381: which route supplies the planes through a line at T_Co, and where it declines."""

import time

from sage_extensions.all import NamedLattices, Sterk, ZZ
from sage_extensions.categories.isotropic_orbits import (
    _chamber_planes_through_line,
    _hyperbolic_completion,
)

START = time.perf_counter()


def clock(label, function):
    start = time.perf_counter()
    value = function()
    print(f"  [{time.perf_counter() - start:8.3f}s] {label}")
    return value


for name, lattice in (("U+U(2)+<-2>", None), ("T_Co", NamedLattices.Tco)):
    if lattice is None:
        from sage_extensions.all import Lattices
        lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
    print(f"===== {name}: rank {lattice.module_rank()} =====")
    if name == "T_Co":
        enriques = NamedLattices.TEn
        cusp = Sterk.selected_isotropic_vectors()["Sterk_5"]
        coordinates = cusp.to_vector()
        labels = tuple(enriques.module_generating_set())
        given = {label: int(coordinates(label)) for label in labels}
        coefficients = {"h": ZZ(given["e"])} if given["e"] else {}
        for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
            if given[label]:
                coefficients[label] = ZZ(given[label])
        vector = lattice.linear_combination(coefficients)
    else:
        labels = tuple(lattice.module_generating_set())
        vector = lattice.module_generator(labels[0])
    line = lattice.primitive_isotropic_subobject(vector)
    print(f"  line div {vector.div()}")
    completion = clock("hyperbolic completion", lambda: _hyperbolic_completion(lattice, line))
    print(f"  completion certified: {completion is not None}")
    planes = clock("chamber route", lambda: _chamber_planes_through_line(lattice, line, completion))
    print(f"  chamber route answered: {planes is not None}" + (f"  planes {len(tuple(planes))}" if planes is not None else ""))
