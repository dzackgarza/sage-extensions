r"""#603: which branch `029J`'s two cusps take, and what the walk costs there."""

import time

from sage_extensions.all import NamedLattices, ZZ

lattice = NamedLattices.TEn
labels = tuple(lattice.module_generating_set())
print("N:", lattice, "rank", lattice.module_rank(), "labels", labels)
for name, index in (("L_1", 0), ("L_2", 2)):
    start = time.perf_counter()
    vector = lattice.module_generator(labels[index])
    subobject = lattice.primitive_isotropic_subobject(vector)
    reduction = subobject.isotropic_reduction()
    quotient = reduction.quotient_lattice()
    generators = tuple(quotient.O().group_generators())
    print(f"===== {name} = Ze_{index + 1}: div {vector.div()}  K_I rank {quotient.module_rank()}  O(K_I) generators {len(generators)}  [{time.perf_counter() - start:7.2f}s]")
    start = time.perf_counter()
    splitting = reduction._reduction_lift_splitting()
    print(f"   splits along the lifts: {splitting is not None}  [{time.perf_counter() - start:7.2f}s]")
    start = time.perf_counter()
    walk = reduction.pointwise_levi_image_generators()
    print(f"   M_I generators: {len(walk)}  all fix v: {all(g(vector) == vector for g in walk)}  [{time.perf_counter() - start:7.2f}s]")
    start = time.perf_counter()
    kernel = reduction._pointwise_kernel_generators()
    print(f"   U_I generators: {len(kernel)}  [{time.perf_counter() - start:7.2f}s]")
    start = time.perf_counter()
    family = subobject.pointed_stabilizer_generators()
    print(f"   family: {len(family)}  all fix v: {all(g(vector) == vector for g in family)}  [{time.perf_counter() - start:7.2f}s]")
