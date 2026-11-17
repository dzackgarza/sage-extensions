r"""Congruence-vector stabilizers use the actual orthogonal image of L/mL (#42).

For U with basis e,f, O(U)={I,-I,S,-S}, S(e)=f and S(f)=e.
Modulo 2, -1=1, so the stabilizer of e is {I,-I}, while e+f is
fixed by the entire O(U). Modulo 6, e has trivial stabilizer;
e+f has stabilizer {I,S}. These are complete independent group
calculations, not comparisons of two implementations.
"""

from sage_extensions.all import *


def _hyperbolic_data():
    lattice = Lattices(ZZ)("U")
    e, f = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    negative = lattice.O()({label: -lattice.module_generator(label) for label in labels})
    swap = lattice.O()(dict(zip(labels, (f, e), strict=True)))
    return lattice.O(), e, f, negative, swap


def test_mod_two_stabilizers_of_line_vector_and_sum_are_correct():
    group, e, f, negative, swap = _hyperbolic_data()
    stabilized = group.congruence_vector_stabilizer(2, e)
    assert stabilized.cardinality() == cardinal(2)
    assert group.one() in stabilized and negative in stabilized
    assert swap not in stabilized and negative * swap not in stabilized
    representation = group.congruence_representation(2)
    reduced_lattice = representation.codomain().supergroup().domain()
    reduced_e = reduced_lattice.module_generator(next(iter(reduced_lattice.module_generating_set())))
    assert all(representation(generator)(reduced_e) == reduced_e for generator in stabilized.group_generators())

    whole = group.congruence_vector_stabilizer(2, e + f)
    assert whole.cardinality() == cardinal(4)
    assert group.one() in whole and negative in whole and swap in whole


def test_composite_mod_six_stabilizers_have_the_exact_images():
    group, e, f, negative, swap = _hyperbolic_data()
    stabilized = group.congruence_vector_stabilizer(6, e)
    assert stabilized.cardinality() == cardinal(1)
    assert group.one() in stabilized
    assert negative not in stabilized and swap not in stabilized

    diagonal = group.congruence_vector_stabilizer(6, e + f)
    assert diagonal.cardinality() == cardinal(2)
    assert group.one() in diagonal and swap in diagonal
    assert negative not in diagonal
    assert all(generator in diagonal for generator in diagonal.group_generators())


def test_infinite_two_u_residue_stabilizer_contains_full_integral_unipotent():
    r"""A genuine infinite-order isometry fixing e lies in Gamma_e(2).

    In 2U, e,f,u,v are null vectors with e.f=u.v=1. The map
    e->e, f->f-v, u->u+e, v->v preserves all pairings and is
    unimodular; its nth power sends u to u+n e, so it has infinite
    order. It is in Gamma_e(m) for every m. Swapping e and f does
    not lie in Gamma_e(2), while global negation does.
    """
    plane = Lattices(ZZ)("U")
    lattice = plane + plane
    group = lattice.O()
    e, f, u, v = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    shear = group(dict(zip(labels, (e, f-v, u+e, v), strict=True)))
    exchange = group(dict(zip(labels, (f, e, u, v), strict=True)))
    negative = group({label: -lattice.module_generator(label) for label in labels})
    gamma = group.congruence_vector_stabilizer(2, e)
    assert shear in gamma and negative in gamma and exchange not in gamma
    assert all((shear**n)(u) == u + n*e for n in (1, 2, 3))


def test_vector_residue_stabilizer_splits_public_isotropic_line_classes():
    r"""Gamma_e(2)={+/-I} splits O(U)'s moving-line orbit into Ze and Zf.

    An element carrying Ze onto Zf must exchange the two null axes.
    Such an element sends the reduction of e to f and is not in Gamma_e(2),
    so the two line classes remain inequivalent in the requested subgroup.
    """
    plane = Lattices(ZZ)("U")
    group = plane.O()
    e, _f = tuple(plane.module_generators())
    gamma = group.congruence_vector_stabilizer(2, e)
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    marked = arrows.object(plane.primitive_isotropic_subobject(e).inclusion())
    orbit_set = group.split_orbit(marked, gamma)
    assert orbit_set.cardinality() == cardinal(2)
    representatives = tuple(orbit_set)
    first, second = representatives
    assert arrows.Core().Mor(first, second).an_element_in(gamma) is None


def test_zero_residue_stabilizer_uses_only_its_one_point_orbit():
    r"""At composite level 1001 the module U/1001U has 1,002,001 points.

    Zero is fixed by every integral isometry, so its orbit is the singleton
    {0} regardless of that module's cardinality. The public stabilizer is
    exactly O(U). It must not enumerate all of U/1001U to recover it.
    """
    group, e, _f, negative, swap = _hyperbolic_data()
    zero = e - e
    gamma = group.congruence_vector_stabilizer(1001, zero)
    assert gamma.cardinality() == cardinal(4)
    assert group.one() in gamma and negative in gamma and swap in gamma
    assert all(generator in gamma for generator in group.group_generators())
