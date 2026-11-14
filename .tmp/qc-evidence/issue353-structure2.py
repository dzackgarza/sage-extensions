"""#353: the structure of U at Sterk's P_2, the families' spans, and the index.

Conventions, checked below: `change` has the block basis vectors of
:meth:`plane_block_basis` -- a ZZ-basis of L in the order (U | P | K), two
vectors each for U and P and eight for K = P^perp/P -- as its ROWS, so a vector
with ambient coordinates v has block coordinates `inverse^T v` and a map with
ambient matrix S has block matrix `inverse^T S change^T`.

The Lie algebra of the radical, in block coordinates and with B the block Gram
(so b(x, y) = x^T B y):

  * N(p) = 0 for the two plane vectors p        (columns 2, 3 of N vanish),
  * N(k) in P for the eight K vectors k         (columns 4..11 vanish outside rows 2, 3),
  * N^t B + B N = 0                             (an isometry of the linearisation),

and its dimension is the rank of U, because the radical is unipotent and exp/log
are polynomial bijections on a unipotent group in characteristic zero.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage.all import ZZ as SageZZ, QQ as SageQQ, matrix as engine_matrix

t0 = time.time()


def say(*args):
    print(f"[{time.time() - t0:7.1f}s]", *args, flush=True)


lattice = NamedLattices.TEn
labels = tuple(lattice.module_generating_set())
n = int(lattice.module_rank())
elements = list(lattice.module_generators())
plane = lattice.primitive_isotropic_subobject(
    2 * elements[0] + 2 * elements[1] + elements[4] + elements[5], elements[2]
)
say("lattice", lattice, "rank", n)

change = engine_matrix(SageQQ, [list(plane.coordinates(vector)) for vector in plane.plane_block_basis()])
inverse = change.inverse()
assert all(entry.denominator() == 1 for entry in inverse.list()), "not a ZZ-basis"
Gram = engine_matrix(SageQQ, plane.gram_matrix())
B = change * Gram * change.transpose()
say("block Gram diagonal blocks: U", [int(B[i, i]) for i in (0, 1)],
    "| P", [int(B[i, i]) for i in (2, 3)],
    "| K", [int(B[i, i]) for i in range(4, n)])
say("b(U, P) =", B[0:2, 2:4].list(), "| b(P, K) =", B[2:4, 4:n].list(),
    "| b(U, K) =", B[0:2, 4:n].list())

size = n * n


def blank():
    return [SageQQ(0)] * size


def fixed_pointwise():
    rows = []
    for j in (2, 3):
        for i in range(n):
            row = blank()
            row[n * i + j] = SageQQ(1)
            rows.append(row)
    return rows


def into_plane():
    rows = []
    for j in range(4, n):
        for i in [position for position in range(n) if position not in (2, 3)]:
            row = blank()
            row[n * i + j] = SageQQ(1)
            rows.append(row)
    return rows


def isometry():
    rows = []
    for a in range(n):
        for b in range(a, n):
            row = blank()
            for i in range(n):
                if B[i, b]:
                    row[n * i + a] += B[i, b]
                if B[a, i]:
                    row[n * i + b] += B[a, i]
            rows.append(row)
    return rows


def system_with(extra_rows=()):
    rows = fixed_pointwise() + into_plane() + list(extra_rows) + isometry()
    return engine_matrix(SageQQ, rows)


system = system_with()
dim_U = size - int(system.rank())
say("constraint matrix", system.dimensions(), "rank", int(system.rank()), "| rank U =", dim_U)

zero_on_perpendicular = []
for j in range(4, n):
    for i in range(n):
        row = blank()
        row[n * i + j] = SageQQ(1)
        zero_on_perpendicular.append(row)
system_Z = system_with(zero_on_perpendicular)
dim_Z = size - int(system_Z.rank())
say("rank Z =", dim_Z, "| rank(U/Z) =", dim_U - dim_Z,
    "| rank Hom(K, P) = 2*rank(K) =", 2 * (n - 4))

# ---------------------------------------------------------------------------
# The generators: ambient matrix, block matrix, logarithm, translation.
# ---------------------------------------------------------------------------


def ambient_coordinates(vector):
    return [SageQQ(int(vector.to_vector()(label))) for label in labels]


def ambient_matrix(automorphism):
    images = [ambient_coordinates(automorphism(lattice.module_generator(label))) for label in labels]
    return engine_matrix(SageQQ, [[images[j][i] for j in range(n)] for i in range(n)])  # S[i][j] = coord i of g(e_j)


def block_matrix(automorphism):
    return inverse.transpose() * ambient_matrix(automorphism) * change.transpose()


def logarithm(automorphism):
    nilpotent = block_matrix(automorphism) - engine_matrix(SageQQ, n, n, 1)
    total = engine_matrix(SageQQ, nilpotent)
    term = engine_matrix(SageQQ, nilpotent)
    for power in range(2, n + 1):
        term = term * nilpotent
        total = total + (-1) ** (power + 1) * term / power
    return total


def satisfies(matrix, constraint_matrix):
    vector = engine_matrix(SageQQ, size, 1, [matrix[i][j] for i in range(n) for j in range(n)])
    return (constraint_matrix * vector).norm() == 0


plane_rows = engine_matrix(SageQQ, [list(plane.coordinates(vector)) for vector in plane.plane_basis()])


def translation(automorphism):
    r"""Return the 16 numbers of the translation on the eight K basis vectors."""
    basis = plane.plane_block_basis()
    entry = []
    for j in range(4, n):
        vector = basis[j]
        difference = automorphism(vector) - vector
        target = engine_matrix(SageQQ, n, 1, ambient_coordinates(difference))
        solution = plane_rows.transpose().solve_right(target)
        assert (plane_rows.transpose() * solution - target).norm() == 0, f"translation {j} leaves P"
        assert all(value.denominator() == 1 for value in solution.list())
        entry.extend(int(value) for value in solution.list())
    return entry


returned = tuple(plane.unipotent_radical_generators())
say("")
say("|unipotent_radical_generators| =", len(returned))

# conventions checked against a direct image
sample = returned[0]
block = block_matrix(sample)
column = engine_matrix(SageQQ, n, 1, [SageQQ(1 if index == 4 else 0) for index in range(n)])
direct = inverse.transpose() * engine_matrix(SageQQ, n, 1, ambient_coordinates(sample(plane.plane_block_basis()[4])))
say("block matrix agrees with the direct image on a K vector:", block * column == direct)
say("(g-1) of the plane basis:", [int(entry) for entry in (ambient_matrix(sample) * engine_matrix(SageQQ, n, 1, list(plane.coordinates(plane.plane_basis()[0]))) - engine_matrix(SageQQ, n, 1, list(plane.coordinates(plane.plane_basis()[0])))).list()])


def analyse(name, family):
    logs, translations, outside = [], [], 0
    for position, automorphism in enumerate(family):
        log = logarithm(automorphism)
        if not satisfies(log, system):
            outside += 1
            say(f"  {name} #{position}: log does not lie in the radical's Lie algebra")
            continue
        logs.append([log[i][j] for i in range(n) for j in range(n)])
        translations.append(translation(automorphism))
    say(f"{name}: {len(family)} elements | in U: {len(logs)} | outside U: {outside}")
    rank_span = int(engine_matrix(SageQQ, logs).rank()) if logs else 0
    rank_translation = int(engine_matrix(SageQQ, translations).rank()) if translations else 0
    say(f"  rank of span(log family) = {rank_span} of rank U = {dim_U} -> "
        f"{'infinite index' if rank_span < dim_U else 'finite index'}")
    say(f"  rank of their translations = {rank_translation} of rank(U/Z) = {dim_U - dim_Z}")
    return rank_span, rank_translation


analyse("returned unipotent generators", returned)

say("building the parabolic family ...")
parabolic = tuple(plane.parabolic_stabilizer_generators())
radical_members = tuple(
    generator for generator in parabolic if generator in plane.unipotent_radical()
)
say("parabolic generators =", len(parabolic), "| in the radical =", len(radical_members))
analyse("parabolic radical members", radical_members)
say("done")
