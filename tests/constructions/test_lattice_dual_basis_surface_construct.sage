r"""A unimodular lattice exposes its metric dual and selected dual basis."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_metric_dual_is_the_dual_lattice() -> None:
    lattice = NamedLattices.U
    dual = lattice.dual_lattice()

    assert lattice.metric_dual() == dual
    assert dual.module_rank() == lattice.module_rank()


def test_hyperbolic_plane_dual_basis_is_the_selected_basis_of_the_dual() -> None:
    lattice = NamedLattices.U
    dual = lattice.dual_lattice()
    dual_basis = lattice.dual_basis()

    assert dual_basis == dual.module_generators()
    assert dual_basis.cardinality() == cardinal(2)
