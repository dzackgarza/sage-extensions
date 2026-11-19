r"""Search Sterk's 22 roots for the issue's invalidating input, and find none.

The issue defines the invalidating input as "a permutation of the 22 roots that preserves the Gram
matrix of R but not its rational relations".  This script decides the question on the fixture itself
and on every subfamily of it that can carry a relation, and prints what it finds.

Run it inside the adopted image with the checkout bound at `/work`:

    /sage/.venv/bin/python results/issue255-the-invalidating-input-search.py

Part one: the 22 roots.  The Gram-preserving permutations are the diagram's automorphisms, since the
Coxeter matrix is a function of the Gram; each is applied to the coordinate matrix and the four
relations are carried through it.

Part two: every subfamily of the 22 roots that carries a relation with at least four zero
coordinates -- the relations that a datum naming some of the vertices could break.  A subfamily whose
span is nondegenerate cannot host one (the relations are then the kernel of its Gram matrix), so only
the degenerate ones are searched; for each, every automorphism of its diagram is asked whether it
carries the whole relation space into itself.
"""

from itertools import combinations

from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.rational_field import QQ

from sage_extensions.all import CoxeterDiagrams, Lattices, NamedLattices, ZZ
from sage_extensions.sterk import Sterk
from sage_extensions.tensors.tensor import _engine_component_matrix

LATTICE = NamedLattices.TdP
LABELS = tuple(LATTICE.module_generating_set())
ROOTS = tuple(Sterk.roots_18_2_0()[f"v{index}"] for index in range(1, 23))
COORDINATES = sage_matrix(
    QQ, [[int(root.to_vector()(label)) for label in LABELS] for root in ROOTS]
)
GRAM = COORDINATES * _engine_component_matrix(LATTICE.gram_tensor()).change_ring(QQ) * COORDINATES.transpose()
RELATIONS = COORDINATES.transpose().right_kernel().basis_matrix()


def carried(relation_matrix, rows):
    r"""Return whether every row of ``relation_matrix`` is still a relation of the roots ``rows``."""
    return relation_matrix * COORDINATES.matrix_from_rows(list(rows)) == 0


def main():
    print(f"roots {len(ROOTS)} rank {COORDINATES.rank()} relations {RELATIONS.nrows()}")
    diagram = CoxeterDiagrams().from_roots(ROOTS)
    preserving = 0
    breaking = 0
    for automorphism in diagram.Aut():
        permutation = [int(automorphism(index)) - 1 for index in range(1, 23)]
        permuted = COORDINATES.matrix_from_rows(permutation)
        if permuted * _engine_component_matrix(LATTICE.gram_tensor()).change_ring(QQ) * permuted.transpose() != GRAM:
            continue
        preserving = preserving + 1
        if not carried(RELATIONS, permutation):
            breaking = breaking + 1
    print(f"diagram automorphisms {int(diagram.Aut().order())}")
    print(f"Gram-preserving permutations {preserving}")
    print(f"of those, breaking a rational relation {breaking}")

    supports = {}
    for subset in combinations(range(22), 4):
        block = RELATIONS.matrix_from_columns(list(subset))
        if block.rank() == 4:
            continue
        in_kernel = block.transpose().right_kernel().basis_matrix() * RELATIONS
        for row in range(in_kernel.nrows()):
            support = tuple(index for index in range(22) if in_kernel[row, index] != 0)
            supports.setdefault(support, None)
    print(f"relation supports with at least four zero coordinates {len(supports)}")

    degenerate = []
    for support in sorted(supports, key=len):
        rows = COORDINATES.matrix_from_rows(list(support))
        if (rows * _engine_component_matrix(LATTICE.gram_tensor()).change_ring(QQ) * rows.transpose()).rank() < rows.rank():
            degenerate.append(support)
    print(f"of those, spans degenerate {len(degenerate)} sizes {sorted(set(len(s) for s in degenerate))}")

    hits = 0
    for support in degenerate:
        subdiagram = CoxeterDiagrams().from_roots(tuple(ROOTS[index] for index in support))
        relation_basis = (
            COORDINATES.matrix_from_rows(list(support)).transpose().right_kernel().basis_matrix()
        )
        for automorphism in subdiagram.Aut():
            permutation = [int(automorphism(index)) - 1 for index in range(1, len(support) + 1)]
            if not carried(relation_basis, [support[position] for position in permutation]):
                hits = hits + 1
    print(f"degenerate supports whose automorphisms break a relation {hits}")

    # The control: the same check on the four-root degenerate family must find its relation broken,
    # so that a zero above is a fact about the 22 roots and not about the check.
    plane = Lattices(ZZ)([[-2, 1, 0], [1, -2, 0], [0, 0, 0]])
    first, second, radical = plane.module_generators()
    small = (first, second, first + second, first + radical)
    small_coordinates = sage_matrix(
        QQ, [[int(root.to_vector()(label)) for label in plane.module_generating_set()] for root in small]
    )
    small_relations = small_coordinates.transpose().right_kernel().basis_matrix()
    swapped = sage_matrix(QQ, small_coordinates.matrix_from_rows([3, 1, 2, 0]))
    print(
        "four-root control:"
        f" relations {small_relations.nrows()}"
        f" broken {small_relations * swapped != 0}"
    )


if __name__ == "__main__":
    main()
