r"""Subgroups and automorphisms of the symmetric group on three letters."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_transposition_generates_a_non_normal_subgroup_of_index_three() -> None:
    r"""In ``S3`` a transposition generates ``C2`` of index 3, whose normal closure is ``S3``."""
    s3 = Groups.S(3)
    transposition = next(g for g in s3 if g.multiplicative_order() == 2)
    subgroup = s3.subgroup((transposition,))

    assert subgroup.cardinality() == 2
    assert s3.cardinality() / subgroup.cardinality() == 3
    assert s3.normal_closure(subgroup).cardinality() == 6


def test_every_automorphism_of_S3_is_inner() -> None:
    r"""``Aut(S3) = Inn(S3) = S3``: order 6.

    ``Z(S3) = 1`` gives ``Inn(S3) = S3``; an automorphism is determined by its
    action on the three transpositions, which generate, so ``|Aut(S3)| <= 6``.
    """
    s3 = Groups.S(3)

    assert s3.center().cardinality() == 1
    assert s3.Aut().cardinality() == 6
    assert s3.Aut().is_isomorphic_to(s3)
