r"""Archived lattice similarities on the live twist/isometry construction.

A similarity of scale ``a`` from ``L`` to ``M`` is an isometry ``L(a) -> M``.
The archived API exposed both the existence predicate and the actual morphism.
The hyperbolic plane and its scale-two twist distinguish this from ordinary
isometry because their determinants differ by a factor of four.
"""

from sage_extensions.all import *


def test_archived_similarity_predicate_does_not_conflate_similarity_with_isometry() -> None:
    source = Lattices(ZZ)("U")
    target = source.twist(2)

    assert source.is_similar(target, 2) is True
    assert source.is_isometric(target) is False
    assert abs(source.determinant()) == 1
    assert abs(target.determinant()) == 4


def test_archived_wrong_similarity_scale_is_rejected_by_the_form_mor() -> None:
    source = Lattices(ZZ)("U")
    target = source.twist(2)

    assert source.is_similar(target, 1) is False
