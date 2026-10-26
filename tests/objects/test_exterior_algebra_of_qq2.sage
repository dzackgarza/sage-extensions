from sage_extensions.all import *


def plane():
    return QQ.free_module(("a", "b"))


def exterior():
    return plane().exterior_algebra()


def test_the_functor_and_the_object_constructions_agree() -> None:
    assert Modules(QQ).exterior_algebra()(plane()) is exterior()


def test_the_categories_of_the_exterior_algebra() -> None:
    algebra = exterior()
    assert algebra in Algebras(QQ)
    assert algebra in AlternatingAlgebras(QQ)
    assert algebra in StrictlyGradedCommutativeAlgebras(QQ)
    assert algebra in GradedAlgebras(QQ)


def test_the_graded_pieces_of_the_exterior_algebra() -> None:
    r"""$\dim \Lambda^n(\mathbb Q^2) = \binom{2}{n}$, total $2^2 = 4$."""
    algebra = exterior()
    assert algebra.graded_piece(0).module_rank() == 1
    assert algebra.graded_piece(1).module_rank() == 2
    assert algebra.graded_piece(2).module_rank() == 1
    assert algebra.graded_piece(2) in Modules(QQ)
    assert algebra.graded_piece(3).module_rank() == 0
    assert algebra.module_rank() == 4


def test_the_exterior_algebra_is_alternating() -> None:
    algebra = exterior()
    a, b = algebra.algebra_generator("a"), algebra.algebra_generator("b")
    assert a * a == algebra.zero()
    assert a * b == -(b * a)
    assert a * b != algebra.zero()
    assert a * b * a == algebra.zero()


def test_the_centre_of_the_exterior_algebra() -> None:
    r"""For $\dim V = 2$ in characteristic $0$ the centre of $\Lambda V$ is $\Lambda^0 \oplus \Lambda^2$: $a$ and $b$ anticommute, $ab$ commutes with both."""
    assert exterior().center().module_rank() == 2


def test_the_exterior_algebra_has_one_endomorphism_category() -> None:
    algebra = exterior()
    endomorphisms = algebra.Mor(algebra)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert algebra.Mor(algebra) is endomorphisms
    assert identity * identity == identity
