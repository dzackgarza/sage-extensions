r"""#603: is an element of the residue action's rational group a member of it, and of its stabilizer?"""

import time

from sage_extensions.all import Lattices, ZZ

START = time.perf_counter()


def stamp(label):
    print(f"[{time.perf_counter() - START:8.3f}s] {label}")


lattice = Lattices(ZZ)([[0, 2, 0], [2, 0, 0], [0, 0, 2]])
labels = tuple(lattice.module_generating_set())
vector = lattice.module_generator(labels[0])
subobject = lattice.primitive_isotropic_subobject(vector)
action = subobject.pointed_stabilizer_action()
group = action.rational_group()
print("group:", group)
print("parent:", group.parent() if hasattr(group, "parent") else "n/a")
generators = tuple(group.group_generators())
print("generators:", len(generators))
for index, generator in enumerate(generators):
    print(f"  [{index}] parent: {generator.parent()}  in group: {generator in group}")
stamp("membership in the group")
stabilizer = action.stabilizer()
print("stabilizer:", stabilizer)
for index, generator in enumerate(generators):
    print(f"  [{index}] in stabilizer: {generator in stabilizer}")
stamp("membership in the stabilizer")

# an integral element: the identity, and a generator of the radical
identity = group.one()
print("identity in group:", identity in group, " identity in stabilizer:", identity in stabilizer)
reduction = subobject.isotropic_reduction()
kernel = tuple(reduction._pointwise_kernel_generators())
print("kernel generators:", len(kernel))
for index, element in enumerate(kernel):
    print(f"  kernel [{index}] in stabilizer: {element in stabilizer}")
stamp("kernel membership")
