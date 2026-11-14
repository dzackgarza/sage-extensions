"""Issue #276: does the existing glue_map already deliver the acceptance?"""
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


# --- specimen 1: the index-2 even overlattice of <2> perp <-2> inside U
U = Lattices(ZZ)("U")
labels = tuple(U.module_generating_set())
vectors = [U.module_generator(label) for label in labels]
candidate = next(
    vector
    for vector in (
        vectors[0] + vectors[1],
        vectors[0] - vectors[1],
        2 * vectors[0] + vectors[1],
    )
    if vector.q() == 2 and vector.is_primitive()
)
stage(f"candidate vector {candidate} of q {candidate.q()}, primitive {candidate.is_primitive()}")
first = U.subobject_on([candidate])
second = U.orthogonal_complement(first)
stage(f"S rank {first.module_rank()} D_S order {first.discriminant_group().cardinality()}; "
      f"R rank {second.module_rank()} D_R order {second.discriminant_group().cardinality()}")
glue = U.glue_map(first, second)
stage("glue_map built")
print("   type:", type(glue).__name__, flush=True)
print("   domain cardinality:", glue.domain().cardinality(), flush=True)
print("   codomain cardinality:", glue.codomain().cardinality(), flush=True)
print("   is_quadratic:", glue.is_quadratic(), flush=True)
for generator in glue.domain().module_generators():
    print("   q_S", glue.domain().q(generator), "->", glue.codomain().q(glue(generator)), flush=True)
print("   inverse ok:", all(glue.inverse()(glue(g)) == g for g in glue.domain().module_generators()), flush=True)
enlarged = (first + second)
stage(f"S + R order {enlarged}")

# --- specimen 2: the Enriques primitive extension
involution = Involutions.I_En
extension = involution.primitive_extension()
stage(f"extension of {extension.lattice}: index {extension.index()}")
witness = extension.glue()
stage("extension glue built")
print("   type:", type(witness).__name__, flush=True)
print("   domain cardinality:", witness.domain().cardinality(), flush=True)
print("   codomain cardinality:", witness.codomain().cardinality(), flush=True)
print("   is_quadratic:", witness.is_quadratic(), flush=True)
print("   invariant D order:", extension.invariant.discriminant_group().cardinality(), flush=True)
print("   complement D order:", extension.orthogonal_complement.discriminant_group().cardinality(), flush=True)
for generator in witness.domain().module_generators():
    print("   q_+", witness.domain().q(generator), "-> q_-(-1)", witness.codomain().q(witness(generator)), flush=True)
print("   inverse ok:", all(witness.inverse()(witness(g)) == g for g in witness.domain().module_generators()), flush=True)
print("DONE", flush=True)
