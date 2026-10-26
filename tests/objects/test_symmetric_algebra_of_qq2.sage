from sage_extensions.all import *


def plane():
    return QQ.free_module(("x", "y"))


def symmetric():
    return plane().symmetric_algebra()


def test_the_functor_and_the_object_constructions_agree() -> None:
    assert Modules(QQ).symmetric_algebra()(plane()) is symmetric()


def test_the_symmetric_algebra_is_the_polynomial_ring() -> None:
    r"""$\operatorname{Sym}(\mathbb Qx \oplus \mathbb Qy) = \mathbb Q[x, y]$."""
    assert symmetric() == QQ.polynomial_ring(("x", "y"))


def test_the_categories_of_the_symmetric_algebra() -> None:
    algebra = symmetric()
    assert algebra in Algebras(QQ)
    assert algebra in Algebras(QQ).Associative().Unital().Commutative()
    assert algebra in SymmetricAlgebras(QQ)
    assert algebra in GradedAlgebras(QQ)
    assert algebra in CommutativeRings()


def test_the_graded_pieces_of_the_symmetric_algebra() -> None:
    r"""$\dim \operatorname{Sym}^n(\mathbb Q^2) = n + 1$."""
    algebra = symmetric()
    assert algebra.graded_piece(0).module_rank() == 1
    assert algebra.graded_piece(1) is plane()
    assert algebra.graded_piece(2).module_rank() == 3
    assert algebra.graded_piece(2) in Modules(QQ)
    assert algebra.graded_piece(3).module_rank() == 4


def test_the_arithmetic_of_the_symmetric_algebra() -> None:
    algebra = symmetric()
    x, y = algebra.algebra_generator("x"), algebra.algebra_generator("y")
    assert x * y == y * x
    assert (x + y) ^ 2 == x ^ 2 + 2 * x * y + y ^ 2
    assert algebra.algebra_generators().cardinality() == 2
    assert algebra.krull_dimension() == 2


def test_the_kahler_differentials_of_the_symmetric_algebra() -> None:
    assert symmetric().kahler_differentials().module_rank() == 2


def test_the_symmetric_algebra_has_one_endomorphism_category() -> None:
    algebra = symmetric()
    endomorphisms = algebra.Mor(algebra)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert algebra.Mor(algebra) is endomorphisms
    assert identity * identity == identity
