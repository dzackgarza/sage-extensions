r"""Raising and lowering tensor indices with the Gram form of a lattice.

`U` is unimodular, so its Gram matrix is invertible over `\mathbb{Z}` and the
correlation `L \to L^\vee` is an isomorphism; `A_2` has determinant 3, so its Gram
matrix inverts only over `\mathbb{Q}` and the cokernel of its correlation is the
discriminant group, of order 3 (Conway--Sloane, *SPLAG*, Ch. 4, section 6.1).
"""

from sage_extensions.all import *


def test_archive_unimodular_gram_raises_to_identity_and_lowers_back() -> None:
    plane = Lattices(ZZ)("U")
    gram = plane.gram_tensor()
    identity = gram.raise_index(plane, 0)

    assert identity.tensor_valence() == (1, 1)
    assert identity == tensor(ZZ, (2,), (2,), [[1, 0], [0, 1]])
    assert identity.lower_index(plane, 0) == gram


def test_archive_nondegenerate_form_raises_after_fraction_field_base_change() -> None:
    a2 = Lattices(ZZ)("A2")
    fraction_map = a2.base_ring().fraction_field_map()
    rationalized = a2.base_change(fraction_map)
    raised = NondegenerateGenericFibreFormModules(ZZ)(a2).raise_index_over_fraction_field(a2.gram_tensor(), 0)

    assert raised.base_ring() is rationalized.base_ring()
    assert raised.tensor_valence() == (1, 1)
    assert raised == tensor(raised.base_ring(), (2,), (2,), [[1, 0], [0, 1]])
    assert rationalized.lower_index(raised, 0) == rationalized.gram_tensor()


def test_the_correlation_is_an_isomorphism_for_u_and_has_cokernel_of_order_three_for_a2() -> None:
    plane = Lattices(ZZ)("U")
    a2 = Lattices(ZZ)("A2")

    assert plane.correlation().is_isomorphism()
    assert not a2.correlation().is_isomorphism()
    assert a2.correlation().is_injective()
    assert a2.correlation().cokernel().cardinality() == 3
