r"""The split null-plane unipotent radical in 3U has full integral parameters.

Its action on the quotient lifts gives Hom(U,ZZ^2), of rank four.
The kernel of that action is the integral skew shear, of rank one.
Surjectivity onto that Hom module and a unit central parameter generate
the full integral two-step unipotent group.
"""

from sage_extensions.all import *


def test_null_plane_unipotent_kernel_has_the_full_hom_and_central_lattices():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    e, f, a, b, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    space = ambient.primitive_isotropic_subobject(e, a)
    inclusion = space.inclusion()
    null_labels = tuple(inclusion.domain().module_generating_set())
    reduction = space.isotropic_reduction()
    kernel = reduction.unipotent_kernel()
    levi = reduction.levi_action()
    parameters = ZZ.free_module(4)
    parameter_labels = tuple(parameters.module_generating_set())
    images = []
    central_parameters = []
    for generator in kernel.group_generators():
        assert generator(e) == e and generator(a) == a
        assert levi(generator) == levi.codomain().one()
        first = inclusion.lift(generator(u)-u).to_vector()
        second = inclusion.lift(generator(v)-v).to_vector()
        values = tuple(first(label) for label in null_labels) + tuple(second(label) for label in null_labels)
        images.append(parameters.linear_combination(dict(zip(parameter_labels, values, strict=True))))
        if all(value == 0 for value in values):
            parameter = generator(f).to_vector()(labels[2])
            assert generator(f) == f+parameter*a
            assert generator(b) == b-parameter*e
            central_parameters.append(parameter)
        for point in (e, f, a, b, u, v):
            assert (~generator)(generator(point)) == point
    assert parameters.subobject_on(images).inclusion().cokernel().cardinality() == cardinal(1)
    assert ZZ.ideal(central_parameters) == ZZ.ideal(1)
