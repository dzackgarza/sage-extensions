r"""#603: is the group's element constructor the crossing the record says does not exist?"""

import time

from sage_extensions.all import Lattices, ZZ
from sage_extensions.categories.modules.pure.modules import ModulesOverIntegralDomains

START = time.perf_counter()
lattice = Lattices(ZZ)([[0, 2, 0], [2, 0, 0], [0, 0, 2]])
labels = tuple(lattice.module_generating_set())
vector = lattice.module_generator(labels[0])
subobject = lattice.primitive_isotropic_subobject(vector)
action = subobject.pointed_stabilizer_action()
group = action.rational_group()
stabilizer = action.stabilizer()
reduction = subobject.isotropic_reduction()
kernel = tuple(reduction._pointwise_kernel_generators())

field_map = lattice.base_ring().fraction_field_map()
rational = lattice.base_change(field_map)
inclusion = ModulesOverIntegralDomains(lattice.base_ring())(lattice).generic_fibre_map()


def rationalized(isometry):
    return rational.Isom(rational)(
        lambda label: inclusion(isometry(lattice.module_generator(label))).underlying_element()
    )


for index, element in enumerate(kernel):
    crossed = group(element)
    print(f"kernel [{index}]: crossed equals the rationalized element: {crossed == rationalized(element)}")
    print(f"   crossed in group: {crossed in group}   in stabilizer: {crossed in stabilizer}")
    print(f"   crossed fixes L pointwise: {all(crossed(lattice.module_generator(label)) == element(lattice.module_generator(label)) for label in labels)}")

# a group generator that should NOT be in the stabilizer: the sheared rational lift
group_generators = tuple(group.group_generators())
for index, generator in enumerate(group_generators):
    print(f"generator [{index}] in stabilizer: {generator in stabilizer}")
print(f"[{time.perf_counter() - START:8.3f}s] done")
