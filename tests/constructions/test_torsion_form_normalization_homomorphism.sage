r"""Finite torsion-form normalization is a homomorphism from the formed Core."""

from sage_extensions.all import *  # noqa: F401,F403


def test_quadratic_normalization_maps_the_form_core_identity_to_the_finite_identity() -> None:
    form = NamedLattices.U.twist(2).discriminant_quadratic_form()
    orthogonal = form.orthogonal_group()
    core = TorsionQuadraticFormModules(ZZ).Core().Mor(form, form)
    normalization = orthogonal.normalization_homomorphism()

    assert normalization.domain() is core
    assert normalization.codomain() is orthogonal
    assert normalization(core.identity()) == orthogonal.identity()
