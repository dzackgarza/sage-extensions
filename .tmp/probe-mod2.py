r"""#603: does any mod-two image separate the radical from the identity?

Prints, for each generator of the pointed family, the matrix of its action on
`L/2L`, and whether that matrix is the identity.
"""

from sage_extensions.all import Lattices, ZZ

for name, gram in (
    ("U(2)+<2>", [[0, 2, 0], [2, 0, 0], [0, 0, 2]]),
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
    print(f"===== {name} =====")
    lattice = Lattices(ZZ)(gram)
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    subobject = lattice.primitive_isotropic_subobject(vector)
    reduction = subobject.isotropic_reduction()
    family = tuple(subobject.pointed_stabilizer_generators())
    radical = tuple(reduction._pointwise_kernel_generators())
    print(f"  family {len(family)}, radical {len(radical)}")
    for index, generator in enumerate(family):
        columns = []
        for label in labels:
            values = generator(lattice.module_generator(label)).to_vector()
            columns.append([int(values(other)) % 2 for other in labels])
        identity = [[1 if row == position else 0 for position in range(len(labels))] for row in range(len(labels))]
        print(f"   [{index:2}] fixes v: {generator(vector) == vector}  trivial mod 2: {columns == identity}")
    print("  radical elements among the family:")
    for index, generator in enumerate(radical):
        columns = []
        for label in labels:
            values = generator(lattice.module_generator(label)).to_vector()
            columns.append([int(values(other)) % 2 for other in labels])
        identity = [[1 if row == position else 0 for position in range(len(labels))] for row in range(len(labels))]
        print(f"   radical [{index}] trivial mod 2: {columns == identity}")
