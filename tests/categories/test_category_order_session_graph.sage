r"""Discriminant groups and an index-two gluing of root lattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_discriminant_group_of_a2_is_cyclic_of_order_three() -> None:
    r"""``A_2^∨/A_2 ≅ ZZ/3``: ``|det A_2| = 3`` and the group is cyclic."""
    discriminant = Lattices(ZZ)("A2").discriminant_group()

    assert discriminant.cardinality() == 3
    assert tuple(discriminant.invariant_factors()) == (3,)


def test_discriminant_group_of_two_scaled_hyperbolic_planes() -> None:
    r"""The Gram matrix of ``U(2) ⊕ U(2)`` has Smith invariants ``(2, 2, 2, 2)``."""
    plane = Lattices(ZZ)("U").twist(2)
    lattice = plane + plane

    discriminant = lattice.discriminant_group()
    assert discriminant.cardinality() == 16
    assert tuple(discriminant.invariant_factors()) == (2, 2, 2, 2)


def test_all_integral_overlattices_of_a_scaled_hyperbolic_plane() -> None:
    r"""The discriminant bilinear space of ``U(2)`` is symplectic of dimension 2
    over ``F_2``. Its three lines and the zero space give all four integral
    overlattice inclusions, of indices 2 and 1 respectively.
    """
    lattice = Lattices(ZZ)("U").twist(2)

    indices = tuple(int(inclusion.index()) for inclusion in lattice.integral_overlattice_inclusions())
    assert indices.count(1) == 1
    assert indices.count(2) == 3
    assert all(index == 1 or index == 2 for index in indices)


def test_u_plus_a2_has_rank_four_and_determinant_minus_three() -> None:
    r"""``det(U ⊕ A_2) = det U · det A_2 = (-1) · 3``, up to the sign convention of
    ``A_2``; the rank is ``2 + 2``."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")

    assert lattice.module_rank() == 4
    assert abs(lattice.determinant()) == 3


def test_gluing_a1_to_the_fourth_along_the_diagonal_class_gives_d4() -> None:
    r"""``A_1^4`` has discriminant ``(ZZ/2)^4`` with ``q(e_i^*) = ±1/2``; the diagonal
    class has ``q = 4 · (±1/2) ≡ 0 mod 2``, so it is isotropic, and the overlattice
    it defines has index 2, rank 4 and ``|det| = 16/4 = 4``: it is ``D_4``.
    Derivation: the orthogonal roots ``e1 ± e2``, ``e3 ± e4`` of
    ``D_4 = {x ∈ ZZ^4 : Σ x_i even}`` span ``A_1^4`` of determinant 16, index 2 in
    ``D_4``, and ``D_4`` is the overlattice they generate with the diagonal glue."""
    a1 = Lattices(ZZ)("A1")
    lattice = a1 + a1 + a1 + a1
    discriminant = lattice.discriminant_module()
    diagonal = sum(discriminant.module_generators(), discriminant.zero())

    assert diagonal.q() == discriminant.quadratic_value_module().zero()
    inclusion = lattice.overlattice(diagonal)
    overlattice = inclusion.codomain()
    assert inclusion.index() == 2
    assert overlattice.module_rank() == 4
    assert abs(overlattice.determinant()) == 4
    assert overlattice.is_isometric(Lattices(ZZ)("D4"))
