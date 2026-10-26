from sage_extensions.all import *


def test_the_points_of_rank_one_lattice_two_within_norm_one_of_one_half_are_zero_and_e() -> None:
    r"""In ``<2>``, ``q(n e - e/2) = 2 (n - 1/2)^2 <= 1`` exactly for ``n = 0, 1``, each at ``1/2``."""
    lattice = Lattices(ZZ)([[2]])
    target = (QQ(1) / 2,)
    close = lattice.close_vectors(target, ZZ(1))

    assert close.cardinality() == 2
    vectors = close.index_set()
    (generator,) = lattice.module_generators()
    assert Set(vectors) == Set((lattice.zero(), generator))
    assert all(close[vector] == QQ(1) / 2 for vector in vectors)
    assert lattice.closest_vector(target) in vectors
