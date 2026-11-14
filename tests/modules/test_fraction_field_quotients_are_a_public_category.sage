r"""``FractionFieldQuotients`` is a public session name and answers as one.

``FractionFieldQuotients(R)(a)`` is the module ``Frac(R) / a`` for a fractional
ideal ``a``; the class declares itself in its module's ``__all__``, the formed
and discriminant module owners place their value modules in it, and the session
module did not re-export it — so a consumer could not name the category its own
discriminants take values in.

The object ``Frac(R)/R`` is spelled ``FractionFieldQuotients(R)()`` (its
``an_object``), and its elements are classes of ``Frac(R)`` modulo ``a``: they
add and scale, ``a`` itself is zero, and two representatives agree exactly when
they differ by an element of ``a``.
"""

from sage_extensions.all import FractionFieldQuotients, QQ, ZZ


def _half():
    one = QQ.one()
    return one / (one + one)


def test_the_category_is_reachable_from_the_session() -> None:
    quotient = FractionFieldQuotients(ZZ)()

    assert quotient in FractionFieldQuotients(ZZ)


def test_the_defining_quotient_relation() -> None:
    quotient = FractionFieldQuotients(ZZ)()
    zero = quotient.zero()
    half = quotient(_half())

    # ``a`` is zero in Frac(R)/a; here a = (1) = ZZ, so the integers vanish.
    assert quotient(ZZ.one() + ZZ.one()) == zero
    assert half + half == zero
    assert -half == half
    # Representatives agree exactly when they differ by an element of a.
    one = QQ.one()
    assert quotient(_half() + one) == half
    assert quotient(one - _half()) == -half


def test_scalars_act_through_the_base_ring() -> None:
    quotient = FractionFieldQuotients(ZZ)()
    half = quotient(_half())

    assert quotient.scalar_multiple(ZZ.one() + ZZ.one(), half) == quotient.zero()
    assert quotient.scalar_multiple(ZZ.one(), half) == half
