from sage_extensions.all import *

import pytest


@pytest.mark.xfail(
    strict=True,
    reason=(
        "the algebraic dual of an infinite-rank free module is not expressible yet. "
        "Hom_R(L,R) is presented as a coordinate family of R.regular_module(), whose "
        "element __call__ takes a basis label, so a functional cannot be applied to a "
        "vector: the natural pairing L* x L -> R is missing. For infinite rank the dual "
        "is the product R^S, not the direct sum, and no product-module presentation "
        "exists; the correlation into it is injective and not surjective. Over QQ the "
        "regular module is a substitute rank-one free module because a ring whose "
        "coefficient ring is smaller is not placed as a module over itself. "
        "Reproduction: Lattices(ZZ)('U').metric_map()(e)(e)."
    ),
)
def test_the_correlation_of_QQ_to_the_NN_is_injective_but_not_onto_its_algebraic_dual() -> None:
    r"""With the standard form on \(\mathbb Q^{(\mathbb N)}\), \(b(v,-)\) has the finite
    support of \(v\), so the all-ones functional is not in the image of the
    correlation, while \(b(e_i, e_i) = 1\) makes it injective."""
    lattice = Lattices(QQ)(QQ**NN)
    dual = lattice.linear_dual()
    correlation = lattice.metric_map()
    e0 = lattice.basis_vector(0)
    e1 = lattice.basis_vector(1)
    e3 = lattice.basis_vector(3)

    first_covector = correlation(e0)
    assert first_covector(e0) == 1
    assert first_covector(e1) == 0

    all_ones = dual(lambda _label: 1)
    assert all_ones(e0) == all_ones(e1) == all_ones(e3) == 1

    assert correlation.is_injective()
    assert not correlation.is_surjective()
    assert lattice.is_nondegenerate()
    assert not lattice.is_unimodular()


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
