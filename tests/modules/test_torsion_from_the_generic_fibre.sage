r"""Torsion computed from the generic fibre.

Over a domain $R$ with fraction field $K$, $\operatorname{Tor}(M) = \ker(M \to K \otimes_R M)$,
and $M$ is torsion exactly when $K \otimes_R M = 0$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_6_is_torsion_with_generic_rank_0_and_is_its_own_torsion_submodule() -> None:
    """Q (x) Z/6 = 0. Source: Atiyah–Macdonald, Introduction to Commutative Algebra, ex. 2.3 and 3.12."""
    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6)))
    assert M.is_torsion()
    assert not M.is_torsion_free()
    assert M.generic_rank() == 0
    assert M.vector_space().is_zero()
    assert ModulesOverIntegralDomains(ZZ)(M).torsion_submodule().inclusion().is_surjective()
    assert ModulesOverIntegralDomains(ZZ)(M).torsion_submodule().cardinality() == 6


def test_z_mod_6_plus_z_has_generic_rank_1_and_is_neither_torsion_nor_torsion_free() -> None:
    """Q (x) (Z/6 + Z) = Q; the torsion submodule is Z/6."""
    F = ZZ**2
    M = F / F.submodule([6 * F.module_generator(0)])
    assert M.generic_rank() == 1
    assert not M.is_torsion()
    assert not M.is_torsion_free()
    assert ModulesOverIntegralDomains(ZZ)(M).torsion_submodule().cardinality() == 6
    assert not ModulesOverIntegralDomains(ZZ)(M).generic_fibre_map().is_injective()
