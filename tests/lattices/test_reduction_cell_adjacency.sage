r"""Adjacency of cones in the standard lattice \(\mathbb Z^2\)."""

from sage_extensions.all import *


def test_a_quadrant_meets_its_reflection_in_a_ray_and_its_opposite_only_at_the_origin() -> None:
    r"""The cones on \((e_0,e_1)\) and \((-e_0,e_1)\) share the ray \(\mathbb R_{\ge0}e_1\);
    the cones on \((e_0,e_1)\) and \((-e_0,-e_1)\) meet only in \(0\).  The reflection
    \(e_0\mapsto-e_0\) in \(O(\mathbb Z^2)\) carries the first onto the second.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    first = lattice.reduction_cell(((1, 0), (0, 1)))
    reflected = lattice.reduction_cell(((-1, 0), (0, 1)))
    opposite = lattice.reduction_cell(((-1, 0), (0, -1)))

    common = first.intersection(reflected)
    assert common.dimension() == 1
    assert common.is_face_of(first)
    assert common.is_face_of(reflected)
    assert first.is_adjacent_to(reflected)
    assert not first.is_adjacent_to(opposite)

    e0, e1 = lattice.module_generators()
    labels = lattice.module_generating_set()
    reflection = lattice.O()({labels[0]: -e0, labels[1]: e1})
    assert first.transported_by(reflection).is_equal_to(reflected)
    assert not first.transported_by(reflection).is_equal_to(first)
