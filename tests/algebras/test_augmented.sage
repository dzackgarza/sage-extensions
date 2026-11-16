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


def test_the_witness_augmented_algebra_is_the_polynomial_algebra_at_zero() -> None:
    r"""``AugmentedAlgebras(ZZ).an_object()`` is ``Sym_Z(Z)`` with ``x |-> 0``.

    The witness is the polynomial algebra on one generator, augmented by
    evaluation at zero: the generator and every positive-degree word die, and
    the unit survives.  Its retained generating module is the input of ``Sym``,
    the module ``Z x``, not the sum of its graded pieces.
    """
    augmented = AugmentedAlgebras(ZZ).an_object()
    x = augmented.algebra_generator("x")

    assert augmented.augmentation()(augmented.one()) == ZZ(1)
    assert augmented.augmentation()(x) == ZZ(0)
    assert augmented.augmentation()(x**2) == ZZ(0)
    assert x**2 in augmented
    assert augmented.generating_module() is ZZ.free_module(("x",))
    assert augmented.is_augmented() is True


def test_the_identity_of_an_augmented_algebra_is_the_identity_map() -> None:
    r"""The identity of ``Gamma(Z[x])`` as an augmented algebra is its identity map.

    An arrow of ``AugmentedAlgebras(Z)`` is an algebra map that preserves the
    chosen augmentation, so the identity arrow is the identity of the
    underlying algebra, it fixes every element, and it belongs to the Mor it
    was asked of: the commuting square it is defined by is one that Mor holds.
    """
    generating_module = ZZ.free_module(("x",))
    gamma = DividedPowerAlgebras(ZZ)(generating_module)
    mor = AugmentedAlgebras(ZZ).Mor(gamma, gamma)
    identity = mor.identity()
    generator = gamma.algebra_generator("x")

    assert identity.parent() is mor
    assert identity in mor
    assert identity(generator) == generator
    assert identity.underlying_arrow() == (
        Algebras(ZZ).Associative().Unital().Mor(gamma, gamma).identity()
    )
