r"""Weil divisors and divisor classes are owned by locally Noetherian integral schemes."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_projective_and_toric_class_groups_inherit_the_common_owner() -> None:
    field = GF(5)
    owner = Schemes(field).LocallyNoetherian().Integral()
    affine_plane = AffineSpaces(field)(2)
    projective_plane = ProjectiveSpaces(field)(2)
    fan = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan()
    toric_plane = fan.toric_variety(field)

    assert affine_plane in owner
    assert projective_plane in owner
    assert toric_plane in owner
    assert affine_plane.class_group().order() == 1
    assert projective_plane.class_group().module_rank() == 1
    assert toric_plane.class_group().module_rank() == 1
    assert projective_plane.picard_to_class_group_morphism().is_isomorphism()


def test_defined_class_operations_survive_when_no_computation_is_selected() -> None:
    polynomial = QQ.polynomial_ring(("x", "y"))
    x, y = polynomial.algebra_generators()
    scheme = Curves(QQ).from_equation(y**2 - x**3)
    owner = Schemes(QQ).LocallyNoetherian().Integral()

    assert scheme in owner
    assert scheme not in Schemes(QQ).Normal()
    assert hasattr(scheme, "full_weil_divisor_group")
    assert hasattr(scheme, "class_group")
    assert hasattr(scheme, "picard_to_class_group_morphism")
    with pytest.raises(AssertionError, match="requires normality"):
        scheme.full_weil_divisor_group()
    with pytest.raises(AssertionError, match="quotient presentation"):
        scheme.class_group()
    with pytest.raises(AssertionError, match="Cartier-to-Weil"):
        scheme.picard_to_class_group_morphism()
