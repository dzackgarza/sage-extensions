r"""Finitely presented abelian groups and the normal forms of their relations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_relations_2x_and_4x_have_hermite_form_2x() -> None:
    r"""$\mathbb Z x / (2x, 4x) = \mathbb Z/2$: the Hermite normal form of the relation column
    $(2, 4)^T$ is $(2, 0)^T$, and the normalization is an isomorphism.

    Source: Cohen, A Course in Computational Algebraic Number Theory, 2.4.2; by hand.

    Stated in the owner's vocabulary: a submodule is ``subobject_on`` and the
    quotient is the cokernel of its inclusion.  The claims are unchanged, and the
    relation span, the retained inclusion and quotient map, and the invariance of
    the quotient under redundant and reordered relations are all checked explicitly.
    """
    F = ZZ**1
    x = F.module_generator(0)
    span = F.subobject_on([2 * x, 4 * x])
    inclusion = span.inclusion()
    M = inclusion.cokernel()

    assert M.cardinality() == 2

    # The relation span is 2Zx inside Zx: its one generator maps to 2x.
    (span_generator,) = tuple(span.module_generators())
    assert inclusion(span_generator) == 2 * x
    # Redundant and reordered relations present the same span and the same quotient.
    assert F.subobject_on([2 * x, 4 * x, 6 * x]).inclusion().domain() == inclusion.domain()
    assert F.subobject_on([4 * x, 2 * x]).inclusion().cokernel().cardinality() == 2

    # The quotient map kills the relation and keeps the generator.
    quotient_map = M.cokernel_projection()
    assert quotient_map(2 * x) == M.zero()
    assert quotient_map(x) != M.zero()

    normalization = M.hermite_form()
    normalized = normalization.codomain()
    relations = normalized.presentation()
    assert relations.domain().module_rank() == 1
    assert relations(relations.domain().module_generator(0)) == 2 * relations.codomain().module_generator(0)
    assert isinstance(normalization, CategoricalIsomorphism)
    assert normalized.cardinality() == 2


def test_z2_modulo_2x_plus_4y_is_z_mod_2_plus_z() -> None:
    r"""$\mathbb Z^2 / (2x + 4y) \cong \mathbb Z/2 \oplus \mathbb Z$: the relation row $(2, 4)$ has
    Smith form $(2, 0)$.

    Source: Cohen 2.4.4 (Smith normal form); by hand, gcd(2, 4) = 2.

    Stated in the owner's vocabulary: the submodule is ``subobject_on`` and the
    quotient is the cokernel of its inclusion.  ``hermite_form`` and
    ``invariant_factor_form`` are both isomorphisms in the owner's sense — the
    returned arrow *is* a ``CategoricalIsomorphism`` — so the claim is the type,
    not a predicate named after it.
    """
    F = ZZ**2
    x, y = F.module_generator(0), F.module_generator(1)
    M = F.subobject_on([2 * x + 4 * y]).inclusion().cokernel()

    assert M.torsion_submodule().cardinality() == 2
    assert M.vector_space().module_rank() == 1
    assert isinstance(M.hermite_form(), CategoricalIsomorphism)
    assert M.invariant_factor_form().codomain().torsion_submodule().cardinality() == 2
