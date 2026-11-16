r"""Classes of a tensor product without a chosen framing hash by their equality.

The tensor product of two modules over a commutative ring is the quotient of
the free module on the product by additivity and linearity in each slot, and a
class is represented by a finite sum of pure tensors.  Equality is that the
reduced difference vanishes, and the reduced form keeps the summands in the
order they were supplied, so ``x (x) y + z (x) w`` and ``z (x) w + x (x) y``
are one class whose term tuples differ.  The quotient is what a hash reads, and
equal classes hash alike, which is the rule of :class:`Sets`.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_orders_of_one_sum_of_pure_tensors_are_one_point() -> None:
    r"""``QQ (x)_ZZ QQ``: the sum ``1 (x) 1 + 2 (x) 1`` does not depend on the order.

    ``QQ`` is not a finitely generated ``ZZ``-module, so this tensor product is
    the generators-and-relations quotient rather than a framed free module.  The
    two sums below reduce to term tuples in the two orders and are one class.
    """
    rationals = Modules(ZZ)(QQ)
    classes = Modules(ZZ).tensor_product((rationals, rationals)).underlying_set()
    one_one = classes.pure((rationals(QQ(1)), rationals(QQ(1))))
    two_one = classes.pure((rationals(QQ(2)), rationals(QQ(1))))

    forward = classes.add(one_one, two_one)
    backward = classes.add(two_one, one_one)

    assert forward == backward
    assert hash(forward) == hash(backward)
    assert FiniteOrderedSets()((forward, backward)).cardinality() == 1
    assert FiniteOrderedSets()((one_one,)).cardinality() == 1
    assert hash(one_one) == hash(classes.pure((rationals(QQ(1)), rationals(QQ(1)))))
