"""#298 probe B: what the existing isometry Mor decides and constructs on the two test pairs.

Measures, for each pair: the emptiness decision, the witness, the column matrix of the witness, and
the Gram equation in both orientations.  Then the same on a non-isometric pair.
"""
import time

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage.matrix.constructor import matrix  # noqa: E402
from sage.rings.integer_ring import ZZ as SageZZ  # noqa: E402
from sage.rings.rational_field import QQ  # noqa: E402
from sage_extensions.all import Lattices, NamedLattices, ZZ  # noqa: E402
from sage_extensions.tensors.tensor import _engine_component_matrix  # noqa: E402


def gram(lattice):
    return _engine_component_matrix(lattice.gram_tensor()).change_ring(QQ)


def column_matrix(morphism):
    domain = morphism.domain()
    codomain = morphism.codomain()
    labels = tuple(codomain.module_generating_set())
    columns = []
    for generator in domain.module_generators():
        image = morphism(generator)
        given = image.to_vector()
        columns.append([int(given(label)) for label in labels])
    return matrix(SageZZ, [[column[row] for column in columns] for row in range(len(labels))])


U = NamedLattices.U
minus_one = Lattices(ZZ)([[-1]])
pairs = {
    "U + <-1> vs I_(1,2)": (U + minus_one, Lattices.IPQ(1, 2)),
    "U + U + <-1>^7 vs U + I_(1,8)": (
        U + U + Lattices.IPQ(0, 7),
        U + Lattices.IPQ(1, 8),
    ),
}
for name, (source, target) in pairs.items():
    print("=" * 20, name)
    for lattice in (source, target):
        print("  rank", int(lattice.module_rank()), "det", lattice.determinant(),
              "signature", tuple(map(int, lattice.signature_pair())),
              "even", lattice.is_even())
    mor = source.Isom(target)
    start = time.time()
    empty = mor.is_empty()
    stamp(f"  is_empty -> {empty} in {round(time.time() - start, 2)}s")
    start = time.time()
    witness = mor.an_element()
    stamp(f"  an_element in {round(time.time() - start, 2)}s")
    M = column_matrix(witness)
    print("  column matrix", M)
    print("  M^T G_target M == G_source:", M.transpose() * gram(target) * M == gram(source))
    print("  M^-T G_source M^-1 == G_target:",
          M.inverse().transpose() * gram(source) * M.inverse() == gram(target))
    print("  det", M.det(), "integral inverse", all(
        entry.denominator() == 1 for entry in M.inverse().list()))
    print("  is_isometric_to source->target", source.is_isometric_to(target),
          "target->source", target.is_isometric_to(source))

print("=" * 20, "non-isometric control")
left = Lattices(ZZ)([[1]])
right = Lattices(ZZ)([[-1]])
start = time.time()
print("  is_isometric_to", left.is_isometric_to(right), "in", round(time.time() - start, 2), "s")
stamp("done")
