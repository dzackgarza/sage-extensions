"""#353: validate the conventions before believing any of them.

Builds the generator's matrix in the ambient basis and in the plane's block basis,
checks that the two agree on images of actual vectors, and then compares the
library's membership test `is_in_image` with an exact coordinate solve on vectors
that are known to lie outside the plane.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage.all import ZZ as SageZZ, QQ as SageQQ, matrix as engine_matrix

t0 = time.time()


def say(*args):
    print(f"[{time.time() - t0:7.1f}s]", *args, flush=True)


lattice = NamedLattices.TEn
labels = tuple(lattice.module_generating_set())
n = len(labels)
elements = list(lattice.module_generators())
plane = lattice.primitive_isotropic_subobject(
    2 * elements[0] + 2 * elements[1] + elements[4] + elements[5], elements[2]
)


def coord(vector):
    return [int(vector.to_vector()(label)) for label in labels]


def built(vector_coordinates):
    return plane.vector_from_coordinates(vector_coordinates)


plane_rows = [coord(vector) for vector in plane.plane_basis()]
plane_matrix = engine_matrix(SageQQ, plane_rows)  # rows: the two plane vectors
perp_rows = [coord(vector) for vector in plane.perpendicular_basis()]
block_rows = [coord(vector) for vector in plane.plane_block_basis()]
change = engine_matrix(SageQQ, block_rows)          # block coords = change * ambient coords
inverse = change.inverse()

say("block basis rows 0..3 (U then P):", block_rows[0], block_rows[1], block_rows[2], block_rows[3])
say("plane rows:", plane_rows)
assert block_rows[2] == plane_rows[0] and block_rows[3] == plane_rows[1], "block P block is the plane"


def in_plane_by_solve(row):
    r"""Whether the coordinate row lies in the plane's ZZ-span, exactly."""
    target = engine_matrix(SageQQ, n, 1, row)
    try:
        solution = plane_matrix.transpose().solve_right(target)
    except (ValueError, ArithmeticError):
        return False
    if (plane_matrix.transpose() * solution - target).norm() != 0:
        return False
    return all(entry.denominator() == 1 for entry in solution.list())


def in_plane_by_gram(row):
    r"""Whether the row is orthogonal to everything killing the plane, plus rank check."""
    return in_plane_by_solve(row)


# --- the library's own membership test on vectors whose answer is known -------
say("")
say("membership test, on vectors whose answer is known by hand:")
for name, row in (
    ("0", [0] * n),
    ("the first plane vector", plane_rows[0]),
    ("twice the second plane vector", [2 * entry for entry in plane_rows[1]]),
    ("e_3 (index 3, NOT in the plane)", [1 if position == 3 else 0 for position in range(n)]),
    ("e_8 (index 8, NOT in the plane)", [1 if position == 8 else 0 for position in range(n)]),
):
    vector = built(row)
    say(f"  {name}: is_in_image={plane.inclusion().is_in_image(vector)} "
        f"by solve={in_plane_by_solve(row)}")

# --- the conventions ---------------------------------------------------------
returned = tuple(plane.unipotent_radical_generators())
say("")
say("|unipotent_radical_generators| =", len(returned))
for position, automorphism in enumerate(returned[:3]):
    images = [coord(automorphism(lattice.module_generator(label))) for label in labels]
    standard = engine_matrix(SageQQ, [[images[j][i] for j in range(n)] for i in range(n)])  # S[i][j] = image of e_j
    block = change * standard * inverse
    sample = block_rows[4]
    direct = change * engine_matrix(SageQQ, n, 1, [sum(sample[j] * images[j][i] for j in range(n)) for i in range(n)])
    through = block * engine_matrix(SageQQ, n, 1, [1 if index == 4 else 0 for index in range(n)])
    say(f"#{position}: block matrix agrees on a K vector: {direct == through}")
    say(f"  (g-1)(plane basis 0) = {[sum(plane_rows[0][j] * images[j][i] for j in range(n)) - plane_rows[0][i] for i in range(n)]}")
    say(f"  (g-1)(plane basis 1) = {[sum(plane_rows[1][j] * images[j][i] for j in range(n)) - plane_rows[1][i] for i in range(n)]}")
    for j in range(4, n):
        difference = [sum(block_rows[j][k] * images[k][i] for k in range(n)) - block_rows[j][i] for i in range(n)]
        if any(difference):
            say(f"  k_{j}: (g-1)k in P by solve = {in_plane_by_solve(difference)} | "
                f"library is_in_image = {plane.inclusion().is_in_image(built(difference))} | "
                f"block components outside P = {[block[i, j] - (1 if i == j else 0) for i in [0, 1] + list(range(4, n))]}")
say("done")
