r"""#603: does rationalizing an integral isometry make it a member of the action's stabilizer?"""

import time

from sage_extensions.all import Lattices, ZZ
from sage_extensions.categories.modules.pure.modules import ModulesOverIntegralDomains

START = time.perf_counter()


def stamp(label):
    print(f"[{time.perf_counter() - START:8.3f}s] {label}")


lattice = Lattices(ZZ)([[0, 2, 0], [2, 0, 0], [0, 0, 2]])
labels = tuple(lattice.module_generating_set())
vector = lattice.module_generator(labels[0])
subobject = lattice.primitive_isotropic_subobject(vector)
action = subobject.pointed_stabilizer_action()
group = action.rational_group()
stabilizer = action.stabilizer()

field_map = lattice.base_ring().fraction_field_map()
rational = lattice.base_change(field_map)
inclusion = ModulesOverIntegralDomains(lattice.base_ring())(lattice).generic_fibre_map()


def rationalized(isometry):
    return rational.Isom(rational)(
        lambda label: inclusion(isometry(lattice.module_generator(label))).underlying_element()
    )


reduction = subobject.isotropic_reduction()
kernel = tuple(reduction._pointwise_kernel_generators())
print("kernel generators:", len(kernel))
for index, element in enumerate(kernel):
    image = rationalized(element)
    print(f"  kernel [{index}]: integral parent {element.parent()}")
    print(f"             rational parent {image.parent()}")
    print(f"             in group: {image in group}   in stabilizer: {image in stabilizer}")

generators = tuple(group.group_generators())
for index, generator in enumerate(generators):
    print(f"  generator [{index}] in stabilizer: {generator in stabilizer}  in group: {generator in group}")

representation = action.finite_representation()
print("g_set:", representation.g_set())
print("selected point:", representation._selected_point())
for index, element in enumerate(kernel):
    image = rationalized(element)
    print(f"  kernel [{index}] permutation fixes the point: "
          f"{representation.permutation_representation()(image)(representation._selected_point()) == representation._selected_point()}")
print("finite stabilizer generators:", len(tuple(representation.finite_stabilizer().group_generators())))
stamp("done")
