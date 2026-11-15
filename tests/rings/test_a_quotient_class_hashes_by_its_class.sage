r"""A class hashes through a representative the engine selects, or not at all.

:meth:`QuotientRings.ElementMethods._richcmp_` decides equality of two classes by
membership of their difference in the defining ideal, so ``1`` and ``4`` are one
class of ``ZZ/(3)``.  A class hashes through a representative the engine selects
one per class -- the residues of ``ZZ/(n)``, or a normal form over a polynomial
cover whose coefficient ring is an exact field -- so equal classes given
different lifts hash equally, and distinct classes of one modulus hash apart.
Over ``ZZ``, and over a cover that is no polynomial ring, no representative is
selected, so a class there refuses a hash instead of separating classes its
equality identifies.

Without the hash, every set of vectors over ``ZZ/(n)`` is unhashable, and the
cache of ``_lattice_subobject_spanning`` cannot be keyed by a span basis over
``ZZ/(3)``.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_classes_with_different_lifts_are_one_key() -> None:
    r"""``1`` and ``4`` are one class of ``ZZ/(3)``, and one dictionary key."""
    ring = GF(3)
    lifted = ring(1)
    relifted = ring(4)
    table = {lifted: cardinal(1), relifted: cardinal(2)}

    assert lifted == relifted
    assert hash(lifted) == hash(relifted)
    assert cardinal(sum(1 for _ in table)) == cardinal(1)
    assert table[relifted] == cardinal(2)


def test_distinct_classes_of_one_modulus_hash_apart() -> None:
    r"""The classes of ``1`` and of ``2`` in ``ZZ/(3)`` are different sets of lifts."""
    ring = GF(3)
    first = ring(1)
    second = ring(2)

    assert first != second
    assert hash(first) != hash(second)
    assert cardinal(sum(1 for _ in {first: cardinal(0), second: cardinal(1)})) == cardinal(2)


def test_a_class_over_zz_refuses_a_hash_because_reduction_is_no_normal_form() -> None:
    r"""Over ``ZZ``, one class has many engine representatives, so it has no hash.

    In ``ZZ[x,y]/(4, 6x)`` the classes of ``x`` and of ``3x`` are equal, since
    \(2x = 6x - 4x\) lies in the ideal.  Sage's representative of the two is
    ``xbar`` and ``-xbar``: over a coefficient ring that is not a field
    ``ideal.reduce`` returns the representative it was given, so a hash of the
    representative is a hash of the lift.
    """
    polynomials = ZZ.polynomial_ring("x,y")
    x = polynomials.algebra_generator("x")
    quotient = polynomials.quotient_ring(polynomials.ideal(ZZ(4), ZZ(6) * x))
    lifted = quotient(x)
    relifted = quotient(ZZ(3) * x)

    assert lifted == relifted
    with pytest.raises(TypeError):
        hash(lifted)
    with pytest.raises(TypeError):
        hash(relifted)


def test_classes_of_a_laurent_quotient_refuse_a_hash() -> None:
    r"""A Laurent cover reduces no representative, so a class of its quotient has no hash.

    In ``QQ[t^{\pm 1}]/(t - 1)`` the classes of ``t`` and of ``1`` are equal.
    ``reduce`` over a Laurent polynomial ring is not a normal form -- it returns
    the representative it was given -- so the two classes would carry two hashes,
    and the class refuses one instead.
    """
    laurent = QQ.laurent_polynomial_ring("t")
    t = laurent.algebra_generator("t")
    quotient = laurent.quotient_ring(laurent.ideal(t - laurent.one()))
    lifted = quotient(t)
    relifted = quotient(laurent.one())

    assert lifted == relifted
    with pytest.raises(TypeError):
        hash(lifted)
    with pytest.raises(TypeError):
        hash(relifted)


def test_classes_of_a_polynomial_quotient_over_a_field_hash_through_its_normal_form() -> None:
    r"""``QQ[x,y]/(x^2 + y)`` does select a representative: the two classes agree.

    The cover is a multivariate polynomial ring over an exact field, whose
    ``reduce`` is Singular's normal form with respect to a Gröbner basis, so the
    lifts ``x`` and ``x - (x^2 + y)`` are one class with one hash.
    """
    polynomials = QQ.polynomial_ring("x,y")
    x = polynomials.algebra_generator("x")
    y = polynomials.algebra_generator("y")
    quotient = polynomials.quotient_ring(polynomials.ideal(x**2 + y))
    lifted = quotient(x)
    relifted = quotient(x - (x**2 + y))

    assert lifted == relifted
    assert hash(lifted) == hash(relifted)
