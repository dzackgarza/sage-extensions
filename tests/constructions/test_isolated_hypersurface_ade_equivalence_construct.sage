r"""An A1 normal form is linearly right-equivalent to itself."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_normal_form_and_identity_linear_right_equivalence() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    node = IsolatedHypersurfaceSingularity(ring, x**2 + y**2)
    identity_images = (x, y)
    equivalence = node.linear_right_equivalence_to(
        node, identity_images, identity_images
    )

    assert node.ade_normal_form_type() == "A1"
    assert node.ade_type_via_linear_right_equivalence(
        identity_images, identity_images
    ) == "A1"
    assert equivalence.source() is node
    assert equivalence.target() is node
