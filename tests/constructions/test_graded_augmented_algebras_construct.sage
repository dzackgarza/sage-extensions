r"""A connected polynomial grading has its canonical augmentation to degree zero."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_algebra_has_the_connected_graded_augmentation() -> None:
    algebra = QQ.free_module(("x", "y")).symmetric_algebra()
    category = GradedAugmentedAlgebras(QQ, algebra.grading_monoid())
    augmentation = algebra.ground_ring_augmentation()

    assert algebra in category
    assert augmentation(algebra.one()) == QQ.one()
    assert augmentation(algebra.algebra_generator("x")) == QQ.zero()
    assert augmentation(algebra.algebra_generator("y")) == QQ.zero()

