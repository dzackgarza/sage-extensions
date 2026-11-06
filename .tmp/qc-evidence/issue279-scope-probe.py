"""Issue #279: what the consumer specimen gives, and what the covering route costs."""
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


T = NamedLattices.TEn
C = NamedLattices.Tco
stage(f"T = T_En: rank {T.module_rank()}, signature {T.signature()}, even {T.is_even()}")
stage(f"C = T_Co: rank {C.module_rank()}, signature {C.signature()}, even {C.is_even()}")
print("|A_T| =", T.discriminant_group().cardinality(), flush=True)
print("|A_C| =", C.discriminant_group().cardinality(), flush=True)

embedding = Embeddings.TCo_into_TEn
stage(f"the catalogue embedding: rank {embedding.domain().module_rank()} -> {embedding.codomain().module_rank()}")
print("primitive:", embedding.is_primitive(), flush=True)
complement = embedding.orthogonal_complement()
stage("orthogonal complement built")
complement_lattice = complement.domain() if hasattr(complement, "domain") else complement
print("complement type:", type(complement_lattice).__name__, flush=True)
print("complement rank:", complement_lattice.module_rank(), flush=True)
print("complement signature:", complement_lattice.signature(), flush=True)
generator = complement_lattice.module_generators()[0]
print("delta:", generator, "| square:", generator.q(), "| primitive:", generator.is_primitive(), flush=True)
print("delta perp is C:", T.orthogonal_complement(complement).domain().is_isometric(C) if hasattr(complement, "domain") else "?", flush=True)

# the index of <delta> + C inside T
summands = complement_lattice + embedding.domain()
print("rank of <delta> + C:", summands.module_rank(), flush=True)
stage(f"generator of the overlattice built")

# the covering-class route the issue names as the finite object
began = time.monotonic()
try:
    covering = T.covering_discriminant_classes(ZZ(-2))
    stage(f"covering_discriminant_classes(-2): {covering.cardinality()} classes in {time.monotonic() - began:.1f}s")
    for element in covering.elements():
        print("   class", element, "q", element.q(), "order", element.additive_order(), flush=True)
except Exception as error:
    print("covering RAISED", type(error).__name__, str(error)[:200], flush=True)

# is the enumerated fibre finite here?
began = time.monotonic()
try:
    fibre = T.vectors_of_square_and_divisibility(ZZ(-2), ZZ(1))
    stage(f"vectors_of_square_and_divisibility(-2, 1): {fibre} in {time.monotonic() - began:.1f}s")
except Exception as error:
    print("fibre RAISED", type(error).__name__, str(error)[:300], flush=True)
print("DONE", flush=True)
