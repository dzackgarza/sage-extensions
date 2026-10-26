r"""Hom, Tor and Ext between finite cyclic groups, from the resolution $0 \to \mathbb Z
\xrightarrow{m} \mathbb Z \to \mathbb Z/m \to 0$.

Tensoring the resolution with $\mathbb Z/n$ gives $\mathbb Z/n \xrightarrow{m} \mathbb Z/n$, so
$\mathbb Z/m \otimes \mathbb Z/n = \operatorname{Tor}_0 = \mathbb Z/\gcd(m, n)$ and
$\operatorname{Tor}_1(\mathbb Z/m, \mathbb Z/n) = \mathbb Z/\gcd(m, n)$; $\operatorname{Tor}_1(\mathbb Z/m,
\mathbb Z) = 0$.  Applying $\operatorname{Hom}(-, N)$ gives $N \xrightarrow{m} N$, so
$\operatorname{Hom}(\mathbb Z/m, \mathbb Z/n) = \operatorname{Ext}^1(\mathbb Z/m, \mathbb Z/n) =
\mathbb Z/\gcd(m, n)$, $\operatorname{Hom}(\mathbb Z/m, \mathbb Z) = 0$ and $\operatorname{Ext}^1(\mathbb
Z/m, \mathbb Z) = \mathbb Z/m$, by hand from these complexes.
"""

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(order):
    r"""$\operatorname{coker}(\mathbb Z \xrightarrow{m} \mathbb Z)$."""
    line = ZZ ^ 1
    return line.Mor(line)({0: order * line.module_generator(0)}).cokernel()


def test_the_resolution_of_z6_has_length_one() -> None:
    r"""$0 \to \mathbb Z \xrightarrow{6} \mathbb Z \to \mathbb Z/6 \to 0$."""
    resolution = cyclic(6).free_resolution()

    assert resolution.length() == 1
    assert resolution.term(0).module_rank() == 1
    assert resolution.term(1).module_rank() == 1
    assert resolution.differential(1).cokernel().is_torsion()


def test_tor_zero_of_z6_and_z4_is_their_tensor_product_z2() -> None:
    r"""$\operatorname{Tor}_0(\mathbb Z/6, \mathbb Z/4) = \mathbb Z/6 \otimes \mathbb Z/4 = \mathbb Z/2$."""
    assert tuple(cyclic(6).tor(cyclic(4), 0).invariant_factors()) == (2,)
    assert tuple(cyclic(6).tensor_product(cyclic(4)).invariant_factors()) == (2,)


def test_tor_one_of_z6_and_z4_is_z2() -> None:
    r"""$\operatorname{Tor}_1(\mathbb Z/6, \mathbb Z/4) = \mathbb Z/\gcd(6, 4) = \mathbb Z/2$."""
    assert tuple(cyclic(6).tor(cyclic(4), 1).invariant_factors()) == (2,)


def test_tor_one_of_z6_and_z9_is_z3_and_of_z6_and_z_is_zero() -> None:
    r"""$\operatorname{Tor}_1(\mathbb Z/6, \mathbb Z/9) = \mathbb Z/3$; $\mathbb Z$ is flat, so
    $\operatorname{Tor}_1(\mathbb Z/6, \mathbb Z) = 0$."""
    assert tuple(cyclic(6).tor(cyclic(9), 1).invariant_factors()) == (3,)
    assert cyclic(6).tor(ZZ ^ 1, 1).is_zero()


def test_ext_one_of_z6_into_z_is_z6_and_hom_is_zero() -> None:
    r"""$\operatorname{Hom}(\mathbb Z/6, \mathbb Z) = 0$ and $\operatorname{Ext}^1(\mathbb Z/6, \mathbb Z)
    = \mathbb Z/6$."""
    assert cyclic(6).ext(ZZ ^ 1, 0).is_zero()
    assert tuple(cyclic(6).ext(ZZ ^ 1, 1).invariant_factors()) == (6,)


def test_hom_and_ext_one_of_z6_into_z4_are_z2() -> None:
    r"""$\operatorname{Hom}(\mathbb Z/6, \mathbb Z/4) = \operatorname{Ext}^1(\mathbb Z/6, \mathbb Z/4) =
    \mathbb Z/2$."""
    assert tuple(cyclic(6).ext(cyclic(4), 0).invariant_factors()) == (2,)
    assert tuple(cyclic(6).ext(cyclic(4), 1).invariant_factors()) == (2,)


def test_ext_two_vanishes_over_the_integers() -> None:
    r"""$\mathbb Z$ has global dimension $1$, so $\operatorname{Ext}^2(\mathbb Z/6, \mathbb Z/4) = 0$ and
    $\operatorname{Tor}_2(\mathbb Z/6, \mathbb Z/4) = 0$."""
    assert cyclic(6).ext(cyclic(4), 2).is_zero()
    assert cyclic(6).tor(cyclic(4), 2).is_zero()


def test_multiplication_by_two_induces_zero_on_tor_one_of_z2_and_z2() -> None:
    r"""$\operatorname{Tor}_1(-, \mathbb Z/2)$ is additive, so $2: \mathbb Z/2 \to \mathbb Z/2$, which is the
    zero map, induces the zero map on $\operatorname{Tor}_1(\mathbb Z/2, \mathbb Z/2) = \mathbb Z/2$, and the
    identity induces the identity."""
    two = cyclic(2)
    doubling = two.End()({0: 2 * two.module_generator(0)})
    induced = doubling.tor_map(two, 1)
    identity = two.End().one().tor_map(two, 1)

    assert induced == induced.domain().End().zero()
    assert identity == identity.domain().End().one()
