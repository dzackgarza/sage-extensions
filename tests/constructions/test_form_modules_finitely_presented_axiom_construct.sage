r"""Finite lattices are finitely presented formed modules."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_lattice_lies_in_the_finitely_presented_form_refinement() -> None:
    form = Lattices(ZZ)("A2")
    category = FormModules(ZZ).FinitelyPresented()

    assert form in category
    assert form.is_finitely_presented()
    assert form.module_rank() == 2
