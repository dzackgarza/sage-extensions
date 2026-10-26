r"""Decomposition, inertia and Frobenius at $2$ in $\mathbb{Q}(\sqrt5)$."""

from sage_extensions.all import *  # noqa: F401,F403


def _root_five_quotient():
    group = QQ.absolute_galois_group()
    field = QuadraticField(5, "a")
    quotient = group.finite_quotient(group.extension_data(field))
    return group, quotient, field.primes_above(2)[0]


def test_two_is_inert_in_the_field_of_root_five() -> None:
    r"""$x^2 - x - 1$ is irreducible mod $2$, so the decomposition group of $G_{\mathbb{Q}}$ at $2$ maps onto $\operatorname{Gal}(\mathbb{Q}(\sqrt5)/\mathbb{Q})$ and inertia maps to $1$.

    Source: Neukirch, *Algebraic Number Theory*, I.8 and I.9.
    """
    group, quotient, prime = _root_five_quotient()

    assert quotient.order() == 2
    assert group.decomposition_group_class(2).image(quotient, prime).order() == 2
    assert group.inertia_group_class(2).image(quotient, prime).order() == 1
    assert quotient.decomposition_group(prime).order() == 2
    assert quotient.inertia_group(prime).order() == 1
    stabilizer = quotient.decomposition_group(prime)
    action = stabilizer.stabilizer_action()
    assert stabilizer.stabilized_object() is prime
    assert action.domain() is quotient.classifying_category()
    assert action.codomain() is Sets()
    assert prime in action(action.domain().an_object())


def test_the_frobenius_at_two_is_the_nontrivial_automorphism_of_q_root_five() -> None:
    r"""Since $2$ is inert, $\mathrm{Frob}_2$ generates $\operatorname{Gal}(\mathbb{Q}(\sqrt5)/\mathbb{Q})$: it sends $\sqrt5 \mapsto -\sqrt5$."""
    group, quotient, prime = _root_five_quotient()
    image = group.frobenius_class(2).image(quotient, prime)

    assert image.representative() != quotient.one()
    assert image.representative().multiplicative_order() == 2
