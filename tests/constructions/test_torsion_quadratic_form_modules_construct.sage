r"""Finite torsion quadratic forms expose isotropic, orthogonal, and Jordan data.

The discriminant quadratic form of ``U(2)`` has three isotropic elements and
two Lagrangian lines.  Its Brown invariant is zero and its orthogonal group has
order two, interchanging the two primitive isotropic classes.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u2_quadratic():
    return Lattices(ZZ)("U").twist(2).discriminant_quadratic_form()


def test_u2_quadratic_form_has_expected_values_brown_invariant_and_group() -> None:
    form = _u2_quadratic()
    e, f = form.module_generators()
    gram = form.gram_matrix()
    bilinear = form.associated_bilinear_form()

    assert form in TorsionQuadraticFormModules(ZZ)
    assert form.q(e) == form.value_module().zero()
    assert form.q(f) == form.value_module().zero()
    assert form.q(e + f) == form.value_module().one()
    assert gram[0, 1] == QQ(1) / 2
    assert bilinear.b(bilinear.module_generator(0), bilinear.module_generator(1)) == bilinear.value_module()(QQ(1) / 2)
    assert form.brown_invariant() == 0
    assert form.O().order() == form.automorphism_group().order() == form.orthogonal_group().order() == 2
    assert form.is_isometric_to(form)
    assert form.is_isomorphic(form)
    assert form.is_anti_isometric(form)
    assert not form.is_anisotropic()
    assert form.is_metabolic()


def test_u2_quadratic_isotropic_objects_orbits_and_characteristic_classes() -> None:
    form = _u2_quadratic()
    e = form.module_generator(0)
    isotropic = form.isotropic_subobjects()
    lagrangians = form.lagrangian_subobjects()
    maximal = form.maximal_isotropic_subobjects()
    metabolizer = form.metabolizer()

    assert form.isotropic_elements().cardinality() == cardinal(3)
    assert isotropic.cardinality() == cardinal(3)
    assert lagrangians.cardinality() == cardinal(2)
    assert maximal.cardinality() == cardinal(2)
    assert metabolizer.cardinality() == cardinal(2)
    assert form.form_vanishes_on(tuple(metabolizer.elements()))
    assert form.orthogonal_subobject(metabolizer) == metabolizer
    assert form.orthogonal_quotient(metabolizer).cardinality() == cardinal(1)
    assert form.orbit(e).cardinality() == cardinal(2)
    assert len(tuple(form.orbits())) == 3
    assert len(tuple(form.orbits_on_isotropic_subobjects())) == 2
    assert len(tuple(form.orbits_on_subobjects())) == 4
    assert form.zero().is_characteristic()
    assert not e.is_characteristic()


def test_u2_quadratic_normalizations_primary_parts_and_jordan_data() -> None:
    form = _u2_quadratic()
    invariant = form.invariant_factor_form()
    normal = form.normal_form()
    normal_iso = form.normal_form_isometry()
    jordan = form.p_adic_jordan_form()
    decomposition = form.p_adic_jordan_decomposition()
    primary = form.primary_components()
    primary_decomposition = form.primary_decomposition()

    assert invariant.is_isomorphism()
    assert normal.is_isomorphism()
    assert normal_iso.is_isomorphism()
    assert jordan.is_isomorphism()
    assert tuple(decomposition.index_set()) == (ZZ(2),)
    assert tuple(primary.index_set()) == (ZZ(2),)
    assert tuple(primary_decomposition.index_set()) == (ZZ(2),)
    assert form.primary_part(2).cardinality() == cardinal(4)
    assert tuple(generator.additive_order() for generator in form.p_adic_jordan_module_generators()) == (2, 2)
    assert form.quadratic_value_module() is form.value_module()


def test_u2_quadratic_reframing_restriction_scale_subquotients_and_twist() -> None:
    form = _u2_quadratic()
    generators = tuple(form.module_generators())
    line = form.subobject_generated_by((generators[0],))
    zero = form.subobject_generated_by(())
    reframing = form.reframing_isometry(generators)
    regenerated = form.regenerate(generators)
    restricted = form.restricted_form(line)

    assert reframing.is_isomorphism()
    assert regenerated.is_isometric_to(form)
    assert line.cardinality() == cardinal(2)
    assert form.subobjects().cardinality() == cardinal(5)
    assert restricted.cardinality() == cardinal(2)
    assert form.scale_submodule().cardinality() == cardinal(2)
    assert form.subquotient_form(zero, zero).cardinality() == cardinal(1)
    assert form.twist(-1).is_isometric_to(form)


def test_torsion_quadratic_form_morphisms_have_identity() -> None:
    form = _u2_quadratic()
    identity = form.Mor(form).identity()

    assert identity(form.zero()) == form.zero()
    assert identity * identity == identity
