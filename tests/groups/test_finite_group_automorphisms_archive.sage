r"""Automorphism groups of small finite groups."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


@pytest.mark.parametrize(
    ("name", "build", "expected_order"),
    (
        ("C8", lambda: Groups.C(8), 4),
        ("V4", lambda: Groups.V4(), 6),
        ("Q8", lambda: Groups.Q(), 24),
        ("S3", lambda: Groups.S(3), 6),
        ("S6", lambda: Groups.S(6), 1440),
    ),
)
def test_standard_finite_group_automorphism_orders(name, build, expected_order) -> None:
    r"""$|\operatorname{Aut}|$: $C_8 \mapsto |(\mathbb{Z}/8)^\times| = 4$, $V_4 \mapsto |GL_2(\mathbb{F}_2)| = 6$, $Q_8 \mapsto |S_4| = 24$, $S_3 \mapsto 6$, $S_6 \mapsto 1440$.

    Source: Dummit–Foote, *Abstract Algebra*, §4.4 and Exercise 4.4.10;
    Rotman, *An Introduction to the Theory of Groups*, Thm. 7.12 (the outer
    automorphism of $S_6$).
    """
    assert build().Aut().order() == expected_order


def test_aut_c8_is_elementary_abelian_of_order_four() -> None:
    r"""$\operatorname{Aut}(C_8) \cong (\mathbb{Z}/8)^\times = \{1, 3, 5, 7\}$, and every unit squares to $1 \bmod 8$."""
    automorphisms = Groups.C(8).Aut()
    identity = automorphisms.one()

    assert automorphisms.order() == 4
    assert all(element * element == identity for element in automorphisms)


def test_aut_v4_is_nonabelian_of_order_six() -> None:
    r"""$\operatorname{Aut}(V_4) \cong GL_2(\mathbb{F}_2) \cong S_3$ is nonabelian."""
    automorphisms = Groups.V4().Aut()
    elements = tuple(automorphisms)

    assert automorphisms.order() == 6
    assert any(left * right != right * left for left in elements for right in elements)


def test_conjugation_realizes_all_automorphisms_of_s3() -> None:
    r"""$S_3$ has trivial centre and every automorphism is inner, so $S_3 \to \operatorname{Aut}(S_3)$ is an isomorphism."""
    group = Groups.S(3)
    conjugation = group.conjugation_morphism()

    assert conjugation.kernel().order() == 1
    assert conjugation.image().order() == group.Aut().order() == 6


def test_s6_inner_automorphisms_have_index_two() -> None:
    r"""$\operatorname{Inn}(S_6) \cong S_6$ has order $720$ and index $2$ in $\operatorname{Aut}(S_6)$: $S_6$ is the only symmetric group with an outer automorphism."""
    group = Groups.S(6)
    conjugation = group.conjugation_morphism()

    assert conjugation.kernel().order() == 1
    assert conjugation.image().order() == 720
    assert group.Aut().order() == 1440
