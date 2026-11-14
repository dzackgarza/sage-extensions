r"""The isotropic reduction and the correlation isomorphism of research issue 614.

Cells 58 and 63 of ``preamble-lattices.ipynb``::

    eU, fU = NamedLattices.U.lattice_basis()
    assert NamedLattices.E8.is_elliptic()
    assert NamedLattices.U.q(eU) == 0
    assert eU * fU == ZZ.one()
    eU.e_perp_mod_e()

    gram = NamedLattices.U.gram_tensor()
    identity = gram.raise_index(NamedLattices.U, 0)
    correlation = NamedLattices.U.correlation_isomorphism()
    forward, inverse = correlation.forward(), correlation.inverse()
    assert tuple(int(entry) for entry in identity.tensor_valence()) == (1, 1)
    assert identity.lower_index(NamedLattices.U, 0) == gram
    assert all(inverse(forward(v)) == v for v in NamedLattices.U.lattice_basis())
    assert all(forward(inverse(f)) == f for f in forward.codomain().module_generators())

Each assertion is checked here, with the retained data behind it: the reduction
is a lattice of its own with the descended form, and the correlation is a
categorical isomorphism whose forward arrow is a module morphism with the
lattice and its dual as the two endpoints.
"""

from sage_extensions.all import Lattices, NamedLattices, ZZ


def test_the_hyperbolic_plane_is_isotropic_and_its_e_reduction_is_the_zero_lattice() -> None:
    r"""\(U\) has \(q(e_0) = 0\), \(e_0 \cdot e_1 = 1\), and \(e_0^\perp = \langle e_0\rangle\),
    so \(e_0^\perp/\langle e_0\rangle\) is the rank-zero lattice."""
    plane = NamedLattices.U
    eU, fU = tuple(plane.lattice_basis())

    assert NamedLattices.E8.is_elliptic()
    assert plane.q(eU) == 0
    assert eU * fU == ZZ.one()

    reduction = eU.e_perp_mod_e()
    # ``e_perp_mod_e`` is the retained archived spelling of the owned
    # isotropic reduction, and it returns the reduced lattice, not a bare module.
    assert reduction == eU.isotropic_reduction()
    assert reduction in Lattices(ZZ)
    assert reduction.module_rank() == 0
    assert reduction.cardinality() == ZZ.one()
    assert tuple(int(entry) for entry in reduction.gram_tensor().tensor_shape()) == (0, 0)


def test_the_correlation_isomorphism_has_module_arrows_and_both_inverse_identities() -> None:
    r"""A unimodular form identifies \(U\) with its dual, and the identification is
    an isomorphism of modules with both round trips verified."""
    plane = NamedLattices.U
    gram = plane.gram_tensor()
    identity = gram.raise_index(plane, 0)

    assert tuple(int(entry) for entry in gram.tensor_valence()) == (0, 2)
    assert tuple(int(entry) for entry in identity.tensor_valence()) == (1, 1)
    assert identity.lower_index(plane, 0) == gram

    correlation = plane.correlation_isomorphism()
    assert type(correlation).__name__ == "CategoricalIsomorphism"
    forward = correlation.forward()
    inverse = correlation.inverse()

    # Module-Mor ownership and the retained endpoints.
    assert "Module" in type(forward).__name__
    assert forward.domain() is plane
    assert inverse.domain() is forward.codomain()
    assert inverse.codomain() is forward.domain()
    assert forward.codomain().module_rank() == plane.module_rank()

    # Both inverse identities, on the lattice's basis and on the dual's
    # generators -- the second family is not the same set as the first.
    basis = tuple(plane.lattice_basis())
    assert all(inverse(forward(vector)) == vector for vector in basis)
    dual_generators = tuple(forward.codomain().module_generators())
    assert len(dual_generators) == len(basis)
    assert all(forward(inverse(functional)) == functional for functional in dual_generators)
    # And the round trips are not vacuous: the forward arrow is injective on a
    # nonzero vector and the inverse recovers it.
    assert (forward(basis[0]) == forward(basis[1])) is False
