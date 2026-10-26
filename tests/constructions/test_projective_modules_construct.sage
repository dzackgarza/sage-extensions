r"""Finite free modules are projective and locally trivial of constant rank.

For ``ZZ^2``, localization at the prime ``(5)`` remains free of rank two; the
canonical local trivialization is an isomorphism.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_plane_is_projective_of_local_rank_two() -> None:
    module = ZZ.free_module(2)
    point = ZZ.spectrum()(ZZ.ideal(5))
    trivialization = module.local_free_trivialization(point)

    assert module in ProjectiveModules(ZZ)
    assert module.is_projective()
    assert module.projective_rank(point) == 2
    assert trivialization.domain().module_rank() == 2
    assert trivialization.is_isomorphism()
