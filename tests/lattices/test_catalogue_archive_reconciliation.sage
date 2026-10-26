r"""The 2-elementary catalogues, the K3 involutions and the embedding chain."""

from sage_extensions.all import *


def test_two_elementary_catalogues_and_searches_retain_the_archive_mathematics() -> None:
    assert TwoElementary.cardinality() == 75
    assert NegativeDefTwoElementary.cardinality() == 51

    target = TwoElementary[(10, 0, 0)]
    candidates = two_elementary_orthogonal_sums(signature_pair(1, 9), 0, 0)
    assert candidates.cardinality() == 1
    candidate = candidates[0]
    assert candidate.gram_tensor().is_equal_tensor(target.gram_tensor())

    repeated = signature_orthogonal_sums(
        signature_pair(0, 2), (NamedLattices.A1,)
    )
    assert repeated.cardinality() == 1
    assert repeated[0].gram_tensor().is_equal_tensor(
        (NamedLattices.A1 + NamedLattices.A1).gram_tensor()
    )


def test_k3_involutions_have_their_classical_invariant_and_coinvariant_lattices() -> None:
    r"""On $L_{K3}$: the Enriques involution has invariant lattice $U(2) \oplus
    E_8(2)$ (Barth--Hulek--Peters--Van de Ven, VIII.19); a Nikulin involution
    has coinvariant lattice $E_8(2)$ (Morrison, *On K3 surfaces with large
    Picard number*, section 5); the del Pezzo involution with invariant
    lattice $U(2)$ has anti-invariant lattice of 2-elementary type
    $(20, 2, 0)$ (Nikulin, *Integral symmetric bilinear forms*, 1.14).
    """
    lattice = NamedLattices.LK3
    identity = lattice.Aut().one()

    for involution in (Involutions.I_En, Involutions.I_Nik, Involutions.I_dP):
        assert involution != identity
        assert involution * involution == identity

    assert lattice.invariant_lattice(Involutions.I_En).is_isometric(NamedLattices.SEn)
    assert lattice.coinvariant_lattice(Involutions.I_En).is_isometric(NamedLattices.TEn)
    assert lattice.coinvariant_lattice(Involutions.I_Nik).is_isometric(NamedLattices.LmNik)
    assert lattice.invariant_lattice(Involutions.I_Nik).is_isometric(NamedLattices.LpNik)
    assert lattice.invariant_lattice(Involutions.I_dP).is_isometric(NamedLattices.U_2)
    assert lattice.coinvariant_lattice(Involutions.I_dP).is_isometric(NamedLattices.TdP)


def test_primitive_embedding_chain_retains_the_archived_generator_maps() -> None:
    tco = NamedLattices.Tco.module_generators()
    ten = NamedLattices.TEn.module_generators()
    tdp = NamedLattices.TdP.module_generators()

    assert Embeddings.TCo_into_TEn(tco[0]) == ten[0] + ten[1]
    assert Embeddings.TCo_into_TEn(tco[1]) == ten[2]
    assert Embeddings.TCo_into_TEn(tco[2]) == ten[3]

    assert Embeddings.TEn_into_TdP(ten[0]) == tdp[0]
    assert Embeddings.TEn_into_TdP(ten[1]) == tdp[1]
    assert Embeddings.TEn_into_TdP(ten[2]) == tdp[2]
    assert Embeddings.TEn_into_TdP(ten[3]) == tdp[3]
    for index in range(8):
        assert Embeddings.TEn_into_TdP(ten[4 + index]) == (
            tdp[4 + index] + tdp[12 + index]
        )

    assert Embeddings.TEn_into_LK3 == Embeddings.TdP_into_LK3 * Embeddings.TEn_into_TdP
    for embedding in (
        Embeddings.TCo_into_TEn,
        Embeddings.TEn_into_TdP,
        Embeddings.TdP_into_LK3,
        Embeddings.U_E8_2_into_TEn,
    ):
        assert embedding.is_primitive()
