r"""Finite discriminant quadratic forms are finitely presented torsion forms."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_discriminant_quadratic_form_lies_in_the_torsion_refinement() -> None:
    form = Lattices(ZZ)("A2").discriminant_quadratic_form()
    category = QuadraticFormModules(ZZ).FinitelyPresented().Torsion()

    assert form in category
    assert form.is_torsion()
    assert form.cardinality() == 3
