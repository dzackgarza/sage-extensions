r"""A discriminant quadratic form is a quadratic map."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_discriminant_quadratic_form_of_a2_scales_by_the_square() -> None:
    r"""$q(nx) = n^2 q(x)$; on $A_2^\vee / A_2 = \mathbb{Z}/3$ with $q = 4/3 \bmod 2$, $q(2g) = 16/3 \equiv 4/3$.

    $2g = -g$ in $\mathbb{Z}/3$, so the law also gives $q(-g) = q(g)$.
    """
    form = Lattices(ZZ)("A2").discriminant_quadratic_form()
    generator = form.module_generator(0)

    assert (2 * generator).q() == 4 * generator.q()
    assert (-generator).q() == generator.q()
    assert generator.q() == form.value_module()(QQ(4) / 3)
