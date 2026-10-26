r"""Algebraic cycles are owned by locally Noetherian schemes, not affine schemes."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_cycle_computation_is_an_inherited_private_case() -> None:
    plane = AffineSpaces(QQ)(2)

    assert plane in Schemes(QQ).LocallyNoetherian()
    cycles = plane.cycle_group(1)
    assert cycles.cycle_scheme() is plane
    assert cycles.cycle_dimension() == 1


def test_nonaffine_locally_noetherian_scheme_keeps_cycle_operations() -> None:
    plane = ProjectiveSpaces(QQ)(2)

    assert plane in Schemes(QQ).LocallyNoetherian().Integral()
    assert plane not in Schemes(QQ).Affine()
    assert hasattr(plane, "cycle_group")
    assert hasattr(plane, "weil_cycle_isomorphism")
    with pytest.raises(AssertionError, match="represented family"):
        plane.cycle_group(1)
    with pytest.raises(AssertionError, match="compatible represented groups"):
        plane.weil_cycle_isomorphism()
