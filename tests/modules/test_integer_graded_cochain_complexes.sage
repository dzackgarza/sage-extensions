r"""Cochain complexes of abelian groups graded by all of $\mathbb Z$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_by_3_to_z_in_degrees_minus_one_and_zero_has_h_minus_one_zero_and_h0_z_mod_3() -> None:
    r"""$H^{-1} = \ker(3) = 0$ and $H^0 = \operatorname{coker}(3) = \mathbb Z/3$.

    Source: by hand.
    """
    A = ZZ**1
    B = ZZ**1
    times_three = A.Mor(B)({0: 3 * B.module_generator(0)})
    complex_ = CochainComplexes(ZZ)({-1: A, 0: B}, {-1: times_three})

    assert complex_.cohomology(-1).is_zero()
    assert complex_.cohomology(0).cardinality() == 3
    assert complex_.cohomology(0).annihilator() == ZZ.ideal(3)
    assert complex_.cohomology(1).is_zero()
    assert complex_.cohomology(-2).is_zero()


def test_h_minus_one_of_z_in_degree_minus_one_sends_doubling_to_doubling() -> None:
    r"""For $\mathbb Z$ concentrated in degree $-1$, $H^{-1} = \mathbb Z$ and the chain map $2$
    induces multiplication by $2$ on the class of the generator.

    Source: functoriality of cohomology; by hand.
    """
    A = ZZ**1
    e = A.module_generator(0)
    complex_ = CochainComplexes(ZZ)({-1: A}, {})
    times_two = CochainComplexes(ZZ).Mor(complex_, complex_)({-1: A.Mor(A)({0: 2 * e})})

    H = CochainComplexes(ZZ).cohomology(-1)
    h = H(complex_)
    generator_class = h.class_of_cycle(e)
    assert generator_class != h.zero()
    assert H(times_two)(generator_class) == 2 * generator_class
    assert not H(times_two).is_surjective()
    assert H(times_two).is_injective()
