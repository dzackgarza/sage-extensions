r"""The quotient kernel of a split null plane contains the full GL action on it.

For L=2U perpendicular K, each GL(2,ZZ) action on the null plane
extends by its inverse transpose on the dual null plane and identity
on K. Its reduction modulo 3 is GL(2,F3), of order 48.
"""

from sage_extensions.all import *


def test_null_plane_quotient_kernel_generates_the_full_reduced_gl_action():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    basis = tuple(ambient.module_generators())
    space = ambient.primitive_isotropic_subobject(basis[0], basis[2])
    reduction = space.isotropic_reduction()
    levi = reduction.levi_action()
    kernel = levi.kernel()
    family = tuple(kernel.group_generators())
    restriction = reduction.isotropic_action()
    ring_map = PrimeFields()(3).quotient_map()
    finite_space = space.inclusion().domain().base_change(ring_map)
    finite_group = finite_space.general_linear_group()
    images = []
    for generator in family:
        assert levi(generator) == levi.codomain().one()
        changed = restriction(generator).base_change(ring_map)
        images.append(finite_group({label: changed(finite_space.module_generator(label)) for label in finite_space.module_generating_set()}))
    assert finite_group.subgroup(images).cardinality() == cardinal(48)
