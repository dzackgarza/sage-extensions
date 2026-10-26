r"""Finitely presented abelian groups and the normal forms of their relations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_relations_2x_and_4x_have_hermite_form_2x() -> None:
    r"""$\mathbb Z x / (2x, 4x) = \mathbb Z/2$: the Hermite normal form of the relation column
    $(2, 4)^T$ is $(2, 0)^T$, and the normalization is an isomorphism.

    Source: Cohen, A Course in Computational Algebraic Number Theory, 2.4.2; by hand.
    """
    F = ZZ**1
    x = F.module_generator(0)
    M = F / F.submodule([2 * x, 4 * x])
    assert M.cardinality() == 2

    normalization = M.hermite_form()
    normalized = normalization.codomain()
    relations = normalized.presentation()
    assert relations.domain().module_rank() == 1
    assert relations(relations.domain().module_generator(0)) == 2 * relations.codomain().module_generator(0)
    assert normalization.is_isomorphism()
    assert normalized.cardinality() == 2


def test_z2_modulo_2x_plus_4y_is_z_mod_2_plus_z() -> None:
    r"""$\mathbb Z^2 / (2x + 4y) \cong \mathbb Z/2 \oplus \mathbb Z$: the relation row $(2, 4)$ has
    Smith form $(2, 0)$.

    Source: Cohen 2.4.4 (Smith normal form); by hand, gcd(2, 4) = 2.
    """
    F = ZZ**2
    x, y = F.module_generator(0), F.module_generator(1)
    M = F / F.submodule([2 * x + 4 * y])
    assert M.torsion_submodule().cardinality() == 2
    assert M.vector_space().module_rank() == 1
    assert M.hermite_form().is_isomorphism()
    assert M.invariant_factor_form().codomain().torsion_submodule().cardinality() == 2
