from sage_extensions.all import *


def test_named_surface_lattices_have_their_expected_signatures_and_ranks() -> None:
    assert NamedLattices.Tco.module_rank() == 11
    assert NamedLattices.Tco.signature_pair() == signature_pair(2, 9)
    assert NamedLattices.TEn.module_rank() == 12
    assert NamedLattices.TEn.signature_pair() == signature_pair(2, 10)
    assert NamedLattices.TdP.module_rank() == 20
    assert NamedLattices.TdP.signature_pair() == signature_pair(2, 18)
    assert NamedLattices.LK3.module_rank() == 22
    assert NamedLattices.LK3.signature_pair() == signature_pair(3, 19)
    assert Lattices.TEn is NamedLattices.TEn
    assert Lattices.TdP is NamedLattices.TdP
    assert Lattices.LK3 is NamedLattices.LK3


def test_tdp_metric_dual_is_the_formed_linear_dual() -> None:
    lattice = NamedLattices.TdP
    value_module = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(QQ)
    metric_dual = lattice.dual_lattice()
    linear_dual = lattice.linear_dual()
    identification = lattice.dual_lattice_to_linear_dual()

    assert identification.domain() is metric_dual
    assert identification.codomain() is linear_dual
    assert metric_dual.value_module() is QQ
    assert value_module.base_ring() is ZZ
    assert value_module.module_over_extension() is QQ
    assert value_module.ring_map().domain() is ZZ
    assert value_module.ring_map().codomain() is QQ
    assert value_module in AdditiveGroups().AdditiveCommutative()
    scalar_action = value_module.scalar_action()
    assert scalar_action.domain() is ZZ
    additive_group = value_module.underlying_additive_group()
    assert scalar_action.codomain() is AdditiveGroups().AdditiveCommutative().End(additive_group)
    assert scalar_action(ZZ(2))(additive_group(QQ(1) / 2)) == additive_group(QQ(1))
    assert metric_dual.base_ring() is ZZ
    assert metric_dual.module_rank() == lattice.module_rank()
    assert metric_dual.gram_tensor().base_ring() is QQ
    assert metric_dual.signature_pair() == lattice.signature_pair()
    assert metric_dual in FormModules(ZZ).Nondegenerate()
    expected_pairing = lattice.gram_tensor().change_ring(QQ).dual_pairing()
    assert metric_dual.gram_tensor().change_ring(QQ).is_equal_tensor(expected_pairing)
    assert identification * lattice.correlation_morphism() == lattice.algebraic_correlation_morphism()
    for label in metric_dual.module_generating_set():
        assert identification(metric_dual.module_generator(label)) == linear_dual.module_generator(label)


def test_named_embedding_chain_is_form_preserving_and_injective() -> None:
    chain = (
        Embeddings.TCo_into_TEn,
        Embeddings.TEn_into_TdP,
        Embeddings.TdP_into_LK3,
    )
    for embedding in chain:
        assert embedding.is_injective()
        for left in embedding.domain().module_generators():
            for right in embedding.domain().module_generators():
                assert left.b(right) == embedding(left).b(embedding(right))








def test_named_k3_automorphisms_are_nontrivial_involutions() -> None:
    k3 = NamedLattices.LK3
    for involution in (Involutions.I_dP, Involutions.I_En, Involutions.I_Nik):
        assert all(involution(involution(generator)) == generator for generator in k3.module_generators())
        assert any(involution(generator) != generator for generator in k3.module_generators())


def test_catalogue_coinvariant_embeddings_are_formed_orthogonal_complements() -> None:
    pairs = (
        (Involutions.I_dP, Embeddings.TdP_into_LK3),
        (Involutions.I_En, Embeddings.TEn_into_LK3),
    )
    for involution, expected in pairs:
        invariant = involution.invariant_lattice()
        formed_coinvariants = involution.formed_coinvariants()
        assert invariant.module_rank() + formed_coinvariants.module_rank() == 22
        assert formed_coinvariants is expected.image()


def test_named_invariant_and_formed_coinvariant_lattices_are_exact() -> None:
    triples = (
        (Involutions.I_dP, NamedLattices.Sdp, NamedLattices.TdP),
        (Involutions.I_En, NamedLattices.SEn, NamedLattices.TEn),
        (Involutions.I_Nik, NamedLattices.LpNik, NamedLattices.LmNik),
    )
    for involution, expected_plus, expected_minus in triples:
        actual_plus = involution.invariant_lattice().inclusion().domain()
        actual_minus = involution.formed_coinvariants().inclusion().domain()
        for actual, expected in (
            (actual_plus, expected_plus),
            (actual_minus, expected_minus),
        ):
            assert actual.gram_tensor().is_equal_tensor(expected.gram_tensor())
            witness = actual.Isom(expected).an_element()
            assert expected.gram_tensor().pullback(witness).is_equal_tensor(
                actual.gram_tensor()
            )


def test_remaining_named_embeddings_are_primitive_and_form_preserving() -> None:
    for embedding in (
        Embeddings.E8_2_into_TdP,
        Embeddings.U_E8_2_into_TEn,
    ):
        assert embedding.is_primitive()
        for left in embedding.domain().module_generators():
            for right in embedding.domain().module_generators():
                assert left.b(right) == embedding(left).b(embedding(right))


def test_signature_block_search_enumerates_multisets_not_subsets() -> None:
    candidates = signature_orthogonal_sums(
        signature_pair(0, 4), (NamedLattices.A1, NamedLattices.D4)
    )
    assert candidates.cardinality() == 2
    assert all(
        candidate.signature_pair() == signature_pair(0, 4) for candidate in candidates
    )
