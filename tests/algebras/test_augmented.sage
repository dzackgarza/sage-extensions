r"""Augmentations of the polynomial algebra by evaluation at a point."""

from sage_extensions.all import *  # noqa: F401,F403


def test_augmentation_ideal_of_evaluation_at_one_is_generated_by_x_minus_one() -> None:
    r"""``ker(ev_1 : QQ[x] -> QQ) = (x - 1)``.

    Derivation: division by the monic ``x - 1`` gives ``f = (x - 1) q + f(1)``.
    """
    polynomials = QQ["x"]
    x = polynomials.gen()
    at_one = polynomials.Mor(QQ)({x: QQ(1)})
    augmentation_ideal = at_one.kernel()

    assert at_one(x**3 - 2 * x) == QQ(-1)
    assert x - 1 in augmentation_ideal
    assert x**2 - 1 in augmentation_ideal
    assert x not in augmentation_ideal
    assert augmentation_ideal == polynomials.ideal([x - 1])
