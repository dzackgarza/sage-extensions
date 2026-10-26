r"""A Gram tensor exposes its variance-indexed modules, shape, graph blocks, and dual tensor."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_three_gram_tensor_retains_covariant_index_data() -> None:
    lattice = NamedLattices.A2 + NamedLattices.A1
    gram = lattice.gram_tensor()

    assert gram.tensor_type() == (0, 2)
    assert gram.tensor_valence() == (0, 2)
    assert gram.tensor_shape().cardinality() == cardinal(2)
    assert gram.contravariant_index_modules().cardinality() == cardinal(0)
    assert gram.covariant_index_modules().cardinality() == cardinal(2)
    assert gram.contravariant_index_generating_sets().cardinality() == cardinal(0)
    assert gram.covariant_index_generating_sets().cardinality() == cardinal(2)
    assert gram.index_modules().cardinality() == cardinal(2)
    assert gram.tensor_indices().cardinality() == cardinal(2)


def test_a2_plus_a1_gram_graph_and_component_cut_match_the_orthogonal_sum() -> None:
    gram = (NamedLattices.A2 + NamedLattices.A1).gram_tensor()
    graph = gram.gram_graph()
    cuts = gram.gram_connected_component_cuts()

    assert graph.has_edge(0, 1)
    assert not graph.has_edge(0, 2)
    assert 2 in cuts
    assert 1 not in cuts


def test_hyperbolic_gram_tensor_is_self_dual_and_tensor_equal_to_itself() -> None:
    gram = NamedLattices.U.gram_tensor()
    dual = gram.dual_tensor()

    assert gram.is_equal_tensor(gram)
    assert dual == tensor(ZZ, (2, 2), (), [[0, 1], [1, 0]])
