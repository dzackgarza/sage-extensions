"""#376: signatures of the two lattices and their two Eichler models, from the Gram matrices."""
import time

from sage_extensions.all import *


def _d16_plus_gram():
    def entry(i, j):
        if i == j:
            return 4 if i in (0, 15) else 2
        if {i, j} == {0, 1}:
            return -2
        if {i, j} == {0, 15}:
            return 1
        if 1 <= i <= 14 and 1 <= j <= 14 and abs(i - j) == 1:
            return -1
        return 0

    return [[entry(i, j) for j in range(16)] for i in range(16)]


def _ints(lattice):
    rank = int(lattice.module_rank())
    gram = lattice.gram_tensor()
    return [[int(gram[i, j]) for j in range(rank)] for i in range(rank)]


def _eigen_inertia(gram):
    import numpy as np

    matrix = np.array(gram, dtype=float)
    values = np.linalg.eigvalsh(matrix)
    positive = int(sum(1 for v in values if v > 1e-6))
    negative = int(sum(1 for v in values if v < -1e-6))
    return (positive, negative, len(values) - positive - negative), (float(values.min()), float(values.max()))


def report(name, lattice):
    gram = _ints(lattice)
    sign = lattice.signature_pair()
    inertia, extent = _eigen_inertia(gram)
    print(f"{name}")
    print(f"    signature_pair() = ({sign.first()}, {sign.second()})")
    print(f"    gram eigenvalues: (t+, t-, t0) = {inertia}, min {extent[0]:.4f} max {extent[1]:.4f}")
    print(
        f"    rank {lattice.module_rank()}  det {lattice.determinant()}  "
        f"even {lattice.is_even()}  unimodular {lattice.is_unimodular()}"
    )
    return gram


C = Lattices(ZZ)

print("=== the pieces ===")
e8 = C("E8")
print("E8 Gram, as the catalogue spells it:")
for row in _ints(e8):
    print("   ", row)
report("E8  [catalogue name]", e8)
report("E8.twist(-1)", e8.twist(-1))
d16_gram = C(_d16_plus_gram())
print("D16+ Gram, as the test spells it:")
for row in _ints(d16_gram):
    print("   ", row)
report("D16+  [the test's _d16_plus_gram()]", d16_gram)
report("D16+.twist(-1)", d16_gram.twist(-1))

print()
print("=== the test's two lattices, as written ===")
e8_squared = C("E8").twist(-1) + C("E8").twist(-1)
d16_plus = C(_d16_plus_gram()).twist(-1)
report("e8_squared = E8.twist(-1) + E8.twist(-1)", e8_squared)
report("d16_plus = _d16_plus_gram().twist(-1)", d16_plus)

print()
print("=== the two Eichler models ===")
source = e8_squared.two_u_eichler_model().lattice()
target = d16_plus.two_u_eichler_model().lattice()
report("source = e8_squared.two_u_eichler_model().lattice()", source)
report("target = d16_plus.two_u_eichler_model().lattice()", target)
for label, model in (("source", source), ("target", target)):
    pairs = [
        (factor.signature_pair().first(), factor.signature_pair().second())
        for factor in model.biproduct_factors()
    ]
    print(f"{label} biproduct factor signatures: {pairs}")

print()
print("=== the decisions, as the test asks them today ===")
for label, left, right in (
    ("e8_squared vs d16_plus (complements)", e8_squared, d16_plus),
    ("source vs target", source, target),
):
    start = time.time()
    try:
        answer = left.is_isometric_to(right)
    except Exception as error:  # noqa: BLE001 - report the shape of the failure
        answer = f"{type(error).__name__}: {error}"
    print(f"{label}: is_isometric_to -> {answer}  [{time.time() - start:.1f} s]")
