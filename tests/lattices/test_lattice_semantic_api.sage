from sage_extensions.all import *

from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.indexed_families import IndexedFamily


def test_the_infinite_rank_dual_is_the_product_and_evaluates_by_projections() -> None:
    r"""The algebraic dual of \\(\\mathbb Q^{(\\mathbb N)}\\) is the product
    \\(\\prod_{\\mathbb N} \\mathbb Q\\), given by its projections.

    The domain is the direct sum: every vector is a finitely supported function
    on the basis labels, so the correlation's image of a vector vanishes outside
    a finite set of indices.  The product's constant family is an element of the
    dual that vanishes nowhere, so it is not in the image.  Evaluation of a
    functional at a vector is the finite sum of the vector's coefficients
    against the functional's projections; no basis of the dual is chosen.

    OPEN: `correlation.is_surjective()` raises `cannot compute the cokernel ...
    no algorithm is available for these modules` (domain the direct-sum lattice,
    codomain the product module). The assertion is kept rather than removed:
    deciding it needs the comparison of the direct-sum image with the product
    (the constant family lies outside the finite span), not a general
    infinite-rank cokernel.
    """
    lattice = Lattices(QQ)(QQ**NN)
    ring = lattice.base_ring()
    dual = lattice.linear_dual()
    construction = lattice._dual_product_construction()
    correlation = lattice.metric_map()

    assert construction is not None
    assert dual is construction.object()

    e0 = lattice.basis_vector(0)
    e1 = lattice.basis_vector(1)
    e7 = lattice.basis_vector(7)
    first = correlation(e0)
    assert first.parent() is dual
    assert lattice.dual_evaluation(first, e0) == ring.one()
    assert lattice.dual_evaluation(first, e1) == ring.zero()
    assert lattice.dual_evaluation(first, lattice.basis_vector(0) + 3 * lattice.basis_vector(2)) == ring.one()

    unit = ring.regular_module()(ring.one())
    constant = Modules(ring).product_element(
        construction, IndexedFamily(NN, lambda _index: unit)
    )
    assert constant.parent() is dual
    assert Modules(ring).product_component(construction, constant, NN(0)) == unit
    assert Modules(ring).product_component(construction, constant, NN(7)) == unit
    assert lattice.dual_evaluation(constant, e0) == ring.one()
    assert lattice.dual_evaluation(constant, e1) == ring.one()
    assert lattice.dual_evaluation(constant, e7) == ring.one()

    # The correlation's image is the direct sum inside the product: at index 7
    # the image of e_0 vanishes and the constant family does not, read through
    # the product's projections rather than by an undecided element equality.
    zero = ring.regular_module()(ring.zero())
    assert Modules(ring).product_component(construction, first, NN(7)) == zero
    assert Modules(ring).product_component(construction, constant, NN(7)) == unit
    assert lattice.dual_evaluation(first, e7) == ring.zero()
    assert correlation.is_injective()
    assert lattice.is_nondegenerate()
    assert not lattice.is_unimodular()

    # Non-surjectivity is refuted by the retained witness, not by a cokernel:
    # it is an element of the product whose component at every index is one,
    # while every value of the correlation vanishes away from the finite
    # support of its argument.
    witness = correlation.non_surjectivity_witness()
    assert witness is not None
    assert witness.parent() is dual
    assert Modules(ring).product_component(construction, witness, NN(0)) == unit
    assert Modules(ring).product_component(construction, witness, NN(7)) == unit
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
