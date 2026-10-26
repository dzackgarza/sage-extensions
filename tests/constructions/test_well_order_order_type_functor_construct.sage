r"""The order-type functor sends a finite well-order to its finite ordinal."""

from sage_extensions.all import *  # noqa: F401,F403


def test_three_element_well_order_has_order_type_three() -> None:
    well_orders = WellOrderedSets()
    three = well_orders.an_object()
    order_type = well_orders.order_type_functor()

    assert order_type.domain() is well_orders.Core()
    assert order_type.codomain() is Ordinals()
    assert order_type(three) == Ordinals()(3)
