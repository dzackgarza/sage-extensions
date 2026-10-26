import pytest

from sage_extensions.all import *


def test_u2_quadratic_and_bilinear_forms_have_actual_metabolizers() -> None:
    quadratic = NamedLattices.U_2.discriminant_group()
    bilinear = quadratic.associated_bilinear_form()

    quadratic_metabolizer = quadratic.metabolizer()
    bilinear_metabolizer = bilinear.metabolizer()

    assert quadratic_metabolizer.cardinality() == 2
    assert bilinear_metabolizer.cardinality() == 2
    assert quadratic.orthogonal_subgroup(quadratic_metabolizer).cardinality() == 2
    assert bilinear.orthogonal_subgroup(bilinear_metabolizer).cardinality() == 2
    assert quadratic.is_metabolic()
    assert bilinear.is_metabolic()


def test_anisotropic_a1_discriminant_has_no_metabolizer() -> None:
    quadratic = NamedLattices.A1.discriminant_group()

    assert not quadratic.is_metabolic()
    with pytest.raises(ValueError):
        quadratic.metabolizer()
