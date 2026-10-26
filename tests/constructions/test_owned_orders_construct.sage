r"""The Gaussian integers are the maximal order in Q(i)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_gaussian_integers_are_a_maximal_owned_order() -> None:
    field = QuadraticField(-1, "i")
    order = field.ring_of_integers()
    identity = order.Mor(order).identity()

    assert order in OwnedOrders()
    assert order.is_maximal()
    assert order.fraction_field() is field
    assert order.module_rank() == field.degree()
    assert order.integral_basis().cardinality() == cardinal(2)
    assert identity(order.one()) == order.one()

