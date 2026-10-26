r"""Faces and stabilizers of the positive quadrant of \(\mathbb Z^2\)."""

from sage_extensions.all import *


def test_the_positive_quadrant_has_two_rays_and_a_stabilizer_of_order_two() -> None:
    r"""\(O(\mathbb Z^2)\) is the signed permutation group of order \(2^2\cdot2!=8\).
    The quadrant \(\mathbb R_{\ge0}e_0+\mathbb R_{\ge0}e_1\) has two rays and is
    stabilized exactly by \(\{1,\ (e_0\leftrightarrow e_1)\}\); the swap moves the
    ray through \(e_0\), so the stabilizer of that ray inside it is trivial.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    orthogonal = lattice.O()
    cell = lattice.reduction_cell(((1, 0), (0, 1)))
    e0, e1 = lattice.module_generators()
    labels = lattice.module_generating_set()
    swap = orthogonal({labels[0]: e1, labels[1]: e0})

    assert orthogonal.cardinality() == 8
    assert cell.faces(1).cardinality() == 2
    assert cell.faces(2).cardinality() == 1
    assert cell.faces(3).cardinality() == 0

    stabilizer = cell.stabilizer(orthogonal)
    assert stabilizer.cardinality() == 2
    assert swap in stabilizer

    ray = cell.facet((1, 0))
    face_stabilizer = cell.face_stabilizer(ray, orthogonal)
    assert face_stabilizer.cardinality() == 1
    assert swap not in face_stabilizer
