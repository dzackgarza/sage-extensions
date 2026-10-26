r"""Tor and Ext are functors in the second variable.

Over $\mathbb Z$, $\operatorname{Tor}_1(\mathbb Z/a, B) = B[a]$ (the $a$-torsion
of $B$) and $\operatorname{Ext}^1(\mathbb Z/a, B) = B/aB$, naturally in $B$
(Weibel, *An Introduction to Homological Algebra*, 3.1.2 and 3.3.2).
"""

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(n):
    return Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(n)))


def test_tor_one_of_z_mod_6_sends_the_doubling_z_mod_2_to_z_mod_4_to_an_isomorphism() -> None:
    r"""$1 \mapsto 2\colon \mathbb Z/2 \to \mathbb Z/4$ induces $(\mathbb Z/2)[6] = \mathbb Z/2 \to
    (\mathbb Z/4)[6] = \{0, 2\}$, $1 \mapsto 2$, an isomorphism.

    Source: Weibel 3.1.2; computed by hand.
    """
    six, two, four = cyclic(6), cyclic(2), cyclic(4)
    doubling = two.Mor(four)({0: 2 * four.module_generator(0)})
    induced = six.tor(doubling, degree=1)
    assert induced.domain().cardinality() == 2
    assert induced.codomain().cardinality() == 2
    assert induced.is_injective()
    assert induced.is_surjective()


def test_tor_one_of_z_mod_6_sends_the_reduction_z_mod_4_to_z_mod_2_to_zero() -> None:
    r"""$\mathbb Z/4 \to \mathbb Z/2$ sends $(\mathbb Z/4)[6] = \{0, 2\}$ to $0$.

    Source: Weibel 3.1.2; computed by hand.
    """
    six, four, two = cyclic(6), cyclic(4), cyclic(2)
    reduction = four.Mor(two)({0: two.module_generator(0)})
    induced = six.tor(reduction, degree=1)
    assert induced.domain().cardinality() == 2
    assert not induced.is_injective()
    assert induced.image().cardinality() == 1


def test_ext_one_of_z_mod_6_sends_the_reduction_z_mod_4_to_z_mod_2_to_an_isomorphism() -> None:
    r"""$\mathbb Z/4 \to \mathbb Z/2$ induces $\mathbb Z/4 \otimes \mathbb Z/6 = \mathbb Z/2 \to
    \mathbb Z/2 \otimes \mathbb Z/6 = \mathbb Z/2$, $1 \mapsto 1$, an isomorphism.

    Source: Weibel 3.3.2; computed by hand.
    """
    six, four, two = cyclic(6), cyclic(4), cyclic(2)
    reduction = four.Mor(two)({0: two.module_generator(0)})
    induced = six.ext(reduction, degree=1)
    assert induced.domain().cardinality() == 2
    assert induced.codomain().cardinality() == 2
    assert induced.is_injective()
    assert induced.is_surjective()


def test_tor_one_of_z_mod_6_is_functorial_on_a_composite() -> None:
    r"""$\operatorname{Tor}_1(\mathbb Z/6, g f) = \operatorname{Tor}_1(\mathbb Z/6, g)\operatorname{Tor}_1(\mathbb Z/6, f)$
    for $f\colon \mathbb Z/2 \to \mathbb Z/4$, $1 \mapsto 2$, and $g\colon \mathbb Z/4 \to \mathbb Z/8$,
    $1 \mapsto 2$; the composite is an isomorphism $\mathbb Z/2 \to (\mathbb Z/8)[6] = \{0, 4\}$.

    Source: functoriality of Tor (Weibel 2.7); computed by hand.
    """
    six, two, four, eight = cyclic(6), cyclic(2), cyclic(4), cyclic(8)
    f = two.Mor(four)({0: 2 * four.module_generator(0)})
    g = four.Mor(eight)({0: 2 * eight.module_generator(0)})
    composite = six.tor(g * f, degree=1)
    assert composite == six.tor(g, degree=1) * six.tor(f, degree=1)
    assert composite.is_injective()
    assert composite.is_surjective()
