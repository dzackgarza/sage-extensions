r"""A form is nondegenerate when its correlation has zero kernel."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_lattice_lies_in_the_nondegenerate_form_refinement() -> None:
    form = Lattices(ZZ)("A2")
    category = FormModules(ZZ).Nondegenerate()

    assert form in category
    assert form.is_nondegenerate()
    assert form.correlation_morphism().is_injective()
