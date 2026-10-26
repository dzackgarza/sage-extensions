r"""Owned toric weight complexes and their induced maps."""

from sage_extensions.all import *


def _projective_plane():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans.projective_space_fan().toric_variety(QQ)


def test_scalar_two_acts_on_the_actual_nonzero_weight_class() -> None:
    plane = _projective_plane()
    divisor = plane.canonical_divisor()
    weight = plane.character_lattice().zero()
    cohomology = plane.weight_cohomology(divisor, weight, 2)

    assert cohomology.dimension() == 1
    cycle_module = cohomology.cochain_complex().graded_piece(2)
    label = next(iter(cycle_module.module_generating_set()))
    cycle = cycle_module.module_generator(label)
    class_ = cohomology.class_of_cycle(cycle)
    assert class_.parent() is cohomology
    assert cohomology.cycle_representative(class_).parent() is cycle_module
    assert class_ != cohomology.zero()

    cochain_map = plane.weight_scalar_cochain_map(divisor, weight, QQ(2))
    induced = plane.weight_scalar_cohomology_map(divisor, weight, 2, QQ(2))

    assert cochain_map.component(2)(cycle) == QQ(2) * cycle
    scaled = QQ(2) * class_
    assert scaled.parent() is cohomology
    assert induced(class_) == scaled
    assert induced(class_).parent() is cohomology




