r"""#603: is an integral lift of a Levi class outside the residue action's stabilizer?"""

import time

from sage_extensions.all import Lattices, ZZ
from sage_extensions.categories.modules.pure.modules import ModulesOverIntegralDomains

START = time.perf_counter()


def clock(label, function):
    start = time.perf_counter()
    value = function()
    print(f"  [{time.perf_counter() - start:8.3f}s] {label}")
    return value


LATTICE = [
    [0, 2, 0, 0, 0],
    [2, 0, 1, 0, 0],
    [0, 1, 0, 2, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, -2],
]

lattice = Lattices(ZZ)(LATTICE)
labels = tuple(lattice.module_generating_set())
vector = lattice.module_generator(labels[0])
subobject = lattice.primitive_isotropic_subobject(vector)
reduction = subobject.isotropic_reduction()
action = clock("pointed stabilizer action", subobject.pointed_stabilizer_action)
group = action.rational_group()
stabilizer = clock("stabilizer", action.stabilizer)
print("group generators:", len(tuple(group.group_generators())))

field_map = lattice.base_ring().fraction_field_map()
rational = lattice.base_change(field_map)
inclusion = ModulesOverIntegralDomains(lattice.base_ring())(lattice).generic_fibre_map()


def rational_image(isometry):
    return rational.Isom(rational)(
        lambda label: inclusion(isometry(lattice.module_generator(label))).underlying_element()
    )


kernel = tuple(reduction._pointwise_kernel_generators())
print("radical generators:", len(kernel))
for index, element in enumerate(kernel):
    print(f"  radical [{index}] crosses into the group: {rational_image(element) in group}"
          f"   in the stabilizer: {rational_image(element) in stabilizer}")

walk = clock("walk", reduction.pointwise_levi_image_generators)
print("walk words:", len(walk))
for index, element in enumerate(walk):
    crossed = rational_image(element)
    print(f"  walk [{index}] fixes v: {element(vector) == vector}"
          f"  in the group: {crossed in group}  in the stabilizer: {crossed in stabilizer}")
print(f"[{time.perf_counter() - START:8.3f}s] done")
