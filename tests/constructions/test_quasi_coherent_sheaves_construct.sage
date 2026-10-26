r"""On an affine scheme, associated quasi-coherent sheaves recover their modules."""

from sage_extensions.all import *  # noqa: F401,F403


def test_associated_sheaf_on_the_affine_line_recovers_global_sections() -> None:
    line = AffineSpaces(QQ)(1, names=("x",))
    algebra = line.coordinate_ring()
    module = algebra.free_module(1)
    sheaves = QuasiCoherentSheaves(line)
    sheaf = sheaves.associated_sheaf(module)

    assert sheaf in sheaves
    assert sheaves.global_sections(sheaf) is module


def test_coordinate_multiplication_has_the_expected_cokernel_sheaf() -> None:
    line = AffineSpaces(QQ)(1, names=("x",))
    algebra = line.coordinate_ring()
    x = algebra.algebra_generator("x")
    sheaves = QuasiCoherentSheaves(line)
    structure = sheaves.associated_sheaf(algebra.free_module(1))
    module = sheaves.global_sections(structure)
    multiply_by_x = sheaves.Mor(structure, structure)(
        {0: module.scalar_multiple(x, module.module_generator(0))}
    )
    cokernel = sheaves.cokernel(multiply_by_x)
    sections = sheaves.global_sections(cokernel)
    generator = sections.module_generator(0)

    assert generator != sections.zero()
    assert sections.scalar_multiple(x, generator) == sections.zero()
