r"""The standard integral lattice in the rational hyperbolic plane has quotient (M/2Mcong(mathbf Z/2)^2)."""

from sage_extensions.all import *  # noqa: F401,F403


def _standard_hyperbolic_integral_structure():
    plane = Lattices(QQ)("U")
    restriction = Modules(QQ).restriction_of_scalars(
        ZZ.Mor(QQ)(lambda n: QQ(n))
    )
    space = restriction(plane)
    e0, e1 = plane.module_generators()
    inclusion = space.submodule([space(e0), space(e1)])
    action = IntegralStructureAction(plane.O(), inclusion)
    return plane, action


def test_standard_hyperbolic_finite_commensurability_quotient_retains_reference_data() -> None:
    plane, action = _standard_hyperbolic_integral_structure()
    quotient = action.finite_quotient(2)

    assert quotient.rational_group() is plane.O()
    assert quotient.reference_inclusion() is action.lattice_inclusion()
    assert quotient.reference_lattice() is action.lattice_inclusion().domain()
    assert quotient.ambient_restricted_space() is action.lattice_inclusion().codomain()
    assert quotient.reference_stabilizer() == action.stabilizer()


def test_standard_hyperbolic_mod_two_quotient_has_four_elements_and_full_reference_image() -> None:
    plane, action = _standard_hyperbolic_integral_structure()
    quotient = action.finite_quotient(2)
    module = quotient.quotient_module()
    projection = quotient.quotient_projection()
    scaling = quotient.scaling_morphism()
    reference = quotient.reference_lattice()
    image = quotient.intermediate_image(quotient.reference_inclusion())

    assert module.cardinality() == cardinal(4)
    assert projection.domain() is reference
    assert projection.codomain() is module
    assert all(
        scaling(generator) == 2 * generator
        for generator in reference.module_generators()
    )
    assert image.cardinality() == cardinal(4)


def test_identity_rational_isometry_restricts_and_descends_to_identity_mod_two() -> None:
    plane, action = _standard_hyperbolic_integral_structure()
    quotient = action.finite_quotient(2)
    identity = plane.O().one()
    restricted = quotient.restricted_automorphism(identity)
    descended = quotient.quotient_automorphism(identity)

    assert restricted == quotient.reference_lattice().O().one()
    assert descended == quotient.quotient_module().Aut().one()
