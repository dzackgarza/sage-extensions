r"""Finite torsion modules enumerate their Smith residues incrementally."""

from sage_extensions.all import *


def test_a_prefix_of_two_cyclic_factors_has_the_expected_addition() -> None:
    module = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((256, 256))
    residues = iter(module)
    prefix = tuple(next(residues) for _ in range(8))

    assert prefix[0] == module.zero()
    assert all(prefix[i] != prefix[j] for i in range(8) for j in range(i))
    assert all(prefix[i] + prefix[1] == prefix[i + 1] for i in range(7))
    assert 256 * prefix[1] == module.zero()
    assert 128 * prefix[1] != module.zero()


def test_complete_iteration_agrees_with_the_selected_finite_residue_set() -> None:
    for orders in ((), (2,), (2, 4), (3, 6)):
        module = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics(orders)
        points = tuple(module)

        assert set(points) == set(module.elements())
        assert int(sum(1 for _ in points)) == int(module.cardinality())
        assert all(point != other for i, point in enumerate(points) for other in points[:i])

