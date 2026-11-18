#!/usr/bin/env python3
"""The level-eight content of the Coble lattice's discriminant kernel.

Run from the repository root: python3 results/coble-kernel-level-eight.py

The discriminant kernel of T_Co = <2> + U(2) + E8(-2) is Gamma = ker(O(L) -> O(A_L)),
the level-two congruence subgroup of the odd unimodular M = <1> + U + E8(-1) whose Gram
matrix is half of T_Co's.  Its level measures are

    Gamma(2^k) = { X in Gamma : X = I mod 2^k },
    Gamma/Gamma(4) = (Z/2)^56,  spanned by the classes (X - I)/2 of the reflections in
    vectors of square +-1 (see tests/lattices/test_the_coble_kernel_candidates_pass_the_generator_checks.sage).

The question this script answers is the next one down: how much of Gamma(4)/Gamma(8) the
reflections reach.  Every reflection in a vector of square +-1 is an involution, so squares
contribute nothing; a product of two reflections lies in Gamma(4) exactly when the two
vectors agree modulo two, and its class (X - I)/4 mod 2 is the object counted here.

Arithmetic is exact integers throughout; no engine is used.
"""
import itertools
import random

N = 11


def cartan():
    matrix = [[0] * 8 for _ in range(8)]
    for i in range(8):
        matrix[i][i] = 2
    for a, b in [(4, 3), (3, 1), (4, 5), (5, 6), (6, 7), (7, 8), (4, 2)]:
        matrix[a - 1][b - 1] = matrix[b - 1][a - 1] = -1
    return matrix


CARTAN = cartan()
HALF = [[0] * N for _ in range(N)]          # the odd unimodular half: T_Co's Gram is twice this
HALF[0][0] = 1
HALF[1][2] = HALF[2][1] = 1
for i in range(8):
    for j in range(8):
        HALF[3 + i][3 + j] = -CARTAN[i][j]


def pairing(vector):
    return [sum(HALF[i][j] * vector[j] for j in range(N)) for i in range(N)]


def square(vector):
    return sum(vector[i] * pairing(vector)[i] for i in range(N))


def product(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(N)) for j in range(N)] for i in range(N)]


def reflection(vector):
    """`s_v = 1 - 2 q(v) v (G v)^T`, integral exactly when `q(v) = +-1`."""
    image = pairing(vector)
    norm = square(vector)
    return [[(1 if i == j else 0) - 2 * norm * vector[i] * image[j] for j in range(N)] for i in range(N)]


def displaced(matrix, vector):
    return [sum(matrix[i][j] * vector[j] for j in range(N)) for i in range(N)]


def is_congruent(matrix, power):
    return all((matrix[i][j] - (1 if i == j else 0)) % (2 ** power) == 0
               for i in range(N) for j in range(N))


def class_of(matrix, power):
    bits = 0
    for i in range(N):
        for j in range(N):
            if ((matrix[i][j] - (1 if i == j else 0)) // (2 ** power)) % 2:
                bits ^= 1 << (i * N + j)
    return bits


def rank_of(rows):
    pivots = {}
    for row in rows:
        current = row
        while current:
            column = current.bit_length() - 1
            if column in pivots:
                current ^= pivots[column]
            else:
                pivots[column] = current
                break
    return len(pivots)


def inverse(matrix):
    import fractions
    wide = [[fractions.Fraction(HALF[i][j]) for j in range(N)]
            + [fractions.Fraction(1 if i == j else 0) for j in range(N)] for i in range(N)]
    for column in range(N):
        pivot = next(row for row in range(column, N) if wide[row][column] != 0)
        wide[column], wide[pivot] = wide[pivot], wide[column]
        scale = wide[column][column]
        wide[column] = [entry / scale for entry in wide[column]]
        for row in range(N):
            if row != column and wide[row][column] != 0:
                factor = wide[row][column]
                wide[row] = [wide[row][k] - factor * wide[column][k] for k in range(2 * N)]
    inverse_half = [[wide[i][N + j] for j in range(N)] for i in range(N)]
    transpose = [[matrix[j][i] for j in range(N)] for i in range(N)]
    return product(product(inverse_half, transpose), HALF)


def roots():
    """The 56 candidate roots, read from the test that carries them."""
    text = open("tests/lattices/test_the_coble_kernel_candidates_pass_the_generator_checks.sage").read()
    block = text.split("CANDIDATE_ROOTS = (")[1].split("\n)")[0]
    return [tuple(int(entry) for entry in line.strip().strip(",").strip("()").split(","))
            for line in block.strip().splitlines() if line.strip()]


def main():
    candidates = [reflection(list(vector)) for vector in roots()]
    inverses = [inverse(matrix) for matrix in candidates]
    print(f"candidates whose square is +-1 and which lie in Gamma: {len(candidates)}")

    commutators = []
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            word = product(product(product(candidates[i], candidates[j]), inverses[i]), inverses[j])
            assert is_congruent(word, 2), "a commutator of two level-two elements left Gamma(4)"
            commutators.append(class_of(word, 2))
    inside = rank_of(commutators)
    print(f"commutators: {len(commutators)}, level-four classes span {inside} dimensions")

    orbits = {}
    for vector in roots():
        key = tuple(entry % 2 for entry in vector)
        pool = {tuple(vector)}
        for matrix in candidates:
            pool.add(tuple(displaced(matrix, list(vector))))
        orbits.setdefault(key, []).extend(list(entry) for entry in sorted(pool)[:6])
    vectors = [(key, vector) for key, pool in orbits.items() for vector in pool]
    print(f"unit vectors conjugate to the candidates: {len(vectors)}")

    pairs = []
    for pool in orbits.values():
        for left, right in itertools.product(pool, pool):
            two = product(reflection(left), reflection(right))
            if is_congruent(two, 2):
                pairs.append(class_of(two, 2))
    print(f"two-fold products in Gamma(4): {len(pairs)}, span {rank_of(pairs)} dimensions, "
          f"with the commutators {rank_of(commutators + pairs)}")

    random.seed(591)
    deeper = 0
    collected = []
    for _ in range(20000):
        chosen = [vectors[random.randrange(len(vectors))][1] for _ in range(4)]
        word = reflection(chosen[0])
        for vector in chosen[1:]:
            word = product(word, reflection(vector))
        if is_congruent(word, 2):
            deeper += 1
            collected.append(class_of(word, 2))
    print(f"four-fold products in Gamma(4): {deeper}, span with the commutators "
          f"{rank_of(commutators + pairs + collected)}")

    space = max(rank_of(commutators), rank_of(pairs), rank_of(commutators + pairs + collected))
    print()
    print(f"every reflection product above lies in one {space}-dimensional subspace of the")
    print("level-four class space, whose dimension is 54 or 55: 55 is the alternating space")
    print("bound, 54 is what these products reach.  If the space is 55-dimensional then no")
    print("subgroup generated by reflections in square-+-1 vectors is all of Gamma, and the")
    print("56 candidates do not generate it; if it is 54-dimensional, the reflections are")
    print("level-eight complete and the missing step is one level deeper.")


if __name__ == "__main__":
    main()
