r"""Isotypic decomposition of a representation of a cyclic group of order two."""

from sage_extensions.all import *  # noqa: F401,F403


def test_q2_with_c2_acting_by_diag_1_minus_1_splits_into_trivial_and_sign_lines() -> None:
    r"""By Maschke's theorem $\mathbb Q^2 = \mathbb Q e_+ \oplus \mathbb Q e_-$, the trivial and the sign
    isotypic components, each of rank one.

    Source: Serre, Linear Representations of Finite Groups, 2.6 (canonical decomposition).
    """
    G = Groups.C(2)
    M = QQ**2
    plus, minus = M.module_generator(0), M.module_generator(1)
    involution = M.Mor(M)({0: plus, 1: -minus})
    rho = G.Mor(M.Aut())({G.group_generators()[0]: involution})
    V = Modules(QQ[G])(M, rho)

    decomposition = V.isotypic_decomposition()
    assert decomposition.number_of_summands() == 2
    ranks = [decomposition.isotypic_component(chi).module_rank() for chi in decomposition.isotypic_characters()]
    assert sorted(ranks) == [1, 1]
    components = [decomposition.isotypic_component(chi) for chi in decomposition.isotypic_characters()]
    assert sum(1 for W in components if W.inclusion().is_in_image(V(plus))) == 1
    assert sum(1 for W in components if W.inclusion().is_in_image(V(minus))) == 1
