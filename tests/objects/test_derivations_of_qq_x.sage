from sage_extensions.all import *


def polynomials():
    return QQ.free_module(("x",)).symmetric_algebra()


def test_the_derivations_of_qq_x() -> None:
    r"""$\operatorname{Der}_{\mathbb Q}(\mathbb Q[x]) = \mathbb Q[x]\,\partial_x$; every derivation obeys Leibniz and kills constants."""
    ring = polynomials()
    x = ring.algebra_generator("x")
    derivations = ring.vector_fields()
    delta = derivations.an_element()
    assert derivations in Modules(ring)
    assert derivations.module_rank() == 1
    assert delta(x ^ 2) == 2 * x * delta(x)
    assert delta.linear_endomorphism()(ring.one()) == ring.zero()


def test_the_degree_minus_one_derivations_of_the_de_rham_algebra() -> None:
    r"""A derivation of degree $-1$ of $\Omega^\bullet_{\mathbb Q[x]}$ kills $\Omega^0$ and is fixed by its value on $dx$: $\operatorname{Hom}(\Omega^1, \mathbb Q[x])$, of rank one."""
    ring = polynomials()
    x = ring.algebra_generator("x")
    de_rham = ring.de_rham_algebra()
    derivations = de_rham.graded_derivations(shift=-1)
    assert derivations.module_rank() == 1
    assert derivations.an_element()(de_rham(x)) == de_rham.zero()

