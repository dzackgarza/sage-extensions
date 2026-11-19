r"""#603: the coset walk's cost after the coordinate-level correction search."""

import time

from sage_extensions.all import Lattices, NamedLattices, Sterk, ZZ

START = time.perf_counter()


def clock(label, function):
    start = time.perf_counter()
    value = function()
    print(f"  [{time.perf_counter() - start:8.3f}s] {label}")
    return value


def report(name, lattice, vector):
    print(f"===== {name}: rank {lattice.module_rank()} div {vector.div()} =====")
    subobject = lattice.primitive_isotropic_subobject(vector)
    reduction = subobject.isotropic_reduction()
    quotient = reduction.quotient_lattice()
    print(f"  K_I rank {quotient.module_rank()}  O(K_I) generators {len(tuple(quotient.O().group_generators()))}")
    splitting = clock("reduction splitting", reduction._reduction_lift_splitting)
    print(f"           splits along the lifts: {splitting is not None}")
    walk = clock("coset walk", reduction.pointwise_levi_image_generators)
    print(f"           M_I generators: {len(walk)}  all fix v: {all(g(vector) == vector for g in walk)}")
    kernel = clock("radical generators", reduction._pointwise_kernel_generators)
    print(f"           U_I generators: {len(kernel)}")
    owned = clock("owned pointed family", subobject.pointed_stabilizer_generators)
    print(f"           owned family: {len(owned)}  all fix v: {all(g(vector) == vector for g in owned)}")
    public = clock("public pointed family", lambda: tuple(lattice.Aut().stabilizer(vector).group_generators()))
    print(f"           public family: {len(public)}  all fix v: {all(g(vector) == vector for g in public)}")


report("U(2)+<2>", Lattices(ZZ)([[0, 2, 0], [2, 0, 0], [0, 0, 2]]), Lattices(ZZ)([[0, 2, 0], [2, 0, 0], [0, 0, 2]]).module_generator("e0") if False else None) if False else None

for name, gram in (
    ("U(2)+<2>", [[0, 2, 0], [2, 0, 0], [0, 0, 2]]),
    ("U(2)+<3>", [[0, 2, 0], [2, 0, 0], [0, 0, 3]]),
    ("U(3)+<3>", [[0, 3, 0], [3, 0, 0], [0, 0, 3]]),
    ("U(2)+<2>+<2>", [[0, 2, 0, 0], [2, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, 2]]),
    (
        "rank five",
        [
            [0, 2, 0, 0, 0],
            [2, 0, 1, 0, 0],
            [0, 1, 0, 2, 0],
            [0, 0, 2, 0, 0],
            [0, 0, 0, 0, -2],
        ],
    ),
):
    lattice = Lattices(ZZ)(gram)
    labels = tuple(lattice.module_generating_set())
    report(name, lattice, lattice.module_generator(labels[0]))

enriques = NamedLattices.TEn
lattice = NamedLattices.Tco
cusp = Sterk.selected_isotropic_vectors()["Sterk_5"]
coordinates = cusp.to_vector()
labels = tuple(enriques.module_generating_set())
given = {label: int(coordinates(label)) for label in labels}
coefficients = {"h": ZZ(given["e"])} if given["e"] else {}
for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
    if given[label]:
        coefficients[label] = ZZ(given[label])
vector = lattice.linear_combination(coefficients)
report("T_Co cusp 5", lattice, vector)

print(f"[{time.perf_counter() - START:8.3f}s] done")
