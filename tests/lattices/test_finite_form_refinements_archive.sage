r"""Quadratic versus bilinear finite-form distinctions retained from the archive.

Nikulin and Miranda--Morrison distinguish a finite quadratic form from its
polar bilinear form.  The rank-one sign pair and the elementary forms ``u_1``
and ``v_1`` are small specimens where the underlying finite groups and
bilinear forms agree while the quadratic refinements do not.
"""

from sage_extensions.all import *


def test_rank_one_sign_pair_is_bilinearly_isomorphic_but_not_quadratically() -> None:
    positive = Lattices(ZZ)([[2]]).discriminant_group()
    negative = Lattices(ZZ)([[-2]]).discriminant_group()
    positive_invariants = positive.invariants()
    negative_invariants = negative.invariants()

    assert positive_invariants == negative_invariants
    assert positive_invariants.cardinality() == 1
    assert positive_invariants[0] == 2
    assert positive.associated_bilinear_form().is_isomorphic(
        negative.associated_bilinear_form()
    )
    assert not positive.is_isomorphic(negative)
    assert positive.is_anti_isometric(negative)


def test_u1_and_v1_share_the_bilinear_form_but_not_the_quadratic_refinement() -> None:
    u1 = Lattices(ZZ)([[0, 2], [2, 0]]).discriminant_group()
    v1 = Lattices.D4.discriminant_group()
    u1_invariants = u1.invariants()
    v1_invariants = v1.invariants()

    assert u1_invariants == v1_invariants
    assert u1_invariants.cardinality() == 2
    assert u1_invariants[0] == u1_invariants[1] == 2
    assert u1.associated_bilinear_form().is_isomorphic(
        v1.associated_bilinear_form()
    )
    assert not u1.is_isomorphic(v1)
    assert u1.brown_invariant() == 0
    assert v1.brown_invariant() == 4
