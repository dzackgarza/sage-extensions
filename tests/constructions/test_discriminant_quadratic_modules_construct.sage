r"""Discriminant quadratic modules retain even-lattice glue and Brown data.

For ``L=<2>+<-2>`` the diagonal class is an isotropic characteristic class.
It is Lagrangian, its orthogonal quotient is zero, and gluing it produces an
even unimodular index-two overlattice.  The Brown invariant is the signature
``(1-1)=0`` modulo eight.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _sign_pair_quadratic():
    lattice = Lattices(ZZ)([[2]]) + Lattices(ZZ)([[-2]])
    form = lattice.discriminant_quadratic_form()
    first, second = form.module_generators()
    characteristic = first + second
    glue = form.subgroup_on((characteristic,))
    return lattice, form, characteristic, glue


def test_discriminant_quadratic_form_polarizes_and_has_brown_invariant_zero() -> None:
    _lattice, form, characteristic, _glue = _sign_pair_quadratic()
    bilinear = form.associated_bilinear_form()

    assert form in DiscriminantQuadraticModules(ZZ)
    assert form.quadratic_value_module() is form.value_module()
    assert form.brown_invariant() == 0
    assert form.q(characteristic) == form.value_module().zero()
    assert characteristic.is_characteristic()
    assert bilinear in DiscriminantBilinearModules(ZZ)
    assert form.invariant_factor_form().is_isomorphism()
    assert form.normal_form().is_isomorphism()


def test_discriminant_quadratic_glue_has_zero_descended_form_and_even_unimodular_overlattice() -> None:
    _lattice, form, _characteristic, glue = _sign_pair_quadratic()
    quotient = form.orthogonal_quotient(glue)
    descended = form.discriminant_form_of_overlattice(glue)
    inclusion = form.overlattice_from_isotropic_subobject(glue)

    assert glue.cardinality() == cardinal(2)
    assert form.form_vanishes_on(tuple(glue.elements()))
    assert quotient.cardinality() == cardinal(1)
    assert descended.cardinality() == cardinal(1)
    assert inclusion.index() == 2
    assert inclusion.codomain().is_even()
    assert inclusion.codomain().is_unimodular()


def test_discriminant_quadratic_isotropic_subgroups_metabolism_and_orthogonal_group() -> None:
    _lattice, form, _characteristic, glue = _sign_pair_quadratic()

    assert form.isotropic_elements().cardinality() == cardinal(2)
    assert form.isotropic_subgroups().cardinality() == cardinal(2)
    assert form.lagrangian_subgroups().cardinality() == cardinal(1)
    assert form.maximal_isotropic_subgroups().cardinality() == cardinal(1)
    assert form.metabolizer() == glue
    assert not form.is_anisotropic()
    assert form.is_metabolic()
    assert form.is_isometric_to(form)
    assert form.is_isomorphic(form)
    assert form.O() == form.orthogonal_group()
    assert form.automorphism_group() == form.O()


def test_discriminant_quadratic_jordan_data_and_twist_remain_quadratic_forms() -> None:
    _lattice, form, _characteristic, _glue = _sign_pair_quadratic()

    assert tuple(form.p_adic_jordan_decomposition().index_set()) == (ZZ(2),)
    assert form.p_adic_jordan_form().is_isomorphism()
    assert tuple(generator.additive_order() for generator in form.p_adic_jordan_module_generators()) == (2, 2)
    assert form.twist(-1) in TorsionQuadraticFormModules(ZZ)
