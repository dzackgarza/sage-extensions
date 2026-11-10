r"""Principal congruence subgroups through the actual image in Aut(L/mL).

O(2U) is (SL2(Z) x SL2(Z))/{+-1} extended by a Klein four group, so its image
modulo three is (SL2(3) x SL2(3))/{+-1} extended by the same group, of order
24*24/2*4 = 1152, and Gamma(3) has index 1152. O(U) has order four and acts
faithfully on U/6U, so the composite modulus six has image of order four.
"""

from sage_extensions.all import *


def test_composite_modulus_on_u_is_faithful():
    group = Lattices(ZZ)("U").O()
    assert group.congruence_representation(6).codomain().cardinality() == cardinal(4)
    assert group.congruence_preimage(6).cardinality() == cardinal(1)


def test_gamma_three_of_two_hyperbolic_planes_has_index_1152():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    group = ambient.O()
    assert group.congruence_representation(3).codomain().cardinality() == cardinal(1152)
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    gamma = group.congruence_preimage(3)
    assert ambient.Aut().one() in gamma
    assert ambient.Aut()(dict(zip(labels, (-e, -f, -u, -v), strict=True))) not in gamma


def test_gamma_three_splits_the_two_null_lines_of_the_hyperbolic_plane():
    r"""O(U) acts faithfully modulo three, so Gamma(3) is trivial and Ze, Zf are two orbits."""
    ambient = Lattices(ZZ)("U")
    group = ambient.O()
    gamma = group.congruence_preimage(3)
    e, _f = tuple(ambient.module_generators())
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    marked = arrows.object(ambient.primitive_isotropic_subobject(e).inclusion())
    orbits = tuple(group.split_orbit(marked, gamma))
    assert len(orbits) == 2
    first, second = orbits[0], orbits[1]
    assert arrows.Core().Mor(first, second).an_element_in(gamma) is None
    assert arrows.Core().Mor(first, first).an_element_in(gamma) is not None

def test_gamma_two_splits_null_lines_of_two_hyperbolic_planes_into_nine_orbits():
    r"""O(2U) maps onto O+(4, 2) modulo two, and -1 is trivial there, so the Gamma(2)-orbits of primitive
    null lines are the (2 + 1)^2 = 9 singular points of the hyperbolic quadric over F_2."""
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    group = ambient.O()
    gamma = group.congruence_preimage(2)
    e, _f, _u, _v = tuple(ambient.module_generators())
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    marked = arrows.object(ambient.primitive_isotropic_subobject(e).inclusion())
    orbits = tuple(group.split_orbit(marked, gamma))
    assert len(orbits) == 9
    assert arrows.Core().Mor(orbits[0], orbits[1]).an_element_in(gamma) is None
