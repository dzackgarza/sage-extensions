r"""Non-unimodular cusp gluing can restrict the Levi image."""

from sage_extensions.all import *


def _glued_divisibility_two_cusp():
    r"""Return the cusp obtained from ``U(2) + A1^4`` by diagonal order-two glue."""
    lattice = Lattices(ZZ)(
        [
            [-2, 1, -1, -1, -1, -1],
            [1, 0, 0, 0, 0, 0],
            [-1, 0, -2, 0, 0, 0],
            [-1, 0, 0, -2, 0, 0],
            [-1, 0, 0, 0, -2, 0],
            [-1, 0, 0, 0, 0, -2],
        ]
    )
    g, _f, r1, r2, r3, r4 = lattice.module_generators()
    isotropic = 2 * g - r1 - r2 - r3 - r4
    line = lattice.primitive_isotropic_subobject(isotropic)
    return lattice, isotropic, line


def test_glued_cusp_has_divisibility_two_and_D4_type_reduction() -> None:
    lattice, isotropic, line = _glued_divisibility_two_cusp()
    reduction = line.isotropic_reduction()

    assert isotropic.q() == 0
    assert isotropic.is_primitive()
    assert isotropic.div() == 2
    assert lattice.determinant().abs() == 16
    assert reduction.module_rank() == 4
    assert reduction.is_even()
    assert reduction.determinant().abs() == 4


def test_nonunimodular_gluing_restricts_the_definite_Levi_image() -> None:
    _lattice, _isotropic, line = _glued_divisibility_two_cusp()
    reduction = line.isotropic_reduction()
    image = reduction.levi_image()

    assert image.supergroup() is reduction.O()
    assert image.cardinality() < reduction.O().cardinality()
    assert image.cardinality() > 1
    assert all(generator in image for generator in reduction.levi_image_generators())
