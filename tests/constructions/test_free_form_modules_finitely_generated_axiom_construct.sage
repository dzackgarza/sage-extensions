r"""Finite-rank lattices lie in the finitely-generated free-form refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_lattice_lies_in_the_finitely_generated_free_form_refinement() -> None:
    form = Lattices(ZZ)("A2")
    category = FreeFormModules(ZZ).FinitelyGenerated()

    assert form in category
    assert form.module_rank() == 2
    assert form.is_nondegenerate()
