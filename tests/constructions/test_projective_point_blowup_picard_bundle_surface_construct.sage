r"""The point blowup of (mathbf P^2) retains the standard Picard pullback and canonical bundle formula."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_point_blowup_source_picard_group_and_line_bundle_pullback() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    blowup = ProjectivePointBlowups(QQ)(plane.point_morphism((1, 1, 1)))
    source_picard = blowup.source_picard_group()
    hyperplane = blowup.hyperplane_picard_class()
    pulled_hyperplane = blowup.pullback_line_bundle(plane.O(1))

    assert source_picard.module_rank() == cardinal(1)
    assert blowup.picard_group().module_rank() == cardinal(2)
    source_generator = source_picard.module_generator(
        next(iter(source_picard.module_generating_set()))
    )
    assert blowup.picard_pullback_morphism()(source_generator) == hyperplane
    assert pulled_hyperplane == blowup.graph_ambient_product().O(1, 0).restrict_to(blowup)


def test_point_blowup_exceptional_and_canonical_line_bundles_satisfy_blowup_formula() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    blowup = ProjectivePointBlowups(QQ)(plane.point_morphism((1, 1, 1)))
    exceptional = blowup.exceptional_line_bundle()
    pulled_canonical = blowup.pulled_back_source_canonical_bundle()
    comparison = blowup.canonical_comparison()

    assert exceptional == blowup.graph_ambient_product().O(1, -1).restrict_to(blowup)
    assert pulled_canonical == blowup.graph_ambient_product().O(-3, 0).restrict_to(blowup)
    assert comparison.domain() == blowup.canonical_line_bundle()
    assert comparison.codomain() == pulled_canonical.tensor_product(exceptional)


def test_picard_group_operation_is_owned_by_ringed_spaces() -> None:
    ringed_space = RingedSpaces().an_object()

    assert ringed_space in RingedSpaces()
    assert ringed_space not in ProjectivePointBlowups(ZZ)
    with pytest.raises(AssertionError, match="group of isomorphism classes"):
        ringed_space.picard_group()
