from sage_extensions.all import *


def test_u2_quadratic_maximal_isotropic_subgroups_are_its_two_lagrangians() -> None:
    quadratic = NamedLattices.U_2.discriminant_group()
    maximal = quadratic.maximal_isotropic_subgroups()

    assert maximal.cardinality() == 2
    assert all(subgroup.cardinality() == 2 for subgroup in maximal)
    assert all(subgroup in quadratic.lagrangian_subgroups() for subgroup in maximal)


def test_u2_bilinear_form_has_three_maximal_isotropic_lines() -> None:
    bilinear = NamedLattices.U_2.discriminant_group().associated_bilinear_form()
    maximal = bilinear.maximal_isotropic_subgroups()

    assert maximal.cardinality() == 3
    assert all(subgroup.cardinality() == 2 for subgroup in maximal)
    assert all(subgroup in bilinear.lagrangian_subgroups() for subgroup in maximal)
