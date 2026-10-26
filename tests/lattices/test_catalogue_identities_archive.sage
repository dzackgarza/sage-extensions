r"""Ranks and signatures of the named period lattices.

The project uses the negative-definite convention for $E_8$.  $L_{K3} =
U^3 \oplus E_8^2$ (Barth--Hulek--Peters--Van de Ven, VIII.3); $E_{10} = U
\oplus E_8$; the Enriques lattices $U(2) \oplus E_8(2)$ and $T_{En} = U \oplus
U(2) \oplus E_8(2)$; the Nikulin involution lattices $U^3 \oplus E_8(2)$ and
$E_8(2)$ (Morrison, *On K3 surfaces with large Picard number*, section 5); the
2-elementary lattice of type $(20, 2, 0)$ of signature $(2, 18)$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _rank_and_signature(lattice):
    signature = lattice.signature_pair()
    return lattice.module_rank(), signature.first(), signature.second()


def test_named_period_lattices_have_their_textbook_ranks_and_signatures() -> None:
    assert _rank_and_signature(NamedLattices.U) == (2, 1, 1)
    assert _rank_and_signature(NamedLattices.U_2) == (2, 1, 1)
    assert _rank_and_signature(NamedLattices.E8) == (8, 0, 8)
    assert _rank_and_signature(NamedLattices.E8_2) == (8, 0, 8)
    assert _rank_and_signature(NamedLattices.E10) == (10, 1, 9)
    assert _rank_and_signature(NamedLattices.E10_2) == (10, 1, 9)
    assert _rank_and_signature(NamedLattices.LK3) == (22, 3, 19)
    assert _rank_and_signature(NamedLattices.SEn) == (10, 1, 9)
    assert _rank_and_signature(NamedLattices.TEn) == (12, 2, 10)
    assert _rank_and_signature(NamedLattices.LpNik) == (14, 3, 11)
    assert _rank_and_signature(NamedLattices.LmNik) == (8, 0, 8)
    assert _rank_and_signature(NamedLattices.TdP) == (20, 2, 18)
