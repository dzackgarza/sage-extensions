r"""Enumerating a finite discriminant module, and deciding its characteristic classes.

A finite discriminant module ``A = A_L`` has order ``|det L|``, and its classes
are the cosets of ``L`` in ``L^#``: ``q`` is the descended norm and ``b`` its
polar pairing, so ``q(a + a') = q(a) + q(a') + 2b(a, a')``.  The finite ordered
set built from a chosen enumeration refuses two equal points at two positions,
so an enumeration of ``|A|`` points lists every class exactly once, and one class
costs one class whatever the order of ``A``.

A class ``c`` is characteristic when ``b(c, a) = q(a)`` modulo ``1`` for every
class ``a``: H. Ito and H. Ohashi, *Classification of involutions on Enriques
surfaces*, arXiv:1302.2316v3, Section 2, p. 4.
"""

from sage_extensions.all import *


def _discriminant_module(rank: int):
    r"""Return ``A_{<2> + U(2)^rank}``, of order ``2^(2 rank + 1)``."""
    return (NamedLattices.Z_2 + NamedLattices.U_2**rank).discriminant_group()


def _enumerates_each_class_once(lattice) -> bool:
    r"""Whether ``A_L`` has order ``|det L|`` and is enumerated once per class.

    The order is read off the Gram matrix, so it is not the module's own
    answer, and the enumeration refuses two equal points at two positions.
    """
    module = lattice.discriminant_group()
    return (
        module.cardinality() == abs(int(lattice.gram_matrix().determinant()))
        and module.elements().cardinality() == module.cardinality()
    )


def test_a_two_elementary_discriminant_module_enumerates_each_class_once() -> None:
    r"""``A_{<2> + U(2)^rank}`` is enumerated once, for two ranks.

    ``|det(<2> + U(2)^rank)| = 2^(2 rank + 1)``, so the two enumerations are
    over 32 and 512 classes.
    """
    for rank in (2, 4):
        assert _enumerates_each_class_once(
            NamedLattices.Z_2 + NamedLattices.U_2**rank
        )


def test_a_cyclic_discriminant_module_of_order_4096_enumerates_each_class_once() -> None:
    r"""``A_{<4096>} = ZZ/4096`` is enumerated once: 4096 classes of one generator.

    The module is cyclic, so each of its classes is one coordinate of the
    module's generator: the enumeration is decided by the classes, not by the
    rank of the lattice.
    """
    assert _enumerates_each_class_once(Lattices(ZZ)([[4096]]))


def test_a_class_is_characteristic_exactly_when_the_definition_says_so() -> None:
    r"""``is_characteristic`` agrees with the definition on ``A_{<2> + U(2)^rank}``.

    The definition is read over every class, for two ranks, so neither the
    positive nor the negative answers come from the decision procedure under
    test.
    """
    for rank in (0, 1):
        module = _discriminant_module(rank)
        classes = tuple(module.elements())
        quadratic_values = tuple(module.q(a).lift() for a in classes)
        for candidate in classes:
            assert candidate.is_characteristic() == all(
                quadratic_values[position] - module.b(a, candidate).lift() in ZZ
                for position, a in enumerate(classes)
            )


def test_the_zero_class_is_not_characteristic_when_the_norm_is_not_integer_valued() -> None:
    r"""On ``A_{<2> + U(2)^5}`` a generator has norm ``1/2``, so the zero class is not characteristic.

    ``b(0, a)`` vanishes for every class ``a``, so the zero class is
    characteristic exactly when ``q`` is integer-valued on ``A``.  The
    exhibited generator has ``q = 1/2``, which decides the zero class without
    asking about any other class.
    """
    module = _discriminant_module(5)
    assert any(
        module.q(generating_class).lift() == QQ(1) / QQ(2)
        for generating_class in module.module_generators()
    )
    assert module.zero().is_characteristic() is False
