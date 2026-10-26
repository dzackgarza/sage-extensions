r"""Maximal isotropic subgroups of the discriminant forms of $U(2)$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_bilinear_discriminant_form_of_u2_has_three_maximal_isotropic_subgroups() -> None:
    r"""On $(\mathbb{Z}/2)^2$ with $b(e, f) = 1/2$, $b(e, e) = b(f, f) = 0$, every line is isotropic.

    $b(e+f, e+f) = 2 \cdot \tfrac12 = 0 \bmod 1$, so all three subgroups of
    order $2$ are isotropic, and the whole group is not, since $b(e, f) \ne 0$.
    """
    form = Lattices(ZZ)("U").twist(2).discriminant_bilinear_form()
    maximal = form.maximal_isotropic_subobjects()

    assert form.cardinality() == 4
    assert maximal.cardinality() == 3
    assert all(subobject.cardinality() == 2 for subobject in maximal)


def test_the_quadratic_discriminant_form_of_u2_has_two_maximal_isotropic_subgroups() -> None:
    r"""On $(\mathbb{Z}/2)^2$ with $q(e) = q(f) = 0$, $q(e+f) = 1 \bmod 2$, only $\langle e\rangle$ and $\langle f\rangle$ are isotropic."""
    form = Lattices(ZZ)("U").twist(2).discriminant_quadratic_form()
    maximal = form.maximal_isotropic_subobjects()

    assert maximal.cardinality() == 2
    assert all(subobject.cardinality() == 2 for subobject in maximal)
    assert form.isotropic_elements().cardinality() == 3
