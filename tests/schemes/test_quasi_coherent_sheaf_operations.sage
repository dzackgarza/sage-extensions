r"""Kernels, cokernels, tensor products and local presentations of quasi-coherent sheaves.

On an affine scheme ``M |-> M~`` is an equivalence onto the quasi-coherent
sheaves, so each operation is the module operation carried across.  The
specimen is multiplication by a coordinate on the affine line, whose cokernel
is the structure sheaf of the origin: nonzero, killed by the coordinate, and
zero on the open where that coordinate is a unit.
"""

from sage_extensions.all import *


def _line_and_multiplication():
    line = AffineSpaces(QQ)(1, names=("x",))
    algebra = line.coordinate_ring()
    x = algebra.algebra_generator("x")
    sheaves = QuasiCoherentSheaves(line)
    structure = sheaves.associated_sheaf(algebra.free_module(1))
    module = sheaves.global_sections(structure)
    multiply_by_x = sheaves.Mor(structure, structure)(
        {0: module.scalar_multiple(x, module.module_generator(0))}
    )
    return line, algebra, x, sheaves, structure, multiply_by_x




def test_multiplication_by_a_coordinate_has_zero_kernel_and_a_skyscraper_cokernel() -> None:
    line, algebra, x, sheaves, structure, multiply_by_x = _line_and_multiplication()

    assert multiply_by_x.domain() is structure
    assert multiply_by_x.codomain() is structure
    assert multiply_by_x in sheaves.Mor(structure, structure)
    assert multiply_by_x.underlying_module_morphism().domain() is sheaves.global_sections(structure)
    assert multiply_by_x.underlying_module_morphism().codomain() is sheaves.global_sections(structure)

    kernel = sheaves.kernel(multiply_by_x)
    kernel_sections = sheaves.global_sections(kernel)
    # Q[x] is a domain, so multiplication by x is injective and the kernel
    # sheaf is zero: every one of its generators is the zero section.
    assert all(
        kernel_sections.module_generator(label) == kernel_sections.zero()
        for label in kernel_sections.module_generating_set()
    )

    cokernel = sheaves.cokernel(multiply_by_x)
    cokernel_sections = sheaves.global_sections(cokernel)
    origin_section = cokernel_sections.module_generator(0)
    assert origin_section != cokernel_sections.zero()
    assert cokernel_sections.scalar_multiple(x, origin_section) == cokernel_sections.zero()

    # Away from the origin x is a unit, so the skyscraper has no sections there.
    away = line.distinguished_open(x)
    restricted = cokernel.restriction_map(line, away)(origin_section)
    assert restricted == cokernel.sections_on_distinguished_open(away).zero()




def test_the_skyscraper_has_the_presentation_that_defines_it() -> None:
    r"""``O --x--> O -> O_origin -> 0`` on the affine line."""
    line, algebra, x, sheaves, structure, multiply_by_x = _line_and_multiplication()
    origin_sheaf = sheaves.associated_sheaf(multiply_by_x.cokernel())

    presentation = sheaves.local_presentation(origin_sheaf)
    assert presentation.domain().module_generating_set().cardinality() == 1
    assert presentation.codomain().module_generating_set().cardinality() == 1
    # The presenting relation is multiplication by x, so the presented sheaf is
    # killed by x while its degree-zero free sheaf is not.
    presented = sheaves.global_sections(origin_sheaf)
    generator = presented.module_generator(0)
    assert generator != presented.zero()
    assert presented.scalar_multiple(x, generator) == presented.zero()
