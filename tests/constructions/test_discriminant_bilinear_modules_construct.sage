r"""Discriminant bilinear modules retain the lattice origin and Nikulin glue.

For ``L=<2>+<-2>`` the diagonal order-two discriminant class is isotropic and
Lagrangian.  Gluing along it gives an index-two unimodular overlattice and the
descended discriminant bilinear form is zero.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _sign_pair_bilinear():
    lattice = Lattices(ZZ)([[2]]) + Lattices(ZZ)([[-2]])
    form = lattice.discriminant_bilinear_form()
    first, second = form.module_generators()
    glue = form.subgroup_on((first + second,))
    return lattice, form, glue


def test_discriminant_bilinear_form_retains_value_module_and_quadratic_refinement() -> None:
    lattice, form, _glue = _sign_pair_bilinear()

    assert form in DiscriminantBilinearModules(ZZ)
    assert form.bilinear_value_module() is form.value_module()
    assert lattice.discriminant_quadratic_form().associated_quadratic_form() == lattice.discriminant_quadratic_form()
    assert form.O() == form.orthogonal_group()
    assert form.automorphism_group() == form.O()
    assert form.invariant_factor_form().is_isomorphism()
    assert form.normal_form().is_isomorphism()


def test_discriminant_bilinear_glue_descends_to_zero_form_and_unimodular_overlattice() -> None:
    _lattice, form, glue = _sign_pair_bilinear()
    quotient = form.orthogonal_quotient(glue)
    descended = form.discriminant_form_of_overlattice(glue)
    inclusion = form.overlattice_from_isotropic_subobject(glue)

    assert glue.cardinality() == cardinal(2)
    assert form.form_vanishes_on(tuple(glue.elements()))
    assert form.orthogonal_subgroup(glue) == glue
    assert quotient.cardinality() == cardinal(1)
    assert descended.cardinality() == cardinal(1)
    assert inclusion.index() == 2
    assert inclusion.codomain().is_unimodular()


def test_discriminant_bilinear_isotropic_subgroups_and_duality_have_expected_sizes() -> None:
    _lattice, form, glue = _sign_pair_bilinear()
    duality = form.pontryagin_dual_identification()

    assert form.isotropic_subgroups().cardinality() == cardinal(2)
    assert form.lagrangian_subgroups().cardinality() == cardinal(1)
    assert form.maximal_isotropic_subgroups().cardinality() == cardinal(1)
    assert form.metabolizer() == glue
    assert not form.is_anisotropic()
    assert form.is_metabolic()
    assert form.is_isometric_to(form)
    assert form.is_isomorphic(form)
    assert all(duality(x)(y) == form.b(x, y) for x in form.elements() for y in form.elements())


def test_discriminant_bilinear_jordan_data_and_twist_preserve_the_form_type() -> None:
    _lattice, form, _glue = _sign_pair_bilinear()

    assert tuple(form.p_adic_jordan_decomposition().index_set()) == (ZZ(2),)
    assert form.p_adic_jordan_form().is_isomorphism()
    assert tuple(generator.additive_order() for generator in form.p_adic_jordan_module_generators()) == (2, 2)
    assert form.twist(-1) in TorsionBilinearFormModules(ZZ)
