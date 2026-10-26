r"""A surjection of finite groups admits one chosen lift for each image element."""

from sage_extensions.all import *  # noqa: F401,F403


def test_reduction_c4_to_c2_has_lifts_of_every_target_element() -> None:
    four = Groups.C(4)
    two = Groups.C(2)
    generator = four.group_generators()[0]
    target = two.group_generators()[0]
    reduction = four.Mor(two)({generator: target})
    lifts = four.finite_image_lifts(reduction)

    assert set(lifts) == set(two)
    assert all(reduction(witness) == image for image, witness in lifts.items())
