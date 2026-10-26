r"""Humphreys' finite Weyl-group orders retained from the archive gap map.

Humphreys, *Reflection Groups and Coxeter Groups* (1990), section 2.11,
tabulates the orders below.  These assertions use the live owned Weyl-group
catalogue; the literature values are the independent oracle rather than a
recomputation from the same backend representation.
"""

from sage_extensions.all import *

WEYL_ORDERS = {
    ("A", 2): 6,
    ("A", 4): 120,
    ("D", 4): 192,
    ("E", 6): 51840,
    ("E", 7): 2903040,
    ("E", 8): 696729600,
}


def test_finite_weyl_group_orders_match_humphreys() -> None:
    for cartan_type, expected_order in WEYL_ORDERS.items():
        group = Groups.Weyl(list(cartan_type))
        assert group.order() == expected_order
