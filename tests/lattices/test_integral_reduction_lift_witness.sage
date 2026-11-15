r"""Marked-line reduction maps have exact integral lift decisions.

The identity of U + <2> has an integral lift. The marked null lines of U
and U(2) have zero reductions, but no integral isometry joins their ambient
lattices, whose determinants differ.
"""

from sage_extensions.all import *


def test_identity_reduction_has_an_integral_marked_line_lift() -> None:
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[2]])
    line = lattice.basis_vector(0)
    reduction = line.isotropic_reduction()
    fibre = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())

    witness = fibre.integral_base_point_or_none()

    assert witness in fibre
    integral = witness.integral_restriction(lattice, lattice)
    assert integral in lattice.Isom(lattice)
    assert integral(line) == line
    assert integral.inverse()(integral(line)) == line


def test_unequal_hyperbolic_determinants_have_no_integral_marked_line_lift() -> None:
    source = Lattices(ZZ)("U")
    target = Lattices(ZZ)([[0, 2], [2, 0]])
    first = source.basis_vector(0).isotropic_reduction()
    second = target.basis_vector(0).isotropic_reduction()
    reduced = first.Isom(second)(())
    fibre = first.rational_lifts(second, reduced)

    assert source.determinant() != target.determinant()
    assert fibre.integral_base_point_or_none() is None


def test_the_lift_torsor_computes_its_base_point_once_per_torsor() -> None:
    r"""The base point is a datum of the torsor, not of the call that reads it.

    The torsor's point set cuts the rational isometries by a predicate, and
    admitting a point into such a set decides that predicate: one membership
    test of the marked line and one per lattice generator, each a preimage
    computation.  The point asked for is the image of the identity under the
    trivialization fixed at construction, so it is the same point on every
    call and is computed once per torsor -- ``Torsors.from_trivialization``
    says as much when a base point is supplied, and this holds when it is not.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[2]])
    line = lattice.basis_vector(0)
    reduction = line.isotropic_reduction()
    fibre = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())

    base = fibre.base_point()

    assert base is fibre.base_point()
    assert fibre.trivialization()(fibre.acting_group().one()) == base
