r"""#603: the pointed family at the nonreflective `K_I`, with the two-factor branch."""

import time

from sage_extensions.all import Lattices, NamedLattices, ZZ

START = time.perf_counter()


def clock(label, function):
    start = time.perf_counter()
    value = function()
    print(f"  [{time.perf_counter() - start:8.3f}s] {label}")
    return value


lattice = Lattices(ZZ)("U") + NamedLattices.BogachevKolpakovNonReflective
labels = tuple(lattice.module_generating_set())
vector = lattice.module_generator(labels[0])
subobject = lattice.primitive_isotropic_subobject(vector)
reduction = subobject.isotropic_reduction()
quotient = reduction.quotient_lattice()
print("L:", lattice.module_rank(), "signature", lattice.signature(), "even:", lattice.is_even(),
      "disc:", lattice.discriminant())
print("K_I:", quotient.module_rank(), "signature", quotient.signature(), "disc:", quotient.discriminant())
print("marked div:", vector.div(), "primitive:", vector.is_primitive(), "q:", vector.q())

generators = clock("O(K_I) generators", lambda: tuple(quotient.O().group_generators()))
print(f"           {len(generators)} generators")
splitting = clock("reduction splitting", reduction._reduction_lift_splitting)
print(f"           splits along the lifts: {splitting is not None}")
walk = clock("coset walk", reduction.pointwise_levi_image_generators)
print(f"           M_I generators: {len(walk)}  all fix v: {all(g(vector) == vector for g in walk)}")
kernel = clock("radical generators", reduction._pointwise_kernel_generators)
print(f"           U_I generators: {len(kernel)}")
family = clock("owned pointed family", subobject.pointed_stabilizer_generators)
print(f"           family: {len(family)}  all fix v: {all(g(vector) == vector for g in family)}")
public = clock("public pointed family", lambda: tuple(lattice.Aut().stabilizer(vector).group_generators()))
print(f"           public family: {len(public)}  all fix v: {all(g(vector) == vector for g in public)}")
print(f"[{time.perf_counter() - START:8.3f}s] done")
