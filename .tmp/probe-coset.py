r"""#381: the transporters of one isotropic plane to another are a coset of its stabilizer."""

import time

from sage_extensions.all import Lattices, ZZ

START = time.perf_counter()


def clock(label, function):
    start = time.perf_counter()
    value = function()
    print(f"  [{time.perf_counter() - start:8.3f}s] {label}")
    return value


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
print("L:", lattice.module_rank(), lattice.signature(), "even:", lattice.is_even())
labels = tuple(lattice.module_generating_set())
print("labels:", labels)
generators = [lattice.module_generator(label) for label in labels]
e, f, e2, f2, g = generators
print("pairings: b(e,f)=", lattice.b(e, f), " b(e2,f2)=", lattice.b(e2, f2), " q(g)=", lattice.q(g))

plane_p = lattice.primitive_isotropic_subobject(e, e2)
plane_q = lattice.primitive_isotropic_subobject(e, f2)
print("P rank:", plane_p.module_rank(), " Q rank:", plane_q.module_rank())

group = lattice.Aut()
witness = clock("transporter witness P -> Q", lambda: group.isotropic_equivalence_witness(plane_p, plane_q))
print("  witness is None:", witness is None)
if witness is not None:
    basis_p = tuple(plane_p.inclusion()(plane_p.module_generator(label)) for label in plane_p.module_generating_set())
    basis_q = tuple(plane_q.inclusion()(plane_q.module_generator(label)) for label in plane_q.module_generating_set())
    print("  witness carries P into Q:", all(witness(p) in plane_q for p in basis_p))
    radical = clock("radical of P", lambda: tuple(plane_p.unipotent_radical_generators()))
    print("  radical generators:", len(radical))
    fixes = all(s(p) == p for s in radical for p in basis_p)
    print("  radical fixes P pointwise:", fixes)
    composed = [witness * s for s in radical]
    print("  every composed map carries P into Q:", all(all(m(p) in plane_q for p in basis_p) for m in composed))
    print("  some composed map moves Q:", any(any(m(q) != q for q in basis_q) for m in composed))
print(f"[{time.perf_counter() - START:8.3f}s] done")
