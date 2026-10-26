r"""Archive reconciliation for the shared finite-Coxeter order oracle.

The archived ``coxeter_tdd_specs/conftest.py`` carried two things: a path
fixture into the retired test-data checkout, and the literature order table
below.  The path fixture has no mathematical content and is not reproduced.
The order table is retained against the live owned Coxeter-group constructor.

For the crystallographic types these orders agree with Humphreys,
*Reflection Groups and Coxeter Groups*, §2.11.  The noncrystallographic
``H`` and dihedral ``I_2(m)`` entries are the standard finite Coxeter-group
orders used by the archived literature corpus.
"""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/tests/coxeter_tdd_specs/conftest.py",
    "live_owner": "tests/groups/test_coxeter_finite_orders_archive.py",
    "owner_overrides": {
        "test_data_dir": "tests/lattices/test_coxeter_literature.py",
    },
    "disposition": "reconciled-live-owner",
}

FINITE_COXETER_ORDERS = {
    ("A", 1): 2,
    ("A", 2): 6,
    ("A", 3): 24,
    ("A", 4): 120,
    ("B", 2): 8,
    ("B", 3): 48,
    ("B", 4): 384,
    ("C", 2): 8,
    ("C", 3): 48,
    ("C", 4): 384,
    ("D", 4): 192,
    ("D", 5): 1920,
    ("E", 6): 51840,
    ("E", 7): 2903040,
    ("E", 8): 696729600,
    ("F", 4): 1152,
    ("G", 2): 12,
    ("H", 3): 120,
    ("H", 4): 14400,
    ("I", 3): 6,
    ("I", 4): 8,
    ("I", 5): 10,
    ("I", 6): 12,
}


def test_archived_finite_coxeter_orders_use_the_live_owned_groups() -> None:
    for cartan_type, expected_order in FINITE_COXETER_ORDERS.items():
        group = Groups.Coxeter(list(cartan_type))
        assert group.order() == expected_order


def test_archived_exceptional_order_oracles_include_large_nonclassical_cases() -> None:
    assert Groups.Coxeter(["H", 4]).order() == FINITE_COXETER_ORDERS[("H", 4)] == 14400
    assert Groups.Coxeter(["E", 8]).order() == FINITE_COXETER_ORDERS[("E", 8)] == 696729600
