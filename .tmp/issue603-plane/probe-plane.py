r"""#603: the radical of the isotropic plane at Sterk's P_2 of T_En, measured."""

import time

from sage_extensions.all import Lattices, NamedLattices, ZZ
from sage.matrix.constructor import matrix as engine_matrix
from sage.rings.integer_ring import ZZ as SageZZ

START = time.perf_counter()


def clock(label, function):
    start = time.perf_counter()
    value = function()
    print(f"  [{time.perf_counter() - start:8.3f}s] {label}")
    return value


def second_representative(lattice):
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


lattice = NamedLattices.TEn
plane = second_representative(lattice)
print("T_En:", lattice.module_rank(), "signature", lattice.signature(), "even:", lattice.is_even())
print("P_2 plane rank:", plane.module_rank(), "perpendicular rank:", plane.isotropic_perpendicular().module_rank())
print("K = I^perp/I rank:", plane.isotropic_reduction().quotient_lattice().module_rank()
      if hasattr(plane, "isotropic_reduction") else "n/a")

modulus = clock("modulus", plane.unipotent_parameter_modulus)
print("           modulus:", modulus)
counts = clock("class counts (modulus, classes, admissible)", plane.unipotent_parameter_class_counts)
print("           counts:", counts)
basis = clock("parameter lattice", lambda: tuple(plane.unipotent_parameter_lattice()))
print("           basis vectors:", len(basis))
matrix_basis = engine_matrix(SageZZ, [list(row) for row in basis])
print("           shape:", matrix_basis.nrows(), "x", matrix_basis.ncols(),
      " rank:", int(matrix_basis.rank()), " determinant:", int(matrix_basis.determinant()))
radical = clock("radical generators", lambda: tuple(plane.unipotent_radical_generators()))
print("           radical family:", len(radical))
transvections = tuple(
    transvection
    for transvection in plane.parabolic_transvection_generators()
    if plane._fixes_isotropic_pointwise(transvection)
    and plane.acts_trivially_on_isotropic_reduction(transvection)
)
print("           transvections in the radical:", len(transvections))
rank = clock("translation rank of the transvections", lambda: plane.unipotent_translation_rank(transvections))
print("           translation rank:", rank)
rank_all = clock("translation rank of the family", lambda: plane.unipotent_translation_rank(radical))
print("           translation rank of the family:", rank_all)
index = clock("radical index", plane.unipotent_radical_index)
print("           radical index:", index)
print(f"[{time.perf_counter() - START:8.3f}s] done")
