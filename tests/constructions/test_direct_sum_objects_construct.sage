r"""A selected lattice direct sum retains its indexed summands as defining data."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_lattice_direct_sum_retains_its_selected_summands() -> None:
    left = Lattices(ZZ)("U")
    right = Lattices(ZZ)("A2")
    lattice = left + right
    direct_sums = DirectSumObjects(Lattices(ZZ))

    assert lattice in direct_sums
    assert lattice.summand(0) is left
    assert lattice.summand(1) is right
    assert lattice.summand_index_set() is lattice.summands().index_set()
    assert direct_sums.verify_decomposition(lattice, lattice.summands()) is lattice


def test_direct_sum_decomposition_rejects_replacement_summands() -> None:
    left = Lattices(ZZ)("U")
    right = Lattices(ZZ)("A2")
    lattice = left + right
    replacement = Lattices(ZZ)("A2")

    with pytest.raises(ValueError):
        DirectSumObjects(Lattices(ZZ)).verify_decomposition(
            lattice,
            (left, replacement),
        )
