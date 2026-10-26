r"""Algebra constructions a mathematician expects, over every named ring.

Polynomial, free, symmetric, exterior and tensor algebras, matrix algebras as
Lie algebras, presented algebras, Kähler differentials and the de Rham
complex: each asked over every ring in the catalogue for which the mathematics
defines it, with the values the definitions determine.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Free, symmetric, exterior and tensor algebras.
# ---------------------------------------------------------------------------


def test_free_algebra_over_every_commutative_ring(commutative_ring) -> None:
    r"""``R[S]`` is ``Sym(F_R(S))`` through the module and ring owners.

    The noncommutative free associative construction is the tensor algebra of
    the corresponding free module.
    """
    ring = commutative_ring
    free = ring.free_module(("a", "b")).symmetric_algebra()
    symmetric = ring.free_module(("a", "b")).symmetric_algebra()
    a = free.algebra_generator("a")
    b = free.algebra_generator("b")

    assert free is symmetric
    assert free in Algebras(ring)
    assert free in FreeAlgebras(ring)
    assert free in Algebras(ring).Associative().Unital().Commutative()
    assert free in CommutativeRings()
    assert a * b == b * a
    assert (a + b) * (a + b) == a * a + ring(2) * a * b + b * b
    assert free.algebra_generators().cardinality() == cardinal(2)


def test_symmetric_algebra_is_the_polynomial_algebra(commutative_ring) -> None:
    ring = commutative_ring
    symmetric = ring.free_module(("x", "y")).symmetric_algebra()
    x = symmetric.algebra_generator("x")
    y = symmetric.algebra_generator("y")

    assert symmetric in Algebras(ring).Associative().Unital().Commutative()
    assert symmetric in SymmetricAlgebras(ring)
    assert symmetric in GradedAlgebras(ring)
    assert x * y == y * x
    assert (x + y) ** 2 == x**2 + 2 * x * y + y**2
    assert symmetric.graded_piece(2).module_rank() == cardinal(3)
    assert symmetric.graded_piece(0).module_rank() == cardinal(1)


def test_symmetric_algebra_of_a_free_module(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(3)
    symmetric = module.symmetric_algebra()
    assert symmetric in Algebras(ring).Associative().Unital().Commutative()
    assert symmetric.generating_module() is module
    assert symmetric.graded_piece(1) is module
    assert symmetric.unformed_module() is not module
    assert symmetric.graded_piece(1).module_rank() == cardinal(3)
    assert symmetric.graded_piece(2).module_rank() == cardinal(6)


def test_exterior_algebra_of_a_free_module(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(3)
    exterior = module.exterior_algebra()
    e0 = exterior.algebra_generator(0)
    e1 = exterior.algebra_generator(1)
    e2 = exterior.algebra_generator(2)

    assert exterior in AlternatingAlgebras(ring)
    assert exterior in StrictlyGradedCommutativeAlgebras(ring)
    assert exterior in GradedAlgebras(ring)
    assert e0 * e0 == exterior.zero()
    assert e0 * e1 == -(e1 * e0)
    assert e0 * e1 * e2 != exterior.zero()
    assert exterior.graded_piece(0).module_rank() == cardinal(1)
    assert exterior.graded_piece(1).module_rank() == cardinal(3)
    assert exterior.graded_piece(2).module_rank() == cardinal(3)
    assert exterior.graded_piece(3).module_rank() == cardinal(1)
    assert exterior.graded_piece(4).module_rank() == cardinal(0)


def test_tensor_algebra_of_a_free_module(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    tensor = module.tensor_algebra()
    a = tensor.algebra_generator(0)
    b = tensor.algebra_generator(1)

    assert tensor in TensorAlgebras(ring)
    assert tensor in Algebras(ring)
    assert tensor not in Algebras(ring).Associative().Unital().Commutative()
    assert a * b != b * a
    assert tensor.graded_piece(2).module_rank() == cardinal(4)
    assert tensor.graded_piece(3).module_rank() == cardinal(8)


def test_polynomial_ring_is_a_commutative_algebra(commutative_ring) -> None:
    ring = commutative_ring
    polynomials = ring.polynomial_ring(("x", "y"))
    assert polynomials in Algebras(ring).Associative().Unital().Commutative()
    assert polynomials in Algebras(ring)
    assert polynomials.algebra_base_ring() is ring
    assert polynomials.algebra_structure_morphism()(ring.one()) == polynomials.one()


# ---------------------------------------------------------------------------
# Matrix algebras and Lie algebras.
# ---------------------------------------------------------------------------


def test_matrix_algebra_is_a_lie_algebra_under_the_commutator(commutative_ring) -> None:
    ring = commutative_ring
    matrices = ring.matrix_space(2)
    e01 = matrices.matrix_unit(0, 1)
    e10 = matrices.matrix_unit(1, 0)
    commutator = Algebras(ring).Associative().commutator_lie_algebra()(matrices)
    module = commutator.underlying_module()
    left = module(e01)
    right = module(e10)

    assert commutator is not matrices
    assert commutator in CommutatorLieAlgebras(ring)
    assert commutator in LieAlgebras(ring)
    assert commutator in Algebras(ring).Lie()
    assert commutator.bracket(left, right) == module(e01 * e10 - e10 * e01)
    assert commutator.bracket(left, left) == module.zero()
    h = commutator.bracket(left, right)
    assert commutator.bracket(h, left) == module.scalar_multiple(ring(2), left)
    assert commutator.bracket(h, right) == module.scalar_multiple(ring(-2), right)


# ---------------------------------------------------------------------------
# Presented algebras.
# ---------------------------------------------------------------------------


def test_coordinate_axes_as_a_presented_algebra(field) -> None:
    plane = field.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = (plane).quotient_by_relations([x * y])
    xbar = axes.algebra_generator("x")
    ybar = axes.algebra_generator("y")

    assert axes in Algebras(field).Associative().Unital().Commutative()
    assert axes in FinitelyPresentedAlgebras(field)
    assert xbar * ybar == axes.zero()
    assert xbar != axes.zero()
    assert xbar**2 != axes.zero()
    assert axes.krull_dimension() == 1
    assert axes.presentation_ring() is plane


# ---------------------------------------------------------------------------
# Kähler differentials.
# ---------------------------------------------------------------------------


def test_kahler_differentials_of_a_ring_over_itself_vanish(commutative_ring) -> None:
    r"""$\Omega_{R/R} = 0$."""
    omega = commutative_ring.kahler_differentials()
    assert omega in Modules(commutative_ring)
    assert omega.cardinality() == cardinal(1)


def test_kahler_differentials_of_the_polynomial_algebra(commutative_ring) -> None:
    r"""$\Omega_{R[x,y]/R} = R[x,y]\,dx \oplus R[x,y]\,dy$ with $d(xy) = y\,dx + x\,dy$."""
    ring = commutative_ring
    polynomials = ring.polynomial_ring(("x", "y"))
    x = polynomials.algebra_generator("x")
    y = polynomials.algebra_generator("y")
    omega = polynomials.kahler_differentials()
    d = omega.universal_derivation()
    dx = omega.differential_generator("x")
    dy = omega.differential_generator("y")

    assert omega in KahlerDifferentialModules(polynomials)
    assert omega in Modules(polynomials)
    assert omega.module_rank() == cardinal(2)
    assert d(x) == dx
    assert d(x * y) == omega.scalar_multiple(y, dx) + omega.scalar_multiple(x, dy)
    assert d(x**3) == omega.scalar_multiple(3 * x**2, dx)
    assert d(polynomials(ring.one())) == omega.zero()


def test_kahler_differentials_of_a_separable_extension_vanish(build) -> None:
    for name, base in (("QQ(i)", QQ), ("QQ(cbrt2)", QQ), ("GF(4)", GF(2))):
        omega = build(name).as_algebra_over(base).kahler_differentials()
        assert omega.cardinality() == cardinal(1)


@pytest.mark.parametrize(
    "name, discriminant",
    [("ZZ[i]", 4), ("ZZ[sqrt-5]", 20), ("ZZ[phi]", 5), ("ZZ[zeta5]", 125), ("ZZ[cbrt2]", 108)],
)
def test_kahler_differentials_of_a_ring_of_integers_have_the_order_of_the_discriminant(
    build, name, discriminant
) -> None:
    r"""$|\Omega_{\mathcal O_K/\mathbb Z}| = |d_K|$."""
    omega = build(name).as_algebra_over(ZZ).kahler_differentials()
    assert omega.cardinality() == cardinal(discriminant)


def test_kahler_differentials_of_a_rational_function_field(build) -> None:
    omega = build("QQ(x)").as_algebra_over(QQ).kahler_differentials()
    assert omega.module_rank() == cardinal(1)
    assert omega.cardinality() == aleph0


def test_kahler_differentials_of_the_coordinate_axes(field) -> None:
    plane = field.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = (plane).quotient_by_relations([x * y])
    xbar = axes.algebra_generator("x")
    ybar = axes.algebra_generator("y")
    omega = axes.kahler_differentials()
    dx = omega.differential_generator("x")
    dy = omega.differential_generator("y")

    assert omega.scalar_multiple(ybar, dx) + omega.scalar_multiple(xbar, dy) == omega.zero()
    assert omega.universal_derivation()(xbar * ybar) == omega.zero()
    assert dx != omega.zero()


# ---------------------------------------------------------------------------
# The de Rham complex.
# ---------------------------------------------------------------------------


def test_de_rham_complex_of_the_affine_line(field) -> None:
    polynomials = field.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    de_rham = polynomials.de_rham_algebra()
    d = de_rham.differential()

    assert de_rham in StrictlyCommutativeDifferentialGradedAlgebras(field)
    assert de_rham.de_rham_source_algebra() is polynomials
    assert de_rham.kahler_differentials().module_rank() == cardinal(1)
    assert d(d(de_rham(x))) == de_rham.zero()
    assert d(de_rham(x**2)) == 2 * de_rham(x) * d(de_rham(x))
    assert de_rham.graded_piece(2).module_rank() == cardinal(0)


@pytest.mark.parametrize("name", ["QQ", "QQ(i)", "RR", "AA"])
def test_poincare_lemma_in_characteristic_zero(build, name) -> None:
    r"""$H^1_{dR}(\mathbb A^1_K) = 0$ and $H^0 = K$ when $\operatorname{char} K = 0$."""
    field = build(name)
    de_rham = field.polynomial_ring("x").de_rham_algebra()
    assert de_rham.cohomology(1).cardinality() == cardinal(1)
    assert de_rham.cohomology(0).module_rank() == cardinal(1)


@pytest.mark.parametrize("name", ["GF(5)", "GF(4)"])
def test_de_rham_cohomology_of_the_line_is_nonzero_in_positive_characteristic(build, name) -> None:
    r"""$x^{p-1}\,dx$ is closed and not exact over $\mathbb F_q$."""
    field = build(name)
    de_rham = field.polynomial_ring("x").de_rham_algebra()
    assert de_rham.cohomology(1).cardinality() != cardinal(1)
    assert de_rham.cohomology(1).module_rank() >= cardinal(1)


def test_de_rham_cohomology_of_the_integer_line_has_torsion() -> None:
    r"""$x\,dx$ is closed over $\mathbb Z$ and $2\,x\,dx = d(x^2)$, so $H^1$ has $2$-torsion."""
    de_rham = ZZ.polynomial_ring("x").de_rham_algebra()
    assert de_rham.cohomology(1).cardinality() != cardinal(1)
    assert de_rham.cohomology(0).module_rank() == cardinal(1)
