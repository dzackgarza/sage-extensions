r"""Finite Galois quotients of $G_{\mathbb{F}_5}$ and of $G_{\mathbb{Q}}$ at $\mathbb{Q}(\zeta_{12})$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_restriction_to_f625_has_kernel_of_index_four_containing_frobenius_to_the_fourth() -> None:
    r"""$G_{\mathbb{F}_5} \to \operatorname{Gal}(\mathbb{F}_{5^4}/\mathbb{F}_5) \cong \mathbb{Z}/4$ is surjective; $\mathrm{Frob} \notin \ker$, $\mathrm{Frob}^4 \in \ker$."""
    group = GF(5).absolute_galois_group()
    frobenius = group.frobenius()
    restriction = group.restriction_map(group.finite_extension(4))
    kernel = restriction.kernel()

    assert restriction.is_surjective()
    assert restriction(frobenius**3 * frobenius**2) == restriction(frobenius**3) * restriction(frobenius**2)
    assert kernel.index() == 4
    assert frobenius not in kernel
    assert frobenius**4 in kernel


def test_the_frobenius_of_f25_has_exactly_two_extensions_to_f625() -> None:
    r"""The fibre of $\operatorname{Gal}(\mathbb{F}_{625}/\mathbb{F}_5) \to \operatorname{Gal}(\mathbb{F}_{25}/\mathbb{F}_5)$ over $\mathrm{Frob}$ has $[\mathbb{F}_{625}:\mathbb{F}_{25}] = 2$ elements, $\sigma$ and $\sigma^3$."""
    group = GF(5).absolute_galois_group()
    frobenius = group.frobenius()
    to_two = group.restriction_map(group.finite_extension(2))
    to_four = group.restriction_map(group.finite_extension(4))
    tau = to_two(frobenius)

    assert [k for k in range(4) if to_two(frobenius**k) == tau] == [1, 3]
    assert to_four(frobenius) != to_four(frobenius**3)


def test_the_automorphisms_of_q_zeta_12_act_on_i_and_root_three_by_their_exponent() -> None:
    r"""With $i = \zeta^3$ and $\sqrt3 = \zeta + \zeta^{-1}$ in $\mathbb{Q}(\zeta_{12})$:

    $\sigma_5$ fixes $i$ and negates $\sqrt3$; $\sigma_7$ negates both;
    $\sigma_{11}$ negates $i$ and fixes $\sqrt3$ (it is complex conjugation).
    """
    x = QQ.polynomial_ring("x").algebra_generator("x")
    cyclotomic = (x**4 - x**2 + 1).number_field("z")
    zeta = cyclotomic.primitive_element()
    i = zeta**3
    root_three = zeta + zeta**-1
    group = QQ.absolute_galois_group()
    quotient = group.finite_quotient(group.extension_data(cyclotomic))
    expected = {1: (i, root_three), 5: (i, -root_three), 7: (-i, -root_three), 11: (-i, root_three)}

    assert root_three**2 == 3
    assert i**2 == -1
    for a, (image_of_i, image_of_root_three) in expected.items():
        sigma = next(s for s in quotient if s(zeta) == zeta**a)
        assert sigma(i) == image_of_i
        assert sigma(root_three) == image_of_root_three
