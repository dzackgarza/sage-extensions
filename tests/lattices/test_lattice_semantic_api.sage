from sage_extensions.all import *

def test_the_infinite_rank_dual_is_the_module_of_functionals_and_evaluates() -> None:
    r"""The algebraic dual of \(\mathbb Q^{(\mathbb N)}\) is its module of
    functionals, and the correlation is an injection that is not onto.

    The domain is the direct sum: every vector is a finitely supported function
    on the basis labels, so the correlation's image of a vector vanishes outside
    a finite set of indices.  A functional is its family of values on the basis,
    which is exactly an element of the module of morphisms into the free module
    of rank one, and evaluation at a vector is the finite sum of the vector's
    coefficients against those values; no basis of the dual is chosen.

    The dual is \(\prod_{\mathbb N} \mathbb Q\), of dimension
    \(2^{\aleph_0}\) over \(\mathbb Q\), so no countable family of its points
    generates it and this library holds no presentation of it.  It is the Mor,
    not a product object built beside it, and the correlation's images are
    points of that Mor.

    The constant functional -- one at every basis vector -- is a point of the
    dual that no finite-support vector maps to, which is the retained witness
    that the correlation is not onto.  It is read off the construction and is
    not a cokernel computation.
    """
    lattice = Lattices(QQ)(QQ**NN)
    ring = lattice.base_ring()
    dual = lattice.linear_dual()
    correlation = lattice.metric_map()

    e0 = lattice.basis_vector(0)
    e1 = lattice.basis_vector(1)
    e7 = lattice.basis_vector(7)
    first = correlation(e0)
    assert first.parent() is dual
    assert dual is lattice.module_category().Mor(lattice, ring.regular_module())
    assert lattice.dual_evaluation(first, e0) == ring.one()
    assert lattice.dual_evaluation(first, e1) == ring.zero()
    assert lattice.dual_evaluation(first, lattice.basis_vector(0) + 3 * lattice.basis_vector(2)) == ring.one()
    assert lattice.dual_evaluation(first, e7) == ring.zero()
    assert correlation.is_injective()
    assert lattice.is_nondegenerate()
    assert not lattice.is_unimodular()

    witness = correlation.non_surjectivity_witness()
    assert witness.parent() is dual
    assert lattice.dual_evaluation(witness, e0) == ring.one()
    assert lattice.dual_evaluation(witness, e1) == ring.one()
    assert lattice.dual_evaluation(witness, e7) == ring.one()
    assert not correlation.is_surjective()


def test_nondegenerate_and_unimodular_are_distinct_and_perfectness_retains_an_inverse() -> None:
    doubled_line = Lattices(ZZ)([[2]])
    assert doubled_line.is_nondegenerate() is True
    assert doubled_line.is_unimodular() is False

    plane = Lattices(ZZ)("U")
    correlation = plane.correlation_isomorphism()
    for generator in plane.module_generators():
        assert correlation.inverse()(correlation.forward()(generator)) == generator
    for functional in correlation.forward().codomain().module_generators():
        assert correlation.forward()(correlation.inverse()(functional)) == functional


def test_a_scalar_valued_pairing_returns_the_ring_value_at_every_rank() -> None:
    r"""\\(b(x,y)\\in R\\), not the coordinate of a represented module.

    A form whose values lie in the base ring is read through that ring's
    regular module privately.  Its public values are elements of the ring, so
    the infinite-framing route (no Gram tensor to contract) must raise the
    pairing through the same realization the finite route uses.
    """
    infinite = Lattices(QQ)(QQ**NN)
    e0 = infinite.basis_vector(0)
    e1 = infinite.basis_vector(1)
    ring = infinite.base_ring()

    assert infinite.b(e0, e0) in ring
    assert infinite.b(e0, e0) == ring.one()
    assert infinite.b(e0, e1) == ring.zero()
    assert infinite.norm(e0) == ring.one()

    finite = Lattices(QQ)([[2]])
    f0 = finite.basis_vector(0)
    finite_ring = finite.base_ring()
    assert finite.b(f0, f0) in finite_ring
    assert finite.b(f0, f0) == 2 * finite_ring.one()


def test_the_isotropic_reduction_of_two_U_along_a_primitive_isotropic_line_is_U() -> None:
    r"""In \(U \oplus U\) with first plane \(\langle e, f\rangle\), \(e^\perp = \mathbb Z e
    \oplus U\), so \(e^\perp/\mathbb Z e \cong U\)."""
    plane = Lattices(ZZ)("U")
    lattice = plane + plane
    e = lattice.basis_vector(0)
    isotropic = lattice.primitive_sublattice_from((e,))

    reduction = isotropic.isotropic_reduction()

    assert reduction.orthogonal_complement().rank() == 3
    assert reduction.quotient_lattice().rank() == 2
    assert reduction.quotient_lattice().is_unimodular()
    assert reduction.quotient_lattice().is_isometric_to(plane)
