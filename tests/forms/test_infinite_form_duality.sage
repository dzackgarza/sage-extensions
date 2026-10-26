r"""Perfect, unimodular and nondegenerate forms are three different conditions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_standard_form_on_a_countable_free_module_is_not_perfect() -> None:
    r"""On $V = \mathbb{Q}^{(\mathbb{N})}$ with $b(e_i, e_j) = \delta_{ij}$, $V \to V^*$ is injective, not surjective.

    The image of $v$ is the functional $b(v, -)$, which vanishes on all but
    finitely many $e_i$; the functional sending every $e_i$ to $1$ is not of
    that form.  Source: Jacobson, *Lectures in Abstract Algebra* II, IX.5.
    """
    module = QQ.free_module(NN)
    formed = module.equip_bilinear_form(QQ, lambda i, j: QQ.one() if i == j else QQ.zero())
    correlation = formed.correlation_morphism()
    all_ones = formed.dual_module()(lambda label: QQ.one())
    e0, e1 = formed.module_generator(0), formed.module_generator(1)

    assert correlation(e0)(e0) == 1
    assert correlation(e0)(e1) == 0
    assert correlation.is_injective()
    assert not correlation.is_surjective()
    assert all_ones not in correlation.image()


def test_u_is_unimodular_but_the_form_two_is_only_nondegenerate() -> None:
    r"""The correlation $L \to L^\vee$ of $U$ is an isomorphism; that of $\langle 2\rangle$ has cokernel of order $2$.

    The cokernel of the correlation has order $|\det L|$, and
    $\det U = -1$, $\det\langle 2\rangle = 2$.
    """
    hyperbolic = Lattices(ZZ)("U")
    two = Lattices(ZZ)([[2]])

    assert hyperbolic.correlation_morphism().is_isomorphism()
    assert two.correlation_morphism().is_injective()
    assert not two.correlation_morphism().is_surjective()
    assert two.correlation_morphism().cokernel().cardinality() == 2
    assert hyperbolic.correlation_morphism().cokernel().cardinality() == 1
