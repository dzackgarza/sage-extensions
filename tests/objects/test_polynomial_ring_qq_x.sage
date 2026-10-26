from sage_extensions.all import *


def polynomials():
    return QQ["x"]


def test_the_bracket_and_the_named_constructions_agree() -> None:
    assert polynomials() is QQ.polynomial_ring("x")


def test_the_polynomial_ring_is_the_symmetric_algebra_of_a_line() -> None:
    r"""$\mathbb Q[x] = \operatorname{Sym}(\mathbb Q x)$."""
    assert QQ.free_module(("x",)).symmetric_algebra() == polynomials()


def test_the_categories_of_qq_x() -> None:
    ring = polynomials()
    assert ring in Rings()
    assert ring in CommutativeRings()
    assert ring in IntegralDomains()
    assert ring in PrincipalIdealDomains()
    assert ring in NoetherianRings()
    assert ring in Algebras(QQ)
    assert ring in Algebras(QQ).Associative().Unital().Commutative()


def test_the_arithmetic_of_qq_x() -> None:
    ring = polynomials()
    x = ring.algebra_generator("x")
    assert (x + 1) ^ 2 == x ^ 2 + 2 * x + 1
    assert (x - 1) * (x + 1) == x ^ 2 - 1
    assert ring.algebra_structure_morphism()(QQ.one()) == ring.one()
    assert ring.algebra_base_ring() is QQ


def test_the_invariants_of_qq_x() -> None:
    ring = polynomials()
    assert ring.cardinality() == aleph0
    assert ring.krull_dimension() == 1


def test_quotients_of_qq_x() -> None:
    r"""$x^2 + 1$ is irreducible over $\mathbb Q$, so $\mathbb Q[x]/(x^2+1)$ is a field; $x^2 - 1$ is not, so $\mathbb Q[x]/(x^2 - 1)$ has zero divisors."""
    ring = polynomials()
    x = ring.algebra_generator("x")
    assert ring.quotient_ring(ring.ideal(x ^ 2 + 1)) in Fields()
    assert ring.quotient_ring(ring.ideal(x ^ 2 - 1)) not in IntegralDomains()


def test_the_points_of_qq_x_over_qq() -> None:
    r"""A ring map $\mathbb Q[x] \to \mathbb Q$ is evaluation at a rational number."""
    assert polynomials().Mor(QQ).cardinality() == aleph0


def test_the_kahler_differentials_of_qq_x() -> None:
    r"""$\Omega_{\mathbb Q[x]/\mathbb Q} = \mathbb Q[x]\,dx$ with $d(x^3) = 3x^2\,dx$."""
    ring = polynomials()
    x = ring.algebra_generator("x")
    omega = ring.kahler_differentials()
    dx = omega.differential_generator("x")
    assert omega.module_rank() == 1
    assert omega.universal_derivation()(x ^ 3) == omega.scalar_multiple(3 * x ^ 2, dx)


def test_the_de_rham_cohomology_of_the_affine_line() -> None:
    r"""Over $\mathbb Q$: $H^0_{dR} = \mathbb Q$ and $H^1_{dR} = 0$."""
    de_rham = polynomials().de_rham_algebra()
    assert de_rham.cohomology(0).module_rank() == 1
    assert de_rham.cohomology(1).cardinality() == 1


def test_qq_x_has_one_endomorphism_category() -> None:
    ring = polynomials()
    endomorphisms = ring.Mor(ring)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert ring.Mor(ring) is endomorphisms
    assert identity * identity == identity
