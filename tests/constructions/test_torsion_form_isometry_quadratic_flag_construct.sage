r"""Finite-form reframing isometries retain whether they preserve quadratic or bilinear data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_quadratic_reframing_isometry_is_marked_quadratic() -> None:
    form = NamedLattices.U.twist(2).discriminant_quadratic_form()
    isometry = form.reframing_isometry(tuple(form.module_generators()))

    assert isometry.is_quadratic()


def test_bilinear_reframing_isometry_is_not_marked_quadratic() -> None:
    form = NamedLattices.U.twist(2).discriminant_bilinear_form()
    isometry = form.reframing_isometry(tuple(form.module_generators()))

    assert not isometry.is_quadratic()
