r"""Archive reconciliation for selected direct-sum decompositions.

The archived wrapper could attach a claimed decomposition to an arbitrary object.
The live owner makes the stronger constructor contract: the object itself must
already carry the selected indexed summands, and ``DirectSumDecomposition`` only
verifies that retained mathematical datum.
"""

import pytest

from sage_extensions.all import (
    ZZ,
    DirectSumObjects,
    Lattices,
)

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/abstract_categories/direct_sum_objects.sage",
    "live_owner": "sage_extensions/categories/abstract_categories/direct_sum_objects.py",
    "disposition": "reconciled-live-owner",
}


def test_constructor_owned_direct_sum_retains_its_indexed_summands() -> None:
    left = Lattices(ZZ)("U")
    right = Lattices(ZZ)("A2")
    lattice = left + right

    assert lattice in DirectSumObjects(Lattices(ZZ))
    assert lattice.summand_index_set() is lattice.summands().index_set()
    assert lattice.summand(0) is left
    assert lattice.summand(1) is right
    assert DirectSumObjects(Lattices(ZZ)).verify_decomposition(lattice, lattice.summands()) is lattice


def test_post_hoc_fake_decomposition_is_not_an_owned_direct_sum() -> None:
    plane = Lattices(ZZ)("U")
    line = Lattices(ZZ)("A1")

    assert plane not in DirectSumObjects(Lattices(ZZ))
    with pytest.raises(ValueError):
        DirectSumObjects(Lattices(ZZ)).verify_decomposition(plane, (line, line))


def test_selected_summands_cannot_be_replaced_by_isomorphic_copies() -> None:
    left = Lattices(ZZ)("U")
    right = Lattices(ZZ)("A2")
    lattice = left + right
    replacement = Lattices(ZZ)("A2")

    assert replacement is not right
    with pytest.raises(ValueError):
        DirectSumObjects(Lattices(ZZ)).verify_decomposition(lattice, (left, replacement))
