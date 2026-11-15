"""#541: public datum identities and per-call costs on a lattice and one plane."""
"""Public datum identities and per-call costs on a lattice and one plane (#541)."""
import gc
import time

from sage_extensions.all import *

L = Lattices(ZZ)("U") + Lattices(ZZ)("U")
labels = tuple(L.module_generating_set())
plane = L.primitive_isotropic_subobject(
    L.module_generator(labels[1]), L.module_generator(labels[2])
)
family = plane.module_generating_set()


def show(label, first, second):
    print(f"{label:52s} one object: {first is second}", flush=True)


show("L.gram_matrix()", L.gram_matrix(), L.gram_matrix())
show("plane.embedded_module_generators()", plane.embedded_module_generators(), plane.embedded_module_generators())
show("L.module_generating_set()", L.module_generating_set(), L.module_generating_set())
show("plane.inclusion()", plane.inclusion(), plane.inclusion())
show("plane.inclusion().cokernel()", plane.inclusion().cokernel(), plane.inclusion().cokernel())
show("L.subobject_on(family)", L.subobject_on(family), L.subobject_on(family))
show("L.module_category().Mor(plane, L)", L.module_category().Mor(plane, L), L.module_category().Mor(plane, L))


def cost(label, call, rounds=300):
    gc.disable()
    start = time.perf_counter()
    for _ in range(rounds):
        call()
    elapsed = time.perf_counter() - start
    gc.enable()
    print(f"{label:52s} {1e6 * elapsed / rounds:8.2f} us a call", flush=True)


cost("plane.embedded_module_generators()", plane.embedded_module_generators)
cost("L.gram_matrix()", L.gram_matrix)
cost("plane.inclusion().cokernel()", plane.inclusion().cokernel)
cost("L.subobject_on(family)", lambda: L.subobject_on(family))
cost("L.b(vector, vector)", lambda: L.b(L.module_generator(labels[1]), L.module_generator(labels[1])))

# Which families the two _span_basis_elements calls of one transport see.
import sage_extensions.categories.lattices as lattices_module

seen = []
original = lattices_module._span_basis_elements


def counting(module, generating):
    seen.append(
        tuple(
            tuple(int(vector.to_vector()(label)) for label in module.module_generating_set())
            for vector in tuple(generating)
        )
    )
    return original(module, generating)


lattices_module._span_basis_elements = counting
transporter = L.Isom(L)(lambda label: -L.module_generator(label))
source = L.primitive_isotropic_subobject(
    L.module_generator(labels[0]), L.module_generator(labels[2])
)
transporter.transport_isotropic_object(source)
print(f"\n_span_basis_elements calls in one transport: {len(seen)}", flush=True)
for entry in seen:
    print(f"  {entry}", flush=True)
print(f"  all families equal: {len(set(seen)) == 1}", flush=True)
