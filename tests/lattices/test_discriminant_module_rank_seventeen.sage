r"""The discriminant module of a negative even rank-17 reduction is not trivial.

The consumer case: ``U^2 + E8^2 + A1`` reduced along its two hyperbolic isotropic
basis vectors.  The two lines lie in different hyperbolic planes, so
``<e, e'>^perp / <e, e'>`` is ``E8^2 + A1``: even, negative definite of rank 17,
with determinant ``+-2`` and discriminant group ``Z/2``.  The minimal case
``<-2>`` is checked first, then the rank-17 quotient, both through the objects
the library already provides: the metric/dual maps, ``discriminant_module``, its
invariant factors and cardinality, and the quotient's own maps.
"""

from sage_extensions.all import *


def test_the_minimal_negative_two_lattice_has_discriminant_z_mod_2() -> None:
    lattice = Lattices(ZZ)([[-2]])
    module = lattice.discriminant_module()
    assert module.cardinality() == 2
    factors = tuple(module.invariant_factors().values())
    assert factors == (ZZ(2),)
    # The discriminant is the cokernel of the correlation L -> L^#, so the
    # projection starts at the metric dual and lands on this exact module.
    projection = lattice.discriminant_projection()
    assert projection.domain() is lattice.dual_lattice()
    assert projection.codomain() is module
    # The group is not trivial: a generator of the metric dual L^# is one half
    # of the basis vector, and its class in L^#/L has order 2.
    dual_generator = lattice.dual_lattice().module_generator(0)
    discriminant_class = lattice.discriminant_class(dual_generator)
    assert discriminant_class.additive_order() == 2


def test_the_two_U_two_E8_A1_reduction_is_even_rank_seventeen_with_discriminant_z_mod_2() -> None:
    plane = NamedLattices.U
    e8 = NamedLattices.E8
    a1 = NamedLattices.A1
    lattice = plane + plane + e8 + e8 + a1
    assert lattice.rank() == 21

    labels = tuple(lattice.module_generating_set())
    first = lattice.module_generator(labels[0])
    second = lattice.module_generator(labels[2])
    isotropic = lattice.primitive_isotropic_subobject(first, second)
    assert isotropic.rank() == 2
    assert isotropic.is_totally_isotropic()
    assert isotropic.inclusion().is_primitive()

    reduction = isotropic.isotropic_reduction()
    quotient = reduction.quotient_lattice()
    for reduced in (reduction, quotient):
        assert reduced.rank() == 17
        assert reduced.is_even()
        positive, negative = tuple(reduced.signature())
        assert positive == 0 and negative == 17
        assert abs(reduced.determinant()) == 2
        module = reduced.discriminant_module()
        assert module.cardinality() == 2
        assert tuple(module.invariant_factors().values()) == (ZZ(2),)
        projection = reduced.discriminant_projection()
        assert projection.domain() is reduced.dual_lattice()
        assert projection.codomain() is module

    # The reduction retains the maps it was built from: I -> I^perp, the
    # complement in the ambient lattice, and the quotient framing.
    assert reduction.inclusion().domain().rank() == 2
    assert reduction.inclusion().codomain().rank() == 19
    assert reduction.orthogonal_complement().rank() == 19
    assert reduction.quotient_lattice().rank() == 17
