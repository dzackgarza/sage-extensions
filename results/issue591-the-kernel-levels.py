"""The levels of the T_Co congruence kernel: the certified family, its level-4 span, level 8.

Not a test.  This script is the probe behind `results/issue591-the-coble-kernel-acceptance.md`,
sections 6 and 7, so that every number quoted there can be regenerated:

    ~/sage-image/run.sh -w /work -b <tree>:/work -b ~/ai-review-ci:/ci -- \
      /bin/sh -c 'export HOME=/root; export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work;
                  /sage/.venv/bin/python -u /work/results/issue591-the-kernel-levels.py'

Part 1 builds a family of elements of the discriminant kernel of `T_Co` and checks each one
twice: exactly an isometry of the lattice (its column matrix `M` satisfies `M^T G M = G` on the
lattice's own Gram matrix, and the coordinate vector of every image rebuilds the image), and
exactly in the kernel (every entry of `M - 1` is even, which for `|A_L| = 2^rank` is the same as a
trivial action on `A_L = L^#/L`), and the library's own `discriminant_morphism()` is the identity.

Part 2 measures, at ranks three, four and five, the image of the whole kernel and of that family in
the level-four quotient `Gamma(2)/Gamma(4)`.  The quotient is elementary abelian there -- with
`M = 1 + 2A` one has `(1+2A)(1+2B) = 1 + 2(A+B) (mod 4)` -- so a subgroup's image is an `F_2`
subspace and its dimension is what is printed.  The whole kernel's image is measured through an
exact generating set (Schreier's family over `O(A_L)`, available exactly at these sizes), the
family's image through the part-1 construction.

Part 3 compares the two subgroups those same two families generate inside `O(L/8L)`, at rank three,
by the action on the 512 vectors of `L/8L`.

Nothing here is stored as a generating set: part 1 certifies membership in the kernel, and parts 2
and 3 measure a quotient, which cannot prove generation.
"""

import sys
import time

from sage.all import GF, ZZ, matrix
from sage.libs.gap.libgap import libgap

from sage_extensions.all import Lattices, NamedLattices

START = time.time()


def step(name):
    print(f"[{time.time() - START:8.2f}s] {name}", flush=True)


def gram(lattice):
    """The lattice's Gram matrix on its selected generators, read through the pairing."""
    labels = tuple(lattice.module_generating_set())
    generators = [lattice.module_generator(label) for label in labels]
    return (
        labels,
        generators,
        matrix(ZZ, [[int(generators[i].b(generators[j])) for j in range(len(generators))]
                    for i in range(len(generators))]),
    )


def column_matrix(lattice, labels, element):
    """The matrix whose j-th column is the image of the j-th generator, checked exactly."""
    columns = []
    for label in labels:
        image = element(lattice.module_generator(label))
        coefficients = [int(image.to_vector()(row)) for row in labels]
        rebuilt = sum((coefficients[i] * lattice.module_generator(row) for i, row in enumerate(labels)),
                      lattice.zero())
        assert rebuilt == image, f"the coordinate vector does not rebuild the image of {label}"
        columns.append(coefficients)
    return matrix(ZZ, columns).transpose()


def is_identity_mod(matrix_, size, modulus):
    return all(int(matrix_[i][j] - (1 if i == j else 0)) % modulus == 0
               for i in range(size) for j in range(size))


def level_four_span(matrices, size):
    """The dimension over F_2 of the images of these elements in Gamma(2)/Gamma(4)."""
    rows = []
    for M in matrices:
        A = ((M - matrix(ZZ, size, size, lambda i, j: 1 if i == j else 0)) / 2).change_ring(GF(2))
        rows.extend([[A[i][j] for j in range(size)] for i in range(size)])
    return matrix(GF(2), rows).rank() if rows else 0


def level_four_available(size, gram_matrix):
    """The dimension of the space a level-four class of an *exact* isometry must land in.

    `M = 1 + 2A` is an isometry of `G` exactly when `A^T G + 2 A^T G A + G A = 0`; writing
    `G = 2H` and reducing modulo two leaves `A^T H + H A = 0`.
    """
    H = (gram_matrix / 2).change_ring(GF(2))
    equations = []
    for a in range(size):
        for b in range(size):
            row = [0] * (size * size)
            for i in range(size):
                if H[i][b]:
                    row[i * size + a] ^= 1
            for j in range(size):
                if H[a][j]:
                    row[j * size + b] ^= 1
            equations.append(row)
    return size * size - matrix(GF(2), equations).rank()


def elementary_family(lattice, labels, generators, gram_matrix):
    """Reflections at norm-two vectors, integral Eichler transvections, and -1.

    Each member is checked to be an isometry of the lattice whose matrix is the identity modulo
    two, and to have trivial discriminant action; the caller's reason for the family is that those
    two checks are the acceptance's per-generator conditions.
    """
    size = len(labels)
    target = lattice.discriminant_group().orthogonal_group()
    trivial = target.one()
    family = []

    def add(name, element):
        M = column_matrix(lattice, labels, element)
        assert M.transpose() * gram_matrix * M == gram_matrix, f"{name} is not an isometry"
        assert is_identity_mod(M, size, 2), f"{name} is not the identity modulo twice the lattice"
        assert element.discriminant_morphism() == trivial, f"{name} acts nontrivially on A_L"
        family.append((name, M))

    first = generators[0]
    isotropic = [g for g in generators if int(g.q()) == 0]
    for vector in isotropic:
        add(f"reflection at {first} + {vector}", lattice.reflection(first + vector))
    add(f"reflection at {first}", lattice.reflection(first))
    add("-1", lattice.Aut()({label: -g for label, g in zip(labels, generators)}))
    for vector in isotropic:
        for other in [first] + list(generators):
            if int(vector.b(other)) == 0 and int(other.q()) != 0:
                add(f"t({vector}, {other})", lattice.eichler_transvection(vector, other))
    return family


U2 = [[0, 2], [2, 0]]


def of_the_type(extras):
    """`<2> + U(2) + <-2>^extras`: the ranks of the T_Co family, from three upwards."""
    factors = (Lattices(ZZ)([[2]]), Lattices(ZZ)(U2)) + tuple(Lattices(ZZ)([[-2]]) for _ in range(extras))
    return Lattices(ZZ).orthogonal_sum(factors)


print("== part 1: the family inside the kernel of T_Co, and its level-four span", flush=True)
T = NamedLattices.Tco
labels, generators, G = gram(T)
size = len(labels)
print(f"   rank {size}  det {T.determinant()}  signature {T.signature_pair()}  "
      f"|A_L| {T.discriminant_group().cardinality()}", flush=True)
print(f"   rank of (G/2) mod 2 {((G / 2).change_ring(GF(2))).rank()}  "
      f"level-four available dimension {level_four_available(size, G)}", flush=True)
family = elementary_family(T, labels, generators, G)
print(f"   family size {len(family)}; every member: isometry of L, == 1 (mod 2L), rho trivial",
      flush=True)
print(f"   family level-four span {level_four_span([M for _, M in family], size)}", flush=True)
for root in generators[3:]:
    if int(root.q()) == -4:
        M = column_matrix(T, labels, T.reflection(root))
        print(f"   control: the reflection at the norm--4 root {root} is an isometry "
              f"{M.transpose() * G * M == G} and is the identity mod 2L "
              f"{is_identity_mod(M, size, 2)}", flush=True)
step("part 1")

print("== part 2: the level-four image of the whole kernel against the family, ranks 3 to 5", flush=True)
for extras in (0, 1, 2):
    L = of_the_type(extras)
    labels, generators, G = gram(L)
    size = len(labels)
    target = L.discriminant_group().orthogonal_group()
    order = int(target.cardinality())
    print(f"   rank {size}: |A_L| {L.discriminant_group().cardinality()}  |O(A_L)| {order}  "
          f"level-four available dimension {level_four_available(size, G)}", flush=True)
    if order > 4096:
        print("      the exact generating family is over 4096 cosets here; not measured", flush=True)
        continue
    exact = tuple(L.stable_orthogonal_group().schreier_generators())
    exact_matrices = [column_matrix(L, labels, g) for g in exact]
    assert all(M.transpose() * G * M == G for M in exact_matrices)
    assert all(is_identity_mod(M, size, 2) for M in exact_matrices)
    assert all(g.discriminant_morphism() == target.one() for g in exact)
    family = elementary_family(L, labels, generators, G)
    print(f"      exact family: {len(exact)} elements, level-four span "
          f"{level_four_span(exact_matrices, size)}", flush=True)
    print(f"      the family : {len(family)} elements, level-four span "
          f"{level_four_span([M for _, M in family], size)}", flush=True)
    step(f"rank {size}")

print("== part 3: the two subgroups inside O(L/8L), rank 3", flush=True)
L = of_the_type(0)
labels, generators, G = gram(L)
size = len(labels)
modulus = 8
points = [(a, b, c) for a in range(modulus) for b in range(modulus) for c in range(modulus)]
position = {point: i for i, point in enumerate(points)}


def permutation(M):
    images = []
    for point in points:
        image = tuple(sum(int(M[i][j]) * point[j] for j in range(size)) % modulus for i in range(size))
        images.append(position[image])
    return libgap.PermList([i + 1 for i in images])


def subgroup(matrices, name):
    group = libgap.Group([permutation(M) for M in matrices])
    print(f"   {name}: {len(matrices)} generators on {len(points)} points, order {group.Size()}",
          flush=True)
    return group


exact = [column_matrix(L, labels, g) for g in L.stable_orthogonal_group().schreier_generators()]
house = [M for _, M in elementary_family(L, labels, generators, G)]
exact_group = subgroup(exact, "exact family")
family_group = subgroup(house, "the family")
print(f"   the family is contained in the exact family: "
      f"{bool(libgap.IsSubgroup(family_group, exact_group))}", flush=True)
print(f"   the exact family is contained in the family: "
      f"{bool(libgap.IsSubgroup(exact_group, family_group))}", flush=True)
step("part 3")
