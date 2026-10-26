r"""Finite torsion bilinear forms expose their full orthogonal geometry.

The discriminant bilinear form of ``U(2)`` is ``(ZZ/2)^2`` with alternating
pairing ``b(e,f)=1/2``.  Its three nonzero lines are exactly the Lagrangians,
and ``O(b)=GL_2(F_2)`` acts transitively on them and on the three nonzero points.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u2_bilinear():
    return Lattices(ZZ)("U").twist(2).discriminant_bilinear_form()


def test_u2_bilinear_form_has_the_expected_pairing_and_orthogonal_group() -> None:
    form = _u2_bilinear()
    e, f = form.module_generators()
    gram = form.gram_matrix()

    assert form in TorsionBilinearFormModules(ZZ)
    assert form.b(e, e) == form.value_module().zero()
    assert form.b(f, f) == form.value_module().zero()
    assert form.b(e, f) == form.value_module()(QQ(1) / 2)
    assert gram[0, 1] == QQ(1) / 2
    assert form.O().order() == form.automorphism_group().order() == form.orthogonal_group().order() == 6
    assert form.is_isometric_to(form)
    assert form.is_isomorphic(form)
    assert form.is_anti_isometric(form)
    assert not form.is_anisotropic()
    assert form.is_metabolic()


def test_u2_bilinear_isotropic_subobjects_orbits_and_orthogonal_quotient() -> None:
    form = _u2_bilinear()
    first = form.module_generator(0)
    isotropic = form.isotropic_subobjects()
    lagrangians = form.lagrangian_subobjects()
    maximal = form.maximal_isotropic_subobjects()
    metabolizer = form.metabolizer()

    assert isotropic.cardinality() == cardinal(4)
    assert lagrangians.cardinality() == cardinal(3)
    assert maximal.cardinality() == cardinal(3)
    assert metabolizer.cardinality() == cardinal(2)
    assert form.form_vanishes_on(tuple(metabolizer.elements()))
    assert form.orthogonal_subobject(metabolizer) == metabolizer
    assert form.orthogonal_quotient(metabolizer).cardinality() == cardinal(1)
    assert form.orbit(first).cardinality() == cardinal(3)
    assert len(tuple(form.orbits())) == 2
    assert len(tuple(form.orbits_on_isotropic_subobjects())) == 2
    assert len(tuple(form.orbits_on_subobjects())) == 3


def test_u2_bilinear_normalizations_primary_parts_and_duality_are_isometries() -> None:
    form = _u2_bilinear()
    invariant = form.invariant_factor_form()
    normal = form.normal_form()
    normal_iso = form.normal_form_isometry()
    jordan = form.p_adic_jordan_form()
    decomposition = form.p_adic_jordan_decomposition()
    primary = form.primary_components()
    primary_decomposition = form.primary_decomposition()
    duality = form.pontryagin_dual_identification()

    assert invariant.is_isomorphism()
    assert normal.is_isomorphism()
    assert normal_iso.is_isomorphism()
    assert jordan.is_isomorphism()
    assert tuple(decomposition.index_set()) == (ZZ(2),)
    assert tuple(primary.index_set()) == (ZZ(2),)
    assert tuple(primary_decomposition.index_set()) == (ZZ(2),)
    assert form.primary_part(2).cardinality() == cardinal(4)
    assert tuple(generator.additive_order() for generator in form.p_adic_jordan_module_generators()) == (2, 2)
    for element in form.elements():
        character = duality(element)
        assert all(character(target) == form.b(element, target) for target in form.elements())


def test_u2_bilinear_reframing_restriction_scale_and_subquotients() -> None:
    form = _u2_bilinear()
    generators = tuple(form.module_generators())
    first = generators[0]
    line = form.subobject_generated_by((first,))
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


def test_torsion_bilinear_form_morphisms_have_identity() -> None:
    form = _u2_bilinear()
    identity = form.Mor(form).identity()

    assert identity(form.zero()) == form.zero()
    assert identity * identity == identity
