r"""Twisting a finite quadratic form by $-1$ negates it."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_negative_twist_of_the_a2_discriminant_form_negates_its_brown_invariant() -> None:
    r"""$q_{A_2}$ on $\mathbb{Z}/3$ is $4/3 \bmod 2$; its $(-1)$-twist is $2/3 \bmod 2$, the form of $A_2(-1)$.

    $A_2$ is negative definite here, so by Milgram's formula its discriminant
    form has Brown invariant $\operatorname{sign} = -2 \equiv 6 \pmod 8$, and
    the twist has Brown invariant $2$.  Both orthogonal groups are $\{\pm 1\}$.
    Source: Milnor–Husemoller, *Symmetric Bilinear Forms*, Appendix 4.
    """
    a2 = Lattices(ZZ)("A2")
    form = a2.discriminant_quadratic_form()
    twisted = form.twist(-1)
    generator = form.module_generator(0)
    values = form.value_module()

    assert form.cardinality() == 3
    assert form.q(generator) == values(QQ(4) / 3)
    assert twisted.q(twisted.module_generator(0)) == twisted.value_module()(QQ(2) / 3)
    assert form.brown_invariant() == 6
    assert twisted.brown_invariant() == 2
    assert not twisted.is_isometric_to(form)
    assert twisted.is_isometric_to(a2.twist(-1).discriminant_quadratic_form())
    assert form.O().order() == 2
    assert twisted.O().order() == 2
