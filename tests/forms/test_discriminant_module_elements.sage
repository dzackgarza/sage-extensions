r"""Enumerating a finite discriminant module, and deciding its characteristic classes.

A finite discriminant module ``A = A_L`` has order ``|det L|``, and its classes
are the cosets of ``L`` in ``L^#``: ``q`` is the descended norm and ``b`` its
polar pairing, so ``q(a + a') = q(a) + q(a') + 2b(a, a')``.  The finite ordered
set built from a chosen enumeration refuses two equal points at two positions,
so an enumeration of ``|A|`` points lists every class exactly once, and one class
costs one class whatever the order of ``A``.

A class ``c`` is characteristic when ``b(c, a) = q(a)`` modulo ``1`` for every
class ``a``: H. Ito and H. Ohashi, *Classification of involutions on Enriques
surfaces*, arXiv:1302.2316v3, Section 2, p. 4.  Reading that condition over a
generating family rather than over every class is a consequence of ``2b`` being
integer-valued, which makes ``q`` modulo the integers a homomorphism.  The
hypothesis is not free: it holds on ``A_{<2> + U(2)^rank}`` and fails on
``<4>``, ``[[2, 1], [1, 2]]`` and ``<2> + <6>``, and each of those is exhibited
against the definition.
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


def _doubled_pairing_is_integral(module) -> bool:
    r"""Whether ``2 b(a, a')`` is an integer for every pair of classes of ``module``.

    This is the hypothesis a characteristic class needs, read as the definition
    of the pairing states it: over every pair of classes, not from a generating
    family.
    """
    classes = tuple(module.elements())
    return all(
        2 * module.b(left, right).lift() in ZZ
        for left in classes
        for right in classes
    )


def _characteristic_by_the_definition(module):
    r"""The classes ``c`` of ``module`` with ``q(a) - b(a, c)`` an integer for every ``a``.

    The definition is read over the whole module, and it short-circuits: a
    class that is not characteristic is decided by its first witness, and only
    a characteristic one is read against all ``|A|`` classes.
    """
    classes = tuple(module.elements())
    return tuple(
        candidate
        for candidate in classes
        if all(
            module.q(a).lift() - module.b(a, candidate).lift() in ZZ
            for a in classes
        )
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


def test_the_doubled_polar_form_is_integral_exactly_when_a_class_is_characteristic() -> None:
    r"""The module decides ``2b``, and a characteristic class exists exactly then.

    ``q`` modulo the integers is a homomorphism ``A -> QQ/ZZ`` exactly when
    ``2b`` is integer-valued, and ``b`` is nondegenerate on a discriminant
    module, so ``b(c, .) = q`` has a solution exactly on those modules.  The
    decision belongs to the module and is not the element's: it is asked of
    the module here as well as being implied by the definition, on specimens
    where the hypothesis holds and on specimens where it fails.
    """
    for lattice in (
        NamedLattices.Z_2,
        NamedLattices.U_2,
        Lattices(ZZ)([[4]]),
        Lattices(ZZ)([[2, 1], [1, 2]]),
        Lattices(ZZ)([[2, 0], [0, 6]]),
    ):
        module = lattice.discriminant_quadratic_form()
        integral = _doubled_pairing_is_integral(module)
        assert module.has_integral_doubled_polar_form() is integral
        assert bool(_characteristic_by_the_definition(module)) is integral


def test_a_class_is_characteristic_exactly_when_the_definition_says_so() -> None:
    r"""``is_characteristic`` agrees with the definition, for every class.

    Two ranks of ``A_{<2> + U(2)^rank}`` carry the hypothesis and three
    lattices violate it, so an implementation that reads a generating family
    without asking whether ``2b`` is integer-valued answers wrongly here: on
    ``<4>``, on ``[[2, 1], [1, 2]]`` and on ``<2> + <6>`` a generating family
    agrees with ``q`` on a class that the definition rejects.
    """
    for lattice in (
        NamedLattices.Z_2 + NamedLattices.U_2,
        NamedLattices.Z_2 + NamedLattices.U_2**2,
        Lattices(ZZ)([[4]]),
        Lattices(ZZ)([[2, 1], [1, 2]]),
        Lattices(ZZ)([[2, 0], [0, 6]]),
    ):
        module = lattice.discriminant_quadratic_form()
        classes = tuple(module.elements())
        assert (
            tuple(candidate for candidate in classes if candidate.is_characteristic())
            == _characteristic_by_the_definition(module)
        )


def test_the_quadratic_generating_class_of_the_rank_four_module_is_characteristic() -> None:
    r"""On ``A_{<2> + U(2)^4}`` the ``<2>`` generating class is characteristic.

    Its norm is ``1/2``, and the definition is asked of it directly, over all
    512 classes of the module: ``q(a) - b(a, c)`` is an integer for every
    class ``a``.  A decision that drops the hypothesis it relies on, or one
    that answers no everywhere, is wrong on this specimen at the order the
    enumeration test is read at.
    """
    module = _discriminant_module(4)
    classes = tuple(module.elements())
    quadratic_class = next(
        generating_class
        for generating_class in module.module_generators()
        if module.q(generating_class).lift() == QQ(1) / QQ(2)
    )
    assert module.has_integral_doubled_polar_form() is True
    assert quadratic_class.is_characteristic() is True
    assert all(
        module.q(a).lift() - module.b(a, quadratic_class).lift() in ZZ
        for a in classes
    )


def test_the_isotropic_generating_classes_of_the_rank_four_module_are_not_characteristic() -> None:
    r"""The eight isotropic generating classes of ``A_{<2> + U(2)^4}`` are not characteristic.

    A class of norm zero pairs trivially with ``q`` on its own class and could
    be characteristic only by pairing as ``q`` everywhere else, which the
    definition denies: each of these is read against all 512 classes until its
    first witness, and the decision has to answer as the definition does.
    """
    module = _discriminant_module(4)
    classes = tuple(module.elements())
    isotropic_classes = tuple(
        generating_class
        for generating_class in module.module_generators()
        if module.q(generating_class).lift() in ZZ
    )
    assert module.has_integral_doubled_polar_form() is True
    assert sum(1 for candidate in isotropic_classes) == 8
    for candidate in isotropic_classes:
        assert candidate.is_characteristic() is all(
            module.q(a).lift() - module.b(a, candidate).lift() in ZZ
            for a in classes
        )


def test_a_characteristic_class_costs_about_one_evaluation_per_generating_class() -> None:
    r"""One decision costs about eleven evaluations of ``q`` and ``b``.

    On ``A_{<2> + U(2)^5}`` -- 2048 classes, eleven generating classes -- the
    yardstick is measured in this process by evaluating ``q`` and ``b`` once
    per generating class, so the assertion is the ratio the decision is
    supposed to hold and not a wall time of one host.  A decision that reads
    the module's classes instead costs one evaluation per class of the module.
    """
    module = _discriminant_module(5)
    generating_classes = tuple(module.module_generators())
    candidate = generating_classes[3] + generating_classes[7]
    start = cputime()
    for generating_class in generating_classes:
        module.q(generating_class)
        module.b(generating_class, candidate)
    yardstick = cputime(start)
    start = cputime()
    candidate.is_characteristic()
    decision = cputime(start)
    assert decision <= yardstick


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
